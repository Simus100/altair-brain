# -*- coding: utf-8 -*-
"""
altair-brain — i contratti di un brain, verificati contro i loro schemi.

PERCHE' ESISTE. I file che definiscono un brain — aree, manifesto, ponti,
provenienza, registro delle esperienze, front-matter delle note — erano descritti in
prosa o solo nel codice. Per riprodurre il sistema bisognava leggere i tool; un
refuso in una chiave ('reviwed' al posto di 'reviewed') spegneva in silenzio la
freschezza di una nota. Ora ogni contratto ha uno schema in schema/, e questo tool
li applica tutti, piu' i controlli che uno schema da solo non puo' fare:
  - ogni ponte collega aree che esistono;
  - ogni 'generata_da' punta a un file che c'e';
  - il nome nel manifesto e' quello del registro.

FORMATO. I contratti hanno un formato, legato alla versione del motore. Un brain
dichiara nel manifesto con quale versione e' stato verificato: se e' di un formato
precedente, qui si controlla solo cio' che quel formato prevedeva, e si indica
come aggiornarlo (tools/brain_upgrade.py). Un brain compatibile non deve fallire.

Se jsonschema non e' installato gli schemi si saltano con un avviso (la CI li
esegue sempre); i controlli incrociati girano comunque.

Uso:  python tools/validate_contracts.py          (exit 1 se c'e' una violazione)
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
try:
    from tools.brain import BRAIN, manifesto, versione
except ImportError:
    BRAIN = ROOT
from tools import frontmatter as fm  # noqa: E402

SCHEMI = os.path.join(ROOT, "schema")
# Dal formato 1.1: parole chiave in areas.json, intestazione uniforme dei contratti.
FORMATO_CONTRATTI = (1, 1, 0)


def _schema(nome):
    with open(os.path.join(SCHEMI, f"{nome}.schema.json"), encoding="utf-8") as f:
        return json.load(f)


def _validatore(nome):
    try:
        import jsonschema
    except ImportError:
        return None
    return jsonschema.Draft202012Validator(_schema(nome))


def _viola(validatore, dati, dove):
    if validatore is None:
        return []
    fuori = []
    for e in sorted(validatore.iter_errors(dati), key=lambda e: list(e.path)):
        percorso = "/".join(str(p) for p in e.path) or "(radice)"
        fuori.append(f"{dove} [{percorso}]: {e.message[:160]}")
    return fuori


def _json(rel):
    p = os.path.join(BRAIN, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def verifica(brain=None):
    """Ritorna (errori, avvisi)."""
    global BRAIN
    if brain:
        BRAIN = brain
    errori, avvisi = [], []
    man = manifesto(BRAIN)
    formato = versione(man.get("motore", "0.0.0"))
    # Durante un aggiornamento il manifesto dichiara ancora la versione di PARTENZA
    # (si aggiorna solo a pipeline verde): i file appena migrati vanno verificati col
    # formato di ARRIVO, altrimenti passerebbero senza essere confrontati col loro schema.
    if os.environ.get("ALTAIR_UPGRADE_IN_CORSO"):
        from tools.brain import versione_motore
        formato = versione(versione_motore())
    moderno = formato >= FORMATO_CONTRATTI
    if _validatore("brain") is None:
        avvisi.append("jsonschema non installato: schemi saltati (la CI li esegue)")

    # --- manifesto
    if man:
        errori += _viola(_validatore("brain"), man, "brain.json")
    else:
        errori.append("brain.json: manifesto assente (python tools/brain_upgrade.py lo crea)")

    # --- aree
    aree = _json("areas.json")
    ids = set()
    if aree is None:
        errori.append("areas.json: assente")
    else:
        ids = {a.get("id") for a in aree.get("areas", [])}
        if moderno:
            errori += _viola(_validatore("areas"), aree, "areas.json")
        else:
            avvisi.append(f"formato dei contratti {'.'.join(map(str, formato))}: aree e "
                          f"provenienza si controllano dal formato 1.1 — "
                          f"aggiorna con  python tools/brain_upgrade.py")
        for a in aree.get("areas", []):
            g = a.get("generata_da")
            if g and not os.path.exists(os.path.join(BRAIN, g)):
                errori.append(f"areas.json [{a['id']}]: generata_da punta a {g}, che non esiste")

    # --- ponti
    ponti = _json(os.path.join("engine", "bridges.json"))
    if ponti is not None:
        errori += _viola(_validatore("bridges"), ponti, "engine/bridges.json")
        for i, b in enumerate(ponti.get("bridges", [])):
            for capo in ("from", "to"):
                area = (b.get(capo) or {}).get("area")
                if area and ids and area not in ids:
                    errori.append(f"engine/bridges.json [{i}]: il ponte '{b.get('concetto')}' "
                                  f"usa l'area '{area}', che areas.json non dichiara")

    # --- provenienza
    prov = _json(os.path.join("engine", "provenance.json"))
    if prov is not None and moderno:
        errori += _viola(_validatore("provenance"), prov, "engine/provenance.json")

    # --- registro delle esperienze: riga per riga
    log = os.path.join(BRAIN, "engine", "lessons.jsonl")
    if os.path.exists(log):
        v = _validatore("lesson")
        with open(log, encoding="utf-8") as f:
            for n, riga in enumerate(f, 1):
                if not riga.strip():
                    continue
                try:
                    voce = json.loads(riga)
                except ValueError:
                    errori.append(f"engine/lessons.jsonl riga {n}: non e' JSON")
                    continue
                errori += _viola(v, voce, f"engine/lessons.jsonl riga {n}")

    # --- front-matter delle note (solo dove c'e': l'assenza la segnala freshness)
    v = _validatore("frontmatter")
    # I README documentano una CARTELLA, non sono conoscenza che invecchia: lo scheletro
    # li crea senza 'date' di proposito, altrimenti un brain appena nato segnalerebbe
    # contenuto scaduto. Per loro vale lo stesso schema, meno l'obbligo della data.
    v_readme = None
    if v is not None:
        import jsonschema
        s = _schema("frontmatter")
        s["required"] = [k for k in s["required"] if k != "date"]
        v_readme = jsonschema.Draft202012Validator(s)
    for strato in ("raw", "wiki", "reports"):
        for p in sorted(glob.glob(os.path.join(BRAIN, strato, "**", "*.md"), recursive=True)):
            rel = os.path.relpath(p, BRAIN).replace("\\", "/")
            if rel.startswith("raw/_inbox/"):
                continue          # transito: le note catturate hanno campi propri
            meta, _ = fm.leggi(p)
            if meta:
                errori += _viola(v_readme if os.path.basename(p) == "README.md" else v,
                                 meta, rel)

    # --- registro dell'officina
    reg_p = os.path.join(ROOT, "brains", "brains.json")
    if os.path.exists(reg_p):
        with open(reg_p, encoding="utf-8") as f:
            reg = json.load(f)
        errori += _viola(_validatore("brains"), reg, "brains/brains.json")
        for b in reg.get("brains", []):
            if os.path.abspath(os.path.join(ROOT, b["percorso"])) == os.path.abspath(BRAIN):
                if man and man.get("nome") != b["nome"]:
                    errori.append(f"brain.json: si chiama '{man.get('nome')}' ma il registro "
                                  f"lo chiama '{b['nome']}'")
    return errori, avvisi


def main():
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass
    errori, avvisi = verifica()
    for a in avvisi:
        print(f"[avviso] {a}")
    if errori:
        print(f"CONTRATTI NON VALIDI — {len(errori)} violazioni:")
        for e in errori[:40]:
            print("  -", e)
        if len(errori) > 40:
            print(f"  ... e altre {len(errori) - 40}")
        return 1
    print(f"Contratti validi: {os.path.relpath(BRAIN, ROOT)} (schemi in schema/)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
