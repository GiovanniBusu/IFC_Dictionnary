"""Moteur de recherche : correspondance texte libre -> classe(s) IFC.

Algorithme (cf. section 5 du cahier des charges) :
 1. détection de la langue de la requête
 2. recherche exacte dans la table de synonymes de la langue détectée
 3. à défaut, recherche floue (similarité de chaînes) toutes langues
    confondues, avec une pénalité si la langue du terme trouvé diffère de
    la langue détectée
 4. recherche « libre » : en complément de la requête entière, chaque mot
    significatif de la requête est aussi recherché individuellement (avec
    une pénalité), afin de gérer les descriptions vulgarisées à la manière
    d'une phrase (« l'endroit où l'on vient appuyer une dalle de
    transition ») plutôt qu'un terme exact
 5. scoring : proximité lexicale + spécificité (un match au niveau
    PredefinedType est plus spécifique qu'un simple synonyme de classe ;
    une expression de plusieurs mots est plus spécifique qu'un mot
    générique)
 6. tri des candidats ; le meilleur devient la suggestion principale, les
    3 à 5 suivants (au-dessus d'un seuil) deviennent les alternatives
 7. génération de la justification en français par gabarit de phrase
 8. si la suggestion principale ne pointe pas vers un PredefinedType précis
    (correspondance générique sur le nom de la classe), la liste complète
    des PredefinedType de cette classe est jointe au résultat pour
    permettre à l'utilisateur de choisir lui-même (section 3.2.1)
"""
from __future__ import annotations

from difflib import SequenceMatcher

from .data_loader import IfcReference, get_reference, normalize
from .language_detect import STOPWORDS, detect_language

MIN_ALTERNATIVE_SCORE = 0.45
MAX_ALTERNATIVES = 5
FUZZY_CUTOFF = 0.80
TOKEN_MATCH_DAMPING = 0.75
MIN_TOKEN_LENGTH = 4
ALL_STOPWORDS = {w for words in STOPWORDS.values() for w in words}
# Un terme identique au mot recherché (ex. « wall » == synonyme « wall »)
# doit toujours l'emporter sur un terme qui ne fait que CONTENIR ce mot par
# coïncidence (ex. « wave wall », « curtain wall panel »...), même si ce
# dernier porte un poids ou une spécificité plus élevée. Sans ce bonus, une
# requête générique (nom de classe nu) se retrouvait à pointer vers un
# PredefinedType arbitraire simplement parce que son synonyme anglais se
# terminait par le mot cherché.
EXACT_MATCH_BONUS = 0.35


SHORT_WORD_CONTAINMENT_DAMPING = 0.85
SHORT_WORD_THRESHOLD = 5


def _string_similarity(a: str, b: str) -> float:
    if a == b:
        return 1.0
    if len(a) >= 3 and len(b) >= 3 and (a in b or b in a):
        shorter, longer = sorted([a, b], key=len)
        score = 0.80 + 0.15 * (len(shorter) / len(longer))
        if len(shorter) <= SHORT_WORD_THRESHOLD:
            # Un mot générique court (« wall », « mur », « beam »...) se
            # retrouve, par pure coïncidence lexicale, à l'intérieur de
            # nombreux synonymes composés appartenant à d'AUTRES classes
            # (ex. « curtain wall panel » -> IfcPlate, « wall plate » ->
            # IfcMember). On atténue ce cas pour ne pas polluer les
            # résultats d'une classe non liée, sans pénaliser les
            # correspondances partielles sur des mots plus longs et
            # spécifiques (ex. « traversa » dans « traversa di
            # irrigidimento »).
            score *= SHORT_WORD_CONTAINMENT_DAMPING
        return score
    return SequenceMatcher(None, a, b).ratio()


def _specificity_bonus(level: str, term: str) -> float:
    bonus = 0.10 if level == "predefined_type" else 0.0
    word_count = len(term.split())
    bonus += 0.03 * min(word_count - 1, 3)
    return bonus


def _collect_candidates(query_norm: str, reference: IfcReference, detected_lang: str,
                         candidates: dict | None = None, damping: float = 1.0):
    """Alimente (et retourne) un dict {(class, predefined_type): meilleur score,
    match info}, en fusionnant avec les candidats déjà trouvés le cas échéant
    (utilisé pour combiner un score sur la requête entière et des scores sur
    des mots individuels de la requête, cf. `_token_candidates`)."""
    candidates = {} if candidates is None else candidates

    for lang in reference.index:
        lang_bonus = 0.05 if lang == detected_lang else 0.0
        for term_norm, matches in reference.index[lang].items():
            sim = _string_similarity(query_norm, term_norm)
            if sim < FUZZY_CUTOFF:
                continue
            exact_bonus = EXACT_MATCH_BONUS if query_norm == term_norm else 0.0
            for m in matches:
                base = sim * m["weight"]
                # Score de tri non plafonné (préserve l'ordre entre un match
                # exact et un match par confinement/flou qui atteindraient
                # tous deux ~1.0 après troncature) ; seul le score affiché
                # est ensuite ramené à l'intervalle [0, 1].
                raw_score = (base + exact_bonus + lang_bonus
                             + _specificity_bonus(m["level"], term_norm)) * damping
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


def _significant_tokens(query_norm: str) -> list[str]:
    """Mots significatifs d'une requête libre (description vulgarisée) :
    plus longs qu'un seuil et hors mots grammaticaux courants toutes
    langues confondues."""
    words = query_norm.split(" ")
    if len(words) < 2:
        return []
    return [w for w in words if len(w) >= MIN_TOKEN_LENGTH and w not in ALL_STOPWORDS]


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


def _available_predefined_types(entry: dict) -> list[dict]:
    """Liste complète des PredefinedType d'une classe, pour un affichage
    direct quand la requête ne pointe pas vers un type précis (ex.
    recherche générique « mur »/« wall ») — section 3.2.1 du cahier des
    charges : « et alors donner chaque PredefinedType »."""
    return [
        {
            "value": p["value"],
            "description_fr": p["description_fr"],
            "since": p["since"],
            "new_in_43": bool(p.get("new_in_43")),
            "deprecated_since": p.get("deprecated_since"),
        }
        for p in entry["predefined_types"]
        if p["value"] not in ("USERDEFINED", "NOTDEFINED")
    ]


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
        "available_predefined_types": (
            _available_predefined_types(entry) if predefined_type is None else []
        ),
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
    for token in _significant_tokens(query_norm):
        _collect_candidates(token, reference, detected_lang, candidates,
                             damping=TOKEN_MATCH_DAMPING)

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
