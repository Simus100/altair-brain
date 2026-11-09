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

MODEL = os.path.join(BRAIN, "engine", "aion.model.json")

def main() -> int:
    with open(MODEL, encoding="utf-8") as f:
        m = json.load(f)

    # contratto: schema_version + (se jsonschema e installato) validazione JSON Schema
    if not isinstance(m.get("schema_version"), int) or m["schema_version"] < 1:
        print("MODELLO NON VALIDO — manca schema_version (intero >= 1)")
        return 1
    schema_path = os.path.join(BRAIN, "engine", "schema", "aion.model.schema.json")
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

    # --- AGGREGAZIONE: che il modello stia insieme, non solo che i nomi esistano ---
    # Verificato a mano il 2026-09-26 su richiesta dell'autore ("gli agenti sono ben
    # aggregati? ETHOS e' coerente?"): tutto reggeva. Diventa regola, cosi' la
    # risposta resta vera anche dopo la prossima modifica al modello.
    agenti = {a["id"]: a for a in m["agenti"]}
    insegnamenti = {t["id"]: t for t in m["insegnamenti"]}

    # simmetria consulta <-> consultato_da (come usa <-> usato_da)
    for a in m["agenti"]:
        for t in a.get("consulta", []):
            if t in insegnamenti and a["id"] not in insegnamenti[t].get("consultato_da", []):
                err.append(f"asimmetria: {a['id']} consulta {t}, ma {t}.consultato_da non lo elenca")
    for t in m["insegnamenti"]:
        for a in t.get("consultato_da", []):
            if a not in agenti:
                err.append(f"{t['id']}.consultato_da -> agente inesistente: {a}")
            elif t["id"] not in agenti[a].get("consulta", []):
                err.append(f"asimmetria: {t['id']}.consultato_da elenca {a}, ma {a}.consulta no")

    # nessun componente inutilizzato: uno strumento che nessun agente usa e' morto
    usati = {c for a in m["agenti"] for c in a.get("usa", [])}
    for c in sorted(cid - usati):
        err.append(f"componente orfano (nessun agente lo usa): {c}")

    # ogni agente raggiungibile dall'orchestratore (orchestra + collabora)
    orchestratori = [a["id"] for a in m["agenti"] if a.get("orchestra")]
    if len(orchestratori) != 1:
        err.append(f"attesi un solo orchestratore, trovati: {orchestratori}")
    else:
        visti, coda = {orchestratori[0]}, [orchestratori[0]]
        while coda:
            x = coda.pop()
            for y in agenti[x].get("orchestra", []) + agenti[x].get("collabora", []):
                if y in agenti and y not in visti:
                    visti.add(y)
                    coda.append(y)
        for a in sorted(aid - visti):
            err.append(f"agente irraggiungibile dall'orchestratore {orchestratori[0]}: {a}")

    # ogni modalita attiva almeno un AGENTE, non solo componenti
    for x in m["modalita"]:
        if not set(x.get("dominanti", [])) & aid:
            err.append(f"{x['id']}: nessun agente dominante — la modalita' non ha chi la guida")

    # ETHOS: un solo cancello, al livello dell'identita', e il protocollo lo applica sempre
    cancelli = [a for a in m["agenti"] if str(a.get("gate")).lower() == "true"]
    if len(cancelli) != 1:
        err.append(f"atteso un solo agente-cancello (gate), trovati: {[a['id'] for a in cancelli]}")
    elif not cancelli[0]["livello"].startswith("livello-identita"):
        err.append(f"il cancello {cancelli[0]['id']} non sta al livello dell'identita'/etica")
    reasoner = os.path.join(BRAIN, "engine", "aion-reasoner.md")
    if cancelli and os.path.exists(reasoner):
        with open(reasoner, encoding="utf-8") as f:
            protocollo = f.read().lower()
        if "gate" not in protocollo or "sempre attivo" not in protocollo:
            err.append("il protocollo del reasoner non applica il cancello come 'sempre attivo'")

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
