import { NavLink, Route, Routes } from "react-router-dom";
import SearchPage from "./pages/SearchPage";
import TreePage from "./pages/TreePage";
import ClassDetailPage from "./pages/ClassDetailPage";

function App() {
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
