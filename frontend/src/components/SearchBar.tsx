/**
 * @preview
 * SearchBar — 知识搜索栏
 */

import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

interface SearchBarProps {
  onSearch: (query: string) => void;
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setQuery(val);
    onSearch(val);
  }, [onSearch]);

  return (
    <div style={{
      position: 'absolute', top: 24,
      left: '50%', transform: 'translateX(-50%)',
      zIndex: 40,
      pointerEvents: 'auto',
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '10px 20px',
        background: 'rgba(15, 12, 30, 0.7)',
        backdropFilter: 'blur(16px)',
        borderRadius: 28,
        border: '1px solid rgba(123, 97, 255, 0.15)',
        minWidth: 360,
        transition: 'border-color 0.3s',
      }}>
        <span style={{ fontSize: 16, opacity: 0.5 }}>🔍</span>
        <input
          type="text"
          value={query}
          onChange={handleChange}
          placeholder={t('search.placeholder')}
          style={{
            background: 'none', border: 'none', outline: 'none',
            color: '#e0e0ff', fontSize: 14,
            fontFamily: "'Inter', sans-serif",
            width: '100%',
          }}
        />
        {query && (
          <button
            onClick={() => { setQuery(''); onSearch(''); }}
            style={{
              background: 'none', border: 'none', color: '#888',
              cursor: 'pointer', fontSize: 14, padding: '0 4px',
            }}
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
