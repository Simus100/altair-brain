# -*- coding: utf-8 -*-
"""
altair-brain — aggiunge il front-matter di provenienza alle note (P2/P5/P8).

PERCHE: senza metadati non si sa da dove viene una nota, quando e stata verificata
l'ultima volta, ne se e ancora valida. La letteratura sulla qualita delle knowledge
base e concorde: l'unita di conoscenza e un passaggio CON provenienza.

CAMPI (tutti opzionali tranne date/area; nessuno viene mai sovrascritto):
  date          quando la nota entra nel brain (dedotta dal PRIMO commit git: deterministica)
  area          macroarea di appartenenza (dedotta dal percorso)
  source        da dove viene il contenuto (URL, libro, esperienza diretta)
  tags          parole chiave
  reviewed      ultima verifica umana -> guida il freshness SLA (tools/freshness_report.py)
  confidence    alta | media | bassa
  valid_from / valid_until / superseded_by   bi-temporalita (modello Zep, arXiv 2501.13956):
                un fatto che smette di essere vero NON si cancella, si invalida

SICUREZZA: si rifiuta di toccare gli strati GENERATI (wiki/aion e generata da
engine/aion.model.json): scriverci significherebbe far divergere wiki e modello e
far fallire la CI. Idempotente: rilanciarlo non duplica nulla.

Uso:
  python tools/add_frontmatter.py                 # anteprima (dry-run)
  python tools/add_frontmatter.py --apply         # scrive
  python tools/add_frontmatter.py --apply --only raw/aion/aion-oracle.md
"""
import argparse, datetime, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Strati GENERATI: mai toccare a mano (fonte unica di verita).
GENERATI = ("wiki/aion/",)
# Dove ha senso avere provenienza: le fonti e le pagine scritte a mano.
TARGET = ("raw/", "wiki/data-science/")
SALTA = ("raw/_inbox/",)          # transito: vivranno altrove dopo il triage


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def data_primo_commit(path):
    """Data del primo commit che introduce il file: deterministica e verificabile."""
    try:
        r = subprocess.run(["git", "log", "--diff-filter=A", "--format=%aI", "--", rel(path)],
                           cwd=ROOT, capture_output=True, text=True, timeout=20)
        righe = [x for x in r.stdout.strip().splitlines() if x.strip()]
        if righe:
            return righe[-1][:10]
    except Exception:
        pass
    return datetime.date.today().isoformat()


def area_di(p):
    parti = rel(p).split("/")
    return parti[1] if len(parti) > 2 and parti[0] in ("raw", "wiki") else "generale"


# delega al parser condiviso: la regola "prima riga esattamente ---" e li, una volta sola
from tools.frontmatter import ha_frontmatter  # noqa: E402


def costruisci(path):
    """Front-matter minimo e onesto: solo cio che si puo dedurre con certezza."""
    # NIENTE righe che iniziano con '#': dentro il front-matter markdown le legge
    # come titoli e diventano nodi spuri del grafo (verificato). La convenzione dei
    # campi opzionali (valid_from/valid_until/superseded_by/confidence) e documentata
    # in raw/README.md, non ripetuta in ogni file.
    campi = [
        "---",
        f"date: {data_primo_commit(path)}",
        f"area: {area_di(path)}",
        "source: ",
        "tags: []",
        f"reviewed: {datetime.date.today().isoformat()}",
        "---",
        "",
    ]
    return "\n".join(campi)


ap = argparse.ArgumentParser()
ap.add_argument("--apply", action="store_true", help="scrive davvero (default: anteprima)")
ap.add_argument("--only", default=None, help="un singolo file (percorso relativo)")
a = ap.parse_args()

candidati = []
if a.only:
    p = os.path.join(ROOT, a.only)
    if not os.path.exists(p):
        sys.exit(f"file inesistente: {a.only}")
    candidati = [p]
else:
    for base in TARGET:
        for root, _, files in os.walk(os.path.join(ROOT, base)):
            for f in files:
                if f.endswith(".md"):
                    candidati.append(os.path.join(root, f))

toccati, gia_ok, rifiutati = [], [], []
for p in sorted(candidati):
    r = rel(p)
    if any(r.startswith(g) for g in GENERATI):
        rifiutati.append(r)
        continue
    if any(r.startswith(s) for s in SALTA):
        continue
    testo = open(p, encoding="utf-8").read()
    if ha_frontmatter(testo):
        gia_ok.append(r)
        continue
    if a.apply:
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(costruisci(p) + testo)
    toccati.append(r)

print(f"{'APPLICATO' if a.apply else 'ANTEPRIMA (dry-run)'}: "
      f"{len(toccati)} file da arricchire, {len(gia_ok)} gia con front-matter.")
for r in toccati[:15]:
    print("  +", r)
if len(toccati) > 15:
    print(f"  ... e altri {len(toccati) - 15}")
if rifiutati:
    print(f"  [protetti] {len(rifiutati)} file in strati GENERATI non toccati "
          f"(es. {rifiutati[0]})")
if not a.apply and toccati:
    print("\nPer scrivere davvero:  python tools/add_frontmatter.py --apply")
