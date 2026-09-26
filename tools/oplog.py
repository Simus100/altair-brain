# -*- coding: utf-8 -*-
"""
altair-brain — il registro delle OPERAZIONI di un brain (log.md, solo aggiunte).

PERCHE' ESISTE. lessons.jsonl registra l'esperienza — cosa si e' imparato. Nessuno
registrava cosa e' stato FATTO al brain e quando: creato, configurato, addestrato,
ricostruito, aggiornato, esportato, smistato. Il pattern LLM Wiki lo tiene come
log.md, cronologico e leggibile con grep; qui mancava.

TRE REGOLE, ciascuna contro un difetto gia' visto:
  - sta nella RADICE del brain (log.md), non in engine/: fuori dall'indice di
    ricerca. La ricostruzione scrive la sua riga DOPO aver costruito l'indice, e un
    log indicizzato resterebbe sempre un giro indietro — lo stesso difetto di ordine
    corretto per LESSONS.md;
  - e' tolto dal grafo (tools/graph_prune.py): e' cronaca, non conoscenza;
  - una ricostruzione che non cambia niente non aggiunge righe: il registro cresce
    quando succede qualcosa, non ogni volta che qualcuno lancia la pipeline.

Formato di una riga, pensato per grep:   - [2026-09-26] rebuild — 1201 nodi, ...

Uso:
  python tools/oplog.py ingest "3 note smistate in finanza"
  python tools/oplog.py --elenco 10
"""
import argparse, datetime, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
try:
    from tools.brain import BRAIN
except ImportError:
    BRAIN = ROOT

TIPI = ("creazione", "onboarding", "training", "ingest", "rebuild", "aggiornamento",
        "export", "correzione")
INTESTAZIONE = ("# Registro delle operazioni\n\n"
                "Cosa e' stato fatto a questo brain, e quando. Solo aggiunte: non si "
                "modifica e non si cancella. L'esperienza — cosa si e' imparato — sta in "
                "engine/lessons.jsonl; qui c'e' la cronaca.\n\n")


def percorso(brain=None):
    return os.path.join(brain or BRAIN, "log.md")


def voci(brain=None):
    p = percorso(brain)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [r.rstrip("\n") for r in f if r.startswith("- [")]


def registra(tipo, testo, brain=None):
    """Aggiunge una riga, se dice qualcosa di nuovo. Ritorna True se l'ha scritta."""
    if tipo not in TIPI:
        raise ValueError(f"tipo sconosciuto: {tipo} (ammessi: {', '.join(TIPI)})")
    testo = " ".join(str(testo).split())[:300]
    # identica all'ultima dello stesso tipo? allora non e' successo niente di nuovo
    for r in reversed(voci(brain)):
        if f"] {tipo} — " in r:
            if r.split(f"] {tipo} — ", 1)[1] == testo:
                return False
            break
    p = percorso(brain)
    nuovo = not os.path.exists(p)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        if nuovo:
            f.write(INTESTAZIONE)
        f.write(f"- [{datetime.date.today().isoformat()}] {tipo} — {testo}\n")
    return True


def main():
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass
    ap = argparse.ArgumentParser(description="Registro delle operazioni del brain")
    ap.add_argument("tipo", nargs="?", choices=TIPI)
    ap.add_argument("testo", nargs="?")
    ap.add_argument("--elenco", type=int, metavar="N", help="mostra le ultime N operazioni")
    a = ap.parse_args()
    if a.elenco or not a.tipo:
        for r in voci()[-(a.elenco or 20):]:
            print(r)
        return 0
    if not a.testo:
        sys.exit("serve una descrizione dell'operazione")
    print("registrata" if registra(a.tipo, a.testo) else "identica all'ultima: non registrata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
