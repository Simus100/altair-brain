# -*- coding: utf-8 -*-
"""
altair-brain — lettura del front-matter, in un posto solo.

PERCHE ESISTE: la stessa logica era duplicata in sette strumenti (indice di ricerca,
freschezza, provenienza, metriche, riemersione, arricchimento, proposte di link) e,
essendo duplicata, era anche sbagliata allo stesso modo in tutti.

IL DIFETTO REALE che ha imposto questo modulo: una nota che inizia con
    --- FUNZIONI DI DATA_PROCESSING EXCEL ---
veniva scambiata per front-matter YAML, perche il controllo era `startswith("---")`.
Conseguenze a catena: lo strumento di arricchimento la saltava credendola gia a
posto, la freschezza non sapeva quando fosse stata rivista, l'indice le mangiava
l'inizio del contenuto.

REGOLA CORRETTA (quella di YAML/Obsidian): il front-matter esiste solo se la PRIMA
riga e esattamente `---` e piu avanti c'e una riga di chiusura esattamente `---`.
Una riga che contiene altro oltre ai trattini e testo, non un delimitatore.
"""


# Strati GENERATI da una fonte unica: il front-matter NON va scritto qui a mano,
# perche' farebbe divergere la pagina dal suo generatore. La provenienza di questi
# file e' dichiarata a livello di strato in engine/provenance.json (ancoraggi_area),
# non file per file — quindi la loro assenza di front-matter non e' una mancanza.
#
# L'ELENCO NON E' SCRITTO QUI: si legge da areas.json, dove ogni area dichiara la
# propria 'generata_da'. Prima era una costante ripetuta in tre file diversi
# (frontmatter, link_suggest, resurface) — la stessa duplicazione che aveva reso
# sbagliati allo stesso modo sette parser. Ed era anche cio' che legava il motore a
# UN brain preciso: leggendola dalla configurazione, il motore vale per qualsiasi
# insieme di aree.
def _strati_generati():
    import json
    import os
    from tools.brain import BRAIN as _B
    reg = os.path.join(_B, "areas.json")
    try:
        with open(reg, encoding="utf-8") as f:
            aree = json.load(f).get("areas", [])
    except (OSError, ValueError):
        return ()
    return tuple(f"wiki/{a['id']}/" for a in aree if a.get("generata_da"))


STRATI_GENERATI = _strati_generati()


def e_generato(percorso) -> bool:
    """Vero se il file appartiene a uno strato generato (esente da front-matter)."""
    p = str(percorso).replace("\\", "/")
    return any(g.rstrip("/") + "/" in p for g in STRATI_GENERATI)


def _righe(testo):
    return (testo or "").lstrip("﻿").splitlines()


def ha_frontmatter(testo) -> bool:
    """Vero solo per un blocco delimitato davvero: prima riga '---' e chiusura '---'."""
    righe = _righe(testo)
    if not righe or righe[0].strip() != "---":
        return False
    return any(r.strip() == "---" for r in righe[1:])


def dividi(testo):
    """(meta, corpo). Senza front-matter valido: ({}, testo intero)."""
    if not ha_frontmatter(testo):
        return {}, testo
    righe = _righe(testo)
    fine = next(i for i, r in enumerate(righe[1:], start=1) if r.strip() == "---")
    meta = {}
    for riga in righe[1:fine]:
        if ":" in riga and not riga.lstrip().startswith("#"):
            k, _, v = riga.partition(":")
            meta[k.strip()] = v.strip()
    return meta, "\n".join(righe[fine + 1:]).lstrip("\n")


def leggi(path):
    """(meta, corpo) da file. (None, '') se illeggibile."""
    try:
        with open(path, encoding="utf-8") as f:
            return dividi(f.read())
    except (OSError, UnicodeDecodeError):
        return None, ""
