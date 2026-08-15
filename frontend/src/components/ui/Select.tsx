import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

export interface SelectOption {
  label: string;
  value: string;
}

interface SelectProps {
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  style?: React.CSSProperties;
  className?: string;
}

export default function Select({
  value,
  onChange,
  options,
  placeholder = 'Select...',
  style = {},
  className = '',
}: SelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedOption = options.find((opt) => opt.value === value);

  return (
    <div
      ref={containerRef}
      className={`custom-select ${className}`}
      style={{ position: 'relative', ...style }}
    >
      <button
        type="button"
        className="select-trigger glass-card"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          width: '100%',
          padding: 'var(--space-2) var(--space-4)',
          minHeight: '40px',
          background: 'var(--color-surface)',
          border: '1px solid var(--glass-border)',
          borderRadius: 'var(--radius-lg)',
          color: selectedOption ? 'var(--color-on-surface)' : 'var(--color-on-surface-variant)',
          fontSize: 'var(--text-small)',
          fontFamily: 'var(--font-body)',
          cursor: 'pointer',
          outline: 'none',
          gap: 'var(--space-3)',
          boxShadow: 'var(--shadow-sm)',
          transition: 'border-color var(--transition-base), box-shadow var(--transition-base), transform var(--transition-fast)',
        }}
      >
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <ChevronDown
          size={16}
          style={{
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform var(--transition-base)',
            color: 'var(--color-outline)',
            flexShrink: 0,
          }}
        />
      </button>

      {isOpen && (
        <div
          className="select-dropdown glass-card animate-in"
          style={{
            position: 'absolute',
            top: 'calc(100% + var(--space-2))',
            left: 0,
            width: '100%',
            maxHeight: '250px',
            overflowY: 'auto',
            zIndex: 50,
            padding: 'var(--space-1)',
            transformOrigin: 'top center',
            background: 'var(--color-surface)',
            boxShadow: 'var(--shadow-lg)',
          }}
        >
          {options.map((option) => {
            const isSelected = option.value === value;
            return (
              <button
                key={option.value}
                type="button"
                className="select-option"
                onClick={() => {
                  onChange(option.value);
                  setIsOpen(false);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  width: '100%',
                  padding: 'var(--space-2) var(--space-3)',
                  border: 'none',
                  background: isSelected ? 'var(--color-primary-muted)' : 'transparent',
                  color: isSelected ? 'var(--color-primary-dim)' : 'var(--color-on-surface)',
                  fontSize: 'var(--text-small)',
                  fontFamily: 'var(--font-body)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-md)',
                  transition: 'background-color var(--transition-fast)',
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) e.currentTarget.style.background = 'var(--color-surface-container-low)';
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) e.currentTarget.style.background = 'transparent';
                }}
              >
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {option.label}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
