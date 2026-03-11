/**
 * @preview
 * StatsOverlay — 三层统计 HUD
 */

import { LAYER_STATS, LAYER_COLORS, DISCIPLINE_COLORS } from '../data/knowledge';

const LAYER_INFO = [
  { key: 'matter', label: '物质记忆', icon: '⚛️', color: LAYER_COLORS.matter },
  { key: 'life', label: '生命经验', icon: '🧬', color: LAYER_COLORS.life },
  { key: 'civilization', label: '文明智慧', icon: '🌌', color: LAYER_COLORS.civilization },
];

const DISCIPLINES = [
  { key: 'math', label: '数学', color: DISCIPLINE_COLORS.math },
  { key: 'physics', label: '物理', color: DISCIPLINE_COLORS.physics },
  { key: 'biology', label: '生命', color: DISCIPLINE_COLORS.biology },
  { key: 'philosophy', label: '哲学', color: DISCIPLINE_COLORS.philosophy },
  { key: 'art', label: '艺术', color: DISCIPLINE_COLORS.art },
  { key: 'engineering', label: '工程', color: DISCIPLINE_COLORS.engineering },
  { key: 'history', label: '历史', color: DISCIPLINE_COLORS.history },
  { key: 'ai', label: 'AI', color: DISCIPLINE_COLORS.ai },
];

export default function StatsOverlay() {
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
        {LAYER_INFO.map(l => (
          <div key={l.key} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{
              width: 8, height: 8, borderRadius: '50%',
              background: l.color, boxShadow: `0 0 6px ${l.color}80`,
            }} />
            <span style={{ minWidth: 60 }}>{l.icon} {l.label}</span>
            <span style={{ color: l.color, fontWeight: 600 }}>
              {LAYER_STATS[l.key as keyof typeof LAYER_STATS]}
            </span>
          </div>
        ))}
        <div style={{
          borderTop: '1px solid rgba(255,255,255,0.06)',
          paddingTop: 6, marginTop: 2,
          display: 'flex', justifyContent: 'space-between',
        }}>
          <span>共 {LAYER_STATS.total} 节点 · {LAYER_STATS.links} 涌现连线</span>
        </div>
      </div>

      {/* 学科色板 */}
      <div style={{
        display: 'flex', flexWrap: 'wrap', gap: 4,
      }}>
        {DISCIPLINES.map(d => (
          <div key={d.key} style={{
            display: 'flex', alignItems: 'center', gap: 4,
            padding: '2px 6px', borderRadius: 4,
            background: `${d.color}10`,
            fontSize: 10,
          }}>
            <div style={{ width: 6, height: 6, borderRadius: 2, background: d.color }} />
            {d.label}
          </div>
        ))}
      </div>

      {/* 交互提示 */}
      <div style={{
        marginTop: 14, fontSize: 10, opacity: 0.3,
        borderTop: '1px solid rgba(255,255,255,0.04)',
        paddingTop: 8,
      }}>
        拖拽旋转 · 滚轮缩放 · 点击探索
      </div>
    </div>
  );
}
