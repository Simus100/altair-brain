# -*- coding: utf-8 -*-
"""
altair-brain — freschezza e validita della conoscenza (P2 + P5).

DUE DOMANDE a cui risponde:
1. FRESCHEZZA — "cosa non verifico da troppo tempo?" Ogni tipo di conoscenza ha una
   vita diversa: un fatto geopolitico invecchia in settimane, un metodo di analisi in
   anni, un principio quasi mai. Si confronta 'reviewed' con l'SLA dell'area.
2. VALIDITA (bi-temporalita, modello Zep arXiv 2501.13956) — "cosa non e piu vero?"
   Un fatto con 'valid_until' passato NON viene cancellato: viene marcato scaduto, e
   'superseded_by' dice cosa lo rimpiazza. La storia resta, la verita corrente cambia.

Parser YAML minimale interno: nessuna dipendenza esterna (gira ovunque, anche in CI).

Uso:  python tools/freshness_report.py            (informativo, exit 0)
      python tools/freshness_report.py --strict   (exit 1 se ci sono problemi gravi)
"""
import argparse, datetime, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OGGI = datetime.date.today()

# Quanti giorni prima che una nota vada RI-VERIFICATA, per famiglia di conoscenza.
# None = non scade (principi, definizioni: stabili per natura).
SLA_GIORNI = {
    "reports/": 30,             # attualita: invecchia in settimane
    "raw/data-science/": 365,   # metodo: stabile ma da rileggere una volta l'anno
    "wiki/data-science/": 365,
    "raw/aion/": None,          # principi del modello di pensiero
    "wiki/aion/": None,
}
SLA_DEFAULT = 180
SCANSIONA = ("raw/", "wiki/", "reports/")


def leggi_frontmatter(path):
    """Estrae le coppie chiave: valore del blocco --- iniziale. Volutamente semplice:
    i campi della convenzione sono scalari o liste in linea, niente YAML annidato."""
    try:
        with open(path, encoding="utf-8") as f:
            testo = f.read()
    except (OSError, UnicodeDecodeError):
        return None
    if not testo.lstrip().startswith("---"):
        return None
    corpo = testo.lstrip()[3:]
    fine = corpo.find("\n---")
    if fine == -1:
        return None
    meta = {}
    for riga in corpo[:fine].splitlines():
        if ":" not in riga or riga.strip().startswith("#"):
            continue
        k, _, v = riga.partition(":")
        meta[k.strip()] = v.strip()
    return meta


def sla_di(rel):
    for prefisso, giorni in SLA_GIORNI.items():
        if rel.startswith(prefisso):
            return giorni
    return SLA_DEFAULT


def come_data(valore):
    try:
        return datetime.date.fromisoformat((valore or "").strip()[:10])
    except ValueError:
        return None


scaduti, da_riverificare, rotti, senza_meta = [], [], [], []

for base in SCANSIONA:
    for root, _, files in os.walk(os.path.join(ROOT, base)):
        for f in files:
            if not f.endswith(".md"):
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            meta = leggi_frontmatter(p)
            if meta is None:
                senza_meta.append(rel)
                continue

            # 1. validita (bi-temporalita)
            fine = come_data(meta.get("valid_until"))
            if fine and fine < OGGI:
                rimpiazzo = meta.get("superseded_by", "").strip()
                if rimpiazzo and not os.path.exists(os.path.join(ROOT, rimpiazzo)):
                    rotti.append(f"{rel}: superseded_by punta a un file inesistente "
                                 f"({rimpiazzo})")
                scaduti.append(f"{rel} (scaduto il {fine}"
                               f"{', sostituito da ' + rimpiazzo if rimpiazzo else ''})")

            # 2. freschezza
            sla = sla_di(rel)
            rev = come_data(meta.get("reviewed")) or come_data(meta.get("date"))
            if sla and rev:
                eta = (OGGI - rev).days
                if eta > sla:
                    da_riverificare.append((eta - sla, f"{rel} — verificata {eta} giorni fa "
                                                       f"(SLA {sla}gg)"))

print("== FRESCHEZZA E VALIDITA DELLA CONOSCENZA ==")
print(f"data di riferimento: {OGGI}\n")

if scaduti:
    print(f"FATTI SCADUTI ({len(scaduti)}) — non piu validi, conservati per la storia:")
    for s in scaduti[:15]:
        print("  -", s)
else:
    print("Fatti scaduti: nessuno.")

if da_riverificare:
    da_riverificare.sort(reverse=True)
    print(f"\nDA RI-VERIFICARE ({len(da_riverificare)}) — oltre l'SLA, dalla piu vecchia:")
    for _, s in da_riverificare[:15]:
        print("  -", s)
    if len(da_riverificare) > 15:
        print(f"  ... e altre {len(da_riverificare) - 15}")
else:
    print("Da ri-verificare: nessuna (tutto entro l'SLA).")

if senza_meta:
    print(f"\nSenza front-matter: {len(senza_meta)} file "
          f"(aggiungilo con tools/add_frontmatter.py --apply)")

if rotti:
    print(f"\nPROBLEMI ({len(rotti)}):")
    for r in rotti:
        print("  !", r)

if rotti and "--strict" in sys.argv:
    sys.exit(1)
