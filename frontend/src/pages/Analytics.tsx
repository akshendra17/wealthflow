import React, { useState, useEffect } from 'react';
import { getTrends, getMonthlySummary } from '../services/api';
import { MONTH_NAMES, MONTH_SHORT, CATEGORY_CONFIG } from '../utils/constants';
import { formatCurrency } from '../utils/formatters';
import TrendChart from '../components/charts/TrendChart';
import CategoryRingChart from '../components/charts/CategoryRingChart';
import Select from '../components/ui/Select';
import EmptyState from '../components/ui/EmptyState';
import { useBankFilter } from '../context/BankFilterContext';
import { BANK_OPTIONS } from '../utils/constants';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';

export default function Analytics() {
  const { bankName, setBankName } = useBankFilter();
  const [trends, setTrends] = useState<any>(null);
  const [selectedMonth, setSelectedMonth] = useState<any>(null);
  const [monthData, setMonthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const t = await getTrends(12, bankName || undefined);
        setTrends(t);
        if (t.months?.length) {
          const latest = t.months.at(-1);
          setSelectedMonth(latest);
          const md = await getMonthlySummary(latest.year, latest.month, bankName || undefined);
          setMonthData(md);
        } else {
          setSelectedMonth(null);
          setMonthData(null);
        }
      } catch { /* pass */ } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [bankName]);

  const handleMonthChange = async (e: any) => {
    const [year, month] = e.target.value.split('-').map(Number);
    setSelectedMonth({ year, month });
    try {
      const md = await getMonthlySummary(year, month, bankName || undefined);
      setMonthData(md);
    } catch { /* pass */ }
  };

  if (loading) {
    return (
      <div>
        <div className="skeleton" style={{ height: 400, borderRadius: 16, marginBottom: 24 }} />
        <div className="skeleton" style={{ height: 300, borderRadius: 16 }} />
      </div>
    );
  }

  // Build bar chart data from monthData
  const barData = monthData?.categories?.map((c: any) => ({
    name: c.category,
    amount: c.total_amount,
    color: CATEGORY_CONFIG[c.category]?.color || '#859399',
  })) || [];

  return (
    <div>
      <div style={styles.headerRow}>
        <h2 style={styles.pageTitle}>Analytics</h2>
        <div style={{ display: 'flex', gap: 'var(--space-4)' }}>
          <Select
            value={bankName}
            onChange={setBankName}
            options={BANK_OPTIONS}
            style={{ width: 180 }}
          />
          {trends?.months?.length > 0 && (
            <Select
              value={selectedMonth ? `${selectedMonth.year}-${selectedMonth.month}` : ''}
              onChange={(val) => handleMonthChange({ target: { value: val } })}
              options={trends.months.map((m: any) => ({
                label: `${MONTH_NAMES[m.month]} ${m.year}`,
                value: `${m.year}-${m.month}`,
              }))}
              style={{ width: 180 }}
            />
          )}
        </div>
      </div>

      {/* Conditional rendering based on data availability */}
      {trends?.months?.length > 0 ? (
        <>
          {/* Trend Chart */}
          <div style={{ marginBottom: 'var(--space-8)' }}>
            <TrendChart trends={trends} />
          </div>

          {/* Month Breakdown */}
          <div style={styles.chartRow}>
            {/* Bar Chart */}
            <div className="glass-card" style={{ flex: 2, padding: 'var(--space-6)' }}>
              <h3 style={styles.sectionTitle}>
                Category Comparison — {selectedMonth ? `${MONTH_SHORT[selectedMonth.month]} ${selectedMonth.year}` : ''}
              </h3>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={barData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#859399', fontSize: 11, fontFamily: 'Inter' }}
                    angle={-35}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#859399', fontSize: 12, fontFamily: 'Inter' }}
                    tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}K`}
                  />
                  <Tooltip
                    cursor={{ fill: 'rgba(255, 255, 255, 0.04)' }}
                    contentStyle={{
                      background: 'rgba(20,20,20,0.95)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: 12,
                      padding: '10px 14px',
                    }}
                    itemStyle={{ color: '#e5e2e1', fontSize: '13px' }}
                    formatter={(value: any) => formatCurrency(value as number)}
                    labelStyle={{ color: '#e5e2e1', fontWeight: 600 }}
                  />
                  <Bar dataKey="amount" radius={[6, 6, 0, 0]} maxBarSize={40}>
                    {barData.map((entry: any) => (
                      <Cell
                        key={entry.name}
                        fill={entry.color}
                        style={{ filter: `drop-shadow(0 0 4px ${entry.color}40)` }}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Ring Chart */}
            <div style={{ flex: 1 }}>
              {monthData && (
                <CategoryRingChart
                  categories={monthData.categories}
                  totalExpenses={monthData.total_expenses}
                />
              )}
            </div>
          </div>
        </>
      ) : (
        <EmptyState 
          title="No Analytics Available" 
          description="Upload a bank statement to unlock spending trends and category insights."
        />
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  headerRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 'var(--space-6)',
    position: 'relative',
    zIndex: 10,
  },
  pageTitle: {
    fontSize: 'var(--text-h1)',
    fontWeight: 600,
  },
  monthSelect: {
    padding: 'var(--space-2) var(--space-4)',
    background: 'var(--color-surface-container)',
    border: '1px solid var(--glass-border)',
    borderRadius: 'var(--radius-lg)',
    color: 'var(--color-on-surface)',
    fontSize: 'var(--text-small)',
    fontFamily: 'var(--font-body)',
    outline: 'none',
  },
  chartRow: {
    display: 'flex',
    gap: 'var(--space-6)',
  },
  sectionTitle: {
    fontSize: 'var(--text-h3)',
    fontWeight: 600,
    marginBottom: 'var(--space-4)',
  },
};
