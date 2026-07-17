import React from 'react';
import { CATEGORY_CONFIG } from '../../utils/constants';
import { formatCurrency } from '../../utils/formatters';
interface StatCardProps { category: string; amount: number; count?: number; percentage?: number; }
export default function StatCard({ category, amount, count, percentage }: StatCardProps) {
  const config = CATEGORY_CONFIG[category] || CATEGORY_CONFIG.Misc;

  return (
    <div className="glass-card glass-card--interactive" style={styles.card}>
      {/* Icon */}
      <div style={{ ...styles.iconWrap, background: `${config.color}15`, border: `1px solid ${config.color}30` }}>
        <span style={styles.icon}>{config.icon}</span>
      </div>

      {/* Content */}
      <div style={styles.content}>
        <span className="text-caption" style={styles.label}>{category}</span>
        <span style={styles.amount}>{formatCurrency(amount)}</span>
      </div>

      {/* Meta */}
      <div style={styles.meta}>
        {percentage != null && (
          <span style={{ ...styles.pct, color: config.color }}>{percentage.toFixed(1)}%</span>
        )}
        {count != null && (
          <span style={styles.count}>{count} txns</span>
        )}
      </div>

      {/* Decorative glow */}
      <div style={{ ...styles.glow, background: config.color }} />
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-4)',
    padding: 'var(--space-5)',
    position: 'relative',
    overflow: 'hidden',
  },
  iconWrap: {
    width: 44,
    height: 44,
    borderRadius: 'var(--radius-lg)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  icon: {
    fontSize: '1.25rem',
  },
  content: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-1)',
  },
  label: {
    fontSize: '0.6875rem',
  },
  amount: {
    fontFamily: 'var(--font-heading)',
    fontSize: '1.1rem',
    fontWeight: 700,
    color: 'var(--color-on-surface)',
    fontVariantNumeric: 'tabular-nums',
  },
  meta: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    gap: 'var(--space-1)',
  },
  pct: {
    fontSize: 'var(--text-small)',
    fontWeight: 700,
    fontVariantNumeric: 'tabular-nums',
  },
  count: {
    fontSize: 'var(--text-caption)',
    color: 'var(--color-on-surface-variant)',
  },
  glow: {
    position: 'absolute',
    bottom: -20,
    right: -20,
    width: 60,
    height: 60,
    borderRadius: '50%',
    opacity: 0.06,
    filter: 'blur(20px)',
    pointerEvents: 'none',
  },
};
