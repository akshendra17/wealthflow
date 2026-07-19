import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, UploadCloud } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
}

export default function EmptyState({
  title = 'No Data Available',
  description = 'Upload a bank statement to see your insights and transactions.',
  actionText = 'Upload Statement',
  onAction,
}: EmptyStateProps) {
  const navigate = useNavigate();

  const handleAction = () => {
    if (onAction) {
      onAction();
    } else {
      navigate('/upload');
    }
  };

  return (
    <div className="glass-card animate-in" style={styles.container}>
      <div style={styles.iconContainer}>
        <FileText size={32} color="var(--color-secondary)" />
      </div>
      <h3 style={styles.title}>{title}</h3>
      <p style={styles.description}>{description}</p>
      
      <button className="btn btn-primary" onClick={handleAction} style={styles.button}>
        <UploadCloud size={18} />
        {actionText}
      </button>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 'var(--space-8)',
    textAlign: 'center',
    minHeight: 300,
    marginTop: 'var(--space-6)',
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: 'var(--radius-full)',
    background: 'rgba(255, 255, 255, 0.05)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 'var(--space-4)',
  },
  title: {
    fontSize: 'var(--text-h3)',
    fontWeight: 600,
    color: 'var(--color-on-surface)',
    marginBottom: 'var(--space-2)',
  },
  description: {
    fontSize: 'var(--text-base)',
    color: 'var(--color-text-secondary)',
    maxWidth: 400,
    marginBottom: 'var(--space-6)',
    lineHeight: 1.5,
  },
  button: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 'var(--space-2)',
  },
};
