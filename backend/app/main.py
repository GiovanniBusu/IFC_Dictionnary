"""API du Dictionnaire IFC interactif.

Endpoints :
  GET /search?q=...&lang=...   -> suggestion principale + alternatives
  GET /class/{ifc_class}       -> fiche détaillée d'une classe
  GET /tree                    -> arborescence complète de classification
  GET /health                  -> vérification de service
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .data_loader import CUSTOM_PSET_GUIDANCE, get_reference
from .search import search as run_search
from .tree import build_tree

app = FastAPI(
    title="Dictionnaire IFC interactif",
    description="API de recherche et de navigation dans la classification IFC "
                 "(jusqu'à IFC4X3), multilingue (FR/EN/IT/DE).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    ref = get_reference()
    return {"status": "ok", "schema_version": ref.schema_version, "classes": len(ref.classes)}


@app.get("/search")
def search(
    q: str = Query(..., min_length=1, description="Terme ou description libre à rechercher"),
    lang: str | None = Query(
        None, pattern="^(fr|en|it|de)$",
        description="Forcer la langue de recherche (sinon détection automatique)"
    ),
):
    reference = get_reference()
    return run_search(q, forced_language=lang, reference=reference)


@app.get("/tree")
def tree():
    reference = get_reference()
    return build_tree(reference)


@app.get("/class/{ifc_class}")
def class_detail(ifc_class: str):
    reference = get_reference()
    entry = reference.get_class(ifc_class)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Classe IFC inconnue : {ifc_class}")
    parent = reference.get_class(entry.get("parent", ""))
    return {
        **entry,
        "parent_known": bool(parent),
        "custom_pset_guidance": CUSTOM_PSET_GUIDANCE,
    }
