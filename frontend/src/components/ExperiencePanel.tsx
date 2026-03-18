/**
 * @preview
 * DetailPanel — 知识节点详情面板
 * 显示 Wikipedia 缩略图、标题、摘要、外链
 */

import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import type { KnowledgeNode } from '../data/knowledge';
import { LAYER_COLORS, DISCIPLINE_COLORS } from '../data/knowledge';

interface MediaItem {
  type: 'image' | 'video';
  url: string;
  thumb?: string;
  caption?: string;
}

interface DetailPanelProps {
  node: KnowledgeNode | null;
  onClose: () => void;
}

const LAYER_ICONS: Record<string, string> = {
  matter: '⚛️',
  life: '🧬',
  civilization: '🌌',
};

export default function DetailPanel({ node, onClose }: DetailPanelProps) {
  const { t, i18n } = useTranslation();
  const isEn = i18n.language === 'en';
  const [mediaLoading, setMediaLoading] = useState(false);
  const [mediaItems, setMediaItems] = useState<MediaItem[]>([]);

  useEffect(() => {
    if (!node?.title_en) {
      setMediaItems([]);
      return;
    }
    
    let isMounted = true;
    setMediaLoading(true);
    setMediaItems([]);

    const fetchMedia = async () => {
      try {
         const title = encodeURIComponent(node.title_en.replace(/ /g, '_'));
         const maxItems = 6;
         const res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/media-list/${title}`);
         if (!res.ok) throw new Error('Failed to fetch media');
         const data = await res.json();
         
         const items: MediaItem[] = [];
         if (data.items && Array.isArray(data.items)) {
           for (const item of data.items) {
             if (items.length >= maxItems) break;
             
             // filter out icons, small svgs, generic logos
             const titleLower = (item.title || "").toLowerCase();
             if (titleLower.includes('.svg') || titleLower.includes('icon') || titleLower.includes('logo') || titleLower.includes('symbol')) continue;

             if (item.type === 'video') {
               const sources = item?.original?.sources || [];
               const webm = sources.find((s: any) => s.mime === 'video/webm') || sources[0];
               if (webm) {
                 const url = webm.url.startsWith('//') ? 'https:' + webm.url : webm.url;
                 const thumb = item?.thumbnail?.source ? (item.thumbnail.source.startsWith('//') ? 'https:' + item.thumbnail.source : item.thumbnail.source) : undefined;
                 items.push({ type: 'video', url, thumb });
               }
             } else if (item.type === 'image') {
                if (item?.srcset && item.srcset.length > 0) {
                  const bestSrc = item.srcset[item.srcset.length - 1].src;
                  const url = bestSrc.startsWith('//') ? 'https:' + bestSrc : bestSrc;
                  const thumb = item?.thumbnail?.source ? (item.thumbnail.source.startsWith('//') ? 'https:' + item.thumbnail.source : item.thumbnail.source) : undefined;
                  items.push({ type: 'image', url, thumb });
                } else if (item?.thumbnail?.source) {
                  const url = item.thumbnail.source.startsWith('//') ? 'https:' + item.thumbnail.source : item.thumbnail.source;
                  items.push({ type: 'image', url });
                }
             }
           }
         }
         
         if (isMounted) {
           setMediaItems(items);
           setMediaLoading(false);
         }
      } catch (err) {
        console.warn("Wikipedia Media list fetch err:", err);
        if (isMounted) setMediaLoading(false);
      }
    };

    fetchMedia();

    return () => {
      isMounted = false;
    };
  }, [node]);

  if (!node) return null;

  const layerIcon = LAYER_ICONS[node.layer] || '🌐';
  const accentColor = node.layer === 'civilization'
    ? (DISCIPLINE_COLORS[node.discipline || 'ai'] || LAYER_COLORS.civilization)
    : LAYER_COLORS[node.layer];

  return (
    <div style={{
      position: 'absolute', right: 0, top: 0, bottom: 0,
      width: 420, maxWidth: '90vw',
      background: 'linear-gradient(135deg, rgba(15, 12, 30, 0.97), rgba(10, 10, 26, 0.98))',
      borderLeft: `1px solid ${accentColor}33`,
      backdropFilter: 'blur(20px)',
      zIndex: 50,
      overflowY: 'auto',
      animation: 'slideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
      fontFamily: "'Inter', sans-serif",
    }}>
      {/* 关闭按钮 */}
      <button onClick={onClose} title={t('experience.closePanel')} style={{
        position: 'absolute', top: 16, left: 16,
        background: 'rgba(0,0,0,0.6)',
        border: '1px solid rgba(255,255,255,0.2)',
        borderRadius: '50%', width: 36, height: 36,
        color: '#fff', fontSize: 16, cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 100,
        backdropFilter: 'blur(10px)',
        transition: 'all 0.2s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
        e.currentTarget.style.transform = 'scale(1.1)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'rgba(0,0,0,0.6)';
        e.currentTarget.style.transform = 'scale(1)';
      }}
      >✕</button>

      {/* 缩略图 */}
      {node.thumbnail && (
        <div style={{
          width: '100%', height: 200,
          backgroundImage: `url(${node.thumbnail})`,
          backgroundSize: 'cover', backgroundPosition: 'center',
          borderBottom: `2px solid ${accentColor}44`,
          position: 'relative',
        }}>
          <div style={{
            position: 'absolute', bottom: 0, left: 0, right: 0, height: 60,
            background: 'linear-gradient(transparent, rgba(10,10,26,0.9))',
          }} />
        </div>
      )}

      {/* 内容 */}
      <div style={{ padding: '24px 28px' }}>
        {/* 层级标签 */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 6,
          padding: '4px 12px', borderRadius: 20,
          background: `${accentColor}15`,
          border: `1px solid ${accentColor}30`,
          fontSize: 12, color: accentColor,
          marginBottom: 16,
        }}>
          {layerIcon} {t(`layers.${node.layer}`)}
          {node.discipline && (
            <span style={{ opacity: 0.6 }}> · {t(`disciplines.${node.discipline}`)}</span>
          )}
        </div>

        {/* 标题 — 节点自身的标题数据 */}
        <h2 style={{
          margin: '0 0 4px', fontSize: 22, fontWeight: 700,
          color: '#f0f0ff', lineHeight: 1.3,
        }}>
          {isEn ? node.title_en : node.title_zh}
        </h2>
        <p style={{
          margin: '0 0 20px', fontSize: 14,
          color: 'rgba(255,255,255,0.4)', fontStyle: 'italic',
        }}>
          {isEn ? node.title_zh : node.title_en}
        </p>

        {/* 重要度指示器 */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          marginBottom: 20, fontSize: 12, color: 'rgba(255,255,255,0.4)',
        }}>
          <span>{t('experience.importance')}</span>
          <div style={{
            display: 'flex', gap: 2,
          }}>
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} style={{
                width: 8, height: 8, borderRadius: 2,
                background: i < node.importance ? accentColor : 'rgba(255,255,255,0.08)',
                transition: 'background 0.3s',
              }} />
            ))}
          </div>
          <span style={{ color: accentColor }}>{node.importance}/10</span>
        </div>

        {/* 摘要 */}
        <div style={{
          padding: '16px 20px',
          background: 'rgba(255,255,255,0.03)',
          borderRadius: 12,
          border: '1px solid rgba(255,255,255,0.06)',
          marginBottom: 20,
        }}>
          <p style={{
            margin: 0, fontSize: 14, lineHeight: 1.8,
            color: 'rgba(255,255,255,0.75)',
          }}>
            {node.summary}
          </p>
        </div>

        {/* 动态富媒体画廊 */}
        {mediaLoading ? (
          <div style={{
            marginBottom: 20, padding: 20, borderRadius: 12,
            background: 'rgba(255,255,255,0.02)',
            border: `1px solid ${accentColor}33`,
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12
          }}>
            <div style={{
              width: 30, height: 30, borderRadius: '50%',
              border: `2px solid ${accentColor}44`,
              borderTopColor: accentColor,
              animation: 'spin 1s linear infinite'
            }} />
            <span style={{ fontSize: 12, color: accentColor, letterSpacing: 2 }}>
              {t('experience.establishingUplink')}
            </span>
            <style>{`
              @keyframes spin { 100% { transform: rotate(360deg); } }
            `}</style>
          </div>
        ) : mediaItems.length > 0 ? (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>
              {t('experience.dataArchives')} ({mediaItems.length})
            </div>
            <div style={{
              display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 8,
              scrollbarWidth: 'thin', scrollbarColor: `${accentColor}44 transparent`
            }}>
              {mediaItems.map((media, idx) => (
                <div key={idx} style={{
                  flexShrink: 0,
                  width: 160, height: 100,
                  borderRadius: 8, overflow: 'hidden',
                  background: 'rgba(0,0,0,0.5)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  position: 'relative',
                  cursor: 'pointer',
                }}
                onClick={() => window.open(media.url, '_blank')}
                onMouseEnter={e => e.currentTarget.style.borderColor = accentColor}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'}
                >
                  {media.type === 'video' ? (
                    <video 
                      src={media.url} 
                      autoPlay loop muted playsInline
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : (
                    <img 
                      src={media.thumb || media.url} 
                      alt="archive"
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  )}
                  {media.type === 'video' && (
                    <div style={{
                      position: 'absolute', top: 4, right: 4,
                      background: 'rgba(0,0,0,0.7)', color: '#fff',
                      fontSize: 10, padding: '2px 6px', borderRadius: 4,
                      border: '1px solid rgba(255,255,255,0.2)'
                    }}>{t('experience.video')}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : null}

        {/* 标签 */}
        {node.tags.length > 0 && (
          <div style={{
            display: 'flex', flexWrap: 'wrap', gap: 6,
            marginBottom: 20,
          }}>
            {node.tags.map(tag => (
              <span key={tag} style={{
                padding: '3px 10px', borderRadius: 12,
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)',
                fontSize: 11, color: 'rgba(255,255,255,0.5)',
              }}>
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Wikipedia 终端风格深度链接 */}
        {node.wiki_url && (
          <a
            href={node.wiki_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '14px 18px',
              background: `linear-gradient(90deg, ${accentColor}11, transparent)`,
              border: `1px solid ${accentColor}33`,
              borderLeft: `4px solid ${accentColor}`,
              borderRadius: 4,
              color: '#fff',
              textDecoration: 'none',
              fontFamily: 'monospace',
              fontSize: 13,
              transition: 'all 0.2s',
              position: 'relative',
              overflow: 'hidden',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.background = `linear-gradient(90deg, ${accentColor}22, ${accentColor}05)`;
              e.currentTarget.style.borderColor = `${accentColor}66`;
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = `linear-gradient(90deg, ${accentColor}11, transparent)`;
              e.currentTarget.style.borderColor = `${accentColor}33`;
            }}
          >
            <div style={{
              width: 8, height: 8, borderRadius: '50%',
              background: accentColor,
              boxShadow: `0 0 8px ${accentColor}`
            }} />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.5)', letterSpacing: 1 }}>{t('experience.uplinkPortal')}</span>
              <span style={{ letterSpacing: 0.5 }}>{t('experience.accessWikiCore')}</span>
            </div>
          </a>
        )}
      </div>
    </div>
  );
}
