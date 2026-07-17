import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { CATEGORY_CONFIG, MONTH_SHORT } from '../../utils/constants';
import { formatCurrency, formatCurrencyCompact } from '../../utils/formatters';

export default function TrendChart({ trends }: { trends: any }) {
  if (!trends || !trends.months?.length) {
    return (
      <div className="glass-card" style={styles.empty}>
        <p className="text-muted">No trend data available. Upload at least 2 months of statements.</p>
      </div>
    );
  }

  // Build chart data
  const chartData = trends.months.map((m: any, i: number) => ({
    name: `${MONTH_SHORT[m.month]} ${String(m.year).slice(2)}`,
    total: trends.totals[i],
    ...Object.fromEntries(
      Object.entries(trends.category_trends).map(([cat, vals]) => [cat, (vals as number[])[i] || 0])
    ),
  }));

  // Top 5 categories by latest month total
  const topCategories = Object.entries(trends.category_trends)
    .map(([cat, vals]) => ({ cat, latest: (vals as number[]).at(-1) || 0 }))
    .sort((a, b) => b.latest - a.latest)
    .slice(0, 5)
    .map((c) => c.cat);

  return (
    <div className="glass-card" style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Expense Velocity</h3>
        <span className="text-caption">Last {trends.months.length} months</span>
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id="gradTotal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00d1ff" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00d1ff" stopOpacity={0} />
            </linearGradient>
            {topCategories.map((cat) => {
              const color = CATEGORY_CONFIG[cat]?.color || '#859399';
              return (
                <linearGradient key={cat} id={`grad-${cat}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={color} stopOpacity={0.2} />
                  <stop offset="95%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              );
            })}
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255,255,255,0.05)"
            vertical={false}
          />
          <XAxis
            dataKey="name"
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#859399', fontSize: 12, fontFamily: 'Inter' }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#859399', fontSize: 12, fontFamily: 'Inter' }}
            tickFormatter={formatCurrencyCompact}
          />
          <Tooltip
            contentStyle={styles.tooltip}
            labelStyle={{ color: '#e5e2e1', fontWeight: 600, marginBottom: 8 }}
            itemStyle={{ fontSize: 13 }}
            formatter={(value: any) => formatCurrency(value as number)}
          />
          <Area
            type="monotone"
            dataKey="total"
            stroke="#00d1ff"
            strokeWidth={2.5}
            fill="url(#gradTotal)"
            name="Total"
            dot={false}
            activeDot={{ r: 5, fill: '#00d1ff', stroke: '#0a0a0a', strokeWidth: 2 }}
          />
          {topCategories.map((cat) => {
            const color = CATEGORY_CONFIG[cat]?.color || '#859399';
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
            wrapperStyle={{ fontSize: 12, fontFamily: 'Inter', color: '#bbc9cf' }}
          />
        </AreaChart>
      </ResponsiveContainer>
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
    background: 'rgba(20, 20, 20, 0.95)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 12,
    padding: '12px 16px',
    backdropFilter: 'blur(10px)',
    boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
  },
  empty: {
    padding: 'var(--space-12)',
    textAlign: 'center',
  },
};
