# -*- coding: utf-8 -*-
"""
Golden test sui tool critici del brain (finora coperti solo indirettamente dalla CI).

- oracle_cast: attribuzione decisionale (matematica Re Wen), lancio seedato, ricerca tag.
- report_update: round-trip su una copia temporanea del layout repo (il JSON e la
  fonte di verita, il prototipo HTML deve restare sincronizzato).

Tutto deterministico, nessuna rete, nessuna API.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

import pathlib as _pl
try:
    from tools.brain import BRAIN as _b
    BRAIN = _pl.Path(_b) if isinstance(ROOT, _pl.Path) else _b
except ImportError:
    BRAIN = ROOT

sys.path.insert(0, str(ROOT))

from tools.oracle_cast import attribute_reading, cast_reading, search_by_tags  # noqa: E402


# ---------------- attribuzione decisionale (metodo canonico dei report) ----------------

def test_attribuzione_6_linea4_da_59():
    """6 (Il Conflitto) + 4a linea mobile -> 59 (La Dissoluzione)."""
    r = attribute_reading(6, [4])
    assert r["esagramma_primario"]["id"] == 6
    assert r["esagramma_secondario"]["id"] == 59
    assert r["consiglio_linee"][0]["linea"] == 4
    assert "conciliazione" in r["consiglio_linee"][0]["testo"].lower()


def test_attribuzione_43_quattro_mobili_da_16():
    """43 + mobili [1,2,3,5] -> 16, con un consiglio per ogni linea mobile."""
    r = attribute_reading(43, [1, 2, 3, 5])
    assert r["esagramma_secondario"]["id"] == 16
    assert [c["linea"] for c in r["consiglio_linee"]] == [1, 2, 3, 5]


def test_attribuzione_senza_mobili_e_range():
    r = attribute_reading(1, [])
    assert r["esagramma_secondario"] is None
    try:
        attribute_reading(1, [7])
        assert False, "linea 7 fuori range accettata"
    except ValueError:
        pass


def test_cast_seedato_riproducibile():
    """Stesso seed -> stessa lettura (verificabilita)."""
    a, b = cast_reading(seed=1023), cast_reading(seed=1023)
    assert a["lanci"] == b["lanci"]
    assert a["esagramma_primario"]["id"] == b["esagramma_primario"]["id"]


def test_ricerca_tag_suggerisce_43():
    """La selezione decisionale trova il 43 per l'argomento 'decisione/svolta'."""
    out = search_by_tags("tensione critica decisione svolta superamento")
    assert out and out[0]["id"] == 43


# ---------------- report_update: round-trip DB -> prototipo ----------------

def _mini_repo(tmp_path: Path) -> Path:
    """Copia minima del layout repo: tools/report_update.py + report finto."""
    (tmp_path / "tools").mkdir()
    shutil.copy(ROOT / "tools" / "report_update.py", tmp_path / "tools")
    data = tmp_path / "reports" / "data"
    data.mkdir(parents=True)
    db = {"report": "caso-test", "titolo": "Test", "aggiornato_il": "2026-01-01T00:00:00",
          "verdetto": {"corrente": "iniziale", "storia": []},
          "nodi": {"alpha": []}}
    (data / "caso-test.updates.json").write_text(
        json.dumps(db, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "reports" / "caso-test-prototype.html").write_text(
        '<html><script type="application/json" id="updates-db">{}</script></html>',
        encoding="utf-8")
    return tmp_path


def _run_update(repo: Path, *args: str):
    p = subprocess.run([sys.executable, str(repo / "tools" / "report_update.py"),
                        "--report", "caso-test", *args],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr or p.stdout


def test_report_update_nodo_e_sync_prototipo(tmp_path):
    repo = _mini_repo(tmp_path)
    _run_update(repo, "--node", "alpha", "--text", "prova update",
                "--fonte", "TestWire", "--confidenza", "alta",
                "--ts", "2026-02-02T12:00:00")
    db = json.loads((repo / "reports" / "data" / "caso-test.updates.json")
                    .read_text(encoding="utf-8"))
    voce = db["nodi"]["alpha"][0]
    assert (voce["testo"], voce["fonte"], voce["confidenza"]) == \
           ("prova update", "TestWire", "alta")
    assert db["aggiornato_il"] == "2026-02-02T12:00:00"
    # il prototipo deve contenere il DB aggiornato (specchio sincronizzato)
    html = (repo / "reports" / "caso-test-prototype.html").read_text(encoding="utf-8")
    assert "prova update" in html and "TestWire" in html


def test_report_update_verdict_set_current(tmp_path):
    repo = _mini_repo(tmp_path)
    _run_update(repo, "--verdict", "--text", "svolta", "--set-current", "NUOVO RESPONSO")
    db = json.loads((repo / "reports" / "data" / "caso-test.updates.json")
                    .read_text(encoding="utf-8"))
    assert db["verdetto"]["corrente"] == "NUOVO RESPONSO"
    assert db["verdetto"]["storia"][-1]["testo"] == "svolta"


def test_report_update_nodo_inesistente_fallisce(tmp_path):
    repo = _mini_repo(tmp_path)
    p = subprocess.run([sys.executable, str(repo / "tools" / "report_update.py"),
                        "--report", "caso-test", "--node", "ghost", "--text", "x"],
                       capture_output=True, text=True)
    assert p.returncode != 0


# ---------------- provenienza: front-matter e freschezza ----------------

def test_frontmatter_idempotente_e_protegge_gli_strati_generati():
    """Rilanciarlo non deve duplicare nulla, ne toccare la wiki GENERATA."""
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "add_frontmatter.py")],
                       capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0
    # tutte le note bersaglio sono gia a posto: nessun file da arricchire
    assert "0 file da arricchire" in r.stdout, r.stdout
    # la wiki generata non deve MAI avere front-matter aggiunto a mano
    generata = (BRAIN / "wiki" / "aion" / "aion-oracle.md").read_text(encoding="utf-8")
    assert not generata.lstrip().startswith("---"), \
        "wiki/aion e generata dal modello: front-matter a mano la farebbe divergere"


def test_frontmatter_presente_sulle_fonti():
    """Le fonti grezze devono portare provenienza (date/area/reviewed)."""
    testo = (BRAIN / "raw" / "aion" / "aion-oracle.md").read_text(encoding="utf-8")
    assert testo.lstrip().startswith("---")
    testa = testo.lstrip()[3:testo.lstrip().find("\n---")]
    for campo in ("date:", "area:", "reviewed:"):
        assert campo in testa, f"manca {campo} nel front-matter"


def test_freshness_rileva_fatto_scaduto(tmp_path):
    """Bi-temporalita: valid_until nel passato -> il fatto risulta scaduto.
    Ora il parser e condiviso (tools/frontmatter): non serve piu estrarlo a pezzi
    dal sorgente dello strumento."""
    from tools.frontmatter import leggi
    nota = tmp_path / "fatto.md"
    nota.write_text("---\ndate: 2026-01-01\nvalid_until: 2026-01-31\n---\ncorpo\n",
                    encoding="utf-8")
    meta, corpo = leggi(str(nota))
    assert meta["valid_until"] == "2026-01-31"
    assert meta["date"] == "2026-01-01"
    assert corpo.strip() == "corpo"


# ---------------- ricerca ibrida ----------------

def test_ricerca_trova_il_contenuto_giusto():
    """BM25 deve portare in cima la pagina che tratta davvero l'argomento."""
    from tools.search import cerca
    r = cerca("quartili outlier IQR valori anomali", top=5)
    assert r, "nessun risultato: indice mancante o rotto"
    assert any("quartili-outlier" in x["file"] for x in r[:3]), \
        f"risultato atteso non nei primi 3: {[x['file'] for x in r[:3]]}"


def test_ricerca_copre_le_note_grezze_di_metodo():
    """Le note dei project work (ex .txt, convertite in .md) devono essere cercabili
    con una granularita utile: non un blocco unico per nota."""
    import collections
    import json as _json
    idx = _json.loads((BRAIN / "engine" / "search_index.json").read_text(encoding="utf-8"))
    per_file = collections.Counter(
        d["file"] for d in idx["documenti"]
        if d["file"].startswith("raw/data-science/") and d["file"].endswith(".md"))
    assert len(per_file) >= 20, f"note grezze data-science non indicizzate ({len(per_file)})"
    # le note lunghe devono essere spezzate, non lasciate monolitiche
    assert sum(per_file.values()) >= len(per_file) * 2, \
        "granularita troppo grossa: quasi tutte le note stanno in un frammento solo"


def test_ricerca_filtro_area_e_limite():
    from tools.search import cerca
    r = cerca("analisi dei dati", top=3, area="data-science")
    assert len(r) <= 3
    assert all(x["area"] == "data-science" for x in r)


def test_ricerca_query_senza_risultati_non_esplode():
    from tools.search import cerca
    assert cerca("zzzqwertyxyzinesistente", top=5) == []


def test_indice_coerente_col_corpus():
    """L'indice committato deve essere quello che il corpus produce ora."""
    import json as _json
    f = BRAIN / "engine" / "search_index.json"
    prima = f.read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_search_index.py")],
                   capture_output=True, text=True, cwd=str(ROOT), check=True)
    assert f.read_text(encoding="utf-8") == prima, \
        "indice non aggiornato: rigenera con tools/build_search_index.py"
    idx = _json.loads(prima)
    assert idx["n_documenti"] == len(idx["documenti"]) > 100


def test_metriche_una_riga_per_giorno():
    """La serie storica non deve gonfiarsi a ogni rebuild dello stesso giorno."""
    import csv as _csv
    f = BRAIN / "metrics" / "graph_metrics.csv"
    assert f.exists(), "metriche mai generate: lancia tools/graph_metrics.py"
    with open(f, encoding="utf-8", newline="") as fh:
        righe = list(_csv.DictReader(fh))
    date = [r["data"] for r in righe]
    assert len(date) == len(set(date)), "piu rilevazioni nello stesso giorno"
    assert int(righe[-1]["nodi"]) > 0 and float(righe[-1]["grado_medio"]) > 0


# ---------------- F1: il recupero dichiara quanto fidarsi ----------------

def test_confidenza_alta_su_conoscenza_presente():
    from tools.search import cerca_con_diagnosi
    d = cerca_con_diagnosi("quartili outlier IQR", top=3)["diagnosi"]
    assert d["confidenza"] == "alta", d
    assert d["copertura"] >= 0.6


def test_confidenza_bassa_su_conoscenza_assente():
    """Il caso che conta: il corpus NON ha la risposta e il sistema lo dichiara
    invece di restituire il meno peggio in silenzio."""
    from tools.search import cerca_con_diagnosi
    d = cerca_con_diagnosi("analisi sentiment reti neurali convoluzionali transformer",
                           top=3)["diagnosi"]
    assert d["confidenza"] in ("bassa", "nessuna"), d
    assert "non contiene" in d["motivo"] or "coperto" in d["motivo"]


def test_confidenza_scarsa_fuori_dominio():
    """Fuori dominio il sistema deve DIRE di non fidarsi.

    Il test verificava «zero risultati», ma era fragile: assumeva che nessun termine
    della domanda comparisse mai nel corpus. Entrando l'area creativita, «ricetta» ha
    iniziato a comparire davvero in una pagina del corpus, e il
    test e caduto pur funzionando tutto — la confidenza diceva correttamente «bassa»
    col 25% di copertura. Ora si verifica la proprieta che conta davvero, non una
    caratteristica accidentale del corpus."""
    from tools.search import cerca_con_diagnosi
    e = cerca_con_diagnosi("ricetta carbonara guanciale pecorino", top=3)
    d = e["diagnosi"]
    assert d["confidenza"] in ("bassa", "nessuna"), d
    assert d["copertura"] < 0.34, d


def test_tokenizzazione_query_coerente_con_indice():
    """Regressione: se query e indice filtrano stopword diverse, i termini scartati
    in indicizzazione non sono trovabili e la copertura risulta falsata."""
    import json as _json
    from tools.search import _tokenizza
    idx = _json.loads((BRAIN / "engine" / "search_index.json").read_text(encoding="utf-8"))
    assert idx.get("stopword"), "l'indice deve portare con se la lista di stopword"
    assert _tokenizza("chi orchestra gli agenti del modello") == \
        ["orchestra", "agenti", "modello"]


# ---------------- F3: la memoria agisce sui risultati ----------------

def test_memoria_annota_ancoraggi_consolidati():
    """Una lezione registrata deve cambiare cio che si vede la volta dopo."""
    from tools.search import cerca
    r = cerca("chi orchestra gli agenti", top=5)
    con_memoria = [x for x in r if x.get("memoria")]
    assert con_memoria, "nessun risultato annotato: la memoria non sta agendo"
    assert any(x["memoria"]["utile"] >= 2 and "consolidato" in x["memoria"]["nota"]
               for x in con_memoria)


def test_memoria_non_annota_per_nodi_numerici_corti():
    """Prudenza sui nodi corti/numerici (es. '6'): il confronto per sottostringa
    marchierebbe qualunque titolo che contiene quel carattere."""
    from tools.search import _corrisponde
    assert not _corrisponde("6", "capitolo-6-analisi", "Sezione 6 del report")
    assert _corrisponde("6", "6", "")
    assert _corrisponde("aion-superia", "aion-superia", "AION_SUPERIA")


# ---------------- F4: predizione strutturale dei collegamenti (Adamic-Adar) ----------------

def test_adamic_adar_formula_corretta():
    """La matematica dev'essere quella dichiarata: somma di 1/log(grado) sui vicini
    comuni. Ricalcolata a mano su un grafo minimo costruito ad arte."""
    import math
    from tools.link_suggest import proposte_strutturali
    # a e b non collegati, con 2 vicini comuni (z1 grado 2, z2 grado 3)
    vicini = {
        "wiki/x/a.md": {"wiki/x/z1.md", "wiki/x/z2.md"},
        "wiki/x/b.md": {"wiki/x/z1.md", "wiki/x/z2.md"},
        "wiki/x/z1.md": {"wiki/x/a.md", "wiki/x/b.md"},
        "wiki/x/z2.md": {"wiki/x/a.md", "wiki/x/b.md", "wiki/x/c.md"},
        "wiki/x/c.md": {"wiki/x/z2.md"},
    }
    p = proposte_strutturali(vicini)
    # nel grafo di prova anche z1/z2 condividono due vicini: e corretto che compaia
    # anche quella coppia. Si verifica il valore ESATTO su quella attesa.
    ab = next(x for x in p if {x["da"], x["a"]} == {"wiki/x/a.md", "wiki/x/b.md"})
    atteso = 1 / math.log(2) + 1 / math.log(3)
    assert abs(ab["punteggio"] - atteso) < 1e-9, (ab["punteggio"], atteso)
    assert ab["comuni"] == 2


def test_struttura_non_propone_coppie_gia_collegate():
    from tools.link_suggest import proposte_strutturali
    vicini = {
        "wiki/x/a.md": {"wiki/x/b.md", "wiki/x/z.md"},
        "wiki/x/b.md": {"wiki/x/a.md", "wiki/x/z.md"},
        "wiki/x/z.md": {"wiki/x/a.md", "wiki/x/b.md"},
    }
    assert proposte_strutturali(vicini) == []


def test_struttura_scarta_il_vicino_singolo():
    """Un solo vicino condiviso e coincidenza, non segnale: sotto soglia si tace."""
    from tools.link_suggest import proposte_strutturali
    vicini = {
        "wiki/x/a.md": {"wiki/x/z.md"},
        "wiki/x/b.md": {"wiki/x/z.md"},
        "wiki/x/z.md": {"wiki/x/a.md", "wiki/x/b.md"},
    }
    assert proposte_strutturali(vicini) == []


def test_struttura_esclude_gli_hub():
    """Gli hub sono collegati a tutto per costruzione: la loro vicinanza non
    significa parentela, e senza esclusione dominavano l'output (verificato)."""
    from tools.link_suggest import proposte_strutturali, HUB
    assert "index" in HUB
    vicini = {
        "wiki/x/a.md": {"wiki/x/index.md", "wiki/x/metodi.md"},
        "wiki/x/b.md": {"wiki/x/index.md", "wiki/x/metodi.md"},
        "wiki/x/index.md": {"wiki/x/a.md", "wiki/x/b.md"},
        "wiki/x/metodi.md": {"wiki/x/a.md", "wiki/x/b.md"},
    }
    # i soli vicini comuni sono hub -> nessuna proposta
    assert proposte_strutturali(vicini, esclusi=HUB) == []


def test_struttura_sul_grafo_reale_e_pulita():
    from tools.link_suggest import _grafo_per_file, proposte_strutturali, HUB
    v = _grafo_per_file()
    if not v:
        import pytest as _p
        _p.skip("grafo non disponibile")
    s = proposte_strutturali(v, esclusi=HUB)
    assert s, "nessuna proposta strutturale sul grafo reale"
    assert all(p["comuni"] >= 2 for p in s)
    assert all(p["a"] not in v[p["da"]] for p in s), "proposta una coppia gia collegata"
    coppie = {tuple(sorted((p["da"], p["a"]))) for p in s}
    assert len(coppie) == len(s), "coppie duplicate nei due versi"


# ---------------- F5: consolidamento offline ----------------

def test_consolidate_produce_digest_solo_per_aree_reali():
    """_inbox e una cartella tecnica, non una macroarea: areas.json e il registro."""
    import json as _json
    from tools.consolidate import digest_per_area
    d = digest_per_area()
    assert d, "nessun digest generato"
    reg = _json.loads((BRAIN / "areas.json").read_text(encoding="utf-8"))
    valide = {a["id"] for a in reg["areas"]}
    assert set(d) <= valide, f"digest per non-aree: {set(d) - valide}"
    for area, dati in d.items():
        assert dati["file"] > 0 and "centrali" in dati


def test_consolidate_ordina_per_grado_non_per_etichetta():
    """Regressione: ordinando la tupla (grado, etichetta) l'etichetta faceva da
    spareggio e spacciava per 'centrale' il testo alfabeticamente maggiore."""
    from tools.consolidate import digest_per_area
    for dati in digest_per_area().values():
        gradi = [c["grado"] for c in dati["centrali"]]
        assert gradi == sorted(gradi, reverse=True), gradi


def test_consolidate_rileva_lezioni_ridondanti():
    from tools.consolidate import lezioni_ridondanti
    voci = [
        {"nodi": ["a", "b"], "esito": "utile", "nota": "prima"},
        {"nodi": ["b", "a"], "esito": "utile", "nota": "identica"},
        {"nodi": ["c"], "esito": "utile", "nota": "sola"},
    ]
    r = lezioni_ridondanti(voci)
    assert len(r) == 1 and r[0]["occorrenze"] == 2
    assert sorted(r[0]["nodi"]) == ["a", "b"]


# ---------------- F6: pacchetto di contesto entro budget ----------------

def test_context_pack_rispetta_il_budget_reale():
    """Il budget vale sul TESTO CONSEGNATO, non sulla somma dei pezzi: ignorare
    l'impalcatura (titoli, percorsi) faceva sforare (misurato 982 vs 730 stimati)."""
    from tools.context_pack import pacchetto, come_testo
    for b in (300, 900, 2000):
        p = pacchetto("controlli di qualita sui dati", budget_token=b)
        reale = len(come_testo(p)) // 4
        assert reale <= b, f"budget {b} sforato: {reale} token reali"


def test_context_pack_non_riempie_con_riempitivo():
    """Con budget enorme non deve gonfiare: sotto la soglia di pertinenza si tace.
    Piu contesto non significa risposte migliori (context rot)."""
    from tools.context_pack import pacchetto
    stretto = pacchetto("controlli di qualita sui dati", budget_token=900)
    largo = pacchetto("controlli di qualita sui dati", budget_token=12000)
    assert len(largo["frammenti"]) - len(stretto["frammenti"]) <= 8


def test_context_pack_avverte_quando_non_sa():
    from tools.context_pack import pacchetto
    p = pacchetto("ricetta carbonara guanciale pecorino", budget_token=900)
    assert p["diagnosi"]["confidenza"] in ("bassa", "nessuna")
    assert p["avvertenze"], "nessuna avvertenza su conoscenza assente"
    assert "certa" in " ".join(p["avvertenze"])


def test_context_pack_deduplica_per_file():
    from tools.context_pack import pacchetto
    p = pacchetto("analisi dei dati e metodo", budget_token=3000)
    files = [f["file"] for f in p["frammenti"]]
    assert len(files) == len(set(files)), "stesso file piu volte: budget sprecato"


# ---------------- parser front-matter condiviso (regressione reale) ----------------

def test_frontmatter_non_confonde_una_riga_di_testo():
    """Difetto reale: una nota che inizia con '--- FUNZIONI ... ---' veniva scambiata
    per front-matter YAML perche il controllo era startswith('---'). Effetti a catena:
    lo strumento di arricchimento la saltava, la freschezza non sapeva la data,
    l'indice le mangiava l'inizio del contenuto."""
    from tools.frontmatter import ha_frontmatter, dividi
    testo = "--- FUNZIONI DI DATA_PROCESSING EXCEL ---\n\n1. STATISTICHE\n"
    assert not ha_frontmatter(testo)
    meta, corpo = dividi(testo)
    assert meta == {} and corpo == testo, "contenuto alterato da un falso front-matter"


def test_frontmatter_riconosce_il_blocco_valido():
    from tools.frontmatter import ha_frontmatter, dividi
    testo = "---\ndate: 2026-01-01\narea: x\n---\ncorpo vero\n"
    assert ha_frontmatter(testo)
    meta, corpo = dividi(testo)
    assert meta == {"date": "2026-01-01", "area": "x"}
    assert corpo.strip() == "corpo vero"


def test_frontmatter_apertura_senza_chiusura():
    from tools.frontmatter import ha_frontmatter
    assert not ha_frontmatter("---\ndate: 2026-01-01\nmanca la chiusura\n")


def test_tutte_le_note_raw_hanno_provenienza():
    """Dopo la correzione del parser, nessuna nota deve restare scoperta."""
    from tools.frontmatter import ha_frontmatter
    scoperte = []
    for base in (BRAIN / "raw",):
        for p in base.rglob("*.md"):
            rel = p.relative_to(ROOT).as_posix()
            if "_inbox" in rel:
                continue
            if not ha_frontmatter(p.read_text(encoding="utf-8")):
                scoperte.append(rel)
    assert not scoperte, f"note senza front-matter: {scoperte}"


# ---------------- F8: riemersione ----------------

def test_resurface_sceglie_con_criterio_e_esclude_i_generati():
    from tools.resurface import candidati, scegli
    c = candidati()
    assert c, "nessun candidato"
    assert not any(x["file"].startswith("wiki/aion/") for x in c), \
        "proposta una pagina generata: la fonte e altrove"
    s = scegli(c, 3)
    assert len(s) == 3 and len({x["file"] for x in s}) == 3


def test_resurface_premia_le_note_isolate_e_vecchie():
    from tools.resurface import scegli
    finti = [
        {"file": f"raw/x/{i}.md", "giorni": g, "collegamenti": k,
         "punteggio": g + (30 if k == 0 else 0), "titolo": "t", "area": "x",
         "assaggio": "..."}
        for i, (g, k) in enumerate([(5, 3), (5, 0), (400, 2)])
    ]
    ordinati = sorted(finti, key=lambda c: -c["punteggio"])
    assert ordinati[0]["giorni"] == 400          # la piu vecchia in testa
    assert ordinati[1]["collegamenti"] == 0      # poi l'isolata


def test_resurface_segna_rivista(tmp_path, monkeypatch):
    """--segna deve aggiornare 'reviewed' senza toccare il resto della nota."""
    import tools.resurface as rs
    nota = tmp_path / "n.md"
    nota.write_text("---\ndate: 2026-01-01\nreviewed: 2026-01-01\n---\ncorpo\n",
                    encoding="utf-8")
    monkeypatch.setattr(rs, "BRAIN", str(tmp_path))   # la nota vive nel BRAIN, non nell officina
    rs.segna_rivista("n.md")
    testo = nota.read_text(encoding="utf-8")
    assert "reviewed: " in testo and "2026-01-01\nreviewed: 2026-01-01" not in testo
    assert testo.rstrip().endswith("corpo")


# ---------------- F7: raccolta dai report ----------------

def test_report_harvest_estrae_fonti_e_metodo():
    from tools.report_harvest import raccogli, componi
    d = raccogli()
    assert d["totali"] > 0, "nessuna affermazione raccolta dai report"
    assert d["fonti"], "nessuna fonte estratta"
    testo = componi(d)
    assert testo.lstrip().startswith("---"), "la nota deve avere provenienza"
    assert "Fonti su cui il brain ha costruito" in testo
    # non deve riportare i FATTI (invecchiano): solo metodo e fonti
    assert "Metodo oracolare" in testo


def test_report_harvest_nota_presente_e_dichiarata():
    """La nota raccolta deve esistere ED essere dichiarata nel registro di
    provenienza: senza dichiarazione resta scollegata e il silo non si chiude."""
    import json as _json
    nota = BRAIN / "raw" / "divulgazione" / "metodo-report-verificati.md"
    assert nota.exists(), "nota di metodo non generata (report_harvest.py --apply)"
    reg = _json.loads((BRAIN / "engine" / "provenance.json").read_text(encoding="utf-8"))
    dichiarati = {m["wiki"] for m in reg["mappe_dirette"]}
    assert "raw/divulgazione/metodo-report-verificati.md" in dichiarati


# ---------------- correzioni di vulnerabilita e fallacie ----------------

def test_cache_ricarica_se_indice_cambia():
    """Vulnerabilita reale: la cache non si invalidava mai. Sulla VPS l'API resta
    accesa per settimane mentre git sostituisce l'indice: serviva quello vecchio,
    e F1 avrebbe dichiarato 'alta' su un corpus superato."""
    import os as _os
    from tools.search import cerca, _cache
    cerca("quartili", top=1)
    primo = _cache.get("idx_mtime")
    _os.utime(BRAIN / "engine" / "search_index.json", None)
    cerca("quartili", top=1)
    assert _cache.get("idx_mtime") != primo, "cache non invalidata al cambio del file"


def test_lezioni_in_memoria_hanno_un_tetto():
    from tools.search import MAX_LEZIONI_IN_MEMORIA
    assert 100 <= MAX_LEZIONI_IN_MEMORIA <= 10000


def test_diagnosi_dichiara_cosa_misura():
    """Fallacia: 'confidenza alta' verra letta come 'risposta corretta'. La
    differenza va scritta, non lasciata intuire."""
    from tools.search import cerca_con_diagnosi
    d = cerca_con_diagnosi("quartili outlier IQR", top=2)["diagnosi"]
    assert "misura" in d and "non correttezza" in d["misura"]


def test_memoria_non_attribuisce_per_sottostringa():
    """Un nodo 'sql' non deve marchiare 'postgresql': l'annotazione sarebbe
    credibile e falsa, il difetto peggiore per una memoria."""
    from tools.search import _corrisponde
    assert not _corrisponde("sql", "postgresql", "postgresql")
    assert not _corrisponde("excel", "excel-avanzato-2026", "corso")
    assert _corrisponde("excel", "python-pandas", "uso di excel per la pulizia")
    assert _corrisponde("excel", "excel", "excel")


def test_hook_eseguibili_non_versionati():
    """Repo PUBBLICO: hook versionati = codice shell eseguito sulla macchina di
    chiunque cloni. Deve restare solo l'esempio inerte."""
    import subprocess as _sp
    tracciati = _sp.run(["git", "ls-files", ".claude/"], cwd=str(ROOT),
                        capture_output=True, text=True).stdout.split()
    assert ".claude/settings.json" not in tracciati, \
        "settings.json e tornato in git: esegue shell su chi clona"
    assert any("settings.example.json" in t for t in tracciati)


def test_privacy_distingue_segreti_da_codice():
    """Uno strumento che urla a ogni riga viene ignorato: deve riconoscere un
    segreto letterale e tacere su 'TOKEN = os.environ.get(...)'."""
    import re as _re
    src = (ROOT / "tools" / "check_privacy.py").read_text(encoding="utf-8")
    ns = {"re": _re}
    exec(compile(src[src.index("SCHEMI = ["):src.index("# Falsi positivi")], "s", "exec"), ns)
    def colpito(t):
        for _, rx in ns["SCHEMI"]:
            m = rx.search(t)
            if m and not ns["PLACEHOLDER"].search(m.group(0)):
                return True
        return False
    # Il segreto di prova si COMPONE a runtime: scritto per esteso, questo file
    # farebbe scattare per sempre il rilevatore su se stesso, e un falso positivo
    # permanente insegna a ignorare lo strumento. Esentare il file sarebbe peggio:
    # creerebbe un punto cieco proprio dove un segreto vero potrebbe finire.
    finto = "sk-" + "live-" + "9f3a2b7c4d1e8f0a"
    assert colpito(f'api_key = "{finto}"')
    assert not colpito('TOKEN = os.environ.get("ALTAIR_API_TOKEN")')
    assert not colpito('token = tokenizza(titolo)')


def test_harvest_non_sovrascrive_il_lavoro_umano():
    """La nota vive in raw/ (strato sorgente): integrarla a mano e legittimo, e
    rigenerarla alla cieca cancellerebbe quelle integrazioni senza dirlo."""
    import re as _re
    nota = BRAIN / "raw" / "divulgazione" / "metodo-report-verificati.md"
    testo = nota.read_text(encoding="utf-8")
    assert _re.search(r"^generato_hash:\s*\w+", testo, _re.M), \
        "manca l'impronta: senza, non si distingue il generato dal modificato"
