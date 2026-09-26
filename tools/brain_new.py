# -*- coding: utf-8 -*-
"""
altair-brain — crea un nuovo brain, e tiene il registro di quelli esistenti.

L'ARCHITETTURA. Questo repo e' un'OFFICINA, non un brain:

    tools/ tests/ server/   il MOTORE, una volta sola, con la sua VERSION
    core/                   il PRODOTTO, generato dal motore (tools/build_core.py)
    brains/                 le ISTANZE: un brain per cartella, piu il registro

UN BRAIN E' CONOSCENZA, NON CODICE. Contiene raw/, wiki/, engine/, areas.json e un
manifesto (brain.json) che dichiara con quale versione del motore e' stato
verificato. Prima ogni brain nasceva con una copia di tools/, tests/ e server/, e
nessuno la aggiornava: in brains/aion 17 tool su 31 erano gia' diversi da core/ il
giorno dell'audit. Una copia che nessuno aggiorna non e' autonomia: e' un motore
vecchio che sembra nuovo.

Due brain restano indipendenti lo stesso: ognuno dichiara la propria versione, e
tools/brain_upgrade.py dice quando uno e' rimasto indietro. Per far girare un brain
FUORI dal repo si esporta: tools/brain_export.py gli affianca il motore della sua
versione.

Uso:
  python tools/brain_new.py --nome ricerca                      crea brains/ricerca/
  python tools/brain_new.py --nome tesi --aree "fonti,capitoli" --training aion
  python tools/brain_new.py --elenco                            mostra il registro
"""
import argparse, datetime, json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(ROOT, "core")
BRAINS = os.path.join(ROOT, "brains")
REGISTRO = os.path.join(BRAINS, "brains.json")

sys.path.insert(0, ROOT)
from tools.brain import manifesto, versione_motore  # noqa: E402

# Le parti di core/ che fanno un brain. Il resto di core/ e' motore, e il motore
# un brain dell'officina non lo porta: lo usa.
PARTI_BRAIN = ("raw", "wiki", "engine", "reports", "metrics", "areas.json")


def _console():
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool


def leggi_registro():
    if not os.path.exists(REGISTRO):
        return {"schema_version": 1,
                "descrizione": "I brain di questo repo: nome e cartella. Tutto il "
                               "resto lo dice il manifesto brain.json di ciascuno.",
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
        return sum(1 for r, _, fs in os.walk(d) for x in fs
                   if x.endswith(ext) and x != "README.md") if os.path.isdir(d) else 0
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
    man = manifesto(percorso)
    return {"aree": aree, "note_raw": quanti("raw"), "pagine_wiki": quanti("wiki"),
            "lezioni": lezioni, "training": man.get("training"),
            "motore": man.get("motore")}


def crea(nome, aree=None, training=None):
    if not nome.replace("-", "").replace("_", "").isalnum():
        sys.exit("il nome deve essere alfanumerico (trattini e underscore ammessi)")
    dest = os.path.join(BRAINS, nome)
    if os.path.exists(dest):
        sys.exit(f"esiste gia': brains/{nome}")
    if not os.path.isdir(CORE):
        sys.exit("core/ assente: esegui prima python tools/build_core.py")

    os.makedirs(dest)
    for parte in PARTI_BRAIN:
        src = os.path.join(CORE, parte)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(dest, parte),
                            ignore=shutil.ignore_patterns("__pycache__"))
        elif os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, parte))
    # Un brain nuovo non eredita l'esperienza di nessuno, nemmeno quella del core.
    open(os.path.join(dest, "engine", "lessons.jsonl"), "w", encoding="utf-8").close()
    with open(os.path.join(dest, "brain.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"schema_version": 1, "nome": nome, "motore": versione_motore(),
                   "training": None, "creato": datetime.date.today().isoformat()},
                  f, ensure_ascii=False, indent=2)
        f.write("\n")

    reg = leggi_registro()
    reg["brains"].append({"nome": nome, "percorso": f"brains/{nome}"})
    scrivi_registro(reg)
    from tools.oplog import registra
    registra("creazione", f"brain '{nome}' creato col motore {versione_motore()}", dest)

    if aree or training:
        from tools import onboarding
        if aree:
            onboarding.imposta_aree(dest, onboarding.aree_da_testo(aree))
        if training and training != "nessuno":
            if not onboarding.adotta_training(dest, training):
                sys.exit(f"training sconosciuto: {training}")
    return dest


def main():
    _console()
    ap = argparse.ArgumentParser(description="Crea un brain o mostra il registro")
    ap.add_argument("--nome", help="nome del nuovo brain (cartella in brains/)")
    ap.add_argument("--aree", default=None,
                    help="macroaree separate da virgola (altrimenti: onboarding interattivo)")
    ap.add_argument("--training", default=None,
                    help="training da adottare (per ora: aion). Vuoto = nessuno")
    ap.add_argument("--elenco", action="store_true", help="mostra i brain esistenti")
    a = ap.parse_args()

    if a.elenco or not a.nome:
        reg = leggi_registro()
        if not reg["brains"]:
            print("Nessun brain. Creane uno:  python tools/brain_new.py --nome <nome>")
            return
        print(f"{len(reg['brains'])} brain in questo repo · motore {versione_motore()}\n")
        for b in reg["brains"]:
            p = os.path.join(ROOT, b["percorso"])
            d = descrivi(p) if os.path.isdir(p) else None
            stato = "" if d else "  [CARTELLA ASSENTE]"
            print(f"  {b['nome']:16} {b['percorso']:24} "
                  f"training: {(d or {}).get('training') or '—'}{stato}")
            if d:
                print(f"    {len(d['aree'])} aree · {d['note_raw']} note grezze · "
                      f"{d['pagine_wiki']} pagine curate · {d['lezioni']} lezioni · "
                      f"verificato col motore {d['motore'] or '— (manifesto assente)'}")
        return

    crea(a.nome, a.aree, a.training)
    print(f"brain creato: brains/{a.nome}  (motore {versione_motore()})")
    if not a.aree:
        print(f"  configuralo:  python tools/onboarding.py --brain brains/{a.nome}")
    print(f"  poi:          ALTAIR_BRAIN=brains/{a.nome} python tools/rebuild_all.py")


if __name__ == "__main__":
    main()
