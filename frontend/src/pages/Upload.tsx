import FileUpload from '../components/ui/FileUpload';
import React, { useState, useEffect } from 'react';
import { getStatements, deleteStatement, deleteAllStatements } from '../services/api';
import { formatCurrency } from '../utils/formatters';
import { MONTH_NAMES } from '../utils/constants';
import { FileText, Trash2 } from 'lucide-react';

import type { Statement } from '../types';

export default function UploadPage() {
  const [statements, setStatements] = useState<Statement[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchStatements = async () => {
    setLoading(true);
    try {
      const data = await getStatements();
      setStatements(data);
    } catch { /* pass */ } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchStatements(); }, []);

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this statement and all its transactions?')) return;
    try {
      await deleteStatement(id);
      fetchStatements();
    } catch { /* pass */ }
  };

  const handleDeleteAll = async () => {
    if (!confirm('Are you sure you want to delete ALL statements and transactions? This cannot be undone.')) return;
    try {
      await deleteAllStatements();
      fetchStatements();
    } catch { /* pass */ }
  };

  return (
    <div>
      <h2 style={styles.pageTitle}>Upload Statement</h2>
      <p style={styles.subtitle}>
        Upload your bank or credit card statement (CSV or PDF format) to automatically extract and categorize transactions.
      </p>

      <FileUpload onUploadSuccess={fetchStatements} />

      {/* Uploaded Statements */}
      <div style={styles.section}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
          <h3 style={styles.sectionTitle}>Uploaded Statements</h3>
          {statements.length > 0 && !loading && (
            <button className="btn btn-outline btn-sm" onClick={handleDeleteAll} style={{ color: 'var(--color-error)', borderColor: 'var(--color-error)' }}>
              Clear All Data
            </button>
          )}
        </div>
        
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 68, borderRadius: 14 }} />
            ))}
          </div>
        ) : statements.length === 0 ? (
          <div className="glass-card" style={{ padding: 'var(--space-8)', textAlign: 'center' }}>
            <p className="text-muted">No statements uploaded yet.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {statements.map((stmt) => (
              <div key={stmt.id} className="glass-card" style={styles.stmtRow}>
                <div style={styles.stmtIcon}>
                  <FileText size={20} color="var(--color-primary-soft)" />
                </div>
                <div style={styles.stmtInfo}>
                  <span style={styles.stmtName}>{stmt.original_filename}</span>
                  <span style={styles.stmtMeta}>
                    {stmt.statement_month && stmt.statement_year
                      ? `${MONTH_NAMES[stmt.statement_month]} ${stmt.statement_year}`
                      : 'Unknown period'
                    } • {stmt.total_transactions} transactions
                  </span>
                </div>
                <div style={styles.stmtAmounts}>
                  <span style={{ color: 'var(--color-error)', fontSize: 'var(--text-small)', fontWeight: 600 }}>
                    ↓ {formatCurrency(stmt.total_debit)}
                  </span>
                  <span style={{ color: 'var(--color-tertiary)', fontSize: 'var(--text-caption)' }}>
                    ↑ {formatCurrency(stmt.total_credit)}
                  </span>
                </div>
                <button
                  onClick={() => handleDelete(stmt.id)}
                  style={styles.deleteBtn}
                  title="Delete statement"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  pageTitle: {
    fontSize: 'var(--text-h1)',
    fontWeight: 600,
    marginBottom: 'var(--space-2)',
  },
  subtitle: {
    fontSize: 'var(--text-body)',
    color: 'var(--color-on-surface-variant)',
    marginBottom: 'var(--space-6)',
    maxWidth: 600,
  },
  section: {
    marginTop: 'var(--space-10)',
  },
  sectionTitle: {
    fontSize: 'var(--text-h3)',
    fontWeight: 600,
  },
  stmtRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-4)',
    padding: 'var(--space-4) var(--space-5)',
  },
  stmtIcon: {
    width: 42,
    height: 42,
    borderRadius: 'var(--radius-lg)',
    background: 'rgba(0, 209, 255, 0.08)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  stmtInfo: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
  },
  stmtName: {
    fontSize: 'var(--text-small)',
    fontWeight: 600,
    color: 'var(--color-on-surface)',
  },
  stmtMeta: {
    fontSize: 'var(--text-caption)',
    color: 'var(--color-on-surface-variant)',
  },
  stmtAmounts: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    gap: 2,
    fontVariantNumeric: 'tabular-nums',
  },
  deleteBtn: {
    background: 'transparent',
    border: '1px solid var(--glass-border)',
    borderRadius: 'var(--radius-md)',
    width: 34,
    height: 34,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--color-outline)',
    cursor: 'pointer',
    transition: 'all var(--transition-fast)',
    flexShrink: 0,
  },
};
