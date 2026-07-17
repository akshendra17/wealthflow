import React from 'react';
import { Bell, Search } from 'lucide-react';

export default function TopBar({ title }: { title: string }) {
  return (
    <header style={styles.topbar}>
      <div style={styles.left}>
        <h1 style={styles.title}>{title}</h1>
      </div>
      <div style={styles.right}>
        <div style={styles.searchBox}>
          <Search size={16} style={{ opacity: 0.5 }} />
          <input
            type="text"
            placeholder="Search transactions..."
            style={styles.searchInput}
          />
        </div>
        <button style={styles.iconBtn} aria-label="Notifications">
          <Bell size={18} />
          <div style={styles.notifDot} />
        </button>
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
    background: 'rgba(10, 10, 10, 0.7)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
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
    background: 'rgba(53, 53, 52, 0.4)',
    border: '1px solid var(--glass-border)',
    borderRadius: 'var(--radius-full)',
    padding: 'var(--space-2) var(--space-4)',
    minWidth: 240,
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
  iconBtn: {
    position: 'relative',
    background: 'rgba(53, 53, 52, 0.3)',
    border: '1px solid var(--glass-border)',
    borderRadius: 'var(--radius-lg)',
    width: 36,
    height: 36,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    color: 'var(--color-on-surface-variant)',
    transition: 'all var(--transition-base)',
  },
  notifDot: {
    position: 'absolute',
    top: 6,
    right: 6,
    width: 7,
    height: 7,
    borderRadius: '50%',
    background: 'var(--color-primary)',
    boxShadow: '0 0 6px rgba(0, 209, 255, 0.6)',
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: 'var(--radius-lg)',
    background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 'var(--text-caption)',
    fontWeight: 700,
    color: '#fff',
    letterSpacing: '0.02em',
  },
};
