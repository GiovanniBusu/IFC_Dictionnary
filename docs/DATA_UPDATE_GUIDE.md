# Guide de mise à jour du référentiel de données

Ce document explique comment maintenir et étendre `data/ifc_reference.json`
lors d'une future révision du schéma IFC (ex. IFC4.4), et comment passer du
sous-ensemble curé actuel (54 classes / ~340 PredefinedType) à une couverture
exhaustive du schéma.

## 1. État actuel

`data/ifc_reference.json` est généré par `scripts/build_reference_data.py`,
qui contient un référentiel **écrit et curé à la main** : une sélection
représentative de classes couvrant la structure, l'architecture, le CVC/
plomberie/électricité, le mobilier, les éléments spatiaux et le génie civil
(nouveautés IFC4.3), avec traductions et synonymes FR/EN/IT/DE pour chacune.

Ce choix a été fait pour livrer un système complet et testable (recherche,
navigation, fiches détaillées) plutôt qu'un squelette exhaustif mais vide de
traductions. La structure de données est cependant conçue pour être étendue
sans changement d'architecture.

## 2. Étendre à la couverture complète d'IFC4X3 (ou une future version)

Pour couvrir l'intégralité des sous-types de `IfcElement`, `IfcElementType`
et `IfcSpatialElement` (~1500 entités/PredefinedType), la marche à suivre
recommandée (cf. section 4.1 du cahier des charges) :

1. **Générer le squelette structurel avec IfcOpenShell**, qui embarque déjà
   le schéma EXPRESS officiel buildingSMART :

   ```python
   import ifcopenshell
   from ifcopenshell.express import express_parser  # ou ifcopenshell.ifcopenshell_wrapper

   schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4X3_ADD2")
   for decl in schema.declarations():
       # filtrer les sous-types de IfcElement / IfcElementType / IfcSpatialElement
       # et leurs énumérations *TypeEnum associées, puis écrire un squelette
       # JSON équivalent à la structure ci-dessous (sans les champs de
       # traduction, à compléter manuellement).
       ...
   ```

   Objectif : produire pour chaque classe un objet avec `class`, `parent`
   (via `decl.supertype()`), et pour chaque `PredefinedType` correspondant
   les valeurs de l'énumération `Ifc<Class>TypeEnum` (via
   `schema.declaration_by_name(...)`).

2. **Fusionner avec les traductions existantes** : pour toute classe déjà
   présente dans `data/ifc_reference.json`, reprendre `class_fr`,
   `definition_fr`, `class_synonyms`, et pour chaque `PredefinedType` déjà
   documenté, reprendre `description_fr` et `synonyms`. Ne compléter que les
   entrées nouvelles ou manquantes.

3. **Compléter les traductions manquantes** manuellement (ou par relecture
   d'une première traduction automatique) : chaque nouvelle classe doit au
   minimum avoir `definition_fr`, `class_fr`, `category_path` et une entrée
   `class_synonyms.fr` non vide pour être trouvable par la recherche.

4. **Mettre à jour le mapping de versions** (`ifc_versions`,
   `predefined_types[].since`, `deprecated_since`, `new_in_43`) en comparant
   les schémas IFC2x3 / IFC4 / IFC4X3 (disponibles sur
   https://technical.buildingsmart.org). Ceci est nécessaire pour la
   traçabilité des dépréciations/renommages signalée à l'utilisateur.

5. **Régénérer et valider** :

   ```bash
   python3 scripts/build_reference_data.py   # si vous modifiez le script Python
   # ou, si vous éditez le JSON généré par IfcOpenShell directement,
   # valider simplement sa structure :
   python3 -c "import json; json.load(open('data/ifc_reference.json'))"
   cd backend && python3 -m pytest tests/ -q
   ```

## 3. Ajouter un synonyme métier sans toucher au schéma

La table de synonymes est volontairement imbriquée dans chaque entrée de
classe/PredefinedType (`class_synonyms` et `predefined_types[].synonyms`),
et non dans un fichier séparé, pour rester simple à ce volume de données.
Pour ajouter un terme régional ou normatif manquant (ex. un terme SIA/CFC),
il suffit d'ajouter une chaîne dans la liste de langue correspondante — soit
directement dans `data/ifc_reference.json`, soit dans
`scripts/build_reference_data.py` si vous préférez garder le script comme
source de vérité (recommandé, pour conserver un historique Git lisible des
ajouts de synonymes).

**Aucun redémarrage du schéma n'est nécessaire** : le backend charge le JSON
au démarrage (`app/data_loader.py`, avec cache `lru_cache`) et reconstruit
son index de recherche à partir de ce fichier uniquement.

## 4. Ajouter une nouvelle langue

1. Ajouter le code de langue à `LANGUAGES` dans `backend/app/data_loader.py`.
2. Ajouter les listes de stopwords/caractères caractéristiques dans
   `backend/app/language_detect.py` (`STOPWORDS`, `CHAR_HINTS`).
3. Ajouter la clé de langue dans chaque `synonyms`/`class_synonyms` du
   référentiel de données (les entrées existantes sans cette clé sont
   traitées comme une liste vide, aucune migration requise).
4. Ajouter le libellé de langue dans `frontend/src/pages/SearchPage.tsx`
   (`LANGUAGE_LABELS`) et `ClassDetailPage.tsx`.

## 5. Limites connues du sous-ensemble actuel

- Seules 54 classes physiques/spatiales sont couvertes (voir
  `data/ifc_reference.json` pour la liste), sur les ~200+ sous-types
  d'`IfcElement`/`IfcSpatialElement` du schéma complet IFC4X3. Le domaine
  infrastructure/ferroviaire, bien que renforcé (13 classes dédiées), ne
  couvre pas non plus l'intégralité de son propre schéma (ex. le domaine
  portuaire/maritime `IfcMarineFacility`, `IfcMooringDevice`,
  `IfcNavigationElement` n'a pas été ajouté, seulement vérifié comme
  disponible dans le dépôt source — voir section 2 pour l'étendre de la
  même façon).
- Les classes purement analytiques (`IfcStructuralCurveMember`,
  `IfcStructuralSurfaceMember`, etc., utilisées en analyse de structure et
  non en modèle de coordination) ne sont pas couvertes : le référentiel se
  limite au modèle produit (« physical model »), conformément au périmètre
  du cahier des charges (section 4.1).
- Le matching flou (`difflib.SequenceMatcher`) est un choix simple et sans
  dépendance externe, suffisant pour la tolérance aux fautes de frappe et
  aux variantes régionales déjà répertoriées ; il peut occasionnellement
  faire remonter un faux positif sur un mot très court partageant de
  nombreuses lettres (ex. « raidisseur » / « radier »). Une amélioration
  future consisterait à passer à une similarité par embeddings (cf. section
  5.3 du cahier des charges), au prix d'une dépendance supplémentaire et
  d'un besoin de connexion (sauf modèle embarqué).
