import React from 'react';
import { X } from 'lucide-react';
import { CATEGORY_CONFIG } from '../../utils/constants';
import { formatCurrency, formatDate } from '../../utils/formatters';

import type { Transaction } from '../../types';

interface TransactionListProps {
  transactions: Transaction[];
  filterCategory?: string | null;
  onResetFilter?: () => void;
}

export default function TransactionList({
  transactions,
  filterCategory = null,
  onResetFilter,
}: TransactionListProps) {
  if (!transactions?.length) {
    return (
      <div className="glass-card animate-in" style={{ padding: 'var(--space-8)', textAlign: 'center' }}>
        <p className="text-muted">
          {filterCategory
            ? `No transactions found for ${filterCategory}.`
            : 'No transactions found.'}
        </p>
        {filterCategory && onResetFilter && (
          <button className="btn btn-ghost btn-sm" onClick={onResetFilter} style={{ marginTop: 'var(--space-4)' }}>
            Reset filter
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="glass-card animate-in-scale" style={styles.container} key={filterCategory ?? 'all'}>
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <h3 style={styles.title}>Recent Transactions</h3>
          {filterCategory && (
            <span className="filter-chip">
              {CATEGORY_CONFIG[filterCategory]?.icon} {filterCategory}
            </span>
          )}
        </div>
        <div style={styles.headerRight}>
          {filterCategory && onResetFilter && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={onResetFilter}
              style={styles.resetBtn}
            >
              <X size={14} />
              Reset
            </button>
          )}
          <span className="text-caption">{transactions.length} items</span>
        </div>
      </div>
      <div style={styles.list}>
        {transactions.map((txn, idx) => {
          const config = CATEGORY_CONFIG[txn.category] || CATEGORY_CONFIG.Misc;
          const isDebit = txn.transaction_type === 'DEBIT';
          return (
            <div
              key={txn.id}
              style={{
                ...styles.row,
                animationDelay: `${idx * 50}ms`,
                borderBottom: idx < transactions.length - 1 ? '1px solid var(--glass-border)' : 'none',
              }}
              className="animate-in tx-row"
            >
              <div style={{ ...styles.icon, background: `${config.color}12`, border: `1px solid ${config.color}25` }}>
                <span>{config.icon}</span>
              </div>

              <div style={styles.info}>
                <span style={styles.desc}>{txn.description}</span>
                <span style={styles.dateCat}>
                  {formatDate(txn.transaction_date)} •{' '}
                  <span style={{ color: config.color }}>{txn.category}</span>
                </span>
              </div>

              <div style={styles.amountWrap}>
                <span style={{
                  ...styles.amount,
                  color: isDebit ? 'var(--color-error)' : 'var(--color-tertiary)',
                }}>
                  {isDebit ? '-' : '+'}{formatCurrency(txn.amount)}
                </span>
                <span style={styles.typeTag}>
                  {txn.transaction_type}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: 0,
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 'var(--space-5) var(--space-6)',
    borderBottom: '1px solid var(--glass-border)',
    gap: 'var(--space-4)',
    flexWrap: 'wrap',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-3)',
    flexWrap: 'wrap',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-3)',
  },
  title: {
    fontSize: 'var(--text-h3)',
    fontWeight: 600,
  },
  resetBtn: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 'var(--space-1)',
  },
  list: {
    maxHeight: 480,
    overflowY: 'auto',
  },
  row: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-4)',
    padding: 'var(--space-4) var(--space-6)',
    transition: 'background-color var(--transition-base)',
    cursor: 'default',
  },
  icon: {
    width: 38,
    height: 38,
    borderRadius: 'var(--radius-md)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1rem',
    flexShrink: 0,
  },
  info: {
    flex: 1,
    minWidth: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
  },
  desc: {
    fontSize: 'var(--text-small)',
    fontWeight: 500,
    color: 'var(--color-on-surface)',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  dateCat: {
    fontSize: 'var(--text-caption)',
    color: 'var(--color-on-surface-variant)',
  },
  amountWrap: {
    textAlign: 'right',
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    flexShrink: 0,
  },
  amount: {
    fontSize: 'var(--text-data)',
    fontWeight: 600,
    fontVariantNumeric: 'tabular-nums',
  },
  typeTag: {
    fontSize: '0.625rem',
    fontWeight: 600,
    letterSpacing: '0.06em',
    color: 'var(--color-outline)',
  },
};
