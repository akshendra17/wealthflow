import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { CATEGORY_CONFIG, MONTH_SHORT } from '../../utils/constants';
import { formatCurrency, formatCurrencyCompact } from '../../utils/formatters';

const PRIMARY_CHART = '#0D9488';
const GRID_STROKE = '#E2E8F0';
const AXIS_TICK = '#94A3B8';

export default function TrendChart({ trends }: { trends: any }) {
  if (!trends || !trends.months?.length) {
    return (
      <div className="glass-card" style={styles.empty}>
        <p className="text-muted">No trend data available. Upload at least 2 months of statements.</p>
      </div>
    );
  }

  const chartData = trends.months.map((m: any, i: number) => ({
    name: `${MONTH_SHORT[m.month]} ${String(m.year).slice(2)}`,
    total: trends.totals[i],
    ...Object.fromEntries(
      Object.entries(trends.category_trends).map(([cat, vals]) => [cat, (vals as number[])[i] || 0])
    ),
  }));

  const topCategories = Object.entries(trends.category_trends)
    .map(([cat, vals]) => ({ cat, latest: (vals as number[]).at(-1) || 0 }))
    .sort((a, b) => b.latest - a.latest)
    .slice(0, 5)
    .map((c) => c.cat);

  return (
    <div className="glass-card chart-card" style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Expense Velocity</h3>
        <span className="text-caption">Last {trends.months.length} months</span>
      </div>
      <div className="chart-card-body">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id="gradTotal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={PRIMARY_CHART} stopOpacity={0.2} />
              <stop offset="95%" stopColor={PRIMARY_CHART} stopOpacity={0} />
            </linearGradient>
            {topCategories.map((cat) => {
              const color = CATEGORY_CONFIG[cat]?.color || '#94A3B8';
              return (
                <linearGradient key={cat} id={`grad-${cat}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={color} stopOpacity={0.15} />
                  <stop offset="95%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              );
            })}
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke={GRID_STROKE}
            vertical={false}
          />
          <XAxis
            dataKey="name"
            axisLine={false}
            tickLine={false}
            tick={{ fill: AXIS_TICK, fontSize: 12, fontFamily: 'Inter' }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: AXIS_TICK, fontSize: 12, fontFamily: 'Inter' }}
            tickFormatter={formatCurrencyCompact}
          />
          <Tooltip
            contentStyle={styles.tooltip}
            labelStyle={{ color: '#0F172A', fontWeight: 600, marginBottom: 8 }}
            itemStyle={{ fontSize: 13, color: '#475569' }}
            formatter={(value: any) => formatCurrency(value as number)}
          />
          <Area
            type="monotone"
            dataKey="total"
            stroke={PRIMARY_CHART}
            strokeWidth={2.5}
            fill="url(#gradTotal)"
            name="Total"
            dot={false}
            activeDot={{ r: 5, fill: PRIMARY_CHART, stroke: '#FFFFFF', strokeWidth: 2 }}
          />
          {topCategories.map((cat) => {
            const color = CATEGORY_CONFIG[cat]?.color || '#94A3B8';
            return (
              <Area
                key={cat}
                type="monotone"
                dataKey={cat}
                stroke={color}
                strokeWidth={1.5}
                fill={`url(#grad-${cat})`}
                name={cat}
                dot={false}
                strokeOpacity={0.7}
              />
            );
          })}
          <Legend
            verticalAlign="top"
            height={36}
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: 12, fontFamily: 'Inter', color: '#64748B' }}
          />
        </AreaChart>
      </ResponsiveContainer>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: 'var(--space-6)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 'var(--space-5)',
  },
  title: {
    fontSize: 'var(--text-h3)',
    fontWeight: 600,
  },
  tooltip: {
    background: '#FFFFFF',
    border: '1px solid #E2E8F0',
    borderRadius: 12,
    padding: '12px 16px',
    boxShadow: '0 8px 24px rgba(15, 23, 42, 0.08)',
  },
  empty: {
    padding: 'var(--space-12)',
    textAlign: 'center',
  },
};
