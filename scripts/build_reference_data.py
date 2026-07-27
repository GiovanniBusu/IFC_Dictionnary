#!/usr/bin/env python3
"""
Génère data/ifc_reference.json à partir du référentiel curé ci-dessous.

Ce script correspond à l'étape de constitution MANUELLE du référentiel
(section 9.1 des livrables). Il couvre un sous-ensemble représentatif du
schéma IFC4X3_ADD2 (~40 classes / familles), choisi pour illustrer toutes
les situations demandées : structure, architecture, CVC/plomberie/électricité,
mobilier, éléments spatiaux et génie civil (nouveautés IFC4.3), y compris des
cas de dépréciation (IfcWallStandardCase) et de renommage/ajout en 4.3.

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
        pt("STANDARD", "4.0", "A standard wall.", "Mur standard, à section constante.",
           {"fr": ["mur standard", "mur droit"], "en": ["standard wall"],
            "it": ["muro standard"], "de": ["Standardwand"]}),
        pt("SHEAR", "4.0", "A wall meant to structurally resist lateral (shear) forces.",
           "Mur de contreventement (voile porteur) résistant aux efforts horizontaux.",
           {"fr": ["voile de contreventement", "voile béton", "mur de refend"],
            "en": ["shear wall"], "it": ["muro di controventamento"],
            "de": ["Aussteifungswand", "Schubwand"]}),
        pt("PARAPET", "4.0", "A low protective wall (e.g. at a roof edge or balcony).",
           "Muret de protection en bordure de toiture ou de balcon.",
           {"fr": ["parapet", "muret"], "en": ["parapet wall"], "it": ["parapetto"],
            "de": ["Brüstung"]}),
        pt("PARTITIONING", "4.0", "A non load-bearing dividing wall.",
           "Cloison de distribution, non porteuse.",
           {"fr": ["cloison"], "en": ["partition wall"], "it": ["parete divisoria"],
            "de": ["Trennwand"]}),
        pt("ELEMENTEDWALL", "4.0", "A wall assembled from prefabricated elements.",
           "Mur composé d'éléments préfabriqués assemblés.",
           {"fr": ["mur élémenté", "mur préfabriqué"], "en": ["elemented wall"],
            "it": ["muro prefabbricato"], "de": ["Elementwand"]}),
    ],
    notes_fr="Si le mur est un simple habillage sans fonction porteuse ni "
             "cloisonnement (ex. mur rideau autoportant), envisager IfcCurtainWall. "
             "Pour un mur générique modélisé en géométrie brute (proxy), voir "
             "IfcBuildingElementProxy.",
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
        pt("COLUMN", "4.0", "A standard column.", "Poteau standard.",
           {"fr": ["poteau standard"], "en": ["standard column"],
            "it": ["pilastro standard"], "de": ["Standardstütze"]}),
        pt("PILASTER", "4.0", "A column integrated into a wall, projecting slightly.",
           "Pilastre engagé dans un mur, en léger relief.",
           {"fr": ["pilastre"], "en": ["pilaster"], "it": ["lesena", "pilastro murato"],
            "de": ["Pilaster", "Wandpfeiler"]}),
    ],
    notes_fr="Un poteau purement décoratif en façade (sans fonction porteuse "
             "réelle) reste néanmoins classé IfcColumn si l'intention de "
             "conception est structurelle ; sinon envisager IfcBuildingElementProxy.",
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
        pt("BEAM", "4.0", "A standard beam.", "Poutre standard.",
           {"fr": ["poutre standard"], "en": ["standard beam"], "it": ["trave standard"],
            "de": ["Standardbalken"]}),
        pt("JOIST", "4.0", "A small beam supporting a floor or roof deck.",
           "Solive supportant un plancher ou une couverture.",
           {"fr": ["solive"], "en": ["joist"], "it": ["travetto"], "de": ["Deckenbalken"]}),
        pt("LINTEL", "4.0", "A beam spanning an opening (door/window).",
           "Linteau au-dessus d'une baie (porte, fenêtre).",
           {"fr": ["linteau"], "en": ["lintel"], "it": ["architrave"], "de": ["Sturz"]}),
        pt("GIRDER_SEGMENT", "4.3", "A segment of a large primary beam (e.g. a bridge girder).",
           "Tronçon de poutre maîtresse, notamment pour ouvrages d'art (ponts).",
           {"fr": ["poutre maîtresse", "tronçon de poutre de pont"],
            "en": ["girder segment"], "it": ["segmento di trave principale"],
            "de": ["Trägersegment"]}, new_in_43=True),
        pt("DIAPHRAGM", "4.3", "A transverse beam stiffening a bridge deck structure.",
           "Entretoise transversale raidissant un tablier de pont.",
           {"fr": ["entretoise de pont"], "en": ["diaphragm beam"],
            "it": ["diaframma trasversale"], "de": ["Querträger"]}, new_in_43=True),
    ],
    notes_fr="Attention à la confusion avec IfcMember : IfcBeam désigne un "
             "élément fléchi principal (structure primaire), IfcMember couvre "
             "les éléments linéaires secondaires (raidisseurs, entretoises "
             "légères, montants).",
))

DATA.append(entry(
    "IfcMember", "Membrure / Élément linéaire", "IfcBuildingElement",
    [PHYS, BLDG, "Charpente et éléments linéaires"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A 1-dimensional structural member, often part of a structural frame, "
    "not otherwise classified as beam or column (e.g. brace, purlin, "
    "stiffener).",
    "Élément linéaire structurel secondaire, non classé comme poutre ou "
    "poteau (contreventement, panne, raidisseur, montant...).",
    ["Pset_MemberCommon"],
    {"fr": ["membrure", "élément linéaire", "barre"], "en": ["member"],
     "it": ["asta", "elemento lineare"], "de": ["Bauteilstab"]},
    [
        pt("STIFFENING_MEMBER", "4.0",
           "A slender member added to prevent buckling or increase local "
           "stiffness of a plated or framed structure.",
           "Élément linéaire destiné à empêcher le flambement ou à "
           "renforcer localement la rigidité d'une structure (plaque, "
           "profilé, âme de poutre) : un raidisseur.",
           {"fr": ["raidisseur", "raidisseur d'âme", "nervure de raidissage"],
            "en": ["stiffener", "stiffening member"],
            "it": ["irrigidimento", "traversa di irrigidimento", "nervatura di rinforzo"],
            "de": ["Aussteifungsstab", "Steife", "Versteifungsrippe", "Aussteifung"]}),
        pt("BRACE", "4.0", "A member providing diagonal bracing/stability.",
           "Barre de contreventement diagonal.",
           {"fr": ["contreventement", "diagonale", "barre de stabilisation"],
            "en": ["brace", "bracing member"], "it": ["controvento", "diagonale"],
            "de": ["Verband", "Diagonalstab"]}),
        pt("PURLIN", "4.0", "A horizontal member supporting roof cladding between rafters.",
           "Panne supportant la couverture de toiture entre chevrons/fermes.",
           {"fr": ["panne"], "en": ["purlin"], "it": ["arcareccio"], "de": ["Pfette"]}),
        pt("RAFTER", "4.0", "An inclined member supporting a roof.",
           "Chevron ou arbalétrier de charpente de toiture.",
           {"fr": ["chevron", "arbalétrier"], "en": ["rafter"], "it": ["puntone", "corrente"],
            "de": ["Sparren"]}),
        pt("MULLION", "4.0", "A vertical member dividing a window/curtain wall panel.",
           "Meneau vertical divisant une baie ou un mur rideau.",
           {"fr": ["meneau"], "en": ["mullion"], "it": ["montante"], "de": ["Pfosten"]}),
        pt("STUD", "4.0", "A vertical light-frame member (e.g. in a stud wall).",
           "Montant vertical d'ossature légère (bois ou métal).",
           {"fr": ["montant d'ossature", "montant"], "en": ["stud"],
            "it": ["montante di parete"], "de": ["Ständer"]}),
        pt("COLLAR", "4.0", "A horizontal tie member near the ridge of a roof truss.",
           "Entrait retroussé reliant deux arbalétriers d'une ferme.",
           {"fr": ["entrait retroussé"], "en": ["collar tie"], "it": ["catena alta"],
            "de": ["Kehlbalken"]}),
    ],
    notes_fr="Cas ambigu fréquent : un « raidisseur » modélisé sans détail de "
             "profilé réel (juste une boîte englobante) est parfois classé "
             "IfcBuildingElementProxy par les logiciels de charpente métallique. "
             "Si l'analyse structurelle est le but, préférer IfcMember + "
             "STIFFENING_MEMBER, qui porte l'information sémantique correcte.",
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
        pt("FLOOR", "4.0", "A slab used as a floor.", "Dalle de plancher courant.",
           {"fr": ["dalle de plancher", "plancher"], "en": ["floor slab"],
            "it": ["solaio di piano"], "de": ["Geschossdecke"]}),
        pt("ROOF", "4.0", "A slab used as a (flat) roof.", "Dalle de toiture-terrasse.",
           {"fr": ["dalle de toiture", "toiture-terrasse"], "en": ["roof slab"],
            "it": ["soletta di copertura"], "de": ["Dachplatte"]}),
        pt("LANDING", "4.0", "A slab forming a landing between stair flights.",
           "Palier de circulation entre volées d'escalier.",
           {"fr": ["palier"], "en": ["landing slab"], "it": ["pianerottolo"],
            "de": ["Podest"]}),
        pt("BASESLAB", "4.0", "A slab in contact with the ground (raft/mat foundation).",
           "Radier ou dalle sur terre-plein en contact avec le sol.",
           {"fr": ["radier", "dalle sur sol", "dalle de fondation"],
            "en": ["base slab", "mat foundation"], "it": ["platea di fondazione"],
            "de": ["Bodenplatte"]}),
        pt("PAVING", "4.3", "An outdoor paving slab.", "Dalle de revêtement extérieur (pavage).",
           {"fr": ["dalle de pavage", "dallage extérieur"], "en": ["paving slab"],
            "it": ["lastra di pavimentazione"], "de": ["Pflasterplatte"]}, new_in_43=True),
    ],
    notes_fr="Une chape mince rapportée sur une dalle structurelle n'est pas "
             "une IfcSlab mais un IfcCovering (PredefinedType=SCREED).",
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
        pt("PAD_FOOTING", "4.0", "An isolated pad footing under a column.",
           "Semelle isolée sous poteau.",
           {"fr": ["semelle isolée", "plot de fondation"], "en": ["pad footing"],
            "it": ["plinto isolato"], "de": ["Einzelfundament"]}),
        pt("STRIP_FOOTING", "4.0", "A continuous strip footing under a wall.",
           "Semelle filante sous mur.",
           {"fr": ["semelle filante"], "en": ["strip footing"], "it": ["fondazione a nastro"],
            "de": ["Streifenfundament"]}),
        pt("PILE_CAP", "4.0", "A footing distributing loads onto a group of piles.",
           "Semelle de répartition sur groupe de pieux.",
           {"fr": ["semelle sur pieux"], "en": ["pile cap"], "it": ["plinto su pali"],
            "de": ["Pfahlkopfplatte"]}),
    ],
    notes_fr="",
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
        pt("DRIVEN", "4.0", "A pile installed by driving (hammering).", "Pieu battu.",
           {"fr": ["pieu battu"], "en": ["driven pile"], "it": ["palo battuto"],
            "de": ["Rammpfahl"]}),
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
        pt("CURTAIN_PANEL", "4.0", "A panel infill of a curtain wall.",
           "Panneau de remplissage d'un mur rideau.",
           {"fr": ["panneau de mur rideau"], "en": ["curtain wall panel"],
            "it": ["pannello di facciata continua"], "de": ["Fassadenpaneel"]}),
        pt("SHEET", "4.0", "A thin sheet plate (e.g. gusset plate).",
           "Plaque mince, ex. gousset d'assemblage métallique.",
           {"fr": ["gousset", "plaque d'assemblage"], "en": ["gusset plate"],
            "it": ["piastra di collegamento"], "de": ["Knotenblech"]}),
    ],
    notes_fr="",
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
        pt("FLAT_ROOF", "4.0", "A flat roof.", "Toiture plate/terrasse.",
           {"fr": ["toiture plate", "toit plat"], "en": ["flat roof"],
            "it": ["tetto piano"], "de": ["Flachdach"]}),
        pt("GABLE_ROOF", "4.0", "A roof with two sloping sides meeting at a ridge.",
           "Toiture à deux pans (pignon).",
           {"fr": ["toit à deux pans", "toiture à pignon"], "en": ["gable roof"],
            "it": ["tetto a due falde"], "de": ["Satteldach"]}),
        pt("HIP_ROOF", "4.0", "A roof with sloping sides on all faces.",
           "Toiture à quatre pans (croupe).",
           {"fr": ["toit à quatre pans", "toiture en croupe"], "en": ["hip roof"],
            "it": ["tetto a padiglione"], "de": ["Walmdach"]}),
        pt("SHED_ROOF", "4.0", "A single-sloped roof.", "Toiture à un seul pan (appentis).",
           {"fr": ["toit en appentis", "monopente"], "en": ["shed roof", "lean-to roof"],
            "it": ["tetto a una falda"], "de": ["Pultdach"]}),
    ],
    notes_fr="IfcRoof sert souvent de conteneur logique ; les surfaces de "
             "couverture proprement dites peuvent être modélisées comme "
             "IfcSlab (ROOF) et/ou IfcCovering (ROOFING).",
))

DATA.append(entry(
    "IfcReinforcingBar", "Armature (barre)", "IfcElementComponent",
    [PHYS, BLDG, "Armatures et précontrainte"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "Steel reinforcing bar, typically used to reinforce concrete.",
    "Barre d'acier utilisée pour armer le béton.",
    ["Pset_ReinforcingBarCommon"],
    {"fr": ["armature", "fer à béton", "barre d'armature"], "en": ["rebar", "reinforcing bar"],
     "it": ["armatura", "ferro d'armatura"], "de": ["Bewehrungsstab"]},
    [
        pt("MAIN", "4.0", "Main longitudinal reinforcement.", "Armature principale longitudinale.",
           {"fr": ["armature principale"], "en": ["main bar"], "it": ["armatura principale"],
            "de": ["Hauptbewehrung"]}),
        pt("STIRRUP", "4.0", "Shear reinforcement wrapping around main bars.",
           "Cadre/étrier d'armature transversale.",
           {"fr": ["étrier", "cadre d'armature"], "en": ["stirrup"], "it": ["staffa"],
            "de": ["Bügel"]}),
        pt("SHEAR", "4.0", "Reinforcement resisting shear forces.",
           "Armature d'effort tranchant.",
           {"fr": ["armature d'effort tranchant"], "en": ["shear reinforcement"],
            "it": ["armatura a taglio"], "de": ["Schubbewehrung"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcReinforcingMesh", "Treillis d'armature", "IfcElementComponent",
    [PHYS, BLDG, "Armatures et précontrainte"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A reinforcing mesh (welded fabric) used to reinforce concrete.",
    "Treillis soudé utilisé pour armer le béton.",
    ["Pset_ReinforcingMeshCommon"],
    {"fr": ["treillis soudé", "panneau de treillis"], "en": ["reinforcing mesh", "welded fabric"],
     "it": ["rete elettrosaldata"], "de": ["Bewehrungsmatte"]},
    [pt("NOTDEFINED", "2x3", "Undefined.", "Non précisé.", {})],
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
        pt("STRAND", "4.0", "A tendon made of a strand.", "Câble constitué de torons.",
           {"fr": ["toron"], "en": ["strand"], "it": ["trefolo"], "de": ["Litze"]}),
        pt("BAR", "4.0", "A tendon made of a solid bar.", "Barre de précontrainte pleine.",
           {"fr": ["barre de précontrainte"], "en": ["tendon bar"], "it": ["barra di precompressione"],
            "de": ["Spannstab"]}),
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
        pt("HANDRAIL", "4.0", "A railing serving as a handrail (grip) only.",
           "Main courante seule.",
           {"fr": ["main courante"], "en": ["handrail"], "it": ["corrimano"],
            "de": ["Handlauf"]}),
        pt("GUARDRAIL", "4.0", "A railing preventing falls (protective barrier).",
           "Garde-corps de protection contre les chutes.",
           {"fr": ["garde-corps de sécurité", "barrière de protection"],
            "en": ["guardrail"], "it": ["parapetto di sicurezza"], "de": ["Absturzsicherung"]}),
        pt("BALUSTRADE", "4.0", "A railing composed of a series of balusters.",
           "Balustrade composée d'une série de balustres.",
           {"fr": ["balustrade"], "en": ["balustrade"], "it": ["balaustra"], "de": ["Balustrade"]}),
    ],
    notes_fr="Le raidisseur d'un garde-corps préfabriqué (renfort de montant) "
             "relève lui d'IfcMember (STIFFENING_MEMBER), pas d'IfcRailing.",
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
    "landings.",
    "Ouvrage de circulation verticale permettant de passer d'un niveau à "
    "l'autre, souvent une agrégation de volées et paliers.",
    ["Pset_StairCommon"],
    {"fr": ["escalier"], "en": ["stair", "staircase"], "it": ["scala"],
     "de": ["Treppe"]},
    [
        pt("STRAIGHT_RUN_STAIR", "4.0", "A stair with a single straight flight.",
           "Escalier droit, à volée unique.",
           {"fr": ["escalier droit"], "en": ["straight stair"], "it": ["scala rettilinea"],
            "de": ["Gerade Treppe"]}),
        pt("SPIRAL_STAIR", "4.0", "A stair winding around a central point/newel.",
           "Escalier hélicoïdal (colimaçon) autour d'un noyau central.",
           {"fr": ["escalier en colimaçon", "escalier hélicoïdal"], "en": ["spiral stair"],
            "it": ["scala a chiocciola"], "de": ["Spindeltreppe", "Wendeltreppe"]}),
        pt("TWO_STRAIGHT_RUN_STAIR", "4.0", "A stair with two straight flights and a landing.",
           "Escalier à deux volées droites avec palier intermédiaire.",
           {"fr": ["escalier à deux volées"], "en": ["dog-leg stair"],
            "it": ["scala a due rampe"], "de": ["Zweiläufige Treppe"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcStairFlight", "Volée d'escalier", "IfcBuildingElement",
    [PHYS, BLDG, "Circulations verticales"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A part of a stair without a turn or change in direction, consisting "
    "of steps.",
    "Partie rectiligne d'un escalier, sans changement de direction, "
    "composée de marches.",
    ["Pset_StairFlightCommon"],
    {"fr": ["volée d'escalier", "volée"], "en": ["stair flight"], "it": ["rampa di scala"],
     "de": ["Treppenlauf"]},
    [pt("NOTDEFINED", "2x3", "Undefined.", "Non précisé.", {})],
    notes_fr="",
))

DATA.append(entry(
    "IfcRamp", "Rampe", "IfcBuildingElement",
    [PHYS, BLDG, "Circulations verticales"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A vertical passageway which provides a means of moving between "
    "different levels using a sloped surface (aggregation of ramp flights).",
    "Ouvrage de circulation verticale à plan incliné (accès PMR, véhicules...).",
    ["Pset_RampCommon"],
    {"fr": ["rampe d'accès", "rampe"], "en": ["ramp"], "it": ["rampa"], "de": ["Rampe"]},
    [
        pt("STRAIGHT_RUN_RAMP", "4.0", "A ramp with a single straight run.",
           "Rampe droite à volée unique.",
           {"fr": ["rampe droite"], "en": ["straight ramp"], "it": ["rampa rettilinea"],
            "de": ["Gerade Rampe"]}),
        pt("SPIRAL_RAMP", "4.0", "A ramp winding around a central point.",
           "Rampe hélicoïdale.",
           {"fr": ["rampe hélicoïdale"], "en": ["spiral ramp"], "it": ["rampa elicoidale"],
            "de": ["Wendelrampe"]}),
    ],
    notes_fr="",
))

DATA.append(entry(
    "IfcRampFlight", "Volée de rampe", "IfcBuildingElement",
    [PHYS, BLDG, "Circulations verticales"],
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A part of a ramp without a turn, forming a single sloped plane.",
    "Partie rectiligne d'une rampe, à pente unique.",
    ["Pset_RampFlightCommon"],
    {"fr": ["volée de rampe"], "en": ["ramp flight"], "it": ["rampa lineare"],
     "de": ["Rampenlauf"]},
    [pt("NOTDEFINED", "2x3", "Undefined.", "Non précisé.", {})],
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
    notes_fr="Les meneaux/traverses de mur rideau sont modélisés en "
             "IfcMember (MULLION), les panneaux en IfcPlate (CURTAIN_PANEL).",
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
        pt("DOOR", "4.0", "A standard door.", "Porte standard.",
           {"fr": ["porte standard"], "en": ["standard door"], "it": ["porta standard"],
            "de": ["Standardtür"]}),
        pt("GATE", "4.0", "A door used as a gate (e.g. vehicular access).",
           "Portail (accès véhicules, clôture).",
           {"fr": ["portail"], "en": ["gate"], "it": ["cancello"], "de": ["Tor"]}),
        pt("TRAPDOOR", "4.0", "A door installed in a floor or ceiling.",
           "Trappe (accès horizontal, plancher/plafond).",
           {"fr": ["trappe"], "en": ["trapdoor", "hatch"], "it": ["botola"], "de": ["Falltür"]}),
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
        pt("WINDOW", "4.0", "A standard window.", "Fenêtre standard.",
           {"fr": ["fenêtre standard"], "en": ["standard window"], "it": ["finestra standard"],
            "de": ["Standardfenster"]}),
        pt("SKYLIGHT", "4.0", "A window installed in a roof.", "Fenêtre de toit (velux).",
           {"fr": ["fenêtre de toit", "velux"], "en": ["skylight"], "it": ["lucernario"],
            "de": ["Dachfenster"]}),
        pt("LIGHTDOME", "4.0", "A dome-shaped rooflight.", "Dôme (coupole) d'éclairage zénithal.",
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
        pt("SCREED", "4.0", "A thin layer applied to level or finish a surface (e.g. floor screed).",
           "Couche mince rapportée pour niveler ou finir une surface (chape).",
           {"fr": ["chape", "chape de ragréage", "chape flottante"], "en": ["screed"],
            "it": ["massetto"], "de": ["Estrich"]}),
        pt("MOLDING", "4.0", "A decorative strip, e.g. cornice or baseboard profile.",
           "Profil décoratif rapporté, ex. corniche ou moulure.",
           {"fr": ["corniche", "moulure décorative"], "en": ["molding", "cornice"],
            "it": ["cornice decorativa", "modanatura"], "de": ["Gesims", "Zierleiste"]}),
        pt("CLADDING", "4.0", "An external covering (e.g. facade cladding).",
           "Bardage ou habillage de façade.",
           {"fr": ["bardage", "habillage de façade"], "en": ["cladding"], "it": ["rivestimento di facciata"],
            "de": ["Verkleidung"]}),
        pt("FLOORING", "4.0", "A floor finish (e.g. tiling, parquet).",
           "Revêtement de sol (carrelage, parquet...).",
           {"fr": ["revêtement de sol", "carrelage", "parquet"], "en": ["flooring"],
            "it": ["pavimentazione"], "de": ["Bodenbelag"]}),
        pt("CEILING", "4.0", "A ceiling finish (e.g. suspended ceiling).",
           "Faux-plafond ou plafond fini.",
           {"fr": ["faux-plafond", "plafond"], "en": ["ceiling"], "it": ["controsoffitto"],
            "de": ["Decke", "Abhangdecke"]}),
        pt("ROOFING", "4.0", "A roof waterproofing/finish layer.",
           "Étanchéité ou couverture de toiture.",
           {"fr": ["étanchéité de toiture", "couverture"], "en": ["roofing"],
            "it": ["manto di copertura"], "de": ["Dachdeckung"]}),
        pt("INSULATION", "4.0", "A thermal or acoustic insulation layer.",
           "Couche d'isolation thermique ou acoustique.",
           {"fr": ["isolation", "isolant"], "en": ["insulation"], "it": ["isolamento"],
            "de": ["Dämmung"]}),
        pt("COPING", "4.0", "A capping course on top of a wall or parapet.",
           "Couvertine posée en tête de mur ou d'acrotère.",
           {"fr": ["couvertine"], "en": ["coping"], "it": ["copertina"], "de": ["Mauerabdeckung"]}),
    ],
    notes_fr="« Corniche » est ambigu : moulure décorative rapportée → "
             "IfcCovering(MOLDING) ; élément porteur en surplomb (corniche "
             "de charpente) → plutôt IfcBeam ou IfcMember selon le contexte.",
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
    {"introduced": "2x3", "current": "4.3", "deprecated": None},
    "A vertical, hollow substructure to convey exhaust gases to the "
    "outer air.",
    "Ouvrage vertical creux évacuant les gaz de combustion vers "
    "l'extérieur.",
    ["Pset_ChimneyCommon"],
    {"fr": ["cheminée", "conduit de fumée"], "en": ["chimney", "flue"], "it": ["camino"],
     "de": ["Schornstein", "Kamin"]},
    [pt("NOTDEFINED", "2x3", "Undefined.", "Non précisé.", {})],
    notes_fr="",
))

DATA.append(entry(
    "IfcShadingDevice", "Protection solaire", "IfcBuildingElement",
    [PHYS, BLDG, "Protections solaires"],
    {"introduced": "4.0", "current": "4.3", "deprecated": None},
    "A device attached to a building or free standing which provides "
    "solar shading, e.g. a louver, jalousie or shutter.",
    "Dispositif rapporté ou autonome assurant une protection solaire "
    "(brise-soleil, jalousie, volet).",
    ["Pset_ShadingDeviceCommon"],
    {"fr": ["protection solaire", "brise-soleil"], "en": ["shading device"],
     "it": ["schermatura solare"], "de": ["Sonnenschutz"]},
    [
        pt("LOUVER", "4.0", "A shading device made of angled slats.",
           "Brise-soleil à lames orientées.",
           {"fr": ["brise-soleil à lames", "claustra"], "en": ["louver"], "it": ["frangisole a lamelle"],
            "de": ["Lamellenschutz"]}),
        pt("JALOUSIE", "4.0", "An adjustable slatted shutter/blind.",
           "Jalousie à lames orientables.",
           {"fr": ["jalousie"], "en": ["jalousie", "venetian blind"], "it": ["gelosia"],
            "de": ["Jalousie"]}),
        pt("SHUTTER", "4.0", "A shutter, often foldable or rolling.",
           "Volet, souvent battant ou roulant.",
           {"fr": ["volet", "volet roulant"], "en": ["shutter"], "it": ["persiana", "tapparella"],
            "de": ["Fensterladen", "Rollladen"]}),
    ],
    notes_fr="",
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
        pt("RIGIDSEGMENT", "4.0", "A rigid duct segment.", "Tronçon de gaine rigide.",
           {"fr": ["gaine rigide"], "en": ["rigid duct"], "it": ["condotto rigido"],
            "de": ["Starrer Kanal"]}),
        pt("FLEXIBLESEGMENT", "4.0", "A flexible duct segment.", "Tronçon de gaine flexible.",
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
        pt("RIGIDSEGMENT", "4.0", "A rigid pipe segment.", "Tronçon de canalisation rigide.",
           {"fr": ["tuyau rigide"], "en": ["rigid pipe"], "it": ["tubo rigido"],
            "de": ["Starres Rohr"]}),
        pt("GUTTER", "4.0", "A gutter conveying rainwater.", "Chéneau ou gouttière.",
           {"fr": ["gouttière", "chéneau"], "en": ["gutter"], "it": ["grondaia"],
            "de": ["Dachrinne"]}),
        pt("CULVERT", "4.3", "A buried conduit conveying water under a road/embankment.",
           "Buse ou dalot enterré sous une voirie ou un remblai.",
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
        pt("WASHHANDBASIN", "4.0", "A wash hand basin.", "Lavabo.",
           {"fr": ["lavabo", "vasque"], "en": ["wash hand basin", "sink"], "it": ["lavabo"],
            "de": ["Waschbecken"]}),
        pt("TOILETPAN", "4.0", "A toilet pan/bowl.", "Cuvette de WC.",
           {"fr": ["wc", "cuvette", "toilette"], "en": ["toilet", "WC pan"], "it": ["water", "wc"],
            "de": ["WC-Becken"]}),
        pt("SHOWER", "4.0", "A shower.", "Douche.",
           {"fr": ["douche"], "en": ["shower"], "it": ["doccia"], "de": ["Dusche"]}),
        pt("BATH", "4.0", "A bath tub.", "Baignoire.",
           {"fr": ["baignoire"], "en": ["bathtub"], "it": ["vasca da bagno"], "de": ["Badewanne"]}),
        pt("URINAL", "4.0", "A urinal.", "Urinoir.",
           {"fr": ["urinoir"], "en": ["urinal"], "it": ["orinatoio"], "de": ["Urinal"]}),
    ],
    notes_fr="",
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
        pt("CABLETRAYSEGMENT", "4.0", "A cable tray segment.", "Tronçon de chemin de câbles.",
           {"fr": ["chemin de câbles"], "en": ["cable tray"], "it": ["passerella portacavi"],
            "de": ["Kabelrinne"]}),
        pt("CONDUITSEGMENT", "4.0", "A conduit segment.", "Tronçon de conduit électrique.",
           {"fr": ["conduit électrique", "gaine électrique"], "en": ["conduit"], "it": ["tubo protettivo"],
            "de": ["Elektroleerrohr"]}),
        pt("CABLETRUNKINGSEGMENT", "4.0", "A cable trunking segment.", "Tronçon de goulotte.",
           {"fr": ["goulotte"], "en": ["cable trunking"], "it": ["canalina"], "de": ["Kabelkanal"]}),
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
        pt("POINTSOURCE", "4.0", "A fixture with a point light source.", "Luminaire ponctuel (spot).",
           {"fr": ["spot", "luminaire ponctuel"], "en": ["point source fixture"],
            "it": ["faretto"], "de": ["Punktleuchte"]}),
        pt("DIRECTIONSOURCE", "4.0", "A fixture with a directional light source.",
           "Luminaire directionnel (projecteur).",
           {"fr": ["projecteur"], "en": ["directional fixture"], "it": ["proiettore"],
            "de": ["Strahler"]}),
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
        pt("DIFFUSER", "4.0", "An air terminal diffusing supply air.", "Diffuseur de soufflage.",
           {"fr": ["diffuseur"], "en": ["diffuser"], "it": ["diffusore"], "de": ["Diffusor"]}),
        pt("GRILLE", "4.0", "A grille covering an air opening.", "Grille de ventilation.",
           {"fr": ["grille de ventilation"], "en": ["grille"], "it": ["griglia"], "de": ["Gitter"]}),
        pt("REGISTER", "4.0", "A grille with adjustable dampers.", "Bouche réglable à registre.",
           {"fr": ["bouche à registre"], "en": ["register"], "it": ["bocchetta regolabile"],
            "de": ["Regelklappe"]}),
    ],
    notes_fr="",
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
    [pt("CONVECTOR", "4.0", "A convector-type space heater.", "Radiateur de type convecteur.",
        {"fr": ["convecteur"], "en": ["convector"], "it": ["convettore"], "de": ["Konvektor"]}),
     pt("RADIATOR", "4.0", "A radiator-type space heater.", "Radiateur classique à eau chaude.",
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
    [pt("NOTDEFINED", "2x3", "Undefined.", "Non précisé.", {})],
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
        pt("SPACE", "4.0", "A standard space.", "Local ou pièce standard.",
           {"fr": ["local standard"], "en": ["standard space"], "it": ["locale standard"],
            "de": ["Standardraum"]}),
        pt("PARKING", "4.0", "A space used for parking.", "Place ou zone de parking.",
           {"fr": ["place de parking", "zone de stationnement"], "en": ["parking space"],
            "it": ["posto auto"], "de": ["Parkplatz"]}),
        pt("GFA", "4.0", "A space used for gross floor area calculation.",
           "Espace utilisé pour le calcul de surface brute de plancher.",
           {"fr": ["surface brute de plancher"], "en": ["gross floor area"],
            "it": ["superficie lorda di piano"], "de": ["Bruttogeschossfläche"]}),
    ],
    notes_fr="",
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
    "pavement, introduced in IFC4.3 for infrastructure projects.",
    "Bordure surélevée en limite de chaussée ou de trottoir. Classe "
    "introduite en IFC4.3 pour les projets d'infrastructure routière.",
    ["Pset_KerbCommon"],
    {"fr": ["bordure de trottoir", "bordure de voirie"], "en": ["kerb", "curb"],
     "it": ["cordolo stradale"], "de": ["Bordstein"]},
    [pt("USERDEFINED", "4.3", "A user-defined kerb type.", "Type défini par l'utilisateur.", {},
        new_in_43=True)],
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
    [pt("USERDEFINED", "4.3", "A user-defined pavement type.", "Type défini par l'utilisateur.", {},
        new_in_43=True)],
    notes_fr="À ne pas confondre avec IfcSlab(PAVING) qui désigne une "
             "dalle de pavage ponctuelle plutôt qu'une structure de "
             "chaussée complète.",
    version_notes="Nouveau en IFC4.3 (extension infrastructure routière).",
))

DATA.append(entry(
    "IfcRail", "Rail (voie ferrée)", "IfcBuildingElement",
    [PHYS, CIVIL, "Voirie et équipements routiers"],
    {"introduced": "4.3", "current": "4.3", "deprecated": None},
    "A rail is a component of railway track providing the running "
    "surface for train wheels, introduced in IFC4.3.",
    "Composant de voie ferrée assurant la surface de roulement des "
    "roues de train. Classe introduite en IFC4.3.",
    ["Pset_RailCommon"],
    {"fr": ["rail", "rail de chemin de fer"], "en": ["rail"], "it": ["rotaia"],
     "de": ["Schiene"]},
    [pt("USERDEFINED", "4.3", "A user-defined rail type.", "Type défini par l'utilisateur.", {},
        new_in_43=True)],
    notes_fr="Domaine ferroviaire, extension infrastructure d'IFC4.3.",
    version_notes="Nouveau en IFC4.3 (extension infrastructure ferroviaire).",
))

# ---------------------------------------------------------------------------

def build_children_index(data):
    by_class = {d["class"]: d for d in data}
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
