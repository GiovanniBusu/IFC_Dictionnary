"""Jeu de tests du moteur de recherche.

Couvre en particulier (section 9.5 du cahier des charges) :
 - le cas d'usage emblématique du raidisseur / stiffener / traversa / Aussteifung
 - les cas ambigus proxy vs classe spécifique
 - les distinctions structurel vs architectural
 - les variantes régionales / vocabulaire suisse (chape, corniche...)
 - la détection de langue sur les 4 langues supportées
 - la traçabilité des versions (nouveauté IFC4.3, dépréciation IFC2x3->IFC4)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.data_loader import get_reference
from app.search import search


@pytest.fixture(scope="module")
def reference():
    return get_reference()


def top_class_pdt(result):
    s = result["suggestion"]
    assert s is not None, f"Aucune suggestion pour la requête {result['query']!r}"
    return s["class"], s["predefined_type"]


# ---------------------------------------------------------------------------
# Cas emblématique multilingue : raidisseur / stiffener / traversa / Aussteifung
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("query,expected_lang", [
    ("raidisseur", "fr"),
    ("stiffener", "en"),
    ("Aussteifung", "de"),
])
def test_stiffener_multilingual(reference, query, expected_lang):
    result = search(query, reference=reference)
    assert result["detected_language"] == expected_lang
    assert top_class_pdt(result) == ("IfcMember", "STIFFENING_MEMBER")


def test_stiffener_italian_traversa(reference):
    # "traversa" est un terme italien plus générique (recoupe aussi
    # "travetto" = solive/IfcBeam.JOIST) : on vérifie seulement que le
    # raidisseur ressort en tête, la langue détectée pouvant être incertaine.
    result = search("traversa", reference=reference)
    assert top_class_pdt(result) == ("IfcMember", "STIFFENING_MEMBER")


def test_stiffener_german_ambiguity_with_shear_wall(reference):
    # "Aussteifung" est un terme allemand générique de contreventement :
    # il doit remonter le raidisseur (IfcMember) en tête, mais signaler le
    # voile de contreventement (IfcWall/SHEAR) comme alternative plausible,
    # conformément à la section 3.2.2 (cas ambigus / disciplines différentes).
    result = search("Aussteifung", reference=reference)
    assert top_class_pdt(result) == ("IfcMember", "STIFFENING_MEMBER")
    alt_keys = [(a["class"], a["predefined_type"]) for a in result["alternatives"]]
    assert ("IfcWall", "SHEAR") in alt_keys


def test_typo_tolerance_on_stiffener(reference):
    result = search("raidiseur", reference=reference)  # faute de frappe (1 seul "s")
    assert top_class_pdt(result) == ("IfcMember", "STIFFENING_MEMBER")


# ---------------------------------------------------------------------------
# Vocabulaire régional suisse / termes normatifs
# ---------------------------------------------------------------------------

def test_swiss_chape(reference):
    result = search("chape", reference=reference)
    assert top_class_pdt(result) == ("IfcCovering", "SCREED")


def test_swiss_corniche_is_molding_not_structural(reference):
    result = search("corniche", reference=reference)
    assert top_class_pdt(result) == ("IfcCovering", "MOLDING")


def test_garde_corps(reference):
    result = search("garde-corps", reference=reference)
    ifc_class, _ = top_class_pdt(result)
    assert ifc_class == "IfcRailing"


# ---------------------------------------------------------------------------
# Ambiguïté proxy vs classe spécifique
# ---------------------------------------------------------------------------

def test_generic_proxy_term_returns_proxy(reference):
    result = search("élément générique", reference=reference)
    assert top_class_pdt(result)[0] == "IfcBuildingElementProxy"


def test_specific_term_outranks_generic_proxy(reference):
    # Un terme très spécifique ("raidisseur") doit scorer strictement plus
    # haut sur sa classe spécifique que sur IfcBuildingElementProxy, qui ne
    # doit même pas apparaître dans les meilleures alternatives.
    result = search("raidisseur", reference=reference)
    ranked_classes = [result["suggestion"]["class"]] + [a["class"] for a in result["alternatives"]]
    assert "IfcBuildingElementProxy" not in ranked_classes


# ---------------------------------------------------------------------------
# Structurel vs architectural (même racine lexicale, disciplines différentes)
# ---------------------------------------------------------------------------

def test_poutre_is_structural_beam(reference):
    result = search("poutre", reference=reference)
    assert top_class_pdt(result)[0] == "IfcBeam"


def test_beam_vs_member_distinction(reference):
    # "panne" (purlin) est un IfcMember, pas un IfcBeam, malgré leur
    # proximité fonctionnelle (les deux supportent une toiture).
    result = search("panne", reference=reference)
    assert top_class_pdt(result) == ("IfcMember", "PURLIN")


def test_voile_de_contreventement_is_shear_wall(reference):
    result = search("voile de contreventement", reference=reference)
    assert top_class_pdt(result) == ("IfcWall", "SHEAR")


# ---------------------------------------------------------------------------
# Traçabilité des versions : nouveauté IFC4.3 / dépréciation
# ---------------------------------------------------------------------------

def test_ifc43_new_class_kerb(reference):
    result = search("bordure de trottoir", reference=reference)
    assert top_class_pdt(result)[0] == "IfcKerb"
    assert result["suggestion"]["version_info"]["min_version"] == "4.3"


def test_ifc43_new_predefined_type_paving(reference):
    result = search("dalle de pavage", reference=reference)
    assert top_class_pdt(result) == ("IfcSlab", "PAVING")
    assert result["suggestion"]["version_info"]["new_in_43"] is True


def test_deprecated_wall_standard_case_flagged(reference):
    entry = reference.get_class("IfcWallStandardCase")
    assert entry["ifc_versions"]["deprecated"] == "4.0"
    assert "déprécié" in entry["notes_fr"].lower() or "Dépréciée" in entry["notes_fr"]


# ---------------------------------------------------------------------------
# Recherche par nom de classe direct
# ---------------------------------------------------------------------------

def test_direct_class_name_lookup(reference):
    result = search("IfcSlab", reference=reference)
    assert top_class_pdt(result)[0] == "IfcSlab"


# ---------------------------------------------------------------------------
# Requête vide / inconnue
# ---------------------------------------------------------------------------

def test_empty_query_returns_no_suggestion(reference):
    result = search("", reference=reference)
    assert result["suggestion"] is None
    assert result["alternatives"] == []


def test_gibberish_query_returns_no_suggestion(reference):
    result = search("xzqwvbkfjpqz", reference=reference)
    assert result["suggestion"] is None


def test_forced_language_overrides_detection(reference):
    result = search("stiffener", forced_language="fr", reference=reference)
    assert result["detected_language"] == "fr"
    assert result["language_confident"] is True
