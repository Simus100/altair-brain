# Progetto: Brazilian E-Commerce (Olist)

Progetto piu completo: e-commerce brasiliano Olist, dai dati al report di business.

**Metodologia**:
- *Import & qualita*: dataset importato in [[postgresql]]; query [[sql]] preliminari per null, outlier e duplicati.
- *Modellazione* ([[progettazione-database]]): 8 tabelle (orders, order_items, customers, sellers, products, payments, reviews, geolocation) con chiavi primarie (*_id) ed esterne (order_items.order_id -> orders.order_id); schema ER in [[drawio]] + DBML.
- *Report* Looker Studio / [[power-bi]] ([[struttura-report-analisi]]) a 3 aree: domanda nel tempo (trend/stagionalita, geografia), prezzi & logistica (tempi di consegna per categoria/zona), customer experience (cancellazioni, recensioni, correlazioni).
- *Storytelling* ([[data-storytelling]]): risultati -> insight di business.

Dati su disco (fuori dal repo): vedi [[dataset]].

Collegati:
- [[progetti]]
- [[workflow-analisi-dati]]
- [[progettazione-database]]
- [[struttura-report-analisi]]
- [[framework-domande-analitiche]]
- [[postgresql]]
- [[sql]]
- [[power-bi]]
- [[drawio]]
- [[algebra-relazionale]]
- [[data-storytelling]]
- [[dataset]]
