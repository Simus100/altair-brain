# core — scheletro di second brain

Il motore, senza la conoscenza di nessuno. Ci metti la tua.

## Cosa c'e dentro

- **Grafo** della conoscenza con sottografi per area e tre viste (estesa, compatta,
  atlante 3D esplorabile che si apre offline).
- **Provenienza**: ogni pagina curata sa da quali fonti grezze deriva, e l'arco
  esiste nel grafo, non solo nella documentazione.
- **Freschezza e bi-temporalita**: SLA per area, fatti che scadono senza essere
  cancellati.
- **Ricerca** BM25 in Python puro, senza dipendenze, con misura di confidenza che
  dichiara cosa sta misurando.
- **Anello di apprendimento**: le lezioni entrano nel prior del ragionamento solo se
  portano un appiglio esterno verificabile, e il prior ha un tetto di dimensione.
- **API** con token, rate limit e validazione dell'input.
- **Guardie**: la suite di test che impedisce alle regole di degradare in silenzio.

## Partenza

```bash
python onboarding.py
```

Chiede le tue macroaree e se attivare il plugin AION. Poi:

```bash
python tools/rebuild_all.py
```

## Training e plugin — due cose diverse

- **`training/`** — un imprinting iniziale: un modo di ragionare gia formato che il
  brain puo adottare. Se ne sceglie **al massimo uno**, o nessuno. Disponibile:
  **aion**, modello di pensiero a livelli con oracolo I Ching eseguibile.
- **`plugins/`** — capacita aggiuntive che non toccano il pensiero. Se ne attivano
  quante se ne vuole.

Senza training il motore funziona lo stesso: il modo di ragionare lo costruisci
strada facendo, e l'anello delle lezioni lo registra man mano.
