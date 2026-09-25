# -*- coding: utf-8 -*-
"""
altair-brain — dove vive il CONTENUTO, che non e' detto sia dove vivono i tool.

IL PROBLEMA CHE RISOLVE. Finora ogni tool costruiva i propri percorsi da ROOT, cioe'
dalla cartella che contiene tools/. Funziona finche' motore e conoscenza stanno nello
stesso posto — ma e' proprio quella coincidenza che impediva a un motore di servire
PIU' brain, e che teneva il brain di una persona mescolato all'infrastruttura.

Separando i due, un repo puo' essere un'OFFICINA (motore + prodotto + istanze) invece
che un brain solo.

COME SI RISOLVE, in ordine:
  1. la variabile d'ambiente ALTAIR_BRAIN, se impostata (scelta esplicita, vince su tutto);
  2. il brain 'attivo' dichiarato in brains/brains.json;
  3. la cartella del repo stesso.

Il caso 3 e' quello di un'istanza autosufficiente — lo scheletro core/, o un brain
esportato con tools/brain_export.py — dove contenuto e motore stanno davvero nella
stessa cartella. I brain dell'officina (brains/<nome>/) invece sono solo conoscenza:
li fa girare il motore della radice.

Uso:  from tools.brain import BRAIN;  os.path.join(BRAIN, "wiki", ...)
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def brain_root(root: str = ROOT) -> str:
    """La cartella che contiene raw/, wiki/, engine/, areas.json di QUESTO brain."""
    esplicito = os.environ.get("ALTAIR_BRAIN")
    if esplicito:
        p = esplicito if os.path.isabs(esplicito) else os.path.join(root, esplicito)
        if os.path.isdir(p):
            return os.path.abspath(p)

    registro = os.path.join(root, "brains", "brains.json")
    if os.path.exists(registro):
        try:
            with open(registro, encoding="utf-8") as f:
                reg = json.load(f)
            attivo = reg.get("attivo")
            if attivo:
                for b in reg.get("brains", []):
                    if b.get("nome") == attivo:
                        p = os.path.join(root, b["percorso"])
                        if os.path.isdir(p):
                            return os.path.abspath(p)
        except (OSError, ValueError, KeyError):
            pass          # registro illeggibile: si ricade sul repo, non si esplode

    return root


BRAIN = brain_root()


def dentro(*parti) -> str:
    """Percorso dentro il brain attivo. Comodita' per non ripetere il join."""
    return os.path.join(BRAIN, *parti)


def relativo() -> str:
    """Il brain attivo come percorso relativo alla radice del repo ('.' se coincide)."""
    r = os.path.relpath(BRAIN, ROOT).replace("\\", "/")
    return r


# --- Versione del motore e manifesto del brain ------------------------------
# Un brain non porta piu' una copia del motore: dichiara con QUALE versione e'
# stato verificato. Prima ogni brain aveva la sua copia di tools/, tests/, server/,
# e nessuno la aggiornava: in brains/aion 17 tool su 31 erano gia' diversi da core/,
# e nulla diceva da quale versione fosse nato. Il motore ora esiste una volta sola;
# il manifesto rende misurabile la distanza fra un brain e il motore che lo fa girare.
def versione_motore(root: str = ROOT) -> str:
    try:
        with open(os.path.join(root, "VERSION"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "0.0.0"


def manifesto(percorso: str = None) -> dict:
    """Il file brain.json di un brain: nome, versione del motore, training."""
    p = os.path.join(percorso or BRAIN, "brain.json")
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def versione(testo: str) -> tuple:
    """'1.4.2' -> (1, 4, 2). Una versione illeggibile vale (0, 0, 0)."""
    try:
        return tuple(int(x) for x in str(testo).strip().split(".")[:3])
    except ValueError:
        return (0, 0, 0)


if __name__ == "__main__":
    try:
        import sys
        sys.path.insert(0, ROOT)
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool
    # Le skill e i documenti per agenti scrivono engine/, raw/, wiki/ relativi al
    # brain attivo, e rimandano qui per sapere quale sia. Senza questa riga un agente
    # che apre il repo vede 'engine/aion.model.json' e cerca un file che non c'e'.
    print(relativo())
