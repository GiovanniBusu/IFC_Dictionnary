import type { VersionInfo } from "../api/types";

export default function VersionBadges({ info }: { info: VersionInfo }) {
  return (
    <div className="card__badges">
      <span className="badge" title="Version IFC minimale requise pour ce type">
        Depuis IFC {info.min_version}
      </span>
      {info.new_in_43 && (
        <span className="badge badge--accent" title="Introduit dans la révision IFC4.3">
          Nouveau en IFC4.3
        </span>
      )}
      {info.deprecated && (
        <span
          className="badge badge--warning"
          title="Ce type est marqué comme déprécié dans le schéma IFC"
        >
          Déprécié depuis IFC {info.deprecated}
        </span>
      )}
    </div>
  );
}
