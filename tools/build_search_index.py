# -*- coding: utf-8 -*-
"""
altair-brain — indice di ricerca lessicale BM25 sul corpus (P4, meta lessicale).

PROBLEMA RISOLTO: `graphify query` naviga la STRUTTURA (nomi, relazioni). Se cerchi
un concetto con parole diverse da quelle scritte nei titoli, non lo trovi. E soprattutto:
graphify indicizza SOLO .md, quindi le 21 note .txt di raw/data-science (430KB di
metodologia reale) erano invisibili. Questo indice le include.

SCELTE:
- BM25 implementato qui, in puro Python: nessuna dipendenza, gira ovunque (CI, VPS,
  qualunque macchina). Il vincolo del progetto e "nessuna API a pagamento e tutto
  deterministico": una libreria in meno e una garanzia di durata in piu.
- L'indice e un JSON committato: i consumatori (API, altri dispositivi) lo usano
  senza ricostruirlo, come gia avviene per engine/iching.db.json.
- Il livello SEMANTICO (embeddings) e opzionale e separato: vedi tools/search.py.

Uso:  python tools/build_search_index.py     (parte di rebuild_all.py)
"""
import json, math, os, re, sys, unicodedata

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

OUT = os.path.join(BRAIN, "engine", "search_index.json")

CARTELLE = ("raw", "wiki", "reports", "engine")
ESTENSIONI = (".md", ".txt", ".sql")
ESCLUDI = ("graphify-out", "node_modules", "__pycache__", "archive")
MIN_CHUNK = 60          # caratteri: sotto questa soglia il frammento non e informativo
MAX_CHUNK = 1800        # caratteri: oltre, si spezza (un blocco troppo lungo diluisce il match)

# Stopword italiane+inglesi essenziali: tolgono rumore senza toccare i termini tecnici.
STOP = set("""
a ai al alla alle allo agli anche ancora avere aveva avevano c che chi ci cio coi col come con
cosa cui da dal dalla dalle dallo dagli dei del della delle dello degli di do dopo dove due e ed
essere fa fare fino fra gli ha hanno ho i il in io la le lei li lo loro ma me mi mia mie mio miei
ne negli nei nel nella nelle nello no noi non nostra nostro o od ogni oltre per perche piu po
qual quale quali quando quanto quel quella quelle quelli quello questa queste questi questo qui
se sei senza si sia siamo sono sta stata stato su sua sue sui sul sulla sulle sullo suo suoi ti
tra tu tua tue tuo tuoi tutti tutto un una uno vi voi
a an and are as at be by for from has have in is it its of on or that the this to was were will with
""".split())


def normalizza(testo: str) -> str:
    """Minuscolo senza accenti: 'analisi' e 'Analisí' devono coincidere."""
    t = unicodedata.normalize("NFKD", testo.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def tokenizza(testo: str) -> list:
    grezzi = re.findall(r"[a-z0-9_]+", normalizza(testo))
    return [t for t in grezzi if len(t) >= 3 and t not in STOP]


def leggi(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def togli_frontmatter(testo):
    """Il front-matter e metadato, non contenuto: non deve inquinare il ranking.
    Regola del blocco delimitato in tools/frontmatter, condivisa."""
    meta, corpo = fm.dividi(testo)
    return corpo, meta


def spezza(testo, rel):
    """Frammenti per titolo markdown quando ci sono titoli; altrimenti blocchi separati
    da righe vuote. Ogni frammento conserva il titolo piu vicino: e il suo contesto.

    GRANULARITA: molte note grezze sono prosa senza titoli. Spezzarle per titolo le
    lascerebbe in un blocco unico, e BM25 penalizza i documenti lunghi (la frequenza
    dei termini e normalizzata sulla lunghezza): una nota intera diventa un pagliaio.
    Con i blocchi si recupera la precisione del recupero."""
    pezzi = []
    ha_titoli = any(r.startswith("#") for r in testo.splitlines())
    if rel.endswith(".md") and ha_titoli:
        titolo, buffer = "", []
        for riga in testo.splitlines():
            if riga.startswith("#"):
                if buffer:
                    pezzi.append((titolo, "\n".join(buffer)))
                    buffer = []
                titolo = riga.lstrip("#").strip()
            else:
                buffer.append(riga)
        if buffer:
            pezzi.append((titolo, "\n".join(buffer)))
    else:
        blocco = []
        for riga in testo.splitlines():
            if riga.strip():
                blocco.append(riga)
            elif blocco:
                pezzi.append(("", "\n".join(blocco)))
                blocco = []
        if blocco:
            pezzi.append(("", "\n".join(blocco)))

    fuori = []
    for titolo, corpo in pezzi:
        corpo = corpo.strip()
        if len(corpo) < MIN_CHUNK:
            continue
        while len(corpo) > MAX_CHUNK:          # taglia sul confine di riga piu vicino
            taglio = corpo.rfind("\n", 0, MAX_CHUNK)
            taglio = taglio if taglio > MIN_CHUNK else MAX_CHUNK
            fuori.append((titolo, corpo[:taglio].strip()))
            corpo = corpo[taglio:].strip()
        if len(corpo) >= MIN_CHUNK:
            fuori.append((titolo, corpo))
    return fuori


# ---------------- raccolta del corpus ----------------
# DETERMINISMO: l'indice e committato e la CI verifica che coincida con quello
# rigenerato su Linux. os.walk NON garantisce l'ordine delle sottocartelle (dipende
# dal filesystem: Windows e Linux danno ordini diversi), e l'ordine dei frammenti
# finisce dentro il JSON. Si raccolgono quindi TUTTI i percorsi e si ordinano prima
# di elaborarli: stesso corpus -> stesso indice, su qualunque macchina.
def raccogli_percorsi():
    trovati = []
    for base in CARTELLE:
        radice = os.path.join(BRAIN, base)
        if not os.path.isdir(radice):
            continue
        for root, dirs, files in os.walk(radice):
            dirs[:] = sorted(d for d in dirs if d not in ESCLUDI and not d.startswith("."))
            for f in files:
                if f.endswith(ESTENSIONI):
                    trovati.append(
                        os.path.relpath(os.path.join(root, f), BRAIN).replace("\\", "/"))
    return sorted(trovati)


documenti, postings, df = [], {}, {}

for rel in raccogli_percorsi():
    testo = leggi(os.path.join(BRAIN, rel))
    if not testo:
        continue
    corpo, meta = togli_frontmatter(testo)
    parti = rel.split("/")
    area = parti[1] if len(parti) > 2 and parti[0] in ("raw", "wiki") else parti[0]
    for titolo, frammento in spezza(corpo, rel):
        idx = len(documenti)
        token = tokenizza(titolo + " " + frammento)
        if not token:
            continue
        documenti.append({
            "file": rel,
            "titolo": titolo or os.path.basename(rel),
            "area": area,
            "estratto": re.sub(r"\s+", " ", frammento)[:280],
            "n_token": len(token),
            "tags": meta.get("tags", ""),
        })
        tf = {}
        for t in token:
            tf[t] = tf.get(t, 0) + 1
        for t, c in tf.items():
            postings.setdefault(t, []).append([idx, c])
            df[t] = df.get(t, 0) + 1

N = len(documenti)
avgdl = sum(d["n_token"] for d in documenti) / N if N else 0.0
idf = {t: round(math.log(1 + (N - n + 0.5) / (n + 0.5)), 5) for t, n in df.items()}

indice = {
    "versione": 1,
    "descrizione": "Indice BM25 del corpus altair-brain. Generato da tools/build_search_index.py; "
                   "interrogato da tools/search.py e dall'endpoint /v1/search. "
                   "Include i .txt che graphify non indicizza.",
    "parametri": {"k1": 1.5, "b": 0.75},
    # La lista viaggia CON l'indice: chi interroga deve filtrare esattamente come si e
    # filtrato in indicizzazione. Tenerne due copie le fa divergere, e una domanda in
    # linguaggio naturale finisce piena di termini che per costruzione non possono
    # essere trovati — falsando la misura di copertura (difetto reale, gia occorso).
    "stopword": sorted(STOP),
    "n_documenti": N,
    "avgdl": round(avgdl, 3),
    "documenti": documenti,
    "idf": idf,
    "postings": postings,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(indice, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    f.write("\n")

file_unici = len({d["file"] for d in documenti})
peso = os.path.getsize(OUT) / 1024
print(f"Indice di ricerca: {N} frammenti da {file_unici} file, "
      f"{len(idf)} termini ({peso:.0f} KB) -> engine/search_index.json")
