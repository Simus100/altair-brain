# -*- coding: utf-8 -*-
"""
altair-brain — pacchetto di contesto per un LLM, entro un budget (F6).

IL PROBLEMA (context rot, misurato su 18 modelli di frontiera): l'accuratezza cala
del 30-50% al crescere dell'input, ben prima del limite dichiarato della finestra.
Piu contesto NON significa risposte migliori: significa risposte peggiori, con
l'aggravante che il degrado e silenzioso.

IL PROBLEMA QUI: il brain offriva pezzi separati — grafo da una parte, ricerca
dall'altra, lezioni da un'altra — e stava all'agente assemblarli, di solito
prendendo troppo. Questo modulo fa il lavoro una volta sola e bene.

COSA MONTA, in ordine di priorita entro il budget:
1. la DIAGNOSI (costa nulla, e dice se fidarsi: va sempre in testa)
2. i FRAMMENTI pertinenti, deduplicati per file (non file interi: estratti precisi)
3. il VICINATO nel grafo dei file in testa (cosa c'e intorno, senza leggere il grafo)
4. le LEZIONI applicabili (cosa si e gia imparato su questi nodi)

Il budget e in token stimati (~4 caratteri per token: approssimazione deterministica,
non serve un tokenizzatore vero per decidere cosa tagliare).

Uso:  python tools/context_pack.py "come si valuta la qualita di un dataset" --budget 1500
Come modulo:  from tools.context_pack import pacchetto
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.search import cerca_con_diagnosi, _memoria, _corrisponde  # noqa: E402

GRAFO = os.path.join(ROOT, "graphify-out", "graph.json")
CHAR_PER_TOKEN = 4
QUOTA_FRAMMENTI = 0.70      # il grosso va al contenuto
QUOTA_VICINATO = 0.15
QUOTA_LEZIONI = 0.15
SOGLIA_PERTINENZA = 0.50    # quanto un frammento deve valere rispetto al migliore


def _token(testo):
    return max(1, len(testo or "") // CHAR_PER_TOKEN)


def _vicinato(file_in_testa, massimo=8):
    """Cosa c'e intorno ai file trovati, secondo il grafo. Evita all'agente di
    doversi caricare il grafo per capire il contesto di cio che ha letto."""
    if not os.path.exists(GRAFO):
        return []
    with open(GRAFO, encoding="utf-8") as f:
        g = json.load(f)
    di_chi = {n["id"]: (n.get("source_file") or "").replace("\\", "/") for n in g["nodes"]}
    vicini = {}
    for e in g["links"]:
        a, b = di_chi.get(e.get("source")), di_chi.get(e.get("target"))
        if not a or not b or a == b:
            continue
        vicini.setdefault(a, set()).add(b)
        vicini.setdefault(b, set()).add(a)
    fuori, visti = [], set(file_in_testa)
    for f in file_in_testa:
        for v in sorted(vicini.get(f, ())):
            if v in visti or not v.endswith(".md"):
                continue
            visti.add(v)
            fuori.append({"file": v, "vicino_di": f})
            if len(fuori) >= massimo:
                return fuori
    return fuori


def _lezioni_pertinenti(file_in_testa, massimo=5):
    """Le lezioni che riguardano cio che stiamo per dare in pasto al modello."""
    basi = {os.path.splitext(os.path.basename(f))[0].lower() for f in file_in_testa}
    fuori = []
    for v in _memoria():
        for nodo in v.get("nodi", []):
            if any(_corrisponde(nodo, b, "") for b in basi):
                fuori.append({"esito": v.get("esito"), "nota": v.get("nota", ""),
                              "nodi": v.get("nodi", []), "quando": (v.get("ts") or "")[:10]})
                break
        if len(fuori) >= massimo:
            break
    return fuori


def pacchetto(query, budget_token=2000, area=None):
    """Assembla il contesto migliore per questa domanda, entro il budget."""
    budget_token = max(200, min(int(budget_token or 2000), 12000))
    esito = cerca_con_diagnosi(query, top=20, area=area)
    diagnosi = esito["diagnosi"]

    # 1. frammenti: uno per file (il secondo frammento dello stesso file aggiunge
    #    poco e consuma budget), tagliati alla quota.
    #    SOGLIA DI PERTINENZA: riempire il budget fino all'orlo con risultati
    #    marginali peggiora la risposta invece di migliorarla (context rot). Si
    #    scarta cio che vale meno di una frazione del migliore: meglio consegnare
    #    tre frammenti buoni che dieci mediocri.
    tetto_frammenti = int(budget_token * QUOTA_FRAMMENTI)
    migliore = esito["risultati"][0]["punteggio"] if esito["risultati"] else 0.0
    soglia = migliore * SOGLIA_PERTINENZA
    frammenti, visti, usati = [], set(), 0
    for r in esito["risultati"]:
        if r["file"] in visti or r["punteggio"] < soglia:
            continue
        costo = _token(r["estratto"]) + _token(r["titolo"])
        if usati + costo > tetto_frammenti:
            continue
        visti.add(r["file"])
        voce = {"file": r["file"], "titolo": r["titolo"], "area": r["area"],
                "testo": r["estratto"]}
        if r.get("memoria"):
            voce["memoria"] = r["memoria"]["nota"]
        frammenti.append(voce)
        usati += costo

    in_testa = [f["file"] for f in frammenti[:4]]

    # 2. vicinato
    vic, tetto_vic, usati_vic = [], int(budget_token * QUOTA_VICINATO), 0
    for v in _vicinato(in_testa):
        costo = _token(v["file"]) + 4
        if usati_vic + costo > tetto_vic:
            break
        vic.append(v)
        usati_vic += costo

    # 3. lezioni
    lez, tetto_lez, usati_lez = [], int(budget_token * QUOTA_LEZIONI), 0
    for l in _lezioni_pertinenti(in_testa):
        costo = _token(l["nota"]) + 8
        if usati_lez + costo > tetto_lez:
            break
        lez.append(l)
        usati_lez += costo

    avvertenze = []
    if diagnosi["confidenza"] in ("bassa", "nessuna"):
        avvertenze.append(
            "Confidenza " + diagnosi["confidenza"] + ": " + diagnosi["motivo"] +
            ". Non dedurne una risposta certa; dillo a chi ha chiesto.")
    if any(l["esito"] == "vicolo-cieco" for l in lez):
        avvertenze.append(
            "Alcuni di questi nodi in passato non hanno portato a nulla: "
            "vedi le lezioni allegate prima di ripercorrere la stessa strada.")

    p = {
        "query": query,
        "area": area,
        "budget_token": budget_token,
        "diagnosi": diagnosi,
        "avvertenze": avvertenze,
        "frammenti": frammenti,
        "vicinato": vic,
        "lezioni": lez,
    }

    # BUDGET SUL TESTO CONSEGNATO, non sui pezzi. Sommare il costo dei frammenti
    # ignora l'impalcatura (titoli, percorsi, intestazioni) e sfora: misurato 982
    # token reali contro 730 stimati. Si misura l'output vero e si pota dalla coda
    # — che e la parte meno pertinente — finche rientra.
    while len(frammenti) > 1 and _token(come_testo(p)) > budget_token:
        frammenti.pop()
        p["frammenti"] = frammenti
    while vic and _token(come_testo(p)) > budget_token:
        vic.pop()
        p["vicinato"] = vic
    p["token_stimati"] = _token(come_testo(p))
    return p


def come_testo(p):
    """Il pacchetto in forma leggibile, pronto da incollare in un prompt."""
    r = [f"# Contesto dal brain per: {p['query']}",
         f"_confidenza {p['diagnosi']['confidenza']}: {p['diagnosi']['motivo']}_", ""]
    for a in p["avvertenze"]:
        r.append(f"> ATTENZIONE: {a}")
    if p["avvertenze"]:
        r.append("")
    if p["frammenti"]:
        r.append("## Conoscenza pertinente")
        for f in p["frammenti"]:
            r.append(f"### {f['titolo']}  _({f['file']})_")
            if f.get("memoria"):
                r.append(f"_memoria: {f['memoria']}_")
            r.append(f["testo"])
            r.append("")
    if p["vicinato"]:
        r.append("## Intorno a questi (nel grafo)")
        r += [f"- `{v['file']}` — collegato a `{v['vicino_di']}`" for v in p["vicinato"]]
        r.append("")
    if p["lezioni"]:
        r.append("## Cosa si e gia imparato")
        r += [f"- [{l['esito']}] {l['nota']} _({l['quando']})_" for l in p["lezioni"]]
        r.append("")
    # token_stimati manca durante la potatura (si misura il testo per decidere cosa
    # tagliare, e il testo cita la misura): si tollera l'assenza invece di duplicare
    # la logica di rendering.
    r.append(f"_~{p.get('token_stimati', '...')} token su un budget di {p['budget_token']}_")
    return "\n".join(r)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Pacchetto di contesto entro budget")
    ap.add_argument("query")
    ap.add_argument("--budget", type=int, default=2000, help="token stimati (200-12000)")
    ap.add_argument("--area", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    p = pacchetto(a.query, a.budget, a.area)
    print(json.dumps(p, ensure_ascii=False, indent=2) if a.json else come_testo(p))
