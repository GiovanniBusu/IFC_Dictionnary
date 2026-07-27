# Dictionnaire IFC interactif

Application web permettant à un utilisateur du domaine AEC de saisir le nom
ou la description d'un élément de construction (français, anglais, italien
ou allemand) et d'obtenir la classe IFC recommandée (classe `Ifc...` +
`PredefinedType`), une justification, des alternatives plausibles et la
position hiérarchique dans la classification IFC — jusqu'à IFC4X3.

Interface entièrement en français ; détection automatique de la langue de
saisie.

## Aperçu fonctionnel

- **Recherche** (`/`) : champ unique, détection de langue, suggestion
  principale + alternatives repliables, chacune avec justification,
  position hiérarchique et information de version IFC (nouveauté 4.3,
  dépréciation...).
- **Parcourir** (`/parcourir`) : arborescence complète de la classification
  (catégories → sous-catégories → classes → `PredefinedType`), indépendante
  de la recherche.
- **Fiche détaillée** (`/classe/:ifcClass`) : définition officielle FR/EN,
  liste des `PredefinedType`, position hiérarchique (parent/enfants),
  Property Sets courants, historique de version, synonymes multilingues.

## Architecture

```
data/                     Référentiel IFC (JSON) — jusqu'à IFC4X3_ADD2
scripts/                  Script de génération du référentiel curé
backend/                  API FastAPI (recherche, arborescence, fiches)
  app/data_loader.py        chargement + indexation du référentiel
  app/language_detect.py    détection heuristique de langue (FR/EN/IT/DE)
  app/search.py             scoring, justification, alternatives
  app/tree.py                construction de l'arborescence
  app/main.py                endpoints HTTP
  tests/                     jeu de tests (cas ambigus, API)
frontend/                 Application React (Vite + TypeScript), UI en français
docs/                     Guides (mise à jour des données, plan de tests)
```

Voir aussi [`docs/DATA_UPDATE_GUIDE.md`](docs/DATA_UPDATE_GUIDE.md) (comment
étendre le référentiel à la couverture complète d'IFC4X3 ou à une future
révision) et [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md) (détail des cas de
test ambigus couverts).

### Couverture des données

Le référentiel actuel (`data/ifc_reference.json`, généré par
`scripts/build_reference_data.py`) couvre **54 classes IFC / ~340
PredefinedType**, sélectionnées pour représenter toutes les situations
demandées : structure porteuse, second œuvre/architecture, CVC/plomberie/
électricité, mobilier, accessoires et pièces d'assemblage (`IfcDiscreteAccessory`,
ex. un « corbeau »), éléments spatiaux, et un volet **infrastructure et
ferroviaire** particulièrement développé (nouveautés IFC4.3) :
`IfcAlignment` et `IfcReferent` (tracé en plan et points kilométriques),
`IfcRoad`/`IfcRoadPart` (chaussée, giratoire, passage à niveau...),
`IfcRailway`/`IfcRailwayPart` (voie, zone d'aiguillage, plateforme...),
`IfcBridge`/`IfcBridgePart` (pont à haubans, culée, tablier, pile...),
`IfcTrackElement` (traverse, cœur d'aiguillage, dérailleur...), `IfcSignal`,
`IfcEarthworksCut`/`IfcEarthworksFill` (déblai/remblai), `IfcCourse`
(couche de ballast, de chaussée...), `IfcKerb`, `IfcPavement`, `IfcRail`.
Chaque classe et chaque `PredefinedType` porte des synonymes FR/EN/IT/DE, y
compris du vocabulaire régional suisse (« chape », « corniche »,
« raidisseur »...) et des termes de chantier vulgarisés. Un cas de
dépréciation (`IfcWallStandardCase`, IFC2x3 → IFC4) illustre la traçabilité
de version demandée pour les utilisateurs travaillant encore en IFC2x3
(Revit/cadwork).

Les valeurs `PredefinedType` et leurs définitions ont été vérifiées auprès du
dépôt source buildingSMART/IFC4.3.x-development plutôt que reconstituées de
mémoire (voir l'en-tête de `scripts/build_reference_data.py`).

Quand une requête correspond seulement au nom générique d'une classe (ex.
« wall », « mur »), la suggestion affiche la classe et **la liste complète de
ses PredefinedType** plutôt qu'un type choisi arbitrairement — la recherche
gère aussi les descriptions libres/vulgarisées (chaque mot significatif de la
requête est aussi recherché individuellement).

Ce n'est **pas** l'intégralité du schéma IFC4X3 (~1500 entités) : c'est un
sous-ensemble curé à la main, choisi pour livrer un système complet et
testé plutôt qu'un squelette vide de traductions. Voir le guide de mise à
jour pour l'étendre avec IfcOpenShell.

## Démarrage rapide

### Backend (API)

```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload --port 8000
```

L'API est alors disponible sur `http://localhost:8000` (documentation
interactive sur `http://localhost:8000/docs`).

Tests :

```bash
cd backend
python3 -m pytest tests/ -q
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

L'application est alors disponible sur `http://localhost:5173`.

Build de production :

```bash
npm run build
```

## Endpoints de l'API

| Endpoint | Description |
|---|---|
| `GET /search?q=...&lang=fr\|en\|it\|de` | Suggestion principale + alternatives pour une requête libre. `lang` force la langue (sinon détection automatique). |
| `GET /class/{ifc_class}` | Fiche détaillée d'une classe (ex. `/class/IfcMember`). |
| `GET /tree` | Arborescence complète de classification. |
| `GET /health` | Vérification de service + version du schéma chargé. |

## Exemple de cas d'usage couvert

Requêtes « raidisseur » (FR), « stiffener » (EN), « traversa » (IT) ou
« Aussteifung » (DE) renvoient toutes `IfcMember` avec
`PredefinedType = STIFFENING_RIB`, avec justification en français,
position hiérarchique complète, et — pour le terme allemand, plus
générique — le voile de contreventement (`IfcWall.SHEAR`) signalé comme
alternative plausible selon la discipline.

Une requête très concrète de chantier comme « corbeau » (l'appui d'une dalle
de transition, courant en construction métallique) est reconnue via la table
de synonymes comme `IfcDiscreteAccessory.BRACKET`, sans que l'utilisateur
ait besoin de connaître le nom de la classe IFC.

Voir [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md) pour l'ensemble des cas ambigus
testés (proxy générique vs classe spécifique, structurel vs architectural,
vocabulaire régional suisse).

## Limites connues

- Couverture de données partielle (54/~1500 classes), documentée ci-dessus.
- Le matching flou (`difflib`, sans dépendance externe) peut occasionnellement
  faire remonter un faux positif sur un mot court ; voir
  `docs/DATA_UPDATE_GUIDE.md` section 5.
- Pas de mode hors-ligne empaqueté (PWA/cache local) dans cette version :
  le frontend nécessite une connexion à l'API. Le référentiel JSON étant
  petit (~quelques centaines de Ko), un cache local (service worker) est une
  extension simple pour un usage chantier hors-ligne.
