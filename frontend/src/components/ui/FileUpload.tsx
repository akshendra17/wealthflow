import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, AlertTriangle, Loader2, Lock } from 'lucide-react';
import { uploadStatement, ApiError } from '../../services/api';
import Select from './Select';
import { BANK_OPTIONS } from '../../utils/constants';
import { useBankFilter } from '../../context/BankFilterContext';

export default function FileUpload({ onUploadSuccess }: { onUploadSuccess?: (data: any) => void }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ type: 'success' | 'error' | 'warning', message: string, data?: any } | null>(null);
  const { bankName, setBankName } = useBankFilter();
  const [password, setPassword] = useState('');
  const inputRef = useRef(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const files = e.dataTransfer.files;
    if (files?.[0]) handleFile(files[0]);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      handleFile(e.target.files[0]);
    }
    // Reset value so selecting the same file again triggers onChange
    e.target.value = '';
  };

  const handleFile = async (file: File) => {
    // Validate
    if (!file.name.toLowerCase().endsWith('.csv') && !file.name.toLowerCase().endsWith('.pdf')) {
      setResult({ type: 'error', message: 'Only CSV and PDF files are supported.' });
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setResult({ type: 'error', message: 'File too large (max 50MB).' });
      return;
    }

    setUploading(true);
    setResult(null);
    try {
      const data = await uploadStatement(file, { bankName, password: password || undefined });
      setResult({
        type: 'success',
        message: `Parsed ${data.total_transactions} transactions from "${data.original_filename}"`,
        data,
      });
      onUploadSuccess?.(data);
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 409) {
        setResult({ type: 'warning', message: err.message });
      } else {
        setResult({ type: 'error', message: err.message });
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="glass-card" style={{ padding: 'var(--space-5)', marginBottom: 'var(--space-6)', display: 'flex', flexWrap: 'wrap', gap: 'var(--space-6)', alignItems: 'flex-start' }}>
        
        <div style={{ flex: '1 1 280px', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          <label htmlFor="bank-select" style={{ fontSize: 'var(--text-small)', fontWeight: 600, color: 'var(--color-on-surface)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <FileText size={16} color="var(--color-primary)" />
            Select Bank <span style={{ color: 'var(--color-on-surface-variant)', fontWeight: 400 }}>(Optional)</span>
          </label>
          <Select
            value={bankName}
            onChange={setBankName}
            options={[
              { label: 'Auto-detect', value: '' },
              ...BANK_OPTIONS.filter((o: { label: string, value: string }) => o.value !== '')
            ]}
          />
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-on-surface-variant)', margin: 0 }}>
            Selecting your bank ensures the most accurate parsing.
          </p>
        </div>

        <div style={{ flex: '1 1 280px', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          <label htmlFor="pdf-password" style={{ fontSize: 'var(--text-small)', fontWeight: 600, color: 'var(--color-on-surface)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Lock size={16} color="var(--color-warning, #f59f00)" />
            PDF Password <span style={{ color: 'var(--color-on-surface-variant)', fontWeight: 400 }}>(If protected)</span>
          </label>
          <div style={{ position: 'relative' }}>
            <div style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-on-surface-variant)' }}>
              <Lock size={16} />
            </div>
            <input
              id="pdf-password"
              type="password"
              placeholder="Enter PDF password..."
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              style={{ width: '100%', paddingLeft: 38, background: 'var(--color-surface-container-low)', border: '1px solid var(--glass-border)', borderRadius: 'var(--radius-md)', height: 42, color: 'var(--color-on-surface)' }}
            />
          </div>
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-on-surface-variant)', margin: 0 }}>
            Required only for password-protected bank statements.
          </p>
        </div>
      </div>
      <div
        className="glass-card"
        style={{ ...styles.container, ...(dragActive ? styles.containerActive : {}) }}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => {
          if (!uploading && !result && inputRef.current) {
            (inputRef.current as HTMLInputElement).click();
          }
        }}
      >
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.pdf"
        onChange={handleChange}
        style={{ display: 'none' }}
        id="file-upload"
      />

      {uploading ? (
        <div style={styles.stateBox}>
          <Loader2 size={40} color="var(--color-primary)" style={{ animation: 'spin 1s linear infinite' }} />
          <p style={styles.stateText}>Processing statement...</p>
          <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
        </div>
      ) : result ? (
        <div style={styles.stateBox}>
          {result.type === 'success' ? (
            <CheckCircle2 size={40} color="var(--color-tertiary)" />
          ) : result.type === 'warning' ? (
            <AlertTriangle size={40} color="var(--color-warning, #f59f00)" />
          ) : (
            <AlertCircle size={40} color="var(--color-error)" />
          )}
          <p style={{ 
            ...styles.stateText, 
            color: result.type === 'success' ? 'var(--color-tertiary)' : 
                   result.type === 'warning' ? 'var(--color-warning, #f59f00)' : 'var(--color-error)' 
          }}>
            {result.message}
          </p>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => { setResult(null); if (inputRef.current) (inputRef.current as any).value = ''; }}
            style={{ marginTop: 'var(--space-3)' }}
          >
            Upload Another
          </button>
        </div>
      ) : (
        <div style={styles.label}>
          <div style={styles.iconCircle}>
            <Upload size={28} color="var(--color-primary)" />
          </div>
          <div>
            <p style={styles.mainText}>
              <span style={{ color: 'var(--color-primary)', fontWeight: 600 }}>Click to upload</span>
              {' '}or drag & drop
            </p>
            <p style={styles.subText}>
              <FileText size={14} style={{ display: 'inline', verticalAlign: '-2px' }} /> CSV or PDF bank statements supported • Max 50MB
            </p>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: 'var(--space-8) var(--space-6)',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'border-color var(--transition-base), background-color var(--transition-base), box-shadow var(--transition-base)',
    position: 'relative',
    overflow: 'hidden',
    border: '2px dashed var(--glass-border-bright)',
    background: 'var(--color-surface-container-low)',
  },
  containerActive: {
    borderColor: 'var(--color-primary)',
    background: 'var(--color-primary-muted)',
    boxShadow: 'var(--shadow-md)',
  },
  label: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-5)',
    cursor: 'pointer',
    justifyContent: 'center',
  },
  iconCircle: {
    width: 60,
    height: 60,
    borderRadius: '50%',
    background: 'var(--color-primary-muted)',
    border: '1px solid rgba(13, 148, 136, 0.15)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  mainText: {
    fontSize: 'var(--text-body)',
    color: 'var(--color-on-surface)',
    marginBottom: 'var(--space-1)',
  },
  subText: {
    fontSize: 'var(--text-small)',
    color: 'var(--color-on-surface-variant)',
  },
  stateBox: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 'var(--space-3)',
    padding: 'var(--space-4)',
  },
  stateText: {
    fontSize: 'var(--text-body)',
    fontWeight: 500,
    whiteSpace: 'pre-line',
    maxWidth: '100%',
    textAlign: 'center',
  },
};
