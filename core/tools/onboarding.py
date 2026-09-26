# -*- coding: utf-8 -*-
"""
altair-brain — prima configurazione di un brain: le macroaree e, se vuoi, un training.

PERCHE' E' UN TOOL DEL MOTORE. Prima viveva come onboarding.py dentro ogni brain, e
configurava la cartella in cui si trovava: funzionava solo finche' ogni brain portava
con se' una copia del motore. Ora il motore esiste una volta sola, e l'onboarding
configura il brain ATTIVO (tools/brain.py), come ogni altro tool. Nello scheletro
ceduto, onboarding.py nella radice resta come porta d'ingresso e chiama questo.

TRAINING. Un training e' un imprinting: fonti, modello e protocollo che decidono
*come* il brain ragiona. Se ne adotta al massimo uno, si puo' non adottarne nessuno,
e si puo' adottare piu' tardi. Adottarlo copia nel brain le fonti (raw/<training>/) e
il modello (engine/); gli strumenti del training entrano nel motore solo se mancano,
cioe' nello scheletro ceduto — nell'officina ci sono gia'.

Uso:
  python tools/onboarding.py                                   interattivo, brain attivo
  python tools/onboarding.py --aree "ricette,tecniche" --training nessuno
  python tools/onboarding.py --training aion                   adotta un training dopo
"""
import argparse
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
try:
    from tools.brain import BRAIN
except ImportError:
    BRAIN = ROOT

# Le aree di un training, come vanno dichiarate in areas.json quando lo si adotta.
AREE_TRAINING = {
    "aion": {"id": "aion", "label": "AION",
             "description": "Modello di pensiero AION.",
             "status": "active", "sla_giorni": None, "coesa": True,
             "generata_da": "engine/aion.model.json",
             "keywords": ["aion", "oracolo", "esagramma", "modalita", "ragionamento"]},
}


def chiedi(testo, default=""):
    try:
        r = input(f"{testo}{f' [{default}]' if default else ''}: ").strip()
    except EOFError:
        r = ""
    return r or default


def _leggi(brain, rel, vuoto):
    p = os.path.join(brain, rel)
    if not os.path.exists(p):
        return vuoto
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _scrivi(brain, rel, dati):
    p = os.path.join(brain, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)
        f.write("\n")


def pacchetto_training(nome):
    """Dove sta il pacchetto di un training: nello scheletro ceduto in training/,
    nell'officina nel prodotto generato core/training/."""
    for base in (os.path.join(ROOT, "training"), os.path.join(ROOT, "core", "training")):
        p = os.path.join(base, nome)
        if os.path.isdir(p):
            return p
    return None


def training_disponibili():
    visti = []
    for base in (os.path.join(ROOT, "training"), os.path.join(ROOT, "core", "training")):
        if os.path.isdir(base):
            visti += [d for d in sorted(os.listdir(base))
                      if os.path.isdir(os.path.join(base, d)) and d not in visti]
    return visti


def imposta_aree(brain, aree):
    """Scrive le aree e crea le loro cartelle. Le aree di un training gia' adottato
    restano: rifare l'onboarding non deve cancellare un imprinting."""
    reg = _leggi(brain, "areas.json", {"schema_version": 1, "areas": []})
    tenute = [a for a in reg.get("areas", []) if a.get("id") in AREE_TRAINING
              and os.path.isdir(os.path.join(brain, "raw", a["id"]))]
    reg["areas"] = tenute + [a for a in aree if a["id"] not in {t["id"] for t in tenute}]
    _scrivi(brain, "areas.json", reg)
    from tools.oplog import registra
    registra("onboarding", "aree: " + ", ".join(a["id"] for a in reg["areas"]), brain)
    for a in aree:
        for strato in ("raw", "wiki"):
            os.makedirs(os.path.join(brain, strato, a["id"]), exist_ok=True)
    return reg["areas"]


def adotta_training(brain, nome):
    """Copia l'imprinting nel brain. Ritorna False se il pacchetto non esiste."""
    tr = pacchetto_training(nome)
    if not tr:
        return False
    src = os.path.join(tr, "engine")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(brain, "engine"), dirs_exist_ok=True)
    src = os.path.join(tr, "raw", nome)
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(brain, "raw", nome), dirs_exist_ok=True)
    # strumenti e skill: nel MOTORE, e solo se mancano (scheletro ceduto)
    for sotto, dest in (("tools", os.path.join(ROOT, "tools")),
                        ("skills", os.path.join(ROOT, ".claude", "skills"))):
        src = os.path.join(tr, sotto)
        if not os.path.isdir(src):
            continue
        for voce in sorted(os.listdir(src)):
            a, b = os.path.join(src, voce), os.path.join(dest, voce)
            if os.path.exists(b):
                continue
            os.makedirs(dest, exist_ok=True)
            (shutil.copytree if os.path.isdir(a) else shutil.copy2)(a, b)
    # la catena fonte -> conoscenza del training si unisce a quella del brain
    parte = _leggi(tr, "provenance.json", {})
    if parte:
        prov = _leggi(brain, "engine/provenance.json",
                      {"schema_version": 1, "ancoraggi_area": [], "mappe_dirette": []})
        for chiave, id_ in (("ancoraggi_area", "indice"), ("mappe_dirette", "wiki")):
            noti = {x.get(id_) for x in prov.setdefault(chiave, [])}
            prov[chiave] += [x for x in parte.get(chiave, []) if x.get(id_) not in noti]
        _scrivi(brain, "engine/provenance.json", prov)
    reg = _leggi(brain, "areas.json", {"schema_version": 1, "areas": []})
    if nome in AREE_TRAINING and nome not in {a["id"] for a in reg["areas"]}:
        reg["areas"].append(dict(AREE_TRAINING[nome]))
        _scrivi(brain, "areas.json", reg)
    man = _leggi(brain, "brain.json", {"schema_version": 1})
    man["training"] = nome
    _scrivi(brain, "brain.json", man)
    from tools.oplog import registra
    registra("training", f"adottato il training {nome}", brain)
    return True


def aree_da_testo(testo):
    """'ricette,tecniche' oppure 'ricette:Ricette:descrizione,...'"""
    aree = []
    for voce in [v.strip() for v in (testo or "").split(",") if v.strip()]:
        parti = voce.split(":")
        i = parti[0].strip()
        aree.append({"id": i,
                     "label": (parti[1].strip() if len(parti) > 1 else i.replace("-", " ").title()),
                     "description": parti[2].strip() if len(parti) > 2 else "",
                     "status": "active", "sla_giorni": 180, "keywords": [i]})
    return aree


def interattivo(brain):
    print("== configurazione iniziale del brain ==\n")
    aree = []
    print("Macroaree (invio vuoto per finire). Un id kebab-case, es. 'finanza'.")
    while True:
        i = chiedi(f"  area #{len(aree) + 1}")
        if not i:
            break
        aree.append({"id": i, "label": chiedi("    etichetta", i.title()),
                     "description": chiedi("    descrizione", ""),
                     "status": "active", "sla_giorni": 180, "keywords": [i]})
    if aree:
        imposta_aree(brain, aree)
    else:
        print("Nessuna area tua per ora: resta quella di esempio, le aggiungi quando vuoi.")

    # La domanda sul training si fa SEMPRE. Prima usciva qui se non si dichiaravano
    # aree: chi voleva partire solo con AION non vedeva mai la scelta.
    if "aion" in training_disponibili():
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
            adotta_training(brain, "aion")
            if not aree:
                # l'area d'esempio era un segnaposto: ora il brain ha un contenuto vero
                reg = _leggi(brain, "areas.json", {"areas": []})
                reg["areas"] = [a for a in reg["areas"] if a.get("id") != "esempio"]
                _scrivi(brain, "areas.json", reg)
            print("  training AION adottato: il brain parte con un modo di ragionare.")
        else:
            print("  nessun training: il brain parte vuoto e impara dall'uso.")
            print("  (si adotta quando vuoi:  python tools/onboarding.py --training aion)")

    n = len(_leggi(brain, "areas.json", {"areas": []})["areas"])
    print(f"\nFatto: {n} aree. Ora:  python tools/rebuild_all.py")


def main(argv=None):
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass
    ap = argparse.ArgumentParser(description="Prima configurazione di un brain")
    ap.add_argument("--brain", default=None, help="cartella del brain (default: il brain attivo)")
    ap.add_argument("--aree", default=None, help="aree separate da virgola, senza domande")
    ap.add_argument("--training", default=None,
                    help="training da adottare senza domande (es. aion), oppure 'nessuno'")
    a = ap.parse_args(argv)
    brain = os.path.abspath(a.brain) if a.brain else BRAIN

    if a.aree is None and a.training is None:
        interattivo(brain)
        return
    if a.aree:
        imposta_aree(brain, aree_da_testo(a.aree))
    if a.training and a.training != "nessuno":
        if not adotta_training(brain, a.training):
            sys.exit(f"training sconosciuto: {a.training} (disponibili: "
                     f"{', '.join(training_disponibili()) or 'nessuno'})")
        print(f"training {a.training} adottato")
    n = len(_leggi(brain, "areas.json", {"areas": []})["areas"])
    print(f"brain configurato: {n} aree in {os.path.relpath(brain, ROOT)}")


if __name__ == "__main__":
    main()
