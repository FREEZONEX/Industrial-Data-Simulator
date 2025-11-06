// src/i18n.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 导入翻译文件
import zh from './locales/zh.json';
import en from './locales/en.json';

i18n
  .use(LanguageDetector)       // 可选，自动检测浏览器语言
  .use(initReactI18next)       // 绑定到 React
  .init({
    resources: {
      zh: { translation: zh },
      en: { translation: en },
    },
    fallbackLng: 'zh',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
