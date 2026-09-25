# -*- coding: utf-8 -*-
"""
altair-brain — il grafo del CODICE del motore, separato da quello della conoscenza.

DUE GRAFI, DUE DOMANDE. Il grafo di un brain risponde a "cosa so": fonti, pagine,
modello. Il grafo del motore risponde a "come e' fatto il sistema": tool, test,
server, istruzioni per gli agenti. Mescolati, uno sporcava l'altro: un terzo del
grafo di aion era codice, e alla domanda "come funziona il reasoner" rispondeva
app.py invece del protocollo del reasoner.

PERCHE' SU UNA COPIA. graphify legge .gitignore e .graphifyignore risalendo fino alla
radice del repo: una regola che escludesse brains/ dalla radice escluderebbe anche i
brain quando il loro grafo si costruisce dall'interno. Quindi il grafo del motore si
costruisce su una copia delle sole cartelle del motore, fuori dal repo, e il
risultato si porta in graphify-out/ nella radice — dove gli agenti lo cercano per le
domande sul codice (graphify query "..." dalla radice).

Il grafo del codice e' uno strumento di lavoro, non un prodotto: si rigenera in
pochi secondi e non sta in git.

Uso:  python tools/build_code_graph.py      (lo chiama rebuild_all, solo nell'officina)
"""
import hashlib, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool

CARTELLE = ("tools", "tests", "server", os.path.join(".claude", "skills"))
DOCUMENTI = ("CLAUDE.md", "AGENTS.md", "README.md", "GUIDA.md", "ROADMAP.md")
DA_PORTARE = ("graph.json", "graph.html", "GRAPH_REPORT.md")
OUT = os.path.join(ROOT, "graphify-out")


def cartella_di_lavoro():
    """Una per repo, stabile fra le esecuzioni: la cache di graphify rende gli
    aggiornamenti successivi incrementali."""
    impronta = hashlib.sha1(os.path.abspath(ROOT).encode("utf-8")).hexdigest()[:10]
    return os.path.join(tempfile.gettempdir(), f"altair-grafo-motore-{impronta}")


def rispecchia(lavoro):
    """La copia deve essere IDENTICA al motore: un tool cancellato che restasse nella
    copia resterebbe nel grafo. Si svuota tutto tranne l'output di graphify."""
    os.makedirs(lavoro, exist_ok=True)
    for voce in os.listdir(lavoro):
        if voce == "graphify-out":
            continue
        p = os.path.join(lavoro, voce)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for c in CARTELLE:
        src = os.path.join(ROOT, c)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(lavoro, c),
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for d in DOCUMENTI:
        if os.path.exists(os.path.join(ROOT, d)):
            shutil.copy2(os.path.join(ROOT, d), os.path.join(lavoro, d))


def main():
    if not os.path.exists(os.path.join(ROOT, "brains", "brains.json")):
        print("grafo del codice: saltato (non e' un'officina: qui motore e brain coincidono)")
        return 0
    if shutil.which("graphify") is None:
        print("grafo del codice: saltato (graphify non installato)")
        return 0
    lavoro = cartella_di_lavoro()
    rispecchia(lavoro)
    # GRAPHIFY_FORCE: la copia e' esatta, quindi un calo di nodi e' un refactoring
    # vero, non un errore da cui proteggersi.
    amb = dict(os.environ, GRAPHIFY_FORCE="1")
    esito = subprocess.run(["graphify", "update", "."], cwd=lavoro, env=amb,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    if esito.returncode != 0:
        print(esito.stdout[-800:], esito.stderr[-800:])
        return 1
    os.makedirs(OUT, exist_ok=True)
    for f in DA_PORTARE:
        src = os.path.join(lavoro, "graphify-out", f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT, f))
    import json
    with open(os.path.join(OUT, "graph.json"), encoding="utf-8") as fh:
        g = json.load(fh)
    print(f"grafo del codice: {len(g['nodes'])} nodi, {len(g['links'])} archi -> "
          f"graphify-out/ (domande sul codice: graphify query \"...\" dalla radice)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
