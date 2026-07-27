#!/usr/bin/env python3
"""
Génère data/ifc_reference.json à partir du référentiel curé ci-dessous.

Ce script correspond à l'étape de constitution MANUELLE du référentiel
(section 9.1 des livrables). Il couvre un sous-ensemble représentatif du
schéma IFC4X3_ADD2 (54 classes / familles), choisi pour illustrer toutes
les situations demandées : structure, architecture, CVC/plomberie/électricité,
mobilier, éléments spatiaux, un volet infrastructure/ferroviaire développé
(alignement, route, voie ferrée, pont, terrassements...), et génie civil
(nouveautés IFC4.3), y compris des cas de dépréciation (IfcWallStandardCase,
IfcWall.STANDARD/POLYGONAL, IfcFooting.CAISSON_FOUNDATION,
IfcSpace.INTERNAL/EXTERNAL) et de renommage/ajout en 4.3.

Les valeurs PredefinedType et leurs définitions anglaises officielles ont
été vérifiées en deux passes :
1. Auprès du dépôt source buildingSMART/IFC4.3.x-development
   (docs/schemas/**/Types/*.md), après qu'une première version de ce fichier
   s'est révélée contenir des valeurs inventées mais plausibles (ex.
   IfcMember.STIFFENING_MEMBER au lieu de la valeur officielle
   STIFFENING_RIB, IfcCovering.SCREED au lieu de TOPPING).
2. Par comparaison systématique avec un export officiel de la buildingSMART
   Data Dictionary (bSDD, dictionnaire IFC 4.3, fourni par l'utilisateur),
   qui a permis de corriger 5 dernières divergences : IfcMember.MEMBER
   (valeur générique manquante), IfcSignal.NON_PHYSICAL_SIGNAL (retiré,
   absent de la version publiée bien que présent dans le dépôt de
   développement), IfcEarthworksFill.SUBGRADEBED (manquant),
   IfcRailwayPart.DILATATIONTRACK -> DILATIONTRACK (orthographe officielle),
   IfcBridgePart.SURFACESTRUCTURE (manquant). Après cette passe, les 54
   classes du référentiel correspondent exactement à bSDD (à l'exception
   d'IfcWallStandardCase, classe historique dépréciée volontairement
   conservée pour la traçabilité IFC2x3, absente du dictionnaire bSDD
   IFC4.3 par construction).

Pour étendre la couverture à l'intégralité du schéma IFC4X3 (toutes les
sous-classes de IfcElement / IfcElementType / IfcSpatialElement, ~1500
entités/PredefinedType), voir docs/DATA_UPDATE_GUIDE.md qui décrit comment
générer automatiquement le squelette avec IfcOpenShell puis fusionner les
traductions/synonymes métier de ce fichier avec le nouveau squelette.
"""
import json
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "ifc_reference.json"

PHYS = "Élément physique"
BLDG = "Élément de bâtiment"
DIST = "Élément de distribution technique"
FURN = "Aménagement intérieur"
CIVIL = "Génie civil et infrastructure"
SPATIAL = "Élément spatial"


def pt(value, since, description_en, description_fr, synonyms,
       deprecated_since=None, new_in_43=False):
    return {
        "value": value,
        "since": since,
        "deprecated_since": deprecated_since,
        "new_in_43": new_in_43,
        "description_en": description_en,
        "description_fr": description_fr,
        "synonyms": {
            "fr": synonyms.get("fr", []),
            "en": synonyms.get("en", []),
            "it": synonyms.get("it", []),
            "de": synonyms.get("de", []),
        },
    }


def entry(ifc_class, class_fr, parent, category_path, versions, definition_en,
          definition_fr, psets_common, class_synonyms, predefined_types,
          notes_fr="", version_notes=""):
    return {
        "class": ifc_class,
        "class_fr": class_fr,
        "parent": parent,
        "category_path": category_path,
        "ifc_versions": versions,
        "definition_en": definition_en,
        "definition_fr": definition_fr,
        "psets_common": psets_common,
        "class_synonyms": {
            "fr": class_synonyms.get("fr", []),
            "en": class_synonyms.get("en", []),
            "it": class_synonyms.get("it", []),
            "de": class_synonyms.get("de", []),
        },
        "predefined_types": predefined_types,
        "notes_fr": notes_fr,
        "version_notes": version_notes,
    }


DATA = []

# ---------------------------------------------------------------------------
# STRUCTURE PORTEUSE
# ---------------------------------------------------------------------------

DATA.append(entry(
    "IfcWall", "Mur", "IfcBuildingElement",
    [PHYS, BLDG, "Murs"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A wall is a vertically-oriented element used to enclose or subdivide "
    "spaces.",
    "Élément vertical utilisé pour enclore ou subdiviser un espace.",
    ["Pset_WallCommon"],
    {"fr": ["mur", "voile", "paroi"], "en": ["wall"], "it": ["muro", "parete"],
     "de": ["Wand"]},
    [
        pt("STANDARD", "4.0", "A standard wall, extruded vertically with a constant thickness.",
           "Mur standard, à section constante extrudée verticalement.",
           {"fr": ["mur standard", "mur droit"], "en": ["standard wall"],
            "it": ["muro standard"], "de": ["Standardwand"]},
           deprecated_since="4.0"),
        pt("SHEAR", "4.0", "A wall designed to withstand shear loads (the name refers to shape, not necessarily to shear resistance).",
           "Mur de contreventement (voile porteur) résistant aux efforts horizontaux.",
           {"fr": ["voile de contreventement", "voile béton", "mur de refend"],
            "en": ["shear wall"], "it": ["muro di controventamento"],
            "de": ["Aussteifungswand", "Schubwand"]}),
        pt("PARAPET", "4.0", "A low protective wall (e.g. at a roof edge or balcony).",
           "Muret de protection en bordure de toiture ou de balcon.",
           {"fr": ["parapet", "muret"], "en": ["parapet wall"], "it": ["parapetto"],
            "de": ["Brüstung"]}),
        pt("PARTITIONING", "4.0", "A non load-bearing dividing wall, often light-weight/sandwich construction.",
           "Cloison de distribution, non porteuse, souvent de construction légère.",
           {"fr": ["cloison"], "en": ["partition wall"], "it": ["parete divisoria"],
            "de": ["Trennwand"]}),
        pt("ELEMENTEDWALL", "4.0", "A wall assembled from prefabricated elements (studs, sheetings, sidings).",
           "Mur composé d'éléments préfabriqués assemblés (ossature, panneaux).",
           {"fr": ["mur élémenté", "mur préfabriqué"], "en": ["elemented wall"],
            "it": ["muro prefabbricato"], "de": ["Elementwand"]}),
        pt("MOVABLE", "4.0", "A movable wall (folding, sliding, or easily removable), often part of the furnishing system.",
           "Mur mobile ou amovible (mur pliant, coulissant), souvent assimilé au mobilier.",
           {"fr": ["mur mobile", "cloison amovible", "paroi mobile"], "en": ["movable wall"],
            "it": ["parete mobile"], "de": ["Mobile Wand"]}),
        pt("PLUMBINGWALL", "4.0", "A pier, enclosure or encasement normally used to enclose plumbing in sanitary rooms.",
           "Gaine ou coffrage technique enfermant la plomberie dans un local sanitaire.",
           {"fr": ["gaine technique sanitaire", "coffrage de plomberie"], "en": ["plumbing wall"],
            "it": ["parete tecnica sanitaria"], "de": ["Installationswand"]}),
        pt("SOLIDWALL", "4.0", "A massive wall construction (single or multi-layer core), often masonry or concrete, load bearing.",
           "Mur massif (maçonnerie ou béton, coulé ou préfabriqué), porteur et coupe-feu.",
           {"fr": ["mur massif", "mur maçonné", "mur en béton"], "en": ["solid wall"],
            "it": ["muro massiccio"], "de": ["Massivwand"]}),
        pt("POLYGONAL", "4.0", "A polygonal wall, extruded vertically, where the wall thickness varies along the path.",
           "Mur polygonal, extrudé verticalement, dont l'épaisseur varie le long du tracé.",
           {"fr": ["mur polygonal"], "en": ["polygonal wall"], "it": ["muro poligonale"],
            "de": ["Polygonale Wand"]}, deprecated_since="4.0"),
        pt("RETAININGWALL", "4.3", "A supporting wall used to protect against soil layers behind it.",
           "Mur de soutènement retenant des terres.",
           {"fr": ["mur de soutènement"], "en": ["retaining wall"], "it": ["muro di sostegno"],
            "de": ["Stützmauer"]}, new_in_43=True),
        pt("WAVEWALL", "4.3", "Protective wall or screen to block overtopping and impact of waves across a breakwater.",
           "Mur brise-lames protégeant contre le franchissement et l'impact des vagues.",
           {"fr": ["mur brise-lames", "écran anti-franchissement"], "en": ["wave wall"],
            "it": ["muro paraonde"], "de": ["Wellenschutzwand"]}, new_in_43=True),
    ],
    notes_fr="Si le mur est un simple habillage sans fonction porteuse ni "
             "cloisonnement (ex. mur rideau autoportant), envisager IfcCurtainWall. "
             "Pour un mur générique modélisé en géométrie brute (proxy), voir "
             "IfcBuildingElementProxy. Le caractère porteur ou non d'un mur n'est "
             "PAS un PredefinedType : il se lit dans la propriété booléenne "
             "LoadBearing du Pset_WallCommon, quel que soit le PredefinedType utilisé. "
             "STANDARD et POLYGONAL sont techniquement dépréciés depuis IFC4 (au profit "
             "d'un IfcMaterialLayerSetUsage) mais restent très largement utilisés en "
             "pratique par la plupart des logiciels (Revit notamment).",
))

DATA.append(entry(
    "IfcWallStandardCase", "Mur (cas standard, historique)", "IfcWall",
    [PHYS, BLDG, "Murs"],
    {"introduced": "2x3", "current": "4.0", "deprecated": "4.0"},
    "Standard case of IfcWall where the wall has a constant thickness "
    "defined by a swept solid, and is represented by an axis and material "
    "layer set.",
    "Cas particulier de mur à épaisseur constante, défini par un axe et un "
    "empilement de couches (utilisé massivement en IFC2x3, notamment par "
    "Revit).",
    ["Pset_WallCommon"],
    {"fr": ["mur standard case", "mur ifc2x3"], "en": ["wall standard case"],
     "it": [], "de": []},
    [
        pt("NOTDEFINED", "2x3", "Undefined predefined type.", "Type non précisé.", {}),
    ],
    notes_fr="Classe historique très fréquente dans les exports Revit/cadwork "
             "en IFC2x3. Dépréciée depuis IFC4 (l'attribut PredefinedType a été "
             "déplacé sur IfcWall lui-même) : à la conversion IFC2x3→IFC4, "
             "remplacer par IfcWall avec PredefinedType='STANDARD'.",
    version_notes="Déprécié en IFC4 au profit de IfcWall.PredefinedType ; "
                  "conservé pour compatibilité ascendante uniquement.",
))

DATA.append(entry(
    "IfcColumn", "Poteau / Colonne", "IfcBuildingElement",
    [PHYS, BLDG, "Ossature verticale"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A vertical structural member which transmits loads from other parts "
    "of the structure to the foundations.",
    "Élément vertical porteur transmettant les charges vers les fondations.",
    ["Pset_ColumnCommon"],
    {"fr": ["poteau", "colonne", "pilier"], "en": ["column", "pillar"],
     "it": ["pilastro", "colonna"], "de": ["Stütze", "Säule"]},
    [
        pt("COLUMN", "4.0", "A usually vertical member that may be load bearing, resisting vertical and sometimes lateral forces.",
           "Poteau standard, généralement vertical, résistant aux efforts verticaux et parfois latéraux.",
           {"fr": ["poteau standard"], "en": ["standard column"],
            "it": ["pilastro standard"], "de": ["Standardstütze"]}),
        pt("PILASTER", "4.0", "A column embedded within a wall, that may be load bearing or purely decorative.",
           "Pilastre engagé dans un mur, porteur ou purement décoratif.",
           {"fr": ["pilastre"], "en": ["pilaster"], "it": ["lesena", "pilastro murato"],
            "de": ["Pilaster", "Wandpfeiler"]}),
        pt("PIERSTEM", "4.3", "An individual vertical part of a pier, may be a simple column or an aggregation of segments and parts.",
           "Fût de pile de pont, simple ou constitué de plusieurs segments/parties.",
           {"fr": ["fût de pile", "fût de pile de pont"], "en": ["pier stem"],
            "it": ["fusto di pila"], "de": ["Pfeilerschaft"]}, new_in_43=True),
        pt("PIERSTEM_SEGMENT", "4.3", "A vertical segment of a pier column.",
           "Tronçon vertical d'un fût de pile.",
           {"fr": ["tronçon de fût de pile"], "en": ["pier stem segment"],
            "it": ["segmento del fusto della pila"], "de": ["Pfeilerschaftsegment"]}, new_in_43=True),
        pt("STANDCOLUMN", "4.3", "A column transmitting vertical loads from a superstructure to an arch below it.",
           "Colonne transmettant les charges verticales d'une superstructure vers un arc porteur.",
           {"fr": ["colonne d'appui d'arche"], "en": ["stand column"],
            "it": ["colonna su arco"], "de": ["Bogenstütze"]}, new_in_43=True),
    ],
    notes_fr="Un poteau purement décoratif en façade (sans fonction porteuse "
             "réelle) reste néanmoins classé IfcColumn si l'intention de "
             "conception est structurelle ; sinon envisager IfcBuildingElementProxy. "
             "PIERSTEM, PIERSTEM_SEGMENT et STANDCOLUMN sont des types spécifiques "
             "aux piles de ponts (ouvrages d'art), ajoutés avec l'extension "
             "infrastructure d'IFC4.3.",
))

DATA.append(entry(
    "IfcBeam", "Poutre", "IfcBuildingElement",
    [PHYS, BLDG, "Ossature horizontale"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A horizontal, or nearly horizontal, structural member that carries "
    "loads primarily by bending.",
    "Élément horizontal (ou quasi) travaillant principalement en flexion.",
    ["Pset_BeamCommon"],
    {"fr": ["poutre", "sommier"], "en": ["beam"], "it": ["trave"], "de": ["Balken", "Träger"]},
    [
        pt("BEAM", "4.0", "A standard beam usually used horizontally.", "Poutre standard.",
           {"fr": ["poutre standard"], "en": ["standard beam"], "it": ["trave standard"],
            "de": ["Standardbalken"]}),
        pt("JOIST", "4.0", "A beam used to support a floor or ceiling.",
           "Solive supportant un plancher ou un plafond.",
           {"fr": ["solive"], "en": ["joist"], "it": ["travetto"], "de": ["Deckenbalken"]}),
        pt("HOLLOWCORE", "4.0", "A wide, often prestressed, beam with a hollow-core profile, usually serving as a slab component.",
           "Poutre large, souvent précontrainte, à profil alvéolé (âme creuse), utilisée aussi comme élément de plancher.",
           {"fr": ["poutre alvéolée", "poutre à âme creuse"], "en": ["hollow-core beam"],
            "it": ["trave alveolare"], "de": ["Hohlkammerbalken"]}),
        pt("LINTEL", "4.0", "A beam spanning an opening (door/window).",
           "Linteau au-dessus d'une baie (porte, fenêtre).",
           {"fr": ["linteau"], "en": ["lintel"], "it": ["architrave"], "de": ["Sturz"]}),
        pt("SPANDREL", "4.0", "A tall beam on the facade of a building, its exterior side finished; can support joists or slab elements.",
           "Poutre-allège en façade, dont la face extérieure est finie, pouvant supporter solives ou dalles.",
           {"fr": ["poutre-allège", "poutre de façade"], "en": ["spandrel beam"],
            "it": ["trave di facciata"], "de": ["Brüstungsträger"]}),
        pt("T_BEAM", "2x3", "A beam forming part of a slab construction and acting together with the slab it carries, often T-shaped.",
           "Poutre solidaire d'une dalle et travaillant avec elle, souvent en forme de T.",
           {"fr": ["poutre en t"], "en": ["T-beam"], "it": ["trave a t"], "de": ["T-Balken"]}),
        pt("GIRDER_SEGMENT", "4.3", "A segment of a girder (e.g. each span of a continuous girder).",
           "Tronçon de poutre maîtresse, notamment pour ouvrages d'art (ponts).",
           {"fr": ["poutre maîtresse", "tronçon de poutre de pont"],
            "en": ["girder segment"], "it": ["segmento di trave principale"],
            "de": ["Trägersegment"]}, new_in_43=True),
        pt("DIAPHRAGM", "4.3", "End portion of a girder transmitting loads to supports, providing moment resistance to the adjoining segment.",
           "Entretoise transversale d'about, raidissant un tablier de pont et transmettant les charges aux appuis.",
           {"fr": ["entretoise de pont"], "en": ["diaphragm beam"],
            "it": ["diaframma trasversale"], "de": ["Querträger"]}, new_in_43=True),
        pt("PIERCAP", "4.3", "A transversal beam on top of a pier.",
           "Chevêtre en tête de pile de pont.",
           {"fr": ["chevêtre de pile"], "en": ["pier cap"], "it": ["testata di pila"],
            "de": ["Pfeilerkopfbalken"]}, new_in_43=True),
        pt("HATSTONE", "4.3", "A beam on top of a retaining wall or wing wall, preventing earth movement.",
           "Chapeau en tête d'un mur de soutènement ou d'un mur en aile, empêchant le mouvement des terres.",
           {"fr": ["chapeau de mur de soutènement"], "en": ["hatstone"], "it": ["cordolo di sommità"],
            "de": ["Mauerkrone"]}, new_in_43=True),
        pt("CORNICE", "4.3", "A non-loadbearing beam on the longitudinal edge of a bridge slab, usually encasing installations.",
           "Corniche de rive de tablier de pont, non porteuse, encastrant souvent des réseaux.",
           {"fr": ["corniche de tablier", "corniche de pont"], "en": ["bridge cornice"],
            "it": ["cornicione del ponte"], "de": ["Brückengesims"]}, new_in_43=True),
        pt("EDGEBEAM", "4.3", "A beam on the longitudinal edge of a bridge slab, usually concrete, providing stiffening and protection.",
           "Poutre de rive de tablier de pont, en béton, assurant raidissage et protection.",
           {"fr": ["poutre de rive de tablier"], "en": ["edge beam"], "it": ["trave di bordo"],
            "de": ["Randbalken"]}, new_in_43=True),
    ],
    notes_fr="Attention à la confusion avec IfcMember : IfcBeam désigne un "
             "élément fléchi principal (structure primaire), IfcMember couvre "
             "les éléments linéaires secondaires (raidisseurs, entretoises "
             "légères, montants). Attention aussi à l'homonymie « corniche » : la "
             "corniche décorative de bâtiment est un IfcCovering (MOLDING), tandis "
             "que la corniche de tablier de pont (non porteuse mais structurelle) "
             "est un IfcBeam (CORNICE) — deux classes différentes pour un même mot "
             "selon le domaine (bâtiment vs ouvrage d'art).",
))

DATA.append(entry(
    "IfcMember", "Membrure / Élément linéaire", "IfcBuildingElement",
    [PHYS, BLDG, "Charpente et éléments linéaires"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A 1-dimensional structural member, often part of a structural frame, "
    "not otherwise classified as beam or column (e.g. brace, purlin, "
    "stiffening rib).",
    "Élément linéaire structurel secondaire, non classé comme poutre ou "
    "poteau (contreventement, panne, raidisseur, montant...).",
    ["Pset_MemberCommon"],
    {"fr": ["membrure", "élément linéaire", "barre"], "en": ["member"],
     "it": ["asta", "elemento lineare"], "de": ["Bauteilstab"]},
    [
        pt("MEMBER", "4.0", "A linear element within a girder or truss with no further meaning.",
           "Élément linéaire générique au sein d'une poutre ou d'une ferme, sans qualification plus précise.",
           {"fr": ["élément linéaire générique"], "en": ["generic member"], "it": ["asta generica"],
            "de": ["Allgemeiner Bauteilstab"]}),
        pt("STIFFENING_RIB", "4.0",
           "Local reinforcement of the flange or web of a girder, added to prevent buckling or increase local stiffness.",
           "Raidissage local de la membrure ou de l'âme d'une poutre, destiné à "
           "empêcher le flambement ou à renforcer localement la rigidité : un raidisseur.",
           {"fr": ["raidisseur", "raidisseur d'âme", "nervure de raidissage"],
            "en": ["stiffener", "stiffening rib"],
            "it": ["irrigidimento", "traversa di irrigidimento", "nervatura di rinforzo"],
            "de": ["Aussteifungsstab", "Steife", "Versteifungsrippe", "Aussteifung"]}),
        pt("BRACE", "4.0", "A linear element (usually sloped) often used for bracing of a girder or truss.",
           "Barre de contreventement diagonal, utilisée pour stabiliser une poutre ou une ferme.",
           {"fr": ["contreventement", "diagonale", "barre de stabilisation"],
            "en": ["brace", "bracing member"], "it": ["controvento", "diagonale"],
            "de": ["Verband", "Diagonalstab"]}),
        pt("CHORD", "4.0", "Upper or lower longitudinal member of a truss, used horizontally or sloped.",
           "Membrure supérieure ou inférieure d'une ferme, horizontale ou inclinée.",
           {"fr": ["membrure de ferme"], "en": ["chord"], "it": ["corrente di capriata"],
            "de": ["Gurt"]}),
        pt("PURLIN", "4.0", "A horizontal member supporting roof cladding between rafters.",
           "Panne supportant la couverture de toiture entre chevrons/fermes.",
           {"fr": ["panne"], "en": ["purlin"], "it": ["arcareccio"], "de": ["Pfette"]}),
        pt("RAFTER", "4.0", "A linear element supporting roof slabs or roof covering, usually sloped.",
           "Chevron ou arbalétrier de charpente de toiture.",
           {"fr": ["chevron", "arbalétrier"], "en": ["rafter"], "it": ["puntone", "corrente"],
            "de": ["Sparren"]}),
        pt("MULLION", "2x3", "A linear element within a curtain wall system to connect two or more panels.",
           "Meneau vertical reliant plusieurs panneaux d'un mur rideau.",
           {"fr": ["meneau"], "en": ["mullion"], "it": ["montante"], "de": ["Pfosten"]}),
        pt("STUD", "4.0", "A vertical light-frame member (e.g. in a stud wall).",
           "Montant vertical d'ossature légère (bois ou métal).",
           {"fr": ["montant d'ossature", "montant"], "en": ["stud"],
            "it": ["montante di parete"], "de": ["Ständer"]}),
        pt("COLLAR", "4.0", "A horizontal member within a roof structure connecting rafters and posts.",
           "Entrait retroussé reliant chevrons et poinçons d'une ferme de toiture.",
           {"fr": ["entrait retroussé"], "en": ["collar tie"], "it": ["catena alta"],
            "de": ["Kehlbalken"]}),
        pt("PLATE", "4.0", "A linear continuous horizontal element in wall framing, such as a head piece or sole plate.",
           "Lisse haute ou basse continue d'une ossature de mur à colombage.",
           {"fr": ["lisse d'ossature"], "en": ["wall plate"], "it": ["corrente di parete"],
            "de": ["Schwelle", "Rähm"]}),
        pt("POST", "4.0", "A linear (usually vertical) member used to support something or mark a point.",
           "Poteau ou montant vertical isolé servant de support ou de repère.",
           {"fr": ["poinçon", "montant vertical"], "en": ["post"], "it": ["montante verticale"],
            "de": ["Pfosten (Stütze)"]}),
        pt("STRUT", "4.0", "A support element within girders/trusses, working mainly in compression.",
           "Barre de contreventement travaillant en compression au sein d'une poutre ou d'une ferme.",
           {"fr": ["étrésillon", "jambe de force"], "en": ["strut"], "it": ["puntello"],
            "de": ["Strebe"]}),
        pt("STRINGER", "4.0", "A sloped support element for a stair or ramp.",
           "Limon d'escalier ou de rampe, incliné, supportant les marches.",
           {"fr": ["limon d'escalier"], "en": ["stringer"], "it": ["cosciale"],
            "de": ["Wangenträger"]}),
        pt("ARCH_SEGMENT", "4.3", "An individual segment of an arch structure.",
           "Segment individuel d'une structure en arc/voûte (pont en arc).",
           {"fr": ["segment d'arc", "segment de voûte"], "en": ["arch segment"],
            "it": ["segmento d'arco"], "de": ["Bogensegment"]}, new_in_43=True),
        pt("STRUCTURALCABLE", "4.3", "A linear cable element used to secure or stabilise a structure by resisting loads through tension only.",
           "Câble structurel résistant uniquement en traction, utilisé pour stabiliser une structure.",
           {"fr": ["câble structurel"], "en": ["structural cable"], "it": ["cavo strutturale"],
            "de": ["Tragseil"]}, new_in_43=True),
        pt("SUSPENSION_CABLE", "4.3", "A steel wire suspended element (e.g. main cable of a suspension bridge).",
           "Câble porteur principal d'un pont suspendu.",
           {"fr": ["câble porteur de pont suspendu"], "en": ["suspension cable"],
            "it": ["cavo di sospensione"], "de": ["Tragkabel"]}, new_in_43=True),
        pt("SUSPENDER", "4.3", "A vertical suspension element hanging from a suspension cable or arch.",
           "Suspente verticale reliant le tablier au câble porteur (pont suspendu).",
           {"fr": ["suspente"], "en": ["suspender"], "it": ["pendino"],
            "de": ["Hänger"]}, new_in_43=True),
        pt("STAY_CABLE", "4.3", "A sloped cable suspending the deck from a pylon (cable-stayed bridge).",
           "Hauban reliant le tablier au pylône d'un pont à haubans.",
           {"fr": ["hauban"], "en": ["stay cable"], "it": ["stralli"],
            "de": ["Schrägseil"]}, new_in_43=True),
        pt("TIEBAR", "4.3", "A linear bar element used to secure a structure by resisting loads through tension and/or compression.",
           "Tirant reprenant des efforts de traction et/ou de compression pour stabiliser une structure.",
           {"fr": ["tirant"], "en": ["tie bar"], "it": ["tirante"],
            "de": ["Zugstab"]}, new_in_43=True),
    ],
    notes_fr="Cas ambigu fréquent : un « raidisseur » modélisé sans détail de "
             "profilé réel (juste une boîte englobante) est parfois classé "
             "IfcBuildingElementProxy par les logiciels de charpente métallique. "
             "Si l'analyse structurelle est le but, préférer IfcMember + "
             "STIFFENING_RIB, qui porte l'information sémantique correcte. Une "
             "plaque de raidissage plane (et non une barre) relève plutôt "
             "d'IfcPlate (STIFFENER_PLATE).",
))

DATA.append(entry(
    "IfcSlab", "Dalle / Plancher", "IfcBuildingElement",
    [PHYS, BLDG, "Dallage"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A slab is a component of the construction that covers a horizontal "
    "area, e.g. floor, roof or landing slab.",
    "Élément couvrant une surface horizontale : plancher, toiture-terrasse, "
    "palier, radier...",
    ["Pset_SlabCommon"],
    {"fr": ["dalle", "plancher"], "en": ["slab"], "it": ["soletta", "solaio"],
     "de": ["Platte", "Decke"]},
    [
        pt("FLOOR", "2x3", "The slab is used to represent a floor slab or a bridge deck.",
           "Dalle de plancher courant, ou tablier de pont.",
           {"fr": ["dalle de plancher", "plancher"], "en": ["floor slab"],
            "it": ["solaio di piano"], "de": ["Geschossdecke"]}),
        pt("ROOF", "2x3", "The slab is used to represent a roof slab (flat or sloped).",
           "Dalle de toiture, plate ou en pente.",
           {"fr": ["dalle de toiture", "toiture-terrasse"], "en": ["roof slab"],
            "it": ["soletta di copertura"], "de": ["Dachplatte"]}),
        pt("LANDING", "2x3", "The slab is used to represent a landing within a stair or ramp.",
           "Palier de circulation entre volées d'escalier ou de rampe.",
           {"fr": ["palier"], "en": ["landing slab"], "it": ["pianerottolo"],
            "de": ["Podest"]}),
        pt("BASESLAB", "2x3", "The slab represents a floor slab against the ground, part of the foundation (mat foundation).",
           "Radier ou dalle sur terre-plein en contact avec le sol.",
           {"fr": ["radier", "dalle sur sol", "dalle de fondation"],
            "en": ["base slab", "mat foundation"], "it": ["platea di fondazione"],
            "de": ["Bodenplatte"]}),
        pt("APPROACH_SLAB", "4.3", "A slab used to provide a transition from an embankment to a bridge.",
           "Dalle de transition assurant la jonction entre un remblai et un pont.",
           {"fr": ["dalle de transition"], "en": ["approach slab"], "it": ["soletta di transizione"],
            "de": ["Übergangsplatte"]}, new_in_43=True),
        pt("PAVING", "4.3", "A rigid pavement course of a road or other paved area, usually concrete.",
           "Dalle de revêtement rigide d'une chaussée ou d'une aire pavée.",
           {"fr": ["dalle de pavage", "dallage extérieur"], "en": ["paving slab"],
            "it": ["lastra di pavimentazione"], "de": ["Pflasterplatte"]}, new_in_43=True),
        pt("WEARING", "4.3", "The slab is used to represent a wearing surface.",
           "Dalle de roulement (couche d'usure) d'une chaussée ou d'un tablier.",
           {"fr": ["dalle de roulement", "couche d'usure"], "en": ["wearing slab"],
            "it": ["strato di usura"], "de": ["Verschleißschicht"]}, new_in_43=True),
        pt("SIDEWALK", "4.3", "The slab is used to represent a sidewalk.",
           "Dalle de trottoir.",
           {"fr": ["dalle de trottoir", "trottoir"], "en": ["sidewalk slab"],
            "it": ["marciapiede"], "de": ["Gehwegplatte"]}, new_in_43=True),
        pt("TRACKSLAB", "4.3", "A reinforced or prestressed concrete slab that is a main element of a slab track (railway).",
           "Dalle de voie ferrée (béton armé ou précontraint), élément principal d'une voie sur dalle.",
           {"fr": ["dalle de voie ferrée", "dalle béton de voie"], "en": ["track slab"],
            "it": ["soletta armata (binario)"], "de": ["Gleistragplatte"]}, new_in_43=True),
    ],
    notes_fr="Une chape mince rapportée sur une dalle structurelle n'est pas "
             "une IfcSlab mais un IfcCovering (PredefinedType=TOPPING).",
))

DATA.append(entry(
    "IfcFooting", "Semelle de fondation", "IfcBuildingElement",
    [PHYS, BLDG, "Fondations"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A footing, also called spread footing, isolated footing or "
    "pad footing, is a part of, usually, a shallow foundation.",
    "Élément de fondation superficielle transmettant les charges au sol.",
    ["Pset_FootingCommon"],
    {"fr": ["semelle", "fondation superficielle"], "en": ["footing"],
     "it": ["fondazione", "plinto"], "de": ["Fundament"]},
    [
        pt("PAD_FOOTING", "4.0", "An element that transfers the load of a single column (possibly two) to the ground.",
           "Semelle isolée sous poteau.",
           {"fr": ["semelle isolée", "plot de fondation"], "en": ["pad footing"],
            "it": ["plinto isolato"], "de": ["Einzelfundament"]}),
        pt("STRIP_FOOTING", "4.0", "A linear element transferring loads into the ground from a continuous element (wall) or series of elements (columns).",
           "Semelle filante sous mur ou sous une série de poteaux.",
           {"fr": ["semelle filante"], "en": ["strip footing"], "it": ["fondazione a nastro"],
            "de": ["Streifenfundament"]}),
        pt("PILE_CAP", "4.0", "An element that transfers the load from a column (or group) to a pier or pile (or group).",
           "Semelle de répartition sur pieu ou groupe de pieux.",
           {"fr": ["semelle sur pieux"], "en": ["pile cap"], "it": ["plinto su pali"],
            "de": ["Pfahlkopfplatte"]}),
        pt("FOOTING_BEAM", "4.0", "Footing elements in bending, supported clear of the ground, normally spanning between piers, piles or pile caps.",
           "Poutre de fondation (longrine) travaillant en flexion, portée entre pieux ou semelles.",
           {"fr": ["longrine", "poutre de fondation"], "en": ["footing beam", "grade beam"],
            "it": ["trave di fondazione"], "de": ["Fundamentbalken"]}),
        pt("CAISSON_FOUNDATION", "4.0", "A foundation construction type used in underwater construction.",
           "Fondation par caisson, utilisée en construction immergée.",
           {"fr": ["fondation par caisson"], "en": ["caisson foundation"], "it": ["fondazione a cassone"],
            "de": ["Kastenfundament"]}, deprecated_since="4.2"),
    ],
    notes_fr="CAISSON_FOUNDATION est déprécié depuis IFC4.2 au profit de la "
             "classe dédiée IfcCaissonFoundation (non couverte par ce "
             "référentiel curé, voir docs/DATA_UPDATE_GUIDE.md pour l'étendre).",
))

DATA.append(entry(
    "IfcPile", "Pieu", "IfcBuildingElement",
    [PHYS, BLDG, "Fondations"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A slender timber, concrete, or steel structural element driven, "
    "drilled or otherwise embedded into the ground for use as a foundation.",
    "Élément élancé (bois, béton, acier) foncé ou foré dans le sol pour "
    "servir de fondation profonde.",
    ["Pset_PileCommon"],
    {"fr": ["pieu"], "en": ["pile"], "it": ["palo di fondazione"], "de": ["Pfahl"]},
    [
        pt("BORED", "4.0", "A pile installed by drilling/boring.", "Pieu foré.",
           {"fr": ["pieu foré"], "en": ["bored pile"], "it": ["palo trivellato"],
            "de": ["Bohrpfahl"]}),
        pt("DRIVEN", "4.0", "A pile installed by driving (hammering, vibrating).", "Pieu battu, vibré ou foncé.",
           {"fr": ["pieu battu"], "en": ["driven pile"], "it": ["palo battuto"],
            "de": ["Rammpfahl"]}),
        pt("JETGROUTING", "4.0", "An injected pile-like construction.", "Pieu réalisé par injection (jet grouting).",
           {"fr": ["pieu par injection", "jet grouting"], "en": ["jet grouting pile"],
            "it": ["palo mediante jet grouting"], "de": ["Düsenstrahlpfahl"]}),
        pt("COHESION", "2x3", "A cohesion pile.", "Pieu travaillant par cohésion du sol.",
           {"fr": ["pieu par cohésion"], "en": ["cohesion pile"], "it": ["palo per coesione"],
            "de": ["Kohäsionspfahl"]}),
        pt("FRICTION", "2x3", "A friction pile.", "Pieu travaillant par frottement latéral.",
           {"fr": ["pieu par frottement"], "en": ["friction pile"], "it": ["palo per attrito"],
            "de": ["Reibungspfahl"]}),
        pt("SUPPORT", "2x3", "A support pile.", "Pieu de soutien ou d'appui.",
           {"fr": ["pieu de soutien"], "en": ["support pile"], "it": ["palo di sostegno"],
            "de": ["Stützpfahl"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcPlate", "Platine / Plaque", "IfcBuildingElement",
    [PHYS, BLDG, "Éléments plans structurels"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A plate is a planar and often flat part with constant thickness.",
    "Élément plan, souvent plat et de faible épaisseur constante.",
    ["Pset_PlateCommon"],
    {"fr": ["platine", "plaque"], "en": ["plate"], "it": ["piastra"], "de": ["Platte"]},
    [
        pt("CURTAIN_PANEL", "2x3", "A planar element within a curtain wall, often a frame with fixed glazing.",
           "Panneau de remplissage d'un mur rideau, souvent vitré.",
           {"fr": ["panneau de mur rideau"], "en": ["curtain wall panel"],
            "it": ["pannello di facciata continua"], "de": ["Fassadenpaneel"]}),
        pt("SHEET", "2x3", "A planar, flat and thin element, usually metal sheet, often an additional part within an assembly.",
           "Plaque mince et plane, souvent une tôle, utilisée comme pièce complémentaire d'un assemblage.",
           {"fr": ["tôle", "plaque mince"], "en": ["metal sheet"],
            "it": ["lamiera"], "de": ["Blech"]}),
        pt("FLANGE_PLATE", "4.3", "A flange plate in linear members with a box or I-profile (e.g. top or bottom flange of a box girder).",
           "Plaque de membrure (semelle) d'un profilé en caisson ou en I, ex. poutre-caisson de pont.",
           {"fr": ["plaque de membrure", "semelle de poutre-caisson"], "en": ["flange plate"],
            "it": ["piastra d'ala"], "de": ["Flanschblech"]}, new_in_43=True),
        pt("WEB_PLATE", "4.3", "A plate connecting flange plates in linear members with a box or I-profile.",
           "Plaque d'âme reliant les membrures d'un profilé en caisson ou en I.",
           {"fr": ["plaque d'âme"], "en": ["web plate"], "it": ["piastra d'anima"],
            "de": ["Stegblech"]}, new_in_43=True),
        pt("STIFFENER_PLATE", "4.3", "A transversal plate added to a flange or web plate for local stiffening.",
           "Plaque raidisseuse transversale, rapportée sur une membrure ou une âme pour un raidissage local.",
           {"fr": ["plaque raidisseuse", "raidisseur plan"], "en": ["stiffener plate"],
            "it": ["piastra di irrigidimento"], "de": ["Steifenblech"]}, new_in_43=True),
        pt("GUSSET_PLATE", "4.3", "A plate or bracket for strengthening an angle in framework (building or bridge).",
           "Gousset : plaque d'assemblage renforçant un angle dans une charpente métallique.",
           {"fr": ["gousset", "plaque d'assemblage"], "en": ["gusset plate"],
            "it": ["piastra di collegamento"], "de": ["Knotenblech"]}, new_in_43=True),
        pt("COVER_PLATE", "4.3", "A plate (underneath or above) a flange to provide additional load capacity.",
           "Couvre-joint : plaque de renfort posée sur une membrure pour augmenter sa capacité.",
           {"fr": ["couvre-joint"], "en": ["cover plate"], "it": ["piastra di copertura"],
            "de": ["Deckblech"]}, new_in_43=True),
        pt("SPLICE_PLATE", "4.3", "A plate connecting two members joined at their ends.",
           "Plaque d'éclissage reliant deux éléments assemblés bout à bout.",
           {"fr": ["éclisse", "plaque d'éclissage"], "en": ["splice plate"], "it": ["piastra di giunzione"],
            "de": ["Laschenblech"]}, new_in_43=True),
        pt("BASE_PLATE", "4.3", "A plate used to spread load over a surface, such as underneath a bearing or column.",
           "Platine de répartition d'appui, ex. platine de pied de poteau.",
           {"fr": ["platine de pied de poteau", "platine d'appui"], "en": ["base plate"],
            "it": ["piastra di base"], "de": ["Fußplatte"]}, new_in_43=True),
    ],
    notes_fr="STIFFENER_PLATE désigne un raidissage sous forme de plaque plane ; "
             "un raidisseur en forme de barre linéaire relève plutôt d'IfcMember "
             "(STIFFENING_RIB).",
))

DATA.append(entry(
    "IfcRoof", "Toiture (ouvrage de charpente)", "IfcBuildingElement",
    [PHYS, BLDG, "Toiture"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "The roof is the covering of the top part of a building, acting as "
    "an aggregate container for all functional parts that make up the roof.",
    "Ouvrage de couverture d'un bâtiment, agrégeant l'ensemble des éléments "
    "qui composent la toiture (souvent un conteneur regroupant dalles, "
    "membrures, couverture...).",
    ["Pset_RoofCommon"],
    {"fr": ["toiture", "toit"], "en": ["roof"], "it": ["tetto", "copertura"],
     "de": ["Dach"]},
    [
        pt("FLAT_ROOF", "2x3", "A roof having no slope, or only a slight pitch, to drain rainwater.",
           "Toiture plate ou à très faible pente, permettant l'écoulement des eaux.",
           {"fr": ["toiture plate", "toit plat"], "en": ["flat roof"],
            "it": ["tetto piano"], "de": ["Flachdach"]}),
        pt("SHED_ROOF", "2x3", "A roof having a single slope.", "Toiture à un seul pan (appentis).",
           {"fr": ["toit en appentis", "monopente"], "en": ["shed roof", "lean-to roof"],
            "it": ["tetto a una falda"], "de": ["Pultdach"]}),
        pt("GABLE_ROOF", "2x3", "A roof sloping downward in two parts from a central ridge, forming a gable at each end.",
           "Toiture à deux pans (pignon), avec faîtage central.",
           {"fr": ["toit à deux pans", "toiture à pignon"], "en": ["gable roof"],
            "it": ["tetto a due falde"], "de": ["Satteldach"]}),
        pt("HIP_ROOF", "2x3", "A roof having sloping ends and sides meeting at an inclined projecting angle.",
           "Toiture à quatre pans (croupe).",
           {"fr": ["toit à quatre pans", "toiture en croupe"], "en": ["hip roof"],
            "it": ["tetto a padiglione"], "de": ["Walmdach"]}),
        pt("HIPPED_GABLE_ROOF", "2x3", "A roof having a hipped end truncating a gable.",
           "Toiture à pignon tronqué par une croupe partielle.",
           {"fr": ["toit à croupe partielle"], "en": ["hipped gable roof"],
            "it": ["tetto a padiglione troncato"], "de": ["Krüppelwalmdach"]}),
        pt("GAMBREL_ROOF", "2x3", "A roof sloping downward in two parts from a central ridge, forming a gable at each end (barn-style double slope).",
           "Toiture à deux pans brisés par versant (type grange américaine, comble à la Mansart sur pignon).",
           {"fr": ["toiture à deux pans brisés"], "en": ["gambrel roof"],
            "it": ["tetto a capanna spezzato"], "de": ["Kriegersparrendach"]}),
        pt("MANSARD_ROOF", "2x3", "A roof having on each side a steeper lower part and a shallower upper part.",
           "Toiture à la Mansart, avec un brisis (pente forte) et un terrasson (pente faible).",
           {"fr": ["toit à la mansart", "toiture mansardée"], "en": ["mansard roof"],
            "it": ["tetto alla mansarda"], "de": ["Mansarddach"]}),
        pt("BARREL_ROOF", "2x3", "A roof or ceiling having a semicylindrical form.",
           "Toiture en berceau, de forme semi-cylindrique.",
           {"fr": ["toiture en berceau"], "en": ["barrel roof"], "it": ["tetto a botte"],
            "de": ["Tonnendach"]}),
        pt("RAINBOW_ROOF", "2x3", "A gable roof in the form of a broad Gothic arch, with gently sloping convex surfaces.",
           "Toiture en arc surbaissé, en forme d'arc gothique aplati.",
           {"fr": ["toiture en arc surbaissé"], "en": ["rainbow roof"], "it": ["tetto ad arco ribassato"],
            "de": ["Bogendach"]}),
        pt("BUTTERFLY_ROOF", "2x3", "A roof having two slopes, each descending inward from the eaves.",
           "Toiture papillon, à deux pans descendant vers l'intérieur.",
           {"fr": ["toiture papillon"], "en": ["butterfly roof"], "it": ["tetto a farfalla"],
            "de": ["Schmetterlingsdach"]}),
        pt("PAVILION_ROOF", "2x3", "A pyramidal hip roof.", "Toiture pyramidale (en pavillon).",
           {"fr": ["toiture en pavillon"], "en": ["pavilion roof"], "it": ["tetto a padiglione piramidale"],
            "de": ["Zeltdach"]}),
        pt("DOME_ROOF", "2x3", "A hemispherical hip roof.", "Toiture en dôme hémisphérique.",
           {"fr": ["toiture en dôme"], "en": ["dome roof"], "it": ["tetto a cupola"],
            "de": ["Kuppeldach"]}),
        pt("FREEFORM", "2x3", "Free form roof, not falling into the basic shapes above.",
           "Toiture de forme libre, ne correspondant à aucune forme de base.",
           {"fr": ["toiture de forme libre"], "en": ["freeform roof"], "it": ["tetto di forma libera"],
            "de": ["Freiformdach"]}),
    ],
    notes_fr="IfcRoof sert souvent de conteneur logique ; les surfaces de "
             "couverture proprement dites peuvent être modélisées comme "
             "IfcSlab (ROOF) et/ou IfcCovering (ROOFING).",
))

DATA.append(entry(
    "IfcReinforcingBar", "Armature (barre)", "IfcElementComponent",
    [PHYS, BLDG, "Armatures et précontrainte"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "Steel reinforcing bar, typically used to reinforce concrete, classified "
    "by the role/purpose it fulfills.",
    "Barre d'acier utilisée pour armer le béton, classée selon son rôle.",
    ["Pset_ReinforcingBarCommon"],
    {"fr": ["armature", "fer à béton", "barre d'armature"], "en": ["rebar", "reinforcing bar"],
     "it": ["armatura", "ferro d'armatura"], "de": ["Bewehrungsstab"]},
    [
        pt("MAIN", "2x3", "The reinforcing bar is a main bar.", "Armature principale longitudinale.",
           {"fr": ["armature principale"], "en": ["main bar"], "it": ["armatura principale"],
            "de": ["Hauptbewehrung"]}),
        pt("LIGATURE", "2x3", "The reinforcing bar is a ligature (link, stirrup).",
           "Cadre ou étrier reliant les armatures principales (armature transversale).",
           {"fr": ["étrier", "cadre d'armature"], "en": ["stirrup", "ligature"], "it": ["staffa"],
            "de": ["Bügel"]}),
        pt("SHEAR", "2x3", "The reinforcing bar is a shear bar.",
           "Armature d'effort tranchant.",
           {"fr": ["armature d'effort tranchant"], "en": ["shear reinforcement"],
            "it": ["armatura a taglio"], "de": ["Schubbewehrung"]}),
        pt("ANCHORING", "4.0", "Anchoring reinforcement.", "Armature d'ancrage.",
           {"fr": ["armature d'ancrage"], "en": ["anchoring bar"], "it": ["armatura di ancoraggio"],
            "de": ["Verankerungsbewehrung"]}),
        pt("EDGE", "2x3", "Edge reinforcement.", "Armature de rive/bord.",
           {"fr": ["armature de rive"], "en": ["edge reinforcement"], "it": ["armatura di bordo"],
            "de": ["Randbewehrung"]}),
        pt("RING", "2x3", "Ring reinforcement.", "Armature annulaire (en anneau).",
           {"fr": ["armature annulaire"], "en": ["ring reinforcement"], "it": ["armatura ad anello"],
            "de": ["Ringbewehrung"]}),
        pt("PUNCHING", "2x3", "Punching reinforcement.", "Armature de poinçonnement.",
           {"fr": ["armature de poinçonnement"], "en": ["punching reinforcement"],
            "it": ["armatura a punzonamento"], "de": ["Durchstanzbewehrung"]}),
        pt("STUD", "2x3", "The reinforcing bar is a stud.", "Goujon d'armature (connecteur).",
           {"fr": ["goujon d'armature"], "en": ["stud"], "it": ["piolo di armatura"],
            "de": ["Bewehrungsdübel"]}),
        pt("SPACEBAR", "2x3", "A stirrup in a pre-stressing system to position the tendon conduit.",
           "Barre d'écartement positionnant la gaine de précontrainte.",
           {"fr": ["barre d'écartement"], "en": ["spacer bar"], "it": ["barra distanziatrice"],
            "de": ["Abstandsbügel"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcReinforcingMesh", "Treillis d'armature", "IfcElementComponent",
    [PHYS, BLDG, "Armatures et précontrainte"],
    {"introduced": "4.0", "current": "4.3", "deprecated": None},
    "A reinforcing mesh (welded fabric) used to reinforce concrete. The "
    "enumeration currently defines no specific mesh types.",
    "Treillis soudé utilisé pour armer le béton. Aucun type spécifique n'est "
    "actuellement défini dans le schéma (uniquement USERDEFINED/NOTDEFINED).",
    ["Pset_ReinforcingMeshCommon"],
    {"fr": ["treillis soudé", "panneau de treillis"], "en": ["reinforcing mesh", "welded fabric"],
     "it": ["rete elettrosaldata"], "de": ["Bewehrungsmatte"]},
    [pt("NOTDEFINED", "4.0", "Undefined.", "Non précisé.", {})],
    notes_fr="",
))

DATA.append(entry(
    "IfcTendon", "Câble de précontrainte", "IfcElementComponent",
    [PHYS, BLDG, "Armatures et précontrainte"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A tendon that is used for pre-tensioning or post-tensioning of a "
    "structural member.",
    "Câble ou barre utilisé pour la précontrainte (pré- ou post-tension) "
    "d'un élément structurel.",
    ["Pset_TendonCommon"],
    {"fr": ["câble de précontrainte", "torons"], "en": ["tendon"],
     "it": ["cavo di precompressione"], "de": ["Spannglied"]},
    [
        pt("STRAND", "2x3", "The tendon is a strand.", "Câble constitué de torons.",
           {"fr": ["toron"], "en": ["strand"], "it": ["trefolo"], "de": ["Litze"]}),
        pt("BAR", "2x3", "The tendon is configured as a bar.", "Barre de précontrainte pleine.",
           {"fr": ["barre de précontrainte"], "en": ["tendon bar"], "it": ["barra di precompressione"],
            "de": ["Spannstab"]}),
        pt("WIRE", "2x3", "The tendon is a wire.", "Fil de précontrainte.",
           {"fr": ["fil de précontrainte"], "en": ["prestressing wire"], "it": ["filo di precompressione"],
            "de": ["Spanndraht"]}),
        pt("COATED", "2x3", "The tendon is coated.", "Câble de précontrainte gainé/enrobé.",
           {"fr": ["câble gainé"], "en": ["coated tendon"], "it": ["cavo rivestito"],
            "de": ["Ummanteltes Spannglied"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcRailing", "Garde-corps", "IfcBuildingElement",
    [PHYS, BLDG, "Garde-corps et gardes-fous"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A railing is a frame or barrier of vertical and horizontal members "
    "acting as protection against falling or as a guide.",
    "Ouvrage de protection contre les chutes ou de guidage, constitué de "
    "montants et de lisses (horizontales/verticales).",
    ["Pset_RailingCommon"],
    {"fr": ["garde-corps", "garde-fou", "rambarde"], "en": ["railing", "guard rail"],
     "it": ["ringhiera", "parapetto"], "de": ["Geländer"]},
    [
        pt("HANDRAIL", "2x3", "A railing serving as an optional structural support at hand height, adjacent to ramps and stairs.",
           "Main courante, support facultatif à hauteur de main, le long des rampes et escaliers.",
           {"fr": ["main courante"], "en": ["handrail"], "it": ["corrimano"],
            "de": ["Handlauf"]}),
        pt("GUARDRAIL", "2x3", "A railing guarding occupants from falling off a stair, ramp, or landing, or restraining vehicles.",
           "Garde-corps de protection contre les chutes, ou glissière retenant les véhicules.",
           {"fr": ["garde-corps de sécurité", "barrière de protection"],
            "en": ["guardrail"], "it": ["parapetto di sicurezza"], "de": ["Absturzsicherung"]}),
        pt("BALUSTRADE", "2x3", "A guardrail located at the edge of a floor rather than a stair or ramp (roof-tops, balconies, bridges).",
           "Garde-corps de rez ou de plancher (toit-terrasse, balcon, pont), plutôt qu'escalier/rampe.",
           {"fr": ["balustrade"], "en": ["balustrade"], "it": ["balaustra"], "de": ["Balustrade"]}),
        pt("FENCE", "2x3", "A non-load bearing, usually lightweight vertical construction that bounds or subdivides an external area.",
           "Clôture : construction verticale non porteuse, généralement légère, délimitant un espace extérieur.",
           {"fr": ["clôture"], "en": ["fence"], "it": ["recinzione"], "de": ["Zaun"]}),
    ],
    notes_fr="Le raidisseur d'un garde-corps préfabriqué (renfort de montant) "
             "relève lui d'IfcMember (STIFFENING_RIB), pas d'IfcRailing.",
))

# ---------------------------------------------------------------------------
# CIRCULATIONS
# ---------------------------------------------------------------------------

DATA.append(entry(
    "IfcStair", "Escalier", "IfcBuildingElement",
    [PHYS, BLDG, "Circulations verticales"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A vertical passageway allowing occupants to walk (step) from one "
    "floor level to another, often an aggregation of stair flights and "
    "landings, distinguished by number of flights/landings and turn type.",
    "Ouvrage de circulation verticale permettant de passer d'un niveau à "
    "l'autre, souvent une agrégation de volées et paliers, distingué par le "
    "nombre de volées/paliers et le type de virage.",
    ["Pset_StairCommon"],
    {"fr": ["escalier"], "en": ["stair", "staircase"], "it": ["scala"],
     "de": ["Treppe"]},
    [
        pt("STRAIGHT_RUN_STAIR", "2x3", "A stair extending from one level to another without turns or winders, one straight flight.",
           "Escalier droit, à volée unique, sans virage.",
           {"fr": ["escalier droit"], "en": ["straight stair"], "it": ["scala rettilinea"],
            "de": ["Gerade Treppe"]}),
        pt("TWO_STRAIGHT_RUN_STAIR", "2x3", "A straight stair consisting of two straight flights without turns but with one landing.",
           "Escalier à deux volées droites sans virage, avec un palier intermédiaire.",
           {"fr": ["escalier à deux volées"], "en": ["dog-leg stair"],
            "it": ["scala a due rampe"], "de": ["Zweiläufige Treppe"]}),
        pt("QUARTER_WINDING_STAIR", "2x3", "A stair consisting of one flight with a quarter winder, making a 90° turn.",
           "Escalier à un quart tournant balancé (virage à 90° sans palier).",
           {"fr": ["escalier à quart tournant balancé"], "en": ["quarter winding stair"],
            "it": ["scala a quarto di giro con gradini a ventaglio"], "de": ["Viertelgewendelte Treppe"]}),
        pt("QUARTER_TURN_STAIR", "2x3", "A stair making a 90° turn, two straight flights connected by a quarterspace landing.",
           "Escalier à quart tournant avec palier (virage à 90° via un palier).",
           {"fr": ["escalier à quart tournant avec palier"], "en": ["quarter turn stair"],
            "it": ["scala a quarto di giro con pianerottolo"], "de": ["Viertelgewendelte Treppe mit Podest"]}),
        pt("HALF_WINDING_STAIR", "2x3", "A stair consisting of one flight with a half winder, making a 180° turn.",
           "Escalier balancé à demi-tour (virage à 180° sans palier).",
           {"fr": ["escalier balancé à demi-tour"], "en": ["half winding stair"],
            "it": ["scala a mezzo giro con gradini a ventaglio"], "de": ["Halbgewendelte Treppe"]}),
        pt("HALF_TURN_STAIR", "2x3", "A stair making a 180° turn, two straight flights connected by a halfspace landing.",
           "Escalier à demi-tour avec palier (virage à 180° via un palier).",
           {"fr": ["escalier à demi-tour avec palier"], "en": ["half turn stair"],
            "it": ["scala a mezzo giro con pianerottolo"], "de": ["Halbgewendelte Treppe mit Podest"]}),
        pt("TWO_QUARTER_WINDING_STAIR", "2x3", "A stair consisting of one flight with two quarter winders, making a 180° turn overall.",
           "Escalier balancé à deux quarts tournants (virage total à 180° sans palier).",
           {"fr": ["escalier balancé à deux quarts tournants"], "en": ["two quarter winding stair"],
            "it": [], "de": []}),
        pt("TWO_QUARTER_TURN_STAIR", "2x3", "A stair making a 180° turn, three straight flights connected by two quarterspace landings.",
           "Escalier à deux quarts tournants avec paliers (virage total à 180°).",
           {"fr": ["escalier à deux quarts tournants avec paliers"], "en": ["two quarter turn stair"],
            "it": [], "de": []}),
        pt("THREE_QUARTER_WINDING_STAIR", "2x3", "A stair consisting of one flight with three quarter winders, making a 270° turn overall.",
           "Escalier balancé à trois quarts tournants (virage total à 270° sans palier).",
           {"fr": ["escalier balancé à trois quarts tournants"], "en": ["three quarter winding stair"],
            "it": [], "de": []}),
        pt("THREE_QUARTER_TURN_STAIR", "2x3", "A stair making a 270° turn, four straight flights connected by three quarterspace landings.",
           "Escalier à trois quarts tournants avec paliers (virage total à 270°).",
           {"fr": ["escalier à trois quarts tournants avec paliers"], "en": ["three quarter turn stair"],
            "it": [], "de": []}),
        pt("SPIRAL_STAIR", "2x3", "A stair constructed with winders around a circular newel, often without landings.",
           "Escalier hélicoïdal (colimaçon) autour d'un noyau central.",
           {"fr": ["escalier en colimaçon", "escalier hélicoïdal"], "en": ["spiral stair"],
            "it": ["scala a chiocciola"], "de": ["Spindeltreppe", "Wendeltreppe"]}),
        pt("DOUBLE_RETURN_STAIR", "2x3", "A stair with one straight flight to a wide quarterspace landing, then two side flights in opposite directions.",
           "Escalier « à l'impériale » : une volée montant à un large palier, puis deux volées symétriques opposées.",
           {"fr": ["escalier à l'impériale"], "en": ["double return stair", "imperial stair"],
            "it": ["scala imperiale"], "de": ["Kaiserliche Treppe"]}),
        pt("CURVED_RUN_STAIR", "2x3", "A stair extending from one level to another without turns, consisting of one curved flight.",
           "Escalier courbe à volée unique, sans virage franc.",
           {"fr": ["escalier courbe"], "en": ["curved stair"], "it": ["scala curva"],
            "de": ["Gebogene Treppe"]}),
        pt("TWO_CURVED_RUN_STAIR", "2x3", "A curved stair consisting of two curved flights without turns but with one landing.",
           "Escalier courbe à deux volées avec un palier intermédiaire.",
           {"fr": ["escalier courbe à deux volées"], "en": ["two curved run stair"],
            "it": [], "de": []}),
        pt("LADDER", "2x3", "A piece of equipment consisting of a series of bars or steps between two upright elements, used for climbing.",
           "Échelle, constituée de barreaux entre deux montants, pour monter ou descendre.",
           {"fr": ["échelle"], "en": ["ladder"], "it": ["scala a pioli"], "de": ["Leiter"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcStairFlight", "Volée d'escalier", "IfcBuildingElement",
    [PHYS, BLDG, "Circulations verticales"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A part of a stair without a turn or change in direction, consisting "
    "of steps, classified by the shape of its walking line.",
    "Partie rectiligne (ou non) d'un escalier, sans changement brusque de "
    "direction, classée selon la forme de sa ligne de foulée.",
    ["Pset_StairFlightCommon"],
    {"fr": ["volée d'escalier", "volée"], "en": ["stair flight"], "it": ["rampa di scala"],
     "de": ["Treppenlauf"]},
    [
        pt("STRAIGHT", "4.0", "A stair flight with a straight walking line.", "Volée droite, à ligne de foulée rectiligne.",
           {"fr": ["volée droite"], "en": ["straight flight"], "it": ["rampa rettilinea"],
            "de": ["Gerader Treppenlauf"]}),
        pt("WINDER", "4.0", "A stair flight with a walking line including straight and curved sections.",
           "Volée balancée, combinant sections rectilignes et courbes.",
           {"fr": ["volée balancée"], "en": ["winder flight"], "it": ["rampa a gradini a ventaglio"],
            "de": ["Gewendelter Treppenlauf"]}),
        pt("SPIRAL", "4.0", "A stair flight with a circular or elliptic walking line.",
           "Volée hélicoïdale, à ligne de foulée circulaire ou elliptique.",
           {"fr": ["volée hélicoïdale"], "en": ["spiral flight"], "it": ["rampa elicoidale"],
            "de": ["Spindelläufer"]}),
        pt("CURVED", "4.0", "A stair flight with a curved walking line.", "Volée courbe.",
           {"fr": ["volée courbe"], "en": ["curved flight"], "it": ["rampa curva"],
            "de": ["Gebogener Treppenlauf"]}),
        pt("FREEFORM", "4.0", "A stair flight with a free form walking line and outer boundaries.",
           "Volée de forme libre.",
           {"fr": ["volée de forme libre"], "en": ["freeform flight"], "it": ["rampa di forma libera"],
            "de": ["Freiform-Treppenlauf"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcRamp", "Rampe", "IfcBuildingElement",
    [PHYS, BLDG, "Circulations verticales"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A vertical passageway which provides a means of moving between "
    "different levels using a sloped surface (aggregation of ramp flights), "
    "distinguished by number of flights/landings and turn type.",
    "Ouvrage de circulation verticale à plan incliné (accès PMR, véhicules...), "
    "distingué par le nombre de volées/paliers et le type de virage.",
    ["Pset_RampCommon"],
    {"fr": ["rampe d'accès", "rampe"], "en": ["ramp"], "it": ["rampa"], "de": ["Rampe"]},
    [
        pt("STRAIGHT_RUN_RAMP", "2x3", "A ramp connecting two levels, consisting of one straight flight without turns or winders.",
           "Rampe droite à volée unique, sans virage.",
           {"fr": ["rampe droite"], "en": ["straight ramp"], "it": ["rampa rettilinea"],
            "de": ["Gerade Rampe"]}),
        pt("TWO_STRAIGHT_RUN_RAMP", "2x3", "A straight ramp consisting of two straight flights without turns but with one landing.",
           "Rampe droite à deux volées avec un palier intermédiaire.",
           {"fr": ["rampe à deux volées"], "en": ["two straight run ramp"],
            "it": [], "de": []}),
        pt("QUARTER_TURN_RAMP", "2x3", "A ramp making a 90° turn, two straight flights connected by a quarterspace landing.",
           "Rampe à quart tournant avec palier (virage à 90°).",
           {"fr": ["rampe à quart tournant"], "en": ["quarter turn ramp"], "it": [], "de": []}),
        pt("TWO_QUARTER_TURN_RAMP", "2x3", "A ramp making a 180° turn, three straight flights connected by two quarterspace landings.",
           "Rampe à deux quarts tournants avec paliers (virage total à 180°).",
           {"fr": ["rampe à deux quarts tournants"], "en": ["two quarter turn ramp"], "it": [], "de": []}),
        pt("HALF_TURN_RAMP", "2x3", "A ramp making a 180° turn, two straight flights connected by a halfspace landing.",
           "Rampe à demi-tour avec palier (virage à 180°).",
           {"fr": ["rampe à demi-tour"], "en": ["half turn ramp"], "it": [], "de": []}),
        pt("SPIRAL_RAMP", "2x3", "A ramp constructed around a circular or elliptical well, without newels and landings.",
           "Rampe hélicoïdale, sans palier.",
           {"fr": ["rampe hélicoïdale"], "en": ["spiral ramp"], "it": ["rampa elicoidale"],
            "de": ["Wendelrampe"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcRampFlight", "Volée de rampe", "IfcBuildingElement",
    [PHYS, BLDG, "Circulations verticales"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A part of a ramp without a turn, forming a single sloped plane, "
    "classified by the shape of its walking line.",
    "Partie d'une rampe sans virage, formant un seul plan incliné.",
    ["Pset_RampFlightCommon"],
    {"fr": ["volée de rampe"], "en": ["ramp flight"], "it": ["rampa lineare"],
     "de": ["Rampenlauf"]},
    [
        pt("STRAIGHT", "4.0", "A ramp flight with a straight walking line.", "Volée de rampe droite.",
           {"fr": ["volée de rampe droite"], "en": ["straight ramp flight"], "it": ["rampa lineare rettilinea"],
            "de": ["Gerader Rampenlauf"]}),
        pt("SPIRAL", "4.0", "A ramp flight with a circular or elliptic walking line.",
           "Volée de rampe hélicoïdale.",
           {"fr": ["volée de rampe hélicoïdale"], "en": ["spiral ramp flight"], "it": ["rampa elicoidale"],
            "de": ["Spindelrampenlauf"]}),
    ],
    notes_fr="",
))

# ---------------------------------------------------------------------------
# ENVELOPPE / SECOND ŒUVRE
# ---------------------------------------------------------------------------

DATA.append(entry(
    "IfcCurtainWall", "Mur rideau", "IfcBuildingElement",
    [PHYS, BLDG, "Baies et façades"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A curtain wall is an exterior wall which is non load-bearing and "
    "carries only its own weight, supported by an auxiliary framework.",
    "Paroi extérieure non porteuse, autoportante, suspendue à une "
    "ossature auxiliaire (montants/traverses).",
    ["Pset_CurtainWallCommon"],
    {"fr": ["mur rideau", "façade rideau"], "en": ["curtain wall"], "it": ["facciata continua"],
     "de": ["Vorhangfassade"]},
    [pt("NOTDEFINED", "2x3", "Undefined.", "Non précisé.", {})],
    notes_fr="Aucun PredefinedType spécifique n'est actuellement défini pour "
             "IfcCurtainWall dans le schéma officiel (seulement USERDEFINED/"
             "NOTDEFINED, réservé pour de futures extensions). Les meneaux/"
             "traverses de mur rideau sont modélisés en IfcMember (MULLION), "
             "les panneaux en IfcPlate (CURTAIN_PANEL).",
))

DATA.append(entry(
    "IfcDoor", "Porte", "IfcBuildingElement",
    [PHYS, BLDG, "Baies et façades"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A door is a building element that is predominately used to provide "
    "controlled access for people, goods, animals and vehicles.",
    "Élément de bâtiment permettant un accès contrôlé (personnes, biens, "
    "véhicules) à travers une baie.",
    ["Pset_DoorCommon"],
    {"fr": ["porte"], "en": ["door"], "it": ["porta"], "de": ["Tür"]},
    [
        pt("DOOR", "4.0", "A standard door within a wall opening, as a curtain wall panel, or free standing.",
           "Porte standard, dans une baie, en panneau de mur rideau, ou autoportante.",
           {"fr": ["porte standard"], "en": ["standard door"], "it": ["porta standard"],
            "de": ["Standardtür"]}),
        pt("GATE", "4.0", "A point of entry into a space, usually within an opening in a fence, or free standing.",
           "Portail : point d'accès, généralement dans une clôture, ou autoportant.",
           {"fr": ["portail"], "en": ["gate"], "it": ["cancello"], "de": ["Tor"]}),
        pt("TRAPDOOR", "4.0", "A special door lying horizontally in a slab opening, often for accessing a cellar or attic.",
           "Trappe horizontale dans une dalle, pour accéder à une cave ou des combles.",
           {"fr": ["trappe"], "en": ["trapdoor", "hatch"], "it": ["botola"], "de": ["Falltür"]}),
        pt("BOOM_BARRIER", "4.3", "A bar or pole pivoted to block vehicular or pedestrian access through a controlled point.",
           "Barrière levante (bras articulé) bloquant un point d'accès contrôlé.",
           {"fr": ["barrière levante"], "en": ["boom gate"], "it": ["sbarra"], "de": ["Schranke"]},
           new_in_43=True),
        pt("TURNSTILE", "4.3", "A mechanical gate with revolving arms, allowing only one person at a time to pass.",
           "Tourniquet mécanique à bras tournants, filtrant le passage une personne à la fois.",
           {"fr": ["tourniquet"], "en": ["turnstile"], "it": ["tornello"], "de": ["Drehkreuz"]},
           new_in_43=True),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcWindow", "Fenêtre", "IfcBuildingElement",
    [PHYS, BLDG, "Baies et façades"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A window is a building element that is predominately used to "
    "provide natural light and fresh air, and is often glazed.",
    "Élément de bâtiment assurant l'éclairage naturel et/ou la ventilation, "
    "généralement vitré.",
    ["Pset_WindowCommon"],
    {"fr": ["fenêtre", "châssis vitré"], "en": ["window"], "it": ["finestra"],
     "de": ["Fenster"]},
    [
        pt("WINDOW", "4.0", "A standard window within a wall opening, as a curtain wall panel, or free standing.",
           "Fenêtre standard, dans une baie, en panneau de mur rideau, ou autoportante.",
           {"fr": ["fenêtre standard"], "en": ["standard window"], "it": ["finestra standard"],
            "de": ["Standardfenster"]}),
        pt("SKYLIGHT", "4.0", "A window within a sloped building element, usually a roof slab.",
           "Fenêtre de toit (velux), posée dans un élément incliné, généralement une dalle de toiture.",
           {"fr": ["fenêtre de toit", "velux"], "en": ["skylight"], "it": ["lucernario"],
            "de": ["Dachfenster"]}),
        pt("LIGHTDOME", "4.0", "A special window lying horizontally in a roof slab opening.",
           "Dôme (coupole) d'éclairage zénithal, horizontal, dans une ouverture de toiture.",
           {"fr": ["coupole zénithale", "dôme d'éclairage"], "en": ["roof light dome"],
            "it": ["cupola di illuminazione"], "de": ["Lichtkuppel"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcCovering", "Revêtement / Finition", "IfcBuildingElement",
    [PHYS, BLDG, "Revêtements et finitions"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A covering is an element applied to another element (or spatial "
    "element) to cover its surface (e.g. finish for floor, wall, ceiling, "
    "roof, or insulation, coping, etc.).",
    "Élément appliqué en surface d'un autre élément ou d'un espace : "
    "revêtement de sol, mur, plafond, toiture, isolation, chape...",
    ["Pset_CoveringCommon"],
    {"fr": ["revêtement", "finition"], "en": ["covering", "finish"], "it": ["rivestimento"],
     "de": ["Bekleidung"]},
    [
        pt("TOPPING", "2x3", "A layer of material used for leveling or flattening a surface.",
           "Couche mince rapportée pour niveler ou finir une surface : une chape.",
           {"fr": ["chape", "chape de ragréage", "chape flottante"], "en": ["topping", "screed"],
            "it": ["massetto"], "de": ["Estrich"]}),
        pt("MOLDING", "4.0", "A molding, a strip of material covering the transition of surfaces (often between wall cladding and ceiling).",
           "Profil décoratif rapporté couvrant la transition entre surfaces, ex. corniche décorative.",
           {"fr": ["corniche", "moulure décorative"], "en": ["molding", "cornice"],
            "it": ["cornice decorativa", "modanatura"], "de": ["Gesims", "Zierleiste"]}),
        pt("SKIRTINGBOARD", "4.0", "A skirting board, a strip of material covering the transition between wall cladding and flooring.",
           "Plinthe couvrant la transition entre le revêtement mural et le sol.",
           {"fr": ["plinthe"], "en": ["skirting board", "baseboard"], "it": ["battiscopa"],
            "de": ["Sockelleiste"]}),
        pt("CLADDING", "2x3", "A cladding.", "Bardage ou habillage de façade.",
           {"fr": ["bardage", "habillage de façade"], "en": ["cladding"], "it": ["rivestimento di facciata"],
            "de": ["Verkleidung"]}),
        pt("FLOORING", "2x3", "A flooring.", "Revêtement de sol (carrelage, parquet...).",
           {"fr": ["revêtement de sol", "carrelage", "parquet"], "en": ["flooring"],
            "it": ["pavimentazione"], "de": ["Bodenbelag"]}),
        pt("CEILING", "2x3", "A ceiling.", "Faux-plafond ou plafond fini.",
           {"fr": ["faux-plafond", "plafond"], "en": ["ceiling"], "it": ["controsoffitto"],
            "de": ["Decke", "Abhangdecke"]}),
        pt("ROOFING", "2x3", "A roof covering.", "Étanchéité ou couverture de toiture.",
           {"fr": ["étanchéité de toiture", "couverture"], "en": ["roofing"],
            "it": ["manto di copertura"], "de": ["Dachdeckung"]}),
        pt("INSULATION", "2x3", "Insulation of an element for thermal or acoustic purposes.",
           "Couche d'isolation thermique ou acoustique.",
           {"fr": ["isolation", "isolant"], "en": ["insulation"], "it": ["isolamento"],
            "de": ["Dämmung"]}),
        pt("MEMBRANE", "2x3", "An impervious layer (roof covering underlay, damp proof course, or waterproofing on a bridge structure).",
           "Membrane d'étanchéité (sous-couche de toiture, pare-vapeur, ou étanchéité de tablier de pont).",
           {"fr": ["membrane d'étanchéité", "pare-vapeur"], "en": ["membrane"], "it": ["membrana impermeabilizzante"],
            "de": ["Abdichtungsbahn"]}),
        pt("SLEEVING", "2x3", "A covering used to isolate a distribution element from the space it is contained in.",
           "Gainage isolant un élément de distribution technique de l'espace qui le contient.",
           {"fr": ["gainage"], "en": ["sleeving"], "it": ["guaina di isolamento"],
            "de": ["Ummantelung"]}),
        pt("WRAPPING", "2x3", "Wrapping, particularly of distribution elements, using tape.",
           "Enrubannage, notamment d'éléments de distribution technique.",
           {"fr": ["enrubannage"], "en": ["wrapping"], "it": ["avvolgimento"],
            "de": ["Umwicklung"]}),
        pt("COPING", "2x3", "A protective capping or covering of a wall or parapet.",
           "Couvertine posée en tête de mur ou d'acrotère.",
           {"fr": ["couvertine"], "en": ["coping"], "it": ["copertina"], "de": ["Mauerabdeckung"]}),
    ],
    notes_fr="« Corniche » est ambigu : moulure décorative rapportée en bâtiment → "
             "IfcCovering(MOLDING) ; corniche non porteuse de tablier de pont → "
             "plutôt IfcBeam(CORNICE) (ajout IFC4.3, domaine ouvrages d'art). "
             "TOPPING a remplacé l'ancienne dénomination officieuse « SCREED » : "
             "c'est la valeur correcte pour une chape.",
))

DATA.append(entry(
    "IfcBuildingElementProxy", "Élément générique (proxy)", "IfcBuildingElement",
    [PHYS, BLDG, "Élément générique / non classé"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A proxy definition that provides a fallback for building elements "
    "that have no equivalent, more specific, semantic definition in the "
    "specification.",
    "Définition de repli pour un élément de bâtiment qui n'a pas "
    "d'équivalent sémantique plus spécifique dans le schéma IFC.",
    [],
    {"fr": ["élément générique", "proxy", "élément non typé"],
     "en": ["generic element", "proxy"], "it": ["elemento generico"],
     "de": ["generisches Bauteil"]},
    [pt("USERDEFINED", "2x3", "A user-defined proxy type.", "Type défini par l'utilisateur.", {}),
     pt("NOTDEFINED", "2x3", "Undefined.", "Non précisé.", {})],
    notes_fr="À utiliser en dernier recours : si un élément ressemble à un "
             "raidisseur, un garde-corps ou un équipement mais que le logiciel "
             "source n'exporte qu'une géométrie brute sans sémantique, il "
             "atterrit souvent ici. Un contrôle qualité IDS doit signaler un "
             "usage excessif de BuildingElementProxy comme un défaut de "
             "modélisation à corriger si une classe plus spécifique existe.",
))

DATA.append(entry(
    "IfcChimney", "Cheminée", "IfcBuildingElement",
    [PHYS, BLDG, "Éléments de superstructure"],
    {"introduced": "4.0", "current": "4.3", "deprecated": None},
    "A vertical, hollow substructure to convey exhaust gases to the "
    "outer air. The enumeration currently defines no specific chimney types.",
    "Ouvrage vertical creux évacuant les gaz de combustion vers "
    "l'extérieur. Aucun type spécifique n'est actuellement défini dans le "
    "schéma (uniquement USERDEFINED/NOTDEFINED).",
    ["Pset_ChimneyCommon"],
    {"fr": ["cheminée", "conduit de fumée"], "en": ["chimney", "flue"], "it": ["camino"],
     "de": ["Schornstein", "Kamin"]},
    [pt("NOTDEFINED", "4.0", "Undefined.", "Non précisé.", {})],
    notes_fr="",
))

DATA.append(entry(
    "IfcShadingDevice", "Protection solaire", "IfcBuildingElement",
    [PHYS, BLDG, "Protections solaires"],
    {"introduced": "4.0", "current": "4.3", "deprecated": None},
    "A device attached to a building or free standing which provides "
    "solar shading, e.g. a jalousie, shutter or awning.",
    "Dispositif rapporté ou autonome assurant une protection solaire "
    "(jalousie, volet, auvent).",
    ["Pset_ShadingDeviceCommon"],
    {"fr": ["protection solaire", "brise-soleil"], "en": ["shading device"],
     "it": ["schermatura solare"], "de": ["Sonnenschutz"]},
    [
        pt("JALOUSIE", "4.0", "A blind with adjustable horizontal slats for admitting light and air while excluding direct sun and rain.",
           "Jalousie à lames horizontales orientables, laissant passer air et lumière tout en filtrant soleil et pluie.",
           {"fr": ["jalousie", "brise-soleil à lames"], "en": ["jalousie", "venetian blind"], "it": ["gelosia"],
            "de": ["Jalousie"]}),
        pt("SHUTTER", "4.0", "A mechanical device limiting the passage of light, often a solid or louvered movable cover for a window.",
           "Volet, dispositif mobile (plein ou à lames) limitant le passage de la lumière devant une fenêtre.",
           {"fr": ["volet", "volet roulant"], "en": ["shutter"], "it": ["persiana", "tapparella"],
            "de": ["Fensterladen", "Rollladen"]}),
        pt("AWNING", "4.0", "A rooflike shelter of canvas or other material extending over a doorway, window, or deck for protection from sun/rain.",
           "Auvent ou store banne en toile, protégeant une baie, une terrasse ou un accès du soleil et de la pluie.",
           {"fr": ["auvent", "store banne"], "en": ["awning"], "it": ["tenda da sole"],
            "de": ["Markise"]}),
    ],
    notes_fr="",
))

# ---------------------------------------------------------------------------
# ACCESSOIRES ET PIÈCES D'ASSEMBLAGE
# ---------------------------------------------------------------------------

DATA.append(entry(
    "IfcDiscreteAccessory", "Accessoire discret / pièce d'assemblage", "IfcElementComponent",
    [PHYS, BLDG, "Accessoires et pièces d'assemblage"],
    {"introduced": "4.0", "current": "4.3", "deprecated": None},
    "A discrete accessory is a small, purpose-made object connecting, "
    "supporting or otherwise interfacing between two or more other "
    "elements, such as a bracket, anchor plate, or shoe.",
    "Petit accessoire connectant, supportant ou faisant l'interface entre "
    "plusieurs éléments : corbeau, platine d'ancrage, sabot d'about, etc.",
    ["Pset_DiscreteAccessoryCommon"],
    {"fr": ["accessoire", "pièce d'assemblage", "pièce de fixation"],
     "en": ["discrete accessory"], "it": ["accessorio discreto"], "de": ["Zubehörteil"]},
    [
        pt("BRACKET", "4.0", "An L-shaped or similarly shaped accessory attached in a corner between elements to hold them together or carry a secondary element.",
           "Corbeau ou console en équerre, fixé à la jonction de deux éléments pour les "
           "solidariser ou porter un élément secondaire — ex. appui d'une dalle de "
           "transition, très courant en construction métallique.",
           {"fr": ["corbeau", "console", "corbeau de support", "console d'appui"],
            "en": ["bracket", "corbel"],
            "it": ["mensola", "beccatello", "mensola di supporto"],
            "de": ["Konsole", "Kragstein", "Kragarm"]}),
        pt("ANCHORPLATE", "4.0", "A steel plate with shear studs or welded-on rebar, embedded into a concrete element so other elements can later be welded/bolted onto it.",
           "Platine d'acier noyée dans le béton (avec connecteurs ou armature soudée), "
           "permettant de souder ou boulonner un élément ultérieurement.",
           {"fr": ["platine d'ancrage", "platine noyée"], "en": ["anchor plate"],
            "it": ["piastra d'ancoraggio"], "de": ["Ankerplatte"]}),
        pt("SHOE", "4.0", "A column shoe or beam shoe (hanger) used to support or secure an element.",
           "Sabot de poteau ou d'about de poutre (étrier suspendu), utilisé pour supporter ou fixer un élément.",
           {"fr": ["sabot d'about", "sabot de poteau", "étrier de poutre"], "en": ["column shoe", "beam shoe", "beam hanger"],
            "it": ["scarpa di appoggio"], "de": ["Stützenschuh", "Trägerschuh"]}),
        pt("EXPANSION_JOINT_DEVICE", "4.0", "Assembly connection element between construction elements allowing for thermal differential expansion.",
           "Joint de dilatation entre éléments de construction, absorbant les dilatations thermiques différentielles.",
           {"fr": ["joint de dilatation", "joint de chaussée"], "en": ["expansion joint"],
            "it": ["giunto di dilatazione"], "de": ["Dehnfuge"]}),
        pt("FILLER", "4.0", "Sealant, gap filler rod, packing material or other used to close a gap.",
           "Mastic, cordon de calfeutrement ou autre matériau utilisé pour combler un joint.",
           {"fr": ["joint de remplissage", "mastic de joint"], "en": ["gap filler"],
            "it": ["sigillante"], "de": ["Fugenfüller"]}),
        pt("FLASHING", "4.0", "Construction material used to manage the passage of water around objects.",
           "Solin, gérant l'écoulement de l'eau autour d'une percée ou d'une jonction.",
           {"fr": ["solin"], "en": ["flashing"], "it": ["scossalina"], "de": ["Abdeckblech"]}),
        pt("CABLEARRANGER", "4.0", "A flexible accessory placed around cables to arrange them and minimize flexing at the point where it is placed.",
           "Peigne ou organiseur de câbles, limitant leur flexion au point de fixation.",
           {"fr": ["peigne de câbles", "organiseur de câbles"], "en": ["cable arranger"],
            "it": ["organizzatore di cavi"], "de": ["Kabelanordner"]}),
        pt("INSULATOR", "4.0", "A device designed to support and insulate a conductive element.",
           "Isolateur électrique supportant et isolant un élément conducteur.",
           {"fr": ["isolateur électrique"], "en": ["insulator"], "it": ["isolatore elettrico"],
            "de": ["Isolator"]}),
        pt("LOCK", "4.0", "A mechanical or electronic fastening device released by a physical object, secret information, or a combination thereof.",
           "Serrure : dispositif mécanique ou électronique de fermeture.",
           {"fr": ["serrure"], "en": ["lock"], "it": ["serratura"], "de": ["Schloss"]}),
        pt("TENSIONINGEQUIPMENT", "4.0", "Equipment used to maintain the tension of conductors or cables.",
           "Équipement maintenant la tension de conducteurs ou de câbles.",
           {"fr": ["équipement de tension"], "en": ["tensioning equipment"],
            "it": ["attrezzatura di tensionamento"], "de": ["Spannvorrichtung"]}),
        pt("RAILPAD", "4.3", "A non-metallic pad placed between rail and baseplate or rail and sleeper.",
           "Semelle non métallique posée entre le rail et le patin ou la traverse.",
           {"fr": ["semelle sous rail"], "en": ["rail pad"], "it": [], "de": []}, new_in_43=True),
        pt("SLIDINGCHAIR", "4.3", "A component supporting and retaining the stock rail, with a surface on which the switch rail's foot slides.",
           "Coussinet de glissement supportant le rail fixe et guidant le rail d'aiguille mobile.",
           {"fr": ["coussinet de glissement d'aiguillage"], "en": ["sliding chair"], "it": [], "de": []},
           new_in_43=True),
        pt("RAIL_LUBRICATION", "4.3", "A device that prevents wearing of rails through the wheel flange, reducing noise emissions.",
           "Dispositif de graissage de rail, réduisant l'usure et le bruit au passage des roues.",
           {"fr": ["graisseur de rail"], "en": ["rail lubrication device"], "it": [], "de": []},
           new_in_43=True),
        pt("PANEL_STRENGTHENING", "4.3", "A component that minimizes pumping effects of the substructure.",
           "Renfort de panneau de voie limitant les effets de pompage de la plateforme.",
           {"fr": ["renfort de panneau de voie"], "en": ["panel strengthening device"], "it": [], "de": []},
           new_in_43=True),
        pt("RAILBRACE", "4.3", "A rail component that prevents rails from tipping and twisting.",
           "Éclisse ou attache empêchant le basculement et le vrillage du rail.",
           {"fr": ["éclisse anti-basculement"], "en": ["rail brace"], "it": [], "de": []},
           new_in_43=True),
        pt("ELASTIC_CUSHION", "4.3", "A track elastic cushion mitigating longitudinal/lateral load impact on ballastless track structures.",
           "Coussin élastique de voie, atténuant les efforts longitudinaux et latéraux sur voie sans ballast.",
           {"fr": ["coussin élastique de voie"], "en": ["elastic cushion"], "it": [], "de": []},
           new_in_43=True),
        pt("SOUNDABSORPTION", "4.3", "A track component for sound absorption, often used with slab tracks.",
           "Absorbeur acoustique de voie, souvent utilisé avec les voies sur dalle.",
           {"fr": ["absorbeur acoustique de voie"], "en": ["sound absorption device"], "it": [], "de": []},
           new_in_43=True),
        pt("POINTMACHINEMOUNTINGDEVICE", "4.3", "A device supporting the mounting of a point machine (switch motor).",
           "Support de fixation du moteur d'aiguille (appareil de voie).",
           {"fr": ["support de moteur d'aiguille"], "en": ["point machine mounting device"], "it": [], "de": []},
           new_in_43=True),
        pt("POINT_MACHINE_LOCKING_DEVICE", "4.3", "A device locking a point machine (switch motor).",
           "Dispositif de verrouillage du moteur d'aiguille.",
           {"fr": ["verrouillage de moteur d'aiguille"], "en": ["point machine locking device"], "it": [], "de": []},
           new_in_43=True),
        pt("RAIL_MECHANICAL_EQUIPMENT", "4.3", "Mechanical equipment installed trackside, e.g. blocking device, speed regulator, track scale.",
           "Équipement mécanique installé en bordure de voie (dispositif de blocage, régulateur de vitesse...).",
           {"fr": ["équipement mécanique de voie"], "en": ["rail mechanical equipment"], "it": [], "de": []},
           new_in_43=True),
        pt("BIRDPROTECTION", "4.3", "A device preventing birds from perching at electrically critical points, protecting against electrical shocks.",
           "Dispositif anti-perchage protégeant les oiseaux (et l'installation) aux points électriquement critiques.",
           {"fr": ["protection anti-oiseaux"], "en": ["bird protection device"], "it": [], "de": []},
           new_in_43=True),
    ],
    notes_fr="Classe souvent recherchée pour des termes très concrets de "
             "chantier plutôt que des noms IFC : un « corbeau » qui reçoit "
             "l'about d'une dalle de transition, un dispositif fréquent en "
             "construction métallique, correspond à BRACKET. La plupart des "
             "valeurs propres au ferroviaire (RAILPAD, SLIDINGCHAIR, etc.) "
             "viennent de l'extension infrastructure d'IFC4.3.",
))

# ---------------------------------------------------------------------------
# DISTRIBUTION TECHNIQUE (CVC / PLOMBERIE / ÉLECTRICITÉ)
# ---------------------------------------------------------------------------

DATA.append(entry(
    "IfcDuctSegment", "Gaine aéraulique (tronçon)", "IfcFlowSegment",
    [PHYS, DIST, "Réseaux aérauliques (CVC)"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A segment of a duct system, distributing air for HVAC purposes.",
    "Tronçon de gaine assurant la distribution d'air (CVC).",
    ["Pset_DuctSegmentTypeCommon"],
    {"fr": ["gaine de ventilation", "conduit d'air", "gaine aéraulique"],
     "en": ["duct segment", "air duct"], "it": ["condotto aria"], "de": ["Luftkanal"]},
    [
        pt("RIGIDSEGMENT", "2x3", "A rigid segment is a continuous linear segment of duct that cannot be deformed.",
           "Tronçon de gaine rigide, ne pouvant être déformé.",
           {"fr": ["gaine rigide"], "en": ["rigid duct"], "it": ["condotto rigido"],
            "de": ["Starrer Kanal"]}),
        pt("FLEXIBLESEGMENT", "2x3", "A flexible segment is a continuous non-linear segment of duct that can be deformed and change flow direction.",
           "Tronçon de gaine flexible, déformable, pouvant changer de direction.",
           {"fr": ["gaine flexible"], "en": ["flexible duct"], "it": ["condotto flessibile"],
            "de": ["Flexkanal"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcPipeSegment", "Tuyauterie (tronçon)", "IfcFlowSegment",
    [PHYS, DIST, "Réseaux hydrauliques"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A segment of a pipe system, distributing fluids (water, gas...).",
    "Tronçon de canalisation assurant le transport d'un fluide (eau, gaz...).",
    ["Pset_PipeSegmentTypeCommon"],
    {"fr": ["tuyau", "canalisation", "conduite"], "en": ["pipe segment", "pipe"],
     "it": ["tubazione"], "de": ["Rohrleitung"]},
    [
        pt("RIGIDSEGMENT", "2x3", "A rigid segment is a continuous linear segment of pipe that cannot be deformed.",
           "Tronçon de canalisation rigide.",
           {"fr": ["tuyau rigide"], "en": ["rigid pipe"], "it": ["tubo rigido"],
            "de": ["Starres Rohr"]}),
        pt("FLEXIBLESEGMENT", "2x3", "A flexible segment is a continuous non-linear segment of pipe that can be deformed.",
           "Tronçon de canalisation flexible.",
           {"fr": ["tuyau flexible"], "en": ["flexible pipe"], "it": ["tubo flessibile"],
            "de": ["Flexrohr"]}),
        pt("GUTTER", "2x3", "A gutter segment is a continuous open-channel segment of pipe.",
           "Chéneau ou gouttière, tronçon de canalisation à ciel ouvert.",
           {"fr": ["gouttière", "chéneau"], "en": ["gutter"], "it": ["grondaia"],
            "de": ["Dachrinne"]}),
        pt("SPOOL", "2x3", "A type of rigid segment, typically shorter, used for providing connectivity within a piping network.",
           "Tronçon rigide court assurant la connectivité au sein d'un réseau de tuyauterie.",
           {"fr": ["tronçon de raccordement"], "en": ["pipe spool"], "it": ["tratto di raccordo"],
            "de": ["Rohrschuss"]}),
        pt("CULVERT", "4.3", "A covered channel or large pipe forming a watercourse below ground level, usually under a road or railway.",
           "Buse ou dalot enterré sous une voirie ou une voie ferrée.",
           {"fr": ["buse", "dalot", "ponceau"], "en": ["culvert"], "it": ["tombino", "canaletta interrata"],
            "de": ["Durchlass"]}, new_in_43=True),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcSanitaryTerminal", "Appareil sanitaire", "IfcFlowTerminal",
    [PHYS, DIST, "Appareils sanitaires"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A sanitary terminal is a construction component used for personal "
    "hygiene, e.g. sink, toilet, bath.",
    "Appareil d'hygiène ou d'usage sanitaire (lavabo, WC, baignoire...).",
    ["Pset_SanitaryTerminalTypeCommon"],
    {"fr": ["appareil sanitaire", "sanitaire"], "en": ["sanitary terminal", "sanitary fixture"],
     "it": ["apparecchio sanitario"], "de": ["Sanitärobjekt"]},
    [
        pt("WASHHANDBASIN", "2x3", "Waste water appliance for washing the upper parts of the body.", "Lavabo.",
           {"fr": ["lavabo", "vasque"], "en": ["wash hand basin", "sink"], "it": ["lavabo"],
            "de": ["Waschbecken"]}),
        pt("TOILETPAN", "2x3", "Soil appliance for the disposal of excrement.", "Cuvette de WC.",
           {"fr": ["wc", "cuvette", "toilette"], "en": ["toilet", "WC pan"], "it": ["water", "wc"],
            "de": ["WC-Becken"]}),
        pt("SHOWER", "2x3", "Installation or waste water appliance emitting a spray of water to wash the human body.", "Douche.",
           {"fr": ["douche"], "en": ["shower"], "it": ["doccia"], "de": ["Dusche"]}),
        pt("BATH", "2x3", "Sanitary appliance for immersion of the human body or parts of it.", "Baignoire.",
           {"fr": ["baignoire"], "en": ["bathtub"], "it": ["vasca da bagno"], "de": ["Badewanne"]}),
        pt("URINAL", "2x3", "Soil appliance that receives urine and directs it to a waste outlet.", "Urinoir.",
           {"fr": ["urinoir"], "en": ["urinal"], "it": ["orinatoio"], "de": ["Urinal"]}),
        pt("BIDET", "2x3", "Waste water appliance for washing the excretory organs while sitting astride the bowl.", "Bidet.",
           {"fr": ["bidet"], "en": ["bidet"], "it": ["bidet"], "de": ["Bidet"]}),
        pt("CISTERN", "2x3", "A water storage unit attached to a sanitary terminal, discharging water to cleanse it.",
           "Réservoir de chasse d'eau alimentant un appareil sanitaire.",
           {"fr": ["réservoir de chasse d'eau", "chasse d'eau"], "en": ["cistern"], "it": ["cassetta di scarico"],
            "de": ["Spülkasten"]}),
        pt("SINK", "2x3", "Waste water appliance for receiving, retaining or disposing of domestic, culinary or industrial liquids.",
           "Évier, pour recevoir ou évacuer des liquides domestiques ou industriels.",
           {"fr": ["évier"], "en": ["sink"], "it": ["lavello"], "de": ["Spüle"]}),
        pt("SANITARYFOUNTAIN", "2x3", "A sanitary terminal that provides a low pressure jet of water for a specific purpose.",
           "Fontaine sanitaire délivrant un jet d'eau à basse pression pour un usage spécifique.",
           {"fr": ["fontaine sanitaire"], "en": ["sanitary fountain"], "it": ["fontanella sanitaria"],
            "de": ["Sanitärbrunnen"]}),
        pt("WCSEAT", "2x3", "Hinged seat that fits on top of a water closet (WC) pan.",
           "Abattant de WC.",
           {"fr": ["abattant de wc"], "en": ["WC seat", "toilet seat"], "it": ["sedile del wc"],
            "de": ["WC-Sitz"]}, deprecated_since="4.3"),
    ],
    notes_fr="WCSEAT est déprécié depuis IFC4.3 : représenter un abattant de "
             "WC via IfcDiscreteAccessory avec ObjectType='WC Seat'.",
))

DATA.append(entry(
    "IfcCableCarrierSegment", "Chemin de câbles (tronçon)", "IfcFlowSegment",
    [PHYS, DIST, "Réseaux électriques"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A segment of a system for carrying cables, e.g. cable tray or "
    "conduit.",
    "Tronçon de système de cheminement de câbles (chemin de câbles, "
    "goulotte, conduit électrique).",
    ["Pset_CableCarrierSegmentTypeCommon"],
    {"fr": ["chemin de câbles", "goulotte", "conduit électrique"],
     "en": ["cable tray", "conduit"], "it": ["canalina", "passerella portacavi"],
     "de": ["Kabeltrasse", "Kabelkanal"]},
    [
        pt("CABLETRAYSEGMENT", "2x3", "A (typically) open carrier segment onto which cables are laid.",
           "Tronçon de chemin de câbles ouvert, sur lequel les câbles reposent.",
           {"fr": ["chemin de câbles"], "en": ["cable tray"], "it": ["passerella portacavi"],
            "de": ["Kabelrinne"]}),
        pt("CABLELADDERSEGMENT", "2x3", "An open carrier segment on which cables are carried on a ladder structure.",
           "Tronçon en forme d'échelle à câbles, structure ouverte supportant les câbles.",
           {"fr": ["échelle à câbles"], "en": ["cable ladder"], "it": ["scaletta portacavi"],
            "de": ["Kabelleiter"]}),
        pt("CONDUITSEGMENT", "2x3", "An enclosed tubular carrier segment through which cables are pulled.",
           "Tronçon de conduit électrique tubulaire fermé, dans lequel les câbles sont tirés.",
           {"fr": ["conduit électrique", "gaine électrique"], "en": ["conduit"], "it": ["tubo protettivo"],
            "de": ["Elektroleerrohr"]}),
        pt("CABLETRUNKINGSEGMENT", "2x3", "An enclosed carrier segment with one or more compartments into which cables are placed.",
           "Tronçon de goulotte fermée, à un ou plusieurs compartiments.",
           {"fr": ["goulotte"], "en": ["cable trunking"], "it": ["canalina"], "de": ["Kabelkanal"]}),
        pt("CABLEBRACKET", "4.3", "A horizontal cable support fixed at one end only, spaced at intervals, on which cables rest.",
           "Console de câbles fixée en porte-à-faux, sur laquelle reposent les câbles.",
           {"fr": ["console de câbles"], "en": ["cable bracket"], "it": ["mensola portacavi"],
            "de": ["Kabelkonsole"]}, new_in_43=True),
        pt("CATENARYWIRE", "4.3", "A longitudinal wire supporting the grooved contact wires of an overhead electrified railway line, directly or indirectly.",
           "Câble porteur longitudinal soutenant le fil de contact d'une ligne électrifiée ferroviaire (caténaire).",
           {"fr": ["câble porteur de caténaire"], "en": ["catenary wire"], "it": ["filo portante della catenaria"],
            "de": ["Tragseil (Fahrleitung)"]}, new_in_43=True),
        pt("DROPPER", "4.3", "A cable carrier used to suspend a cable from another cable; could also conduct electricity.",
           "Pendule suspendant un câble à un autre câble (caténaire), pouvant aussi conduire l'électricité.",
           {"fr": ["pendule de caténaire"], "en": ["dropper"], "it": ["pendino della catenaria"],
            "de": ["Hänger (Fahrleitung)"]}, new_in_43=True),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcLightFixture", "Luminaire", "IfcFlowTerminal",
    [PHYS, DIST, "Éclairage"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A light fixture (or luminaire) is a piece of equipment that houses "
    "a light source.",
    "Appareil d'éclairage abritant une ou plusieurs sources lumineuses.",
    ["Pset_LightFixtureTypeCommon"],
    {"fr": ["luminaire", "appareil d'éclairage"], "en": ["light fixture", "luminaire"],
     "it": ["apparecchio di illuminazione"], "de": ["Leuchte"]},
    [
        pt("POINTSOURCE", "2x3", "A light fixture with negligible area, emitting light with approximately equal intensity in all directions.",
           "Luminaire ponctuel (spot), émettant une lumière d'intensité quasi égale dans toutes les directions.",
           {"fr": ["spot", "luminaire ponctuel"], "en": ["point source fixture"],
            "it": ["faretto"], "de": ["Punktleuchte"]}),
        pt("DIRECTIONSOURCE", "2x3", "A light fixture with a length or surface area emitting light in a direction (e.g. fluorescent tube).",
           "Luminaire directionnel (ex. réglette fluorescente), émettant la lumière dans une direction.",
           {"fr": ["projecteur", "réglette lumineuse"], "en": ["directional fixture"], "it": ["proiettore"],
            "de": ["Strahler"]}),
        pt("SECURITYLIGHTING", "4.0", "A light fixture directing occupants in an emergency, such as an illuminated exit sign or emergency flood light.",
           "Éclairage de sécurité guidant les occupants en cas d'urgence (bloc issue de secours, projecteur d'évacuation).",
           {"fr": ["éclairage de sécurité", "bloc de secours"], "en": ["security lighting", "emergency lighting"],
            "it": ["illuminazione di sicurezza"], "de": ["Sicherheitsbeleuchtung"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcAirTerminal", "Bouche de ventilation", "IfcFlowTerminal",
    [PHYS, DIST, "Terminaux aérauliques"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "An air terminal is a construction element that typically covers an "
    "air distribution outlet or inlet, e.g. a diffuser or grille.",
    "Élément terminal d'un réseau aéraulique : diffuseur, grille de "
    "soufflage ou de reprise.",
    ["Pset_AirTerminalTypeCommon"],
    {"fr": ["bouche de ventilation", "grille de soufflage", "diffuseur"],
     "en": ["air terminal", "diffuser", "grille"], "it": ["bocchetta"],
     "de": ["Luftdurchlass"]},
    [
        pt("DIFFUSER", "2x3", "An outlet discharging supply air in various directions and planes.", "Diffuseur de soufflage.",
           {"fr": ["diffuseur"], "en": ["diffuser"], "it": ["diffusore"], "de": ["Diffusor"]}),
        pt("GRILLE", "2x3", "A covering for any area through which air passes.", "Grille de ventilation.",
           {"fr": ["grille de ventilation"], "en": ["grille"], "it": ["griglia"], "de": ["Gitter"]}),
        pt("REGISTER", "2x3", "A grille typically equipped with a damper or control valve.", "Bouche réglable à registre.",
           {"fr": ["bouche à registre"], "en": ["register"], "it": ["bocchetta regolabile"],
            "de": ["Regelklappe"]}),
        pt("LOUVRE", "4.0", "A rectilinear louvre.", "Grille à lames rectilignes.",
           {"fr": ["grille à lames"], "en": ["louvre"], "it": ["griglia a lamelle"],
            "de": ["Lamellengitter"]}),
    ],
    notes_fr="Un brise-soleil architectural à lames orientables (louver de "
             "façade) relève d'IfcShadingDevice, pas de ce PredefinedType "
             "LOUVRE qui désigne une grille de ventilation rectiligne.",
))

DATA.append(entry(
    "IfcSpaceHeater", "Émetteur de chauffage", "IfcFlowTerminal",
    [PHYS, DIST, "Émetteurs de chauffage"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A space heater is a device used to warm the air in an occupied "
    "space using heated water, steam or electricity, e.g. a radiator.",
    "Appareil de chauffage d'un espace occupé (radiateur, convecteur).",
    ["Pset_SpaceHeaterTypeCommon"],
    {"fr": ["radiateur", "émetteur de chauffage", "convecteur"], "en": ["space heater", "radiator"],
     "it": ["radiatore"], "de": ["Heizkörper"]},
    [pt("CONVECTOR", "2x3", "A heat-distributing unit that operates with gravity-circulated air.",
        "Radiateur de type convecteur, fonctionnant par circulation d'air par gravité.",
        {"fr": ["convecteur"], "en": ["convector"], "it": ["convettore"], "de": ["Konvektor"]}),
     pt("RADIATOR", "2x3", "A heat-distributing unit that operates with thermal radiation.",
        "Radiateur classique à eau chaude, fonctionnant par rayonnement thermique.",
        {"fr": ["radiateur à eau chaude"], "en": ["radiator"], "it": ["radiatore"],
         "de": ["Heizkörper"]})],
    notes_fr="",
))

# ---------------------------------------------------------------------------
# AMÉNAGEMENT INTÉRIEUR
# ---------------------------------------------------------------------------

DATA.append(entry(
    "IfcFurniture", "Mobilier", "IfcElement",
    [PHYS, FURN, "Mobilier"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "An object which is used to equip an interior space, e.g. tables, "
    "chairs, cabinets.",
    "Objet équipant un espace intérieur : tables, chaises, armoires...",
    ["Pset_FurnitureTypeCommon"],
    {"fr": ["mobilier", "meuble"], "en": ["furniture"], "it": ["arredo", "mobilio"],
     "de": ["Möbel"]},
    [
        pt("CHAIR", "4.0", "Furniture for seating a single person.", "Chaise, pour une seule personne.",
           {"fr": ["chaise"], "en": ["chair"], "it": ["sedia"], "de": ["Stuhl"]}),
        pt("TABLE", "4.0", "Furniture with a countertop for multiple people.", "Table, pour plusieurs personnes.",
           {"fr": ["table"], "en": ["table"], "it": ["tavolo"], "de": ["Tisch"]}),
        pt("DESK", "4.0", "Furniture with a countertop and optional drawers for a single person.",
           "Bureau, plan de travail avec tiroirs éventuels, pour une personne.",
           {"fr": ["bureau"], "en": ["desk"], "it": ["scrivania"], "de": ["Schreibtisch"]}),
        pt("BED", "4.0", "Furniture for sleeping.", "Lit.",
           {"fr": ["lit"], "en": ["bed"], "it": ["letto"], "de": ["Bett"]}),
        pt("FILECABINET", "4.0", "Furniture with sliding drawers for storing files.", "Classeur à tiroirs.",
           {"fr": ["classeur"], "en": ["filing cabinet"], "it": ["schedario"], "de": ["Aktenschrank"]}),
        pt("SHELF", "4.0", "Furniture for storing books or other items.", "Étagère.",
           {"fr": ["étagère"], "en": ["shelf"], "it": ["scaffale"], "de": ["Regal"]}),
        pt("SOFA", "4.0", "Furniture for seating multiple people.", "Canapé, pour plusieurs personnes.",
           {"fr": ["canapé"], "en": ["sofa"], "it": ["divano"], "de": ["Sofa"]}),
        pt("TECHNICALCABINET", "4.0", "A piece of furniture for holding, displaying and protecting technical appliances.",
           "Armoire technique organisant appareils, tiroirs ou racks.",
           {"fr": ["armoire technique"], "en": ["technical cabinet"], "it": ["armadio tecnico"],
            "de": ["Technikschrank"]}),
    ],
    notes_fr="",
))

# ---------------------------------------------------------------------------
# ÉLÉMENTS SPATIAUX
# ---------------------------------------------------------------------------

DATA.append(entry(
    "IfcSpace", "Espace / Local", "IfcSpatialElement",
    [SPATIAL, "Structure spatiale", "Espace"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A space represents an area or volume bounded actually or "
    "theoretically, used for the containment or delimitation of "
    "physical elements.",
    "Zone ou volume délimité, réel ou théorique, utilisé pour contenir "
    "ou délimiter des éléments physiques (pièce, local).",
    ["Pset_SpaceCommon"],
    {"fr": ["espace", "local", "pièce"], "en": ["space", "room"], "it": ["ambiente", "locale"],
     "de": ["Raum"]},
    [
        pt("SPACE", "2x3", "Any space not falling into another category.", "Local ou pièce standard.",
           {"fr": ["local standard"], "en": ["standard space"], "it": ["locale standard"],
            "de": ["Standardraum"]}),
        pt("PARKING", "2x3", "A space dedicated for use as a parking spot for vehicles, including access.",
           "Place ou zone de parking, y compris ses accès.",
           {"fr": ["place de parking", "zone de stationnement"], "en": ["parking space"],
            "it": ["posto auto"], "de": ["Parkplatz"]}),
        pt("GFA", "2x3", "Gross Floor Area - a space for each building story including all net and construction area.",
           "Espace utilisé pour le calcul de surface brute de plancher.",
           {"fr": ["surface brute de plancher"], "en": ["gross floor area"],
            "it": ["superficie lorda di piano"], "de": ["Bruttogeschossfläche"]}),
        pt("INTERNAL", "4.0", "A space inside a facility.", "Espace intérieur (à l'intérieur d'un ouvrage).",
           {"fr": ["espace intérieur"], "en": ["internal space"], "it": ["spazio interno"],
            "de": ["Innenraum"]}, deprecated_since="4.3"),
        pt("EXTERNAL", "4.0", "A space outside of a facility.", "Espace extérieur (hors d'un ouvrage).",
           {"fr": ["espace extérieur"], "en": ["external space"], "it": ["spazio esterno"],
            "de": ["Außenraum"]}, deprecated_since="4.3"),
        pt("BERTH", "4.3", "A space dedicated to the berthing of vessels within a port or managed area.",
           "Poste d'amarrage dédié aux navires dans un port ou une zone gérée.",
           {"fr": ["poste d'amarrage"], "en": ["berth"], "it": ["ormeggio"],
            "de": ["Liegeplatz"]}, new_in_43=True),
    ],
    notes_fr="INTERNAL et EXTERNAL sont dépréciés depuis IFC4.3.2.0 : utiliser "
             "à la place la propriété booléenne IsExternal du Pset_SpaceCommon.",
))

DATA.append(entry(
    "IfcBuildingStorey", "Étage / Niveau", "IfcSpatialStructureElement",
    [SPATIAL, "Structure spatiale", "Étage"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A building storey represents a (nearly) horizontal aggregation of "
    "spaces that are vertically bound.",
    "Regroupement (quasi) horizontal d'espaces situés à un même niveau "
    "vertical.",
    ["Pset_BuildingStoreyCommon"],
    {"fr": ["étage", "niveau"], "en": ["building storey", "floor level"], "it": ["piano"],
     "de": ["Geschoss"]},
    [pt("NOTDEFINED", "2x3", "Undefined.", "Non précisé.", {})],
    notes_fr="",
))

DATA.append(entry(
    "IfcBuilding", "Bâtiment", "IfcSpatialStructureElement",
    [SPATIAL, "Structure spatiale", "Bâtiment"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A building represents a structure that provides shelter for its "
    "occupants or contents.",
    "Structure abritant des occupants ou des biens.",
    ["Pset_BuildingCommon"],
    {"fr": ["bâtiment", "immeuble"], "en": ["building"], "it": ["edificio"], "de": ["Gebäude"]},
    [pt("NOTDEFINED", "2x3", "Undefined.", "Non précisé.", {})],
    notes_fr="",
))

DATA.append(entry(
    "IfcSite", "Terrain / Site", "IfcSpatialStructureElement",
    [SPATIAL, "Structure spatiale", "Site"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A site is defined as a designated area of land on which the "
    "project construction is to be completed.",
    "Zone de terrain désignée sur laquelle le projet de construction est "
    "réalisé.",
    ["Pset_SiteCommon"],
    {"fr": ["terrain", "site", "parcelle"], "en": ["site", "plot"], "it": ["terreno", "sito"],
     "de": ["Grundstück"]},
    [pt("NOTDEFINED", "2x3", "Undefined.", "Non précisé.", {})],
    notes_fr="",
))

# ---------------------------------------------------------------------------
# GÉNIE CIVIL ET INFRASTRUCTURE (nouveautés IFC4.3)
# ---------------------------------------------------------------------------

DATA.append(entry(
    "IfcKerb", "Bordure de trottoir", "IfcCivilElement",
    [PHYS, CIVIL, "Voirie et équipements routiers"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A kerb (curb) is a raised border along the edge of a road or "
    "pavement, introduced in IFC4.3 for infrastructure projects. The "
    "enumeration currently defines no specific kerb types.",
    "Bordure surélevée en limite de chaussée ou de trottoir. Classe "
    "introduite en IFC4.3 ; aucun type spécifique n'est actuellement défini "
    "(uniquement USERDEFINED/NOTDEFINED).",
    ["Pset_KerbCommon"],
    {"fr": ["bordure de trottoir", "bordure de voirie"], "en": ["kerb", "curb"],
     "it": ["cordolo stradale"], "de": ["Bordstein"]},
    [pt("NOTDEFINED", "4.3", "Undefined kerb type.", "Type non précisé.", {}, new_in_43=True)],
    notes_fr="Classe absente d'IFC2x3 et IFC4 : nouveauté du domaine "
             "infrastructure introduite en IFC4.3.",
    version_notes="Nouveau en IFC4.3 (extension infrastructure routière).",
))

DATA.append(entry(
    "IfcPavement", "Revêtement de chaussée", "IfcCivilElement",
    [PHYS, CIVIL, "Voirie et équipements routiers"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A pavement is the durable surface material laid down on a road, "
    "path or similar area, introduced in IFC4.3.",
    "Structure de surface durable d'une chaussée, d'un chemin ou d'une "
    "aire similaire. Classe introduite en IFC4.3.",
    ["Pset_PavementCommon"],
    {"fr": ["revêtement de chaussée", "chaussée"], "en": ["pavement"], "it": ["pavimentazione stradale"],
     "de": ["Fahrbahnbelag"]},
    [
        pt("FLEXIBLE", "4.3", "Pavement with a bituminous surfacing and a base layer with or without a hydrocarbon binder.",
           "Chaussée souple, à surface bitumineuse (enrobé) et couche de base avec ou sans liant hydrocarboné.",
           {"fr": ["chaussée souple", "chaussée en enrobé", "chaussée bitumineuse"],
            "en": ["flexible pavement", "asphalt pavement"], "it": ["pavimentazione flessibile", "pavimentazione bituminosa"],
            "de": ["Flexibler Fahrbahnbelag", "Asphaltbelag"]}, new_in_43=True),
        pt("RIGID", "4.3", "Pavement substantially constructed of cement concrete.",
           "Chaussée rigide, essentiellement construite en béton de ciment.",
           {"fr": ["chaussée rigide"], "en": ["rigid pavement"], "it": ["pavimentazione rigida"],
            "de": ["Starrer Fahrbahnbelag"]}, new_in_43=True),
    ],
    notes_fr="À ne pas confondre avec IfcSlab(PAVING) qui désigne une "
             "dalle de pavage ponctuelle plutôt qu'une structure de "
             "chaussée complète.",
    version_notes="Nouveau en IFC4.3 (extension infrastructure routière).",
))

DATA.append(entry(
    "IfcRail", "Rail (voie ferrée)", "IfcBuildingElement",
    [PHYS, CIVIL, "Voie ferrée et équipements ferroviaires"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A rail is a special section bar ensuring the guidance of the wheel "
    "of rolling stock or other heavy machinery, introduced in IFC4.3.",
    "Barre profilée assurant le guidage des roues d'un matériel roulant. "
    "Classe introduite en IFC4.3.",
    ["Pset_RailCommon"],
    {"fr": ["rail", "rail de chemin de fer"], "en": ["rail"], "it": ["rotaia"],
     "de": ["Schiene"]},
    [
        pt("RAIL", "4.3", "A special section bar (usually steel) ensuring the guidance of the wheel of rolling stock; two rails form a track.",
           "Rail courant : barre profilée (généralement acier) assurant le guidage des roues d'un matériel roulant.",
           {"fr": ["rail courant"], "en": ["running rail"], "it": ["rotaia corrente"],
            "de": ["Regelschiene"]}, new_in_43=True),
        pt("RACKRAIL", "4.3", "A rack rail is a building module for enhancing traction and brake performance.",
           "Rail à crémaillère améliorant la traction et le freinage (chemins de fer de montagne).",
           {"fr": ["rail à crémaillère"], "en": ["rack rail"], "it": ["rotaia a cremagliera"],
            "de": ["Zahnstange"]}, new_in_43=True),
        pt("BLADE", "4.3", "A machined rail, fixed/joined at the heel end, providing continuity of wheel support at a switch (points).",
           "Lame d'aiguillage : rail mobile usiné assurant la continuité de roulement au niveau d'un aiguillage.",
           {"fr": ["lame d'aiguillage", "aiguille"], "en": ["switch blade"], "it": ["ago di scambio"],
            "de": ["Zungenschiene"]}, new_in_43=True),
        pt("STOCKRAIL", "4.3", "A fixed machined rail ensuring continuity on the main or diverging track with the switch open, supporting the switch rail.",
           "Rail fixe usiné supportant la lame d'aiguillage et assurant la continuité de la voie.",
           {"fr": ["contre-aiguille", "rail support d'aiguillage"], "en": ["stock rail"], "it": ["controrotaia"],
            "de": ["Backenschiene"]}, new_in_43=True),
        pt("CHECKRAIL", "4.3", "A rail laid close to the gauge face of a running rail, aiding lateral wheel guidance and preventing derailment.",
           "Contre-rail de guidage, posé au plus près du rail courant pour prévenir le déraillement en courbe serrée.",
           {"fr": ["contre-rail de guidage"], "en": ["check rail"], "it": ["controrotaia di guida"],
            "de": ["Radlenker"]}, new_in_43=True),
        pt("GUARDRAIL", "4.3", "A guard rail limits the risk of train derailment, normally not loaded.",
           "Contre-rail anti-déraillement ferroviaire (à ne pas confondre avec un garde-corps de bâtiment).",
           {"fr": ["contre-rail anti-déraillement"], "en": ["guard rail (track)"], "it": ["controrotaia di sicurezza"],
            "de": ["Schutzschiene"]}, new_in_43=True),
    ],
    notes_fr="Attention à l'homonymie : IfcRail.GUARDRAIL (contre-rail "
             "ferroviaire anti-déraillement) n'a rien à voir avec "
             "IfcRailing.GUARDRAIL (garde-corps de protection contre les "
             "chutes en bâtiment) — deux classes et deux domaines différents "
             "pour le même mot anglais.",
    version_notes="Nouveau en IFC4.3 (extension infrastructure ferroviaire).",
))

DATA.append(entry(
    "IfcTrackElement", "Élément de voie ferrée", "IfcBuildingElement",
    [PHYS, CIVIL, "Voie ferrée et équipements ferroviaires"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A track element is a built element used specifically in the track "
    "domain in railway.",
    "Élément construit utilisé spécifiquement dans le domaine de la voie "
    "ferrée.",
    ["Pset_TrackElementCommon"],
    {"fr": ["élément de voie", "composant de voie ferrée"], "en": ["track element"],
     "it": ["elemento del binario"], "de": ["Gleiselement"]},
    [
        pt("SLEEPER", "4.3", "A track element that supports running rails, guard rails and check rails, usually at right angles to the track axis.",
           "Traverse : élément de voie supportant les rails de roulement, contre-rails et rails de guidage.",
           {"fr": ["traverse", "traverse de voie"], "en": ["sleeper", "railroad tie"],
            "it": ["traversina"], "de": ["Schwelle"]}, new_in_43=True),
        pt("FROG", "4.3", "An arrangement ensuring the intersection of two opposite running edges of turnouts or diamond crossings.",
           "Cœur d'aiguillage : dispositif assurant le croisement des files de roulement d'un appareil de voie.",
           {"fr": ["cœur d'aiguillage", "cœur de croisement"], "en": ["frog"], "it": ["cuore di scambio"],
            "de": ["Herzstück"]}, new_in_43=True),
        pt("DERAILER", "4.3", "A fixed device which, when placed on the rail, derails the wheels of a vehicle to protect a converging line.",
           "Dérailleur : dispositif fixe provoquant le déraillement volontaire d'un véhicule pour protéger une voie convergente.",
           {"fr": ["dérailleur"], "en": ["derailer"], "it": ["deviatoio di sicurezza"],
            "de": ["Gleissperre"]}, new_in_43=True),
        pt("VEHICLESTOP", "4.3", "A fixed installation at the end of the track which stops any vehicle movement (e.g. buffer stop, sand hump).",
           "Butoir de voie : installation fixe en fin de voie arrêtant tout mouvement de véhicule.",
           {"fr": ["butoir", "butoir de voie", "heurtoir"], "en": ["buffer stop"], "it": ["paraurti di fine binario"],
            "de": ["Prellbock"]}, new_in_43=True),
        pt("BLOCKINGDEVICE", "4.3", "A device composed of pneumatic, mechanic or electric components causing the braking of a train in case of emergency.",
           "Dispositif de blocage d'urgence provoquant le freinage d'un train.",
           {"fr": ["dispositif de blocage d'urgence"], "en": ["blocking device"], "it": ["dispositivo di blocco"],
            "de": ["Blockiervorrichtung"]}, new_in_43=True),
        pt("SPEEDREGULATOR", "4.3", "A device composed of pneumatic, mechanic or electric components causing the braking of a train.",
           "Régulateur de vitesse : dispositif provoquant le freinage contrôlé d'un train.",
           {"fr": ["régulateur de vitesse"], "en": ["speed regulator"], "it": ["regolatore di velocità"],
            "de": ["Geschwindigkeitsregler"]}, new_in_43=True),
        pt("HALF_SET_OF_BLADES", "4.3", "One stock rail and its switch rail complete with small fittings, right or left hand as seen from the switch toe.",
           "Demi-jeu de lames d'aiguille : un rail fixe et sa lame mobile associée, avec petite quincaillerie.",
           {"fr": ["demi-jeu de lames d'aiguille"], "en": ["half set of blades"], "it": ["semiscambio"],
            "de": ["Halber Zungensatz"]}, new_in_43=True),
        pt("TRACKENDOFALIGNMENT", "4.3", "A special functional installation such as an axle-gauge changeover point or transporter wagon loading point.",
           "Installation spéciale de fin de voie (changement d'écartement, chargement de wagon transporteur...).",
           {"fr": ["fin de voie (installation spéciale)"], "en": ["track end of alignment"], "it": [], "de": []},
           new_in_43=True),
    ],
    notes_fr="SLEEPER (traverse) est l'un des termes ferroviaires les plus "
             "recherchés : à ne pas confondre avec IfcCourse(BALLASTBED), "
             "la couche de ballast sur laquelle reposent les traverses.",
    version_notes="Nouveau en IFC4.3 (extension infrastructure ferroviaire).",
))

DATA.append(entry(
    "IfcSignal", "Signal (ferroviaire/routier)", "IfcFlowTerminal",
    [PHYS, CIVIL, "Signalisation"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "An active device that conveys information or instructions to users, "
    "by means of an audio, visual signal, or a combination of both — e.g. "
    "a railway signal frame or a traffic light unit.",
    "Dispositif actif transmettant une information ou une instruction "
    "(signal visuel, sonore ou mixte) — ex. un signal ferroviaire ou un feu "
    "de circulation.",
    ["Pset_SignalCommon"],
    {"fr": ["signal", "signal ferroviaire", "feu de signalisation"], "en": ["signal"],
     "it": ["segnale"], "de": ["Signal"]},
    [
        pt("VISUAL", "4.3", "A signal type conveying information in a visual manner, such as a light, cluster of lights, or mechanical moving shape.",
           "Signal visuel (feu, ensemble de feux, ou forme mécanique mobile).",
           {"fr": ["signal visuel"], "en": ["visual signal"], "it": ["segnale visivo"],
            "de": ["Visuelles Signal"]}, new_in_43=True),
        pt("AUDIO", "4.3", "A signal type conveying information by emitting an audio signal such as a beep, ring, horn or explosive sound.",
           "Signal sonore (avertisseur, sonnerie, corne...).",
           {"fr": ["signal sonore"], "en": ["audio signal"], "it": ["segnale acustico"],
            "de": ["Akustisches Signal"]}, new_in_43=True),
        pt("MIXED", "4.3", "A signal type conveying information in both a visual and audio manner.",
           "Signal mixte, à la fois visuel et sonore.",
           {"fr": ["signal mixte"], "en": ["mixed signal"], "it": ["segnale misto"],
            "de": ["Gemischtes Signal"]}, new_in_43=True),
    ],
    notes_fr="",
    version_notes="Nouveau en IFC4.3.",
))

DATA.append(entry(
    "IfcEarthworksCut", "Terrassement en déblai (fouille)", "IfcCivilElement",
    [PHYS, CIVIL, "Terrassements et couches de structure"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "The resulting void from modification of existing terrain or road "
    "structure by excavation or other means of removing material.",
    "Vide résultant de la modification d'un terrain ou d'une structure "
    "routière existante par excavation ou tout autre moyen d'enlèvement de "
    "matériau.",
    ["Pset_EarthworksCutCommon"],
    {"fr": ["déblai", "terrassement en déblai", "fouille"], "en": ["earthworks cut", "excavation"],
     "it": ["scavo"], "de": ["Aushub"]},
    [
        pt("TRENCH", "4.3", "Excavation whose length greatly exceeds the depth and width, e.g. for strip foundations or buried services.",
           "Tranchée : excavation dont la longueur dépasse largement la profondeur et la largeur (fondations filantes, réseaux enterrés).",
           {"fr": ["tranchée"], "en": ["trench"], "it": ["trincea"], "de": ["Graben"]}, new_in_43=True),
        pt("DREDGING", "4.3", "Underwater excavation to recover material or to create a greater depth of water.",
           "Dragage : excavation sous l'eau pour récupérer du matériau ou augmenter la profondeur d'eau.",
           {"fr": ["dragage"], "en": ["dredging"], "it": ["dragaggio"], "de": ["Baggerung"]}, new_in_43=True),
        pt("EXCAVATION", "4.3", "General type of excavation when a more accurate type is not specified.",
           "Excavation générale, quand un type plus précis n'est pas spécifié.",
           {"fr": ["excavation générale"], "en": ["general excavation"], "it": ["scavo generale"],
            "de": ["Allgemeiner Aushub"]}, new_in_43=True),
        pt("OVEREXCAVATION", "4.3", "Excavation beyond the depth required for construction, to replace unsuitable material.",
           "Sur-excavation, au-delà de la profondeur nécessaire, pour remplacer un matériau impropre.",
           {"fr": ["sur-excavation"], "en": ["overexcavation"], "it": ["sovrascavo"],
            "de": ["Übertiefer Aushub"]}, new_in_43=True),
        pt("TOPSOILREMOVAL", "4.3", "Excavation where the topmost layer of soil containing organic material is cut or stripped.",
           "Décapage de la terre végétale (couche superficielle organique).",
           {"fr": ["décapage de terre végétale"], "en": ["topsoil removal"], "it": ["scortico"],
            "de": ["Mutterbodenabtrag"]}, new_in_43=True),
        pt("STEPEXCAVATION", "4.3", "Removal of the soft part of an existing road slope, dug into steps, when widening a road.",
           "Excavation en redans (marches) du talus existant, lors de l'élargissement d'une route.",
           {"fr": ["excavation en redans"], "en": ["step excavation"], "it": ["scavo a gradoni"],
            "de": ["Stufenaushub"]}, new_in_43=True),
        pt("PAVEMENTMILLING", "4.3", "Removal of expired material from the top of a pavement, to be replaced by new material.",
           "Fraisage de chaussée : enlèvement du matériau usagé en surface avant remplacement.",
           {"fr": ["fraisage de chaussée", "rabotage de chaussée"], "en": ["pavement milling"],
            "it": ["fresatura della pavimentazione"], "de": ["Fahrbahnfräsung"]}, new_in_43=True),
        pt("CUT", "4.3", "Excavation where soil or rock below topsoil is cut to the depth required for roads/railways; removed material can be reused as fill.",
           "Déblai : matériau excavé sous la terre végétale à la profondeur requise (route, voie ferrée), pouvant être réutilisé en remblai.",
           {"fr": ["déblai"], "en": ["cut"], "it": ["scavo di sbancamento"], "de": ["Abtrag"]}, new_in_43=True),
        pt("BASE_EXCAVATION", "4.3", "Excavation for basements of buildings, bridge abutments or similar structures, partially or completely below ground.",
           "Fouille de fondation pour un sous-sol, une culée de pont ou un ouvrage similaire.",
           {"fr": ["fouille de fondation"], "en": ["base excavation"], "it": ["scavo di fondazione"],
            "de": ["Baugrubenaushub"]}, new_in_43=True),
    ],
    notes_fr="",
    version_notes="Nouveau en IFC4.3 (extension infrastructure).",
))

DATA.append(entry(
    "IfcEarthworksFill", "Terrassement en remblai", "IfcCivilElement",
    [PHYS, CIVIL, "Terrassements et couches de structure"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "An earthworks element created by earthwork activities to build a "
    "subgrade or to raise the level of the ground in general.",
    "Élément de terrassement créé pour constituer une plateforme support ou "
    "rehausser le niveau du terrain.",
    ["Pset_EarthworksFillCommon"],
    {"fr": ["remblai", "terrassement en remblai"], "en": ["earthworks fill", "embankment"],
     "it": ["rilevato"], "de": ["Damm"]},
    [
        pt("BACKFILL", "4.3", "Fill behind retaining walls or other structures such as quays, behind abutments and bridges.",
           "Remblai de contact, mis en œuvre derrière un mur de soutènement, un quai ou une culée de pont.",
           {"fr": ["remblai de contact"], "en": ["backfill"], "it": ["rinterro"], "de": ["Hinterfüllung"]},
           new_in_43=True),
        pt("COUNTERWEIGHT", "4.3", "Embankment built on the side of the main road structure to reduce settlement.",
           "Remblai de contrepoids, construit sur le côté de l'ouvrage principal pour réduire les tassements.",
           {"fr": ["remblai de contrepoids"], "en": ["counterweight fill"], "it": ["rilevato di contrappeso"],
            "de": ["Gegengewichtsdamm"]}, new_in_43=True),
        pt("SUBGRADE", "4.3", "The structure below pavement and above natural soil, supporting the loads transmitted by the overlying structure.",
           "Plateforme support de chaussée, entre le sol naturel et la structure de chaussée.",
           {"fr": ["plateforme support de chaussée"], "en": ["subgrade"], "it": ["sottofondo"],
            "de": ["Planum"]}, new_in_43=True),
        pt("EMBANKMENT", "4.3", "A predominantly longitudinal earthworks element, formed by cut or fill, where finished ground level is above or below original level.",
           "Remblai longitudinal, formé par déblai ou apport, dont le niveau fini diffère du terrain naturel.",
           {"fr": ["remblai"], "en": ["embankment"], "it": ["rilevato"], "de": ["Damm"]}, new_in_43=True),
        pt("TRANSITIONSECTION", "4.3", "A section of subgrade ensuring consistency of stiffness and preventing uneven settlement (e.g. embankment/bridge abutment).",
           "Zone de transition de remblai assurant la continuité de rigidité (ex. entre remblai et culée de pont).",
           {"fr": ["zone de transition de remblai"], "en": ["transition section"], "it": ["tratto di transizione"],
            "de": ["Übergangsbereich"]}, new_in_43=True),
        pt("SLOPEFILL", "4.3", "Side slope (batter) fill abutting the road structure or back slope fill.",
           "Remblai de talus, adossé à la structure routière.",
           {"fr": ["remblai de talus"], "en": ["slope fill"], "it": ["riempimento di scarpata"],
            "de": ["Böschungsauffüllung"]}, new_in_43=True),
        pt("SUBGRADEBED", "4.3", "Upper part of the soil, natural or constructed, that supports the loads transmitted by the overlying structure of a road, runway, or similar hard surface.",
           "Assise de plateforme : partie supérieure du sol, naturelle ou constituée, supportant les charges transmises par la structure routière.",
           {"fr": ["assise de plateforme"], "en": ["subgrade bed"], "it": ["strato di sottofondo"],
            "de": ["Planumsschicht"]}, new_in_43=True),
    ],
    notes_fr="",
    version_notes="Nouveau en IFC4.3 (extension infrastructure).",
))

DATA.append(entry(
    "IfcCourse", "Couche de structure (chaussée/voie)", "IfcCivilElement",
    [PHYS, CIVIL, "Terrassements et couches de structure"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A built element whose length greatly exceeds its thickness, usually a "
    "single material laid on site on top of another built element — a "
    "graded granular material, distinct from earthworks (soil-based).",
    "Élément dont la longueur dépasse largement l'épaisseur, généralement "
    "d'un seul matériau granulaire mis en œuvre sur un autre élément — "
    "distinct du terrassement (matériau du sol en place).",
    ["Pset_CourseCommon"],
    {"fr": ["couche de structure", "couche de forme"], "en": ["course", "layer"],
     "it": ["strato"], "de": ["Schicht"]},
    [
        pt("BALLASTBED", "4.3", "A layer composed of broken stones under the sleepers.",
           "Couche de ballast, constituée de pierres concassées sous les traverses.",
           {"fr": ["couche de ballast", "ballast"], "en": ["ballast bed"], "it": ["strato di ballast"],
            "de": ["Schotterbett"]}, new_in_43=True),
        pt("PAVEMENT", "4.3", "A layer within a pavement structure that forms a paved area or road (e.g. an asphalt layer).",
           "Couche de chaussée formant une aire pavée ou une route — c'est ici que se classe un enrobé "
           "(couche d'enrobé bitumineux), cité en exemple dans la définition officielle du type IfcCourse.",
           {"fr": ["couche de chaussée", "enrobé", "couche d'enrobé", "enrobé bitumineux"],
            "en": ["pavement course", "asphalt layer"], "it": ["strato di pavimentazione", "strato di conglomerato bituminoso"],
            "de": ["Fahrbahnschicht", "Asphaltschicht"]}, new_in_43=True),
        pt("ARMOUR", "4.3", "An aggregate layer whose primary function is to protect against erosion by water, e.g. riprap.",
           "Couche de protection contre l'érosion par l'eau (enrochement).",
           {"fr": ["enrochement de protection"], "en": ["armour layer", "riprap"], "it": ["strato di protezione"],
            "de": ["Steinschüttung"]}, new_in_43=True),
        pt("FILTER", "4.3", "An intermediate layer whose primary function is to prevent the washing through of fine materials.",
           "Couche filtrante empêchant le lessivage des matériaux fins.",
           {"fr": ["couche filtrante"], "en": ["filter layer"], "it": ["strato filtrante"],
            "de": ["Filterschicht"]}, new_in_43=True),
        pt("CORE", "4.3", "The bulk internal structure of aggregate structures.",
           "Noyau : structure interne massive d'un ouvrage en enrochement.",
           {"fr": ["noyau"], "en": ["core layer"], "it": ["nucleo"], "de": ["Kernschicht"]},
           new_in_43=True),
        pt("PROTECTION", "4.3", "A layer with the primary task of providing protection against erosion and scour.",
           "Couche de protection contre l'érosion et l'affouillement.",
           {"fr": ["couche de protection"], "en": ["protection layer"], "it": ["strato di protezione"],
            "de": ["Schutzschicht"]}, new_in_43=True),
    ],
    notes_fr="BALLASTBED (couche de ballast) est la couche sur laquelle "
             "reposent les traverses (IfcTrackElement.SLEEPER) ; à ne pas "
             "confondre avec une chape (IfcCovering.TOPPING), sans rapport.",
    version_notes="Nouveau en IFC4.3 (extension infrastructure).",
))

DATA.append(entry(
    "IfcAlignment", "Alignement (référence linéaire)", "IfcLinearElement",
    [PHYS, CIVIL, "Alignement et référencement linéaire"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A reference system for linear positioning used to place elements "
    "along linear construction works (roads, rails, bridges), combining a "
    "horizontal layout, an optional vertical layout, and (for rail) a cant "
    "layout.",
    "Système de référence géométrique utilisé pour positionner des "
    "éléments le long d'un ouvrage linéaire (route, voie ferrée, pont), "
    "combinant un tracé en plan (horizontal), un profil en long (vertical) "
    "et, pour le ferroviaire, un dévers (cant).",
    ["Pset_Stationing"],
    {"fr": ["alignement", "tracé en plan", "axe en plan"], "en": ["alignment"],
     "it": ["tracciato", "asse stradale"], "de": ["Trassierung", "Achse"]},
    [pt("NOTDEFINED", "4.3", "Undefined predefined type.", "Type non précisé.", {}, new_in_43=True)],
    notes_fr="Concept central de tout modèle d'infrastructure IFC4.3 : "
             "l'alignement est la colonne vertébrale géométrique le long de "
             "laquelle tous les autres éléments linéaires (route, voie "
             "ferrée, pont) sont positionnés et repérés (voir IfcReferent "
             "pour les points kilométriques/gares nichés sur l'alignement).",
    version_notes="Nouveau en IFC4.3 (concept central du domaine "
                  "infrastructure).",
))

DATA.append(entry(
    "IfcReferent", "Repère linéaire (point kilométrique, station)", "IfcProduct",
    [PHYS, CIVIL, "Alignement et référencement linéaire"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "Defines a position at a particular offset along an alignment curve — "
    "used for stations, mileposts, events or physical landmarks along a "
    "linear referencing system.",
    "Définit une position à une distance donnée le long d'un alignement — "
    "station, point kilométrique, événement ou repère physique au sein "
    "d'un système de référencement linéaire.",
    ["Pset_Stationing", "Pset_LinearReferencingMethod"],
    {"fr": ["point kilométrique", "pk", "chaînage", "repère linéaire"],
     "en": ["referent", "chainage marker"], "it": ["punto chilometrico"],
     "de": ["Kilometrierung"]},
    [
        pt("KILOPOINT", "4.3", "Kilo point.", "Point kilométrique (PK).",
           {"fr": ["point kilométrique", "pk"], "en": ["kilopoint"], "it": ["chilometrica"],
            "de": ["Kilometerpunkt"]}, new_in_43=True),
        pt("MILEPOINT", "4.3", "Mile point.", "Point milliaire.",
           {"fr": ["point milliaire"], "en": ["milepoint"], "it": ["punto miliare"],
            "de": ["Meilenpunkt"]}, new_in_43=True),
        pt("STATION", "4.3", "Defines the stationing (chainage) system along a linear element, establishing the origin or a station equation.",
           "Définit le système de stationnement (chaînage) le long d'un élément linéaire, origine ou équation de chaînage.",
           {"fr": ["station de chaînage"], "en": ["station"], "it": ["stazionamento"],
            "de": ["Station"]}, new_in_43=True),
        pt("REFERENCEMARKER", "4.3", "A notation referent, typically a marker physically located in the right of way of the road, rail or other system.",
           "Balise de repérage, matérialisée physiquement en bordure de route, de voie ferrée ou autre.",
           {"fr": ["balise de repérage"], "en": ["reference marker"], "it": ["indicatore di riferimento"],
            "de": ["Referenzmarke"]}, new_in_43=True),
        pt("LANDMARK", "4.3", "The referent is the location of a physical landmark visible in the field.",
           "Point de repère physique visible sur le terrain.",
           {"fr": ["point de repère visible"], "en": ["landmark"], "it": ["punto di riferimento"],
            "de": ["Landmarke"]}, new_in_43=True),
        pt("BOUNDARY", "4.3", "Where an administrative or maintenance boundary crosses the linear element being measured.",
           "Limite administrative ou de gestion croisant l'élément linéaire mesuré.",
           {"fr": ["limite administrative"], "en": ["boundary"], "it": ["confine amministrativo"],
            "de": ["Verwaltungsgrenze"]}, new_in_43=True),
        pt("INTERSECTION", "4.3", "The location of an intersection specified by the referent name.",
           "Point d'intersection désigné par le nom du repère.",
           {"fr": ["point d'intersection"], "en": ["intersection referent"], "it": ["punto di intersezione"],
            "de": ["Kreuzungspunkt"]}, new_in_43=True),
        pt("POSITION", "4.3", "Fully describes a linearly referenced location given the linear element, the measurement method and a measure value.",
           "Décrit une position chaînée complète (élément linéaire, méthode de mesure, valeur).",
           {"fr": ["position chaînée"], "en": ["position referent"], "it": ["posizione lineare"],
            "de": ["Linienbezogene Position"]}, new_in_43=True),
        pt("WIDTHEVENT", "4.3", "Specifies the width at a specific location along a road alignment and the type of transition from the previous location.",
           "Événement spécifiant la largeur à un point donné d'un alignement routier et le type de transition.",
           {"fr": ["événement de largeur"], "en": ["width event"], "it": ["evento di larghezza"],
            "de": ["Breitenereignis"]}, new_in_43=True),
        pt("SUPERELEVATIONEVENT", "4.3", "Specifies the superelevation (cross slope) at a specific location along a road alignment.",
           "Événement spécifiant le dévers (pente transversale) à un point donné d'un alignement routier.",
           {"fr": ["événement de dévers"], "en": ["superelevation event"], "it": ["evento di sopraelevazione"],
            "de": ["Überhöhungsereignis"]}, new_in_43=True),
    ],
    notes_fr="Le point kilométrique (« PK »), très utilisé en France/Suisse "
             "romande en génie civil routier et ferroviaire, correspond ici "
             "à IfcReferent(KILOPOINT), niché sur un IfcAlignment via "
             "IfcRelNests.",
    version_notes="Nouveau en IFC4.3 (référencement linéaire).",
))

# ---------------------------------------------------------------------------
# STRUCTURES SPATIALES D'INFRASTRUCTURE (route, voie ferrée, pont) — IFC4.3
# ---------------------------------------------------------------------------

DATA.append(entry(
    "IfcRoad", "Route (structure spatiale)", "IfcFacility",
    [SPATIAL, "Structure spatiale", "Route"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A route built on land to allow travel from one location to another "
    "(highways, streets, cycle/foot paths), excluding railways. As a "
    "Facility, provides the basic project structure element for a road "
    "project.",
    "Voie de circulation aménagée sur terrain (autoroute, rue, piste "
    "cyclable, cheminement piéton), à l'exclusion des voies ferrées. "
    "Élément de base de la hiérarchie spatiale d'un projet routier.",
    ["Pset_RoadCommon"],
    {"fr": ["route", "projet routier"], "en": ["road"], "it": ["strada"], "de": ["Straße"]},
    [pt("NOTDEFINED", "4.3", "Undefined road type.", "Type non précisé.", {}, new_in_43=True)],
    notes_fr="",
    version_notes="Nouveau en IFC4.3 (extension infrastructure routière).",
))

DATA.append(entry(
    "IfcRoadPart", "Partie de route", "IfcFacilityPart",
    [SPATIAL, "Structure spatiale", "Route"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A spatial structure element used to spatially decompose an IfcRoad "
    "into manageable parts (carriageway, shoulder, sidewalk, roundabout...).",
    "Élément de structure spatiale décomposant un IfcRoad en parties "
    "gérables (chaussée, accotement, trottoir, giratoire...).",
    ["Pset_RoadPartCommon"],
    {"fr": ["partie de route"], "en": ["road part"], "it": ["parte di strada"],
     "de": ["Straßenteil"]},
    [
        pt("CARRIAGEWAY", "4.3", "Unitary lateral part of road built for traffic, possibly with several traffic lanes and lay-bys.",
           "Chaussée : partie latérale unitaire de la route construite pour la circulation.",
           {"fr": ["chaussée"], "en": ["carriageway"], "it": ["carreggiata"], "de": ["Fahrbahn"]},
           new_in_43=True),
        pt("TRAFFICLANE", "4.3", "Lateral part of carriageway designated to vehicular traffic for a particular purpose.",
           "Voie de circulation : bande de chaussée dédiée à la circulation d'une file de véhicules.",
           {"fr": ["voie de circulation"], "en": ["traffic lane"], "it": ["corsia di marcia"],
            "de": ["Fahrstreifen"]}, new_in_43=True),
        pt("SHOULDER", "4.3", "A lateral part of road adjacent to the carriageway, not intended for vehicular traffic but usable in emergencies.",
           "Accotement : partie latérale non destinée à la circulation, utilisable en cas d'urgence.",
           {"fr": ["accotement"], "en": ["shoulder"], "it": ["banchina"], "de": ["Bankett"]},
           new_in_43=True),
        pt("HARDSHOULDER", "4.3", "A surfaced type of shoulder providing for safe use by vehicles in distress.",
           "Bande d'arrêt d'urgence : accotement revêtu pour l'usage des véhicules en difficulté.",
           {"fr": ["bande d'arrêt d'urgence"], "en": ["hard shoulder"], "it": ["corsia di emergenza"],
            "de": ["Befestigtes Bankett"]}, new_in_43=True),
        pt("SOFTSHOULDER", "4.3", "A type of shoulder that is not surfaced.",
           "Accotement non revêtu.",
           {"fr": ["accotement non revêtu"], "en": ["soft shoulder"], "it": ["banchina non pavimentata"],
            "de": ["Unbefestigtes Bankett"]}, new_in_43=True),
        pt("SIDEWALK", "4.3", "A footpath along the side of a road, normally separated from the vehicular section by a kerb.",
           "Trottoir : cheminement piéton le long de la route, séparé de la chaussée par une bordure.",
           {"fr": ["trottoir"], "en": ["sidewalk"], "it": ["marciapiede"], "de": ["Gehweg"]},
           new_in_43=True),
        pt("CENTRALRESERVE", "4.3", "Lateral road part separating two carriageways of the same road, or traffic lanes and sidewalk.",
           "Terre-plein central séparant deux chaussées d'une même route.",
           {"fr": ["terre-plein central"], "en": ["central reserve", "median"], "it": ["spartitraffico"],
            "de": ["Mittelstreifen"]}, new_in_43=True),
        pt("ROADWAYPLATEAU", "4.3", "Lateral part of road comprising the carriageway(s), shoulders and medians.",
           "Plateforme routière regroupant chaussée(s), accotements et terre-plein.",
           {"fr": ["plateforme routière"], "en": ["roadway platform"], "it": ["piattaforma stradale"],
            "de": ["Fahrbahnplattform"]}, new_in_43=True),
        pt("ROADSIDE", "4.3", "A lateral road part located along the road adjoining the outer edges of the shoulders.",
           "Abords de route : zone en dehors de la plateforme routière, hors circulation.",
           {"fr": ["abords de route"], "en": ["roadside"], "it": ["margine stradale"],
            "de": ["Straßenrand"]}, new_in_43=True),
        pt("ROADSIDEPART", "4.3", "A general concept for various parts of the roadside, e.g. side slopes, roadside ditches, back slopes.",
           "Partie latérale de bord de route (talus, fossé, contre-pente...).",
           {"fr": ["partie de bord de route"], "en": ["roadside part"], "it": ["parte del margine stradale"],
            "de": ["Straßenrandteil"]}, new_in_43=True),
        pt("ROUNDABOUT", "4.3", "Type of at-grade junction at which traffic streams are directed around a circle.",
           "Giratoire (rond-point) : carrefour où la circulation tourne autour d'un îlot central.",
           {"fr": ["giratoire", "rond-point"], "en": ["roundabout"], "it": ["rotatoria"],
            "de": ["Kreisverkehr"]}, new_in_43=True),
        pt("CENTRALISLAND", "4.3", "The center of a roundabout, not intended for traffic.",
           "Îlot central d'un giratoire.",
           {"fr": ["îlot central de giratoire"], "en": ["central island"], "it": ["isola centrale"],
            "de": ["Kreisverkehrsinsel"]}, new_in_43=True),
        pt("REFUGEISLAND", "4.3", "A raised platform or guarded area sited in the carriageway to divide traffic streams and provide refuge for pedestrians.",
           "Îlot refuge protégeant les piétons au milieu de la chaussée.",
           {"fr": ["îlot refuge"], "en": ["refuge island"], "it": ["isola spartitraffico"],
            "de": ["Verkehrsinsel"]}, new_in_43=True),
        pt("TRAFFICISLAND", "4.3", "A raised or marked area on the carriageway, typically at a junction, shaped to direct traffic and/or provide pedestrian refuge.",
           "Îlot directionnel, généralement à un carrefour, orientant la circulation.",
           {"fr": ["îlot directionnel"], "en": ["traffic island"], "it": ["isola direzionale"],
            "de": ["Verkehrslenkungsinsel"]}, new_in_43=True),
        pt("INTERSECTION", "4.3", "At-grade junction where two or more roads meet or cross.",
           "Carrefour : jonction à niveau où deux routes ou plus se rencontrent.",
           {"fr": ["carrefour"], "en": ["intersection"], "it": ["intersezione"], "de": ["Kreuzung"]},
           new_in_43=True),
        pt("RAILWAYCROSSING", "4.3", "At-grade crossing between road and railway.",
           "Passage à niveau entre une route et une voie ferrée.",
           {"fr": ["passage à niveau"], "en": ["railway level crossing"], "it": ["passaggio a livello"],
            "de": ["Bahnübergang"]}, new_in_43=True),
        pt("PEDESTRIAN_CROSSING", "4.3", "Designated level crossing over a road for pedestrians.",
           "Passage piéton, traversée aménagée pour les piétons.",
           {"fr": ["passage piéton"], "en": ["pedestrian crossing"], "it": ["attraversamento pedonale"],
            "de": ["Fußgängerüberweg"]}, new_in_43=True),
        pt("BICYCLECROSSING", "4.3", "Designated level crossing over a road for cyclists.",
           "Traversée cyclable aménagée.",
           {"fr": ["traversée cyclable"], "en": ["bicycle crossing"], "it": ["attraversamento ciclabile"],
            "de": ["Radwegüberquerung"]}, new_in_43=True),
        pt("PARKINGBAY", "4.3", "Lateral part of road for parking vehicles.",
           "Aire de stationnement en bordure de route.",
           {"fr": ["aire de stationnement"], "en": ["parking bay"], "it": ["area di sosta"],
            "de": ["Parkbucht"]}, new_in_43=True),
        pt("BUS_STOP", "4.3", "Lateral part of road for stopping buses, allowing them to draw out of the traffic lanes.",
           "Arrêt de bus, en retrait des voies de circulation.",
           {"fr": ["arrêt de bus"], "en": ["bus stop"], "it": ["fermata dell'autobus"],
            "de": ["Bushaltestelle"]}, new_in_43=True),
        pt("PASSINGBAY", "4.3", "A lateral part of a single-lane road that is a widening, allowing one vehicle to move over so another can pass.",
           "Aire de croisement, élargissement ponctuel d'une route à voie unique.",
           {"fr": ["aire de croisement"], "en": ["passing bay"], "it": ["piazzola di incrocio"],
            "de": ["Ausweichstelle"]}, new_in_43=True),
        pt("LAYBY", "4.3", "A lateral part of road where vehicles can divert from the ordinary stream of traffic.",
           "Aire de repos latérale, où les véhicules peuvent s'écarter de la circulation.",
           {"fr": ["aire de repos latérale"], "en": ["layby"], "it": ["piazzola di sosta"],
            "de": ["Rastplatz"]}, new_in_43=True),
        pt("TOLLPLAZA", "4.3", "A part of a road facility where tolls are collected for use of a toll road, tunnel or bridge.",
           "Gare de péage où les péages sont collectés.",
           {"fr": ["gare de péage"], "en": ["toll plaza"], "it": ["stazione di pedaggio"],
            "de": ["Mautstelle"]}, new_in_43=True),
        pt("ROADSEGMENT", "4.3", "A longitudinal, linear segment of a road, defined by uniform characteristics or as a transition segment.",
           "Tronçon longitudinal de route, à caractéristiques uniformes ou de transition.",
           {"fr": ["tronçon de route"], "en": ["road segment"], "it": ["segmento stradale"],
            "de": ["Straßenabschnitt"]}, new_in_43=True),
    ],
    notes_fr="",
    version_notes="Nouveau en IFC4.3 (extension infrastructure routière).",
))

DATA.append(entry(
    "IfcRailway", "Voie ferrée (structure spatiale)", "IfcFacility",
    [SPATIAL, "Structure spatiale", "Voie ferrée"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A spatial structure element representing a route for the guided "
    "passage of wheeled vehicles on rails, supporting the breakdown of a "
    "railway project into manageable parts.",
    "Élément de structure spatiale représentant un itinéraire pour le "
    "passage guidé de véhicules sur rails, structurant un projet "
    "ferroviaire en parties gérables.",
    ["Pset_RailwayCommon"],
    {"fr": ["voie ferrée", "ligne ferroviaire", "chemin de fer", "projet ferroviaire"],
     "en": ["railway"], "it": ["ferrovia"], "de": ["Eisenbahn", "Bahnstrecke"]},
    [pt("NOTDEFINED", "4.3", "Undefined railway type.", "Type non précisé.", {}, new_in_43=True)],
    notes_fr="",
    version_notes="Nouveau en IFC4.3 (extension infrastructure ferroviaire).",
))

DATA.append(entry(
    "IfcRailwayPart", "Partie de voie ferrée", "IfcFacilityPart",
    [SPATIAL, "Structure spatiale", "Voie ferrée"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A spatial structure element used to spatially organise a railway line "
    "(track, line-side, substructure, above-track), vertically and/or "
    "longitudinally.",
    "Élément de structure spatiale organisant une ligne ferroviaire (voie, "
    "abords, plateforme, zone caténaire), verticalement et/ou "
    "longitudinalement.",
    ["Pset_RailwayPartCommon"],
    {"fr": ["partie de voie ferrée"], "en": ["railway part"], "it": ["parte di ferrovia"],
     "de": ["Bahnteil"]},
    [
        pt("TRACK", "4.3", "A spatial structure element containing track-related elements, e.g. rails and sleepers.",
           "Voie : élément spatial regroupant les éléments de voie (rails, traverses...).",
           {"fr": ["voie"], "en": ["track"], "it": ["binario"], "de": ["Gleis"]}, new_in_43=True),
        pt("PLAINTRACK", "4.3", "A spatial structure element further dividing a track; does not contain turnout or dilatation panels.",
           "Voie courante : partie de voie sans appareil de voie ni joint de dilatation.",
           {"fr": ["voie courante"], "en": ["plain track"], "it": ["binario semplice"],
            "de": ["Freie Strecke"]}, new_in_43=True),
        pt("TURNOUTTRACK", "4.3", "A spatial structure element further dividing a track; contains turnouts (switches).",
           "Zone d'appareil de voie (aiguillage).",
           {"fr": ["zone d'aiguillage"], "en": ["turnout track"], "it": ["zona di scambio"],
            "de": ["Weichenbereich"]}, new_in_43=True),
        pt("DILATIONTRACK", "4.3", "A spatial structure element used at points where expansions or movements of tracks need to be accommodated (e.g. near a bridge).",
           "Zone de joint de dilatation de voie, où les mouvements de la voie doivent être absorbés.",
           {"fr": ["zone de joint de dilatation"], "en": ["dilatation track"], "it": ["zona di dilatazione"],
            "de": ["Dilatationsbereich"]}, new_in_43=True),
        pt("TRACKPART", "4.3", "A spatial structure element further dividing a track for purposes not covered by plain/turnout/dilatation track.",
           "Partie générique de voie, pour un usage non couvert par les autres catégories.",
           {"fr": ["partie générique de voie"], "en": ["track part"], "it": ["parte del binario"],
            "de": ["Gleisteil"]}, new_in_43=True),
        pt("LINESIDE", "4.3", "A spatial structure element containing elements of the railway not in or over the tracks.",
           "Abords de voie : éléments ferroviaires situés en dehors de l'emprise de la voie.",
           {"fr": ["abords de voie"], "en": ["line-side"], "it": ["margine della linea"],
            "de": ["Streckenrand"]}, new_in_43=True),
        pt("LINESIDEPART", "4.3", "A spatial structure element further dividing a line-side part into manageable volumes.",
           "Partie d'abords de voie, subdivision d'une zone d'abords de voie.",
           {"fr": ["partie d'abords de voie"], "en": ["line-side part"], "it": ["parte del margine linea"],
            "de": ["Streckenrandteil"]}, new_in_43=True),
        pt("ABOVETRACK", "4.3", "A spatial structure element containing elements positioned above or over the track, e.g. catenary lines.",
           "Zone au-dessus de la voie, contenant les éléments aériens (caténaire...).",
           {"fr": ["zone au-dessus de la voie", "zone caténaire"], "en": ["above-track zone"],
            "it": ["zona sopra il binario"], "de": ["Bereich über dem Gleis"]}, new_in_43=True),
        pt("SUBSTRUCTURE", "4.3", "A spatial structure element containing elements positioned below the track, e.g. earthwork platform, subgrade, embankment.",
           "Plateforme : infrastructure sous voie (terrassement, plateforme support, remblai).",
           {"fr": ["plateforme (infrastructure sous voie)"], "en": ["substructure"], "it": ["sottostruttura"],
            "de": ["Unterbau"]}, new_in_43=True),
    ],
    notes_fr="",
    version_notes="Nouveau en IFC4.3 (extension infrastructure ferroviaire).",
))

DATA.append(entry(
    "IfcBridge", "Pont (structure spatiale)", "IfcFacility",
    [SPATIAL, "Structure spatiale", "Pont"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A civil engineering works that allows passage over obstacles (water, "
    "valleys, roads, railways) by spanning them, classified per its "
    "primary structural typology.",
    "Ouvrage de génie civil permettant le franchissement d'un obstacle "
    "(cours d'eau, vallée, route, voie ferrée), classé selon sa typologie "
    "structurelle principale.",
    ["Pset_BridgeCommon"],
    {"fr": ["pont", "ouvrage d'art", "projet de pont"], "en": ["bridge"], "it": ["ponte"],
     "de": ["Brücke"]},
    [
        pt("ARCHED", "4.3", "A bridge that has one or more arches as its main structure.",
           "Pont en arc, dont la structure principale est constituée d'un ou plusieurs arcs.",
           {"fr": ["pont en arc"], "en": ["arch bridge"], "it": ["ponte ad arco"],
            "de": ["Bogenbrücke"]}, new_in_43=True),
        pt("CABLE_STAYED", "4.3", "A bridge with one or more towers and inclined cables connected to the tower, supporting the deck.",
           "Pont à haubans, où le tablier est suspendu par des câbles inclinés reliés à un ou plusieurs pylônes.",
           {"fr": ["pont à haubans"], "en": ["cable-stayed bridge"], "it": ["ponte strallato"],
            "de": ["Schrägseilbrücke"]}, new_in_43=True),
        pt("SUSPENSION", "4.3", "A bridge whose main structural members are catenary cables from which the deck is suspended.",
           "Pont suspendu, dont le tablier est suspendu à des câbles porteurs en caténaire.",
           {"fr": ["pont suspendu"], "en": ["suspension bridge"], "it": ["ponte sospeso"],
            "de": ["Hängebrücke"]}, new_in_43=True),
        pt("CANTILEVER", "4.3", "A bridge whose main structural members are cantilevers.",
           "Pont en encorbellement (cantilever).",
           {"fr": ["pont en encorbellement"], "en": ["cantilever bridge"], "it": ["ponte a sbalzo"],
            "de": ["Auslegerbrücke"]}, new_in_43=True),
        pt("GIRDER", "4.3", "A bridge that uses girders as the means of supporting its deck.",
           "Pont à poutres, dont le tablier est supporté par des poutres.",
           {"fr": ["pont à poutres"], "en": ["girder bridge"], "it": ["ponte a travata"],
            "de": ["Balkenbrücke"]}, new_in_43=True),
        pt("TRUSS", "4.3", "A bridge with a braced triangulated frame designed to act as a beam.",
           "Pont à treillis, structure triangulée contreventée agissant comme une poutre.",
           {"fr": ["pont à treillis"], "en": ["truss bridge"], "it": ["ponte a traliccio"],
            "de": ["Fachwerkbrücke"]}, new_in_43=True),
        pt("FRAMEWORK", "4.3", "A framework bridge, whose structure is a rigid portal frame.",
           "Pont à structure en portique (cadre rigide).",
           {"fr": ["pont-cadre", "pont en portique"], "en": ["framework bridge"], "it": ["ponte a telaio"],
            "de": ["Rahmenbrücke"]}, new_in_43=True),
        pt("CULVERT", "4.3", "A transverse drain or waterway construction under a road, railway or canal, or through an embankment.",
           "Ponceau ou buse : ouvrage de franchissement transversal sous une route, une voie ferrée ou un remblai.",
           {"fr": ["ponceau", "buse de franchissement"], "en": ["culvert bridge"], "it": ["tombino stradale"],
            "de": ["Durchlassbrücke"]}, new_in_43=True),
    ],
    notes_fr="Les prédéfinis de tablier/pile/culée s'expriment via "
             "IfcBridgePart, tandis que les éléments structurels détaillés "
             "(poutres, piles, plaques...) restent modélisés avec IfcBeam, "
             "IfcColumn, IfcPlate etc., déjà enrichis de PredefinedType "
             "spécifiques aux ponts (ex. IfcBeam.PIERCAP, IfcColumn.PIERSTEM).",
    version_notes="Nouveau en IFC4.3 (extension infrastructure — ouvrages d'art).",
))

DATA.append(entry(
    "IfcBridgePart", "Partie de pont", "IfcFacilityPart",
    [SPATIAL, "Structure spatiale", "Pont"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A spatial structure element used to spatially decompose an IfcBridge "
    "into manageable parts (abutment, deck, pier, pylon, sub/superstructure).",
    "Élément de structure spatiale décomposant un IfcBridge en parties "
    "gérables (culée, tablier, pile, pylône, infra/superstructure).",
    ["Pset_BridgePartCommon"],
    {"fr": ["partie de pont"], "en": ["bridge part"], "it": ["parte di ponte"],
     "de": ["Brückenteil"]},
    [
        pt("ABUTMENT", "4.3", "The substructure at the ends of a bridge, supporting its superstructure (wing walls, head wall, stem wall, cone).",
           "Culée : appui d'extrémité du pont, supportant la superstructure.",
           {"fr": ["culée"], "en": ["abutment"], "it": ["spalla"], "de": ["Widerlager"]},
           new_in_43=True),
        pt("PIER", "4.3", "A structure extending to the ground or into water, supporting the bridge superstructure and transferring loads to the foundation.",
           "Pile : appui intermédiaire du pont, transmettant les charges à la fondation.",
           {"fr": ["pile de pont"], "en": ["pier"], "it": ["pila"], "de": ["Pfeiler"]},
           new_in_43=True),
        pt("PIER_SEGMENT", "4.3", "A segment of a bridge pier; segments may be separated by construction or expansion joints.",
           "Tronçon de pile de pont, séparé par des joints de construction ou de dilatation.",
           {"fr": ["tronçon de pile"], "en": ["pier segment"], "it": ["segmento della pila"],
            "de": ["Pfeilersegment"]}, new_in_43=True),
        pt("DECK", "4.3", "The bridge deck comprises the elements used for conveying traffic, not performing structural functions of the superstructure.",
           "Tablier : partie du pont dédiée à la circulation, sans fonction structurelle propre de superstructure.",
           {"fr": ["tablier"], "en": ["deck"], "it": ["impalcato"], "de": ["Fahrbahnplatte"]},
           new_in_43=True),
        pt("DECK_SEGMENT", "4.3", "A segment of the bridge deck; segments may be separated by construction or expansion joints.",
           "Tronçon de tablier, séparé par des joints de construction ou de dilatation.",
           {"fr": ["tronçon de tablier"], "en": ["deck segment"], "it": ["segmento dell'impalcato"],
            "de": ["Fahrbahnsegment"]}, new_in_43=True),
        pt("FOUNDATION", "4.3", "Structural elements that support and anchor the bridge to the ground, transmitting all loads to the supporting strata.",
           "Fondation de pont, transmettant les charges au sol porteur.",
           {"fr": ["fondation de pont"], "en": ["bridge foundation"], "it": ["fondazione del ponte"],
            "de": ["Brückenfundament"]}, new_in_43=True),
        pt("PYLON", "4.3", "A vertical structure supporting cables in suspended or stayed structures.",
           "Pylône supportant les câbles d'un pont suspendu ou à haubans.",
           {"fr": ["pylône"], "en": ["pylon"], "it": ["pilone"], "de": ["Pylon"]}, new_in_43=True),
        pt("SUBSTRUCTURE", "4.3", "The elements that transfer loads to the ground; includes abutments and piers.",
           "Infrastructure : ensemble des éléments transmettant les charges au sol (culées, piles).",
           {"fr": ["infrastructure (partie basse)"], "en": ["substructure"], "it": ["sottostruttura"],
            "de": ["Unterbau (Brücke)"]}, new_in_43=True),
        pt("SUPERSTRUCTURE", "4.3", "The part of the bridge that spans horizontally and transfers the traffic load to the bridge substructures.",
           "Superstructure : partie du pont qui franchit l'obstacle et transmet les charges à l'infrastructure.",
           {"fr": ["superstructure (partie haute)"], "en": ["superstructure"], "it": ["sovrastruttura"],
            "de": ["Überbau"]}, new_in_43=True),
        pt("SURFACESTRUCTURE", "4.3", "A structural part of the bridge represented as a surface (planar) structural element, as distinct from the substructure/superstructure grouping.",
           "Élément structurel de pont représenté comme une structure surfacique (planaire), par opposition au regroupement infrastructure/superstructure.",
           {"fr": ["structure surfacique"], "en": ["surface structure"], "it": ["struttura superficiale"],
            "de": ["Flächentragwerk"]}, new_in_43=True),
    ],
    notes_fr="",
    version_notes="Nouveau en IFC4.3 (extension infrastructure — ouvrages d'art).",
))

# ---------------------------------------------------------------------------

def build_children_index(data):
    for d in data:
        d["children"] = sorted([c["class"] for c in data if c["parent"] == d["class"]])
    return data


def main():
    data = build_children_index(DATA)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"schema_version": "IFC4X3_ADD2", "classes": data}, f,
                   ensure_ascii=False, indent=2)
    print(f"Écrit {len(data)} classes dans {OUT_PATH}")


if __name__ == "__main__":
    main()
