#!/usr/bin/env python3
"""
Complète data/ifc_reference.json avec une entrée pour CHAQUE entité du schéma
IFC4X3_ADD2 officiel (872 entités), au-delà des 54 classes curées à la main
par build_reference_data.py.

Contrairement aux 54 classes curées (définitions + synonymes 4 langues +
notes de désambiguïsation rédigés et vérifiés à la main), les entités
ajoutées ici sont un SQUELETTE généré automatiquement depuis les sources
officielles buildingSMART :
  - le schéma EXPRESS lui-même (via le paquet `ifcopenshell`, qui expose la
    hiérarchie de types, les PredefinedType et leur disponibilité par
    version IFC2x3/IFC4/IFC4X3) ;
  - les définitions textuelles officielles (anglais), extraites du dépôt
    buildingSMART/IFC4.3.x-development (docs/schemas/**/Entities/*.md et
    **/Types/*.md) ;
  - la correspondance classe -> Pset/Qto applicables, extraite des 612
    définitions XML officielles (reference_schemas/psd/*.xml).

Conséquence : ces entrées n'ont PAS de traduction FR/IT/DE soignée (le texte
anglais officiel est dupliqué tel quel dans les 4 langues, en attendant une
curation ultérieure) ni de notes de désambiguïsation — seule la recherche en
anglais/nom de classe est pleinement fiable dessus pour l'instant. Elles
portent en revanche un nouveau champ commun à TOUTES les classes (curées et
squelettes) : `ifc_root_path`, le véritable chemin de super-types EXPRESS
jusqu'à IfcRoot (ex. IfcAlignmentHorizontal -> IfcLinearElement -> IfcProduct
-> IfcObject -> IfcObjectDefinition -> IfcRoot), distinct du `category_path`
qui reste une catégorisation UX choisie à la main pour les 54 classes curées.

Prérequis : lancer d'abord `python3 build_reference_data.py` (produit les 54
classes curées + i18n), PUIS ce script sous un interpréteur où `ifcopenshell`
est installé (`pip install ifcopenshell`) pour compléter avec le reste du
schéma. Le dépôt buildingSMART/IFC4.3.x-development doit être cloné (sparse
checkout de docs/schemas et reference_schemas/psd) ; voir REPO_PATH ci-dessous.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "ifc_reference.json"
REPO_PATH = Path(
    sys.argv[1] if len(sys.argv) > 1 else
    "/tmp/claude-0/-home-user-IFC-Dictionnary/c78b3a80-ab15-5f50-ad69-111b902e5634/scratchpad/ifc43repo"
)

try:
    import ifcopenshell
except ImportError:
    sys.exit(
        "ifcopenshell introuvable sous cet interpréteur. "
        "Installer avec `pip install ifcopenshell` (nécessite Python >=3.9) "
        "et relancer ce script avec ce même interpréteur."
    )

try:
    import wordninja
except ImportError:
    wordninja = None
    print(
        "ATTENTION : module `wordninja` introuvable — les valeurs de "
        "PredefinedType composées sans séparateur (ex. ROOFDRAIN) ne seront "
        "indexées que sous leur forme brute non segmentée (ex. « roofdrain » "
        "au lieu de « roof drain »), ce qui dégrade la recherche en langage "
        "naturel mais préserve la correspondance exacte au terme IFC officiel.",
        file=sys.stderr,
    )


# ---------------------------------------------------------------------------
# Micro-curation ciblée : quelques classes du schéma complet sont de toute
# évidence recherchées dans la vie courante avec un vocabulaire français très
# éloigné du nom EXPRESS anglais (ex. « géométrie horizontale » plutôt que
# « IfcAlignmentHorizontal ») ; sans un minimum de synonymes FR, ces entités
# squelette restent introuvables sauf en tapant le nom de classe lui-même.
# Ceci n'est PAS la curation complète (pas de notes de désambiguïsation, pas
# de traduction IT/DE) mais juste quelques synonymes de recherche choisis à
# la main pour les cas les plus évidents, au fil de l'eau.
# ---------------------------------------------------------------------------
EXTRA_SYNONYMS = {
    "IfcAlignmentHorizontal": {
        "fr": ["géométrie horizontale", "tracé en plan", "alignement horizontal"],
        "it": ["geometria orizzontale", "tracciato planimetrico"],
        "de": ["horizontale Trassierung", "Lageplan"],
    },
    "IfcAlignmentVertical": {
        "fr": ["géométrie verticale", "profil en long", "alignement vertical"],
        "it": ["geometria verticale", "profilo longitudinale"],
        "de": ["vertikale Trassierung", "Höhenplan"],
    },
    "IfcAlignmentCant": {
        "fr": ["dévers", "géométrie de dévers"],
        "it": ["sopraelevazione", "geometria di sopraelevazione"],
        "de": ["Überhöhung", "Überhöhungstrassierung"],
    },
    "IfcAlignmentHorizontalSegment": {
        "fr": ["segment de tracé en plan", "segment horizontal d'alignement"],
        "it": ["segmento del tracciato planimetrico"],
        "de": ["Segment der horizontalen Trasse"],
    },
    "IfcAlignmentVerticalSegment": {
        "fr": ["segment de profil en long", "segment vertical d'alignement"],
        "it": ["segmento del profilo longitudinale"],
        "de": ["Segment der vertikalen Trasse"],
    },
    "IfcAlignmentCantSegment": {
        "fr": ["segment de dévers"],
        "it": ["segmento di sopraelevazione"],
        "de": ["Überhöhungssegment"],
    },
}
# ---------------------------------------------------------------------------
# Micro-curation ciblée, niveau PredefinedType cette fois : quelques valeurs
# d'énumération sont recherchées dans la vie courante avec un vocabulaire très
# éloigné de leur libellé EXPRESS (ex. « lift » pour ELEVATOR, un terme
# britannique courant que ni la forme brute « elevator » ni sa segmentation
# wordninja ne couvrent). Clé = (nom de classe EXPRESS, valeur d'énumération).
# Ajouté à la liste anglaise produite par `enum_value_synonyms` plutôt que de
# la remplacer.
# ---------------------------------------------------------------------------
EXTRA_ENUM_SYNONYMS = {
    ("IfcTransportElement", "ELEVATOR"): ["lift"],
    ("IfcOutlet", "POWEROUTLET"): ["socket", "power socket"],
    ("IfcSensor", "SMOKESENSOR"): ["smoke detector"],
}


# ---------------------------------------------------------------------------
# Schémas (toutes versions, pour dater l'apparition de chaque entité/valeur)
# ---------------------------------------------------------------------------
SCHEMA_43 = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4X3")
SCHEMA_4 = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4")
SCHEMA_23 = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC2X3")


def _exists_in(schema, name):
    try:
        schema.declaration_by_name(name)
        return True
    except RuntimeError:
        return False


def introduced_version(name):
    if _exists_in(SCHEMA_23, name):
        return "2x3"
    if _exists_in(SCHEMA_4, name):
        return "4.0"
    return "4.3"


def enum_literal_introduced(enum_name, literal):
    if _exists_in(SCHEMA_23, enum_name) and literal in SCHEMA_23.declaration_by_name(enum_name).enumeration_items():
        return "2x3"
    if _exists_in(SCHEMA_4, enum_name) and literal in SCHEMA_4.declaration_by_name(enum_name).enumeration_items():
        return "4.0"
    return "4.3"


# ---------------------------------------------------------------------------
# Documentation officielle (markdown) : définitions + descriptions d'enum
# ---------------------------------------------------------------------------
def _strip_md(text):
    text = re.sub(r"_([^_]+)_", r"\1", text)  # _italics_ -> italics
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_entity_definition(path):
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^# .+?\n\n(.*?)\n<!-- end of short definition -->", text, re.S | re.M)
    if not m:
        return ""
    return _strip_md(m.group(1))


def parse_entity_deprecation(path):
    text = path.read_text(encoding="utf-8")
    head = text.split("## Concepts")[0]
    for line in head.splitlines():
        line = line.strip()
        if line.startswith(">") and "DEPREC" in line.upper():
            m = re.search(r"IFC\s?([0-9][0-9x.]*)", line)
            return m.group(1) if m else "4.3"
    return None


def parse_enum_items(path):
    text = path.read_text(encoding="utf-8")
    items = {}
    parts = re.split(r"^### (\S+)\s*$", text, flags=re.M)
    for i in range(1, len(parts), 2):
        name = parts[i].strip()
        body = parts[i + 1]
        desc_lines = []
        deprecated_version = None
        for line in body.strip().splitlines():
            s = line.strip()
            if s.startswith(">"):
                if "DEPREC" in s.upper():
                    m = re.search(r"IFC\s?([0-9][0-9x.]*)", s)
                    deprecated_version = m.group(1) if m else "4.3"
                continue
            if s == "":
                if desc_lines:
                    break
                continue
            desc_lines.append(s)
        items[name] = {
            "description": _strip_md(" ".join(desc_lines)),
            "deprecated_since": deprecated_version,
        }
    return items


def build_doc_indexes(repo_path):
    entity_md = {p.stem: p for p in repo_path.glob("docs/schemas/**/Entities/*.md")}
    enum_md = {p.stem: p for p in repo_path.glob("docs/schemas/**/Types/*.md")}
    return entity_md, enum_md


# ---------------------------------------------------------------------------
# Pset/Qto applicables par classe (reference_schemas/psd/*.xml)
# ---------------------------------------------------------------------------
def build_pset_index(repo_path):
    index = {}
    psd_dir = repo_path / "reference_schemas" / "psd"
    for f in sorted(psd_dir.glob("*.xml")):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        name_el = root.find("Name")
        if name_el is None or not name_el.text:
            continue
        pset_name = name_el.text.strip()
        for cn in root.findall("./ApplicableClasses/ClassName"):
            if cn.text:
                index.setdefault(cn.text.strip(), []).append(pset_name)
    return index


# ---------------------------------------------------------------------------
# Libellé lisible dérivé du nom de classe (PAS une traduction : simple mise
# en forme mécanique, ex. "IfcAlignmentHorizontal" -> "Alignment Horizontal")
# ---------------------------------------------------------------------------
def psets_for(name, pset_index):
    """Les définitions de Pset officielles référencent presque toujours la
    classe d'OCCURRENCE (ex. IfcSlab) dans ApplicableClasses, jamais sa
    classe de TYPE associée (IfcSlabType) — bien que le Pset s'applique
    conceptuellement aux deux (cf. ApplicableTypeValue du XML). On reporte
    donc les Psets de la classe d'occurrence sur sa classe de Type quand
    cette dernière n'a pas de correspondance directe."""
    direct = pset_index.get(name, [])
    if direct or not name.endswith("Type"):
        return direct
    return pset_index.get(name[:-4], [])


def split_camel_label(ifc_class):
    s = ifc_class[3:] if ifc_class.startswith("Ifc") else ifc_class
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)
    return s.strip()


def enum_value_synonyms(value):
    """Transforme une valeur d'énumération EXPRESS (ex. "ROOFDRAIN",
    "T_BEAM") en synonymes de recherche anglais lisibles. Sans ceci, une
    valeur de PredefinedType squelette n'est indexée sous AUCUN terme
    propre — seul le nom de la classe (ex. IfcWasteTerminal) reste
    cherchable, pas "roof drain" ni même "roofdrain" tel que pourrait le
    taper un utilisateur cherchant un terme technique IFC exact.

    Retourne 1 ou 2 synonymes :
    - la forme brute (minuscules, « _ » -> espace) : couvre une recherche
      au plus près du terme officiel IFC (ex. "drainage" pour DRAINAGE) ;
    - si `wordninja` est disponible et que la forme segmentée diffère
      (ex. "roof drain" pour ROOFDRAIN, sans séparateur dans le schéma),
      elle est ajoutée aussi, pour couvrir une recherche en langage naturel
      multi-mots."""
    raw = value.replace("_", " ").lower()
    synonyms = [raw]
    if wordninja and " " not in raw and len(raw) > 4:
        segmented = " ".join(wordninja.split(raw))
        if segmented != raw and len(segmented.split()) <= 4:
            synonyms.append(segmented)
    return synonyms


# ---------------------------------------------------------------------------
# Hiérarchie EXPRESS
# ---------------------------------------------------------------------------
def supertype_chain(decl):
    """Parent -> ... -> IfcRoot (n'inclut pas l'entité elle-même)."""
    chain = []
    s = decl.supertype()
    while s:
        chain.append(s.name())
        s = s.supertype()
    return chain


def predefined_type_enum(decl):
    for a in decl.all_attributes():
        if a.name() == "PredefinedType":
            try:
                t = a.type_of_attribute()
                dt = t.declared_type()
                return dt.as_enumeration_type() if hasattr(dt, "as_enumeration_type") else None
            except (AttributeError, RuntimeError):
                return None
    return None


def build_predefined_types(enum, enum_md_index, class_name=None):
    if enum is None:
        return []
    enum_name = enum.name()
    doc_items = {}
    if enum_name in enum_md_index:
        doc_items = parse_enum_items(enum_md_index[enum_name])
    out = []
    for value in enum.enumeration_items():
        if value in ("USERDEFINED", "NOTDEFINED"):
            continue
        since = enum_literal_introduced(enum_name, value)
        doc = doc_items.get(value, {})
        en_synonyms = enum_value_synonyms(value) + EXTRA_ENUM_SYNONYMS.get((class_name, value), [])
        out.append({
            "value": value,
            "since": since,
            "deprecated_since": doc.get("deprecated_since"),
            "new_in_43": since == "4.3",
            "description_en": doc.get("description", ""),
            "description_fr": doc.get("description", ""),
            "synonyms": {"fr": [], "en": en_synonyms, "it": [], "de": []},
            "description": {
                "fr": doc.get("description", ""), "en": doc.get("description", ""),
                "it": doc.get("description", ""), "de": doc.get("description", ""),
            },
        })
    return out


def main():
    if not REPO_PATH.exists():
        sys.exit(f"Dépôt IFC4.3.x-development introuvable : {REPO_PATH}")

    existing = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    classes = existing["classes"]
    category_labels = existing.get("category_labels", {})
    curated_names = {c["class"] for c in classes}

    entity_md, enum_md = build_doc_indexes(REPO_PATH)
    pset_index = build_pset_index(REPO_PATH)

    all_entities = [d for d in SCHEMA_43.declarations() if d.as_entity()]
    print(f"{len(all_entities)} entités dans le schéma IFC4X3_ADD2 "
          f"({len(curated_names)} déjà curées à la main).")

    # --- 1) Ajoute ifc_root_path / ifc_subtypes aux classes déjà curées ---
    for c in classes:
        decl = SCHEMA_43.declaration_by_name(c["class"])
        c["ifc_root_path"] = supertype_chain(decl)
        c["ifc_subtypes"] = sorted(s.name() for s in decl.subtypes())
        c["is_abstract"] = decl.is_abstract()
        c["curated"] = True

    # --- 2) Génère un squelette pour chaque entité restante ---
    skipped_no_def = 0
    for decl in all_entities:
        name = decl.name()
        if name in curated_names:
            continue
        root_path = supertype_chain(decl)
        definition_en = ""
        if name in entity_md:
            definition_en = parse_entity_definition(entity_md[name])
        else:
            skipped_no_def += 1
        deprecated_since = parse_entity_deprecation(entity_md[name]) if name in entity_md else None
        since = introduced_version(name)
        label = split_camel_label(name)
        enum = predefined_type_enum(decl)
        predefined_types = build_predefined_types(enum, enum_md, class_name=name)
        psets = sorted(set(psets_for(name, pset_index)))

        entry = {
            "class": name,
            "class_fr": label,
            "class_label": {"fr": label, "en": label, "it": label, "de": label},
            "parent": root_path[0] if root_path else None,
            "category_path": list(reversed(root_path)),
            "ifc_root_path": root_path,
            "ifc_subtypes": sorted(s.name() for s in decl.subtypes()),
            "is_abstract": decl.is_abstract(),
            "ifc_versions": {"introduced": since, "current": "4.3", "deprecated": deprecated_since},
            "definition_en": definition_en,
            "definition_fr": definition_en,
            "definition": {"fr": definition_en, "en": definition_en, "it": definition_en, "de": definition_en},
            "psets_common": psets,
            "class_synonyms": {
                "fr": list(EXTRA_SYNONYMS.get(name, {}).get("fr", [])),
                "en": [label.lower()] if label else [],
                "it": list(EXTRA_SYNONYMS.get(name, {}).get("it", [])),
                "de": list(EXTRA_SYNONYMS.get(name, {}).get("de", [])),
            },
            "predefined_types": predefined_types,
            "notes_fr": "",
            "notes": {"fr": "", "en": "", "it": "", "de": ""},
            "version_notes": "",
            "version_notes_i18n": {"fr": "", "en": "", "it": "", "de": ""},
            "curated": False,
        }
        classes.append(entry)

    print(f"{len(classes) - len(curated_names)} entités squelette ajoutées "
          f"({skipped_no_def} sans définition markdown trouvée).")

    # recalcule children (classes filles directement référencées) sur
    # l'ensemble complet, comme build_reference_data.py le fait pour les
    # classes curées.
    by_class = {c["class"]: c for c in classes}
    for c in classes:
        c["children"] = sorted(k for k, v in by_class.items() if v.get("parent") == c["class"])

    OUT_PATH.write_text(
        json.dumps({"schema_version": existing["schema_version"], "classes": classes,
                     "category_labels": category_labels}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Écrit {len(classes)} classes dans {OUT_PATH}")


if __name__ == "__main__":
    main()
