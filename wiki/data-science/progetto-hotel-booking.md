# Progetto: Analisi prenotazioni hotel

Analisi di un dataset di prenotazioni alberghiere in [[excel]] con prototipo in [[python-pandas]].

**Metodologia** (segue il [[workflow-analisi-dati]]):
- *Cleaning* ([[controlli-qualita-dati]]): valori mancanti, outlier, coerenza delle categoriche e della logica interna (fogli data_cleaning e data_logic).
- *Feature engineering* ([[feature-engineering]]): total_nights, total_guests, booking_value = adr*notti, lead_time in fasce, is_family, room_match, e season/country via CERCA.X su tabelle di lookup.
- *Domande* ([[framework-domande-analitiche]]): % cancellazioni; lead_time vs cancellazione; stagionalita; city vs resort (cancellazioni, ADR, durata); top-10 paesi; famiglie vs durata; ADR per segmento; richieste speciali vs cancellazione.
- *Report* ([[struttura-report-analisi]]) a 3 pagine: panoramica temporale, prezzi & ricavi, cancellazioni.

Dati su disco (fuori dal repo): vedi [[dataset]].

Collegati:
- [[progetti]]
- [[workflow-analisi-dati]]
- [[controlli-qualita-dati]]
- [[feature-engineering]]
- [[framework-domande-analitiche]]
- [[struttura-report-analisi]]
- [[excel]]
- [[python-pandas]]
- [[quartili-outlier]]
- [[dataset]]
