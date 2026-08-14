# -*- coding: utf-8 -*-
"""
Guardie sull'anello di apprendimento: dalla conversazione al prior del ragionamento.

IL DIFETTO CHE HANNO CHIUSO. Il passo 0 di engine/aion-reasoner.md — "consulta le
lezioni apprese", il punto in cui il feedback rientra nel ragionamento — puntava a
graphify-out/reflections/LESSONS.md, un file di 495 byte fermo da sei settimane,
mentre il digest vero cresceva in engine/LESSONS.md. L'anello era APERTO proprio dove
doveva chiudersi, e nulla lo segnalava: il sistema sembrava imparare e non imparava.

I due pericoli che questi test tengono a bada valgono piu' del difetto:

1. AUTOFAGIA. Un brain che impara dalla prosa che il modello stesso ha scritto
   amplifica i propri errori a ogni giro. La difesa non e' filtrare meglio: e'
   pretendere un APPIGLIO ESTERNO — un test, un errore, una misura, una correzione
   dell'utente, una guardia che ha fermato qualcosa. Senza, resta osservazione.

2. CONTEXT ROT. Il prior viene letto prima di OGNI risposta. Se cresce senza limite,
   ogni domanda paga un pedaggio crescente e la qualita' cala ovunque, senza sintomi.
   Una memoria che dura non ricorda tutto: resta della stessa dimensione mentre
   l'esperienza cresce.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

import pathlib as _pl
try:
    from tools.brain import BRAIN as _b
    BRAIN = _pl.Path(_b) if isinstance(ROOT, _pl.Path) else _b
except ImportError:
    BRAIN = ROOT

sys.path.insert(0, str(ROOT))

PRIOR = BRAIN / "engine" / "LESSONS.md"
REGISTRO = BRAIN / "engine" / "lessons.jsonl"
REASONER = BRAIN / "engine" / "aion-reasoner.md"


def registrazioni():
    return [json.loads(r) for r in REGISTRO.read_text(encoding="utf-8").splitlines() if r.strip()]


# --------------------------------------------------------------- l'anello chiuso
def test_il_reasoner_legge_il_prior_che_viene_davvero_generato():
    """Il difetto originale: produzione e consumo puntavano a due file diversi."""
    testo = REASONER.read_text(encoding="utf-8")
    assert "engine/LESSONS.md" in testo, \
        "il passo 0 non nomina il file che tools/lessons_digest.py genera"
    # Solo le ISTRUZIONI del passo 0: la nota storica (righe che iniziano con '>')
    # cita di proposito il percorso morto, per spiegare perche' la regola esiste.
    passo0 = testo.split("### 0.")[1].split("### 1.")[0]
    istruzioni = [r for r in passo0.splitlines() if not r.strip().startswith(">")]
    assert "graphify-out/reflections/LESSONS.md" not in "\n".join(istruzioni), \
        "il passo 0 istruisce ancora a leggere il percorso morto"


def test_ogni_regola_del_registro_arriva_nel_prior():
    """Se una regola resta nel registro e non compare nel prior, l'anello e aperto:
    il brain ha imparato qualcosa che poi non rilegge mai.

    Il controllo e sul CONTENUTO, non sull'orario: confrontare gli mtime rendeva
    rosso il test ogni volta che si registrava una lezione prima di consolidarla,
    e un test che si lamenta di routine insegna a ignorare i test."""
    assert PRIOR.exists() and REGISTRO.exists()
    testo = PRIOR.read_text(encoding="utf-8")
    superate = {v["supera"] for v in registrazioni() if v.get("supera")}
    attese = [v for v in registrazioni()
              if v.get("ancora") and v.get("allora") and v.get("ts") not in superate]
    mancanti = [v["allora"][:50] for v in attese if v["allora"] not in testo]
    assert not mancanti, (
        "regole registrate ma assenti dal prior: " + " | ".join(mancanti) +
        "\nrimedio:  python tools/lessons_digest.py")


# --------------------------------------------------------------- anti-autofagia
def test_ogni_regola_operativa_porta_un_appiglio_esterno():
    """La regola che impedisce al brain di imparare da se stesso."""
    testo = PRIOR.read_text(encoding="utf-8")
    if "## Regole operative" not in testo:
        pytest.skip("nessuna regola operativa ancora consolidata")
    blocco = testo.split("## Regole operative")[1].split("\n## ")[0]
    regole = [r for r in blocco.splitlines() if r.startswith("- **Quando**")]
    appigli = [r for r in blocco.splitlines() if "appiglio:" in r]
    assert len(regole) == len(appigli), \
        f"{len(regole)} regole ma {len(appigli)} appigli: qualcuna e senza prova"


def test_i_tipi_di_ancora_sono_verificabili_da_terzi():
    """Un'ancora deve nominare qualcosa che qualcun altro puo' andare a controllare."""
    from tools.lesson_log import ANCORE, ANCORE_FORTI
    assert set(ANCORE) >= {"test", "errore", "misura", "utente", "guardia"}
    assert set(ANCORE_FORTI) <= set(ANCORE)
    for v in registrazioni():
        if v.get("ancora"):
            assert v.get("ancora_tipo") in ANCORE, f"tipo di ancora ignoto: {v}"
            assert len(v["ancora"].split(":", 1)[-1].strip()) >= 8, \
                f"ancora troppo vaga per essere verificata: {v['ancora']!r}"


def test_senza_ancora_resta_osservazione(tmp_path):
    """Prova eseguita: una registrazione senza appiglio non diventa regola."""
    amb = dict(os.environ); amb["PYTHONIOENCODING"] = "utf-8"
    esito = subprocess.run(
        [sys.executable, "tools/lesson_log.py", "--skill", "manuale",
         "--domanda", "prova del vincolo di ancoraggio",
         "--allora", "questa regola non deve entrare nel prior",
         "--ts", "1999-01-01T00:00:00"],
        cwd=str(ROOT), capture_output=True, env=amb)
    try:
        assert esito.returncode == 0
        assert "osservazione registrata" in esito.stdout.decode("utf-8", "replace")
        ultima = registrazioni()[-1]
        assert ultima["livello"] == "osservazione"
        assert not ultima.get("ancora")
    finally:                                   # il registro e append-only: si ripulisce
        righe = [r for r in REGISTRO.read_text(encoding="utf-8").splitlines()
                 if r.strip() and "1999-01-01T00:00:00" not in r]
        REGISTRO.write_text("\n".join(righe) + "\n", encoding="utf-8", newline="\n")


def test_ancora_inventata_viene_respinta():
    """Un tipo di ancora fuori elenco non deve passare: altrimenti il vincolo
    si aggira scrivendo 'ancora: perche si'."""
    amb = dict(os.environ); amb["PYTHONIOENCODING"] = "utf-8"
    esito = subprocess.run(
        [sys.executable, "tools/lesson_log.py", "--skill", "manuale",
         "--domanda", "prova", "--ancora", "intuizione: mi sembra giusto"],
        cwd=str(ROOT), capture_output=True, env=amb)
    assert esito.returncode != 0, "un'ancora inventata e stata accettata"


# --------------------------------------------------------------- anti context rot
def test_il_prior_resta_dentro_il_suo_tetto():
    """La difesa contro il pedaggio crescente su OGNI risposta."""
    from tools.lessons_digest import MAX_KB
    peso = PRIOR.stat().st_size / 1024
    assert peso <= MAX_KB, (
        f"il prior pesa {peso:.1f} KB, oltre il tetto di {MAX_KB} KB. "
        "Viene letto prima di ogni risposta: abbassa MAX_REGOLE/RECENTI "
        "oppure supera le regole vecchie con --supera.")


def test_il_tetto_e_dichiarato_e_non_simbolico():
    """Un tetto che nessuno controlla non e un tetto."""
    from tools.lessons_digest import MAX_KB, MAX_REGOLE, RECENTI
    assert 4 <= MAX_KB <= 64, "tetto irrealistico"
    assert MAX_REGOLE <= 60 and RECENTI <= 30, \
        "le sezioni per esteso non possono crescere all'infinito"


def test_il_registro_cresce_ma_il_prior_no():
    """La proprieta' che rende il sistema durevole: l'esperienza si accumula nel
    registro append-only, il prior resta limitato. Se il prior fosse proporzionale
    al registro, il sistema si strozzerebbe da solo crescendo."""
    n = len(registrazioni())
    peso = PRIOR.stat().st_size / 1024
    assert n >= 20, "registro troppo piccolo per considerare provata la proprieta"
    assert peso / n < 1.0, \
        f"il prior cresce ~1 KB per registrazione ({peso:.1f} KB / {n}): non e limitato"


# --------------------------------------------------------------- bi-temporalita
def test_una_regola_superata_esce_dal_prior_ma_resta_nel_registro():
    """Una lezione che si rivela sbagliata non si cancella: si supera. La storia
    resta consultabile, il prior porta solo cio' che vale adesso."""
    ts_superati = {v["supera"] for v in registrazioni() if v.get("supera")}
    if not ts_superati:
        pytest.skip("nessuna regola ancora superata")
    testo = PRIOR.read_text(encoding="utf-8")
    for v in registrazioni():
        if v.get("ts") in ts_superati and v.get("allora"):
            assert v["allora"] not in testo, \
                f"una regola superata e ancora nel prior: {v['allora'][:60]}"
