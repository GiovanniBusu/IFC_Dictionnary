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
| Terme structurel multilingue | `test_stiffener_multilingual` | « raidisseur » (FR), « stiffener » (EN), « Aussteifung » (DE) pointent tous vers `IfcMember.STIFFENING_MEMBER`, avec la bonne langue détectée. |
| Terme italien générique | `test_stiffener_italian_traversa` | « traversa » (IT, terme plus polysémique) remonte bien le raidisseur en tête malgré une détection de langue incertaine. |
| Ambiguïté structure vs discipline | `test_stiffener_german_ambiguity_with_shear_wall` | « Aussteifung » (DE, terme générique de contreventement) doit renvoyer le raidisseur en suggestion principale mais signaler le voile de contreventement (`IfcWall.SHEAR`) comme alternative plausible — exactement le type de cas ambigu inter-discipline demandé en section 3.2.2. |
| Tolérance aux fautes de frappe | `test_typo_tolerance_on_stiffener` | « raidiseur » (faute d'orthographe) retrouve tout de même `STIFFENING_MEMBER`. |
| Vocabulaire régional suisse | `test_swiss_chape`, `test_swiss_corniche_is_molding_not_structural` | « chape » → `IfcCovering.SCREED` ; « corniche » → `IfcCovering.MOLDING` (et non un élément porteur), cas explicitement cité dans le cahier des charges. |
| Garde-corps | `test_garde_corps` | Retrouve bien la famille `IfcRailing`. |
| Proxy générique vs classe spécifique | `test_generic_proxy_term_returns_proxy`, `test_specific_term_outranks_generic_proxy` | Un terme générique (« élément générique ») doit renvoyer `IfcBuildingElementProxy` ; un terme spécifique (« raidisseur ») ne doit jamais faire remonter le proxy dans le top des résultats — le proxy est un repli, pas une distraction. |
| Structurel vs architectural | `test_poutre_is_structural_beam`, `test_beam_vs_member_distinction`, `test_voile_de_contreventement_is_shear_wall` | Vérifie la distinction poutre (`IfcBeam`) / membrure secondaire (`IfcMember`), et qu'un « voile de contreventement » est bien un mur de type `SHEAR`, pas un élément structurel analytique. |
| Traçabilité de version | `test_ifc43_new_class_kerb`, `test_ifc43_new_predefined_type_paving`, `test_deprecated_wall_standard_case_flagged` | Une classe nouvelle en IFC4.3 (`IfcKerb`) et un PredefinedType nouveau en 4.3 (`IfcSlab.PAVING`) sont bien signalés `new_in_43` ; `IfcWallStandardCase` est bien marqué déprécié depuis IFC4 — essentiel pour les utilisateurs travaillant encore en IFC2x3 (Revit/cadwork). |
| Recherche directe par nom de classe | `test_direct_class_name_lookup` | « IfcSlab » (nom de classe brut) doit être reconnu directement. |
| Requêtes vides / non reconnues | `test_empty_query_returns_no_suggestion`, `test_gibberish_query_returns_no_suggestion` | Pas de faux résultat sur une requête vide ou un charabia. |
| Forçage manuel de la langue | `test_forced_language_overrides_detection` | L'utilisateur peut forcer la langue si la détection automatique se trompe (section 6). |

## Cas couverts (`test_api.py`)

Vérifie le contrat HTTP de l'API : `/health`, `/search` (y compris validation
422 sur requête vide ou langue non supportée), `/tree` (structure racine),
`/class/{ifc_class}` (200 + 404 sur classe inconnue).

## Ce qui n'est pas encore couvert (limites assumées)

- Pas de test de performance automatisé pour la contrainte « < 300 ms
  perçus » (section 8) : à valider en conditions réelles une fois déployé,
  le volume de données actuel (40 classes, ~103 PredefinedType) rend la
  recherche largement infra-milliseconde en local.
- Pas de test end-to-end frontend automatisé (Playwright) : la validation a
  été faite manuellement en lançant l'application (voir captures dans le
  README) ; un futur ajout de `@playwright/test` sur les 3 parcours
  (recherche, navigation, fiche détaillée) est recommandé avant mise en
  production.
