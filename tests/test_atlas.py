# -*- coding: utf-8 -*-
"""
Guardie sulla terza vista del grafo (tools/build_atlas_view.py).

L'atlante vale solo se la posizione SIGNIFICA. Un layout che sbaglia lo strato o
lo spicchio non e brutto: e' una bugia disegnata, e nessuno se ne accorge
guardando. Questi test verificano le tre promesse dichiarate nell'intestazione
del tool — altezza=strato, spicchio=area, raggio=centralita — piu le due
proprieta che tengono la vista utilizzabile nel tempo: determinismo e assenza di
dipendenze esterne (deve aprirsi offline, da file://).
"""
import json
import math
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

atlas = pytest.importorskip("tools.build_atlas_view")

GRAFO = os.path.join(ROOT, "graphify-out", "graph.json")
pytestmark = pytest.mark.skipif(not os.path.exists(GRAFO),
                                reason="graph.json assente: serve 'graphify update .'")


@pytest.fixture(scope="module")
def dati():
    return atlas.costruisci()


def _angolo(n):
    """Angolo del nodo nel piano, normalizzato in [0, 2pi)."""
    return math.atan2(n["z"], n["x"]) % (2 * math.pi)


def _delta_angolare(a, b):
    """Differenza angolare minima tra due angoli (il cerchio si richiude)."""
    d = abs(a - b) % (2 * math.pi)
    return min(d, 2 * math.pi - d)


def test_ogni_file_del_grafo_ha_un_posto(dati):
    """Nessun file resta fuori dall'atlante: una vista parziale e' peggio di
    nessuna vista, perche' non si vede cosa manca."""
    with open(GRAFO, encoding="utf-8") as f:
        g = json.load(f)
    sorgenti = {(n.get("source_file") or "").replace("\\", "/")
                for n in g["nodes"] if n.get("source_file")}
    assert len(dati["nodi"]) == len(sorgenti)
    assert {n["f"] for n in dati["nodi"]} == sorgenti


def test_altezza_corrisponde_allo_strato(dati):
    """La quota di un nodo deve stare nella fascia del suo strato. Il rilievo
    interno (micro-quota per community) non puo' invadere lo strato vicino: gli
    strati distano 2.0, il rilievo massimo dichiarato e' 0.15."""
    for n in dati["nodi"]:
        atteso = atlas.STRATI[n["s"]]["y"]
        assert abs(n["y"] - atteso) <= 0.16, f"{n['f']} fuori dallo strato {n['s']}"


def test_lo_strato_segue_la_cartella(dati):
    """La regola dichiarata: raw->fonti, wiki->sapere, motore, uso."""
    per_file = {n["f"]: n["s"] for n in dati["nodi"]}
    for percorso, strato in per_file.items():
        testa = percorso.split("/")[0]
        if testa == "raw":
            assert strato == "fonti"
        elif testa == "wiki":
            assert strato == "sapere"
        elif testa in atlas.CARTELLE_MOTORE:
            assert strato == "motore"
        else:
            assert strato == "uso"


def test_ogni_area_sta_nel_suo_spicchio(dati):
    """Due nodi di aree diverse non possono trovarsi nello stesso settore: se
    accade, la lettura angolare dell'atlante e' falsa."""
    aree = dati["aree"]
    passo = 2 * math.pi / len(aree)
    meta = (passo * 0.80) / 2                      # semiampiezza dello spicchio
    for n in dati["nodi"]:
        centro = (aree.index(n["a"]) / len(aree)) * 2 * math.pi
        scarto = _delta_angolare(_angolo(n), centro)
        assert scarto <= meta + 1e-6, f"{n['f']} ({n['a']}) fuori dal suo spicchio"


def test_i_nodi_connessi_stanno_piu_vicino_allasse(dati):
    """Il raggio deve essere monotono nel rango di centralita, dentro ogni
    gruppo (area, strato). E' la promessa che rende utile volare verso il centro."""
    gruppi = {}
    for n in dati["nodi"]:
        gruppi.setdefault((n["a"], n["s"]), []).append(n)
    controllati = 0
    for gruppo in gruppi.values():
        if len(gruppo) < 3:
            continue
        ordinati = sorted(gruppo, key=lambda n: (-n["g"], n["f"]))
        raggi = [math.hypot(n["x"], n["z"]) for n in ordinati]
        assert raggi == sorted(raggi), "il raggio non segue il rango di centralita"
        assert atlas.R_MIN - 1e-6 <= raggi[0]
        assert raggi[-1] <= atlas.R_MAX + 1e-6
        controllati += 1
    assert controllati >= 3, "troppo pochi gruppi per considerare provata la regola"


def test_archi_puntano_a_nodi_esistenti(dati):
    n = len(dati["nodi"])
    for e in dati["archi"]:
        assert 0 <= e["a"] < n and 0 <= e["b"] < n
        assert e["a"] != e["b"]
    coppie = {(min(e["a"], e["b"]), max(e["a"], e["b"]), e["r"]) for e in dati["archi"]}
    assert len(coppie) == len(dati["archi"]), "archi duplicati: la linea sarebbe disegnata due volte"


def test_la_provenienza_sale_di_uno_strato(dati):
    """Gli archi 'derived_from' collegano una fonte al sapere che ne deriva:
    devono essere VERTICALI. Se diventassero orizzontali, la catena fonte->
    conoscenza non sarebbe piu' leggibile a colpo d'occhio."""
    prov = [e for e in dati["archi"] if e["r"] == "derived_from"]
    assert prov, "nessun arco di provenienza: apply_provenance.py non ha girato?"
    for e in prov:
        a, b = dati["nodi"][e["a"]], dati["nodi"][e["b"]]
        assert a["s"] != b["s"], f"provenienza piatta tra {a['f']} e {b['f']}"


def test_costruzione_deterministica():
    """Stesso grafo, stesso atlante. Senza questo, ogni rebuild sporca il diff
    di git e la CI non puo' piu' distinguere un cambiamento vero dal rumore."""
    uno = json.dumps(atlas.costruisci(), sort_keys=True)
    due = json.dumps(atlas.costruisci(), sort_keys=True)
    assert uno == due


def test_pagina_autosufficiente(tmp_path):
    """Nessuna CDN, nessun font remoto, nessuna chiamata di rete: l'atlante deve
    aprirsi da file:// su una macchina staccata da internet."""
    subprocess.run([sys.executable, "tools/build_atlas_view.py"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    with open(atlas.OUT, encoding="utf-8") as f:
        pagina = f.read()
    for vietato in ("https://", "http://", "<script src", "<link rel=\"stylesheet\"",
                    "@import", "fetch(", "XMLHttpRequest"):
        assert vietato not in pagina, f"dipendenza esterna nella pagina: {vietato}"
    assert "__DATI__" not in pagina, "segnaposto dei dati non sostituito"
    assert "__R_MIN__" not in pagina and "__R_MAX__" not in pagina


def test_la_porta_apre_le_tre_viste():
    """graphify-out/index.html deve linkare file che esistono davvero: una porta
    che si apre sul vuoto e' peggio di nessuna porta."""
    indice = pytest.importorskip("tools.build_views_index")
    subprocess.run([sys.executable, "tools/build_views_index.py"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    pagina = open(indice.USCITA, encoding="utf-8").read()
    for vista in indice.VISTE:
        assert f'href="{vista["file"]}"' in pagina, f"{vista['file']} non linkato"
        assert os.path.exists(os.path.join(ROOT, "graphify-out", vista["file"]))
    # i link sono RELATIVI: la porta deve funzionare aperta da file://
    assert "https://" not in pagina and "http://" not in pagina
    # i numeri vengono dal grafo, non da un segnaposto
    assert "216" in pagina or str(len(atlas.costruisci()["nodi"])) in pagina


def test_la_porta_e_deterministica():
    indice = pytest.importorskip("tools.build_views_index")
    uno = indice.html(indice.numeri())
    due = indice.html(indice.numeri())
    assert uno == due
