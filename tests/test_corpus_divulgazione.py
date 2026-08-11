# -*- coding: utf-8 -*-
"""
Guardie sulla separazione tra OPINIONE FIRMATA e MODELLO IMPERSONALE.

Il corpus di articoli pubblicati porta posizioni, simpatie, un modo di guardare. AION
e' l'opposto per costruzione: un'architettura di ragionamento che deve valere a
prescindere da chi la usa. Se il primo entra nel secondo, AION smette di essere quello
che dichiara di essere — e nessuno se ne accorge leggendo, perche' il testo resta
plausibile.

E' gia' successo una volta: due note del corpus erano finite in raw/aion/ con wikilink
verso aion-oracle, creando quattro archi dal materiale d'opinione al modello. Questi
test esistono perche' non succeda in silenzio una seconda volta.
"""
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.frontmatter import dividi  # noqa: E402

PREFISSO = "universalis-"
AREE_AMMESSE = {"divulgazione", "finanza"}
GRAFO = os.path.join(ROOT, "graphify-out", "graph.json")


def note_del_corpus():
    """Ogni nota-fonte del corpus, come percorso relativo con separatori POSIX."""
    trovate = []
    for radice, _, file in os.walk(os.path.join(ROOT, "raw")):
        for f in file:
            if f.startswith(PREFISSO) and f.endswith(".md"):
                rel = os.path.relpath(os.path.join(radice, f), ROOT)
                trovate.append(rel.replace("\\", "/"))
    return sorted(trovate)


def test_il_corpus_esiste():
    note = note_del_corpus()
    assert len(note) >= 17, f"attese almeno 17 note del corpus, trovate {len(note)}"


def test_il_corpus_vive_solo_in_due_aree():
    """Opinione firmata: sta dove la soggettivita' e' dichiarata (divulgazione) o dove
    il contenuto e' materia di dominio verificabile (finanza). Mai altrove."""
    fuori = [n for n in note_del_corpus() if n.split("/")[1] not in AREE_AMMESSE]
    assert not fuori, f"note del corpus fuori dalle aree ammesse: {fuori}"


def test_nessuna_nota_del_corpus_e_in_aion():
    """La regola piu' importante, resa esplicita anche se implicata dalla precedente:
    il materiale d'opinione non entra nel modello impersonale."""
    dentro = [n for n in note_del_corpus() if n.startswith("raw/aion/")]
    assert not dentro, f"opinione firmata dentro AION: {dentro}"


def test_nessun_wikilink_dal_corpus_verso_aion():
    """Un wikilink e' un arco del grafo: basta quello per collegare le due cose."""
    colpevoli = {}
    for n in note_del_corpus():
        with open(os.path.join(ROOT, n), encoding="utf-8") as f:
            link = re.findall(r"\[\[([^\]]+)\]\]", f.read())
        verso_aion = [x for x in link if x.startswith("aion-")]
        if verso_aion:
            colpevoli[n] = verso_aion
    assert not colpevoli, f"wikilink dal corpus verso AION: {colpevoli}"


@pytest.mark.skipif(not os.path.exists(GRAFO), reason="graph.json assente")
def test_nessun_arco_del_grafo_lega_il_corpus_ad_aion():
    """La verifica che conta davvero: non l'intenzione, ma il grafo costruito."""
    with open(GRAFO, encoding="utf-8") as f:
        g = json.load(f)
    per_id = {n["id"]: (n.get("source_file") or "").replace("\\", "/") for n in g["nodes"]}
    cattivi = []
    for e in g["links"]:
        a, b = per_id.get(e.get("source"), ""), per_id.get(e.get("target"), "")
        for x, y in ((a, b), (b, a)):
            if PREFISSO in os.path.basename(x) and ("raw/aion/" in y or "wiki/aion/" in y):
                cattivi.append(f"{x} --{e.get('relation')}--> {y}")
    assert not cattivi, "archi tra corpus d'opinione e AION:\n  " + "\n  ".join(cattivi)


def test_nessun_ponte_curato_tra_divulgazione_e_aion():
    """I ponti sono archi dichiarati a mano: la separazione va tenuta anche li'."""
    with open(os.path.join(ROOT, "engine", "bridges.json"), encoding="utf-8") as f:
        ponti = json.load(f)["bridges"]
    cattivi = [p["concetto"] for p in ponti
               if {p["from"]["area"], p["to"]["area"]} == {"divulgazione", "aion"}]
    assert not cattivi, f"ponti tra divulgazione e AION: {cattivi}"


def test_ogni_nota_dichiara_l_area_in_cui_vive():
    """Front-matter e cartella devono coincidere: se divergono, il router e le
    metriche contano una cosa e l'utente ne legge un'altra."""
    disallineate = {}
    for n in note_del_corpus():
        with open(os.path.join(ROOT, n), encoding="utf-8") as f:
            meta, _ = dividi(f.read())
        dichiarata = (meta or {}).get("area")
        cartella = n.split("/")[1]
        if dichiarata != cartella:
            disallineate[n] = f"front-matter '{dichiarata}' ma cartella '{cartella}'"
    assert not disallineate, f"area dichiarata != cartella: {disallineate}"


def test_ogni_nota_porta_la_sua_fonte():
    """Senza URL nel front-matter la nota non e' piu' risalibile all'articolo."""
    senza = []
    for n in note_del_corpus():
        with open(os.path.join(ROOT, n), encoding="utf-8") as f:
            meta, _ = dividi(f.read())
        if not str((meta or {}).get("source", "")).startswith("http"):
            senza.append(n)
    assert not senza, f"note del corpus senza URL di origine: {senza}"
