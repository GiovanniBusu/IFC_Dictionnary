import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getClassDetail } from "../api/client";
import type { ClassDetail, Language } from "../api/types";

const LANGUAGE_LABELS: Record<Language, string> = {
  fr: "Français",
  en: "Anglais",
  it: "Italien",
  de: "Allemand",
};

export default function ClassDetailPage() {
  const { ifcClass } = useParams<{ ifcClass: string }>();
  const [detail, setDetail] = useState<ClassDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showEnglish, setShowEnglish] = useState(false);

  useEffect(() => {
    if (!ifcClass) return;
    setDetail(null);
    setError(null);
    getClassDetail(ifcClass)
      .then(setDetail)
      .catch((err: Error) => setError(err.message));
  }, [ifcClass]);

  if (error) return <div className="error-state">Erreur : {error}</div>;
  if (!detail) return <div className="loading">Chargement…</div>;

  return (
    <section>
      <div className="breadcrumb">
        <Link to="/parcourir">Parcourir</Link>
        <span className="breadcrumb__sep">→</span>
        {detail.category_path.map((seg, i) => (
          <span key={i} style={{ display: "inline-flex", gap: "0.3rem" }}>
            <span>{seg}</span>
            <span className="breadcrumb__sep">→</span>
          </span>
        ))}
        <span className="mono">{detail.class}</span>
      </div>

      <h1 className="mono">{detail.class}</h1>
      <p style={{ color: "var(--text-muted)" }}>{detail.class_fr}</p>

      <div className="card">
        <h3>Définition</h3>
        <div className="definition-block">
          <div className="definition-block__label">Français</div>
          <p style={{ margin: 0 }}>{detail.definition_fr}</p>
        </div>
        <button
          className="alternatives-toggle"
          onClick={() => setShowEnglish((v) => !v)}
          aria-expanded={showEnglish}
        >
          <span>Version originale anglaise (buildingSMART)</span>
          <span>{showEnglish ? "▾" : "▸"}</span>
        </button>
        {showEnglish && (
          <div className="definition-block" style={{ marginTop: "0.5rem" }}>
            <div className="definition-block__label">English</div>
            <p style={{ margin: 0 }}>{detail.definition_en}</p>
          </div>
        )}
      </div>

      <div className="card">
        <h3>Position dans la hiérarchie</h3>
        <p>
          Classe parente :{" "}
          {detail.parent_known ? (
            <Link to={`/classe/${detail.parent}`} className="mono">
              {detail.parent}
            </Link>
          ) : (
            <span className="mono">{detail.parent}</span>
          )}
        </p>
        {detail.children.length > 0 && (
          <p>
            Classes filles référencées :{" "}
            {detail.children.map((c, i) => (
              <span key={c}>
                <Link to={`/classe/${c}`} className="mono">
                  {c}
                </Link>
                {i < detail.children.length - 1 && ", "}
              </span>
            ))}
          </p>
        )}
      </div>

      {detail.predefined_types.length > 0 && (
        <div className="card">
          <h3>Types prédéfinis (PredefinedType)</h3>
          <table className="pdt-table">
            <thead>
              <tr>
                <th>Valeur</th>
                <th>Depuis</th>
                <th>Description (FR)</th>
                <th>Synonymes</th>
              </tr>
            </thead>
            <tbody>
              {detail.predefined_types.map((pdt) => (
                <tr key={pdt.value}>
                  <td className="mono">
                    {pdt.value}
                    {pdt.new_in_43 && (
                      <div className="badge badge--accent" style={{ marginTop: "0.25rem" }}>
                        Nouveau en 4.3
                      </div>
                    )}
                    {pdt.deprecated_since && (
                      <div className="badge badge--warning" style={{ marginTop: "0.25rem" }}>
                        Déprécié {pdt.deprecated_since}
                      </div>
                    )}
                  </td>
                  <td>IFC {pdt.since}</td>
                  <td>{pdt.description_fr}</td>
                  <td>
                    {(Object.keys(pdt.synonyms) as Language[]).map((lang) =>
                      pdt.synonyms[lang].length ? (
                        <div key={lang} style={{ marginBottom: "0.3rem" }}>
                          <strong style={{ fontSize: "0.72rem" }}>
                            {LANGUAGE_LABELS[lang]} :{" "}
                          </strong>
                          <span className="synonym-list" style={{ display: "inline-flex" }}>
                            {pdt.synonyms[lang].map((s) => (
                              <span className="synonym-chip" key={s}>
                                {s}
                              </span>
                            ))}
                          </span>
                        </div>
                      ) : null
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {detail.psets_common.length > 0 && (
        <div className="card">
          <h3>Property Sets couramment associés</h3>
          <div className="synonym-list">
            {detail.psets_common.map((p) => (
              <span className="synonym-chip mono" key={p}>
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <h3>Historique de version</h3>
        <p>
          Introduit en IFC{detail.ifc_versions.introduced}, version courante IFC
          {detail.ifc_versions.current}.
          {detail.ifc_versions.deprecated &&
            ` Déprécié depuis IFC${detail.ifc_versions.deprecated}.`}
        </p>
        {detail.version_notes && <p style={{ color: "var(--text-muted)" }}>{detail.version_notes}</p>}
      </div>

      {detail.notes_fr && <div className="notes">{detail.notes_fr}</div>}
    </section>
  );
}
