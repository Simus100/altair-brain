# -*- coding: utf-8 -*-
"""
altair-brain — distilla raw/aion/aion-oracle.md in engine/iching.db.json.

Il DB rende AION_Oracle ESEGUIBILE: 64 esagrammi con struttura, relazioni
(opposto/rovesciato/nucleare), tag, giudizio, immagine, interpretazione e linee mobili,
piu la tabella di lookup binario->ID (sequenza di Re Wen: l'ID NON e binario+1!).

Deterministico, valida tutto (exit 1 se il parse e incompleto). Uso:
  python tools/build_iching_db.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "raw", "aion", "aion-oracle.md")
OUT = os.path.join(ROOT, "engine", "iching.db.json")

with open(SRC, encoding="utf-8") as f:
    text = f.read()

errors = []

# ---------- Sezione 3.5: trigrammi ----------
trigrammi = []
sec35 = re.search(r"## SEZIONE 3\.5.*?(?=## SEZIONE 3\.6)", text, re.S)
if not sec35:
    errors.append("Sezione 3.5 (trigrammi) non trovata")
else:
    for row in re.finditer(r"^\|\s*([☰☷☳☵☶☴☲☱])\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|\s*([01]{3})\s*\|",
                           sec35.group(0), re.M):
        trigrammi.append({
            "simbolo": row.group(1),
            "nome": row.group(2).strip(),
            "hanzi": row.group(3).strip(),
            "pinyin": row.group(4).strip(),
            "attributo": row.group(5).strip(),
            "elemento": row.group(6).strip(),
            "famiglia": row.group(8).strip(),
            "binario": row.group(9),
        })
    if len(trigrammi) != 8:
        errors.append(f"trigrammi: attesi 8, trovati {len(trigrammi)}")

# ---------- Sezione 3.6: lookup binario -> ID (Re Wen) ----------
lookup = {}
sec36 = re.search(r"## SEZIONE 3\.6.*?(?=## SEZIONE 4)", text, re.S)
if not sec36:
    errors.append("Sezione 3.6 (lookup Re Wen) non trovata")
else:
    for row in re.finditer(r"^\|\s*([01]{6})\s*\|\s*\d+\s*\|\s*(\d+)\s*\|", sec36.group(0), re.M):
        lookup[row.group(1)] = int(row.group(2))
    if len(lookup) != 64:
        errors.append(f"lookup Re Wen: attese 64 voci, trovate {len(lookup)}")
    if sorted(lookup.values()) != list(range(1, 65)):
        errors.append("lookup Re Wen: gli ID non coprono 1..64 esattamente una volta")

# ---------- Sezione 4: i 64 esagrammi ----------
HEX_HEADER = re.compile(r"^## (\d+)\.\s+(\S+)\s+(.+?)\s+\(([^)]+)\)\s+(\S+)\s*$", re.M)
headers = list(HEX_HEADER.finditer(text))
esagrammi = []

def section(block, name, next_names):
    stop = "|".join(re.escape(n) for n in next_names)
    m = re.search(rf"### {re.escape(name)}\s*\n(.*?)(?=\n### (?:{stop})|\Z)", block, re.S)
    return m.group(1).strip() if m else ""

for i, h in enumerate(headers):
    start = h.end()
    end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
    block = text[start:end]
    eid = int(h.group(1))
    e = {"id": eid, "hanzi": h.group(2), "nome": h.group(3).strip(),
         "pinyin": h.group(4).strip(), "simbolo": h.group(5)}

    m = re.search(r"\*\*Codifica Binaria:\*\*\s*([01]{6})", block)
    e["binario"] = m.group(1) if m else None
    m = re.search(r"\*\*Trigramma Superiore:\*\*\s*(\S+)\s+([^(\n]+)", block)
    e["trigramma_sup"] = {"simbolo": m.group(1), "nome": m.group(2).strip()} if m else None
    m = re.search(r"\*\*Trigramma Inferiore:\*\*\s*(\S+)\s+([^(\n]+)", block)
    e["trigramma_inf"] = {"simbolo": m.group(1), "nome": m.group(2).strip()} if m else None

    rel = {}
    for k in ("Opposto", "Rovesciato", "Nucleare"):
        m = re.search(rf"\*\*{k}:\*\*\s*(\d+)", block)
        rel[k.lower()] = int(m.group(1)) if m else None
    e["relazioni"] = rel

    e["tag"] = re.findall(r"`([^`]+)`", section(block, "Tag",
                          ["Giudizio", "Immagine", "Interpretazione Moderna", "Linee Mobili"]))
    e["giudizio"] = section(block, "Giudizio", ["Immagine", "Interpretazione Moderna", "Linee Mobili"])
    e["immagine"] = section(block, "Immagine", ["Interpretazione Moderna", "Linee Mobili"])
    e["interpretazione"] = section(block, "Interpretazione Moderna", ["Linee Mobili"])
    # taglia eventuali separatori in coda
    for k in ("giudizio", "immagine", "interpretazione"):
        e[k] = re.split(r"\n═+|\n---", e[k])[0].strip()

    linee = {}
    for lm in re.finditer(r"-\s*\*\*Linea (\d)\s*(?:\(([^)]*)\))?[:：]?\*\*:?\s*(.+)", block):
        linee[int(lm.group(1))] = {"notazione": (lm.group(2) or "").strip(),
                                   "testo": lm.group(3).strip()}
    e["linee"] = [linee.get(n, {"notazione": "", "testo": ""}) for n in range(1, 7)]
    esagrammi.append(e)

# ---------- validazione ----------
if len(esagrammi) != 64:
    errors.append(f"esagrammi: attesi 64, trovati {len(esagrammi)}")
ids = sorted(e["id"] for e in esagrammi)
if ids != list(range(1, 65)):
    errors.append("esagrammi: gli ID non coprono 1..64")
for e in esagrammi:
    tag = f"esagramma {e['id']} ({e['nome']})"
    if not e["binario"]:
        errors.append(f"{tag}: codifica binaria mancante")
    elif lookup.get(e["binario"]) != e["id"]:
        errors.append(f"{tag}: binario {e['binario']} non corrisponde nel lookup Re Wen "
                      f"(lookup dice {lookup.get(e['binario'])})")
    for k, v in e["relazioni"].items():
        if not isinstance(v, int) or not 1 <= v <= 64:
            errors.append(f"{tag}: relazione '{k}' mancante o fuori range")
    if not e["tag"]:
        errors.append(f"{tag}: tag mancanti")
    if not e["giudizio"] or not e["interpretazione"]:
        errors.append(f"{tag}: giudizio o interpretazione mancanti")
    vuote = [i + 1 for i, l in enumerate(e["linee"]) if not l["testo"]]
    if vuote:
        errors.append(f"{tag}: linee mobili mancanti {vuote}")

if errors:
    print(f"PARSE NON VALIDO — {len(errors)} errori:")
    for x in errors:
        print("  -", x)
    sys.exit(1)

db = {
    "schema_version": 1,
    "fonte": "raw/aion/aion-oracle.md",
    "nota": "ID secondo la sequenza di Re Wen: usare lookup_binario, MAI binario+1. "
            "Valori linee: 6=yin mobile, 7=yang stabile, 8=yin stabile, 9=yang mobile.",
    "lookup_binario": {k: lookup[k] for k in sorted(lookup)},
    "trigrammi": trigrammi,
    "esagrammi": sorted(esagrammi, key=lambda e: e["id"]),
}
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"engine/iching.db.json: 64 esagrammi, {len(lookup)} lookup, {len(trigrammi)} trigrammi. Validazione OK.")
