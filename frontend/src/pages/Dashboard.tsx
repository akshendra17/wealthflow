import React, { useState, useEffect, useRef, useCallback } from 'react';
import { TrendingDown, TrendingUp, DollarSign, CreditCard, ArrowUpRight, X } from 'lucide-react';
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
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const transactionsRef = useRef<HTMLDivElement>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [dashData, txnData] = await Promise.all([
        getDashboard(bankName || undefined),
        getTransactions({
          page: 1,
          pageSize: 15,
          type: 'DEBIT',
          bankName: bankName || undefined,
          category: categoryFilter || undefined,
        }),
      ]);
      setDashboard(dashData);
      setTransactions(txnData.items);
    } catch (err: any) {
      console.error(err.message);
    } finally {
      setLoading(false);
    }
  }, [bankName, categoryFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCategorySelect = (category: string) => {
    setCategoryFilter((prev) => (prev === category ? null : category));
    requestAnimationFrame(() => {
      transactionsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  };

  const handleResetFilter = () => {
    setCategoryFilter(null);
  };

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
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 'var(--space-6)' }}>
        <Select
          value={bankName}
          onChange={setBankName}
          options={BANK_OPTIONS}
          style={{ width: 220 }}
        />
      </div>

      <div style={styles.heroRow} className="animate-in">
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
                  background: mom <= 0 ? 'var(--color-success-muted)' : 'var(--color-error-muted)',
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
        </div>

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

      {hasData && dashboard.categories?.length > 0 && (
        <div style={styles.section} className="animate-in animate-in-delay-2">
          <div style={styles.sectionHeader}>
            <h2 style={styles.sectionTitle}>Spending Breakdown</h2>
            {categoryFilter && (
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={handleResetFilter}
                style={styles.resetBtn}
              >
                <X size={14} />
                Reset filter
              </button>
            )}
          </div>
          <div className="carousel">
            {dashboard.categories.slice(0, 8).map((cat: any, idx: number) => (
              <div
                key={cat.category}
                style={{
                  minWidth: 260,
                  flexShrink: 0,
                  animationDelay: `${idx * 60}ms`,
                  opacity: 0,
                }}
                className="animate-in"
              >
                <StatCard
                  category={cat.category}
                  amount={cat.total_amount}
                  count={cat.transaction_count}
                  percentage={cat.percentage}
                  selected={categoryFilter === cat.category}
                  onClick={handleCategorySelect}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {hasData && (
        <div className="chart-row animate-in animate-in-delay-3" style={styles.chartRow}>
          <div style={{ flex: 2 }}>
            <TrendChart trends={dashboard.trends} />
          </div>
          <div style={{ flex: 1 }}>
            <CategoryRingChart
              categories={dashboard.categories}
              totalExpenses={dashboard.total_expenses}
              selectedCategory={categoryFilter}
              onCategorySelect={handleCategorySelect}
            />
          </div>
        </div>
      )}

      <div ref={transactionsRef} style={styles.section}>
        {(transactions.length > 0 || categoryFilter) && (
          <div className="animate-in animate-in-delay-4">
            <TransactionList
              transactions={transactions}
              filterCategory={categoryFilter}
              onResetFilter={handleResetFilter}
            />
          </div>
        )}
      </div>

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
    background: 'var(--color-primary-muted)',
    border: '1px solid rgba(13, 148, 136, 0.15)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
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
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 'var(--space-5)',
    gap: 'var(--space-4)',
  },
  sectionTitle: {
    fontSize: 'var(--text-h2)',
    fontWeight: 600,
    marginBottom: 0,
  },
  resetBtn: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 'var(--space-1)',
  },
  chartRow: {
    marginTop: 'var(--space-8)',
  },
};
