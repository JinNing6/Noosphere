/**
 * LanguageSwitcher — 浮动语言切换器
 *
 * 玻璃拟态风格，放置在页面右上角。
 * 点击 🌐 图标展开语言列表。
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES } from '../i18n';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // 点击外部关闭
  const handleClickOutside = useCallback((e: MouseEvent) => {
    if (ref.current && !ref.current.contains(e.target as Node)) {
      setOpen(false);
    }
  }, []);

  useEffect(() => {
    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [open, handleClickOutside]);

  const currentLang = SUPPORTED_LANGUAGES.find(l => i18n.language?.startsWith(l.code))
    || SUPPORTED_LANGUAGES[1]; // fallback to English

  return (
    <div ref={ref} style={containerStyle}>
      {/* 触发按钮 */}
      <button
        onClick={() => setOpen(prev => !prev)}
        style={buttonStyle}
        aria-label="Switch language"
        title="Switch language"
      >
        <span style={{ fontSize: 16 }}>🌐</span>
        <span style={{ fontSize: 11, opacity: 0.8, marginLeft: 4 }}>
          {currentLang.code.toUpperCase()}
        </span>
      </button>

      {/* 下拉菜单 */}
      {open && (
        <div style={dropdownStyle}>
          {SUPPORTED_LANGUAGES.map(lang => {
            const isActive = currentLang.code === lang.code;
            return (
              <button
                key={lang.code}
                onClick={() => {
                  i18n.changeLanguage(lang.code);
                  setOpen(false);
                }}
                style={{
                  ...itemStyle,
                  background: isActive ? 'rgba(123, 97, 255, 0.25)' : 'transparent',
                  color: isActive ? '#7b61ff' : '#e0e0ff',
                }}
              >
                <span style={{ fontSize: 14 }}>{lang.flag}</span>
                <span style={{ fontSize: 12, marginLeft: 8 }}>{lang.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ─── Styles ─── */

const containerStyle: React.CSSProperties = {
  position: 'fixed',
  top: 16,
  right: 16,
  zIndex: 1000,
  fontFamily: "'Inter', 'Noto Sans SC', 'Noto Sans JP', 'Noto Sans KR', sans-serif",
};

const buttonStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 2,
  padding: '6px 12px',
  background: 'rgba(15, 15, 35, 0.75)',
  backdropFilter: 'blur(16px)',
  WebkitBackdropFilter: 'blur(16px)',
  border: '1px solid rgba(123, 97, 255, 0.25)',
  borderRadius: 20,
  color: '#e0e0ff',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  boxShadow: '0 2px 12px rgba(0, 0, 0, 0.3)',
};

const dropdownStyle: React.CSSProperties = {
  position: 'absolute',
  top: 'calc(100% + 8px)',
  right: 0,
  minWidth: 140,
  background: 'rgba(15, 15, 35, 0.92)',
  backdropFilter: 'blur(20px)',
  WebkitBackdropFilter: 'blur(20px)',
  border: '1px solid rgba(123, 97, 255, 0.25)',
  borderRadius: 12,
  padding: '6px 0',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
  animation: 'fadeIn 0.2s ease',
};

const itemStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  width: '100%',
  padding: '8px 16px',
  border: 'none',
  cursor: 'pointer',
  transition: 'background 0.2s ease',
  textAlign: 'left',
};
