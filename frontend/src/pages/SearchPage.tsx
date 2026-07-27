import { useEffect, useState } from "react";
import { search } from "../api/client";
import type { Language, SearchResponse } from "../api/types";
import ResultCard from "../components/ResultCard";

const LANGUAGE_LABELS: Record<Language, string> = {
  fr: "français",
  en: "anglais",
  it: "italien",
  de: "allemand",
};

const DEBOUNCE_MS = 250;

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [forcedLang, setForcedLang] = useState<Language | "">("");
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAlternatives, setShowAlternatives] = useState(true);

  useEffect(() => {
    const trimmed = query.trim();
    if (!trimmed) {
      setResult(null);
      setError(null);
      return;
    }
    setLoading(true);
    const handle = setTimeout(() => {
      search(trimmed, forcedLang || undefined)
        .then((res) => {
          setResult(res);
          setError(null);
        })
        .catch((err: Error) => setError(err.message))
        .finally(() => setLoading(false));
    }, DEBOUNCE_MS);
    return () => clearTimeout(handle);
  }, [query, forcedLang]);

  return (
    <section>
      <h1>Rechercher un élément de construction</h1>
      <p style={{ color: "var(--text-muted)", marginTop: "0.3rem" }}>
        Saisissez un nom, une description ou une classe IFC (français, anglais, italien ou
        allemand).
      </p>

      <div className="search-box" style={{ marginTop: "0.9rem" }}>
        <input
          type="text"
          className="search-input"
          placeholder="ex. raidisseur, garde-corps, chape, IfcWall…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
          aria-label="Terme de recherche"
        />
      </div>

      <div className="search-meta">
        {result?.detected_language && (
          <span
            className={`badge ${result.language_confident ? "badge--accent" : ""}`}
            title="Langue détectée automatiquement dans le terme saisi"
          >
            détecté : {LANGUAGE_LABELS[result.detected_language]}
            {!result.language_confident && " (incertain)"}
          </span>
        )}
        <label style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
          Forcer la langue :{" "}
          <select
            className="lang-select"
            value={forcedLang}
            onChange={(e) => setForcedLang(e.target.value as Language | "")}
          >
            <option value="">automatique</option>
            <option value="fr">français</option>
            <option value="en">anglais</option>
            <option value="it">italien</option>
            <option value="de">allemand</option>
          </select>
        </label>
      </div>

      {!loading && result?.forced_language_had_no_match && (
        <div className="notes" style={{ marginTop: "0.7rem" }}>
          Aucune correspondance trouvée en {LANGUAGE_LABELS[forcedLang as Language]} pour «{" "}
          {query} ». Résultat affiché toutes langues confondues à la place.
        </div>
      )}

      {loading && <div className="loading">Recherche en cours…</div>}
      {error && <div className="error-state">Erreur : {error}</div>}

      {!loading && !error && query.trim() && result && !result.suggestion && (
        <div className="empty-state">
          Aucune correspondance trouvée pour « {query} ». Essayez un terme plus général, ou
          vérifiez l'orthographe.
        </div>
      )}

      {!loading && result?.suggestion && (
        <>
          <ResultCard result={result.suggestion} variant="primary" />

          {result.alternatives.length > 0 && (
            <>
              <button
                className="alternatives-toggle"
                onClick={() => setShowAlternatives((v) => !v)}
                aria-expanded={showAlternatives}
              >
                <span>Alternatives plausibles ({result.alternatives.length})</span>
                <span>{showAlternatives ? "▾" : "▸"}</span>
              </button>
              {showAlternatives &&
                result.alternatives.map((alt) => (
                  <ResultCard
                    key={`${alt.class}.${alt.predefined_type ?? ""}`}
                    result={alt}
                    variant="alternative"
                  />
                ))}
            </>
          )}
        </>
      )}
    </section>
  );
}
