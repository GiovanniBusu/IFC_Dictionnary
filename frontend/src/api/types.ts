export type Language = "fr" | "en" | "it" | "de";

export interface VersionInfo {
  min_version: string;
  deprecated: string | null;
  new_in_43: boolean;
  version_notes: string;
}

export interface SearchResult {
  class: string;
  class_fr: string;
  predefined_type: string | null;
  score: number;
  matched_term: string;
  matched_language: Language;
  match_level: "class_name" | "class" | "predefined_type";
  category_path: string[];
  hierarchy_path: string[];
  version_info: VersionInfo;
  justification_fr: string;
  alternative_reason_fr: string;
  notes_fr: string;
}

export interface SearchResponse {
  query: string;
  detected_language: Language | null;
  language_confident: boolean;
  suggestion: SearchResult | null;
  alternatives: SearchResult[];
}

export interface PredefinedType {
  value: string;
  since: string;
  deprecated_since: string | null;
  new_in_43: boolean;
  description_en: string;
  description_fr: string;
  synonyms: Record<Language, string[]>;
}

export interface ClassDetail {
  class: string;
  class_fr: string;
  parent: string;
  parent_known: boolean;
  children: string[];
  category_path: string[];
  ifc_versions: { introduced: string; current: string; deprecated: string | null };
  definition_en: string;
  definition_fr: string;
  psets_common: string[];
  class_synonyms: Record<Language, string[]>;
  predefined_types: PredefinedType[];
  notes_fr: string;
  version_notes: string;
}

export interface TreeNodeData {
  type: "category" | "class" | "predefined_type";
  name: string;
  ifc_class?: string;
  class_fr?: string;
  predefined_type?: string;
  children: TreeNodeData[];
}
