import { NavLink, Route, Routes } from "react-router-dom";
import SearchPage from "./pages/SearchPage";
import TreePage from "./pages/TreePage";
import ClassDetailPage from "./pages/ClassDetailPage";
import { useOutputLanguage } from "./outputLanguage";
import type { Language } from "./api/types";

const OUTPUT_LANGUAGE_LABELS: Record<Language, string> = {
  fr: "Français",
  en: "English",
  it: "Italiano",
  de: "Deutsch",
};

function App() {
  const { outputLang, setOutputLang } = useOutputLanguage();

  return (
    <>
      <header className="app-header">
        <div className="app-header__inner">
          <span className="app-header__title">Dictionnaire IFC interactif</span>
          <nav className="app-nav">
            <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
              Rechercher
            </NavLink>
            <NavLink to="/parcourir" className={({ isActive }) => (isActive ? "active" : "")}>
              Parcourir la classification
            </NavLink>
          </nav>
          <label
            style={{ marginLeft: "auto", fontSize: "0.82rem", color: "var(--text-muted)" }}
            title="Langue d'affichage des résultats (définitions, notes, justifications) — indépendante de la langue de recherche"
          >
            Afficher en :{" "}
            <select
              className="lang-select"
              value={outputLang}
              onChange={(e) => setOutputLang(e.target.value as Language)}
            >
              {(Object.keys(OUTPUT_LANGUAGE_LABELS) as Language[]).map((lang) => (
                <option key={lang} value={lang}>
                  {OUTPUT_LANGUAGE_LABELS[lang]}
                </option>
              ))}
            </select>
          </label>
        </div>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/parcourir" element={<TreePage />} />
          <Route path="/classe/:ifcClass" element={<ClassDetailPage />} />
        </Routes>
      </main>
      <footer className="app-footer">
        Référentiel IFC4X3_ADD2 (sous-ensemble curé) — buildingSMART International
      </footer>
    </>
  );
}

export default App;
