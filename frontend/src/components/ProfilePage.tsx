/**
 * @preview
 * ProfilePage — 个人意识星球页面容器
 *
 * 组合 ProfilePlanet（3D 星球）+ ProfileCard（信息卡片）+ DetailPanel（节点详情）
 * 通过 URL 参数 ?profile=username 访问
 */

import { useState, useCallback, useEffect } from 'react';
import ProfilePlanet from './ProfilePlanet';
import ProfileCard from './ProfileCard';
import DetailPanel from './ExperiencePanel';
import LanguageSwitcher from './LanguageSwitcher';
import type { KnowledgeNode, CreatorStats } from '../data/knowledge';
import { fetchConsciousnessPayloadsByCreator } from '../data/knowledge';

interface ProfilePageProps {
  username: string;
}

export default function ProfilePage({ username }: ProfilePageProps) {
  const [nodes, setNodes] = useState<KnowledgeNode[]>([]);
  const [stats, setStats] = useState<CreatorStats>({
    totalFragments: 0,
    totalResonance: 0,
    typeCounts: {},
    firstUpload: '',
    latestUpload: '',
  });
  const [selectedNode, setSelectedNode] = useState<KnowledgeNode | null>(null);
  const [loading, setLoading] = useState(true);

  // 加载该用户的意识碎片
  useEffect(() => {
    setLoading(true);
    fetchConsciousnessPayloadsByCreator(username).then(({ nodes: fetchedNodes, stats: fetchedStats }) => {
      setNodes(fetchedNodes);
      setStats(fetchedStats);
      setLoading(false);
      console.log(`[Noosphere Profile] Loaded ${fetchedNodes.length} fragments for ${username}`);
    });
  }, [username]);

  const handleSelect = useCallback((node: KnowledgeNode) => {
    setSelectedNode(node);
  }, []);

  const handleClose = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const handleBackToUniverse = useCallback(() => {
    // 导航回主页（移除 profile 参数）
    const url = new URL(window.location.href);
    url.searchParams.delete('profile');
    window.location.href = url.toString();
  }, []);

  return (
    <div style={{
      width: '100vw', height: '100vh',
      overflow: 'hidden', position: 'relative',
      background: '#050510',
    }}>
      {/* Loading 过渡 */}
      {loading && (
        <div style={{
          position: 'absolute', inset: 0, zIndex: 200,
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          background: '#050510',
          fontFamily: "'Inter', sans-serif",
          color: 'rgba(255,255,255,0.4)',
          gap: 16,
        }}>
          <div style={{
            width: 40, height: 40, borderRadius: '50%',
            border: '2px solid rgba(123,97,255,0.2)',
            borderTopColor: '#7b61ff',
            animation: 'spin 1s linear infinite',
          }} />
          <div style={{ fontSize: 12, letterSpacing: 3, textTransform: 'uppercase' }}>
            Loading consciousness...
          </div>
          <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      {/* 3D 星球 */}
      <div style={{
        width: '100%', height: '100%',
        opacity: loading ? 0 : 1,
        transition: 'opacity 0.6s ease',
      }}>
        <ProfilePlanet
          nodes={nodes}
          onSelectNode={handleSelect}
          onBackgroundClick={handleClose}
        />
      </div>

      {/* 信息卡片 */}
      {!loading && (
        <ProfileCard
          username={username}
          stats={stats}
          onBackToUniverse={handleBackToUniverse}
        />
      )}

      {/* 节点详情面板 */}
      <DetailPanel node={selectedNode} onClose={handleClose} />

      {/* 语言切换器 */}
      <LanguageSwitcher />
    </div>
  );
}
