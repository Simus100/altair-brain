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
    amb = dict(os.environ, ALTAIR_BRAIN=brain, PYTHONIOENCODING="utf-8")
    amb[SALTA] = "1"
    print(f"ricostruisco {os.path.relpath(brain, ROOT)} col motore {versione_motore()}...")
    esito = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "rebuild_all.py")],
                           cwd=ROOT, env=amb)
    if esito.returncode != 0:
        sys.exit("pipeline fallita: il manifesto NON viene aggiornato. Il brain resta "
                 "dichiarato con la versione precedente, che e' quella verificata.")
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
