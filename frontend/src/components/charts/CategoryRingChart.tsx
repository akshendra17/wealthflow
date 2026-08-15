import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { CATEGORY_CONFIG } from '../../utils/constants';
import { formatCurrency } from '../../utils/formatters';

interface CategoryRingChartProps {
  categories: any[];
  totalExpenses: number;
  selectedCategory?: string | null;
  onCategorySelect?: (category: string) => void;
}

export default function CategoryRingChart({
  categories,
  totalExpenses,
  selectedCategory = null,
  onCategorySelect,
}: CategoryRingChartProps) {
  if (!categories?.length) return null;

  const data = categories.map((c) => ({
    name: c.category,
    value: c.total_amount,
    color: CATEGORY_CONFIG[c.category]?.color || '#94A3B8',
    icon: CATEGORY_CONFIG[c.category]?.icon || '📦',
  }));

  const displayTotal = selectedCategory
    ? data.find((d) => d.name === selectedCategory)?.value ?? totalExpenses
    : totalExpenses;

  return (
    <div className="glass-card chart-card" style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Spending Distribution</h3>
      </div>
      <div style={styles.chartWrap} className="chart-card-body">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius="55%"
              outerRadius="80%"
              paddingAngle={2}
              dataKey="value"
              stroke="none"
              onClick={(_, index) => onCategorySelect?.(data[index].name)}
            >
              {data.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={entry.color}
                  opacity={
                    selectedCategory && selectedCategory !== entry.name ? 0.35 : 1
                  }
                  style={{ cursor: onCategorySelect ? 'pointer' : 'default' }}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={styles.tooltip}
              formatter={(value: any) => formatCurrency(value as number)}
              labelStyle={{ color: '#0F172A', fontWeight: 600 }}
            />
          </PieChart>
        </ResponsiveContainer>

        <div style={styles.centerLabel}>
          <span className="text-caption">{selectedCategory || 'Total'}</span>
          <span style={styles.centerAmount}>{formatCurrency(displayTotal)}</span>
        </div>
      </div>

      <div style={styles.legend}>
        {data.slice(0, 6).map((item) => {
          const isSelected = selectedCategory === item.name;
          return (
            <button
              key={item.name}
              type="button"
              className={`category-legend-btn ${isSelected ? 'category-legend-btn--selected' : ''}`}
              onClick={() => onCategorySelect?.(item.name)}
              aria-pressed={isSelected}
            >
              <span style={{ ...styles.legendDot, background: item.color }} />
              <span style={styles.legendLabel}>{item.icon} {item.name}</span>
              <span style={styles.legendValue}>{formatCurrency(item.value)}</span>
            </button>
          );
        })}
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
    flexShrink: 0,
  },
  title: {
    fontSize: 'var(--text-h3)',
    fontWeight: 600,
  },
  chartWrap: {
    position: 'relative',
    minHeight: 240,
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
    pointerEvents: 'none',
  },
  centerAmount: {
    fontFamily: 'var(--font-heading)',
    fontSize: '1.25rem',
    fontWeight: 700,
    color: 'var(--color-on-surface)',
  },
  tooltip: {
    background: '#FFFFFF',
    border: '1px solid #E2E8F0',
    borderRadius: 12,
    padding: '10px 14px',
    boxShadow: '0 8px 24px rgba(15, 23, 42, 0.08)',
  },
  legend: {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-1)',
    marginTop: 'var(--space-4)',
    flexShrink: 0,
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
