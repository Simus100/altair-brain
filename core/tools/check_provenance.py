# -*- coding: utf-8 -*-
"""
altair-brain — verifica che le affermazioni fattuali abbiano una fonte (P8).

PRINCIPIO (letteratura sulla qualita delle knowledge base): l'unita di conoscenza e
un passaggio CON provenienza. Un'affermazione con numeri, percentuali o date e una
pretesa di fatto: senza fonte non e verificabile, e fra un anno nessuno — nemmeno chi
l'ha scritta — sapra se era vera.

DUE LIVELLI, dal piu rigoroso al piu indicativo:
1. REPORT (bloccante con --strict): ogni voce di timeline che contiene numeri deve
   avere il campo 'fonte'. E il prodotto editoriale: qui la regola non si negozia.
2. NOTE (informativo): note con molti dati ma senza 'source' nel front-matter.
   Un promemoria, non un obbligo: certe note sono riflessioni proprie.

Uso:  python tools/check_provenance.py            (informativo)
      python tools/check_provenance.py --strict    (exit 1 se i report sono scoperti)
"""
import glob, json, os, re, sys

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


# Una pretesa di fatto: percentuali, cifre con separatori, valute, anni, date.
FATTUALE = re.compile(r"\d+[.,]\d+|\d+\s*%|\d{4}|[$€£]\s*\d|\b\d{2}/\d{2}\b")
# Soglia per le note: sotto questa densita di numeri e prosa, non dati.
MIN_FATTI_NOTA = 6

scoperti, note_dense = [], []

# ---- 1. report living: le timeline sono il prodotto editoriale ----
for db_path in sorted(glob.glob(os.path.join(ROOT, "reports", "data", "*.updates.json"))):
    rel = os.path.relpath(db_path, ROOT).replace("\\", "/")
    try:
        with open(db_path, encoding="utf-8") as f:
            db = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        scoperti.append(f"{rel}: illeggibile ({e})")
        continue

    sezioni = []
    for chiave in ("verdetto", "conclusioni"):
        if isinstance(db.get(chiave), dict):
            sezioni.append((chiave, db[chiave].get("storia", [])))
    for nodo, voci in (db.get("nodi") or {}).items():
        sezioni.append((f"nodo {nodo}", voci))

    for nome, voci in sezioni:
        for v in voci or []:
            testo = v.get("testo", "")
            if FATTUALE.search(testo) and not v.get("fonte"):
                scoperti.append(f"{rel} · {nome} · {v.get('ts', '?')}: "
                                f"dati senza fonte — \"{testo[:70]}...\"")

# ---- 2. note: promemoria, non obbligo ----
for base in ("raw", "wiki"):
    for root, dirs, files in os.walk(os.path.join(ROOT, base)):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "archive"]
        for f in files:
            if not f.endswith((".md", ".txt")):
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            try:
                with open(p, encoding="utf-8") as fh:
                    testo = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            s = testo.lstrip()
            fonte = ""
            if s.startswith("---"):
                fine = s.find("\n---", 3)
                if fine != -1:
                    m = re.search(r"^source:\s*(.+)$", s[:fine], re.M)
                    fonte = (m.group(1).strip() if m else "")
                    testo = s[fine + 4:]
            if not fonte and len(FATTUALE.findall(testo)) >= MIN_FATTI_NOTA:
                note_dense.append(rel)

print("== PROVENIENZA DELLE AFFERMAZIONI ==\n")

if scoperti:
    print(f"REPORT — {len(scoperti)} affermazioni con dati SENZA fonte:")
    for s in scoperti[:20]:
        print("  !", s)
    if len(scoperti) > 20:
        print(f"  ... e altre {len(scoperti) - 20}")
else:
    print("Report: ogni affermazione con dati ha la sua fonte.")

if note_dense:
    print(f"\nNote ricche di dati senza 'source' nel front-matter: {len(note_dense)}")
    for n in note_dense[:10]:
        print("  -", n)
    if len(note_dense) > 10:
        print(f"  ... e altre {len(note_dense) - 10}")
    print("  (promemoria, non errore: aggiungi 'source:' dove il dato viene da fuori)")

if scoperti and "--strict" in sys.argv:
    sys.exit(1)
