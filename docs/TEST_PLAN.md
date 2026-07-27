# Jeu de tests — cas ambigus et couverture multilingue

Les tests automatisés vivent dans `backend/tests/` (pytest). Ce document
récapitule les cas couverts et pourquoi ils ont été choisis (section 9.5 du
cahier des charges : « cas ambigus connus »).

Exécution :

```bash
cd backend
pip install -r requirements.txt
python3 -m pytest tests/ -q
```

## Cas couverts (`test_search.py`)

| Cas | Test | Ce qu'il vérifie |
|---|---|---|
| Terme structurel multilingue | `test_stiffener_multilingual` | « raidisseur » (FR), « stiffener » (EN), « Aussteifung » (DE) pointent tous vers `IfcMember.STIFFENING_RIB`, avec la bonne langue détectée. |
| Terme italien générique / homonymie inter-langues | `test_stiffener_italian_traversa` | « traversa » (IT, raidisseur) est lexicalement proche du français « traverse » (traverse de voie ferrée) : le raidisseur doit rester identifiable (suggestion ou alternative) sans que ce soit imposé comme unique résultat possible. |
| Ambiguïté structure vs discipline | `test_stiffener_german_ambiguity_with_shear_wall` | « Aussteifung » (DE, terme générique de contreventement) doit renvoyer le raidisseur en suggestion principale mais signaler le voile de contreventement (`IfcWall.SHEAR`) comme alternative plausible — exactement le type de cas ambigu inter-discipline demandé en section 3.2.2. |
| Tolérance aux fautes de frappe | `test_typo_tolerance_on_stiffener` | « raidiseur » (faute d'orthographe) retrouve tout de même `STIFFENING_RIB`. |
| Vocabulaire régional suisse | `test_swiss_chape`, `test_swiss_corniche_is_molding_not_structural` | « chape » → `IfcCovering.TOPPING` ; « corniche » → `IfcCovering.MOLDING` (et non l'homonyme `IfcBeam.CORNICE` de tablier de pont), cas explicitement cité dans le cahier des charges. |
| Garde-corps | `test_garde_corps` | Retrouve bien la famille `IfcRailing`. |
| Terme de chantier vulgarisé | `test_corbeau_vulgarized_term_maps_to_discrete_accessory_bracket` | « corbeau » (appui d'une dalle de transition, courant en construction métallique) est reconnu comme `IfcDiscreteAccessory.BRACKET` sans que l'utilisateur connaisse le nom de la classe IFC. |
| Description libre (recherche « vulgarisée ») | `test_free_form_description_matches_corbel_context` | Une phrase descriptive complète (plutôt qu'un terme exact) fait remonter les classes pertinentes via la recherche par mots significatifs. |
| Requête générique sur un nom de classe | `test_generic_wall_query_lists_all_predefined_types`, `test_generic_french_mur_query_lists_all_predefined_types`, `test_specific_predefined_type_match_has_no_available_types_list` | « wall »/« mur » (nom de classe nu, sans PredefinedType précis) renvoient la classe accompagnée de la liste complète de ses PredefinedType, sans bruit d'autres classes par coïncidence lexicale (ex. `IfcPlate.CURTAIN_PANEL` contient aussi le mot « wall ») ; une requête déjà spécifique n'a pas besoin de cette liste. |
| Proxy générique vs classe spécifique | `test_generic_proxy_term_returns_proxy`, `test_specific_term_outranks_generic_proxy` | Un terme générique (« élément générique ») doit renvoyer `IfcBuildingElementProxy` ; un terme spécifique (« raidisseur ») ne doit jamais faire remonter le proxy dans le top des résultats — le proxy est un repli, pas une distraction. |
| Structurel vs architectural | `test_poutre_is_structural_beam`, `test_beam_vs_member_distinction`, `test_voile_de_contreventement_is_shear_wall` | Vérifie la distinction poutre (`IfcBeam`) / membrure secondaire (`IfcMember`), et qu'un « voile de contreventement » est bien un mur de type `SHEAR`, pas un élément structurel analytique. |
| Traçabilité de version | `test_ifc43_new_class_kerb`, `test_ifc43_new_predefined_type_paving`, `test_deprecated_wall_standard_case_flagged` | Une classe nouvelle en IFC4.3 (`IfcKerb`) et un PredefinedType nouveau en 4.3 (`IfcSlab.PAVING`) sont bien signalés `new_in_43` ; `IfcWallStandardCase` est bien marqué déprécié depuis IFC4 — essentiel pour les utilisateurs travaillant encore en IFC2x3 (Revit/cadwork). |
| Recherche directe par nom de classe | `test_direct_class_name_lookup` | « IfcSlab » (nom de classe brut) doit être reconnu directement. |
| Requêtes vides / non reconnues | `test_empty_query_returns_no_suggestion`, `test_gibberish_query_returns_no_suggestion` | Pas de faux résultat sur une requête vide ou un charabia. |
| Forçage manuel de la langue | `test_forced_language_overrides_detection` | L'utilisateur peut forcer la langue si la détection automatique se trompe (section 6). |
| Vocabulaire ferroviaire et infrastructure | `test_sleeper_traverse_de_voie`, `test_ballast_layer`, `test_frog_coeur_daiguillage`, `test_kilopoint_point_kilometrique`, `test_bridge_abutment_culee`, `test_bridge_type_cable_stayed`, `test_roundabout_giratoire`, `test_railway_crossing_passage_a_niveau`, `test_earthworks_cut_and_fill` | Couvre le vocabulaire de chantier ferroviaire/routier/ouvrages d'art ajouté suite au constat d'un manque de données sur ce domaine : traverse, ballast, cœur d'aiguillage, point kilométrique, culée, pont à haubans, giratoire, passage à niveau, déblai/remblai. |
| Homonymie inter-domaines (rail vs bâtiment) | `test_rail_guardrail_vs_railing_guardrail_homonym` | `IfcRail.GUARDRAIL` (contre-rail ferroviaire anti-déraillement) et `IfcRailing.GUARDRAIL` (garde-corps de bâtiment) partagent le même mot anglais mais sont deux classes de domaines différents ; une requête bâtiment ne doit pas remonter le rail. |
| Présence des classes d'infrastructure | `test_alignment_and_referent_classes_exist`, `test_infrastructure_spatial_structures_exist` | Vérifie que le référentiel contient bien `IfcAlignment`, `IfcReferent`, `IfcRoad(Part)`, `IfcRailway(Part)`, `IfcBridge(Part)`. |

## Cas couverts (`test_api.py`)

Vérifie le contrat HTTP de l'API : `/health`, `/search` (y compris validation
422 sur requête vide ou langue non supportée), `/tree` (structure racine),
`/class/{ifc_class}` (200 + 404 sur classe inconnue).

## Ce qui n'est pas encore couvert (limites assumées)

- Pas de test de performance automatisé pour la contrainte « < 300 ms
  perçus » (section 8) : à valider en conditions réelles une fois déployé,
  le volume de données actuel (54 classes, ~338 PredefinedType) rend la
  recherche largement infra-milliseconde en local.
- Pas de test end-to-end frontend automatisé (Playwright) : la validation a
  été faite manuellement en lançant l'application (voir captures dans le
  README) ; un futur ajout de `@playwright/test` sur les 3 parcours
  (recherche, navigation, fiche détaillée) est recommandé avant mise en
  production.
