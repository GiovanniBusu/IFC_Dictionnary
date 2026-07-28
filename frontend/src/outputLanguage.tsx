import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { Language } from "./api/types";

const STORAGE_KEY = "ifc-dict-output-lang";

function readStored(): Language {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === "fr" || stored === "en" || stored === "it" || stored === "de") return stored;
  return "fr";
}

interface OutputLanguageContextValue {
  outputLang: Language;
  setOutputLang: (lang: Language) => void;
}

const OutputLanguageContext = createContext<OutputLanguageContextValue | null>(null);

/** Langue d'AFFICHAGE des résultats (justification, description, notes),
 * mémorisée dans le navigateur : indépendante de la langue de RECHERCHE
 * (celle-ci reste un réglage ponctuel par requête, cf. SearchPage). */
export function OutputLanguageProvider({ children }: { children: ReactNode }) {
  const [outputLang, setOutputLangState] = useState<Language>(readStored);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, outputLang);
  }, [outputLang]);

  return (
    <OutputLanguageContext.Provider value={{ outputLang, setOutputLang: setOutputLangState }}>
      {children}
    </OutputLanguageContext.Provider>
  );
}

export function useOutputLanguage(): OutputLanguageContextValue {
  const ctx = useContext(OutputLanguageContext);
  if (!ctx) throw new Error("useOutputLanguage must be used within OutputLanguageProvider");
  return ctx;
}
