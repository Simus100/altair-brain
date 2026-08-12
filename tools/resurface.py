# -*- coding: utf-8 -*-
"""
altair-brain — riporta a galla la tua stessa conoscenza (F8).

TUTTO IL RESTO DEL BRAIN E OTTIMIZZATO PER L'AI. Questo no. Un archivio che non
riemerge e un archivio morto: la ricerca sui sistemi di conoscenza personale e
concorde sulla curva dell'oblio — cio che non si rivede, si perde, anche quando e
scritto e indicizzato. Il brain sa tutto e tu non ricordi cosa c'e dentro.

COSA FA: sceglie poche note da rivedere, con un criterio, non a caso.
  - priorita a cio che NON rivedi da piu tempo (campo `reviewed` del front-matter)
  - priorita a cio che il grafo considera ISOLATO: le note senza collegamenti sono
    le prime a sparire dalla memoria, e sono anche quelle che chiedono un [[link]]
  - si escludono gli strati generati (rivedere una pagina generata non serve: la
    fonte e altrove)

Deterministico a parita di giorno: la selezione dipende dalla data, non dal caso —
rilanciarlo lo stesso giorno da le stesse note, il giorno dopo altre.

Uso:  python tools/resurface.py            (3 note da rivedere oggi)
      python tools/resurface.py --quante 5 --area data-science
      python tools/resurface.py --segna raw/aion/aion-oracle.md   (aggiorna 'reviewed')
"""
import argparse, collections, datetime, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import frontmatter as fm  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Console Windows (cp1252): vedi tools/console.py. Attivo SOLO da riga di comando,
# per non toccare i flussi di chi importa questo modulo (test compresi).
if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool

GRAFO = os.path.join(ROOT, "graphify-out", "graph.json")
GENERATI = ("wiki/aion/",)
CARTELLE = ("raw", "wiki")


def _frontmatter(path):
    """Parser condiviso (tools/frontmatter)."""
    return fm.leggi(path)


def _gradi_per_file():
    """Quanto e collegata ogni nota: le isolate sono quelle che si dimenticano prima."""
    if not os.path.exists(GRAFO):
        return {}
    with open(GRAFO, encoding="utf-8") as f:
        g = json.load(f)
    di_chi = {n["id"]: (n.get("source_file") or "").replace("\\", "/") for n in g["nodes"]}
    gradi = collections.Counter()
    for e in g["links"]:
        a, b = di_chi.get(e.get("source")), di_chi.get(e.get("target"))
        if a and b and a != b:
            gradi[a] += 1
            gradi[b] += 1
    return gradi


def candidati(area=None):
    oggi = datetime.date.today()
    gradi = _gradi_per_file()
    fuori = []
    for base in CARTELLE:
        for root, dirs, files in os.walk(os.path.join(ROOT, base)):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "archive"]
            for f in sorted(files):
                if not f.endswith(".md") or f.upper().startswith("README"):
                    continue
                rel = os.path.relpath(os.path.join(root, f), ROOT).replace("\\", "/")
                if any(rel.startswith(g) for g in GENERATI):
                    continue
                if area and f"/{area}/" not in rel:
                    continue
                meta, corpo = _frontmatter(os.path.join(ROOT, rel))
                if meta is None or len(corpo.strip()) < 120:
                    continue
                rev = meta.get("reviewed") or meta.get("date") or ""
                try:
                    giorni = (oggi - datetime.date.fromisoformat(rev[:10])).days
                except ValueError:
                    giorni = 999
                collegamenti = gradi.get(rel, 0)
                # piu tempo passa e meno e collegata, piu merita di riemergere
                punteggio = giorni + (30 if collegamenti == 0 else 0)
                titolo = next((r.lstrip("# ").strip() for r in corpo.splitlines()
                               if r.startswith("#")), os.path.basename(rel))
                fuori.append({
                    "file": rel, "titolo": titolo, "giorni": giorni,
                    "collegamenti": collegamenti, "punteggio": punteggio,
                    "area": meta.get("area", "?"),
                    "assaggio": re.sub(r"\s+", " ", corpo.strip())[:220],
                })
    return fuori


def scegli(cands, quante=3):
    """Le piu meritevoli, ma variando: si prende dal gruppo di testa ruotando in base
    al giorno, cosi non escono sempre le stesse tre note finche non le si tocca."""
    if not cands:
        return []
    ordinati = sorted(cands, key=lambda c: (-c["punteggio"], c["file"]))
    finestra = ordinati[:max(quante * 4, 12)]
    inizio = datetime.date.today().toordinal() % max(len(finestra), 1)
    scelte = [finestra[(inizio + i) % len(finestra)] for i in range(min(quante, len(finestra)))]
    return scelte


def segna_rivista(rel):
    """Aggiorna 'reviewed' a oggi: e cosi che la nota esce dalla coda."""
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        sys.exit(f"file inesistente: {rel}")
    with open(p, encoding="utf-8") as f:
        testo = f.read()
    oggi = datetime.date.today().isoformat()
    if not testo.lstrip().startswith("---"):
        sys.exit(f"{rel} non ha front-matter: aggiungilo con tools/add_frontmatter.py")
    s = testo.lstrip()
    fine = s.find("\n---", 3)
    testa, resto = s[:fine], s[fine:]
    if re.search(r"^reviewed:", testa, re.M):
        testa = re.sub(r"^reviewed:.*$", f"reviewed: {oggi}", testa, flags=re.M)
    else:
        testa += f"\nreviewed: {oggi}"
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(testa + resto)
    print(f"segnata come rivista oggi: {rel}")


def main():
    ap = argparse.ArgumentParser(description="Note da rivedere (per te, non per l'AI)")
    ap.add_argument("--quante", type=int, default=3)
    ap.add_argument("--area", default=None)
    ap.add_argument("--segna", default=None, help="marca una nota come rivista oggi")
    a = ap.parse_args()

    if a.segna:
        segna_rivista(a.segna.replace("\\", "/"))
        return

    cands = candidati(a.area)
    if not cands:
        print("Nessuna nota con front-matter da riproporre.")
        return
    scelte = scegli(cands, a.quante)
    mai = sum(1 for c in cands if c["collegamenti"] == 0)

    print(f"== DA RIVEDERE OGGI ({datetime.date.today()}) ==")
    print(f"{len(cands)} note in archivio · {mai} senza collegamenti nel grafo\n")
    for i, c in enumerate(scelte, 1):
        stato = f"{c['giorni']} giorni fa" if c["giorni"] < 999 else "mai verificata"
        isolata = "  [ISOLATA: nessun collegamento]" if c["collegamenti"] == 0 else ""
        print(f"{i}. {c['titolo']}   [{c['area']}]{isolata}")
        print(f"   {c['file']}  ·  rivista {stato}")
        print(f"   {c['assaggio'][:180]}...")
        print(f"   quando l'hai riletta:  python tools/resurface.py --segna \"{c['file']}\"")
        print()
    print("Suggerimento: se leggendola ti viene in mente un collegamento, aggiungilo —")
    print("e il modo piu diretto per far risalire il grado medio in metrics/.")


if __name__ == "__main__":
    main()
