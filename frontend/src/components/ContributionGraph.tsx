import React, { useState, useEffect } from 'react';
import type { Contributor } from '../data/mockContributions';
import { MOCK_HEATMAP_DATA, calculateTitle, fetchGitHubContributors } from '../data/mockContributions';

export default function ContributionGraph() {
  const [isOpen, setIsOpen] = useState(false);
  const [contributors, setContributors] = useState<Contributor[]>([]);
  const [loading, setLoading] = useState(false);

  // 面板打开时从 GitHub API 加载真实数据
  useEffect(() => {
    if (!isOpen) return;
    if (contributors.length > 0) return; // 已有数据则不重复请求

    let cancelled = false;
    setLoading(true);

    fetchGitHubContributors()
      .then((data) => {
        if (!cancelled) {
          setContributors(data);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [isOpen, contributors.length]);

  // 渲染热力图颜色
  const getHeatmapColor = (level: number) => {
    switch (level) {
      case 1: return 'rgba(123, 97, 255, 0.3)';   // 浅紫
      case 2: return 'rgba(123, 97, 255, 0.6)';   // 中紫
      case 3: return 'rgba(0, 232, 120, 0.8)';    // 智识绿
      case 4: return 'rgba(255, 107, 53, 1)';     // 熔岩橙 (最高活跃)
      default: return 'rgba(255, 255, 255, 0.05)'; // 无活动
    }
  };

  const getHeatmapShadow = (level: number) => {
    switch (level) {
      case 3: return '0 0 8px rgba(0, 232, 120, 0.6)';
      case 4: return '0 0 12px rgba(255, 107, 53, 0.8)';
      default: return 'none';
    }
  };

  return (
    <>
      {/* 触发按钮 */}
      <div 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'absolute',
          bottom: 24,
          right: 24,
          width: 56,
          height: 56,
          borderRadius: '50%',
          background: 'rgba(8, 6, 18, 0.6)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(123, 97, 255, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.4), inset 0 0 12px rgba(123, 97, 255, 0.2)',
          zIndex: 100,
          color: '#fff',
          fontSize: 24,
          transition: 'all 0.3s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)';
          e.currentTarget.style.borderColor = 'rgba(0, 232, 120, 0.6)';
          e.currentTarget.style.boxShadow = '0 0 20px rgba(0, 232, 120, 0.4), inset 0 0 15px rgba(0, 232, 120, 0.2)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.borderColor = 'rgba(123, 97, 255, 0.3)';
          e.currentTarget.style.boxShadow = '0 4px 24px rgba(0, 0, 0, 0.4), inset 0 0 12px rgba(123, 97, 255, 0.2)';
        }}
      >
        🌌
      </div>

      {/* 贡献面板 */}
      <div 
        className="detail-glass"
        style={{
          position: 'absolute',
          bottom: 96,
          right: 24,
          width: 600,
          maxHeight: '80vh',
          borderRadius: 16,
          padding: 24,
          color: '#fff',
          zIndex: 99,
          fontFamily: "'Inter', sans-serif",
          transform: isOpen ? 'translateY(0) scale(1)' : 'translateY(20px) scale(0.95)',
          opacity: isOpen ? 1 : 0,
          pointerEvents: isOpen ? 'auto' : 'none',
          transition: 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
          overflowY: 'auto'
        }}
      >
        {/* Header区: 双排行文，不要截断文字 */}
        <div style={{ marginBottom: 24, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 16 }}>
          <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: '0.05em', color: '#e0e0ff', lineHeight: 1.4 }}>
            意识贡献热力网络
          </div>
          <div style={{ fontSize: 13, fontWeight: 300, color: 'rgba(255,255,255,0.5)', marginTop: 4, letterSpacing: '0.1em' }}>
            Consciousness Contribution Heatmap
          </div>
        </div>

        {/* 热力图区 */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ display: 'flex', gap: 4, alignItems: 'flex-start' }}>
            {MOCK_HEATMAP_DATA.map((week, wIdx) => (
              <div key={wIdx} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {week.map((level, dIdx) => (
                  <div 
                    key={`${wIdx}-${dIdx}`}
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: 2,
                      background: getHeatmapColor(level),
                      boxShadow: getHeatmapShadow(level),
                      transition: 'all 0.2s',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'scale(1.5)';
                      e.currentTarget.style.zIndex = '2';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scale(1)';
                      e.currentTarget.style.zIndex = '1';
                    }}
                    title={level > 0 ? `活跃度: ${level}` : '未连接'}
                  />
                ))}
              </div>
            ))}
          </div>

          {/* 活跃度图例 */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', marginTop: 12, gap: 8, fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>
            <span>沉寂 / Silenced</span>
            {[0, 1, 2, 3, 4].map(level => (
              <div 
                key={`legend-${level}`}
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: 2,
                  background: getHeatmapColor(level),
                  boxShadow: getHeatmapShadow(level)
                }}
              />
            ))}
            <span>涌现 / Emerged</span>
          </div>
        </div>

        {/* 排行榜区 */}
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: 20 }}>
          <div style={{ fontSize: 18, fontWeight: 600, color: '#00e878', marginBottom: 4 }}>
            宇宙建筑师排行
          </div>
          <div style={{ fontSize: 12, fontWeight: 300, color: 'rgba(255,255,255,0.5)', marginBottom: 20 }}>
            Architects of Noosphere · Powered by GitHub
          </div>

          {/* Loading 骨架屏 */}
          {loading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[1, 2, 3].map(i => (
                <div key={`skeleton-${i}`} style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.05)',
                  borderRadius: 8, padding: '12px 16px',
                }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: '50%',
                    background: 'linear-gradient(90deg, rgba(123,97,255,0.1) 25%, rgba(123,97,255,0.2) 50%, rgba(123,97,255,0.1) 75%)',
                    backgroundSize: '200% 100%',
                    animation: 'shimmer 1.5s infinite',
                  }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ width: 120, height: 14, borderRadius: 4, background: 'rgba(255,255,255,0.06)', marginBottom: 6 }} />
                    <div style={{ width: 80, height: 10, borderRadius: 4, background: 'rgba(255,255,255,0.04)' }} />
                  </div>
                </div>
              ))}
              <style>{`@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }`}</style>
            </div>
          )}

          {/* 无数据提示 */}
          {!loading && contributors.length === 0 && (
            <div style={{
              textAlign: 'center', padding: '24px 0',
              color: 'rgba(255,255,255,0.3)', fontSize: 14,
            }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>🌌</div>
              <div>宇宙还处于奇点阶段</div>
              <div style={{ fontSize: 12, marginTop: 4, opacity: 0.6 }}>
                The universe is still at its singularity
              </div>
            </div>
          )}

          {/* 贡献者列表 */}
          {!loading && contributors.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {contributors.map((user, idx) => (
                <div 
                  key={user.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.05)',
                    borderRadius: 8,
                    padding: '12px 16px',
                    transition: 'background 0.2s',
                    cursor: 'pointer',
                  }}
                  onClick={() => window.open(`https://github.com/${user.login}`, '_blank')}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(123, 97, 255, 0.1)';
                    e.currentTarget.style.borderColor = 'rgba(123, 97, 255, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)';
                  }}
                >
                  <div style={{ 
                    width: 30, 
                    fontSize: 16, 
                    fontWeight: 'bold', 
                    color: idx === 0 ? '#ffd700' : idx === 1 ? '#e0e0e0' : idx === 2 ? '#cd7f32' : 'rgba(255,255,255,0.3)'
                  }}>
                    #{idx + 1}
                  </div>
                  
                  {/* GitHub 真实头像 */}
                  <img
                    src={`${user.avatarUrl}&s=48`}
                    alt={user.login}
                    style={{
                      width: 36, height: 36, borderRadius: '50%',
                      marginRight: 12,
                      border: `2px solid ${calculateTitle(user.totalScore).color}44`,
                      boxShadow: calculateTitle(user.totalScore).glow,
                    }}
                    onError={(e) => {
                      // 头像加载失败时显示首字母
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                    }}
                  />
                  
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ fontWeight: 600, fontSize: 16, color: '#fff' }}>{user.login}</div>
                      
                      {/* 阶梯称号 Badge */}
                      <div style={{
                        display: 'flex', alignItems: 'center', gap: 4,
                        padding: '2px 8px', borderRadius: 12,
                        background: `linear-gradient(90deg, ${calculateTitle(user.totalScore).color}22, transparent)`,
                        border: `1px solid ${calculateTitle(user.totalScore).color}44`,
                        fontSize: 11, fontWeight: 500,
                        color: calculateTitle(user.totalScore).color,
                        textShadow: calculateTitle(user.totalScore).glow
                      }}>
                        {calculateTitle(user.totalScore).icon} {calculateTitle(user.totalScore).label}
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: 12, marginTop: 6, fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>
                      <span>📦 Commits: <span style={{ color: '#00d4ff' }}>{user.commits}</span></span>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 18, fontWeight: 'bold', color: '#ff6b35' }}>
                      {user.totalScore}
                    </div>
                    <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', marginTop: 2 }}>
                      灵能总值<br/>Total Psi
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
