# -*- coding: utf-8 -*-
"""
altair-brain — ricerca IBRIDA sul corpus (P4).

DUE MOTORI, FUSI CON RRF:
1. LESSICALE (BM25, sempre attivo): trova i termini esatti — nomi propri, sigle,
   codici, formule. Nessuna dipendenza: legge engine/search_index.json.
2. SEMANTICO (embeddings, OPZIONALE): trova per significato anche con parole diverse.
   Si attiva da solo se sono presenti sentence-transformers e l'indice denso
   (tools/build_dense_index.py). Se mancano, la ricerca resta lessicale: degradazione
   controllata, stesso principio gia usato per graphify (503 invece di crash).

PERCHE RRF E NON UNA MEDIA PESATA: i punteggi BM25 e le similarita coseno vivono su
scale diverse e instabili; normalizzarli e fragile. RRF usa solo la POSIZIONE in
classifica — score = somma di 1/(k + rango) — ed e la pratica consolidata.

Uso:
  python tools/search.py "quartili e outlier"
  python tools/search.py "come struttura un report" --area data-science --top 5
Come modulo:  from tools.search import cerca
"""
import json, math, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(ROOT, "engine", "search_index.json")
DENSO = os.path.join(ROOT, "graphify-out", "search", "dense.json")
RRF_K = 60          # costante standard: attenua il peso delle prime posizioni

_cache = {}


def _carica():
    if "idx" not in _cache:
        with open(INDICE, encoding="utf-8") as f:
            _cache["idx"] = json.load(f)
    return _cache["idx"]


def _normalizza(t):
    t = unicodedata.normalize("NFKD", (t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def _tokenizza(t):
    return [x for x in re.findall(r"[a-z0-9_]+", _normalizza(t)) if len(x) >= 3]


def cerca_bm25(query, limite=40):
    """Ranking BM25 classico. Ritorna [(indice_doc, punteggio)] decrescente."""
    idx = _carica()
    k1 = idx["parametri"]["k1"]
    b = idx["parametri"]["b"]
    avgdl = idx["avgdl"] or 1.0
    docs = idx["documenti"]
    punteggi = {}
    for termine in _tokenizza(query):
        posting = idx["postings"].get(termine)
        if not posting:
            continue
        peso_idf = idx["idf"].get(termine, 0.0)
        for doc_id, tf in posting:
            dl = docs[doc_id]["n_token"]
            num = tf * (k1 + 1)
            den = tf + k1 * (1 - b + b * dl / avgdl)
            punteggi[doc_id] = punteggi.get(doc_id, 0.0) + peso_idf * num / den
    return sorted(punteggi.items(), key=lambda x: -x[1])[:limite]


def cerca_denso(query, limite=40):
    """Ranking semantico. Attivo solo se indice denso e libreria sono presenti."""
    if not os.path.exists(DENSO):
        return []
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        return []
    try:
        with open(DENSO, encoding="utf-8") as f:
            meta = json.load(f)
        vettori = np.array(meta["vettori"], dtype="float32")
        modello = SentenceTransformer(meta["modello"])
        q = modello.encode([query], normalize_embeddings=True)[0]
        sim = vettori @ q
        ordine = sim.argsort()[::-1][:limite]
        return [(int(i), float(sim[i])) for i in ordine]
    except Exception:
        return []          # il semantico non deve mai far cadere la ricerca


def _rrf(classifiche):
    """Reciprocal Rank Fusion: fonde piu classifiche usando solo la posizione."""
    fusi = {}
    for classifica in classifiche:
        for rango, (doc_id, _) in enumerate(classifica, start=1):
            fusi[doc_id] = fusi.get(doc_id, 0.0) + 1.0 / (RRF_K + rango)
    return sorted(fusi.items(), key=lambda x: -x[1])


def cerca(query, top=8, area=None):
    """Ricerca ibrida. Ritorna una lista di risultati leggibili."""
    idx = _carica()
    docs = idx["documenti"]
    lessicale = cerca_bm25(query)
    semantico = cerca_denso(query)
    classifiche = [c for c in (lessicale, semantico) if c]
    if not classifiche:
        return []
    ordinati = _rrf(classifiche) if len(classifiche) > 1 else \
        [(d, s) for d, s in classifiche[0]]

    fuori = []
    for doc_id, punteggio in ordinati:
        d = docs[doc_id]
        if area and d["area"] != area:
            continue
        fuori.append({
            "file": d["file"],
            "titolo": d["titolo"],
            "area": d["area"],
            "estratto": d["estratto"],
            "punteggio": round(punteggio, 5),
            "motori": ("lessicale+semantico" if len(classifiche) > 1 else "lessicale"),
        })
        if len(fuori) >= top:
            break
    return fuori


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Ricerca ibrida nel second brain")
    ap.add_argument("query", help="cosa cerchi")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--area", default=None, help="filtra per macroarea")
    ap.add_argument("--json", action="store_true", help="output JSON")
    a = ap.parse_args()

    risultati = cerca(a.query, top=a.top, area=a.area)
    if a.json:
        print(json.dumps(risultati, ensure_ascii=False, indent=2))
    elif not risultati:
        print("Nessun risultato.")
    else:
        motore = risultati[0]["motori"]
        print(f"{len(risultati)} risultati per {a.query!r} (motore: {motore})\n")
        for i, r in enumerate(risultati, 1):
            print(f"{i}. [{r['area']}] {r['titolo']}  ({r['punteggio']})")
            print(f"   {r['file']}")
            print(f"   {r['estratto'][:160]}...\n")
