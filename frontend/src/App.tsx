/**
 * @preview
 * App — Noosphere 主入口
 * 万物智识圈
 *
 * 性能优化：Canvas 在 SplashScreen 期间即开始预挂载（WebGL 预热），
 * SplashScreen 结束后仅移除遮罩层，避免同步挂载导致的卡顿。
 *
 * 实时数据：从 consciousness_index.json 动态加载用户上传的意识体，
 * 合并到 3D Globe 与静态节点一起展示。
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import NoosphereGlobe from './components/NoosphereGlobe';
import DetailPanel from './components/ExperiencePanel';
import SearchBar from './components/SearchBar';
import StatsOverlay from './components/StatsOverlay';
import ContributionGraph from './components/ContributionGraph';
import ConsciousnessUploader from './components/ConsciousnessUploader';
import LanguageSwitcher from './components/LanguageSwitcher';
import type { KnowledgeNode } from './data/knowledge';
import { fetchConsciousnessPayloads } from './data/knowledge';
import SplashScreen from './components/SplashScreen';
import { useResonancePolling } from './utils/useResonancePolling';
import type { ResonanceRippleHandle } from './components/ResonanceRipple';

export default function App() {
  const [selectedNode, setSelectedNode] = useState<KnowledgeNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  // splashDone = false → SplashScreen 遮罩 + 3D 后台预热
  // splashDone = true  → SplashScreen 消失 + 3D 已渲染好直接显示
  const [splashDone, setSplashDone] = useState(false);
  // 动态加载的意识体节点
  const [dynamicNodes, setDynamicNodes] = useState<KnowledgeNode[]>([]);

  // 在 SplashScreen 期间异步加载意识体数据（利用 splash 动画等待时间）
  useEffect(() => {
    fetchConsciousnessPayloads().then(nodes => {
      setDynamicNodes(nodes);
      console.log(`[Noosphere] Loaded ${nodes.length} consciousness payloads`);
    });
  }, []);

  const handleSelect = useCallback((node: KnowledgeNode) => {
    setSelectedNode(node);
  }, []);

  const handleClose = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const handleSearch = useCallback((q: string) => {
    setSearchQuery(q);
  }, []);

  // 在线意识上传成功后，将新节点追加到动态意识体列表
  const addDynamicNode = useCallback((node: KnowledgeNode) => {
    setDynamicNodes(prev => [node, ...prev]);
  }, []);

  const handleBootComplete = useCallback(() => {
    // SplashScreen 动画结束 → 移除遮罩（3D 已在后台渲染好）
    setSplashDone(true);
  }, []);

  // ── 实时共振涟漪系统 ──
  const rippleRef = useRef<ResonanceRippleHandle | null>(null);
  const onRipple = useCallback((event: import('./components/ResonanceRipple').RippleEvent) => {
    rippleRef.current?.triggerRipple(event);
  }, []);
  useResonancePolling(dynamicNodes, onRipple);

  return (
    <div style={{
      width: '100vw', height: '100vh',
      overflow: 'hidden', position: 'relative',
      background: '#0a0a1a',
    }}>
      {/*
        ★ 核心优化：3D 场景在 SplashScreen 期间即开始挂载
        → WebGL 上下文创建 + Shader 编译 + 几何体生成
        → SplashScreen 5 秒足够完成所有初始化
        → SplashScreen 消失时 3D 已 warm，无卡顿
      */}
      <div style={{
        width: '100%', height: '100%',
        opacity: splashDone ? 1 : 0,
        transition: 'opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
        // 未完成 splash 时隐藏但仍然渲染（预热 WebGL）
        pointerEvents: splashDone ? 'auto' : 'none',
      }}>
        {/* 3D 智识圈 — 接收动态意识体节点 + 共振涟漪 */}
        <NoosphereGlobe
          onSelectNode={handleSelect}
          onBackgroundClick={handleClose}
          searchQuery={searchQuery}
          dynamicNodes={dynamicNodes}
          rippleRef={rippleRef}
        />

        {/* 搜索栏 */}
        <SearchBar onSearch={handleSearch} />

        {/* 语言切换器 */}
        <LanguageSwitcher />

        {/* 统计 HUD */}
        <StatsOverlay dynamicNodeCount={dynamicNodes.length} />

        {/* 详情面板 */}
        <DetailPanel
          node={selectedNode}
          onClose={handleClose}
        />

        {/* 意识贡献排行面板 */}
        <ContributionGraph />

        {/* 在线意识上传面板 — 零门槛体验核心 */}
        <ConsciousnessUploader onUploadSuccess={addDynamicNode} />
      </div>

      {/* 沉浸式跨维度闪屏遮罩（在 3D 层之上） */}
      {!splashDone && (
        <div style={{
          position: 'absolute', inset: 0, zIndex: 1000,
        }}>
          <SplashScreen onComplete={handleBootComplete} />
        </div>
      )}
    </div>
  );
}
