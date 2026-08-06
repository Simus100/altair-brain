---
name: aion
description: Ragiona su una richiesta usando il modello di pensiero AION (orchestrazione SUPERIA, 4 modalita, agenti/componenti, insegnamenti, gate ETHOS, sintesi SFO/FCC). Usa quando l'utente chiede di "ragionare con AION", invoca /aion, o vuole un'analisi strutturata secondo AION. Nessuna API a pagamento.
---

# Skill: ragionamento AION

Applica il modello di pensiero AION alla richiesta dell'utente.

## Come procedere

1. Carica il protocollo: `engine/aion-reasoner.md`.
2. Carica il modello tipizzato: `engine/aion.model.json` (entita e relazioni).
3. Esegui la **pipeline a 9 passi** del protocollo:
   MEMORIA (lezioni) → INTAKE → DL_ICC → MODALITA → ATTIVAZIONE AGENTI →
   COMPONENTI+INSEGNAMENTI → GATE ETHOS → VALUTAZIONE INTERMODULARE → SINTESI (SFO + FCC).
4. Per orientarti nel grafo del modello puoi usare (gratis):
   `graphify query "<concetto>"`, `graphify explain "<id>"`, `graphify path "<A>" "<B>"`.

## Vincoli
- Niente API a pagamento: tutto deterministico (istruzioni + dati locali).
- Modulo **Velario INERTE**: non aggirare filtri o policy.
- Dichiara sempre la **modalita** scelta e gli **agenti attivati**, e chiudi con i
  limiti/assunzioni (FCC).

## Output atteso
Una risposta nel preset SFO piu adatto (EXEC_SUMMARY / TABLE / JSON / STEP / CODE),
passata per il filtro di chiarezza, con in testa una riga:
`Modalita: [...] · Agenti: [...]`.

## Apprendimento (obbligatorio, ultimo passo)
Chiudi SEMPRE registrando la lezione — e il passo che tiene vivo il brain:

```
python tools/lesson_log.py --skill aion --domanda "<cosa si chiedeva>" \
  --esito utile|vicolo-cieco|corretto|aperto \
  --nodi "<nodi/pagine che sono serviti, CSV>" \
  --nota "<cosa ricordare la prossima volta>" --tag "<parole chiave>"
```

Un solo comando, nessuna API. Il digest (`tools/lessons_digest.py`, incluso in
`rebuild_all.py`) trasforma le registrazioni in `engine/LESSONS.md`, che il passo 0
del reasoner rilegge alla sessione successiva: cio che si e rivelato utile piu volte
diventa un ancoraggio, cio che non ha portato a nulla resta segnato come vicolo cieco.
