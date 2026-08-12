# -*- coding: utf-8 -*-
"""
altair-brain — livello SEMANTICO opzionale della ricerca ibrida (P4, meta densa).

OPZIONALE PER SCELTA: richiede sentence-transformers (~2 GB con torch). Il brain
funziona benissimo senza — la ricerca resta lessicale (BM25). Chi lo attiva ottiene
il recupero per SIGNIFICATO: "come valuto se un dato e sporco" trova "controlli di
qualita" anche senza parole in comune. I due motori vengono poi fusi con RRF.

Il modello gira in LOCALE, offline dopo il primo download: nessuna API a pagamento,
vincolo del progetto rispettato.

ATTIVARE:
    pip install sentence-transformers
    python tools/build_dense_index.py
    (poi tools/search.py usa automaticamente entrambi i motori)

L'indice denso NON va in git (e grande e ricostruibile): vedi .gitignore.
"""
import json, os, sys

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

INDICE = os.path.join(ROOT, "engine", "search_index.json")
OUT_DIR = os.path.join(ROOT, "graphify-out", "search")
OUT = os.path.join(OUT_DIR, "dense.json")

# Multilingue e leggero (~470MB): il corpus e in italiano con termini tecnici inglesi.
MODELLO = os.environ.get("ALTAIR_EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("sentence-transformers non installato: livello semantico non attivato.")
    print("  La ricerca resta lessicale (BM25), che funziona gia.")
    print("  Per attivarlo:  pip install sentence-transformers")
    sys.exit(0)

if not os.path.exists(INDICE):
    sys.exit("manca engine/search_index.json: lancia prima tools/build_search_index.py")

with open(INDICE, encoding="utf-8") as f:
    idx = json.load(f)

testi = [f"{d['titolo']}. {d['estratto']}" for d in idx["documenti"]]
print(f"Codifica di {len(testi)} frammenti con {MODELLO} (solo la prima volta scarica il modello)...")

modello = SentenceTransformer(MODELLO)
vettori = modello.encode(testi, normalize_embeddings=True, batch_size=32,
                         show_progress_bar=True)

os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump({
        "modello": MODELLO,
        "n_documenti": len(testi),
        "dimensioni": int(vettori.shape[1]),
        "vettori": [[round(float(x), 6) for x in v] for v in vettori],
    }, f, separators=(",", ":"))
    f.write("\n")

print(f"Indice semantico pronto: {len(testi)} vettori a {vettori.shape[1]} dimensioni "
      f"-> {os.path.relpath(OUT, ROOT)}")
print("  La ricerca ora fonde lessicale + semantico con RRF.")
