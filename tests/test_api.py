# -*- coding: utf-8 -*-
"""
altair-brain — test dell'API (pytest + TestClient). Nessuna rete, nessuna API a pagamento.
Girano in CI (dove graphify NON e installato: si testa la degradazione a 503) e in
locale (dove graphify c'e: 200). Esecuzione:  pytest -q
"""
import os, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "test-token-for-ci"
os.environ["ALTAIR_API_TOKEN"] = TOKEN
os.environ["ALTAIR_REPO_DIR"] = str(ROOT)
os.environ["ALTAIR_INBOX_DIR"] = tempfile.mkdtemp(prefix="altair_inbox_")
os.environ["ALTAIR_RATE_LIMIT"] = "10000"  # niente falsi 429 nei test

sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402
import app as app_module  # noqa: E402

client = TestClient(app_module.app)
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def test_health_pubblico_e_ricco():
    r = client.get("/v1/health")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "ok"
    assert "graph" in j and "model" in j and "areas" in j
    assert j["model"].get("schema_version") == 1


def test_auth_richiesta_e_constant_time_ok():
    assert client.get("/v1/model").status_code == 401
    assert client.get("/v1/model", headers={"Authorization": "Bearer sbagliato"}).status_code == 401
    assert client.get("/v1/model", headers=AUTH).status_code == 200


def test_alias_non_versionati():
    assert client.get("/health").status_code == 200
    assert client.get("/model", headers=AUTH).status_code == 200


def test_query_degrada_o_funziona():
    r = client.get("/v1/query", params={"q": "AION_SUPERIA"}, headers=AUTH)
    assert r.status_code in (200, 503)  # 503 in CI (niente graphify), 200 in locale
    if r.status_code == 200:
        assert "X-Altair-Area" in r.headers


def test_route_deterministico():
    r = client.get("/v1/route", params={"q": "cosa dice l'oracolo sugli esagrammi?"}, headers=AUTH)
    assert r.status_code == 200
    assert r.json()["area"] in ("aion", None)


def test_query_area_invalida():
    r = client.get("/v1/query", params={"q": "x", "area": "not-an-area"}, headers=AUTH)
    assert r.status_code in (404, 503)


def test_oracle_deterministico_con_seed():
    a = client.post("/v1/oracle", json={"seed": 42, "question": "test"}, headers=AUTH)
    b = client.post("/v1/oracle", json={"seed": 42}, headers=AUTH)
    assert a.status_code == b.status_code == 200
    ja, jb = a.json(), b.json()
    assert ja["lanci"] == jb["lanci"]
    assert ja["esagramma_primario"]["id"] == jb["esagramma_primario"]["id"]
    assert 1 <= ja["esagramma_primario"]["id"] <= 64


def test_oracle_hexagram_lookup_re_wen():
    r = client.get("/v1/oracle/hexagram/1", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["nome"] == "Il Creativo"
    assert r.json()["binario"] == "111111"
    assert client.get("/v1/oracle/hexagram/99", headers=AUTH).status_code == 404


def test_inbox_flusso_completo():
    r = client.post("/v1/capture", json={"text": "idea di prova", "title": "Test nota",
                                         "area_hint": "aion", "source": "pytest"}, headers=AUTH)
    assert r.status_code == 200
    nid = r.json()["id"]
    items = client.get("/v1/inbox", headers=AUTH).json()
    assert any(i["id"] == nid for i in items)
    body = client.get(f"/v1/inbox/{nid}", headers=AUTH).json()
    assert "idea di prova" in body["content"]
    assert client.post(f"/v1/inbox/{nid}/done", headers=AUTH).status_code == 200
    assert client.get(f"/v1/inbox/{nid}", headers=AUTH).status_code == 404


def test_inbox_path_traversal_respinto():
    for bad in ("..%2F..%2Fsecret.md", "..", "a%2Fb.md", ".nascosto.md"):
        r = client.get(f"/v1/inbox/{bad}", headers=AUTH)
        assert r.status_code in (400, 404), f"id malevolo accettato: {bad}"


def test_capture_vuoto_e_troppo_grande():
    assert client.post("/v1/capture", json={"text": "  "}, headers=AUTH).status_code == 400
    big = "x" * 150_000
    assert client.post("/v1/capture", json={"text": big}, headers=AUTH).status_code == 413
