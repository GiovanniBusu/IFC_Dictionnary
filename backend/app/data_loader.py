"""Chargement et indexation du référentiel IFC (data/ifc_reference.json)."""
from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ifc_reference.json"

LANGUAGES = ("fr", "en", "it", "de")

# Les préfixes "Pset_" et "Qto_" sont réservés aux Property Sets/Quantity Sets
# officiels définis par buildingSMART : un Pset personnalisé ne doit jamais
# les réutiliser, sous peine de collision avec une future définition
# officielle et d'échec de validation IDS. Cf. discussions buildingSMART
# (forums.buildingsmart.org, "Are there rules for Custom Pset naming
# conventions?").
CUSTOM_PSET_GUIDANCE = (
    "Si aucun des Psets officiels ci-dessus ne couvre la propriété recherchée, "
    "créez un Pset personnalisé SANS utiliser les préfixes « Pset_ » ou « Qto_ » "
    "(réservés aux définitions officielles buildingSMART) : leur réutilisation "
    "provoque des collisions et des échecs de validation IDS. Nommez-le plutôt "
    "avec un préfixe propre à votre organisation ou projet, par exemple "
    "« VotreOrg_NomDuPset »."
)


def normalize(text: str) -> str:
    """Minuscule, sans accents, espaces normalisés. Utilisé pour l'indexation
    et la comparaison (les accents ne sont conservés que côté détection de
    langue, cf. language_detect.py)."""
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(text.split())


class IfcReference:
    def __init__(self, raw: dict):
        self.schema_version = raw["schema_version"]
        self.classes = raw["classes"]
        self.by_class = {c["class"]: c for c in self.classes}
        # index[lang][normalized_term] -> list of match dicts
        self.index = {lang: {} for lang in LANGUAGES}
        self._build_index()

    def _add_term(self, lang, term, ifc_class, predefined_type, level, weight):
        norm = normalize(term)
        if not norm:
            return
        self.index[lang].setdefault(norm, []).append({
            "term": term,
            "class": ifc_class,
            "predefined_type": predefined_type,
            "level": level,  # "class" or "predefined_type"
            "weight": weight,
        })

    def _build_index(self):
        for c in self.classes:
            ifc_class = c["class"]
            # nom de la classe elle-même (ex: "IfcWall", "wall")
            self._add_term("en", ifc_class, ifc_class, None, "class_name", 0.9)
            self._add_term("en", ifc_class.replace("Ifc", "", 1), ifc_class, None,
                           "class_name", 0.85)
            for lang in LANGUAGES:
                for term in c.get("class_synonyms", {}).get(lang, []):
                    self._add_term(lang, term, ifc_class, None, "class", 0.85)
            for pdt in c.get("predefined_types", []):
                for lang in LANGUAGES:
                    for term in pdt.get("synonyms", {}).get(lang, []):
                        self._add_term(lang, term, ifc_class, pdt["value"],
                                       "predefined_type", 1.0)

    def all_terms(self, lang: str):
        return self.index.get(lang, {})

    def get_class(self, ifc_class: str):
        return self.by_class.get(ifc_class)


@lru_cache(maxsize=1)
def get_reference() -> IfcReference:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return IfcReference(raw)
