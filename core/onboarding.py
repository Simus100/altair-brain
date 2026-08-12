# -*- coding: utf-8 -*-
"""Prima configurazione: le tue macroaree e i plugin da attivare."""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
try:
    sys.path.insert(0, ROOT)
    from tools.console import usa_utf8
    usa_utf8()
except ImportError:
    pass


def chiedi(testo, default=""):
    try:
        r = input(f"{testo}{f' [{default}]' if default else ''}: ").strip()
    except EOFError:
        r = ""
    return r or default


def main():
    print("== configurazione iniziale del brain ==\n")

    aree = []
    print("Macroaree (invio vuoto per finire). Un id kebab-case, es. 'finanza'.")
    while True:
        i = chiedi(f"  area #{len(aree) + 1}")
        if not i:
            break
        aree.append({"id": i, "label": chiedi("    etichetta", i.title()),
                     "description": chiedi("    descrizione", ""),
                     "status": "active", "sla_giorni": 180})
    if not aree:
        print("Nessuna area: resta quella di esempio.")
        return

    reg = json.load(open(os.path.join(ROOT, "areas.json"), encoding="utf-8"))
    reg["areas"] = aree
    json.dump(reg, open(os.path.join(ROOT, "areas.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    router = json.load(open(os.path.join(ROOT, "engine/router.json"), encoding="utf-8"))
    router["aree"] = {a["id"]: {"descrizione": a["description"],
                                "keywords": [a["id"]]} for a in aree}
    json.dump(router, open(os.path.join(ROOT, "engine/router.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    for a in aree:
        os.makedirs(os.path.join(ROOT, "raw", a["id"]), exist_ok=True)
        os.makedirs(os.path.join(ROOT, "wiki", a["id"]), exist_ok=True)

    tr = os.path.join(ROOT, "training", "aion")
    if os.path.isdir(tr):
        print("\n-- TRAINING INIZIALE (opzionale) --")
        print("Un training e un imprinting: il brain adotta un modo di ragionare gia")
        print("formato, invece di partire senza. Non e uno strumento in piu.")
        print("")
        print("Disponibile: AION — modello di pensiero a livelli, quattro modalita di")
        print("ragionamento, un gate etico sempre attivo, e un oracolo I Ching")
        print("eseguibile per le decisioni. Aggiunge la macroarea 'aion'.")
        print("")
        print("Puoi non sceglierne nessuno: il motore funziona lo stesso e il modo di")
        print("ragionare lo costruisci strada facendo. Si adotta anche piu tardi.")
        if chiedi("Adottare il training AION? (s/n)", "n").lower().startswith("s"):
            for sotto, dest in (("engine", "engine"), ("tools", "tools"),
                                ("skills", ".claude/skills")):
                src = os.path.join(tr, sotto)
                if os.path.isdir(src):
                    shutil.copytree(src, os.path.join(ROOT, dest), dirs_exist_ok=True)
            src_raw = os.path.join(tr, "raw", "aion")
            if os.path.isdir(src_raw):
                shutil.copytree(src_raw, os.path.join(ROOT, "raw", "aion"),
                                dirs_exist_ok=True)
            reg["areas"].append({"id": "aion", "label": "AION",
                                 "description": "Modello di pensiero AION.",
                                 "status": "active", "sla_giorni": None,
                                 "coesa": True,
                                 "generata_da": "engine/aion.model.json"})
            router["aree"]["aion"] = {"descrizione": "Modello di pensiero AION.",
                                      "keywords": ["aion", "oracolo", "esagramma",
                                                   "modalita", "ragionamento"]}
            for dati, dove in ((reg, "areas.json"), (router, "engine/router.json")):
                json.dump(dati, open(os.path.join(ROOT, dove), "w", encoding="utf-8"),
                          ensure_ascii=False, indent=2)
            print("  training AION adottato: il brain parte con un modo di ragionare.")
        else:
            print("  nessun training: il brain parte vuoto e impara dall'uso.")
            print("  (resta in training/, si adotta quando vuoi)")

    print(f"\nFatto: {len(reg['areas'])} aree. Ora:  python tools/rebuild_all.py")


if __name__ == "__main__":
    main()
