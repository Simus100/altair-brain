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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import frontmatter as fm  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, ROOT)
try:
    from tools.brain import BRAIN            # dove vive il CONTENUTO
except ImportError:
    BRAIN = ROOT                             # istanza autosufficiente


# Console Windows (cp1252): vedi tools/console.py. Attivo SOLO da riga di comando,
# per non toccare i flussi di chi importa questo modulo (test compresi).
if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool

OGGI = datetime.date.today()

# Quanti giorni prima che una nota vada RI-VERIFICATA, per famiglia di conoscenza.
# None = non scade (principi, definizioni: stabili per natura).
# Gli SLA per area NON sono scritti qui: ogni area li dichiara in areas.json
# ('sla_giorni'). Erano una tabella con dentro i nomi di UN brain preciso — il che
# rendeva il motore inservibile a chiunque avesse aree diverse, e imponeva di
# modificare il codice per aggiungere una macroarea.
def _sla_dalle_aree():
    import json
    tabella = {"reports/": 30}          # l'attualita' invecchia in settimane: vale sempre
    try:
        with open(os.path.join(BRAIN, "areas.json"), encoding="utf-8") as f:
            aree = json.load(f).get("areas", [])
    except (OSError, ValueError):
        return tabella
    for a in aree:
        if "sla_giorni" in a:
            tabella[f"raw/{a['id']}/"] = a["sla_giorni"]
            tabella[f"wiki/{a['id']}/"] = a["sla_giorni"]
    return tabella


SLA_GIORNI = _sla_dalle_aree()
SLA_DEFAULT = 180
SCANSIONA = ("raw/", "wiki/", "reports/")


def leggi_frontmatter(path):
    """Delega al parser condiviso (tools/frontmatter): la regola del blocco
    delimitato vive in un posto solo. Ritorna None se non c'e front-matter."""
    meta, _ = fm.leggi(path)
    return meta or None


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

# Distinzione necessaria: i file degli strati GENERATI non possono avere front-matter
# scritto a mano (divergerebbero dal generatore) e la loro provenienza e' gia'
# dichiarata a livello di strato. Contarli insieme agli altri produceva un numero
# allarmante e un consiglio ESEGUIBILE SOLO IN PARTE: add_frontmatter.py si rifiuta
# di toccarli. Un rapporto che suggerisce un comando destinato a non fare nulla
# insegna a ignorare i rapporti.
esenti = [s for s in senza_meta if fm.e_generato(s)]
mancanti = [s for s in senza_meta if not fm.e_generato(s)]

if mancanti:
    print(f"\nSenza front-matter: {len(mancanti)} file "
          f"(aggiungilo con tools/add_frontmatter.py --apply)")
    for s in mancanti[:10]:
        print("  -", s)
if esenti:
    print(f"\nEsenti per costruzione: {len(esenti)} file negli strati generati "
          f"({', '.join(fm.STRATI_GENERATI)}) — provenienza dichiarata a livello di "
          f"strato in engine/provenance.json, non file per file.")

if rotti:
    print(f"\nPROBLEMI ({len(rotti)}):")
    for r in rotti:
        print("  !", r)

if rotti and "--strict" in sys.argv:
    sys.exit(1)
