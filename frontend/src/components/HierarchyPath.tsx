import { Link } from "react-router-dom";
import type { SearchResult } from "../api/types";

export default function HierarchyPath({ result }: { result: SearchResult }) {
  const path = result.hierarchy_path;
  return (
    <div className="breadcrumb" aria-label="Position hiérarchique">
      {path.map((segment, i) => {
        const isLast = i === path.length - 1;
        return (
          <span key={`${segment}-${i}`} style={{ display: "inline-flex", gap: "0.3rem" }}>
            {isLast ? (
              <Link to={`/classe/${result.class}`} className="mono">
                {segment}
              </Link>
            ) : (
              <span>{segment}</span>
            )}
            {!isLast && <span className="breadcrumb__sep">→</span>}
          </span>
        );
      })}
    </div>
  );
}
