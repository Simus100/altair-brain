---
name: oracle
description: Consulta AION_Oracle (I Ching eseguibile) per una domanda strategica - lancio esagrammi, linee mobili, interpretazione. Usa quando l'utente chiede "consulta l'oracolo", "/oracle", "lancia gli esagrammi", "cosa dice l'I Ching".
---

# Skill: AION_Oracle (I Ching eseguibile)

Consulenza decisionale simbolica secondo il componente AION_Oracle.

## Procedura

1. Chiedi/identifica la **domanda strategica** dell'utente (se non gia data).
2. Esegui il lancio (deterministico, nessuna API):
   `python tools/oracle_cast.py --question "<domanda>"`
   (aggiungi `--seed N` solo se l'utente vuole riproducibilita).
3. Il JSON contiene: esagramma primario (giudizio, immagine, interpretazione, tag),
   linee mobili, `linea_focus` con la `regola_applicata`, ed eventuale esagramma
   secondario (direzione del cambiamento).
4. **Interpreta secondo AION**: attiva la modalita [MYTHIC_NARRATIVE] o [HYBRID_SYNTH]
   del protocollo (`engine/aion-reasoner.md`): collega giudizio + linea focus +
   trasformazione alla domanda concreta dell'utente. Sii evocativo ma ancorato:
   niente predizioni assolute, offri una lettura strategica (leve, rischi, tempi).
5. Cita sempre: numero e nome dei due esagrammi, le linee mobili e la regola applicata.
6. A fine lettura proponi di registrare l'esito con `graphify save-result` quando
   l'utente sapra se la lettura e stata utile.

## Vincoli
- Il lancio e SOLO via tools/oracle_cast.py (lookup Re Wen corretto): mai inventare
  esagrammi o calcolarli come binario+1.
- Gate ETHOS attivo: e uno strumento riflessivo, non divinazione vincolante.
