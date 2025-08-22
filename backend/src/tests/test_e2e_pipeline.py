# tests/test_e2e_pipeline.py
import os
import shutil
import pytest
from src.app import create_app, db
from flask import url_for

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
AZUL_SRC = "/data/uploads/2024_ENEM_AZUL_DIA1.pdf"
AMARELO_SRC = "/data/uploads/2024_ENEM_AMARELO_DIA2.pdf"
GABARITO_SRC = "/data/uploads/2023-GB-ENEM_AMARELO_DIA2.pdf"
AZUL_DST = os.path.join(FIXTURE_DIR, "2024_ENEM_AZUL_DIA1.pdf")
AMARELO_DST = os.path.join(FIXTURE_DIR, "2024_ENEM_AMARELO_DIA2.pdf")

@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
    client = app.test_client()
    yield client
    with app.app_context():
        db.drop_all()

def ensure_fixtures():
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    if not os.path.exists(AZUL_DST) and os.path.exists(AZUL_SRC):
        shutil.copy(AZUL_SRC, AZUL_DST)
    if not os.path.exists(AMARELO_DST) and os.path.exists(AMARELO_SRC):
        shutil.copy(AMARELO_SRC, AMARELO_DST)
    if not os.path.exists(os.path.join(FIXTURE_DIR,"2023-GB-ENEM_AMARELO_DIA2.pdf")) and os.path.exists(GABARITO_SRC):
        shutil.copy(GABARITO_SRC, os.path.join(FIXTURE_DIR,"2023-GB-ENEM_AMARELO_DIA2.pdf"))    
    assert os.path.exists(AZUL_DST), f"Fixture missing: {AZUL_DST}"
    assert os.path.exists(AMARELO_DST), f"Fixture missing: {AMARELO_DST}"

def test_upload_and_assuntos_endpoint(test_client):
    ensure_fixtures()
    with open(AZUL_DST, "rb") as f:
        data = {
            "file": (f, "2024_ENEM_AZUL_DIA1.pdf"),
            "prova": "ENEM",
            "ano": "2024",
            "dia": "1",
            "materia": "Linguagens"
        }
        resp = test_client.post("/api/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code in (201, 409)  
    with open(AMARELO_DST, "rb") as fq, open(os.path.join(FIXTURE_DIR,"2023-GB-ENEM_AMARELO_DIA2.pdf"), "rb") as fg:
        data = {
            "file": (fq, "2023_ENEM_AMARELO_DIA2.pdf"),
            "gabarito_file": (fg, "2023-GB-ENEM_AMARELO_DIA2.pdf"),
            "prova": "ENEM",
            "ano": "2024",
            "dia": "2",
            "materia": "Matemática"
        }
        resp = test_client.post("/api/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code in (201, 409)


    r = test_client.get("/api/provas?ano=2024&page=1&per_page=10")
    assert r.status_code == 200
    js = r.get_json()
    assert "meta" in js and js["meta"]["total"] >= 1
    items = js["items"]
    if len(items) == 0:
        pytest.skip("no provas inserted")
    prova_id = items[0]["id"]
    r2 = test_client.get(f"/api/provas/{prova_id}/assuntos")
    assert r2.status_code == 200
    res = r2.get_json()
    assert isinstance(res, dict)
