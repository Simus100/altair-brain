# -*- coding: utf-8 -*-
"""
altair-brain — crea un nuovo brain da core/, e tiene il registro di quelli esistenti.

L'ARCHITETTURA. Questo repo e' un'OFFICINA, non un brain:

    tools/ tests/ server/   il MOTORE, sorgente unica
    core/                   il PRODOTTO, generato dal motore (tools/build_core.py)
    brains/                 le ISTANZE: un brain per cartella, piu il registro

Un brain e' autosufficiente: ha i propri tool (provvisti da core/), la propria
conoscenza, il proprio grafo. Non condivide nulla con gli altri se non l'origine.
E' la ragione per cui i tool risolvono i percorsi rispetto alla cartella in cui
vivono: dentro un'istanza, `wiki/...` significa la wiki di QUEL brain.

PERCHE' ISTANZE E NON UNA CARTELLA CONDIVISA. Due brain che condividessero il motore
sarebbero legati per sempre alla stessa versione: aggiornarne uno vorrebbe dire
aggiornarli tutti, e un esperimento su uno potrebbe rompere l'altro. Provvisti da
core/, invece, ognuno si aggiorna quando decidi tu (tools/brain_sync.py).

Uso:
  python tools/brain_new.py --nome ricerca            crea brains/ricerca/
  python tools/brain_new.py --nome tesi --training aion
  python tools/brain_new.py --elenco                  mostra il registro
"""
import argparse, datetime, json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(ROOT, "core")
BRAINS = os.path.join(ROOT, "brains")
REGISTRO = os.path.join(BRAINS, "brains.json")


def _console():
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool


def leggi_registro():
    if not os.path.exists(REGISTRO):
        return {"schema_version": 1,
                "descrizione": "I brain di questo repo. Ognuno e un'istanza "
                               "autosufficiente provvista da core/.",
                "brains": []}
    with open(REGISTRO, encoding="utf-8") as f:
        return json.load(f)


def scrivi_registro(reg):
    os.makedirs(BRAINS, exist_ok=True)
    with open(REGISTRO, "w", encoding="utf-8", newline="\n") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
        f.write("\n")


def descrivi(percorso):
    """Cosa contiene davvero un brain: si conta, non si dichiara."""
    def quanti(sotto, ext=".md"):
        d = os.path.join(percorso, sotto)
        return sum(1 for r, _, fs in os.walk(d) for x in fs if x.endswith(ext)) \
            if os.path.isdir(d) else 0
    aree = []
    reg = os.path.join(percorso, "areas.json")
    if os.path.exists(reg):
        with open(reg, encoding="utf-8") as f:
            aree = [a["id"] for a in json.load(f).get("areas", [])]
    lezioni = 0
    log = os.path.join(percorso, "engine", "lessons.jsonl")
    if os.path.exists(log):
        with open(log, encoding="utf-8") as f:
            lezioni = sum(1 for r in f if r.strip())
    return {"aree": aree, "note_raw": quanti("raw"), "pagine_wiki": quanti("wiki"),
            "lezioni": lezioni}


def crea(nome, training=None):
    if not nome.replace("-", "").replace("_", "").isalnum():
        sys.exit("il nome deve essere alfanumerico (trattini e underscore ammessi)")
    dest = os.path.join(BRAINS, nome)
    if os.path.exists(dest):
        sys.exit(f"esiste gia': brains/{nome}")
    if not os.path.isdir(CORE):
        sys.exit("core/ assente: esegui prima python tools/build_core.py")

    shutil.copytree(CORE, dest)
    # Un brain nuovo non eredita l'esperienza di nessuno, nemmeno quella del core.
    for vuoto in ("engine/lessons.jsonl",):
        p = os.path.join(dest, vuoto)
        if os.path.exists(p):
            open(p, "w", encoding="utf-8").close()

    reg = leggi_registro()
    reg["brains"].append({
        "nome": nome,
        "percorso": f"brains/{nome}",
        "creato": datetime.date.today().isoformat(),
        "training": training or None,
        "origine": "core/",
    })
    scrivi_registro(reg)
    return dest


def main():
    _console()
    ap = argparse.ArgumentParser(description="Crea un brain o mostra il registro")
    ap.add_argument("--nome", help="nome del nuovo brain (cartella in brains/)")
    ap.add_argument("--training", default=None,
                    help="training da adottare (per ora: aion). Vuoto = nessuno")
    ap.add_argument("--elenco", action="store_true", help="mostra i brain esistenti")
    a = ap.parse_args()

    if a.elenco or not a.nome:
        reg = leggi_registro()
        if not reg["brains"]:
            print("Nessun brain. Creane uno:  python tools/brain_new.py --nome <nome>")
            return
        print(f"{len(reg['brains'])} brain in questo repo:\n")
        for b in reg["brains"]:
            p = os.path.join(ROOT, b["percorso"])
            d = descrivi(p) if os.path.isdir(p) else None
            stato = "" if d else "  [CARTELLA ASSENTE]"
            print(f"  {b['nome']:16} {b['percorso']:24} "
                  f"training: {b.get('training') or '—'}{stato}")
            if d:
                print(f"    {len(d['aree'])} aree · {d['note_raw']} note grezze · "
                      f"{d['pagine_wiki']} pagine curate · {d['lezioni']} lezioni")
        return

    dest = crea(a.nome, a.training)
    print(f"brain creato: brains/{a.nome}")
    print(f"  provvisto da core/ — motore, guardie, training disponibili")
    print(f"  ora:  cd brains/{a.nome} && python onboarding.py")


if __name__ == "__main__":
    main()
