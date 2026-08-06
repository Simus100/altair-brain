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
import argparse, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
HUB = {"index", "metodi", "strumenti", "progetti", "insegnamenti"}
# Strati GENERATI: un wikilink scritto a mano li verrebbe sovrascritto al rebuild.
# Li si migliora aggiungendo la relazione in engine/aion.model.json, non nella pagina.
GENERATI = ("wiki/aion/",)

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

proposte.sort(key=lambda p: (-p["intercampo"], -p["affinita"]))

if not proposte:
    print("Nessuna proposta sopra la soglia: la wiki e gia ben collegata.")
    sys.exit(0)

intercampo = [p for p in proposte if p["intercampo"]]
righe = [
    "# Proposte di collegamento (da rivedere a mano)",
    "",
    f"Generate da `tools/link_suggest.py` — {len(proposte)} proposte, "
    f"di cui **{len(intercampo)} INTERCAMPO** (collegano aree diverse: le piu preziose).",
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
    marchio = " **[INTERCAMPO]**" if p["intercampo"] else ""
    righe.append(f"- `{p['da']}` → `[[{p['wikilink']}]]`{marchio} _(affinita {p['affinita']})_")
    righe.append(f"  - {p['perche']}...")

testo_finale = "\n".join(righe)
if a.out:
    with open(os.path.join(ROOT, a.out), "w", encoding="utf-8", newline="\n") as f:
        f.write(testo_finale + "\n")
    print(f"{len(proposte)} proposte ({len(intercampo)} intercampo) -> {a.out}")
else:
    print(testo_finale)
