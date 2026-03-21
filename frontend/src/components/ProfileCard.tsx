/**
 * @preview
 * ProfileCard — 个人意识星球用户信息卡片
 *
 * 浮在 3D 星球左侧的暗色毛玻璃面板，展示：
 * - GitHub 头像 + 用户名 + 阶梯称号
 * - 贡献统计（总碎片 / 总共振 / 首次上传）
 * - 意识类型分布图
 * - 分享按钮（复制链接 / X 分享）
 * - 返回宇宙全景按钮
 */

import { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { CreatorStats } from '../data/knowledge';
import { CONSCIOUSNESS_TYPE_COLORS } from '../data/knowledge';
import { calculateTitle } from '../data/mockContributions';

/* ═══════════════ 类型分布条形图 ═══════════════ */

const TYPE_LABELS: Record<string, { icon: string; labelKey: string }> = {
  epiphany: { icon: '💡', labelKey: 'uploader.type.epiphany' },
  warning:  { icon: '⚠️', labelKey: 'uploader.type.warning' },
  pattern:  { icon: '🔄', labelKey: 'uploader.type.pattern' },
  decision: { icon: '🎯', labelKey: 'uploader.type.decision' },
  image:    { icon: '🖼️', labelKey: 'profile.typeImage' },
  video:    { icon: '🎬', labelKey: 'profile.typeVideo' },
  voice:    { icon: '🎵', labelKey: 'profile.typeVoice' },
};

function TypeDistribution({ typeCounts, total }: { typeCounts: Record<string, number>; total: number }) {
  const { t } = useTranslation();
  if (total === 0) return null;

  const entries = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]);

  return (
    <div style={{ marginTop: 16 }}>
      <div style={{
        fontSize: 10, color: 'rgba(255,255,255,0.4)',
        letterSpacing: 2, textTransform: 'uppercase', marginBottom: 10,
      }}>
        {t('profile.typeDistribution')}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {entries.map(([type, count]) => {
          const info = TYPE_LABELS[type] || { icon: '💠', labelKey: type };
          const color = CONSCIOUSNESS_TYPE_COLORS[type] || '#e0e0ff';
          const pct = Math.round((count / total) * 100);
          return (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 14, width: 22, textAlign: 'center' }}>{info.icon}</span>
              <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.6)', minWidth: 56 }}>
                {t(info.labelKey, type)}
              </span>
              <div style={{
                flex: 1, height: 6, borderRadius: 3,
                background: 'rgba(255,255,255,0.06)',
                overflow: 'hidden',
              }}>
                <div style={{
                  width: `${pct}%`, height: '100%', borderRadius: 3,
                  background: `linear-gradient(90deg, ${color}, ${color}88)`,
                  transition: 'width 0.8s ease',
                }} />
              </div>
              <span style={{ fontSize: 11, color, fontWeight: 600, minWidth: 28, textAlign: 'right' }}>
                {count}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════ 主组件 ═══════════════ */

interface ProfileCardProps {
  username: string;
  stats: CreatorStats;
  onBackToUniverse: () => void;
}

export default function ProfileCard({ username, stats, onBackToUniverse }: ProfileCardProps) {
  const { t } = useTranslation();
  const [linkCopied, setLinkCopied] = useState(false);

  const avatarUrl = `https://github.com/${username}.png?size=128`;
  const profileUrl = `${window.location.origin}${import.meta.env.BASE_URL}?profile=${username}`;

  // 称号
  const title = useMemo(() => {
    const psi = stats.totalFragments * 10 + stats.totalResonance * 5;
    return calculateTitle(psi);
  }, [stats]);

  // 格式化日期
  const formatDate = (iso: string) => {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleDateString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric',
      });
    } catch { return iso.slice(0, 10); }
  };

  /* ── 分享功能 ── */

  const handleCopyLink = () => {
    navigator.clipboard.writeText(profileUrl).then(() => {
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    });
  };

  const handleShareTwitter = () => {
    const text = t('profile.twitterText', {
      defaultValue: 'Check out my Consciousness Planet on Noosphere — where ideas become stars ✨🧠',
    });
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(profileUrl)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  /* ── Empty state ── */

  if (stats.totalFragments === 0) {
    return (
      <div style={{
        position: 'absolute', left: 24, top: '50%', transform: 'translateY(-50%)',
        width: 320, maxWidth: '90vw', padding: '40px 28px',
        background: 'linear-gradient(135deg, rgba(15,12,30,0.95), rgba(10,10,26,0.97))',
        borderRadius: 20, border: '1px solid rgba(123,97,255,0.15)',
        backdropFilter: 'blur(24px)', fontFamily: "'Inter', sans-serif",
        zIndex: 50, textAlign: 'center', color: 'rgba(255,255,255,0.5)',
      }}>
        <img src={avatarUrl} alt={username}
          style={{ width: 64, height: 64, borderRadius: '50%', border: '2px solid rgba(123,97,255,0.3)', marginBottom: 16 }}
          onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
        />
        <div style={{ fontSize: 18, fontWeight: 700, color: '#e0e0ff', marginBottom: 8 }}>{username}</div>
        <div style={{ fontSize: 28, marginBottom: 12 }}>🌑</div>
        <div style={{ fontSize: 14 }}>{t('profile.noFragments')}</div>
        <button onClick={onBackToUniverse} style={{
          marginTop: 24, padding: '10px 24px', borderRadius: 12,
          background: 'rgba(123,97,255,0.15)', border: '1px solid rgba(123,97,255,0.3)',
          color: '#b388ff', cursor: 'pointer', fontFamily: "'Inter', sans-serif",
          fontSize: 13, transition: 'all 0.2s',
        }}
        onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(123,97,255,0.25)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(123,97,255,0.15)'; }}
        >
          ← {t('profile.backToUniverse')}
        </button>
      </div>
    );
  }

  /* ── 正常卡片 ── */
  return (
    <div style={{
      position: 'absolute', left: 24, top: '50%', transform: 'translateY(-50%)',
      width: 340, maxWidth: '90vw',
      background: 'linear-gradient(135deg, rgba(15,12,30,0.95), rgba(10,10,26,0.97))',
      borderRadius: 20, border: '1px solid rgba(123,97,255,0.15)',
      backdropFilter: 'blur(24px)', fontFamily: "'Inter', sans-serif",
      zIndex: 50, overflow: 'hidden',
      boxShadow: '0 8px 40px rgba(0,0,0,0.5), inset 0 0 40px rgba(123,97,255,0.03)',
      animation: 'slideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
    }}>

      {/* ── 头像区域 ── */}
      <div style={{
        padding: '28px 28px 20px', textAlign: 'center',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        background: 'linear-gradient(180deg, rgba(123,97,255,0.06), transparent)',
      }}>
        <img src={avatarUrl} alt={username}
          style={{
            width: 80, height: 80, borderRadius: '50%',
            border: `3px solid ${title.color}44`,
            boxShadow: title.glow,
            marginBottom: 14,
          }}
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.style.display = 'none';
          }}
        />

        <div style={{ fontSize: 22, fontWeight: 700, color: '#f0f0ff', letterSpacing: '0.02em' }}>
          {username}
        </div>

        {/* 称号 */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 6,
          marginTop: 8, padding: '4px 14px', borderRadius: 20,
          background: `linear-gradient(90deg, ${title.color}15, transparent)`,
          border: `1px solid ${title.color}33`,
          fontSize: 12, color: title.color, fontWeight: 500,
        }}>
          {title.icon} {t(title.labelKey)}
        </div>

        {/* 副标题 */}
        <div style={{
          marginTop: 10, fontSize: 11,
          color: 'rgba(255,255,255,0.35)', letterSpacing: '0.15em',
          textTransform: 'uppercase',
        }}>
          {t('profile.subtitle', { defaultValue: 'CONSCIOUSNESS PLANET' })}
        </div>
      </div>

      {/* ── 统计区 ── */}
      <div style={{ padding: '20px 28px' }}>
        {/* 核心数值 */}
        <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
          <div style={{ flex: 1, textAlign: 'center' }}>
            <div style={{ fontSize: 28, fontWeight: 700, color: '#7b61ff' }}>
              {stats.totalFragments}
            </div>
            <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: 1, marginTop: 2 }}>
              {t('profile.totalFragments')}
            </div>
          </div>
          <div style={{ width: 1, background: 'rgba(255,255,255,0.06)' }} />
          <div style={{ flex: 1, textAlign: 'center' }}>
            <div style={{ fontSize: 28, fontWeight: 700, color: '#00e878' }}>
              {stats.totalResonance}
            </div>
            <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: 1, marginTop: 2 }}>
              {t('profile.totalResonance')}
            </div>
          </div>
        </div>

        {/* 时间信息 */}
        <div style={{
          display: 'flex', justifyContent: 'space-between',
          padding: '10px 14px', borderRadius: 10,
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid rgba(255,255,255,0.04)',
          fontSize: 11,
        }}>
          <div>
            <div style={{ color: 'rgba(255,255,255,0.35)', marginBottom: 2 }}>{t('profile.firstUpload')}</div>
            <div style={{ color: 'rgba(255,255,255,0.7)' }}>{formatDate(stats.firstUpload)}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ color: 'rgba(255,255,255,0.35)', marginBottom: 2 }}>{t('profile.latestUpload')}</div>
            <div style={{ color: 'rgba(255,255,255,0.7)' }}>{formatDate(stats.latestUpload)}</div>
          </div>
        </div>

        {/* 类型分布 */}
        <TypeDistribution typeCounts={stats.typeCounts} total={stats.totalFragments} />
      </div>

      {/* ── 分享 + 导航区 ── */}
      <div style={{
        padding: '16px 28px 24px',
        borderTop: '1px solid rgba(255,255,255,0.06)',
        display: 'flex', flexDirection: 'column', gap: 10,
      }}>
        {/* 分享按钮行 */}
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            onClick={handleCopyLink}
            style={{
              flex: 1, padding: '10px 0', borderRadius: 10,
              background: linkCopied ? 'rgba(0,232,120,0.15)' : 'rgba(123,97,255,0.1)',
              border: `1px solid ${linkCopied ? 'rgba(0,232,120,0.3)' : 'rgba(123,97,255,0.2)'}`,
              color: linkCopied ? '#00e878' : '#b388ff',
              cursor: 'pointer', fontFamily: "'Inter', sans-serif",
              fontSize: 12, fontWeight: 500, transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (!linkCopied) e.currentTarget.style.background = 'rgba(123,97,255,0.2)';
            }}
            onMouseLeave={(e) => {
              if (!linkCopied) e.currentTarget.style.background = 'rgba(123,97,255,0.1)';
            }}
          >
            {linkCopied ? `✓ ${t('profile.copied')}` : `📋 ${t('profile.copyLink')}`}
          </button>

          <button
            onClick={handleShareTwitter}
            style={{
              flex: 1, padding: '10px 0', borderRadius: 10,
              background: 'rgba(29,161,242,0.1)',
              border: '1px solid rgba(29,161,242,0.2)',
              color: '#1DA1F2',
              cursor: 'pointer', fontFamily: "'Inter', sans-serif",
              fontSize: 12, fontWeight: 500, transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(29,161,242,0.2)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(29,161,242,0.1)'; }}
          >
            𝕏 {t('profile.shareTwitter')}
          </button>
        </div>

        {/* 返回宇宙 */}
        <button
          onClick={onBackToUniverse}
          style={{
            width: '100%', padding: '10px 0', borderRadius: 10,
            background: 'transparent',
            border: '1px solid rgba(255,255,255,0.08)',
            color: 'rgba(255,255,255,0.5)',
            cursor: 'pointer', fontFamily: "'Inter', sans-serif",
            fontSize: 12, transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'rgba(255,255,255,0.2)';
            e.currentTarget.style.color = 'rgba(255,255,255,0.8)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)';
            e.currentTarget.style.color = 'rgba(255,255,255,0.5)';
          }}
        >
          ← {t('profile.backToUniverse')}
        </button>
      </div>
    </div>
  );
}
