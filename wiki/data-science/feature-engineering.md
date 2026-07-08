# Feature engineering (colonne derivate)

Costruzione di colonne derivate per rendere i dati adatti all'analisi e al report. Pattern ricorrenti dai progetti:

- **Fasce/bucket**: variabile continua -> categorie (lead_time 0-7/8-30/31-90/91-180/181+; eta Giovane/Adulto/Senior; BMI Sottopeso/Normopeso/Sovrappeso/Obeso; charges_level via percentili) con SE annidati.
- **Rapporti/combinazioni**: booking_value = adr * total_nights; total_nights; Rapp_Social_Sonno; Tempo_Libero = 24 - sonno - social.
- **Flag binari**: is_family, room_match, high_cost_outlier (SE/O).
- **Score compositi**: risk_score 0-3 (+1 fumatore, +1 obeso, +1 eta>=50).
- **Lookup**: mappare codici a etichette con CERCA.X e tabelle di lookup (season, country).

Regola d'oro: le feature non si creano a caso, si preparano gia per le domande ([[framework-domande-analitiche]]) e le pagine del report ([[struttura-report-analisi]]).

Collegati:
- [[metodi]]
- [[quartili-outlier]]
- [[excel]]
- [[framework-domande-analitiche]]
- [[struttura-report-analisi]]
