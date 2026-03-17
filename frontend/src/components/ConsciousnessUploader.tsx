/**
 * @preview
 * ConsciousnessUploader — 在线意识上传面板
 * 
 * 零门槛体验：用户在 3D 星球上直接上传自己的顿悟/经验/警示，
 * 通过 GitHub API 创建 Issue，实时在星球上冒出新光点。
 * 
 * 视觉：赛博朋克毛玻璃卡片，与 StatsOverlay 统一风格。
 * 交互：折叠态 → 展开态 → 提交 → 成功动画 → 光点飞向星球
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import type { KnowledgeNode, Layer, Discipline } from '../data/knowledge';

/* ═══════════════ 常量 ═══════════════ */

const OWNER = 'JinNing6';
const REPO = 'Noosphere';

/** 意识类型定义 */
const CONSCIOUSNESS_TYPES = [
  { key: 'epiphany',  label: '💡 顿悟', labelEn: 'Epiphany',  color: '#ffd700' },
  { key: 'warning',   label: '⚠️ 警示', labelEn: 'Warning',   color: '#ff6b35' },
  { key: 'pattern',   label: '🔄 规律', labelEn: 'Pattern',   color: '#7b61ff' },
  { key: 'decision',  label: '⚡ 决策', labelEn: 'Decision',  color: '#00e878' },
] as const;

type ConsciousnessType = typeof CONSCIOUSNESS_TYPES[number]['key'];

/** 意识类型 → 三层映射 */
const TYPE_TO_LAYER: Record<ConsciousnessType, Layer> = {
  warning:  'life',
  pattern:  'matter',
  decision: 'matter',
  epiphany: 'civilization',
};

/** 意识类型 → 学科推断 */
const TYPE_TO_DISCIPLINE: Record<ConsciousnessType, Discipline> = {
  warning:  'engineering',
  pattern:  'physics',
  decision: 'ai',
  epiphany: 'philosophy',
};

/* ═══════════════ GitHub API ═══════════════ */

function getStoredToken(): string | null {
  try {
    return localStorage.getItem('noosphere_github_token');
  } catch {
    return null;
  }
}

function storeToken(token: string): void {
  try {
    localStorage.setItem('noosphere_github_token', token);
  } catch {
    // ignore
  }
}

async function createIssue(
  token: string,
  type: ConsciousnessType,
  thought: string,
  context: string,
  creator: string,
  tags: string[],
  isAnonymous: boolean,
): Promise<{ success: boolean; issueUrl?: string; error?: string }> {
  const typeInfo = CONSCIOUSNESS_TYPES.find(t => t.key === type)!;
  const displayCreator = isAnonymous ? 'Anonymous' : creator;

  const title = `🧠 [${typeInfo.labelEn}] ${thought.slice(0, 60)}${thought.length > 60 ? '...' : ''}`;

  const body = `## Consciousness Upload

> Uploaded via Noosphere Web Interface

### Metadata
\`\`\`yaml
type: ${type}
creator: ${displayCreator}
anonymous: ${isAnonymous}
tags: [${tags.join(', ')}]
uploaded_at: ${new Date().toISOString()}
source: web_uploader
\`\`\`

### 💭 Thought
${thought}

### 🌍 Context
${context || 'N/A'}

---
*This consciousness fragment was uploaded through the [Noosphere 3D Globe](https://${OWNER}.github.io/${REPO}/).*
`;

  const labels = [
    'consciousness',
    `type:${type}`,
    ...tags.slice(0, 3).map(t => `tag:${t}`),
  ];

  try {
    const resp = await fetch(`https://api.github.com/repos/${OWNER}/${REPO}/issues`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, body, labels }),
    });

    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}));
      return { success: false, error: errData.message || `HTTP ${resp.status}` };
    }

    const data = await resp.json();
    return { success: true, issueUrl: data.html_url };
  } catch (err) {
    return { success: false, error: (err as Error).message };
  }
}

/* ═══════════════ 主组件 ═══════════════ */

interface Props {
  onUploadSuccess: (node: KnowledgeNode) => void;
}

export default function ConsciousnessUploader({ onUploadSuccess }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [showTokenInput, setShowTokenInput] = useState(false);

  // 表单状态
  const [type, setType] = useState<ConsciousnessType>('epiphany');
  const [thought, setThought] = useState('');
  const [context, setContext] = useState('');
  const [creator, setCreator] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [token, setToken] = useState(getStoredToken() || '');

  // 提交状态
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<{ success: boolean; message: string } | null>(null);
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 打开面板时聚焦文本框
  useEffect(() => {
    if (isOpen && textareaRef.current) {
      setTimeout(() => textareaRef.current?.focus(), 300);
    }
  }, [isOpen]);

  const handleSubmit = useCallback(async () => {
    // 验证
    if (thought.trim().length < 20) {
      setSubmitResult({ success: false, message: '意识内容至少需要 20 个字符' });
      return;
    }
    if (!token.trim()) {
      setShowTokenInput(true);
      setSubmitResult({ success: false, message: '请先配置 GitHub Token' });
      return;
    }

    setIsSubmitting(true);
    setSubmitResult(null);

    const tags = tagInput.split(/[,，\s]+/).filter(Boolean);
    const result = await createIssue(token, type, thought.trim(), context.trim(), creator.trim() || 'Anonymous', tags, isAnonymous);

    if (result.success) {
      // 存储 Token
      storeToken(token);

      // 成功动画
      setShowSuccessAnimation(true);
      setSubmitResult({ success: true, message: '✨ 意识已上传到 Noosphere！' });

      // 构造新的动态节点
      const newNode: KnowledgeNode = {
        id: `upload-${Date.now()}`,
        title_zh: thought.length > 30 ? thought.slice(0, 28) + '…' : thought,
        title_en: isAnonymous ? 'Anonymous Consciousness' : (creator || 'You'),
        layer: TYPE_TO_LAYER[type],
        discipline: TYPE_TO_DISCIPLINE[type],
        summary: thought + (context ? `\n\n**场景**: ${context}` : ''),
        thumbnail: null,
        importance: Math.min(10, 5 + Math.floor(thought.length / 50)),
        tags: [...tags, type, `by:${isAnonymous ? '匿名' : (creator || 'You')}`],
      };

      // 通知父组件追加节点
      onUploadSuccess(newNode);

      // 3 秒后重置表单
      setTimeout(() => {
        setShowSuccessAnimation(false);
        setThought('');
        setContext('');
        setTagInput('');
        setSubmitResult(null);
      }, 3000);
    } else {
      setSubmitResult({ success: false, message: result.error || '上传失败' });
    }

    setIsSubmitting(false);
  }, [thought, context, creator, tagInput, isAnonymous, token, type, onUploadSuccess]);

  const charCount = thought.trim().length;
  const isValid = charCount >= 20;
  const selectedType = CONSCIOUSNESS_TYPES.find(t => t.key === type)!;

  /* ═══════════════ 折叠态 ═══════════════ */

  if (!isOpen) {
    return (
      <button
        id="consciousness-upload-trigger"
        onClick={() => setIsOpen(true)}
        style={{
          position: 'absolute',
          bottom: 28,
          right: 28,
          zIndex: 50,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '14px 24px',
          border: '1px solid rgba(123, 97, 255, 0.25)',
          borderRadius: 16,
          background: 'rgba(8, 6, 18, 0.6)',
          backdropFilter: 'blur(24px) saturate(1.5)',
          color: '#e0e0ff',
          fontSize: 14,
          fontFamily: "'Inter', sans-serif",
          fontWeight: 500,
          letterSpacing: '0.02em',
          cursor: 'pointer',
          transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 20px rgba(123, 97, 255, 0.08)',
          animation: 'breathe 4s ease-in-out infinite',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.borderColor = 'rgba(123, 97, 255, 0.5)';
          e.currentTarget.style.boxShadow = '0 8px 32px rgba(123, 97, 255, 0.15), 0 0 30px rgba(123, 97, 255, 0.12)';
          e.currentTarget.style.transform = 'translateY(-2px)';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.borderColor = 'rgba(123, 97, 255, 0.25)';
          e.currentTarget.style.boxShadow = '0 8px 32px rgba(0,0,0,0.3), 0 0 20px rgba(123, 97, 255, 0.08)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        <span style={{ fontSize: 20 }}>✨</span>
        <span>上传你的顿悟</span>
        <span style={{ fontSize: 10, opacity: 0.4 }}>Upload Consciousness</span>
      </button>
    );
  }

  /* ═══════════════ 展开态 ═══════════════ */

  return (
    <div
      id="consciousness-uploader-panel"
      className="uploader-glass"
      style={{
        position: 'absolute',
        bottom: 24,
        right: 24,
        zIndex: 50,
        width: 380,
        maxHeight: 'calc(100vh - 48px)',
        overflowY: 'auto',
        borderRadius: 20,
        padding: 24,
        fontFamily: "'Inter', sans-serif",
        animation: 'slideUpPanel 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
      }}
    >
      {/* 成功动画遮罩 */}
      {showSuccessAnimation && (
        <div style={{
          position: 'absolute',
          inset: 0,
          borderRadius: 20,
          background: 'rgba(0, 232, 120, 0.05)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10,
          animation: 'successGlow 3s ease forwards',
        }}>
          <div style={{
            textAlign: 'center',
            animation: 'slideUp 0.5s ease forwards',
          }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>🌌</div>
            <div style={{ fontSize: 16, fontWeight: 600, color: '#00e878' }}>
              意识已上传
            </div>
            <div style={{ fontSize: 11, opacity: 0.5, marginTop: 6 }}>
              Consciousness Uploaded to Noosphere
            </div>
            <div style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: '#00e878',
              margin: '16px auto 0',
              animation: 'flyToGlobe 2s ease-out 0.5s forwards',
              boxShadow: '0 0 20px rgba(0, 232, 120, 0.8)',
            }} />
          </div>
        </div>
      )}

      {/* 标题栏 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 20,
      }}>
        <div>
          <div style={{
            fontSize: 15,
            fontWeight: 600,
            color: '#e0e0ff',
            letterSpacing: '0.05em',
          }}>
            ✨ 上传意识
          </div>
          <div style={{ fontSize: 10, opacity: 0.4, marginTop: 2, letterSpacing: '0.08em' }}>
            UPLOAD CONSCIOUSNESS
          </div>
        </div>
        <button
          id="close-uploader"
          onClick={() => setIsOpen(false)}
          style={{
            width: 32, height: 32,
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 8,
            background: 'rgba(255,255,255,0.03)',
            color: 'rgba(255,255,255,0.4)',
            fontSize: 14,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.borderColor = 'rgba(255,107,53,0.3)';
            e.currentTarget.style.color = '#ff6b35';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)';
            e.currentTarget.style.color = 'rgba(255,255,255,0.4)';
          }}
        >
          ✕
        </button>
      </div>

      {/* 意识类型选择 */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, opacity: 0.5, marginBottom: 8 }}>意识类型 · Type</div>
        <div style={{ display: 'flex', gap: 6 }}>
          {CONSCIOUSNESS_TYPES.map(t => (
            <button
              key={t.key}
              id={`type-${t.key}`}
              onClick={() => setType(t.key)}
              style={{
                flex: 1,
                padding: '8px 4px',
                border: `1px solid ${type === t.key ? t.color + '60' : 'rgba(255,255,255,0.06)'}`,
                borderRadius: 10,
                background: type === t.key ? t.color + '12' : 'rgba(255,255,255,0.02)',
                color: type === t.key ? t.color : 'rgba(255,255,255,0.5)',
                fontSize: 12,
                cursor: 'pointer',
                transition: 'all 0.2s',
                fontFamily: "'Inter', sans-serif",
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* 意识内容输入 */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
          <span style={{ fontSize: 11, opacity: 0.5 }}>意识内容 · Thought</span>
          <span style={{
            fontSize: 10,
            color: isValid ? '#00e878' : (charCount > 0 ? '#ff6b35' : 'rgba(255,255,255,0.3)'),
            transition: 'color 0.2s',
          }}>
            {charCount}/20+
          </span>
        </div>
        <textarea
          ref={textareaRef}
          id="thought-input"
          value={thought}
          onChange={e => setThought(e.target.value)}
          placeholder="写下你此刻的顿悟、经验或洞察..."
          rows={4}
          style={{
            width: '100%',
            padding: '12px 14px',
            border: `1px solid ${isValid ? 'rgba(0, 232, 120, 0.15)' : 'rgba(255,255,255,0.06)'}`,
            borderRadius: 12,
            background: 'rgba(255,255,255,0.03)',
            color: '#e0e0ff',
            fontSize: 13,
            fontFamily: "'Inter', sans-serif",
            lineHeight: 1.6,
            resize: 'vertical',
            outline: 'none',
            transition: 'border-color 0.2s',
          }}
          onFocus={e => {
            e.currentTarget.style.borderColor = selectedType.color + '40';
          }}
          onBlur={e => {
            e.currentTarget.style.borderColor = isValid ? 'rgba(0, 232, 120, 0.15)' : 'rgba(255,255,255,0.06)';
          }}
        />
      </div>

      {/* 场景/上下文 */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, opacity: 0.5, marginBottom: 8 }}>场景 · Context <span style={{ opacity: 0.5 }}>(可选)</span></div>
        <input
          id="context-input"
          type="text"
          value={context}
          onChange={e => setContext(e.target.value)}
          placeholder="在什么场景下产生的这个想法？"
          style={{
            width: '100%',
            padding: '10px 14px',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 10,
            background: 'rgba(255,255,255,0.03)',
            color: '#e0e0ff',
            fontSize: 12,
            fontFamily: "'Inter', sans-serif",
            outline: 'none',
          }}
        />
      </div>

      {/* 标签 */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, opacity: 0.5, marginBottom: 8 }}>标签 · Tags <span style={{ opacity: 0.5 }}>(逗号分隔)</span></div>
        <input
          id="tags-input"
          type="text"
          value={tagInput}
          onChange={e => setTagInput(e.target.value)}
          placeholder="AI, consciousness, philosophy"
          style={{
            width: '100%',
            padding: '10px 14px',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 10,
            background: 'rgba(255,255,255,0.03)',
            color: '#e0e0ff',
            fontSize: 12,
            fontFamily: "'Inter', sans-serif",
            outline: 'none',
          }}
        />
      </div>

      {/* 创作者 + 匿名 */}
      <div style={{ marginBottom: 16, display: 'flex', gap: 10, alignItems: 'flex-end' }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 11, opacity: 0.5, marginBottom: 8 }}>签名 · Creator</div>
          <input
            id="creator-input"
            type="text"
            value={creator}
            onChange={e => setCreator(e.target.value)}
            placeholder="你的 GitHub ID"
            disabled={isAnonymous}
            style={{
              width: '100%',
              padding: '10px 14px',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: 10,
              background: isAnonymous ? 'rgba(255,255,255,0.01)' : 'rgba(255,255,255,0.03)',
              color: isAnonymous ? 'rgba(255,255,255,0.2)' : '#e0e0ff',
              fontSize: 12,
              fontFamily: "'Inter', sans-serif",
              outline: 'none',
            }}
          />
        </div>
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '10px 12px',
          border: `1px solid ${isAnonymous ? 'rgba(123, 97, 255, 0.2)' : 'rgba(255,255,255,0.06)'}`,
          borderRadius: 10,
          background: isAnonymous ? 'rgba(123, 97, 255, 0.08)' : 'rgba(255,255,255,0.02)',
          cursor: 'pointer',
          fontSize: 12,
          color: isAnonymous ? '#7b61ff' : 'rgba(255,255,255,0.4)',
          transition: 'all 0.2s',
          whiteSpace: 'nowrap',
        }}>
          <input
            type="checkbox"
            checked={isAnonymous}
            onChange={e => setIsAnonymous(e.target.checked)}
            style={{ display: 'none' }}
          />
          <span style={{ fontSize: 14 }}>{isAnonymous ? '🎭' : '👤'}</span>
          匿名
        </label>
      </div>

      {/* GitHub Token 配置 */}
      <div style={{ marginBottom: 20 }}>
        <button
          id="toggle-token"
          onClick={() => setShowTokenInput(!showTokenInput)}
          style={{
            fontSize: 11,
            color: token ? 'rgba(0, 232, 120, 0.6)' : 'rgba(255, 107, 53, 0.6)',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontFamily: "'Inter', sans-serif",
            padding: 0,
          }}
        >
          {token ? '🔑 Token 已配置' : '🔑 配置 GitHub Token'} {showTokenInput ? '▲' : '▼'}
        </button>
        {showTokenInput && (
          <div style={{ marginTop: 8 }}>
            <input
              id="token-input"
              type="password"
              value={token}
              onChange={e => setToken(e.target.value)}
              placeholder="ghp_xxxxxxxxxxxx"
              style={{
                width: '100%',
                padding: '10px 14px',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: 10,
                background: 'rgba(255,255,255,0.03)',
                color: '#e0e0ff',
                fontSize: 12,
                fontFamily: "'Inter', monospace",
                outline: 'none',
              }}
            />
            <div style={{ fontSize: 10, opacity: 0.3, marginTop: 6, lineHeight: 1.5 }}>
              需要 repo 权限的 Personal Access Token
              <br />
              Token 仅存储在本地浏览器中，不会上传到任何服务器
            </div>
          </div>
        )}
      </div>

      {/* 提交结果反馈 */}
      {submitResult && (
        <div style={{
          marginBottom: 14,
          padding: '10px 14px',
          borderRadius: 10,
          fontSize: 12,
          background: submitResult.success ? 'rgba(0, 232, 120, 0.08)' : 'rgba(255, 107, 53, 0.08)',
          border: `1px solid ${submitResult.success ? 'rgba(0, 232, 120, 0.2)' : 'rgba(255, 107, 53, 0.2)'}`,
          color: submitResult.success ? '#00e878' : '#ff6b35',
          animation: 'fadeIn 0.3s ease',
        }}>
          {submitResult.message}
        </div>
      )}

      {/* 提交按钮 */}
      <button
        id="submit-consciousness"
        onClick={handleSubmit}
        disabled={isSubmitting || !isValid}
        style={{
          width: '100%',
          padding: '14px',
          border: 'none',
          borderRadius: 14,
          background: isValid
            ? `linear-gradient(135deg, ${selectedType.color}90, ${selectedType.color}40)`
            : 'rgba(255,255,255,0.04)',
          color: isValid ? '#fff' : 'rgba(255,255,255,0.2)',
          fontSize: 14,
          fontWeight: 600,
          fontFamily: "'Inter', sans-serif",
          letterSpacing: '0.05em',
          cursor: isValid && !isSubmitting ? 'pointer' : 'not-allowed',
          transition: 'all 0.3s',
          opacity: isSubmitting ? 0.6 : 1,
          boxShadow: isValid ? `0 4px 20px ${selectedType.color}20` : 'none',
        }}
      >
        {isSubmitting ? (
          <span>
            <span style={{ animation: 'pulse 1s ease-in-out infinite', display: 'inline-block' }}>⏳</span>
            {' '}上传中...
          </span>
        ) : (
          <span>🚀 上传到意识星球</span>
        )}
      </button>

      {/* 底部提示 */}
      <div style={{
        marginTop: 14,
        fontSize: 10,
        opacity: 0.25,
        textAlign: 'center',
        lineHeight: 1.5,
      }}>
        你的意识将作为 GitHub Issue 永久保存
        <br />
        Your consciousness will be preserved as eternal digital heritage
      </div>
    </div>
  );
}
