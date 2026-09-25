# -*- coding: utf-8 -*-
"""
altair-brain — porta un brain fuori dall'officina, insieme al motore della sua versione.

PERCHE' ESISTE. Un brain dell'officina e' solo conoscenza: il motore lo usa, non lo
porta. Per farlo girare altrove — un altro PC, un server, una consegna — serve
affiancargli il motore. Prima lo si faceva copiando la cartella del brain, che aveva
una copia propria del motore; ma quella copia non si aggiornava mai, e un brain
copiato altrove girava col codice del giorno in cui era nato.

L'export invece e' GENERATO al momento: lo scheletro core/ (motore della versione
corrente, verificato dalla CI) piu' la conoscenza del brain, piu' gli strumenti del
suo training se ne ha adottato uno. Si esporta solo un brain verificato con la
versione corrente del motore: cosi' la copia non nasce gia' vecchia, e il suo
manifesto dice con esattezza quale motore la accompagna.

Il risultato e' un'istanza autosufficiente: dentro, tools/brain.py risolve il brain
nella cartella stessa, e .gitignore tiene fuori da git i dati pesanti delle aree.

Uso:
  python tools/brain_export.py --nome cucina --dest ../cucina-standalone
"""
import argparse, json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(ROOT, "core")
sys.path.insert(0, ROOT)
from tools.brain import manifesto, versione_motore  # noqa: E402
from tools.brain_upgrade import stato  # noqa: E402

# Cio' che e' del brain. Tutto il resto dell'export viene da core/.
PARTI_BRAIN = ("raw", "wiki", "engine", "reports", "metrics", "graphify-out",
               "areas.json", "brain.json")
NON_COPIARE = shutil.ignore_patterns("__pycache__", "cache", "memory")


def trova(nome):
    """Un nome del registro, oppure il percorso di un brain."""
    reg = os.path.join(ROOT, "brains", "brains.json")
    if os.path.exists(reg):
        with open(reg, encoding="utf-8") as f:
            for b in json.load(f).get("brains", []):
                if b.get("nome") == nome:
                    return os.path.join(ROOT, b["percorso"])
    return os.path.abspath(nome) if os.path.isdir(nome) else None


def esporta(brain, dest):
    codice, msg = stato(brain)
    if codice != "ok":
        sys.exit(f"export rifiutato: {msg}")
    if os.path.exists(dest):
        sys.exit(f"la destinazione esiste gia': {dest}")
    if not os.path.isdir(CORE):
        sys.exit("core/ assente: esegui prima python tools/build_core.py")

    shutil.copytree(CORE, dest, ignore=shutil.ignore_patterns("__pycache__"))
    for parte in PARTI_BRAIN:
        p = os.path.join(dest, parte)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    for parte in PARTI_BRAIN:
        src = os.path.join(brain, parte)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(dest, parte), ignore=NON_COPIARE)
        elif os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, parte))

    training = manifesto(brain).get("training")
    if training:
        tr = os.path.join(CORE, "training", training)
        for sotto, arrivo in (("tools", "tools"), ("skills", os.path.join(".claude", "skills"))):
            src = os.path.join(tr, sotto)
            if not os.path.isdir(src):
                continue
            for voce in sorted(os.listdir(src)):
                a, b = os.path.join(src, voce), os.path.join(dest, arrivo, voce)
                if os.path.exists(b):
                    continue
                os.makedirs(os.path.dirname(b), exist_ok=True)
                (shutil.copytree if os.path.isdir(a) else shutil.copy2)(a, b)
    return training


def main():
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass
    ap = argparse.ArgumentParser(description="Esporta un brain con il suo motore")
    ap.add_argument("--nome", required=True, help="nome nel registro, o percorso del brain")
    ap.add_argument("--dest", required=True, help="cartella da creare")
    a = ap.parse_args()
    brain = trova(a.nome)
    if not brain:
        sys.exit(f"brain sconosciuto: {a.nome}")
    training = esporta(brain, os.path.abspath(a.dest))
    print(f"esportato in {a.dest}: brain {a.nome} + motore {versione_motore()}"
          f"{' + training ' + training if training else ''}")
    print(f"  li':  python tools/rebuild_all.py")


if __name__ == "__main__":
    main()
