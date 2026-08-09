---
name: scrivi
description: Scrive o revisiona un testo applicando la dottrina della prosa del brain (area creativita / BookForge) e la verifica stilometrica eseguibile. Usa quando l'utente chiede di scrivere un capitolo, un articolo, un report, una nota lunga, o di revisionare un testo esistente — e ogni volta che il brain produce prosa destinata a essere letta da qualcuno.
---

# Scrivi — prosa che vale la pena leggere

Il brain non serve solo a ricordare: **scrive**. Report editoriali, pagine curate, note
di metodo. Questa skill applica a quella prosa la dottrina dell'area `creativita`
(distillata dal sistema BookForge) e la sua verifica misurabile.

## L'ordine conta — non invertirlo

L'ultima cosa letta prima della prima frase dev'essere **prosa**, non regolamento. Un
elenco di divieti attivo mentre scrivi produce scrittura difensiva e rende salienti
proprio i tic che vorresti evitare.

### In stesura vale SOLO la Carta

Leggi `wiki/creativita/carta-della-prosa.md`. Sono imperativi positivi:

- **Concreto, non astratto** — il moltiplicatore numero uno. Non «una macchina vecchia»
  ma «una Panda col paraurti tenuto su dal fil di ferro».
- **Una voce** — niente telecamera neutra: ogni passaggio ha un modo suo di nominare le cose.
- **Ritmo dal senso, non da una quota** — periodo disteso quando il pensiero è disteso,
  frase corta sul colpo.
- **Necessità** — se togli un paragrafo e non cambia nulla, va tagliato. Scrivi a caldo,
  poi togli il 10%.
- **La scelta più vera, non la più probabile** — nomina la versione ovvia, poi chiediti
  se una meno ovvia è *più vera o più chiara*. Tienila solo se lo è.

> **Regola sovrana: se una frase va riletta per essere capita, va riscritta più
> semplice.** Nessuna altra regola può violare la chiarezza. Quando confliggono, vince
> la chiarezza. Sempre.

**Non sono difetti e non si toccano:** la chiarezza, la frase corta, l'emozione detta
in modo pulito, la sintassi semplice.

### Solo DOPO aver scritto: la revisione

1. **Perizia eseguibile:**
   ```bash
   python tools/style_check.py <file>
   python tools/style_check.py --report <nome-report>
   ```
   Leggi l'output in **due classi**:
   - **OGGETTIVA — correggi sempre:** anglicismi e calchi, ripetizioni verbatim.
   - **INDIZIARIA — solo segnalazione:** lunghezza media, flag anglo-tradotto, tic da
     LLM. Dice *dove guardare*. **L'orecchio batte i numeri**: uno staccato voluto non
     è un difetto perché una soglia dice così.

2. **Apri ora** `wiki/creativita/anti-ai.md` (mai prima) e orientati sui due fallimenti:
   se la pagina è competente ma **anonima** manca voce — aggiungi specifico e opinione;
   se è brillante a *ogni* riga e in posa, **togli lucidatura**.

3. **Budget: massimo ~10 interventi di merito.** La revisione illimitata carteggia —
   toglie i difetti e la vita insieme. La classe oggettiva non consuma budget. Se dopo
   il budget il testo ancora non convince, il problema è più profondo della limatura:
   dillo, invece di continuare a limare.

## Per testi lunghi o seriali

Consulta `wiki/creativita/stato-narrativo.md`. L'idea più riutilizzabile è il **Ledger
PIP**: annota come hai aperto e chiuso ogni pezzo, quale senso e quale campo metaforico
dominavano — e nel pezzo successivo **scegli diverso**. La ripetizione invisibile, pezzo
dopo pezzo, è ciò che fa «suonare AI» una serie anche quando la singola pagina è buona.
Vale per i report quanto per i capitoli.

## Se serve calibrare il registro

`wiki/creativita/styledna.md` — 12 assi da 1 a 10. Ricorda i **tetti di salute**
(ST ≤ 7, SUB ≤ 7, RV ≤ 7): oltre, la prosa diventa fredda e oscura, ed è una lezione
pagata su un progetto reale. Una deroga si **guadagna** con una scena-prova verificata,
non si dichiara.

## Apprendimento (ultimo passo, obbligatorio)

```bash
python tools/lesson_log.py --skill scrivi --domanda "<cosa si scriveva>" \
  --esito utile|vicolo-cieco|corretto --nodi "<pagine consultate>" \
  --nota "<cosa ha funzionato o cosa evitare la prossima volta>" --tag "scrittura"
```
