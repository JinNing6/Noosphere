/**
 * @preview
 * App — Noosphere 主入口
 * 万物智识圈
 */

import { useState, useCallback, useEffect } from 'react';
import NoosphereGlobe from './components/NoosphereGlobe';
import DetailPanel from './components/ExperiencePanel';
import SearchBar from './components/SearchBar';
import StatsOverlay from './components/StatsOverlay';
import ContributionGraph from './components/ContributionGraph';
import type { KnowledgeNode } from './data/knowledge';
import SplashScreen from './components/SplashScreen';

export default function App() {
  const [selectedNode, setSelectedNode] = useState<KnowledgeNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  // 闪屏阶段：'booting' → 'ready' → 'visible'
  // booting: 闪屏播放中，不挂载重型组件
  // ready:   闪屏结束，挂载主内容但先透明
  // visible: 主内容淡入完成
  const [bootStage, setBootStage] = useState<'booting' | 'ready' | 'visible'>('booting');

  const handleSelect = useCallback((node: KnowledgeNode) => {
    setSelectedNode(node);
  }, []);

  const handleClose = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const handleSearch = useCallback((q: string) => {
    setSearchQuery(q);
  }, []);

  const handleBootComplete = useCallback(() => {
    // SplashScreen 动画结束 → 先挂载主内容（透明态）
    setBootStage('ready');
  }, []);

  // ready 阶段：等一帧让 3D 场景初始化，然后触发淡入
  useEffect(() => {
    if (bootStage === 'ready') {
      const raf = requestAnimationFrame(() => {
        // 用 setTimeout 确保浏览器完成一次绘制后再触发过渡
        setTimeout(() => setBootStage('visible'), 60);
      });
      return () => cancelAnimationFrame(raf);
    }
  }, [bootStage]);

  const showMain = bootStage === 'ready' || bootStage === 'visible';

  return (
    <div style={{
      width: '100vw', height: '100vh',
      overflow: 'hidden', position: 'relative',
      background: '#0a0a1a',
    }}>
      {/* 沉浸式跨维度闪屏加载 */}
      {bootStage === 'booting' && <SplashScreen onComplete={handleBootComplete} />}

      {/* 主内容区：延迟挂载 + 淡入过渡 */}
      {showMain && (
        <div style={{
          width: '100%', height: '100%',
          opacity: bootStage === 'visible' ? 1 : 0,
          transition: 'opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          {/* 3D 智识圈 */}
          <NoosphereGlobe
            onSelectNode={handleSelect}
            searchQuery={searchQuery}
          />

          {/* 搜索栏 */}
          <SearchBar onSearch={handleSearch} />

          {/* 统计 HUD */}
          <StatsOverlay />

          {/* 详情面板 */}
          <DetailPanel
            node={selectedNode}
            onClose={handleClose}
          />

          {/* 意识贡献排行面板 */}
          <ContributionGraph />
        </div>
      )}
    </div>
  );
}
