import React, { useState, useEffect } from 'react';
import { TrendingDown, TrendingUp, DollarSign, CreditCard, ArrowUpRight } from 'lucide-react';
import { getDashboard, getTransactions } from '../services/api';
import { formatCurrency, formatPercent } from '../utils/formatters';
import { MONTH_NAMES } from '../utils/constants';
import StatCard from '../components/ui/StatCard';
import TrendChart from '../components/charts/TrendChart';
import CategoryRingChart from '../components/charts/CategoryRingChart';
import TransactionList from '../components/transactions/TransactionList';
import EmptyState from '../components/ui/EmptyState';
import Select from '../components/ui/Select';
import { useBankFilter } from '../context/BankFilterContext';
import { BANK_OPTIONS } from '../utils/constants';

export default function Dashboard() {
  const { bankName, setBankName } = useBankFilter();
  const [dashboard, setDashboard] = useState<any>(null);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [dashData, txnData] = await Promise.all([
        getDashboard(bankName || undefined),
        getTransactions({ page: 1, pageSize: 15, type: 'DEBIT', bankName: bankName || undefined }),
      ]);
      setDashboard(dashData);
      setTransactions(txnData.items);
    } catch (err: any) {
      console.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [bankName]);

  if (loading) {
    return (
      <div style={styles.loadingGrid}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: i < 2 ? 160 : 80, borderRadius: 16 }} />
        ))}
      </div>
    );
  }

  const hasData = dashboard?.has_data;
  const mom = dashboard?.trends?.mom_change_pct;
  const latestMonth = dashboard?.latest_month;

  return (
    <div>
      {/* ── Filters ── */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 'var(--space-6)' }}>
        <Select
          value={bankName}
          onChange={setBankName}
          options={BANK_OPTIONS}
          style={{ width: 220 }}
        />
      </div>

      {/* ── Hero Section ── */}
      <div style={styles.heroRow} className="animate-in">
        {/* Total Expenses Card */}
        <div className="glass-card" style={styles.heroCard}>
          <div style={styles.heroInner}>
            <div>
              <span className="text-caption">
                {hasData
                  ? `${MONTH_NAMES[latestMonth.month]} ${latestMonth.year}`
                  : 'No Data Yet'}
              </span>
              <div style={styles.heroAmount}>
                {hasData ? formatCurrency(dashboard.total_expenses) : '₹0'}
              </div>
              {mom != null && (
                <div style={{
                  ...styles.momBadge,
                  color: mom <= 0 ? 'var(--color-tertiary)' : 'var(--color-error)',
                  background: mom <= 0 ? 'rgba(0, 252, 146, 0.1)' : 'rgba(255, 180, 171, 0.1)',
                }}>
                  {mom <= 0 ? <TrendingDown size={14} /> : <TrendingUp size={14} />}
                  {formatPercent(mom)} from last month
                </div>
              )}
            </div>
            <div style={styles.heroIconWrap}>
              <DollarSign size={32} color="var(--color-primary)" />
            </div>
          </div>
          {/* Decorative gradient */}
          <div style={styles.heroGradient} />
        </div>

        {/* Quick Stats */}
        <div className="glass-card" style={styles.quickStats}>
          <div style={styles.quickRow}>
            <div style={styles.quickItem}>
              <CreditCard size={18} color="var(--color-secondary-soft)" />
              <div>
                <span className="text-caption">Categories</span>
                <span style={styles.quickVal}>{dashboard?.category_count || 0}</span>
              </div>
            </div>
            <div style={styles.quickDivider} />
            <div style={styles.quickItem}>
              <ArrowUpRight size={18} color="var(--color-tertiary)" />
              <div>
                <span className="text-caption">Top Spend</span>
                <span style={styles.quickVal}>
                  {dashboard?.categories?.[0]?.category || '—'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Category Cards Grid ── */}
      {hasData && dashboard.categories?.length > 0 && (
        <div style={styles.section} className="animate-in animate-in-delay-2">
          <h2 style={styles.sectionTitle}>Spending Breakdown</h2>
          <div className="carousel">
            {dashboard.categories.slice(0, 8).map((cat: any) => (
              <div key={cat.category} style={{ minWidth: 260, flexShrink: 0 }}>
                <StatCard
                  category={cat.category}
                  amount={cat.total_amount}
                  count={cat.transaction_count}
                  percentage={cat.percentage}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Charts Row ── */}
      {hasData && (
        <div style={styles.chartRow} className="animate-in animate-in-delay-3">
          <div style={{ flex: 2 }}>
            <TrendChart trends={dashboard.trends} />
          </div>
          <div style={{ flex: 1 }}>
            <CategoryRingChart
              categories={dashboard.categories}
              totalExpenses={dashboard.total_expenses}
            />
          </div>
        </div>
      )}

      {/* ── Transactions ── */}
      {transactions.length > 0 && (
        <div style={styles.section} className="animate-in animate-in-delay-4">
          <TransactionList transactions={transactions} />
        </div>
      )}

      {!hasData && (
        <EmptyState />
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  loadingGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: 'var(--space-6)',
  },
  heroRow: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr',
    gap: 'var(--space-6)',
    marginBottom: 'var(--space-6)',
  },
  heroCard: {
    padding: 'var(--space-8)',
    position: 'relative',
    overflow: 'hidden',
  },
  heroInner: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    position: 'relative',
    zIndex: 1,
  },
  heroAmount: {
    fontFamily: 'var(--font-heading)',
    fontSize: 'clamp(2rem, 1.5rem + 2vw, 3rem)',
    fontWeight: 700,
    color: 'var(--color-on-surface)',
    letterSpacing: '-0.02em',
    marginTop: 'var(--space-2)',
    marginBottom: 'var(--space-3)',
  },
  momBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 'var(--space-2)',
    padding: 'var(--space-1) var(--space-3)',
    borderRadius: 'var(--radius-full)',
    fontSize: 'var(--text-small)',
    fontWeight: 600,
  },
  heroIconWrap: {
    width: 60,
    height: 60,
    borderRadius: 'var(--radius-xl)',
    background: 'rgba(0, 209, 255, 0.08)',
    border: '1px solid rgba(0, 209, 255, 0.15)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  heroGradient: {
    position: 'absolute',
    bottom: -40,
    right: -40,
    width: 200,
    height: 200,
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(0,209,255,0.1) 0%, transparent 70%)',
    pointerEvents: 'none',
  },
  quickStats: {
    padding: 'var(--space-6)',
    display: 'flex',
    alignItems: 'center',
  },
  quickRow: {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-5)',
    width: '100%',
  },
  quickItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-3)',
  },
  quickVal: {
    display: 'block',
    fontFamily: 'var(--font-heading)',
    fontSize: '1.1rem',
    fontWeight: 700,
    color: 'var(--color-on-surface)',
    marginTop: 2,
  },
  quickDivider: {
    height: 1,
    background: 'var(--glass-border)',
  },
  section: {
    marginTop: 'var(--space-8)',
  },
  sectionTitle: {
    fontSize: 'var(--text-h2)',
    fontWeight: 600,
    marginBottom: 'var(--space-5)',
  },
  chartRow: {
    display: 'flex',
    gap: 'var(--space-6)',
    marginTop: 'var(--space-8)',
  },
};
