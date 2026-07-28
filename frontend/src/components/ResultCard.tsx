import { Link } from "react-router-dom";
import type { SearchResult } from "../api/types";
import VersionBadges from "./VersionBadges";
import HierarchyPath from "./HierarchyPath";
import { useOutputLanguage } from "../outputLanguage";
import { UI_STRINGS } from "../uiStrings";

interface Props {
  result: SearchResult;
  variant: "primary" | "alternative";
}

export default function ResultCard({ result, variant }: Props) {
  const { outputLang } = useOutputLanguage();
  const t = UI_STRINGS[outputLang];
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
            {result.class_label}
          </div>
        </div>
        <VersionBadges info={result.version_info} />
      </div>

      <HierarchyPath result={result} />

      {variant === "primary" ? (
        <p className="justification">{result.justification}</p>
      ) : (
        <p className="justification">{result.alternative_reason}</p>
      )}

      {result.available_predefined_types.length > 0 && (
        <div className="predefined-types-list">
          <div className="predefined-types-list__label">
            {t.availableTypesFor} {result.class} :
          </div>
          <ul>
            {result.available_predefined_types.map((p) => (
              <li key={p.value}>
                <span className="mono">{p.value}</span>
                {p.new_in_43 && <span className="badge badge--accent">4.3</span>}
                {p.deprecated_since && (
                  <span className="badge badge--warning">déprécié</span>
                )}
                <span className="predefined-types-list__desc">{p.description}</span>
              </li>
            ))}
          </ul>
          <p className="predefined-types-list__hint">
            {t.refineHint} {result.class_label.toLowerCase()}{" "}
            {result.available_predefined_types[0].value.toLowerCase()}
            {t.refineHintEnd}{" "}
            <Link to={`/classe/${result.class}`}>{t.detailSheet}</Link> {t.forCompleteList}
          </p>
        </div>
      )}

      {variant === "primary" && result.psets_common.length > 0 && (
        <div className="psets-block">
          <div className="psets-block__label">{t.whichPset}</div>
          <div className="synonym-list">
            {result.psets_common.map((p) => (
              <span className="synonym-chip mono" key={p}>
                {p}
              </span>
            ))}
          </div>
          <p className="psets-block__guidance">{result.custom_pset_guidance}</p>
        </div>
      )}

      {result.notes && variant === "primary" && (
        <div className="notes">{result.notes}</div>
      )}

      <div
        style={{
          marginTop: "0.5rem",
          fontSize: "0.78rem",
          color: "var(--text-muted)",
        }}
      >
        {t.matchedTerm} : « {result.matched_term} » ({result.matched_language.toUpperCase()}) ·
        {t.score} {Math.round(result.score * 100)}%
      </div>
    </article>
  );
}
