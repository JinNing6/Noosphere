/**
 * i18n 初始化配置
 *
 * 使用 react-i18next + 浏览器语言自动检测
 * 翻译资源直接打包进 bundle（无 HTTP 加载延迟）
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import zh from './locales/zh';
import en from './locales/en';
import ja from './locales/ja';
import ko from './locales/ko';
import fr from './locales/fr';
import es from './locales/es';

export const SUPPORTED_LANGUAGES = [
  { code: 'zh', label: '中文', flag: '🇨🇳' },
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'ja', label: '日本語', flag: '🇯🇵' },
  { code: 'ko', label: '한국어', flag: '🇰🇷' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'es', label: 'Español', flag: '🇪🇸' },
] as const;

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      zh: { translation: zh },
      en: { translation: en },
      ja: { translation: ja },
      ko: { translation: ko },
      fr: { translation: fr },
      es: { translation: es },
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React 已自带 XSS 防护
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'noosphere-lang',
    },
    react: {
      useSuspense: false, // 避免 3D Canvas 闪烁
    },
  });

export default i18n;
