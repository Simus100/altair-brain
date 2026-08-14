# -*- coding: utf-8 -*-
"""
altair-brain — una riga sola, per un guasto che si e' ripresentato quattro volte.

IL PROBLEMA. La console di Windows parla cp1252. Qualsiasi tool che stampi contenuto
del brain — un estratto di ricerca, un rilievo stilistico, il titolo di una nota — puo'
incontrare una freccia, un trattino lungo, una virgoletta caporale o una lettera
accentata fuori tabella, e MORIRE con UnicodeEncodeError prima di dire quello che
aveva trovato.

E' il modo peggiore di fallire: non un risultato sbagliato, ma nessun risultato — e
l'utente vede una traccia di stack invece della risposta. Un tool che si schianta sul
contenuto che deve mostrare non serve a niente.

Uso:  from tools.console import usa_utf8;  usa_utf8()
"""
import sys


def usa_utf8():
    """Forza stdout/stderr in UTF-8, sostituendo cio' che non e' rappresentabile.

    'replace' invece di 'strict': meglio un carattere sbagliato in un estratto che
    un tool che non stampa nulla. Silenzioso se i flussi sono rediretti o gia'
    adeguati — non deve mai essere lui la causa di un errore.
    """
    for flusso in (sys.stdout, sys.stderr):
        try:
            flusso.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
