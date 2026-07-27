import { Link } from "react-router-dom";
import type { SearchResult } from "../api/types";
import VersionBadges from "./VersionBadges";
import HierarchyPath from "./HierarchyPath";

interface Props {
  result: SearchResult;
  variant: "primary" | "alternative";
}

export default function ResultCard({ result, variant }: Props) {
  const label = result.predefined_type
    ? `${result.class}.${result.predefined_type}`
    : result.class;

  return (
    <article className={`card ${variant === "primary" ? "card--primary" : "alt-card"}`}>
      <div className="card__header">
        <div>
          <div className="card__class-name">
            <Link to={`/classe/${result.class}`}>{label}</Link>
          </div>
          <div style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            {result.class_fr}
          </div>
        </div>
        <VersionBadges info={result.version_info} />
      </div>

      <HierarchyPath result={result} />

      {variant === "primary" ? (
        <p className="justification">{result.justification_fr}</p>
      ) : (
        <p className="justification">{result.alternative_reason_fr}</p>
      )}

      {result.notes_fr && variant === "primary" && (
        <div className="notes">{result.notes_fr}</div>
      )}

      <div
        style={{
          marginTop: "0.5rem",
          fontSize: "0.78rem",
          color: "var(--text-muted)",
        }}
      >
        Terme correspondant : « {result.matched_term} » ({result.matched_language.toUpperCase()}) ·
        score {Math.round(result.score * 100)}%
      </div>
    </article>
  );
}
