# -*- coding: utf-8 -*-
"""
altair-brain — test di tools/apply_iching_relations.py (SPERIMENTALE, opzionale).

Non gira contro il grafo reale del repo (lo strumento non e cablato in rebuild_all.py
di proposito): usa un grafo minimo costruito ad arte, cosi il test non dipende da
quanti nodi-esagramma esistono oggi ne rischia di scrivere nel grafo committato.

Verifica le due proprieta su cui si basa la sicurezza dello strumento:
- IDEMPOTENZA: rilanciarlo non duplica archi
- CORRETTEZZA: aggiunge solo coppie dichiarate nel DB, con la relazione giusta
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.apply_iching_relations as air  # noqa: E402


def _grafo_minimo():
    """3 esagrammi come nodi-file, nessuna relazione ancora nel grafo."""
    return {
        "nodes": [
            {"id": "h1", "label": "1. 乾 Il Creativo (Qián) ䷀", "source_file": "raw/aion/aion-oracle.md"},
            {"id": "h2", "label": "2. 坤 Il Ricettivo (Kūn) ䷁", "source_file": "raw/aion/aion-oracle.md"},
            {"id": "h11", "label": "11. 泰 La Pace (Tài) ䷊", "source_file": "raw/aion/aion-oracle.md"},
        ],
        "links": [],
    }


def _db_minimo():
    """1 opposto a 2 (unica relazione reale, come nel DB vero); 11 con relazioni
    auto-riferite (rovesciato/nucleare su se stesso, legittimo per i palindromi)."""
    return {"esagrammi": [
        {"id": 1, "relazioni": {"opposto": 2, "rovesciato": 1, "nucleare": 1}},
        {"id": 2, "relazioni": {"opposto": 1, "rovesciato": 2, "nucleare": 2}},
        {"id": 11, "relazioni": {"opposto": 12, "rovesciato": 11, "nucleare": 11}},
    ]}


def _db_doppia_relazione():
    """Caso reale trovato sui 64 esagrammi veri (11/12, 17/18, 53/54, 63/64): due
    esagrammi legati da opposto E rovesciato verso lo STESSO bersaglio. Il primo
    tentativo dello strumento perdeva la seconda relazione in silenzio."""
    return {"esagrammi": [
        {"id": 1, "relazioni": {"opposto": 2, "rovesciato": 2, "nucleare": 1}},
        {"id": 2, "relazioni": {"opposto": 1, "rovesciato": 1, "nucleare": 2}},
    ]}


def test_trova_tutti_i_nodi_esagramma():
    trovati = air.trova_nodi_esagramma(_grafo_minimo())
    assert trovati == {1: "h1", 2: "h2", 11: "h11"}


def test_aggiunge_solo_le_coppie_dichiarate(tmp_path, monkeypatch):
    g_path = tmp_path / "graph.json"
    db_path = tmp_path / "iching.db.json"
    g_path.write_text(json.dumps(_grafo_minimo()), encoding="utf-8")
    db_path.write_text(json.dumps(_db_minimo()), encoding="utf-8")
    monkeypatch.setattr(air, "GRAPH", str(g_path))
    monkeypatch.setattr(air, "DB", str(db_path))

    monkeypatch.setattr(sys, "argv", ["apply_iching_relations.py"])
    air.main()

    g = json.loads(g_path.read_text(encoding="utf-8"))
    # solo 1<->2 (opposto): rovesciato/nucleare di 1 e 2 puntano a se stessi (skip
    # per j==i), 11 punta a 12 che non esiste nel grafo minimo (skip: j not in nodi)
    coppie = [tuple(sorted((e["source"], e["target"]))) for e in g["links"]]
    assert coppie == [("h1", "h2")], coppie
    assert g["links"][0]["relation"] == "iching_opposto"
    assert g["links"][0]["source_file"] == "engine/iching.db.json"


def test_relazioni_multiple_sulla_stessa_coppia_non_si_perdono(tmp_path, monkeypatch):
    """DIFETTO REALE (trovato testando contro i 64 esagrammi veri, non ipotizzato):
    con la deduplica per sola coppia (source,target), quando due esagrammi sono
    legati da PIU relazioni verso lo stesso bersaglio (8 casi reali: 11/12, 17/18,
    53/54 hanno opposto+rovesciato; 63/64 tutte e tre), la seconda relazione veniva
    scartata come 'gia presente' mentre era un fatto logico diverso. Corretto
    includendo la relazione nella chiave di deduplica."""
    g_path = tmp_path / "graph.json"
    db_path = tmp_path / "iching.db.json"
    g_path.write_text(json.dumps(_grafo_minimo()), encoding="utf-8")
    db_path.write_text(json.dumps(_db_doppia_relazione()), encoding="utf-8")
    monkeypatch.setattr(air, "GRAPH", str(g_path))
    monkeypatch.setattr(air, "DB", str(db_path))
    monkeypatch.setattr(sys, "argv", ["apply_iching_relations.py"])

    air.main()
    g = json.loads(g_path.read_text(encoding="utf-8"))
    relazioni = {e["relation"] for e in g["links"]}
    assert relazioni == {"iching_opposto", "iching_rovesciato"}, (
        f"attese entrambe le relazioni tra 1 e 2, trovate solo: {relazioni}")
    # ogni relazione compare una volta sola (simmetrica, vista da entrambi i lati)
    assert len(g["links"]) == 2, g["links"]


def test_idempotente_su_grafo_minimo(tmp_path, monkeypatch):
    g_path = tmp_path / "graph.json"
    db_path = tmp_path / "iching.db.json"
    g_path.write_text(json.dumps(_grafo_minimo()), encoding="utf-8")
    db_path.write_text(json.dumps(_db_minimo()), encoding="utf-8")
    monkeypatch.setattr(air, "GRAPH", str(g_path))
    monkeypatch.setattr(air, "DB", str(db_path))
    monkeypatch.setattr(sys, "argv", ["apply_iching_relations.py"])

    air.main()
    dopo_primo = json.loads(g_path.read_text(encoding="utf-8"))
    air.main()
    dopo_secondo = json.loads(g_path.read_text(encoding="utf-8"))

    assert len(dopo_primo["links"]) == len(dopo_secondo["links"]), \
        "il secondo lancio ha aggiunto archi: non e idempotente"


def test_dry_run_non_scrive(tmp_path, monkeypatch, capsys):
    g_path = tmp_path / "graph.json"
    db_path = tmp_path / "iching.db.json"
    originale = json.dumps(_grafo_minimo())
    g_path.write_text(originale, encoding="utf-8")
    db_path.write_text(json.dumps(_db_minimo()), encoding="utf-8")
    monkeypatch.setattr(air, "GRAPH", str(g_path))
    monkeypatch.setattr(air, "DB", str(db_path))
    monkeypatch.setattr(sys, "argv", ["apply_iching_relations.py", "--dry-run"])

    air.main()
    assert g_path.read_text(encoding="utf-8") == originale, \
        "--dry-run ha scritto sul file"


def test_non_e_cablato_in_rebuild_all():
    """Sperimentale per scelta: rebuild_all.py non deve invocarlo di default."""
    testo = (ROOT / "tools" / "rebuild_all.py").read_text(encoding="utf-8")
    assert "apply_iching_relations" not in testo
