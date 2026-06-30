---
name: aion
description: Ragiona su una richiesta usando il modello di pensiero AION (orchestrazione SUPERIA, 4 modalita, agenti/componenti, insegnamenti, gate ETHOS, sintesi SFO/FCC). Usa quando l'utente chiede di "ragionare con AION", invoca /aion, o vuole un'analisi strutturata secondo AION. Nessuna API a pagamento.
---

# Skill: ragionamento AION

Applica il modello di pensiero AION alla richiesta dell'utente.

## Come procedere

1. Carica il protocollo: `engine/aion-reasoner.md`.
2. Carica il modello tipizzato: `engine/aion.model.json` (entita e relazioni).
3. Esegui la **pipeline a 8 passi** del protocollo:
   INTAKE → DL_ICC → MODALITA → ATTIVAZIONE AGENTI → COMPONENTI+INSEGNAMENTI →
   GATE ETHOS → VALUTAZIONE INTERMODULARE → SINTESI (SFO + FCC).
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

## Apprendimento
Se la risposta e significativa, proponi di registrarla con
`graphify save-result` (outcome useful|dead_end|corrected) per il miglioramento nel tempo.
