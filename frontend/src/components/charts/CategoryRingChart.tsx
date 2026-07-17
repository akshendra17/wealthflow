import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { CATEGORY_CONFIG } from '../../utils/constants';
import { formatCurrency } from '../../utils/formatters';

export default function CategoryRingChart({ categories, totalExpenses }: { categories: any[], totalExpenses: number }) {
  if (!categories?.length) return null;

  const data = categories.map((c) => ({
    name: c.category,
    value: c.total_amount,
    color: CATEGORY_CONFIG[c.category]?.color || '#859399',
    icon: CATEGORY_CONFIG[c.category]?.icon || '📦',
  }));

  return (
    <div className="glass-card" style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Spending Distribution</h3>
      </div>
      <div style={styles.chartWrap}>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={80}
              outerRadius={120}
              paddingAngle={2}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={entry.color}
                  style={{
                    filter: `drop-shadow(0 0 6px ${entry.color}50)`,
                    cursor: 'pointer',
                  }}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={styles.tooltip}
              formatter={(value: any) => formatCurrency(value as number)}
              labelStyle={{ color: '#e5e2e1', fontWeight: 600 }}
            />
          </PieChart>
        </ResponsiveContainer>

        {/* Center label */}
        <div style={styles.centerLabel}>
          <span className="text-caption">Total</span>
          <span style={styles.centerAmount}>{formatCurrency(totalExpenses)}</span>
        </div>
      </div>

      {/* Legend */}
      <div style={styles.legend}>
        {data.slice(0, 6).map((item) => (
          <div key={item.name} style={styles.legendItem}>
            <span style={{ ...styles.legendDot, background: item.color }} />
            <span style={styles.legendLabel}>{item.icon} {item.name}</span>
            <span style={styles.legendValue}>{formatCurrency(item.value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: 'var(--space-6)',
  },
  header: {
    marginBottom: 'var(--space-2)',
  },
  title: {
    fontSize: 'var(--text-h3)',
    fontWeight: 600,
  },
  chartWrap: {
    position: 'relative',
  },
  centerLabel: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    textAlign: 'center',
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  centerAmount: {
    fontFamily: 'var(--font-heading)',
    fontSize: '1.25rem',
    fontWeight: 700,
    color: 'var(--color-on-surface)',
  },
  tooltip: {
    background: 'rgba(20, 20, 20, 0.95)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 12,
    padding: '10px 14px',
  },
  legend: {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-2)',
    marginTop: 'var(--space-2)',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-3)',
    padding: 'var(--space-1) 0',
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    flexShrink: 0,
  },
  legendLabel: {
    flex: 1,
    fontSize: 'var(--text-small)',
    color: 'var(--color-on-surface-variant)',
  },
  legendValue: {
    fontSize: 'var(--text-small)',
    fontWeight: 600,
    color: 'var(--color-on-surface)',
    fontVariantNumeric: 'tabular-nums',
  },
};
