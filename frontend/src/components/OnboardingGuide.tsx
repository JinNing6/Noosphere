/**
 * @preview
 * OnboardingGuide — 首次访问 3 步引导气泡
 *
 * 检测 localStorage 判断是否首次访问，展示 3 步引导：
 * Step 1: 指向上传按钮 → "上传你的第一个想法"
 * Step 2: 指向搜索栏 → "搜索意识碎片"
 * Step 3: 指向星球节点 → "点击光点感受共鸣"
 *
 * 视觉：浮动高亮气泡 + 脉冲动画 + 半透明遮罩
 */

import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

const STORAGE_KEY = 'noosphere_onboarded';

interface OnboardingStep {
  targetId: string;           // 目标元素 ID
  titleKey: string;           // i18n key
  descKey: string;            // i18n key
  icon: string;               // emoji icon
  position: 'bottom-right' | 'bottom-left' | 'top-center';
  fallbackPosition?: { top: number; left: number }; // 当元素不存在时的回退位置
}

const STEPS: OnboardingStep[] = [
  {
    targetId: 'consciousness-upload-trigger',
    titleKey: 'onboarding.step1Title',
    descKey: 'onboarding.step1Desc',
    icon: '✨',
    position: 'bottom-left',
    fallbackPosition: { top: 70, left: 70 },
  },
  {
    targetId: 'search-input',
    titleKey: 'onboarding.step2Title',
    descKey: 'onboarding.step2Desc',
    icon: '🔍',
    position: 'bottom-left',
    fallbackPosition: { top: 20, left: 50 },
  },
  {
    targetId: 'stats-overlay',
    titleKey: 'onboarding.step3Title',
    descKey: 'onboarding.step3Desc',
    icon: '💖',
    position: 'bottom-right',
    fallbackPosition: { top: 20, left: 20 },
  },
];

interface OnboardingGuideProps {
  delayMs?: number;
}

export default function OnboardingGuide({ delayMs = 1500 }: OnboardingGuideProps) {
  const { t } = useTranslation();
  const [currentStep, setCurrentStep] = useState(-1); // -1 = not started
  const [bubblePos, setBubblePos] = useState<{ top: number; left: number }>({ top: 0, left: 0 });
  const [visible, setVisible] = useState(false);

  const calculatePosition = useCallback((
    rect: DOMRect,
    position: OnboardingStep['position'],
  ): { top: number; left: number } => {
    switch (position) {
      case 'bottom-left':
        return { top: rect.top - 140, left: rect.left - 240 };
      case 'bottom-right':
        return { top: rect.bottom + 16, left: rect.left };
      case 'top-center':
        return { top: rect.bottom + 16, left: rect.left + rect.width / 2 - 150 };
      default:
        return { top: rect.bottom + 16, left: rect.left };
    }
  }, []);

  const completeOnboarding = useCallback(() => {
    setVisible(false);
    try {
      localStorage.setItem(STORAGE_KEY, 'true');
    } catch {
      // ignore
    }
  }, []);

  // 检查是否需要显示引导
  useEffect(() => {
    try {
      const done = localStorage.getItem(STORAGE_KEY);
      if (!done) {
        // 延迟后开始引导（等待首屏价值展示完成）
        const timer = setTimeout(() => {
          setCurrentStep(0);
          setVisible(true);
        }, delayMs);
        return () => clearTimeout(timer);
      }
    } catch {
      // localStorage 受限，跳过
    }
  }, [delayMs]);

  // 当前步骤变化时，定位气泡
  useEffect(() => {
    if (currentStep < 0 || currentStep >= STEPS.length) return;

    const frame = window.requestAnimationFrame(() => {
      const step = STEPS[currentStep];
      const el = document.getElementById(step.targetId);

      if (el) {
        const rect = el.getBoundingClientRect();
        const pos = calculatePosition(rect, step.position);
        setBubblePos(pos);
      } else if (step.fallbackPosition) {
        setBubblePos({
          top: (window.innerHeight * step.fallbackPosition.top) / 100,
          left: (window.innerWidth * step.fallbackPosition.left) / 100,
        });
      }
    });

    return () => window.cancelAnimationFrame(frame);
  }, [calculatePosition, currentStep]);

  const handleNext = useCallback(() => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      // 完成引导
      completeOnboarding();
    }
  }, [completeOnboarding, currentStep]);

  const handleSkip = useCallback(() => {
    completeOnboarding();
  }, [completeOnboarding]);

  if (!visible || currentStep < 0 || currentStep >= STEPS.length) return null;

  const step = STEPS[currentStep];

  // 保证气泡在可视区域内
  const constrainedPos = {
    top: Math.max(20, Math.min(window.innerHeight - 200, bubblePos.top)),
    left: Math.max(20, Math.min(window.innerWidth - 340, bubblePos.left)),
  };

  return (
    <>
      {/* 半透明遮罩 */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.4)',
          zIndex: 900,
          backdropFilter: 'blur(2px)',
          animation: 'fadeIn 0.3s ease',
        }}
        onClick={handleSkip}
      />

      {/* 引导气泡 */}
      <div
        id="onboarding-bubble"
        style={{
          position: 'fixed',
          top: constrainedPos.top,
          left: constrainedPos.left,
          zIndex: 910,
          width: 320,
          padding: 24,
          borderRadius: 20,
          background: 'rgba(8, 6, 18, 0.85)',
          backdropFilter: 'blur(24px) saturate(1.5)',
          border: '1px solid rgba(123, 97, 255, 0.3)',
          boxShadow: '0 8px 40px rgba(0, 0, 0, 0.5), 0 0 40px rgba(123, 97, 255, 0.1)',
          fontFamily: "'Inter', sans-serif",
          color: '#e0e0ff',
          animation: 'slideUpPanel 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        }}
      >
        {/* 步骤指示 */}
        <div style={{
          display: 'flex',
          gap: 6,
          marginBottom: 16,
        }}>
          {STEPS.map((_, idx) => (
            <div
              key={idx}
              style={{
                width: idx === currentStep ? 24 : 8,
                height: 4,
                borderRadius: 2,
                background: idx <= currentStep
                  ? 'linear-gradient(90deg, #7b61ff, #00e878)'
                  : 'rgba(255, 255, 255, 0.1)',
                transition: 'all 0.4s ease',
              }}
            />
          ))}
        </div>

        {/* 图标 + 标题 */}
        <div style={{ marginBottom: 12 }}>
          <span style={{ fontSize: 28, marginRight: 10 }}>{step.icon}</span>
          <span style={{
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: '0.03em',
          }}>
            {t(step.titleKey)}
          </span>
        </div>

        {/* 描述文本 */}
        <p style={{
          fontSize: 13,
          lineHeight: 1.7,
          opacity: 0.75,
          margin: '0 0 20px 0',
        }}>
          {t(step.descKey)}
        </p>

        {/* 按钮区 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button
            id="onboarding-skip"
            onClick={handleSkip}
            style={{
              background: 'none',
              border: 'none',
              color: 'rgba(255, 255, 255, 0.3)',
              fontSize: 12,
              cursor: 'pointer',
              fontFamily: "'Inter', sans-serif",
              padding: '6px 0',
            }}
          >
            {t('onboarding.skip')}
          </button>

          <button
            id="onboarding-next"
            onClick={handleNext}
            style={{
              padding: '10px 28px',
              borderRadius: 12,
              border: 'none',
              background: 'linear-gradient(135deg, rgba(123, 97, 255, 0.8), rgba(0, 232, 120, 0.6))',
              color: '#fff',
              fontSize: 13,
              fontWeight: 600,
              fontFamily: "'Inter', sans-serif",
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: '0 4px 16px rgba(123, 97, 255, 0.3)',
              letterSpacing: '0.03em',
            }}
          >
            {currentStep === STEPS.length - 1 ? t('onboarding.finish') : t('onboarding.next')}
          </button>
        </div>
      </div>
    </>
  );
}
