"""Détection heuristique de la langue d'une requête (FR/EN/IT/DE).

Approche à deux niveaux, adaptée aux requêtes courtes typiques d'un
dictionnaire technique (un ou deux mots) :

1. Dictionnaire : si le terme saisi (normalisé) figure dans la table de
   synonymes d'une seule langue, on retient directement cette langue avec
   une confiance élevée.
2. Heuristique lexicale : à défaut, on note le texte selon des indices
   caractéristiques de chaque langue (caractères accentués propres, mots
   grammaticaux fréquents) et on retient le meilleur score.

Ceci évite une dépendance à une bibliothèque de détection statistique
(peu fiable sur des textes de quelques caractères) tout en restant simple
et déterministe pour l'utilisation hors-ligne.
"""
from __future__ import annotations

from dataclasses import dataclass

from .data_loader import IfcReference, normalize

# Mots grammaticaux / stopwords fréquents par langue (poids égal pour tous)
STOPWORDS = {
    "fr": {"de", "le", "la", "les", "du", "des", "un", "une", "et", "en",
           "pour", "avec", "sur", "dans", "au", "aux", "ou", "est", "sont"},
    "en": {"the", "of", "and", "a", "an", "for", "with", "on", "in", "to",
           "is", "are", "or"},
    "it": {"il", "lo", "la", "i", "gli", "le", "di", "e", "per", "con",
           "su", "in", "un", "una", "è", "sono"},
    "de": {"der", "die", "das", "und", "für", "mit", "auf", "in", "ein",
           "eine", "ist", "sind", "oder", "den", "dem"},
}

# Caractères / séquences fortement caractéristiques d'une langue donnée
CHAR_HINTS = {
    "de": set("ßüöä"),
    "fr": set("éèêàçùâîôûï"),
    "it": set("àèìòù"),
}

DEFAULT_LANGUAGE = "fr"  # l'interface étant en français, on privilégie le FR
# en cas d'ambiguïté totale.


@dataclass
class LanguageGuess:
    language: str
    confident: bool


def _dictionary_lookup(query_norm: str, reference: IfcReference) -> str | None:
    matches = [lang for lang in reference.index if query_norm in reference.index[lang]]
    if len(matches) == 1:
        return matches[0]
    return None


def _heuristic_score(query: str) -> dict:
    scores = {lang: 0.0 for lang in ("fr", "en", "it", "de")}
    lower = query.lower()
    words = [w.strip(".,;:!?()") for w in lower.split()]

    for lang, hint_chars in CHAR_HINTS.items():
        for ch in lower:
            if ch in hint_chars:
                scores[lang] += 1.0

    for lang, stop in STOPWORDS.items():
        for w in words:
            if w in stop:
                scores[lang] += 2.0

    # Terminaisons indicatives simples
    for w in words:
        if w.endswith(("tion", "eau", "age")):
            scores["fr"] += 0.3
        if w.endswith(("ung", "heit", "keit", "chen")):
            scores["de"] += 0.5
        if w.endswith(("zione", "aggio", "etto", "etta")):
            scores["it"] += 0.5
        if w.endswith("ing") or w.endswith("ness"):
            scores["en"] += 0.3

    return scores


def detect_language(query: str, reference: IfcReference) -> LanguageGuess:
    query_norm = normalize(query)
    if not query_norm:
        return LanguageGuess(DEFAULT_LANGUAGE, False)

    dict_hit = _dictionary_lookup(query_norm, reference)
    if dict_hit:
        return LanguageGuess(dict_hit, True)

    # Un terme composé : tester chaque mot individuellement au dictionnaire
    words = query_norm.split()
    if len(words) > 1:
        per_word_hits = [_dictionary_lookup(w, reference) for w in words]
        per_word_hits = [w for w in per_word_hits if w]
        if per_word_hits:
            # langue la plus fréquente parmi les mots reconnus
            best = max(set(per_word_hits), key=per_word_hits.count)
            return LanguageGuess(best, True)

    scores = _heuristic_score(query)
    best_lang = max(scores, key=scores.get)
    best_score = scores[best_lang]
    if best_score <= 0:
        return LanguageGuess(DEFAULT_LANGUAGE, False)
    # confiance faible si l'écart avec la 2e langue est faible
    ranked = sorted(scores.values(), reverse=True)
    confident = len(ranked) < 2 or (ranked[0] - ranked[1]) >= 1.0
    return LanguageGuess(best_lang, confident)
