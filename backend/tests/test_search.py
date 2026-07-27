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
    assert top_class_pdt(result) == ("IfcMember", "STIFFENING_RIB")


def test_stiffener_italian_traversa(reference):
    # "traversa" (IT, raidisseur) est lexicalement très proche du français
    # "traverse" (traverse de voie ferrée, IfcTrackElement.SLEEPER) : une
    # fois le vocabulaire ferroviaire ajouté, ce terme devient une véritable
    # ambiguïté inter-langues plutôt qu'un cas à sens unique. On vérifie que
    # le raidisseur reste bien identifié (suggestion ou alternative), sans
    # exiger qu'il soit toujours la toute première suggestion.
    result = search("traversa", reference=reference)
    ranked = [top_class_pdt(result)] + [(a["class"], a["predefined_type"]) for a in result["alternatives"]]
    assert ("IfcMember", "STIFFENING_RIB") in ranked


def test_stiffener_german_ambiguity_with_shear_wall(reference):
    # "Aussteifung" est un terme allemand générique de contreventement :
    # il doit remonter le raidisseur (IfcMember) en tête, mais signaler le
    # voile de contreventement (IfcWall/SHEAR) comme alternative plausible,
    # conformément à la section 3.2.2 (cas ambigus / disciplines différentes).
    result = search("Aussteifung", reference=reference)
    assert top_class_pdt(result) == ("IfcMember", "STIFFENING_RIB")
    alt_keys = [(a["class"], a["predefined_type"]) for a in result["alternatives"]]
    assert ("IfcWall", "SHEAR") in alt_keys


def test_typo_tolerance_on_stiffener(reference):
    result = search("raidiseur", reference=reference)  # faute de frappe (1 seul "s")
    assert top_class_pdt(result) == ("IfcMember", "STIFFENING_RIB")


# ---------------------------------------------------------------------------
# Vocabulaire régional suisse / termes normatifs
# ---------------------------------------------------------------------------

def test_swiss_chape(reference):
    result = search("chape", reference=reference)
    assert top_class_pdt(result) == ("IfcCovering", "TOPPING")


def test_swiss_corniche_is_molding_not_structural(reference):
    result = search("corniche", reference=reference)
    assert top_class_pdt(result) == ("IfcCovering", "MOLDING")


def test_garde_corps(reference):
    result = search("garde-corps", reference=reference)
    ifc_class, _ = top_class_pdt(result)
    assert ifc_class == "IfcRailing"


def test_corbeau_vulgarized_term_maps_to_discrete_accessory_bracket(reference):
    # "corbeau" est un terme de chantier très concret (appui d'une dalle de
    # transition, très courant en construction métallique) qui ne
    # correspond à aucun nom de classe IFC direct : il doit être reconnu via
    # la table de synonymes comme IfcDiscreteAccessory.BRACKET.
    result = search("corbeau", reference=reference)
    assert top_class_pdt(result) == ("IfcDiscreteAccessory", "BRACKET")


def test_free_form_description_matches_corbel_context(reference):
    # Recherche "vulgarisée" par description libre plutôt que par le terme
    # technique exact : chaque mot significatif de la phrase est aussi
    # recherché individuellement (section 5 du cahier des charges).
    result = search(
        "l'endroit où l'on vient appuyer une dalle de transition en construction métallique",
        reference=reference,
    )
    ranked_classes = [result["suggestion"]["class"]] + [a["class"] for a in result["alternatives"]]
    assert "IfcSlab" in ranked_classes


# ---------------------------------------------------------------------------
# Requête générique sur un nom de classe : lister tous les PredefinedType
# ---------------------------------------------------------------------------

def test_generic_wall_query_lists_all_predefined_types(reference):
    result = search("wall", reference=reference)
    suggestion = result["suggestion"]
    assert suggestion["class"] == "IfcWall"
    assert suggestion["predefined_type"] is None
    values = {p["value"] for p in suggestion["available_predefined_types"]}
    assert {"STANDARD", "SHEAR", "PARAPET", "PARTITIONING", "SOLIDWALL"} <= values
    # Pas de bruit d'autres classes juste par coïncidence lexicale
    # (ex. IfcPlate.CURTAIN_PANEL contient aussi le mot "wall").
    assert all(a["class"] == "IfcWall" for a in result["alternatives"])


def test_generic_french_mur_query_lists_all_predefined_types(reference):
    result = search("mur", reference=reference)
    suggestion = result["suggestion"]
    assert suggestion["class"] == "IfcWall"
    assert suggestion["predefined_type"] is None
    assert len(suggestion["available_predefined_types"]) >= 10


def test_specific_predefined_type_match_has_no_available_types_list(reference):
    # Quand la requête pointe déjà vers un PredefinedType précis, la liste
    # complète n'est pas nécessaire (elle reste consultable sur la fiche
    # détaillée de la classe).
    result = search("raidisseur", reference=reference)
    assert result["suggestion"]["available_predefined_types"] == []


# ---------------------------------------------------------------------------
# Infrastructure et ferroviaire (extension IFC4.3)
# ---------------------------------------------------------------------------

def test_sleeper_traverse_de_voie(reference):
    result = search("traverse de voie", reference=reference)
    assert top_class_pdt(result) == ("IfcTrackElement", "SLEEPER")


def test_ballast_layer(reference):
    result = search("ballast", reference=reference)
    assert top_class_pdt(result) == ("IfcCourse", "BALLASTBED")


def test_frog_coeur_daiguillage(reference):
    result = search("cœur d'aiguillage", reference=reference)
    assert top_class_pdt(result) == ("IfcTrackElement", "FROG")


def test_kilopoint_point_kilometrique(reference):
    result = search("point kilométrique", reference=reference)
    assert top_class_pdt(result) == ("IfcReferent", "KILOPOINT")


def test_bridge_abutment_culee(reference):
    result = search("culée", reference=reference)
    assert top_class_pdt(result) == ("IfcBridgePart", "ABUTMENT")


def test_bridge_type_cable_stayed(reference):
    result = search("pont à haubans", reference=reference)
    assert top_class_pdt(result) == ("IfcBridge", "CABLE_STAYED")


def test_roundabout_giratoire(reference):
    result = search("giratoire", reference=reference)
    assert top_class_pdt(result) == ("IfcRoadPart", "ROUNDABOUT")


def test_railway_crossing_passage_a_niveau(reference):
    result = search("passage à niveau", reference=reference)
    assert top_class_pdt(result) == ("IfcRoadPart", "RAILWAYCROSSING")


def test_earthworks_cut_and_fill(reference):
    assert top_class_pdt(search("déblai", reference=reference)) == ("IfcEarthworksCut", "CUT")
    assert top_class_pdt(search("remblai", reference=reference)) == ("IfcEarthworksFill", "EMBANKMENT")


def test_enrobe_asphalt_layer_vs_flexible_pavement(reference):
    # "Enrobé" n'a pas de classe IFC dédiée ; le terme se classe soit comme
    # couche (IfcCourse.PAVEMENT, dont la définition officielle cite
    # explicitement "Asphalt layers" en exemple) soit, pour la structure de
    # chaussée complète, comme IfcPavement.FLEXIBLE.
    assert top_class_pdt(search("enrobé", reference=reference)) == ("IfcCourse", "PAVEMENT")
    assert top_class_pdt(search("chaussée en enrobé", reference=reference)) == ("IfcPavement", "FLEXIBLE")


def test_rail_guardrail_vs_railing_guardrail_homonym(reference):
    # Homonymie intentionnelle : IfcRail.GUARDRAIL (contre-rail ferroviaire)
    # et IfcRailing.GUARDRAIL (garde-corps de bâtiment) partagent le même mot
    # anglais mais sont deux classes de domaines différents. La requête
    # générique "garde-corps" (FR, bâtiment) ne doit pas remonter le rail.
    result = search("garde-corps", reference=reference)
    assert top_class_pdt(result)[0] == "IfcRailing"


def test_alignment_and_referent_classes_exist(reference):
    assert reference.get_class("IfcAlignment") is not None
    assert reference.get_class("IfcReferent") is not None


def test_infrastructure_spatial_structures_exist(reference):
    for cls in ["IfcRoad", "IfcRoadPart", "IfcRailway", "IfcRailwayPart", "IfcBridge", "IfcBridgePart"]:
        assert reference.get_class(cls) is not None, f"{cls} manquant du référentiel"


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


# ---------------------------------------------------------------------------
# Property Sets et guidance de nommage pour un Pset personnalisé
# ---------------------------------------------------------------------------

def test_search_result_exposes_psets_and_custom_pset_guidance(reference):
    result = search("raidisseur", reference=reference)
    suggestion = result["suggestion"]
    assert "Pset_MemberCommon" in suggestion["psets_common"]
    assert "Pset_" in suggestion["custom_pset_guidance"]
    assert "Qto_" in suggestion["custom_pset_guidance"]


def test_wall_psets_include_quantities_and_reinforcement(reference):
    # Vérifié contre l'export bSDD officiel : IfcWall a plus qu'un seul Pset
    # "Common" (aussi un Qto de quantités et un Pset de renfort de ferraillage).
    entry = reference.get_class("IfcWall")
    assert set(entry["psets_common"]) == {
        "Pset_WallCommon", "Qto_WallBaseQuantities", "Pset_ReinforcementBarPitchOfWall",
    }
