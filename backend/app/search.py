"""Moteur de recherche : correspondance texte libre -> classe(s) IFC.

Algorithme (cf. section 5 du cahier des charges) :
 1. détection de la langue de la requête
 2. recherche exacte dans la table de synonymes de la langue détectée
 3. à défaut, recherche floue (similarité de chaînes) toutes langues
    confondues, avec une pénalité si la langue du terme trouvé diffère de
    la langue détectée
 4. scoring : proximité lexicale + spécificité (un match au niveau
    PredefinedType est plus spécifique qu'un simple synonyme de classe ;
    une expression de plusieurs mots est plus spécifique qu'un mot
    générique)
 5. tri des candidats ; le meilleur devient la suggestion principale, les
    3 à 5 suivants (au-dessus d'un seuil) deviennent les alternatives
 6. génération de la justification en français par gabarit de phrase
"""
from __future__ import annotations

from difflib import SequenceMatcher

from .data_loader import IfcReference, get_reference, normalize
from .language_detect import detect_language

MIN_ALTERNATIVE_SCORE = 0.45
MAX_ALTERNATIVES = 5
FUZZY_CUTOFF = 0.80


def _string_similarity(a: str, b: str) -> float:
    if a == b:
        return 1.0
    if len(a) >= 3 and len(b) >= 3 and (a in b or b in a):
        shorter, longer = sorted([a, b], key=len)
        return 0.80 + 0.15 * (len(shorter) / len(longer))
    return SequenceMatcher(None, a, b).ratio()


def _specificity_bonus(level: str, term: str) -> float:
    bonus = 0.10 if level == "predefined_type" else 0.0
    word_count = len(term.split())
    bonus += 0.03 * min(word_count - 1, 3)
    return bonus


def _collect_candidates(query_norm: str, reference: IfcReference, detected_lang: str):
    """Retourne un dict {(class, predefined_type): meilleur score, match info}."""
    candidates: dict[tuple[str, str | None], dict] = {}

    for lang in reference.index:
        lang_bonus = 0.05 if lang == detected_lang else 0.0
        for term_norm, matches in reference.index[lang].items():
            sim = _string_similarity(query_norm, term_norm)
            if sim < FUZZY_CUTOFF:
                continue
            for m in matches:
                base = sim * m["weight"]
                # Score de tri non plafonné (préserve l'ordre entre un match
                # exact et un match par confinement/flou qui atteindraient
                # tous deux ~1.0 après troncature) ; seul le score affiché
                # est ensuite ramené à l'intervalle [0, 1].
                raw_score = base + lang_bonus + _specificity_bonus(m["level"], term_norm)
                key = (m["class"], m["predefined_type"])
                existing = candidates.get(key)
                if existing is None or raw_score > existing["raw_score"]:
                    candidates[key] = {
                        "raw_score": raw_score,
                        "score": min(raw_score, 1.0),
                        "matched_term": m["term"],
                        "matched_lang": lang,
                        "level": m["level"],
                    }
    return candidates


def _hierarchy_path(entry: dict, predefined_type: str | None) -> list[str]:
    path = list(entry["category_path"])
    leaf = entry["class"] + (f".{predefined_type}" if predefined_type else "")
    path.append(leaf)
    return path


def _version_info(entry: dict, pdt: dict | None) -> dict:
    info = {
        "min_version": entry["ifc_versions"]["introduced"],
        "deprecated": entry["ifc_versions"]["deprecated"],
        "new_in_43": False,
        "version_notes": entry.get("version_notes", ""),
    }
    if pdt:
        info["min_version"] = pdt["since"]
        info["new_in_43"] = bool(pdt.get("new_in_43"))
        info["deprecated"] = pdt.get("deprecated_since")
    return info


def _justification(entry: dict, pdt: dict | None, query: str, matched_term: str) -> str:
    class_fr = entry["class_fr"]
    class_name = entry["class"]
    label = class_name + (f".{pdt['value']}" if pdt else "")
    description = pdt["description_fr"] if pdt else entry["definition_fr"]
    path = " → ".join(_hierarchy_path(entry, pdt["value"] if pdt else None))

    sentence = (
        f"« {query} » se rapproche du terme référencé « {matched_term} », associé à "
        f"{class_fr} ({label}). {description} Position hiérarchique : {path}."
    )
    version = _version_info(entry, pdt)
    if version["new_in_43"]:
        sentence += " Ce type est une nouveauté d'IFC4.3."
    if version["deprecated"]:
        sentence += f" Attention : déprécié depuis IFC{version['deprecated']}."
    return sentence


def _alternative_reason(entry: dict, pdt: dict | None) -> str:
    if pdt and pdt.get("description_fr"):
        base = pdt["description_fr"]
    else:
        base = entry["definition_fr"]
    reason = f"Pertinent si : {base}"
    if entry.get("notes_fr"):
        reason += f" {entry['notes_fr']}"
    return reason


def _build_result(entry: dict, predefined_type: str | None, match_info: dict, query: str):
    pdt = None
    if predefined_type:
        pdt = next((p for p in entry["predefined_types"] if p["value"] == predefined_type), None)
    return {
        "class": entry["class"],
        "class_fr": entry["class_fr"],
        "predefined_type": predefined_type,
        "score": round(match_info["score"], 3),
        "matched_term": match_info["matched_term"],
        "matched_language": match_info["matched_lang"],
        "match_level": match_info["level"],
        "category_path": entry["category_path"],
        "hierarchy_path": _hierarchy_path(entry, predefined_type),
        "version_info": _version_info(entry, pdt),
        "justification_fr": _justification(entry, pdt, query, match_info["matched_term"]),
        "alternative_reason_fr": _alternative_reason(entry, pdt),
        "notes_fr": entry.get("notes_fr", ""),
    }


def search(query: str, forced_language: str | None = None, reference: IfcReference | None = None):
    reference = reference or get_reference()
    query = query.strip()
    if not query:
        return {"query": query, "detected_language": None, "language_confident": False,
                "suggestion": None, "alternatives": []}

    guess = detect_language(query, reference)
    detected_lang = forced_language or guess.language

    query_norm = normalize(query)
    candidates = _collect_candidates(query_norm, reference, detected_lang)

    ranked = sorted(candidates.items(), key=lambda kv: kv[1]["raw_score"], reverse=True)

    results = []
    for (ifc_class, predefined_type), match_info in ranked:
        entry = reference.get_class(ifc_class)
        if not entry:
            continue
        results.append(_build_result(entry, predefined_type, match_info, query))

    suggestion = results[0] if results else None
    alternatives = [
        r for r in results[1:]
        if r["score"] >= MIN_ALTERNATIVE_SCORE
    ][:MAX_ALTERNATIVES]

    return {
        "query": query,
        "detected_language": detected_lang,
        "language_confident": guess.confident if not forced_language else True,
        "suggestion": suggestion,
        "alternatives": alternatives,
    }
