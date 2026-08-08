---
date: 2026-08-08
area: divulgazione
source: estratto dai report pubblicati (tools/report_harvest.py)
tags: [metodo, report, fonti, verifica]
reviewed: 2026-08-08
---
# Metodo dei report verificati

Conoscenza di metodo estratta dai report gia pubblicati. NON contiene i fatti
(invecchiano e vivono nei report): contiene come sono stati costruiti e su
quali fonti ci si e appoggiati davvero — cio che serve al report successivo.

## Fonti su cui il brain ha costruito

Frequenza d'uso reale, non un elenco di buoni propositi: dice su chi si e
poggiata l'analisi quando contava.

| Fonte | Volte citata |
|---|---|
| CNN | 13 |
| Al Jazeera | 11 |
| CNBC | 6 |
| ABC News | 2 |
| UAE MoD | 2 |
| The Soufan Center | 2 |
| UN News | 2 |
| Washington Times | 2 |
| ISIS | 2 |
| NPR | 2 |
| CNN (testo integrale del MoU) | 1 |
| sintesi multi-fonte (CNN, Al Jazeera, ISIS, IAEA, Iran HRM) | 1 |
| IAEA | 1 |
| verifica multi-fonte (12 lug) | 1 |
| verifica multi-fonte (15 lug, sera) | 1 |

## Convenzioni editoriali in uso

- **Copertura della provenienza**: 92% delle affermazioni porta una fonte (34 su 37).
- **Confidenza dichiarata per voce**: alta 27, media 9.
- **Firme**: AION_Analyst (11), AION_SUPERIA (9), AION_STRATEGIC_ENGINE (7), AION_Vision (6), AION_SUPERIA + redazione (3).
- **Regola non negoziabile**: ogni affermazione con numeri o date porta la sua
  fonte; la verifica e automatica (`tools/check_provenance.py --strict`).
- **Fatti che invecchiano**: non si cancellano, si invalidano (`valid_until`,
  `superseded_by`). La cronologia resta leggibile, la verita corrente e una.

## Casi seguiti

- **AI Tools Directory 2026 — AION NEXUS Report** — 2 aggiornamenti, dal 2026-07-12 al 2026-07-12.
- **Caso Iran 2026 — AION NEXUS Report** — 35 aggiornamenti, dal 2026-01-20 al 2026-07-15.
  - lettura oracolare per *attribuzione decisionale*: 6 Il Conflitto -> 59 La Dissoluzione

## Metodo oracolare nei report

L'esagramma NON si estrae a caso: si **attribuisce** allo stato del caso
(candidati con `oracle_cast.py --cerca`), le linee mobili marcano i vettori in
mutamento e il loro testo e il consiglio operativo. La mutazione produce la
destinazione. Verificabile: `python tools/oracle_cast.py --attribuisci <id> --mobili <n>`.

Collegati:
- [[README]]

_Generato da `tools/report_harvest.py` il 2026-08-08. Rilanciarlo aggiorna i numeri;
il testo di metodo si puo integrare a mano: e una nota grezza, non un file generato._
