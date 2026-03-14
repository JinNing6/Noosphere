/**
 * @preview
 * App — Noosphere 主入口
 * 万物智识圈
 */

import { useState, useCallback } from 'react';
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
  // 新增加载状态拦截器：初始设为 true 显示闪屏
  const [isBooting, setIsBooting] = useState(true);

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
    setIsBooting(false);
  }, []);

  return (
    <div style={{
      width: '100vw', height: '100vh',
      overflow: 'hidden', position: 'relative',
      background: '#0a0a1a',
    }}>
      {/* 沉浸式跨维度闪屏加载 */}
      {isBooting && <SplashScreen onComplete={handleBootComplete} />}

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
  );
}
