/**
 * useResonanceRippleTrigger — 入场共振涟漪 Hook
 *
 * 当用户进入 3D 宇宙后，自动对有共振的意识体触发涟漪效果，
 * 让宇宙一进入就给人"活着"的感觉。
 *
 * 触发逻辑：
 *   页面加载 → 动态节点就绪 → 延迟 2 秒（等 3D 场景渲染完毕）
 *   → 挑选有共振的节点 → 按时间间隔逐个触发涟漪（避免同时爆发）
 */

import { useEffect, useRef } from 'react';
import type { KnowledgeNode } from '../data/knowledge';
import { CONSCIOUSNESS_TYPE_COLORS } from '../data/knowledge';
import type { RippleEvent } from '../components/ResonanceRipple';
import { goldenSpherePoint } from '../components/InfiniteParticleEngine';

function getNodePosition(nodeId: string, nodes: KnowledgeNode[]): [number, number, number] | null {
  const idx = nodes.findIndex(n => n.id === nodeId);
  if (idx === -1) return null;
  return goldenSpherePoint(idx, Math.max(nodes.length, 1), 5.5);
}

function getNodeColor(node: KnowledgeNode): [number, number, number] {
  const colorHex = CONSCIOUSNESS_TYPE_COLORS[node.consciousnessType || 'epiphany'] || '#e0e0ff';
  const r = parseInt(colorHex.slice(1, 3), 16) / 255;
  const g = parseInt(colorHex.slice(3, 5), 16) / 255;
  const b = parseInt(colorHex.slice(5, 7), 16) / 255;
  return [r, g, b];
}

export function useResonancePolling(
  dynamicNodes: KnowledgeNode[],
  onRipple: (event: RippleEvent) => void,
) {
  const triggeredRef = useRef(false);
  const onRippleRef = useRef(onRipple);
  onRippleRef.current = onRipple;

  useEffect(() => {
    if (triggeredRef.current || dynamicNodes.length === 0) return;
    triggeredRef.current = true;

    // 挑选有共振的节点（按共振数降序，最多 5 个）
    const resonatedNodes = dynamicNodes
      .filter(n => (n.resonanceCount ?? 0) > 0)
      .sort((a, b) => (b.resonanceCount ?? 0) - (a.resonanceCount ?? 0))
      .slice(0, 5);

    // 如果没有共振节点，随机挑 3 个节点展示入场涟漪
    const targets = resonatedNodes.length > 0
      ? resonatedNodes
      : dynamicNodes
          .sort(() => Math.random() - 0.5)
          .slice(0, 3);

    // 延迟 2 秒（等 3D 场景就绪），然后逐个触发涟漪（每隔 600ms）
    const timers: ReturnType<typeof setTimeout>[] = [];

    targets.forEach((node, i) => {
      const timer = setTimeout(() => {
        const position = getNodePosition(node.id, dynamicNodes);
        if (position) {
          const resonance = node.resonanceCount ?? 0;
          onRippleRef.current({
            position,
            color: getNodeColor(node),
            intensity: Math.min(2.0, 1.0 + resonance * 0.2),
          });
        }
      }, 2000 + i * 600); // 2s 起步，每 600ms 触发一个

      timers.push(timer);
    });

    return () => timers.forEach(clearTimeout);
  }, [dynamicNodes]);
}
