# -*- coding: utf-8 -*-
"""
Guardie sui CONTRATTI di un brain: i file che lo definiscono hanno uno schema.

IL DIFETTO CHE CHIUDONO. Aree, manifesto, ponti, provenienza, registro delle
esperienze e front-matter erano descritti in prosa o solo nel codice. Per riprodurre
il sistema bisognava leggere i tool, e le chiavi mescolavano due convenzioni
(version/schema_version, description/descrizione, areas/aree). Il router era un
secondo registro delle aree, e nel brain aion ne aveva una in piu' del primo.

Dal formato 1.1: gli schemi stanno in schema/, un solo registro delle aree, e ogni
contratto apre con schema_version e descrizione. I brain passano da un formato
all'altro con tools/brain_upgrade.py, che migra i file e annulla tutto se la
pipeline fallisce.
"""
import json
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import validate_contracts as vc  # noqa: E402
from tools.brain import BRAIN  # noqa: E402

pytest.importorskip("jsonschema", reason="gli schemi si verificano in CI")


def test_il_brain_attivo_rispetta_i_suoi_contratti():
    errori, _ = vc.verifica(BRAIN)
    assert not errori, "contratti violati:\n  " + "\n  ".join(errori[:15])


def test_ogni_contratto_ha_il_suo_schema():
    attesi = {"areas", "brain", "brains", "bridges", "provenance", "lesson", "frontmatter"}
    presenti = {p.name.replace(".schema.json", "") for p in (ROOT / "schema").glob("*.schema.json")}
    assert attesi <= presenti, f"schemi mancanti: {sorted(attesi - presenti)}"
    for p in (ROOT / "schema").glob("*.schema.json"):
        json.loads(p.read_text(encoding="utf-8"))


def _brain_minimo(tmp_path, aree=None, lezioni=(), note=None):
    b = tmp_path / "b"
    (b / "engine").mkdir(parents=True)
    (b / "raw" / "alfa").mkdir(parents=True)
    (b / "brain.json").write_text(json.dumps(
        {"schema_version": 1, "nome": "b", "motore": "1.1.0"}), encoding="utf-8")
    (b / "areas.json").write_text(json.dumps(aree or {
        "schema_version": 1,
        "areas": [{"id": "alfa", "label": "Alfa", "status": "active", "keywords": ["alfa"]}]}),
        encoding="utf-8")
    (b / "engine" / "lessons.jsonl").write_text(
        "".join(json.dumps(x) + "\n" for x in lezioni), encoding="utf-8")
    for nome, testo in (note or {}).items():
        (b / "raw" / "alfa" / nome).write_text(testo, encoding="utf-8")
    return str(b)


def test_un_brain_corretto_passa(tmp_path):
    errori, _ = vc.verifica(_brain_minimo(tmp_path))
    assert not errori, errori


def test_una_chiave_sconosciuta_nel_front_matter_viene_vista(tmp_path):
    """Il caso che ha motivato gli schemi: 'reviwed' spegneva in silenzio la freschezza."""
    b = _brain_minimo(tmp_path, note={"n.md": "---\ndate: 2026-01-01\narea: alfa\n"
                                             "reviwed: 2026-02-01\n---\ntesto\n"})
    errori, _ = vc.verifica(b)
    assert any("reviwed" in e for e in errori), errori


def test_una_regola_senza_allora_viene_vista(tmp_path):
    """Una regola con l'appiglio ma senza 'allora' non dice cosa fare: il digest la
    scarterebbe in silenzio."""
    b = _brain_minimo(tmp_path, lezioni=[{
        "ts": "2026-09-25T10:00:00", "skill": "x", "domanda": "y", "esito": "utile",
        "quando": "succede z", "ancora": "test: tests/test_x.py", "ancora_tipo": "test"}])
    errori, _ = vc.verifica(b)
    assert any("allora" in e for e in errori), errori


def test_un_ponte_verso_un_area_inesistente_viene_visto(tmp_path):
    b = _brain_minimo(tmp_path)
    pathlib.Path(b, "engine", "bridges.json").write_text(json.dumps({
        "schema_version": 1, "bridges": [{"concetto": "c", "from": {"area": "alfa", "page": "p"},
                                          "to": {"area": "fantasma", "page": "q"}}]}),
        encoding="utf-8")
    errori, _ = vc.verifica(b)
    assert any("fantasma" in e for e in errori), errori


def test_la_migrazione_1_1_porta_il_router_nelle_aree(tmp_path):
    from tools import brain_upgrade
    b = tmp_path / "vecchio"
    (b / "engine").mkdir(parents=True)
    (b / "areas.json").write_text(json.dumps({
        "version": 1, "description": "vecchio formato", "convention": {"id": "kebab"},
        "areas": [{"id": "alfa", "label": "Alfa", "status": "active"}]}), encoding="utf-8")
    (b / "engine" / "router.json").write_text(json.dumps({
        "schema_version": 1, "aree": {"alfa": {"keywords": ["alfa", "prima"], "budget_default": 900},
                                       "core": {"keywords": ["server"]}}}), encoding="utf-8")
    (b / "engine" / "provenance.json").write_text(json.dumps({
        "description": "catena", "ancoraggi_area": [], "mappe_dirette": []}), encoding="utf-8")
    brain_upgrade.migra_1_1(str(b))
    aree = json.loads((b / "areas.json").read_text(encoding="utf-8"))
    assert list(aree)[:2] == ["schema_version", "descrizione"], "intestazione non uniforme"
    assert aree["areas"][0]["keywords"] == ["alfa", "prima"] and aree["areas"][0]["budget"] == 900
    assert not (b / "engine" / "router.json").exists(), "il secondo registro e' rimasto"
    prov = json.loads((b / "engine" / "provenance.json").read_text(encoding="utf-8"))
    assert prov["schema_version"] == 1 and prov["descrizione"] == "catena"


def test_il_server_instrada_con_le_parole_chiave_delle_aree():
    """Dopo la migrazione il router non c'e' piu': le parole chiave vengono da areas.json,
    e le domande sull'infrastruttura vanno comunque al contenitore 'core'."""
    sys.path.insert(0, str(ROOT / "server"))
    os.environ.setdefault("ALTAIR_API_TOKEN", "t")
    import brain_core
    tab = brain_core.load_router()["aree"]
    assert "core" in tab, "le domande sull'infrastruttura non hanno piu' una destinazione"
    aree = json.loads((pathlib.Path(brain_core.BRAIN) / "areas.json").read_text(encoding="utf-8"))
    con_parole = [a["id"] for a in aree["areas"] if a.get("keywords")]
    assert set(con_parole) <= set(tab), "aree con parole chiave che il server non instrada"
