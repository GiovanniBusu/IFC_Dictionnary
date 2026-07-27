"""Moteur de recherche : correspondance texte libre -> classe(s) IFC.

Algorithme (cf. section 5 du cahier des charges) :
 1. détection heuristique de la langue de la requête (utilisée comme
    repli d'affichage et comme bonus de tri interne, jamais comme seul
    juge de ce qui est un « bon » résultat — cf. point 7)
 2. recherche exacte dans la table de synonymes ; si une langue est
    forcée par l'utilisateur, la recherche est RESTREINTE à cette seule
    langue (et non plus une recherche toutes langues avec simple bonus,
    qui rendait le forçage quasiment sans effet)
 3. à défaut de correspondance exacte, recherche floue (similarité de
    chaînes, tolérante aux fautes de frappe/orthographe) dans le même
    périmètre de langues, avec une pénalité si la langue du terme trouvé
    diffère de la langue de référence pour le tri
 4. recherche « libre » : en complément de la requête entière, chaque mot
    significatif de la requête est aussi recherché individuellement (avec
    une pénalité), afin de gérer les descriptions vulgarisées à la manière
    d'une phrase (« l'endroit où l'on vient appuyer une dalle de
    transition ») plutôt qu'un terme exact
 5. scoring : proximité lexicale + spécificité (un match au niveau
    PredefinedType est plus spécifique qu'un simple synonyme de classe ;
    une expression de plusieurs mots est plus spécifique qu'un mot
    générique). L'atténuation appliquée aux mots courts contenus par
    coïncidence dans un synonyme composé (« wall » dans « curtain wall
    panel ») ne s'applique QUE si le mot ne couvre qu'une petite fraction
    du terme trouvé, afin de ne pas pénaliser une faute de frappe ou une
    troncature légitime (« poutr » -> « poutre »)
 6. tri des candidats ; le meilleur devient la suggestion principale, les
    3 à 5 suivants (au-dessus d'un seuil) deviennent les alternatives
 7. si une langue est forcée et qu'AUCUNE correspondance n'existe dans
    cette langue, repli explicite sur une recherche toutes langues
    confondues plutôt que de renvoyer un résultat vide (ce serait
    contraire à la tolérance recherchée) ; ce repli est signalé via
    `forced_language_had_no_match` pour rester transparent. La langue
    affichée (`detected_language`) est alors dérivée a posteriori de la
    langue du terme qui a effectivement gagné (fait vérifiable), et non
    plus d'une supposition faite avant la recherche
 8. génération de la justification en français par gabarit de phrase
 9. si la suggestion principale ne pointe pas vers un PredefinedType précis
    (correspondance générique sur le nom de la classe), la liste complète
    des PredefinedType de cette classe est jointe au résultat pour
    permettre à l'utilisateur de choisir lui-même (section 3.2.1)
"""
from __future__ import annotations

from difflib import SequenceMatcher

from .data_loader import CUSTOM_PSET_GUIDANCE, IfcReference, get_reference, normalize
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
SHORT_WORD_RATIO_THRESHOLD = 0.6


def _string_similarity(a: str, b: str) -> float:
    if a == b:
        return 1.0
    if len(a) >= 3 and len(b) >= 3 and (a in b or b in a):
        shorter, longer = sorted([a, b], key=len)
        ratio = len(shorter) / len(longer)
        score = 0.80 + 0.15 * ratio
        if len(shorter) <= SHORT_WORD_THRESHOLD and ratio < SHORT_WORD_RATIO_THRESHOLD:
            # Un mot générique court (« wall », « mur », « beam »...) se
            # retrouve, par pure coïncidence lexicale, à l'intérieur de
            # nombreux synonymes composés appartenant à d'AUTRES classes
            # (ex. « curtain wall panel » -> IfcPlate, « wall plate » ->
            # IfcMember) : il ne représente alors qu'une PETITE fraction du
            # terme trouvé (ratio faible). On atténue seulement ce cas-là.
            # Un mot court tronqué ou avec une faute de frappe (« poutr » ->
            # « poutre », « murr » -> « mur ») couvre au contraire la quasi-
            # totalité du terme (ratio élevé) et ne doit PAS être pénalisé.
            score *= SHORT_WORD_CONTAINMENT_DAMPING
        return score
    return SequenceMatcher(None, a, b).ratio()


def _specificity_bonus(level: str, term: str) -> float:
    bonus = 0.10 if level == "predefined_type" else 0.0
    word_count = len(term.split())
    bonus += 0.03 * min(word_count - 1, 3)
    return bonus


def _collect_candidates(query_norm: str, reference: IfcReference, detected_lang: str,
                         candidates: dict | None = None, damping: float = 1.0,
                         languages: tuple[str, ...] | None = None):
    """Alimente (et retourne) un dict {(class, predefined_type): meilleur score,
    match info}, en fusionnant avec les candidats déjà trouvés le cas échéant
    (utilisé pour combiner un score sur la requête entière et des scores sur
    des mots individuels de la requête, cf. `_token_candidates`).

    `languages` restreint la recherche à un sous-ensemble de langues (utilisé
    quand l'utilisateur force une langue : section 6 du cahier des charges).
    Par défaut (None), toutes les langues du référentiel sont parcourues, ce
    qui permet la tolérance aux requêtes multilingues/mixtes."""
    candidates = {} if candidates is None else candidates
    search_languages = languages if languages is not None else tuple(reference.index)

    for lang in search_languages:
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
        "psets_common": entry.get("psets_common", []),
        "custom_pset_guidance": CUSTOM_PSET_GUIDANCE,
    }


def _rank_results(query: str, query_norm: str, reference: IfcReference,
                   bonus_target_lang: str, languages: tuple[str, ...] | None):
    candidates = _collect_candidates(query_norm, reference, bonus_target_lang, languages=languages)
    for token in _significant_tokens(query_norm):
        _collect_candidates(token, reference, bonus_target_lang, candidates,
                             damping=TOKEN_MATCH_DAMPING, languages=languages)
    ranked = sorted(candidates.items(), key=lambda kv: kv[1]["raw_score"], reverse=True)
    results = []
    for (ifc_class, predefined_type), match_info in ranked:
        entry = reference.get_class(ifc_class)
        if not entry:
            continue
        results.append(_build_result(entry, predefined_type, match_info, query))
    suggestion = results[0] if results else None
    alternatives = [r for r in results[1:] if r["score"] >= MIN_ALTERNATIVE_SCORE][:MAX_ALTERNATIVES]
    return suggestion, alternatives


def search(query: str, forced_language: str | None = None, reference: IfcReference | None = None):
    reference = reference or get_reference()
    query = query.strip()
    if not query:
        return {"query": query, "detected_language": None, "language_confident": False,
                "suggestion": None, "alternatives": [], "forced_language_had_no_match": False}

    guess = detect_language(query, reference)
    query_norm = normalize(query)
    forced_language_had_no_match = False

    if forced_language:
        # La recherche est d'abord restreinte à la seule langue forcée (et
        # non plus « toutes les langues avec un simple bonus de 0.05 pour
        # celle-ci ») : sans cette restriction, forcer une langue n'avait
        # presque aucun effet, un match exact dans une AUTRE langue (ex.
        # « Aussteifung » en allemand) l'emportant toujours sur le bonus.
        suggestion, alternatives = _rank_results(
            query, query_norm, reference, forced_language, languages=(forced_language,)
        )
        if suggestion is None:
            # Repli : rien dans la langue forcée (faute de frappe sur le
            # sélecteur, ou terme d'une autre langue) -> on retombe sur une
            # recherche toutes langues plutôt que de laisser l'utilisateur
            # face à un « aucun résultat » silencieux ; le repli est signalé
            # explicitement pour rester transparent sur ce qui s'est passé.
            suggestion, alternatives = _rank_results(
                query, query_norm, reference, guess.language, languages=None
            )
            forced_language_had_no_match = True
    else:
        suggestion, alternatives = _rank_results(
            query, query_norm, reference, guess.language, languages=None
        )

    if forced_language and not forced_language_had_no_match:
        # La langue affichée est alors littéralement celle demandée par
        # l'utilisateur : pas une supposition, un fait.
        detected_lang_out = forced_language
        confident_out = True
    elif suggestion:
        # La langue affichée est celle du synonyme qui a effectivement
        # produit la meilleure correspondance (fait vérifiable), plutôt
        # qu'une supposition heuristique faite AVANT la recherche : le badge
        # « détecté : X » est ainsi toujours exact par construction.
        detected_lang_out = suggestion["matched_language"]
        confident_out = True
    else:
        # Aucune correspondance, dans aucune langue : on affiche la
        # meilleure estimation heuristique à titre indicatif, explicitement
        # marquée incertaine.
        detected_lang_out = guess.language
        confident_out = False

    return {
        "query": query,
        "detected_language": detected_lang_out,
        "language_confident": confident_out,
        "suggestion": suggestion,
        "alternatives": alternatives,
        "forced_language_had_no_match": forced_language_had_no_match,
    }
