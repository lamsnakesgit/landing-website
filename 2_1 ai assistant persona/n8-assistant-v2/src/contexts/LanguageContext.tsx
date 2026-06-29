"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { ru } from "../locales/ru";
import { en } from "../locales/en";

type Language = "ru" | "en";
type Translations = typeof ru;

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: React.ReactNode }) => {
  const [lang, setLangState] = useState<Language>("ru");

  useEffect(() => {
    // Check localStorage on mount
    const savedLang = localStorage.getItem("lang") as Language;
    if (savedLang === "ru" || savedLang === "en") {
      setLangState(savedLang);
    } else {
      // Auto-detect based on browser preference if desired, but default to 'ru'
      setLangState("ru");
    }
  }, []);

  const setLang = (newLang: Language) => {
    setLangState(newLang);
    localStorage.setItem("lang", newLang);
  };

  const t = lang === "ru" ? ru : en;

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
};
