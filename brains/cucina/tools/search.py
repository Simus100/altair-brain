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
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, ROOT)
try:
    from tools.brain import BRAIN            # dove vive il CONTENUTO
except ImportError:
    BRAIN = ROOT                             # istanza autosufficiente

INDICE = os.path.join(BRAIN, "engine", "search_index.json")
DENSO = os.path.join(BRAIN, "graphify-out", "search", "dense.json")
RRF_K = 60          # costante standard: attenua il peso delle prime posizioni

_cache = {}


def _fresco(chiave, path):
    """Ricarica se il file su disco e cambiato.

    DIFETTO REALE CORRETTO: la cache era a livello di modulo e non si invalidava mai.
    Sulla VPS l'API resta accesa per settimane mentre l'auto-update sostituisce
    l'indice via git: il processo continuava a servire quello caricato al primo
    avvio. Aggravante: la diagnosi di confidenza avrebbe dichiarato 'alta' su un
    corpus vecchio — un meccanismo nato per dire quanto fidarsi che mente con
    sicurezza e peggio che non averlo.
    """
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        mtime = None
    if _cache.get(chiave + "_mtime") != mtime:
        _cache.pop(chiave, None)
        _cache[chiave + "_mtime"] = mtime
    return chiave in _cache


def _carica():
    if not _fresco("idx", INDICE):
        with open(INDICE, encoding="utf-8") as f:
            _cache["idx"] = json.load(f)
    return _cache["idx"]


def _normalizza(t):
    t = unicodedata.normalize("NFKD", (t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def _tokenizza(t):
    """Stessa tokenizzazione usata in indicizzazione: la lista di stopword viaggia
    dentro l'indice proprio per non poter divergere."""
    stop = set(_carica().get("stopword", ()))
    return [x for x in re.findall(r"[a-z0-9_]+", _normalizza(t))
            if len(x) >= 3 and x not in stop]


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


# ---------------- F1: valutatore di confidenza (CRAG deterministico) ----------------
# CRAG (arXiv 2401.15884) mette un valutatore davanti al generatore: se il recupero e
# scadente, lo dichiara invece di far finta di niente. Qui il valutatore e statistico,
# non un modello: due segnali indipendenti e spiegabili.
COPERTURA_ALTA, COPERTURA_BASSA = 0.60, 0.34
SEPARAZIONE_MIN = 0.15


def _termini_del_documento(doc_id, termini):
    """Quali termini della domanda compaiono davvero nel documento."""
    idx = _carica()
    presenti = set()
    for t in termini:
        for d, _ in idx["postings"].get(t, ()):
            if d == doc_id:
                presenti.add(t)
                break
    return presenti


def diagnosi(query, classifica_bm25):
    """Quanto fidarsi di questo recupero. Deterministico e motivato.

    copertura   = quanti termini della domanda sono coperti dai risultati in TESTA
                  (non dal solo primo: l'indice e per frammenti, e un frammento breve
                  puo contenere la risposta giusta pur citando poche parole della
                  domanda — misurare sul solo primo produce falsi allarmi, verificato).
                  Se chiedi 5 cose e i migliori ne coprono 1, il corpus non ha la
                  risposta: sta solo restituendo il meno peggio.
    separazione = quanto il primo stacca il quinto. Se tutti valgono uguale,
                  nessuno spicca: la domanda e diffusa o fuori dominio.
    """
    termini = _tokenizza(query)
    if not classifica_bm25 or not termini:
        return {"confidenza": "nessuna", "copertura": 0.0, "separazione": 0.0,
                "motivo": "nessun risultato: il corpus non contiene questi termini"}

    coperti = set()
    for doc_id, _ in classifica_bm25[:3]:
        coperti |= _termini_del_documento(doc_id, termini)
    copertura = len(coperti) / len(termini)

    punteggi = [p for _, p in classifica_bm25[:5]]
    separazione = ((punteggi[0] - punteggi[-1]) / punteggi[0]
                   if len(punteggi) > 1 and punteggi[0] > 0 else 1.0)

    if copertura < COPERTURA_BASSA:
        livello = "bassa"
        motivo = (f"solo {copertura:.0%} dei termini della domanda e coperto dai "
                  f"risultati: probabilmente il brain non contiene questa conoscenza")
    elif copertura >= COPERTURA_ALTA and separazione >= SEPARAZIONE_MIN:
        livello = "alta"
        motivo = f"{copertura:.0%} dei termini trovati e un risultato stacca gli altri"
    else:
        livello = "media"
        motivo = (f"{copertura:.0%} dei termini trovati"
                  + ("; nessun risultato spicca sugli altri"
                     if separazione < SEPARAZIONE_MIN else ""))

    return {"confidenza": livello, "copertura": round(copertura, 2),
            "separazione": round(separazione, 2), "motivo": motivo,
            # ONESTA DELLA MISURA: 'alta' significa che i termini della domanda sono
            # coperti dal corpus, NON che la risposta sia corretta o aggiornata. Chi
            # legge un'etichetta persuasiva tende a inferire affidabilita: la
            # differenza va dichiarata, non lasciata intuire.
            "misura": "copertura lessicale dei termini nel corpus — non correttezza, "
                      "non aggiornamento: verificare sempre la fonte e la sua data"}


# ---------------- F3: la memoria agisce sui risultati ----------------
# Registrare una lezione non deve servire solo a rileggerla: deve cambiare cio che
# vedi la volta dopo. Qui le lezioni ANNOTANO i risultati (non li filtrano mai:
# nascondere un risultato per una lezione vecchia sarebbe peggio del problema).
MAX_LEZIONI_IN_MEMORIA = 2000    # oltre, contano solo le piu recenti


def _memoria():
    path = os.path.join(BRAIN, "engine", "lessons.jsonl")
    if not _fresco("lezioni", path):
        voci = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for riga in f:
                    riga = riga.strip()
                    if riga:
                        try:
                            voci.append(json.loads(riga))
                        except json.JSONDecodeError:
                            continue
        # Il registro e append-only e cresce senza limite: caricarlo tutto a ogni
        # query si degraderebbe in silenzio. Le lezioni piu recenti sono anche le
        # piu attendibili (il brain e cambiato da allora).
        _cache["lezioni"] = voci[-MAX_LEZIONI_IN_MEMORIA:]
    return _cache["lezioni"]


def _corrisponde(nodo, base, etichetta):
    """Un nodo citato da una lezione si riferisce a questo risultato?

    Prudenza voluta: i nodi delle lezioni sono testo libero. Un nodo corto o numerico
    (es. '6', un esagramma) col confronto per sottostringa marchierebbe qualunque
    titolo che contiene quel carattere. Per quelli si pretende identita esatta.
    """
    n = os.path.splitext(str(nodo).strip().lower())[0]
    if not n:
        return False
    if len(n) < 4 or n.isdigit():
        return n == base
    if n == base:
        return True
    # Niente sottostringa nuda: un nodo 'excel' marchierebbe ogni file col nome che
    # lo contiene, attribuendo esperienza a note che non c'entrano. L'annotazione
    # sarebbe credibile e falsa, che e il difetto peggiore per una memoria.
    return re.search(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", etichetta) is not None


def _annota_memoria(file_rel, titolo):
    """Cosa dice l'esperienza passata su questo risultato."""
    base = os.path.splitext(os.path.basename(file_rel))[0].lower()
    etichetta = (titolo or "").lower()
    utile = cieco = 0
    for v in _memoria():
        for nodo in v.get("nodi", []):
            if _corrisponde(nodo, base, etichetta):
                if v.get("esito") == "utile":
                    utile += 1
                elif v.get("esito") == "vicolo-cieco":
                    cieco += 1
                break
    if not utile and not cieco:
        return None
    if cieco and not utile:
        nota = f"in passato non ha portato a nulla ({cieco}x)"
    elif utile >= 2:
        nota = f"ancoraggio consolidato: utile {utile}x"
    elif cieco:
        nota = f"esiti contrastanti: {utile}x utile, {cieco}x a vuoto"
    else:
        nota = f"gia risultato utile {utile}x (da confermare)"
    return {"utile": utile, "vicolo_cieco": cieco, "nota": nota}


def cerca(query, top=8, area=None):
    """Ricerca ibrida. Ritorna una lista di risultati, ognuno annotato con cio che
    la memoria operativa sa di quel nodo (F3)."""
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
        voce = {
            "file": d["file"],
            "titolo": d["titolo"],
            "area": d["area"],
            "estratto": d["estratto"],
            "punteggio": round(punteggio, 5),
            "motori": ("lessicale+semantico" if len(classifiche) > 1 else "lessicale"),
        }
        memoria = _annota_memoria(d["file"], d["titolo"])
        if memoria:
            voce["memoria"] = memoria
        fuori.append(voce)
        if len(fuori) >= top:
            break
    return fuori


def cerca_con_diagnosi(query, top=8, area=None):
    """Ricerca + valutazione della propria affidabilita (F1). E la forma che usano
    l'API e la CLI: un risultato senza giudizio sulla sua qualita induce a fidarsi
    anche quando non si dovrebbe."""
    risultati = cerca(query, top=top, area=area)
    return {"risultati": risultati, "diagnosi": diagnosi(query, cerca_bm25(query))}


if __name__ == "__main__":
    import argparse
    import sys as _sys
    _sys.path.insert(0, ROOT)
    from tools.console import usa_utf8
    usa_utf8()      # gli estratti contengono il corpus: accenti, caporali, trattini

    ap = argparse.ArgumentParser(description="Ricerca ibrida nel second brain")
    ap.add_argument("query", help="cosa cerchi")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--area", default=None, help="filtra per macroarea")
    ap.add_argument("--json", action="store_true", help="output JSON")
    a = ap.parse_args()

    esito = cerca_con_diagnosi(a.query, top=a.top, area=a.area)
    risultati, d = esito["risultati"], esito["diagnosi"]
    if a.json:
        print(json.dumps(esito, ensure_ascii=False, indent=2))
    elif not risultati:
        print(f"Nessun risultato. {d['motivo']}")
    else:
        simbolo = {"alta": "***", "media": "**", "bassa": "*", "nessuna": "-"}
        print(f"{len(risultati)} risultati per {a.query!r} "
              f"(motore: {risultati[0]['motori']})")
        print(f"confidenza {simbolo.get(d['confidenza'], '')} {d['confidenza'].upper()} "
              f"- {d['motivo']}\n")
        for i, r in enumerate(risultati, 1):
            print(f"{i}. [{r['area']}] {r['titolo']}  ({r['punteggio']})")
            print(f"   {r['file']}")
            if r.get("memoria"):
                print(f"   memoria: {r['memoria']['nota']}")
            print(f"   {r['estratto'][:160]}...\n")
