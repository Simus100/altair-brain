# -*- coding: utf-8 -*-
"""
altair-brain — consolidamento offline della memoria (F5, "sleep-time compute").

L'IDEA (tema di frontiera 2026: SCM arXiv 2604.20943, Anthropic Dreaming): un sistema
che accumula e basta si degrada. Gli agenti che durano elaborano la memoria TRA le
interazioni — fondono duplicati, estraggono pattern, segnalano cio che e stantio — e
precalcolano cio che servira, invece di ricominciare da zero a ogni domanda.

QUI E DETERMINISTICO. Niente modello: conteggi, insiemi e sovrapposizione di termini.
Cio che serve un LLM (riscrivere due note in una) NON viene fatto: viene PROPOSTO.

PRODUCE:
1. DIGEST PER AREA (la parte "sleep" vera): risposte precalcolate alle domande di
   orientamento — i nodi piu centrali, cosa e cambiato di recente, i temi ricorrenti.
   Un agente che apre il brain domani trova gia la mappa, senza ricostruirla.
2. PROPOSTE DI POTATURA: lezioni ridondanti, note quasi identiche, conoscenza stantia.
   Sempre e solo proposte: cancellare in automatico e come lasciar riordinare la
   libreria a chi non sa cosa stai scrivendo.

Uso:  python tools/consolidate.py            (rigenera i digest, elenca le proposte)
      python tools/consolidate.py --solo-proposte
"""
import argparse, collections, datetime, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

GRAFO = os.path.join(ROOT, "graphify-out", "graph.json")
LEZIONI = os.path.join(ROOT, "engine", "lessons.jsonl")
INDICE = os.path.join(ROOT, "engine", "search_index.json")
OUT_DIR = os.path.join(ROOT, "engine", "digest")

MAX_FILE_CONFRONTO = 1500   # oltre, il doppio ciclo non e piu accettabile
SOGLIA_SIMILI = 0.55        # sovrapposizione di termini oltre cui due note si somigliano
RECENTI_GIORNI = 30


def _carica_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _lezioni():
    voci = []
    if os.path.exists(LEZIONI):
        with open(LEZIONI, encoding="utf-8") as f:
            for riga in f:
                riga = riga.strip()
                if riga:
                    try:
                        voci.append(json.loads(riga))
                    except json.JSONDecodeError:
                        continue
    return voci


# ---------------- 1. digest per area (precalcolo) ----------------
def digest_per_area():
    """Per ogni macroarea: i nodi piu centrali, le note recenti, i temi.
    E' la mappa che altrimenti ogni agente si ricostruisce a ogni sessione."""
    g = _carica_json(GRAFO)
    if not g:
        return {}
    di_chi = {n["id"]: (n.get("source_file") or "").replace("\\", "/") for n in g["nodes"]}
    etichetta = {n["id"]: n.get("label", "") for n in g["nodes"]}

    grado = collections.Counter()
    for e in g["links"]:
        for estremo in (e.get("source"), e.get("target")):
            if estremo in di_chi:
                grado[estremo] += 1

    # Solo le macroaree dichiarate: areas.json e il registro canonico. Cartelle
    # tecniche come _inbox non sono aree e non meritano un digest.
    reg = _carica_json(os.path.join(ROOT, "areas.json"), {}) or {}
    valide = {a["id"] for a in reg.get("areas", [])} or None

    per_area = collections.defaultdict(lambda: {"nodi": [], "file": set()})
    for nid, sf in di_chi.items():
        parti = sf.split("/")
        if len(parti) > 2 and parti[0] in ("raw", "wiki"):
            if valide and parti[1] not in valide:
                continue
            a = per_area[parti[1]]
            a["nodi"].append((grado[nid], etichetta[nid], sf))
            a["file"].add(sf)

    oggi = datetime.date.today()
    digest = {}
    for area, dati in per_area.items():
        # Ordina per GRADO soltanto: usare l'etichetta come spareggio farebbe vincere
        # il testo alfabeticamente maggiore tra nodi di pari grado, spacciando per
        # "centrale" un nodo qualunque (difetto colto alla prima esecuzione).
        centrali = sorted(dati["nodi"], key=lambda x: -x[0])[:12]
        recenti = []
        for f in sorted(dati["file"]):
            p = os.path.join(ROOT, f)
            if not os.path.exists(p):
                continue
            eta = (oggi - datetime.date.fromtimestamp(os.path.getmtime(p))).days
            if eta <= RECENTI_GIORNI:
                recenti.append((eta, f))
        digest[area] = {
            "generato_il": oggi.isoformat(),
            "file": len(dati["file"]),
            "nodi": len(dati["nodi"]),
            "centrali": [{"nodo": lab, "grado": gr, "dove": sf}
                         for gr, lab, sf in centrali if lab],
            "modificati_di_recente": [{"giorni_fa": e, "file": f}
                                      for e, f in sorted(recenti)[:10]],
        }
    return digest


# ---------------- 2. proposte di potatura ----------------
def lezioni_ridondanti(voci):
    """Stessa lezione registrata piu volte: stessi nodi e stesso esito."""
    gruppi = collections.defaultdict(list)
    for v in voci:
        chiave = (tuple(sorted(v.get("nodi", []))), v.get("esito"))
        if chiave[0]:
            gruppi[chiave].append(v)
    return [{"nodi": list(k[0]), "esito": k[1], "occorrenze": len(g),
             "esempio": (g[0].get("nota") or g[0].get("domanda", ""))[:90]}
            for k, g in gruppi.items() if len(g) > 1]


def note_simili():
    """Note che dicono quasi la stessa cosa, per sovrapposizione dei termini.
    Segnale grezzo ma onesto: serve a farsi la domanda, non a decidere."""
    idx = _carica_json(INDICE)
    if not idx:
        return []
    per_file = collections.defaultdict(collections.Counter)
    for d, posting in idx["postings"].items():
        for doc_id, _ in posting:
            per_file[idx["documenti"][doc_id]["file"]][d] += 1

    files = sorted(f for f in per_file if f.startswith(("raw/", "wiki/")))
    # Il confronto e O(n^2): a 134 file e istantaneo, a 5.000 sono ~12M coppie e
    # il consolidamento smetterebbe di essere "offline" per diventare "mai".
    # Meglio dichiarare il limite che degradare in silenzio.
    if len(files) > MAX_FILE_CONFRONTO:
        print(f"  [nota] {len(files)} file: confronto delle note simili saltato "
              f"(limite {MAX_FILE_CONFRONTO}). Serve un indice invertito, non un "
              f"doppio ciclo.")
        return []
    fuori = []
    for i, a in enumerate(files):
        ta = set(per_file[a])
        if len(ta) < 25:                      # note troppo brevi: confronto inaffidabile
            continue
        for b in files[i + 1:]:
            tb = set(per_file[b])
            if len(tb) < 25:
                continue
            j = len(ta & tb) / len(ta | tb)
            if j >= SOGLIA_SIMILI:
                fuori.append({"a": a, "b": b, "sovrapposizione": round(j, 3)})
    return sorted(fuori, key=lambda x: -x["sovrapposizione"])


def conoscenza_stantia():
    """Nodi mai risultati utili e mai citati: candidati a revisione, non a cestino."""
    voci = _lezioni()
    citati = {str(n).lower() for v in voci for n in v.get("nodi", [])}
    ciechi = collections.Counter()
    for v in voci:
        if v.get("esito") == "vicolo-cieco":
            for n in v.get("nodi", []):
                ciechi[str(n).lower()] += 1
    return {"mai_citati_nelle_lezioni": len(citati) == 0,
            "vicoli_ciechi_ricorrenti": [{"nodo": n, "volte": c}
                                         for n, c in ciechi.most_common(10) if c >= 2]}


def main():
    ap = argparse.ArgumentParser(description="Consolidamento offline della memoria")
    ap.add_argument("--solo-proposte", action="store_true",
                    help="non riscrivere i digest, elenca solo cosa andrebbe potato")
    a = ap.parse_args()

    voci = _lezioni()
    print("== CONSOLIDAMENTO OFFLINE ==\n")

    if not a.solo_proposte:
        digest = digest_per_area()
        os.makedirs(OUT_DIR, exist_ok=True)
        for area, d in sorted(digest.items()):
            with open(os.path.join(OUT_DIR, f"{area}.json"), "w",
                      encoding="utf-8", newline="\n") as f:
                json.dump(d, f, ensure_ascii=False, indent=2, sort_keys=True)
                f.write("\n")
        print(f"Digest precalcolati: {len(digest)} aree -> engine/digest/")
        for area, d in sorted(digest.items()):
            capo = d["centrali"][0]["nodo"] if d["centrali"] else "-"
            print(f"  {area}: {d['file']} file, {d['nodi']} nodi, "
                  f"{len(d['modificati_di_recente'])} modificati di recente "
                  f"(piu centrale: {capo})")
        print()

    print(f"Lezioni in memoria: {len(voci)}")
    rid = lezioni_ridondanti(voci)
    if rid:
        print(f"\nLEZIONI RIDONDANTI ({len(rid)}) — stessi nodi, stesso esito:")
        for r in rid[:8]:
            print(f"  - {r['occorrenze']}x {r['esito']} su {r['nodi']}: {r['esempio']}")
        print("  (proposta: tenerne una, o registrare cosa e cambiato tra le due)")
    else:
        print("Lezioni ridondanti: nessuna.")

    simili = note_simili()
    if simili:
        print(f"\nNOTE MOLTO SIMILI ({len(simili)}) — sovrapposizione di termini:")
        for s in simili[:8]:
            print(f"  - {s['sovrapposizione']:.0%}  {s['a']}")
            print(f"           {s['b']}")
        print("  (proposta: fonderle, o distinguerle meglio se trattano cose diverse)")
    else:
        print("\nNote quasi duplicate: nessuna.")

    st = conoscenza_stantia()
    if st["vicoli_ciechi_ricorrenti"]:
        print(f"\nVICOLI CIECHI RICORRENTI:")
        for v in st["vicoli_ciechi_ricorrenti"]:
            print(f"  - {v['nodo']}: {v['volte']} volte senza esito")
        print("  (proposta: rivedere quella conoscenza, o segnarla come non operativa)")

    print("\nNessun file e stato modificato o cancellato: sono proposte.")


if __name__ == "__main__":
    main()
