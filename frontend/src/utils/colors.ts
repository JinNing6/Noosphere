/**
 * Noosphere 配色方案
 * 
 * 源自设计文档 Section 5.5
 */

export const COLORS = {
  /** 深空黑背景 */
  background: '#0a0a1a',
  /** 球体蓝紫光晕 */
  glow: ['#4a3aff', '#7b61ff'] as const,
  /** 经验类型颜色 */
  failure: '#ff4d6a',     // 🔴 珊瑚红
  success: '#00e878',     // 🟢 荧光绿
  pattern: '#4dc9f6',     // 🔵 天际蓝
  warning: '#ffc107',     // 🟡 琥珀黄
  migration: '#b388ff',   // 🟣 星云紫
  /** 连线 */
  connection: 'rgba(255, 255, 255, 0.06)',
  /** 脉冲能量 */
  pulse: '#7b61ff',
  /** 月光白文字 */
  text: '#e0e0ff',
  /** 次级文字 */
  textSecondary: '#8888aa',
  /** 面板背景 */
  panelBg: 'rgba(15, 15, 35, 0.92)',
  /** 面板边框 */
  panelBorder: 'rgba(123, 97, 255, 0.25)',
} as const;

/** 根据经验类型获取颜色 */
export function getTypeColor(type: string): string {
  const map: Record<string, string> = {
    failure: COLORS.failure,
    success: COLORS.success,
    pattern: COLORS.pattern,
    warning: COLORS.warning,
    migration: COLORS.migration,
  };
  return map[type] || COLORS.pulse;
}

/** 根据经验类型获取图标 */
export function getTypeIcon(type: string): string {
  const map: Record<string, string> = {
    failure: '🔴',
    success: '🟢',
    pattern: '🔵',
    warning: '🟡',
    migration: '🟣',
  };
  return map[type] || '⚪';
}

/** 根据经验类型获取中文名 */
export function getTypeName(type: string): string {
  const map: Record<string, string> = {
    failure: '踩坑记录',
    success: '最佳实践',
    pattern: '设计模式',
    warning: '风险预警',
    migration: '迁移指南',
  };
  return map[type] || type;
}
