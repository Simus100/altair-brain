# -*- coding: utf-8 -*-
"""
altair-brain — propone collegamenti mancanti tra note (P7, A-MEM in versione sicura).

L'IDEA (A-MEM, arXiv 2502.12110): quando una nota entra nel sistema, il sistema cerca
le note affini e crea i collegamenti — cosi la rete si infittisce da sola e emergono
pattern che nessuno aveva pianificato (il principio Zettelkasten: connection over
collection).

LA VERSIONE SICURA: qui il sistema PROPONE e basta. Non scrive mai dentro le note.
Un collegamento sbagliato scritto in automatico corrompe il corpus in modo silenzioso
e difficile da rilevare; una proposta sbagliata si ignora. Il guadagno resta quasi
intatto, il rischio scende a zero.

COME: per ogni pagina della wiki usa il suo stesso contenuto come interrogazione
sull'indice ibrido (tools/search.py); le pagine molto affini che NON sono gia
collegate da un [[wikilink]] diventano proposte, ordinate per affinita.

Uso:
  python tools/link_suggest.py                    # top proposte a schermo
  python tools/link_suggest.py --area data-science --min 2.0
  python tools/link_suggest.py --out proposte.md  # da rivedere con calma
"""
import argparse, collections, json, math, os, re, sys

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

sys.path.insert(0, ROOT)

from tools.search import cerca  # noqa: E402


def pagine_wiki(area=None):
    base = os.path.join(ROOT, "wiki")
    fuori = []
    for root, _, files in os.walk(base):
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(root, f), ROOT).replace("\\", "/")
            if area and f"/{area}/" not in rel:
                continue
            fuori.append(rel)
    return fuori


def contenuto(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        t = f.read()
    s = t.lstrip()
    if s.startswith("---"):                      # via il front-matter
        fine = s.find("\n---", 3)
        if fine != -1:
            t = s[fine + 4:]
    return t


def link_esistenti(testo):
    return {m.lower() for m in re.findall(r"\[\[([^\]]+)\]\]", testo)}


# ---------------- F4: segnale STRUTTURALE (Adamic-Adar) ----------------
# Il segnale testuale vede solo le parole condivise. La teoria dei grafi ne offre uno
# indipendente: due pagine con molti VICINI IN COMUNE ma nessun collegamento diretto
# sono candidate forti. L'indice di Adamic-Adar pesa ogni vicino comune per la rarita
# (1/log(grado)): un vicino molto connesso — un indice, un hub — dice poco; un vicino
# raro dice molto. Euristica non supervisionata: nessun addestramento, nessuna
# dipendenza, deterministica.

def _grafo_per_file():
    """Adiacenza a livello di FILE: due pagine sono vicine se un qualsiasi loro nodo
    e collegato. E' la granularita giusta per 'questa pagina dovrebbe citare quella'."""
    path = os.path.join(ROOT, "graphify-out", "graph.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        g = json.load(f)
    di_chi = {n["id"]: (n.get("source_file") or "").replace("\\", "/") for n in g["nodes"]}
    vicini = collections.defaultdict(set)
    for e in g["links"]:
        a, b = di_chi.get(e.get("source")), di_chi.get(e.get("target"))
        if a and b and a != b:
            vicini[a].add(b)
            vicini[b].add(a)
    return vicini


# Il confronto e O(n^2): oltre questa soglia si guardano solo le pagine piu
# connesse, che sono anche quelle dove i collegamenti mancanti pesano di piu.
MAX_PAGINE_CONFRONTO = 800
MIN_VICINI_COMUNI = 2      # un solo vicino condiviso e coincidenza, non segnale
MIN_ADAMIC_ADAR = 1.0


def proposte_strutturali(vicini, area=None, esclusi=frozenset()):
    """Coppie di pagine wiki non collegate ma con vicini in comune, per Adamic-Adar.

    Le coppie sono NON ORIENTATE: graphify tiene un solo arco tra due pagine, quindi
    proporre sia A->B che B->A raddoppierebbe il rumore senza aggiungere nulla.
    Gli hub (indici, pagine-elenco) sono esclusi qui come nel segnale testuale: sono
    collegati a tutto per costruzione, e la loro vicinanza non significa parentela.
    """
    pagine = [f for f in vicini
              if f.startswith("wiki/") and f.endswith(".md")
              and os.path.splitext(os.path.basename(f))[0].lower() not in esclusi
              and (not area or f"/{area}/" in f)]
    if len(pagine) > MAX_PAGINE_CONFRONTO:
        pagine = sorted(pagine, key=lambda f: -len(vicini[f]))[:MAX_PAGINE_CONFRONTO]
    fuori = []
    for i, a in enumerate(pagine):
        for b in pagine[i + 1:]:
            if b in vicini[a]:
                continue                      # gia collegate: niente da proporre
            comuni = {z for z in vicini[a] & vicini[b]
                      if os.path.splitext(os.path.basename(z))[0].lower() not in esclusi}
            if len(comuni) < MIN_VICINI_COMUNI:
                continue
            punteggio = sum(1.0 / math.log(len(vicini[z]))
                            for z in comuni if len(vicini[z]) > 1)
            if punteggio >= MIN_ADAMIC_ADAR:
                fuori.append({"da": a, "a": b, "punteggio": punteggio,
                              "comuni": len(comuni)})
    return sorted(fuori, key=lambda p: -p["punteggio"])


# --- costanti condivise (importabili: servono anche ai test) ---

# Gli indici sono hub: collegano tutto per definizione, proporli non aggiunge nulla.
HUB = {"index", "metodi", "strumenti", "progetti", "insegnamenti"}
# Strati GENERATI: un wikilink scritto a mano li verrebbe sovrascritto al rebuild.
# Li si migliora aggiungendo la relazione in engine/aion.model.json, non nella pagina.
from tools.frontmatter import STRATI_GENERATI as GENERATI   # noqa: E402


def main():
    """Flusso CLI. Isolato in una funzione perche il modulo dev'essere
    IMPORTABILE: con argparse a livello globale, un semplice import esegue il
    parsing e termina il processo (SystemExit) — rilevato dai test."""
    ap = argparse.ArgumentParser(description="Proposte di collegamento tra pagine della wiki")
    ap.add_argument("--area", default=None, help="limita a una macroarea")
    ap.add_argument("--min", type=float, default=0.55,
                    help="affinita RELATIVA minima 0-1 (default 0.55): quanto il candidato "
                         "e vicino al miglior risultato di quella pagina")
    ap.add_argument("--per-pagina", type=int, default=2, help="max proposte per pagina")
    ap.add_argument("--out", default=None, help="scrive un report markdown invece di stampare")
    ap.add_argument("--include-generated", action="store_true",
                    help="includi gli strati GENERATI (wiki/aion): li i link vanno aggiunti "
                         "nel modello engine/aion.model.json, non nella pagina")
    a = ap.parse_args()

    # Gli indici sono hub: collegano tutto per definizione, proporli non aggiunge nulla.

    proposte, saltate_generate = [], 0
    for rel in pagine_wiki(a.area):
        if any(rel.startswith(g) for g in GENERATI) and not a.include_generated:
            saltate_generate += 1
            continue
        testo = contenuto(rel)
        if len(testo.strip()) < 80:
            continue
        nome = os.path.splitext(os.path.basename(rel))[0].lower()
        if nome in HUB:
            continue
        gia = link_esistenti(testo) | {nome}
        area_pagina = rel.split("/")[1]

        # la pagina interroga il corpus con le proprie stesse parole
        risultati = [r for r in cerca(testo[:1200], top=15)
                     if r["file"].startswith("wiki/") and r["file"] != rel]
        if not risultati:
            continue
        # BM25 non e normalizzato e cresce con la lunghezza della query: l'affinita
        # ASSOLUTA non e confrontabile tra pagine. Si usa quella RELATIVA al miglior
        # risultato della pagina stessa, che invece lo e.
        massimo = max(r["punteggio"] for r in risultati) or 1.0
        presi = 0
        for r in risultati:
            candidato = os.path.splitext(os.path.basename(r["file"]))[0].lower()
            if candidato in gia or candidato in HUB:
                continue
            affinita = r["punteggio"] / massimo
            if affinita < a.min:
                continue
            proposte.append({
                "da": rel, "a": r["file"], "wikilink": candidato,
                "affinita": round(affinita, 3),
                "intercampo": area_pagina != r["area"],
                "perche": r["estratto"][:140],
            })
            gia.add(candidato)
            presi += 1
            if presi >= a.per_pagina:
                break

    # --- fusione col segnale strutturale (F4) ---
    # Testo e struttura sbagliano in modi diversi: il testo vede parole condivise anche
    # dove non c'e relazione reale, la struttura vede relazioni anche senza parole in
    # comune. Si fondono per POSIZIONE (stessa logica RRF usata nella ricerca), perche
    # affinita testuale e indice Adamic-Adar non sono grandezze confrontabili.
    vicini = _grafo_per_file()
    strutturali = proposte_strutturali(vicini, a.area, esclusi=HUB) if vicini else []

    RRF_K = 60
    punti, dettagli = collections.defaultdict(float), {}


    def _coppia(x, y):
        """Chiave NON orientata: un collegamento tra due pagine e uno solo."""
        return tuple(sorted((x, y)))


    for rango, p in enumerate(proposte, start=1):
        k = _coppia(p["da"], p["a"])
        punti[k] += 1.0 / (RRF_K + rango)
        dettagli.setdefault(k, {}).update(p, segnale="testo")

    for rango, p in enumerate(strutturali, start=1):
        k = _coppia(p["da"], p["a"])
        punti[k] += 1.0 / (RRF_K + rango)
        d = dettagli.setdefault(k, {
            "da": p["da"], "a": p["a"],
            "wikilink": os.path.splitext(os.path.basename(p["a"]))[0].lower(),
            "affinita": 0.0,
            "intercampo": p["da"].split("/")[1] != p["a"].split("/")[1],
            "perche": f"{p['comuni']} vicini in comune nel grafo, nessun collegamento diretto",
        })
        d["segnale"] = "testo+struttura" if d.get("segnale") == "testo" else "struttura"
        d["adamic_adar"] = round(p["punteggio"], 3)

    proposte = []
    for k, v in dettagli.items():
        if v["da"] == v["a"]:
            continue
        v["fusione"] = round(punti[k], 5)
        proposte.append(v)

    # Ordine: prima le intercampo (piu preziose), poi quelle su cui DUE metodi
    # indipendenti concordano, poi il punteggio fuso.
    proposte.sort(key=lambda p: (-p["intercampo"],
                                 p.get("segnale") != "testo+struttura",
                                 -p["fusione"]))

    if not proposte:
        print("Nessuna proposta sopra la soglia: la wiki e gia ben collegata.")
        sys.exit(0)

    intercampo = [p for p in proposte if p["intercampo"]]
    doppio = [p for p in proposte if p.get("segnale") == "testo+struttura"]
    righe = [
        "# Proposte di collegamento (da rivedere a mano)",
        "",
        f"Generate da `tools/link_suggest.py` — {len(proposte)} proposte, di cui "
        f"**{len(intercampo)} INTERCAMPO** (collegano aree diverse: le piu preziose) e "
        f"**{len(doppio)} confermate da entrambi i segnali** (testo *e* struttura del "
        f"grafo: le piu affidabili, perche due metodi indipendenti concordano).",
        "",
        "> Nessuna e stata scritta nelle note. Per accettarne una: aggiungi il `[[wikilink]]`",
        "> nella pagina di partenza (o, se collega due aree, dichiarala in `engine/bridges.json`),",
        "> poi rilancia `python tools/rebuild_all.py`.",
        "",
    ]
    if saltate_generate:
        righe += [f"_({saltate_generate} pagine di strati GENERATI escluse: li un wikilink a mano "
                  f"verrebbe sovrascritto — si aggiunge la relazione in `engine/aion.model.json`. "
                  f"Per vederle comunque: `--include-generated`.)_", ""]
    for p in proposte[:60]:
        marchi = []
        if p["intercampo"]:
            marchi.append("**[INTERCAMPO]**")
        if p.get("segnale") == "testo+struttura":
            marchi.append("**[DOPPIO SEGNALE]**")
        prova = f"testo {p['affinita']}" if p["affinita"] else ""
        if p.get("adamic_adar"):
            prova = (prova + " · " if prova else "") + f"struttura {p['adamic_adar']}"
        righe.append(f"- `{p['da']}` → `[[{p['wikilink']}]]` "
                     f"{' '.join(marchi)} _({prova})_")
        righe.append(f"  - {p['perche']}...")

    testo_finale = "\n".join(righe)
    if a.out:
        with open(os.path.join(ROOT, a.out), "w", encoding="utf-8", newline="\n") as f:
            f.write(testo_finale + "\n")
        print(f"{len(proposte)} proposte ({len(intercampo)} intercampo) -> {a.out}")
    else:
        print(testo_finale)



if __name__ == "__main__":
    main()
