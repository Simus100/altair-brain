# -*- coding: utf-8 -*-
"""
altair-brain — compatibilita' fra un brain e il motore che lo fa girare.

IL PROBLEMA. Ogni brain portava una copia del motore, e nessuno la aggiornava: le
correzioni restavano nell'officina, e un brain esportato girava col motore del
giorno in cui era nato — senza che nulla lo dicesse. Ora il motore esiste una volta
sola (VERSION nella radice) e ogni brain dichiara nel manifesto brain.json con quale
versione e' stato verificato l'ultima volta. La distanza fra le due si misura.

LA REGOLA (versionamento semantico del contratto fra motore e brain):
  stessa versione                     compatibile
  motore piu' nuovo, stessa MAJOR     compatibile — il brain e' aggiornabile
  MAJOR diversa                       incompatibile: e' cambiato il formato dei file
  brain piu' nuovo del motore         incompatibile: aggiorna il motore, non il brain

AGGIORNARE non e' cambiare un numero: si ricostruisce il brain con il motore
corrente, e il manifesto si aggiorna SOLO se l'intera pipeline passa. Cosi' il
numero nel manifesto significa "verificato con", non "copiato da".

Uso:
  python tools/brain_upgrade.py --verifica     exit 1 se incompatibile (lo usa rebuild_all)
  python tools/brain_upgrade.py                ricostruisce e, se verde, aggiorna il manifesto
  ALTAIR_BRAIN=brains/cucina python tools/brain_upgrade.py
"""
import argparse, datetime, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.brain import BRAIN, manifesto, versione, versione_motore  # noqa: E402

# --- MIGRAZIONI ---------------------------------------------------------------
# Quando il formato dei file di un brain cambia, il motore porta con se' il modo di
# convertirli. Una migrazione si applica a un brain verificato con una versione
# PRECEDENTE alla sua, in ordine; se la pipeline poi fallisce, i file tornano com'erano.

def _leggi(brain, rel):
    p = os.path.join(brain, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _scrivi(brain, rel, dati):
    with open(os.path.join(brain, rel), "w", encoding="utf-8", newline="\n") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _intestazione(dati, descrizione=None):
    """Ogni contratto apre con schema_version e descrizione, in quest'ordine."""
    testa = {"schema_version": dati.pop("schema_version", None) or dati.pop("version", None) or 1}
    d = dati.pop("descrizione", None) or dati.pop("description", None) or descrizione
    if d:
        testa["descrizione"] = d
    conv = dati.pop("convenzione", None) or dati.pop("convention", None)
    if conv:
        testa["convenzione"] = conv
    testa.update(dati)
    return testa


# Colori delle aree che il motore conosceva per nome: erano scritti nel codice
# dell'atlante, cioe' il motore sapeva come si chiamano le aree di UN brain. La
# migrazione li sposta nell'areas.json del brain che li usa; il motore da ora
# assegna un colore da una tavolozza a chi non ne dichiara uno.
_COLORI_STORICI = {
    "aion": "#a78bfa", "creativita": "#f472b6", "data-science": "#22d3ee",
    "divulgazione": "#34d399", "finanza": "#fbbf24", "web-design": "#fb923c",
}


def migra_1_1(brain):
    """Formato 1.1: un solo registro delle aree, intestazione uniforme dei contratti."""
    cambi = []
    aree = _leggi(brain, "areas.json")
    router = _leggi(brain, os.path.join("engine", "router.json")) or {}
    instradamento = router.get("aree", {})
    if aree is not None:
        aree = _intestazione(aree)
        aree.setdefault("convenzione", {})
        aree["convenzione"].setdefault(
            "keywords", "parole che instradano una domanda a quest'area (sottostringa)")
        aree["convenzione"].setdefault("colore", "colore dello spicchio nell'atlante 3D")
        for a in aree.get("areas", []):
            r = instradamento.get(a["id"], {})
            if "keywords" not in a:
                a["keywords"] = r.get("keywords") or [a["id"]]
            if "budget" not in a and r.get("budget_default"):
                a["budget"] = r["budget_default"]
            if "colore" not in a and a["id"] in _COLORI_STORICI:
                a["colore"] = _COLORI_STORICI[a["id"]]
        _scrivi(brain, "areas.json", aree)
        cambi.append("areas.json: parole chiave dal router, intestazione uniforme")
    if os.path.exists(os.path.join(brain, "engine", "router.json")):
        os.remove(os.path.join(brain, "engine", "router.json"))
        cambi.append("engine/router.json: tolto (era un secondo registro delle aree)")
    prov = _leggi(brain, os.path.join("engine", "provenance.json"))
    if prov is not None:
        _scrivi(brain, os.path.join("engine", "provenance.json"), _intestazione(prov))
        cambi.append("engine/provenance.json: intestazione uniforme")
    return cambi


# (versione che la introduce, cosa cambia, funzione)
MIGRAZIONI = [
    ("1.1.0", "un solo registro delle aree; contratti con intestazione uniforme", migra_1_1),
]
TOCCATI = ("areas.json", os.path.join("engine", "router.json"),
           os.path.join("engine", "provenance.json"))


def migrazioni_da_applicare(brain):
    vb = versione(manifesto(brain).get("motore", "0.0.0"))
    vm = versione(versione_motore())
    return [m for m in MIGRAZIONI if vb < versione(m[0]) <= vm]


# Variabile con cui brain_upgrade chiede a rebuild_all di non verificare la versione
# che sta appunto aggiornando: senza, un brain indietro non si aggiornerebbe mai.
SALTA = "ALTAIR_UPGRADE_IN_CORSO"


def stato(brain=BRAIN):
    """(codice, messaggio). codice: 'ok' | 'aggiornabile' | 'incompatibile' | 'senza'."""
    man = manifesto(brain)
    m = versione_motore()
    if not man.get("motore"):
        return "senza", (f"il brain non ha un manifesto con la versione del motore: "
                         f"python tools/brain_upgrade.py lo crea (motore {m})")
    b = man["motore"]
    vb, vm = versione(b), versione(m)
    if vb == vm:
        return "ok", f"brain verificato col motore {m}"
    if vb > vm:
        return "incompatibile", (f"il brain e' stato verificato con un motore piu' nuovo "
                                 f"({b}) di questo ({m}): aggiorna il motore")
    if vb[0] != vm[0]:
        return "incompatibile", (f"il brain e' del motore {b}, questo e' {m}: e' cambiata "
                                 f"la versione principale, cioe' il formato dei file")
    return "aggiornabile", (f"il brain e' del motore {b}, questo e' {m}: compatibile. "
                            f"Per aggiornarlo:  python tools/brain_upgrade.py")


def aggiorna(brain=BRAIN):
    codice, msg = stato(brain)
    if codice == "ok":
        print(msg)
        return 0
    if codice == "incompatibile" and versione(manifesto(brain).get("motore", "0")) > \
            versione(versione_motore()):
        sys.exit(msg)
    # Copia di sicurezza dei file che le migrazioni possono toccare: se la pipeline
    # fallisce, il brain torna esattamente com'era, con la versione che dichiarava.
    copia = {}
    for rel in TOCCATI:
        p = os.path.join(brain, rel)
        if os.path.exists(p):
            with open(p, "rb") as fh:
                copia[rel] = fh.read()
    for da, cosa, funzione in migrazioni_da_applicare(brain):
        print(f"migrazione {da}: {cosa}", flush=True)
        for c in funzione(brain):
            print(f"  - {c}", flush=True)

    amb = dict(os.environ, ALTAIR_BRAIN=brain, PYTHONIOENCODING="utf-8")
    amb[SALTA] = "1"
    print(f"ricostruisco {os.path.relpath(brain, ROOT)} col motore {versione_motore()}...", flush=True)
    esito = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "rebuild_all.py")],
                           cwd=ROOT, env=amb)
    if esito.returncode != 0:
        for rel in TOCCATI:
            p = os.path.join(brain, rel)
            if rel in copia:
                with open(p, "wb") as fh:
                    fh.write(copia[rel])
            elif os.path.exists(p):
                os.remove(p)
        sys.exit("pipeline fallita: migrazioni annullate e manifesto NON aggiornato. Il "
                 "brain resta com'era, dichiarato con la versione che era stata verificata.")
    man = manifesto(brain) or {"schema_version": 1,
                               "nome": os.path.basename(os.path.abspath(brain))}
    man["motore"] = versione_motore()
    man["verificato"] = datetime.date.today().isoformat()
    with open(os.path.join(brain, "brain.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"brain aggiornato: verificato col motore {man['motore']}")
    return 0


def main():
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass
    ap = argparse.ArgumentParser(description="Compatibilita' fra brain e motore")
    ap.add_argument("--verifica", action="store_true",
                    help="solo controllo: exit 1 se il brain non e' compatibile")
    a = ap.parse_args()
    if a.verifica:
        if os.environ.get(SALTA):
            print("verifica di versione sospesa: aggiornamento in corso")
            return 0
        codice, msg = stato()
        print(msg)
        return 1 if codice in ("incompatibile", "senza") else 0
    return aggiorna()


if __name__ == "__main__":
    sys.exit(main())
