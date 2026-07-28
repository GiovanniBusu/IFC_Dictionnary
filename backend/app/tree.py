"""Construction de l'arborescence de classification IFC pour la vue
« Parcourir » (indépendante de la recherche, cf. section 3.2.3)."""
from __future__ import annotations

from .data_loader import IfcReference


def _new_category_node(name: str) -> dict:
    return {"type": "category", "name": name, "children": {}}


ROOT_LABELS = {
    "fr": "Classification IFC4X3",
    "en": "IFC4X3 classification",
    "it": "Classificazione IFC4X3",
    "de": "IFC4X3-Klassifikation",
}


def build_tree(reference: IfcReference, output_lang: str = "fr") -> dict:
    root = _new_category_node(ROOT_LABELS.get(output_lang, ROOT_LABELS["fr"]))

    for entry in reference.classes:
        node = root
        localized_path = reference.localize_category_path(entry["category_path"], output_lang)
        for level_name in localized_path:
            node["children"].setdefault(level_name, _new_category_node(level_name))
            node = node["children"][level_name]

        class_node = {
            "type": "class",
            "name": entry["class"],
            "ifc_class": entry["class"],
            "class_label": entry["class_label"][output_lang],
            "children": {
                pdt["value"]: {
                    "type": "predefined_type",
                    "name": f"{entry['class']}.{pdt['value']}",
                    "ifc_class": entry["class"],
                    "predefined_type": pdt["value"],
                    "children": {},
                }
                for pdt in entry["predefined_types"]
            },
        }
        node["children"][entry["class"]] = class_node

    return _finalize(root)


def _finalize(node: dict) -> dict:
    children = sorted(node["children"].values(), key=lambda n: n["name"])
    result = {k: v for k, v in node.items() if k != "children"}
    result["children"] = [_finalize(c) for c in children]
    return result
