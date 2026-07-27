import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["schema_version"] == "IFC4X3_ADD2"


def test_search_endpoint():
    r = client.get("/search", params={"q": "raidisseur"})
    assert r.status_code == 200
    data = r.json()
    assert data["suggestion"]["class"] == "IfcMember"
    assert data["suggestion"]["predefined_type"] == "STIFFENING_MEMBER"


def test_search_requires_query():
    r = client.get("/search")
    assert r.status_code == 422


def test_search_rejects_unsupported_language():
    r = client.get("/search", params={"q": "mur", "lang": "es"})
    assert r.status_code == 422


def test_tree_endpoint_structure():
    r = client.get("/tree")
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "category"
    assert len(data["children"]) > 0


def test_class_detail_endpoint():
    r = client.get("/class/IfcMember")
    assert r.status_code == 200
    data = r.json()
    assert data["class"] == "IfcMember"
    assert any(p["value"] == "STIFFENING_MEMBER" for p in data["predefined_types"])


def test_class_detail_not_found():
    r = client.get("/class/IfcDoesNotExist")
    assert r.status_code == 404
