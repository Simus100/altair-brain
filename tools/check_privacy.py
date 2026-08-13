# -*- coding: utf-8 -*-
"""
altair-brain — cosa stai per rendere pubblico (controllo prima del push).

PERCHE: il repo e PUBBLICO per scelta, e ogni push e pubblicazione permanente (fork,
mirror, cache, scraper: non esiste "tolgo dopo"). Il rischio non e il singolo file —
sono due effetti di concentrazione introdotti dagli strumenti stessi:

  - engine/search_index.json contiene estratti di OGNI nota in un file solo: le note
    erano gia pubbliche, ma cosi diventano scaricabili e analizzabili in blocco;
  - engine/lessons.jsonl registra le tue domande, i tuoi errori e il tuo modo di
    lavorare — un profilo, non degli appunti.

Questo strumento NON decide cosa e privato: segnala schemi che di solito non si
vogliono pubblicare, e lascia la scelta a te.

Uso:  python tools/check_privacy.py           (informativo)
      python tools/check_privacy.py --strict  (exit 1 se trova qualcosa)
"""
import argparse, json, os, re, subprocess, sys

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


SCHEMI = [
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", re.I)),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")),
    ("codice fiscale", re.compile(r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b")),
    ("telefono", re.compile(r"\b(?:\+39\s?)?3\d{2}[\s.-]?\d{6,7}\b")),
    # Solo VALORI LETTERALI fra virgolette: un `TOKEN = os.environ.get(...)` o un
    # `token = tokenizza(...)` sono codice corretto, non un segreto. Uno strumento
    # che urla a ogni riga viene ignorato, e allora tanto vale non averlo.
    ("segreto scritto in chiaro", re.compile(
        r"(?:api[_-]?key|auth[_-]?token|access[_-]?token|secret|passwd|password)"
        r"\s*[:=]\s*[\"'][A-Za-z0-9_\-./+]{12,}[\"']", re.I)),
    ("chiave privata", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
# Valori palesemente finti: non vale la pena segnalarli.
PLACEHOLDER = re.compile(r"test|esempio|example|placeholder|xxx|tuo[-_]|your[-_]|<.*>", re.I)
# Falsi positivi noti: esempi e documentazione parlano di token senza contenerne.
ESENTI = ("server/.env.example", "GUIDA.md", "ROADMAP.md", "CLAUDE.md",
          "server/README.md", "tools/check_privacy.py")


def tracciati():
    r = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    return [f for f in r.stdout.splitlines() if f.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    trovati = []
    for rel in tracciati():
        if rel in ESENTI or not rel.endswith((".md", ".txt", ".json", ".jsonl", ".sql", ".py")):
            continue
        p = os.path.join(ROOT, rel)
        try:
            with open(p, encoding="utf-8") as f:
                testo = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        for nome, rx in SCHEMI:
            for m in rx.finditer(testo):
                if PLACEHOLDER.search(m.group(0)):
                    continue
                trovati.append((rel, nome, m.group(0)[:32]))
                break

    print("== COSA STAI PUBBLICANDO ==\n")

    idx = os.path.join(BRAIN, "engine", "search_index.json")
    if os.path.exists(idx):
        with open(idx, encoding="utf-8") as f:
            d = json.load(f)
        print(f"CONCENTRAZIONE: engine/search_index.json espone estratti di "
              f"{len({x['file'] for x in d['documenti']})} file "
              f"({os.path.getsize(idx) // 1024} KB) in un unico file scaricabile.")
    lez = os.path.join(BRAIN, "engine", "lessons.jsonl")
    if os.path.exists(lez):
        n = sum(1 for r in open(lez, encoding="utf-8") if r.strip())
        print(f"PROFILO: engine/lessons.jsonl espone {n} lezioni — domande poste, "
              f"errori commessi, modo di lavorare.")
    print("  (entrambi sono voluti: servono ai consumatori. Sappi che sono pubblici.)\n")

    if trovati:
        print(f"DATI SENSIBILI POTENZIALI ({len(trovati)}):")
        for rel, nome, esempio in trovati[:20]:
            print(f"  ! {nome} in {rel}: {esempio}...")
        print("\n  Se sono reali: rimuovili PRIMA del push. Dopo e troppo tardi —")
        print("  un repo pubblico si clona, si specchia e si indicizza in automatico.")
    else:
        print("Nessuno schema sensibile riconosciuto nei file tracciati.")

    if trovati and a.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
