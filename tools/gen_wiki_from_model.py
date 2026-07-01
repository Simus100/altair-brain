# -*- coding: utf-8 -*-
"""
altair-brain — genera wiki/aion/ da engine/aion.model.json (FONTE UNICA DI VERITA).

Il modello tipizzato e l'unica sorgente: questo tool deriva le pagine wiki con i
[[wikilink]] dalle relazioni del modello (livello, usa, collabora, consulta, modalita,
orchestra, dominanti, interagisce). Modificare AION = modificare il modello + rigenerare.

Deterministico, idempotente, nessuna API. Uso:
  python tools/gen_wiki_from_model.py
poi:  graphify update .  e  python tools/altair_compact_view.py
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, "engine", "aion.model.json")
OUT = os.path.join(ROOT, "wiki", "aion")

with open(MODEL, encoding="utf-8") as f:
    M = json.load(f)

os.makedirs(OUT, exist_ok=True)
written = set()

def w(stem, title, body, links):
    """Scrive una pagina: corpo + lista 'Collegati:' (niente sotto-heading -> niente nodi spurii)."""
    seen, uniq = set(), []
    for l in links:
        if l and l != stem and l not in seen:
            seen.add(l); uniq.append(l)
    txt = f"# {title}\n\n{body.strip()}\n\nCollegati:\n"
    txt += "".join(f"- [[{l}]]\n" for l in uniq)
    with open(os.path.join(OUT, stem + ".md"), "w", encoding="utf-8") as f:
        f.write(txt)
    written.add(stem + ".md")

# ---------- agenti ----------
for a in M["agenti"]:
    body = a["ruolo"]
    extra = []
    if a.get("orchestra"):
        extra.append("Orchestra gli agenti del framework.")
    if a.get("gate"):
        extra.append("Agisce come gate: vincolo sempre attivo su ogni output.")
    if a.get("attivazione"):
        soglie = "; ".join(f"{k} -> {v}" for k, v in a["attivazione"].items())
        extra.append(f"Soglie di attivazione: {soglie}.")
    if extra:
        body += "\n\n" + " ".join(extra)
    links = ([a["livello"]] + a.get("orchestra", []) + a.get("usa", [])
             + a.get("collabora", []) + a.get("modalita", []) + a.get("consulta", []))
    w(a["id"], a["label"], body, links)

# ---------- componenti ----------
for c in M["componenti"]:
    links = [c["livello"]] + c.get("usato_da", []) + c.get("interagisce", [])
    w(c["id"], c["label"], c["ruolo"], links)

# ---------- livelli ----------
level_members = {l["id"]: [] for l in M["livelli"]}
for a in M["agenti"]:
    level_members.setdefault(a["livello"], []).append(a["id"])
for c in M["componenti"]:
    level_members.setdefault(c["livello"], []).append(c["id"])
for l in M["livelli"]:
    body = l["ruolo"]
    w(l["id"], "Livello " + l["label"], body, level_members.get(l["id"], []))

# ---------- modalita ----------
for x in M["modalita"]:
    body = f"Tag: `{x['tag']}` — priorita: {x['priorita']}."
    w(x["id"], f"Modalita {x['tag']}", body,
      x.get("dominanti", []) + ["livello-orchestrazione-stile"])

# ---------- insegnamenti ----------
for t in M["insegnamenti"]:
    n = t["id"].split("-")[-1]
    w(t["id"], f"Insegnamento {n} - {t['titolo']}", t["testo"],
      ["insegnamenti"] + t.get("consultato_da", []))

w("insegnamenti", "Insegnamenti attivi di AION",
  "I 26 insegnamenti trasversali di AION: filtri euristici e principi guida applicati "
  "in ogni fase operativa, in coerenza con [[aion-ethos]] e il Manifest.",
  [t["id"] for t in M["insegnamenti"]])

# ---------- indice ----------
w("index", "AION - modello di pensiero",
  "AION e un'entita analitica meta-strutturale: quattro livelli logici, agenti "
  "orchestrati da [[aion-superia]], componenti operativi, quattro modalita canoniche e "
  "26 insegnamenti. Questa wiki e GENERATA da engine/aion.model.json "
  "(fonte unica di verita) tramite tools/gen_wiki_from_model.py: non modificarla a mano. "
  "Le sorgenti grezze sono in raw/aion.",
  [l["id"] for l in M["livelli"]] + [x["id"] for x in M["modalita"]]
  + ["aion-superia", "insegnamenti"])

# ---------- pulizia pagine orfane (non piu nel modello) ----------
removed = []
for f in os.listdir(OUT):
    if f.endswith(".md") and f not in written:
        os.remove(os.path.join(OUT, f)); removed.append(f)

print(f"wiki/aion generata dal modello: {len(written)} pagine"
      + (f" (rimosse {len(removed)} orfane: {removed})" if removed else ""))
