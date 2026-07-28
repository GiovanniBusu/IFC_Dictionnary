export type Language = "fr" | "en" | "it" | "de";

export interface VersionInfo {
  min_version: string;
  deprecated: string | null;
  new_in_43: boolean;
  version_notes: string;
}

export interface AvailablePredefinedType {
  value: string;
  description: string;
  since: string;
  new_in_43: boolean;
  deprecated_since: string | null;
}

export interface SearchResult {
  class: string;
  /** Libellé de classe dans la langue d'affichage demandée (output_lang). */
  class_label: string;
  predefined_type: string | null;
  score: number;
  matched_term: string;
  matched_language: Language;
  match_level: "class_name" | "class" | "predefined_type";
  /** Fil d'Ariane traduit dans la langue d'affichage ; les identifiants IFC
   * eux-mêmes (dans hierarchy_path) restent toujours en anglais. */
  category_path: string[];
  hierarchy_path: string[];
  version_info: VersionInfo;
  justification: string;
  alternative_reason: string;
  notes: string;
  /** Peuplé uniquement quand predefined_type est null (correspondance
   * générique sur la classe) : liste complète des PredefinedType existants,
   * pour que l'utilisateur puisse choisir lui-même. */
  available_predefined_types: AvailablePredefinedType[];
  psets_common: string[];
  custom_pset_guidance: string;
}

export interface SearchResponse {
  query: string;
  detected_language: Language | null;
  language_confident: boolean;
  /** Langue d'affichage effectivement utilisée pour ce résultat. */
  output_language: Language;
  suggestion: SearchResult | null;
  alternatives: SearchResult[];
  /** true si une langue a été forcée mais qu'aucune correspondance n'a été
   * trouvée dans cette langue : le résultat affiché retombe alors sur une
   * recherche toutes langues confondues. */
  forced_language_had_no_match: boolean;
}

export interface PredefinedType {
  value: string;
  since: string;
  deprecated_since: string | null;
  new_in_43: boolean;
  description_en: string;
  /** Description dans la langue d'affichage demandée (output_lang). */
  description: string;
  synonyms: Record<Language, string[]>;
}

export interface ClassDetail {
  class: string;
  class_label: string;
  parent: string;
  parent_known: boolean;
  children: string[];
  category_path: string[];
  ifc_versions: { introduced: string; current: string; deprecated: string | null };
  /** Version anglaise originale (bSDD), toujours disponible quelle que soit
   * la langue d'affichage — utilisée pour le panneau "version originale". */
  definition_en: string;
  definition: string;
  psets_common: string[];
  class_synonyms: Record<Language, string[]>;
  predefined_types: PredefinedType[];
  notes: string;
  version_notes: string;
  custom_pset_guidance: string;
}

export interface TreeNodeData {
  type: "category" | "class" | "predefined_type";
  name: string;
  ifc_class?: string;
  class_label?: string;
  predefined_type?: string;
  children: TreeNodeData[];
}
