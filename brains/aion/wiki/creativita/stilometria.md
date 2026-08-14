---
date: 2026-08-09
area: creativita
source: raw/creativita/bookforge/ (sistema BookForge v7.6.1)
tags: [stilometria, misura, verifica, qualita]
reviewed: 2026-08-09
---
# Stilometria — la verifica eseguibile della prosa

La prosa si **misura**, non si giudica soltanto. È il gemello letterario di quello che
`controlli-qualita-dati` (area data-science) fa per i dataset: prima di fidarsi, si verifica.

## Come si usa nel brain

```bash
python tools/style_check.py <file.md|.html|.txt>
python tools/style_check.py --report altair-brain-iran-2026
```

Il motore è lo script canonico di BookForge (`raw/creativita/bookforge/stylometry.py`),
importato e non duplicato: se BookForge migliora l'analisi, il brain la eredita.

## Le due classi di segnale — la distinzione che conta

Il valore del metodo non sta nelle metriche: sta nel **non confonderle**.

**OGGETTIVA — si corregge sempre.** Anglicismi e calchi dall'inglese, ripetizioni
verbatim di bigrammi e trigrammi, parole messe al bando dal progetto. Sono fatti, non
opinioni.

**INDIZIARIA — solo segnalazione.** Lunghezza media delle frasi, flag «anglo-tradotto»,
tic da LLM. Dice **dove guardare**, non cosa fare. Uno staccato voluto in un noir non
è un difetto perché una soglia dice così.

> **L'orecchio batte i numeri.** Le soglie non sono quote da rispettare mentre si
> scrive: scrivere per i contatori è già un tic.

## Cosa misura

- **Registro italiano**: ASL, frasi cortissime, frasi nominali → flag «anglo-tradotto».
  Sintomo di prosa frantumata che sa di traduzione; la cura è *ri-legare* dove serve,
  non allungare per principio.
- **Assi quantitativi dello [[styledna]]**: SL, SC, RV, VR, DW già calibrati 1-10.
  Per confrontare capitoli fra loro serve la MATTR, non la TTR (che dipende dalla
  lunghezza del campione).
- **Tic da LLM**: antitesi-riflesso, terzine, trattino drammatico, epigrammi in
  chiusura, schema somatico ripetuto, raffica di «come se», aggettivi-portata.
  Scattano **a grappolo**: una singola occorrenza giusta non è un difetto.

## Prova sul brain stesso

Applicata al report Iran ha trovato ripetizioni verbatim reali («12 luglio» 5 volte,
«il canale» 5 volte) e un abuso di trattini — segnali veri su prosa che sembrava a
posto. È la ragione per cui esiste.

Collegati:
- [[index]]
- [[styledna]]
- [[anti-ai]]
