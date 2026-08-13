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

Il caso 3 e' il default ed e' quello che rende il cambiamento sicuro: un'istanza
autosufficiente — core/ dopo l'onboarding, o brains/<nome>/ — continua a comportarsi
esattamente come prima, perche' li' contenuto e motore coincidono davvero.

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
