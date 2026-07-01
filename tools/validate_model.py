# -*- coding: utf-8 -*-
"""
altair-brain — validatore di consistenza di engine/aion.model.json.

Garantisce che il modello tipizzato sia sempre integro prima che i consumatori
(VPS, API, altri dispositivi) lo ricevano. Nessun riferimento penzolante ammesso.

Exit code 0 = valido; 1 = errori (adatto a CI e hook).
Uso:  python tools/validate_model.py
"""
import json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, "engine", "aion.model.json")

def main() -> int:
    with open(MODEL, encoding="utf-8") as f:
        m = json.load(f)

    # contratto: schema_version + (se jsonschema e installato) validazione JSON Schema
    if not isinstance(m.get("schema_version"), int) or m["schema_version"] < 1:
        print("MODELLO NON VALIDO — manca schema_version (intero >= 1)")
        return 1
    schema_path = os.path.join(ROOT, "engine", "schema", "aion.model.schema.json")
    if os.path.exists(schema_path):
        try:
            import jsonschema
            with open(schema_path, encoding="utf-8") as f:
                jsonschema.validate(m, json.load(f))
            print("JSON Schema: conforme")
        except ImportError:
            print("[info] jsonschema non installato: validazione schema saltata (la CI la esegue)")
        except Exception as e:
            print(f"MODELLO NON VALIDO — violazione JSON Schema: {str(e)[:300]}")
            return 1

    aid = {a["id"] for a in m["agenti"]}
    cid = {c["id"] for c in m["componenti"]}
    lid = {l["id"] for l in m["livelli"]}
    mid = {x["id"] for x in m["modalita"]}
    tid = {t["id"] for t in m["insegnamenti"]}
    err = []

    for a in m["agenti"]:
        for c in a.get("usa", []):
            if c not in cid and c != "aion-manifest":
                err.append(f"{a['id']}.usa -> componente inesistente: {c}")
        for k in a.get("collabora", []):
            if k not in aid:
                err.append(f"{a['id']}.collabora -> agente inesistente: {k}")
        for t in a.get("consulta", []):
            if t not in tid:
                err.append(f"{a['id']}.consulta -> insegnamento inesistente: {t}")
        for md in a.get("modalita", []):
            if md not in mid:
                err.append(f"{a['id']}.modalita -> modalita inesistente: {md}")
        if a["livello"] not in lid:
            err.append(f"{a['id']}.livello inesistente: {a['livello']}")
        for o in a.get("orchestra", []):
            if o not in aid:
                err.append(f"{a['id']}.orchestra -> agente inesistente: {o}")

    for c in m["componenti"]:
        for u in c.get("usato_da", []):
            if u not in aid:
                err.append(f"{c['id']}.usato_da -> agente inesistente: {u}")
        for i in c.get("interagisce", []):
            if i not in cid:
                err.append(f"{c['id']}.interagisce -> componente inesistente: {i}")
        if c["livello"] not in lid:
            err.append(f"{c['id']}.livello inesistente: {c['livello']}")

    # simmetria usa <-> usato_da
    for a in m["agenti"]:
        for c in a.get("usa", []):
            comp = next((x for x in m["componenti"] if x["id"] == c), None)
            if comp and a["id"] not in comp.get("usato_da", []):
                err.append(f"asimmetria: {a['id']} usa {c}, ma {c}.usato_da non lo elenca")
    for c in m["componenti"]:
        for u in c.get("usato_da", []):
            ag = next((x for x in m["agenti"] if x["id"] == u), None)
            if ag and c["id"] not in ag.get("usa", []):
                err.append(f"asimmetria: {c['id']}.usato_da elenca {u}, ma {u}.usa non lo include")

    # ogni insegnamento consultato da almeno un agente
    for t in sorted(tid):
        if not any(t in a.get("consulta", []) for a in m["agenti"]):
            err.append(f"insegnamento orfano (nessun agente lo consulta): {t}")

    # ogni modalita ha dominanti esistenti
    for x in m["modalita"]:
        for d in x.get("dominanti", []):
            if d not in aid | cid:
                err.append(f"{x['id']}.dominanti -> entita inesistente: {d}")

    if err:
        print(f"MODELLO NON VALIDO — {len(err)} errori:")
        for e in err:
            print("  -", e)
        return 1
    print(f"Modello valido: {len(aid)} agenti, {len(cid)} componenti, {len(lid)} livelli, "
          f"{len(mid)} modalita, {len(tid)} insegnamenti. 0 errori.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
