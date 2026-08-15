import { LayoutDashboard, Upload, List, BarChart3, Wallet, LogOut } from 'lucide-react';
import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'upload', label: 'Upload', icon: Upload },
  { id: 'transactions', label: 'Transactions', icon: List },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
];

export default function Sidebar({ activePage, onNavigate }: { activePage: string, onNavigate: (page: string) => void }) {
  const { logout } = useAuth();
  return (
    <aside style={styles.sidebar}>
      <div style={styles.logo}>
        <div style={styles.logoIcon}>
          <Wallet size={22} color="var(--color-primary)" />
        </div>
        <div>
          <div style={styles.logoText}>TxnNova</div>
          <div style={styles.logoSub}>Finance Dashboard</div>
        </div>
      </div>

      <nav style={styles.nav}>
        <div style={styles.navLabel}>Menu</div>
        {NAV_ITEMS.map((item) => {
          const isActive = activePage === item.id;
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              style={{
                ...styles.navItem,
                ...(isActive ? styles.navItemActive : {}),
              }}
            >
              {isActive && <div style={styles.activeStrip} />}
              <Icon size={18} style={{ opacity: isActive ? 1 : 0.55 }} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={styles.bottomSection}>
        <button style={styles.logoutButton} onClick={logout}>
          <LogOut size={18} style={{ opacity: 0.55 }} />
          <span>Sign Out</span>
        </button>
        <div style={styles.divider} />
        <div style={styles.versionTag}>v0.1.0 · Beta</div>
      </div>
    </aside>
  );
}

const styles: Record<string, React.CSSProperties> = {
  sidebar: {
    position: 'fixed',
    left: 0,
    top: 0,
    bottom: 0,
    width: 'var(--sidebar-width)',
    background: 'var(--color-surface)',
    borderRight: '1px solid var(--glass-border)',
    display: 'flex',
    flexDirection: 'column',
    padding: 'var(--space-6) var(--space-4)',
    zIndex: 100,
    boxShadow: 'var(--shadow-sm)',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-3)',
    marginBottom: 'var(--space-10)',
    paddingLeft: 'var(--space-2)',
  },
  logoIcon: {
    width: 40,
    height: 40,
    borderRadius: 'var(--radius-lg)',
    background: 'var(--color-primary-muted)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    border: '1px solid rgba(13, 148, 136, 0.15)',
  },
  logoText: {
    fontFamily: 'var(--font-heading)',
    fontSize: '1.125rem',
    fontWeight: 700,
    color: 'var(--color-on-surface)',
    letterSpacing: '-0.01em',
  },
  logoSub: {
    fontSize: 'var(--text-caption)',
    color: 'var(--color-on-surface-variant)',
    fontWeight: 500,
    textTransform: 'none',
    letterSpacing: 'normal',
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-1)',
    flex: 1,
  },
  navLabel: {
    fontSize: 'var(--text-caption)',
    fontWeight: 600,
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
    color: 'var(--color-outline)',
    padding: 'var(--space-2) var(--space-3)',
    marginBottom: 'var(--space-2)',
  },
  navItem: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-3)',
    padding: 'var(--space-3) var(--space-4)',
    borderRadius: 'var(--radius-lg)',
    border: 'none',
    background: 'transparent',
    color: 'var(--color-on-surface-variant)',
    fontSize: 'var(--text-small)',
    fontWeight: 500,
    fontFamily: 'var(--font-body)',
    cursor: 'pointer',
    transition: 'background-color var(--transition-base), color var(--transition-base), transform var(--transition-fast)',
    textAlign: 'left',
    width: '100%',
  },
  navItemActive: {
    background: 'var(--color-primary-muted)',
    color: 'var(--color-primary-dim)',
    fontWeight: 600,
  },
  activeStrip: {
    position: 'absolute',
    left: 0,
    top: '25%',
    bottom: '25%',
    width: 3,
    borderRadius: 'var(--radius-full)',
    background: 'var(--color-primary)',
  },
  bottomSection: {
    paddingTop: 'var(--space-4)',
  },
  divider: {
    height: 1,
    background: 'var(--glass-border)',
    marginBottom: 'var(--space-4)',
  },
  versionTag: {
    fontSize: 'var(--text-caption)',
    color: 'var(--color-outline)',
    textAlign: 'center',
    textTransform: 'none',
    letterSpacing: 'normal',
    fontWeight: 400,
  },
  logoutButton: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-3)',
    padding: 'var(--space-3) var(--space-4)',
    borderRadius: 'var(--radius-lg)',
    border: 'none',
    background: 'transparent',
    color: 'var(--color-error)',
    fontSize: 'var(--text-small)',
    fontWeight: 500,
    fontFamily: 'var(--font-body)',
    cursor: 'pointer',
    transition: 'background-color var(--transition-base), transform var(--transition-fast)',
    textAlign: 'left',
    width: '100%',
    marginBottom: 'var(--space-4)',
  },
};
