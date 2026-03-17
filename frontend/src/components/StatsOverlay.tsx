/**
 * @preview
 * StatsOverlay — 三层统计 HUD
 */

import { useTranslation } from 'react-i18next';
import { LAYER_STATS, LAYER_COLORS, DISCIPLINE_COLORS } from '../data/knowledge';

const LAYER_KEYS = [
  { key: 'matter', icon: '⚛️', color: LAYER_COLORS.matter },
  { key: 'life', icon: '🧬', color: LAYER_COLORS.life },
  { key: 'civilization', icon: '🌌', color: LAYER_COLORS.civilization },
] as const;

const DISCIPLINE_KEYS = [
  { key: 'math', color: DISCIPLINE_COLORS.math },
  { key: 'physics', color: DISCIPLINE_COLORS.physics },
  { key: 'biology', color: DISCIPLINE_COLORS.biology },
  { key: 'philosophy', color: DISCIPLINE_COLORS.philosophy },
  { key: 'art', color: DISCIPLINE_COLORS.art },
  { key: 'engineering', color: DISCIPLINE_COLORS.engineering },
  { key: 'history', color: DISCIPLINE_COLORS.history },
  { key: 'ai', color: DISCIPLINE_COLORS.ai },
] as const;

export default function StatsOverlay({ dynamicNodeCount = 0 }: { dynamicNodeCount?: number }) {
  const { t } = useTranslation();

  return (
    <div style={{
      position: 'absolute', bottom: 24, left: 24,
      fontFamily: "'Inter', sans-serif",
      color: 'rgba(255,255,255,0.6)', fontSize: 12,
      pointerEvents: 'none', userSelect: 'none',
      maxWidth: 260,
    }}>
      {/* 品牌 */}
      <div style={{ marginBottom: 16 }}>
        <div style={{
          fontSize: 16, fontWeight: 700, color: '#e0e0ff',
          letterSpacing: '0.15em', marginBottom: 2,
        }}>
          🧠 NOOSPHERE
        </div>
        <div style={{ fontSize: 10, letterSpacing: '0.1em', opacity: 0.4 }}>
          THE COLLECTIVE CONSCIOUSNESS NETWORK
        </div>
      </div>

      {/* 三层统计 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 14 }}>
        {LAYER_KEYS.map(l => (
          <div key={l.key} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{
              width: 8, height: 8, borderRadius: '50%',
              background: l.color, boxShadow: `0 0 6px ${l.color}80`,
            }} />
            <span style={{ minWidth: 60 }}>{l.icon} {t(`layers.${l.key}`)}</span>
            <span style={{ color: l.color, fontWeight: 600 }}>
              {LAYER_STATS[l.key as keyof typeof LAYER_STATS]}
            </span>
          </div>
        ))}
        {/* 实时意识体统计 */}
        {dynamicNodeCount > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{
              width: 8, height: 8, borderRadius: '50%',
              background: '#00d4ff', boxShadow: '0 0 6px #00d4ff80',
              animation: 'pulse 2s ease-in-out infinite',
            }} />
            <span style={{ minWidth: 60 }}>💭 {t('stats.dynamicLabel')}</span>
            <span style={{ color: '#00d4ff', fontWeight: 600 }}>
              {dynamicNodeCount}
            </span>
          </div>
        )}
        <div style={{
          borderTop: '1px solid rgba(255,255,255,0.06)',
          paddingTop: 6, marginTop: 2,
          display: 'flex', justifyContent: 'space-between',
        }}>
          <span>{t('stats.totalNodes')} {LAYER_STATS.total + dynamicNodeCount} · {t('stats.totalLinks')} {LAYER_STATS.links}</span>
        </div>
      </div>

      {/* 学科色板 */}
      <div style={{
        display: 'flex', flexWrap: 'wrap', gap: 4,
      }}>
        {DISCIPLINE_KEYS.map(d => (
          <div key={d.key} style={{
            display: 'flex', alignItems: 'center', gap: 4,
            padding: '2px 6px', borderRadius: 4,
            background: `${d.color}10`,
            fontSize: 10,
          }}>
            <div style={{ width: 6, height: 6, borderRadius: 2, background: d.color }} />
            {t(`disciplines.${d.key}`)}
          </div>
        ))}
      </div>

      {/* 交互提示 */}
      <div style={{
        marginTop: 14, fontSize: 10, opacity: 0.3,
        borderTop: '1px solid rgba(255,255,255,0.04)',
        paddingTop: 8,
      }}>
        {t('stats.clickHint')}
      </div>
    </div>
  );
}
