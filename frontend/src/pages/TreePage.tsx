import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getClassDetail, getTree } from "../api/client";
import type { ClassDetail, TreeNodeData } from "../api/types";
import TreeNode from "../components/TreeNode";
import { useOutputLanguage } from "../outputLanguage";

export default function TreePage() {
  const [tree, setTree] = useState<TreeNodeData | null>(null);
  const [selected, setSelected] = useState<ClassDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { outputLang } = useOutputLanguage();

  useEffect(() => {
    getTree(outputLang)
      .then(setTree)
      .catch((err: Error) => setError(err.message));
  }, [outputLang]);

  const handleSelectClass = (ifcClass: string) => {
    getClassDetail(ifcClass, outputLang)
      .then(setSelected)
      .catch((err: Error) => setError(err.message));
  };

  return (
    <section>
      <h1>Parcourir la classification IFC</h1>
      <p style={{ color: "var(--text-muted)", marginTop: "0.3rem" }}>
        Arborescence complète : catégories → sous-catégories → classes → types prédéfinis
        (PredefinedType), jusqu'à IFC4X3.
      </p>

      {error && <div className="error-state">Erreur : {error}</div>}

      <div className="tree-panel" style={{ marginTop: "1rem" }}>
        <div className="tree-scroll">
          {tree ? (
            <TreeNode node={tree} depth={0} onSelectClass={handleSelectClass} defaultOpen />
          ) : (
            <div className="loading">Chargement de l'arborescence…</div>
          )}
        </div>

        <div>
          {!selected && (
            <div className="empty-state">
              Sélectionnez une classe dans l'arborescence pour afficher un aperçu.
            </div>
          )}
          {selected && (
            <div className="card card--primary">
              <div className="breadcrumb">
                {selected.category_path.map((seg, i) => (
                  <span key={i} style={{ display: "inline-flex", gap: "0.3rem" }}>
                    <span>{seg}</span>
                    <span className="breadcrumb__sep">→</span>
                  </span>
                ))}
                <span className="mono">{selected.class}</span>
              </div>
              <div className="card__class-name">{selected.class}</div>
              <div style={{ color: "var(--text-muted)", marginBottom: "0.5rem" }}>
                {selected.class_label}
              </div>
              <p>{selected.definition}</p>
              <p>
                <Link to={`/classe/${selected.class}`}>Voir la fiche détaillée →</Link>
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
