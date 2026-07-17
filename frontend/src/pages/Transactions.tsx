import React, { useState, useEffect } from 'react';
import { getTransactions } from '../services/api';
import { CATEGORY_CONFIG } from '../utils/constants';
import TransactionList from '../components/transactions/TransactionList';
import Select from '../components/ui/Select';

import type { Transaction } from '../types';

export default function Transactions() {
  const [data, setData] = useState<{items: Transaction[], total: number, has_next?: boolean}>({ items: [], total: 0 });
  const [filters, setFilters] = useState({ page: 1, category: '', search: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const res = await getTransactions({
          page: filters.page,
          pageSize: 30,
          category: filters.category || undefined,
          search: filters.search || undefined,
        });
        setData(res);
      } catch {
        /* handled in UI */
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [filters]);

  return (
    <div>
      <h2 style={styles.pageTitle}>All Transactions</h2>

      {/* Filters */}
      <div style={styles.filtersRow}>
        <input
          type="text"
          placeholder="Search descriptions..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
          style={styles.searchInput}
        />
        <Select
          value={filters.category}
          onChange={(val) => setFilters({ ...filters, category: val, page: 1 })}
          options={[
            { label: 'All Categories', value: '' },
            ...Object.keys(CATEGORY_CONFIG).map((cat) => ({
              label: `${CATEGORY_CONFIG[cat].icon} ${cat}`,
              value: cat,
            }))
          ]}
          style={{ width: 220 }}
        />
      </div>

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 52, borderRadius: 10 }} />
          ))}
        </div>
      ) : (
        <>
          <TransactionList transactions={data.items} />
          {/* Pagination */}
          {data.total > 30 && (
            <div style={styles.pagination}>
              <button
                className="btn btn-ghost btn-sm"
                disabled={filters.page <= 1}
                onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
              >
                ← Previous
              </button>
              <span className="text-caption">
                Page {filters.page} of {Math.ceil(data.total / 30)}
              </span>
              <button
                className="btn btn-ghost btn-sm"
                disabled={!data.has_next}
                onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  pageTitle: {
    fontSize: 'var(--text-h1)',
    fontWeight: 600,
    marginBottom: 'var(--space-6)',
  },
  filtersRow: {
    display: 'flex',
    gap: 'var(--space-4)',
    marginBottom: 'var(--space-6)',
    position: 'relative',
    zIndex: 10,
  },
  searchInput: {
    flex: 1,
    padding: 'var(--space-3) var(--space-4)',
    background: 'var(--color-surface-container)',
    border: '1px solid var(--glass-border)',
    borderRadius: 'var(--radius-lg)',
    color: 'var(--color-on-surface)',
    fontSize: 'var(--text-small)',
    fontFamily: 'var(--font-body)',
    outline: 'none',
  },
  select: {
    padding: 'var(--space-3) var(--space-4)',
    background: 'var(--color-surface-container)',
    border: '1px solid var(--glass-border)',
    borderRadius: 'var(--radius-lg)',
    color: 'var(--color-on-surface)',
    fontSize: 'var(--text-small)',
    fontFamily: 'var(--font-body)',
    outline: 'none',
    minWidth: 180,
  },
  pagination: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 'var(--space-4)',
    marginTop: 'var(--space-6)',
  },
};
