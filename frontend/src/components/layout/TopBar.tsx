import React from 'react';
import { Search } from 'lucide-react';

export default function TopBar({ title }: { title: string }) {
  return (
    <header style={styles.topbar}>
      <div style={styles.left}>
        <h1 style={styles.title}>{title}</h1>
      </div>
      <div style={styles.right}>
        <div style={styles.searchBox}>
          <Search size={16} style={{ opacity: 0.45, color: 'var(--color-outline)' }} />
          <input
            type="text"
            placeholder="Search transactions..."
            style={styles.searchInput}
          />
        </div>
        <div style={styles.avatar}>AK</div>
      </div>
    </header>
  );
}

const styles: Record<string, React.CSSProperties> = {
  topbar: {
    position: 'fixed',
    top: 0,
    left: 'var(--sidebar-width)',
    right: 0,
    height: 'var(--topbar-height)',
    background: 'rgba(255, 255, 255, 0.92)',
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
    borderBottom: '1px solid var(--glass-border)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 var(--space-8)',
    zIndex: 90,
  },
  left: {
    display: 'flex',
    alignItems: 'center',
  },
  title: {
    fontSize: 'var(--text-h2)',
    fontWeight: 600,
    color: 'var(--color-on-surface)',
  },
  right: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-4)',
  },
  searchBox: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-2)',
    background: 'var(--color-surface-container-low)',
    border: '1px solid var(--glass-border)',
    borderRadius: 'var(--radius-full)',
    padding: 'var(--space-2) var(--space-4)',
    minWidth: 240,
    transition: 'border-color var(--transition-base), box-shadow var(--transition-base)',
  },
  searchInput: {
    background: 'transparent',
    border: 'none',
    outline: 'none',
    color: 'var(--color-on-surface)',
    fontSize: 'var(--text-small)',
    fontFamily: 'var(--font-body)',
    width: '100%',
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: 'var(--radius-lg)',
    background: 'var(--color-primary)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 'var(--text-caption)',
    fontWeight: 700,
    color: '#FFFFFF',
    letterSpacing: '0.02em',
  },
};
