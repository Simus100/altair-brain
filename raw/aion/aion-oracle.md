- AION ORACLE - Componente I Ching

   Ruolo: Consulenza decisionale, adattamento strategico, generazione di scenari.

   Struttura: Componente autonomo con database, gestione dell'estrazione e interpretazione dinamica.

   Interazione: Collegato al Framework per il supporto analitico e al Manifest per la coerenza filosofica.

---

 - L'uso narrativo dell'I Ching è supportato da AION_Fabula, ma il modulo Oracle rimane la fonte primaria di interpretazione simbolica.

---

## SEZIONE 0: ##  Struttura del Componente:

Il componente "AION_Oracle" integra la logica tradizionale dell'I Ching con l'intelligenza modulare di Aion, offrendo risposte evolutive e riflessive.

---

## SEZIONE 1: ##  Funzionamento del Sistema (modo attivo):

 1. L'utente formula una domanda strategica.

 2. Il sistema elabora gli esagrammi come segue:

   - FASE 1:  Generazione:

AION_Oracle genera 6 valori tra 6 e 9. Ogni numero rappresenta una linea (dal basso verso l'alto):

| Valore | Tipo di Linea       | Stato         | Codice Binario |
|--------|----------------------|---------------|----------------|
| 6      | Yin mobile         | Muta → Yang   | 0              |
| 7      | Yang stabile        | Invariata     | 1              |
| 8      | Yin stabile         | Invariata     | 0              |
| 9      | Yang mobile        | Muta → Yin    | 1              |



     - FASE 2: Identificazione dell'Esagramma:

Metodo A – Codifica Binaria:

1. Le 6 linee sono convertite in bit (0/1).
2. La sequenza è ordinata dal basso verso l'alto.
3. Il numero binario viene convertito in decimale.
4. Si aggiunge +1 per ottenere l'ID dell'esagramma (range: 1–64).

ATTENZIONE: La sequenza di Re Wen (King Wen) NON è ordinata per valore binario.
Per ottenere l'ID corretto dall'encoding binario, è NECESSARIO usare la tabella di lookup
nella Sezione 3.6. Il metodo decimale+1 NON è valido.

Metodo B – Identificazione per Trigrammi:

1. Le linee 1-2-3 (dal basso) formano il trigramma inferiore.
2. Le linee 4-5-6 (dal basso) formano il trigramma superiore.
3. Si consulta la Sezione 3.5 per identificare i due trigrammi.
4. La combinazione dei due trigrammi identifica univocamente l'esagramma nella Sezione 4.



      - FASE 3: Mutazione e Secondo Esagramma:

Le linee mobili (6 e 9) vengono trasformate:
- 6 → 7 (Yin → Yang)
- 9 → 8 (Yang → Yin)

Il secondo esagramma rappresenta la direzione del cambiamento. Si applica la stessa logica binaria o trigrammatica per determinarne l'ID.



     - FASE 4: Interpretazione

AION_Oracle restituisce:

1. Significato generale del primo esagramma.
2. Interpretazione delle linee mobili selezionate.
3. Significato generale del secondo esagramma (se linee mobili presenti).
4. Sintesi discorsiva della trasformazione.

Regole per l'uso delle linee mobili:
- 1 sola → interpreta quella
- 2 (yin + yang) → scegli Yin
- 3 → scegli la mediana
- 4 → scegli la più alta fissa
- 6 linee mobili → ignora il primo esagramma, consulta il secondo

---

##  SEZIONE 2:  ## Funzionamento Creativo e Autonomo:

1. AION_Fabula può richiamare AION_Oracle per generare **spunti narrativi evolutivi**.

2. I due esagrammi possono rappresentare:
  
   - **Evento + Trasformazione**
   - **Personaggio + Evoluzione**
   - **Scenario + Crisi**

3. Il modulo accede al Database Oracle per costruire:
  
   - Massime
   - Archetipi
   - Strutture narrative mutanti

---

##  SEZIONE 3:  ## Utilizzo Narrativo dell'I Ching:

Il modulo si integra nel sistema narrativo AION per generare storytelling simbolico.

###  Spunti di Trama:
Ogni esagramma è un **tema archetipico**: *Difficoltà Iniziale*, *Il Ristagno*, *La Nutrizione*, ecc.

###  Caratterizzazione dei Personaggi  
Gli esagrammi possono rappresentare **stati interiori, ruoli, conflitti o trasformazioni**.

###  Ambientazioni e Atmosfere:  
Trigrammi elementali (fuoco, acqua, terra, vento, tuono...) influenzano lo scenario simbolico.

###  Tensioni e Svolte:  
Le linee mobili fungono da **marcatori di crisi o svolta narrativa**, utili per innescare colpi di scena o metamorfosi.

---

## SEZIONE 3.5: ## Riferimento Trigrammi — Gli 8 Trigrammi (Bāguà):

| Simbolo | Nome IT    | Hanzi | Pinyin | Attributo               | Elemento | Immagine     | Famiglia       | Binario |
|---------|------------|-------|--------|--------------------------|----------|--------------|----------------|---------|
| ☰      | Cielo      | 乾    | Qián   | Forza, Creatività        | Metallo  | Cielo        | Padre          | 111     |
| ☷      | Terra      | 坤    | Kūn    | Ricettività, Devozione   | Terra    | Terra        | Madre          | 000     |
| ☳      | Tuono      | 震    | Zhèn   | Movimento, Incitamento   | Legno    | Tuono        | Primo Figlio   | 100     |
| ☵      | Acqua      | 坎    | Kǎn    | Pericolo, Profondità     | Acqua    | Acqua        | Secondo Figlio | 010     |
| ☶      | Montagna   | 艮    | Gèn    | Arresto, Quiete          | Terra    | Montagna     | Terzo Figlio   | 001     |
| ☴      | Vento      | 巽    | Xùn    | Penetrazione, Dolcezza   | Legno    | Vento/Legno  | Prima Figlia   | 011     |
| ☲      | Fuoco      | 離    | Lí     | Aderenza, Chiarezza      | Fuoco    | Fuoco        | Seconda Figlia | 101     |
| ☱      | Lago       | 兌    | Duì    | Gioia, Serenità          | Metallo  | Lago         | Terza Figlia   | 110     |

Note:
- Il codice binario è letto dal basso verso l'alto (linea 1 → bit più a sinistra).
- Yang (linea intera) = 1, Yin (linea spezzata) = 0.
- I Cinque Elementi (Wǔ Xíng): Metallo, Legno, Acqua, Fuoco, Terra.

---

## SEZIONE 3.6: ## Tabella di Lookup — Codifica Binaria → ID Esagramma (Sequenza di Re Wen):

La codifica binaria è composta da 6 bit letti dal basso verso l'alto (linea 1 = bit sinistro).
I primi 3 bit corrispondono al trigramma inferiore, gli ultimi 3 al trigramma superiore.

| Binario | Dec | ID | Nome                                    | Superiore | Inferiore |
|---------|-----|----|-----------------------------------------|-----------|-----------|
| 111111  | 63  |  1 | Il Creativo                             | ☰ Cielo   | ☰ Cielo   |
| 000000  |  0  |  2 | Il Ricettivo                            | ☷ Terra   | ☷ Terra   |
| 100010  | 34  |  3 | Difficoltà Iniziale                     | ☵ Acqua   | ☳ Tuono   |
| 010001  | 17  |  4 | L'Inesperienza                          | ☶ Montagna| ☵ Acqua   |
| 111010  | 58  |  5 | L'Attesa                                | ☵ Acqua   | ☰ Cielo   |
| 010111  | 23  |  6 | Il Conflitto                            | ☰ Cielo   | ☵ Acqua   |
| 010000  | 16  |  7 | L'Esercito                              | ☷ Terra   | ☵ Acqua   |
| 000010  |  2  |  8 | La Coesione                             | ☵ Acqua   | ☷ Terra   |
| 111011  | 59  |  9 | La Forza Domata dal Piccolo             | ☴ Vento   | ☰ Cielo   |
| 110111  | 55  | 10 | Il Procedere                            | ☰ Cielo   | ☱ Lago    |
| 111000  | 56  | 11 | La Pace                                 | ☷ Terra   | ☰ Cielo   |
| 000111  |  7  | 12 | Il Ristagno                             | ☰ Cielo   | ☷ Terra   |
| 101111  | 47  | 13 | La Comunità                             | ☰ Cielo   | ☲ Fuoco   |
| 111101  | 61  | 14 | Il Possesso Grande                      | ☲ Fuoco   | ☰ Cielo   |
| 001000  |  8  | 15 | La Modestia                             | ☷ Terra   | ☶ Montagna|
| 000100  |  4  | 16 | L'Entusiasmo                            | ☳ Tuono   | ☷ Terra   |
| 100110  | 38  | 17 | Il Seguimento                           | ☱ Lago    | ☳ Tuono   |
| 011001  | 25  | 18 | Il Lavoro sul Deterioramento            | ☶ Montagna| ☴ Vento   |
| 110000  | 48  | 19 | L'Avvicinamento                         | ☷ Terra   | ☱ Lago    |
| 000011  |  3  | 20 | La Contemplazione                       | ☴ Vento   | ☷ Terra   |
| 100101  | 37  | 21 | Il Morso che Spezza                     | ☲ Fuoco   | ☳ Tuono   |
| 101001  | 41  | 22 | La Grazia                               | ☶ Montagna| ☲ Fuoco   |
| 000001  |  1  | 23 | Il Disgregarsi                          | ☶ Montagna| ☷ Terra   |
| 100000  | 32  | 24 | Il Ritorno                              | ☷ Terra   | ☳ Tuono   |
| 100111  | 39  | 25 | L'Innocenza                             | ☰ Cielo   | ☳ Tuono   |
| 111001  | 57  | 26 | La Forza Domatrice del Grande           | ☶ Montagna| ☰ Cielo   |
| 100001  | 33  | 27 | Gli Angoli della Bocca                  | ☶ Montagna| ☳ Tuono   |
| 011110  | 30  | 28 | La Preponderanza del Grande             | ☱ Lago    | ☴ Vento   |
| 010010  | 18  | 29 | L'Abissale                              | ☵ Acqua   | ☵ Acqua   |
| 101101  | 45  | 30 | L'Aderente                              | ☲ Fuoco   | ☲ Fuoco   |
| 001110  | 14  | 31 | L'Attrazione                            | ☱ Lago    | ☶ Montagna|
| 011100  | 28  | 32 | La Durata                               | ☳ Tuono   | ☴ Vento   |
| 001111  | 15  | 33 | La Ritirata                             | ☰ Cielo   | ☶ Montagna|
| 111100  | 60  | 34 | La Potenza del Grande                   | ☳ Tuono   | ☰ Cielo   |
| 000101  |  5  | 35 | Il Progresso                            | ☲ Fuoco   | ☷ Terra   |
| 101000  | 40  | 36 | L'Ottenebramento della Luce             | ☷ Terra   | ☲ Fuoco   |
| 101011  | 43  | 37 | La Casata                               | ☴ Vento   | ☲ Fuoco   |
| 110101  | 53  | 38 | L'Opposizione                           | ☲ Fuoco   | ☱ Lago    |
| 001010  | 10  | 39 | L'Impedimento                           | ☵ Acqua   | ☶ Montagna|
| 010100  | 20  | 40 | La Liberazione                          | ☳ Tuono   | ☵ Acqua   |
| 110001  | 49  | 41 | La Diminuzione                          | ☶ Montagna| ☱ Lago    |
| 100011  | 35  | 42 | L'Accrescimento                         | ☴ Vento   | ☳ Tuono   |
| 111110  | 62  | 43 | Lo Straripamento                        | ☱ Lago    | ☰ Cielo   |
| 011111  | 31  | 44 | Il Farsi Incontro                       | ☰ Cielo   | ☴ Vento   |
| 000110  |  6  | 45 | La Raccolta                             | ☱ Lago    | ☷ Terra   |
| 011000  | 24  | 46 | L'Ascendere                             | ☷ Terra   | ☴ Vento   |
| 010110  | 22  | 47 | L'Esaurimento                           | ☱ Lago    | ☵ Acqua   |
| 011010  | 26  | 48 | Il Pozzo                                | ☵ Acqua   | ☴ Vento   |
| 101110  | 46  | 49 | Il Sovvertimento                        | ☱ Lago    | ☲ Fuoco   |
| 011101  | 29  | 50 | Il Crogiolo                             | ☲ Fuoco   | ☴ Vento   |
| 100100  | 36  | 51 | Il Tuono                                | ☳ Tuono   | ☳ Tuono   |
| 001001  |  9  | 52 | L'Arresto                               | ☶ Montagna| ☶ Montagna|
| 001011  | 11  | 53 | Lo Sviluppo                             | ☴ Vento   | ☶ Montagna|
| 110100  | 52  | 54 | La Ragazza che Si Sposa                 | ☳ Tuono   | ☱ Lago    |
| 101100  | 44  | 55 | L'Abbondanza                            | ☳ Tuono   | ☲ Fuoco   |
| 001101  | 13  | 56 | Il Viandante                            | ☲ Fuoco   | ☶ Montagna|
| 011011  | 27  | 57 | Il Vento                                | ☴ Vento   | ☴ Vento   |
| 110110  | 54  | 58 | Il Sereno                               | ☱ Lago    | ☱ Lago    |
| 010011  | 19  | 59 | La Dissoluzione                         | ☴ Vento   | ☵ Acqua   |
| 110010  | 50  | 60 | La Limitazione                          | ☵ Acqua   | ☱ Lago    |
| 110011  | 51  | 61 | La Veracità Interiore                   | ☴ Vento   | ☱ Lago    |
| 001100  | 12  | 62 | La Preponderanza del Piccolo            | ☳ Tuono   | ☶ Montagna|
| 101010  | 42  | 63 | Dopo il Compimento                      | ☵ Acqua   | ☲ Fuoco   |
| 010101  | 21  | 64 | Prima del Compimento                    | ☲ Fuoco   | ☵ Acqua   |

---

## SEZIONE 4: ## Database Oracle – 64 Esagrammi:

AION_Oracle include un database strutturato contenente i 64 esagrammi.
Ogni esagramma è identificato dal numero prima del nome (## 1. = ID 1, ## 2. = ID 2, ..., ## 64. = ID 64).

Formato di ogni voce:
- Struttura: trigrammi, codifica binaria, simbolo Unicode
- Relazioni: esagramma opposto, rovesciato, nucleare
- Tag: parole chiave per ricerca semantica
- Giudizio: testo tradizionale (dal classico)
- Immagine: testo tradizionale (dal classico)
- Interpretazione Moderna: lettura contemporanea
- Linee Mobili: interpretazione per ogni linea con notazione tradizionale

═══════════════════════════════════════════════════════════════════════════════════


## 1. 乾 Il Creativo (Qián) ䷀

### Struttura
- **Trigramma Superiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Trigramma Inferiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Codifica Binaria:** 111111 (dec: 63)

### Relazioni
- **Opposto:** 2 — Il Ricettivo
- **Rovesciato:** 1 — Il Creativo (palindromo)
- **Nucleare:** 1 — Il Creativo

### Tag
`leadership` `iniziativa` `potere` `determinazione` `ambizione` `forza creatrice` `cielo`

### Giudizio
Il Creativo opera sublime riuscita, propizio per la perseveranza.

### Immagine
Il moto del Cielo è pieno di potenza. Così il nobile rende sé stesso forte e instancabile.

### Interpretazione Moderna
Energia pura e forza iniziatrice. Il potere di plasmare la realtà con determinazione. Sii ambizioso, prendi l'iniziativa, ma non diventare arrogante.

### Linee Mobili
- **Linea 1 (初九):** L'impeto iniziale va calibrato: prudenza nel fare il primo passo.
- **Linea 2 (九二):** Cooperazione e saggezza nel consolidare la propria forza.
- **Linea 3 (九三):** Attenzione all'eccesso di fiducia, rischi di superare i limiti.
- **Linea 4 (九四):** Crescita armoniosa, ma serve una base solida.
- **Linea 5 (九五):** Leadership ispirata; mantieni una visione lungimirante.
- **Linea 6 (上九):** Evita la tracotanza finale; la vetta non deve farti perdere l'umiltà.

═══════════════════════════════════════════════════════════════════════════════════


## 2. 坤 Il Ricettivo (Kūn) ䷁

### Struttura
- **Trigramma Superiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Trigramma Inferiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Codifica Binaria:** 000000 (dec: 0)

### Relazioni
- **Opposto:** 1 — Il Creativo
- **Rovesciato:** 2 — Il Ricettivo (palindromo)
- **Nucleare:** 2 — Il Ricettivo

### Tag
`ricettività` `adattamento` `flessibilità` `strategia passiva` `terra` `sostegno` `devozione`

### Giudizio
Il Ricettivo opera sublime riuscita, propizia attraverso la perseveranza di una cavalla. Il nobile ha dove andare.

### Immagine
Lo stato della Terra è la devozione ricettiva. Così il nobile porta con ampiezza di carattere il mondo esterno.

### Interpretazione Moderna
L'arte della strategia passiva. La flessibilità e la capacità di adattarsi alla situazione sono fondamentali. Non tutto va forzato: il flusso naturale è spesso il migliore.

### Linee Mobili
- **Linea 1 (初六):** Riconosci i tuoi limiti iniziali, resta aperto.
- **Linea 2 (六二):** Avanza con calma; ricettività costruttiva.
- **Linea 3 (六三):** Non confondere la modestia con la sottomissione.
- **Linea 4 (六四):** Sfrutta il potenziale di chi ti circonda.
- **Linea 5 (六五):** Salda le fondamenta per una crescita duratura.
- **Linea 6 (上六):** Evita l'eccessiva passività, agisci con coraggio.

═══════════════════════════════════════════════════════════════════════════════════


## 3. 屯 Difficoltà Iniziale (Zhūn) ䷂

### Struttura
- **Trigramma Superiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Trigramma Inferiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Codifica Binaria:** 100010 (dec: 34)

### Relazioni
- **Opposto:** 50 — Il Crogiolo
- **Rovesciato:** 4 — L'Inesperienza
- **Nucleare:** 23 — Il Disgregarsi

### Tag
`inizio` `caos` `ostacoli` `costruzione` `resilienza` `organizzazione` `nascita`

### Giudizio
Difficoltà Iniziale. Sublime riuscita, propizia per la perseveranza. Non si deve intraprendere nulla; è propizio istituire aiutanti.

### Immagine
Nuvole e tuono: l'immagine della Difficoltà Iniziale. Così il nobile porta ordine con la separazione e la struttura.

### Interpretazione Moderna
Inizio turbolento, caos creativo. Gli ostacoli sono normali nelle fasi iniziali, ma ciò che costruisci ora diventerà solido in futuro. Resisti, organizza e avanza.

### Linee Mobili
- **Linea 1 (初九):** Il caos iniziale dev'essere fronteggiato con lucidità.
- **Linea 2 (六二):** Piccoli passi costruiscono la base per il successo.
- **Linea 3 (六三):** Non perdere tempo con preoccupazioni inutili, agisci.
- **Linea 4 (六四):** Sviluppa una strategia concreta, non solo idee astratte.
- **Linea 5 (九五):** Lavora in squadra, condividi responsabilità.
- **Linea 6 (上六):** Concludi la fase caotica prima di passare oltre.

═══════════════════════════════════════════════════════════════════════════════════


## 4. 蒙 L'Inesperienza (Méng) ䷃

### Struttura
- **Trigramma Superiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Trigramma Inferiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Codifica Binaria:** 010001 (dec: 17)

### Relazioni
- **Opposto:** 49 — Il Sovvertimento
- **Rovesciato:** 3 — Difficoltà Iniziale
- **Nucleare:** 24 — Il Ritorno

### Tag
`apprendimento` `crescita` `inesperienza` `mentore` `umiltà` `educazione` `giovinezza`

### Giudizio
L'Inesperienza ha riuscita. Non sono io a cercare il giovane folle, è il giovane folle a cercare me. Alla prima consultazione rispondo. Perseveranza propizia.

### Immagine
Ai piedi della montagna sgorga una sorgente: l'immagine della Giovinezza. Così il nobile alimenta il suo carattere con azione risoluta.

### Interpretazione Moderna
Crescita e apprendimento. Non temere di essere all'inizio di un percorso. Accetta i consigli, sii umile e impara velocemente.

### Linee Mobili
- **Linea 1 (初六):** Curiosità e volontà di imparare sono essenziali.
- **Linea 2 (九二):** Individua una guida o un mentore.
- **Linea 3 (六三):** Non farti bloccare dall'insicurezza; sperimenta.
- **Linea 4 (六四):** Equilibrio tra teoria e pratica.
- **Linea 5 (六五):** Fai tesoro di errori e consigli.
- **Linea 6 (上九):** Evita l'arroganza di chi crede di sapere tutto.

═══════════════════════════════════════════════════════════════════════════════════


## 5. 需 L'Attesa (Xū) ䷄

### Struttura
- **Trigramma Superiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Trigramma Inferiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Codifica Binaria:** 111010 (dec: 58)

### Relazioni
- **Opposto:** 35 — Il Progresso
- **Rovesciato:** 6 — Il Conflitto
- **Nucleare:** 38 — L'Opposizione

### Tag
`pazienza` `attesa` `tempo` `strategia` `preparazione` `nutrimento` `fiducia`

### Giudizio
L'Attesa. Se sei veritiero, hai luce e riuscita. La perseveranza reca salute. È propizio attraversare la grande acqua.

### Immagine
Nuvole salgono nel cielo: l'immagine dell'Attesa. Così il nobile mangia, beve, è lieto e di buon umore.

### Interpretazione Moderna
Il tempo giusto non è sempre adesso. Pazienza strategica: a volte è meglio aspettare il momento giusto piuttosto che forzare una situazione.

### Linee Mobili
- **Linea 1 (初九):** Non forzare gli eventi, ma preparati.
- **Linea 2 (九二):** La calma iniziale favorisce la crescita futura.
- **Linea 3 (九三):** Evita l'impulsività; il tempo non è ancora maturo.
- **Linea 4 (六四):** Mantieni alta la concentrazione in vista di sviluppi imminenti.
- **Linea 5 (九五):** Quando si presenta l'occasione, coglila con decisione.
- **Linea 6 (上六):** Troppa attesa può portare all'inazione.

═══════════════════════════════════════════════════════════════════════════════════


## 6. 訟 Il Conflitto (Sòng) ䷅

### Struttura
- **Trigramma Superiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Trigramma Inferiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Codifica Binaria:** 010111 (dec: 23)

### Relazioni
- **Opposto:** 36 — L'Ottenebramento della Luce
- **Rovesciato:** 5 — L'Attesa
- **Nucleare:** 37 — La Casata

### Tag
`conflitto` `tensione` `negoziazione` `ritiro` `giustizia` `dispute` `compromesso`

### Giudizio
Il Conflitto. Sei veritiero e vieni ostacolato. Fermarsi a metà porta salute. Portare le cose alla fine reca sciagura. È propizio vedere il grande uomo. Non è propizio attraversare la grande acqua.

### Immagine
Cielo e acqua vanno in direzioni opposte: l'immagine del Conflitto. Così il nobile, in tutti gli affari, considera attentamente l'inizio.

### Interpretazione Moderna
La tensione esiste, ma devi scegliere se combattere o ritirarti con intelligenza. Se la battaglia non porta vantaggi, lasciala andare.

### Linee Mobili
- **Linea 1 (初六):** Non scatenare la guerra finché non sei pronto.
- **Linea 2 (九二):** Chiarisci la natura del conflitto, trova alleati.
- **Linea 3 (六三):** Evita una lotta estenuante senza scopi precisi.
- **Linea 4 (九四):** Cerca una conciliazione, se possibile.
- **Linea 5 (九五):** Agisci con fermezza, ma rispetta i limiti.
- **Linea 6 (上九):** Un conflitto protratto rischia di logorarti.

═══════════════════════════════════════════════════════════════════════════════════


## 7. 師 L'Esercito (Shī) ䷆

### Struttura
- **Trigramma Superiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Trigramma Inferiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Codifica Binaria:** 010000 (dec: 16)

### Relazioni
- **Opposto:** 13 — La Comunità
- **Rovesciato:** 8 — La Coesione
- **Nucleare:** 24 — Il Ritorno

### Tag
`disciplina` `strategia` `organizzazione` `leadership` `risorse` `coordinazione` `esercito`

### Giudizio
L'Esercito. L'esercito ha bisogno di perseveranza e di un uomo forte. Salute, senza macchia.

### Immagine
Nel mezzo della terra c'è acqua: l'immagine dell'Esercito. Così il nobile accresce le sue moltitudini essendo generoso verso il popolo.

### Interpretazione Moderna
Disciplina e strategia. Un piano ben organizzato porta alla vittoria. Agisci con coordinazione, gestisci le risorse con saggezza.

### Linee Mobili
- **Linea 1 (初六):** Definisci ruoli e gerarchie con chiarezza.
- **Linea 2 (九二):** Un esercito efficace ha obiettivi condivisi.
- **Linea 3 (六三):** Non sprecare risorse; valuta rischi e vantaggi.
- **Linea 4 (六四):** Coordinati con chi dirige le operazioni.
- **Linea 5 (六五):** Leadership autorevole e giusta.
- **Linea 6 (上六):** Evita dispersioni e diserzioni, mantieni coesione.

═══════════════════════════════════════════════════════════════════════════════════


## 8. 比 La Coesione (Bǐ) ䷇

### Struttura
- **Trigramma Superiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Trigramma Inferiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Codifica Binaria:** 000010 (dec: 2)

### Relazioni
- **Opposto:** 14 — Il Possesso Grande
- **Rovesciato:** 7 — L'Esercito
- **Nucleare:** 23 — Il Disgregarsi

### Tag
`unione` `collaborazione` `fiducia` `alleanza` `legame` `comunità` `coesione`

### Giudizio
La Coesione reca salute. Esamina l'oracolo ancora una volta per verificare se possiedi sublimità, durata e perseveranza; allora non c'è macchia.

### Immagine
Sulla terra c'è acqua: l'immagine della Coesione. Così gli antichi re fondavano i loro stati e coltivavano relazioni con i feudatari.

### Interpretazione Moderna
Unione e collaborazione. I legami forti creano successo. Circondati di persone che condividono la tua visione.

### Linee Mobili
- **Linea 1 (初六):** Cerca affinità con chi condivide i tuoi valori.
- **Linea 2 (六二):** Non imporre l'unione; coltivala.
- **Linea 3 (六三):** Se c'è discordia, trova un terreno comune.
- **Linea 4 (六四):** Rafforza la fiducia reciproca.
- **Linea 5 (九五):** Un leader coeso ispira la squadra.
- **Linea 6 (上六):** Evita di isolarti, mantieni l'armonia.

═══════════════════════════════════════════════════════════════════════════════════


## 9. 小畜 La Forza Domata dal Piccolo (Xiǎo Chù) ䷈

### Struttura
- **Trigramma Superiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Trigramma Inferiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Codifica Binaria:** 111011 (dec: 59)

### Relazioni
- **Opposto:** 16 — L'Entusiasmo
- **Rovesciato:** 10 — Il Procedere
- **Nucleare:** 38 — L'Opposizione

### Tag
`dettagli` `pazienza` `piccoli passi` `tatto` `moderazione` `influenza sottile` `contenimento`

### Giudizio
La Forza Domata dal Piccolo ha riuscita. Nubi dense, nessuna pioggia dalle nostre regioni a occidente.

### Immagine
Il vento soffia in cielo: l'immagine della Forza Domata dal Piccolo. Così il nobile raffina le manifestazioni esteriori della sua natura.

### Interpretazione Moderna
Piccole forze possono guidare grandi eventi. Procedi con tatto e attenzione ai dettagli.

### Linee Mobili
- **Linea 1 (初九):** Non sottovalutare l'importanza dei dettagli.
- **Linea 2 (九二):** Consolidati progressi, passo dopo passo.
- **Linea 3 (九三):** Troppa ambizione può rompere l'equilibrio.
- **Linea 4 (六四):** Una minima correzione di rotta può avere grandi effetti.
- **Linea 5 (九五):** Focalizzati sulle soluzioni più semplici.
- **Linea 6 (上九):** Riconosci quando è il momento di espandersi.

═══════════════════════════════════════════════════════════════════════════════════


## 10. 履 Il Procedere (Lǚ) ䷉

### Struttura
- **Trigramma Superiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Trigramma Inferiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Codifica Binaria:** 110111 (dec: 55)

### Relazioni
- **Opposto:** 15 — La Modestia
- **Rovesciato:** 9 — La Forza Domata dal Piccolo
- **Nucleare:** 37 — La Casata

### Tag
`prudenza` `condotta` `rispetto` `coraggio` `integrità` `cammino` `prova`

### Giudizio
Il Procedere. Pestare la coda della tigre. Essa non morde l'uomo. Riuscita.

### Immagine
In alto il cielo, in basso il lago: l'immagine del Procedere. Così il nobile distingue alto e basso e consolida il senso del popolo.

### Interpretazione Moderna
Cammina con attenzione e rispetto. La prudenza ti aiuterà a superare gli ostacoli.

### Linee Mobili
- **Linea 1 (初九):** Parti con piccoli passi, la fretta è nemica.
- **Linea 2 (九二):** Mantieni integrità anche se la via è stretta.
- **Linea 3 (六三):** Evita la superficialità; ogni passo conta.
- **Linea 4 (九四):** Affronta la paura con coraggio misurato.
- **Linea 5 (九五):** Procedere con dignità porta fiducia.
- **Linea 6 (上九):** Superata la prova, non dimenticare l'umiltà.

═══════════════════════════════════════════════════════════════════════════════════


## 11. 泰 La Pace (Tài) ䷊

### Struttura
- **Trigramma Superiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Trigramma Inferiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Codifica Binaria:** 111000 (dec: 56)

### Relazioni
- **Opposto:** 12 — Il Ristagno
- **Rovesciato:** 12 — Il Ristagno
- **Nucleare:** 54 — La Ragazza che Si Sposa

### Tag
`armonia` `equilibrio` `pace` `prosperità` `unione degli opposti` `crescita` `fioritura`

### Giudizio
La Pace. Il piccolo se ne va, il grande viene. Salute e riuscita.

### Immagine
Cielo e terra si uniscono: l'immagine della Pace. Così il sovrano divide e compie il corso di cielo e terra, amministra e ordina i doni di cielo e terra, e così assiste il popolo.

### Interpretazione Moderna
Armonia tra forze opposte. Un periodo favorevole di equilibrio e crescita.

### Linee Mobili
- **Linea 1 (初九):** All'inizio, sii sicuro dei tuoi principi.
- **Linea 2 (九二):** Lavora per una collaborazione equilibrata.
- **Linea 3 (九三):** Evita conflitti interni prima che diventino gravi.
- **Linea 4 (六四):** Resta vigile: la pace può essere fragile.
- **Linea 5 (六五):** Se la leadership è saggia, la comunità prospera.
- **Linea 6 (上六):** Quando la pace si esaurisce, prepara nuove strategie.

═══════════════════════════════════════════════════════════════════════════════════


## 12. 否 Il Ristagno (Pǐ) ䷋

### Struttura
- **Trigramma Superiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Trigramma Inferiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Codifica Binaria:** 000111 (dec: 7)

### Relazioni
- **Opposto:** 11 — La Pace
- **Rovesciato:** 11 — La Pace
- **Nucleare:** 53 — Lo Sviluppo

### Tag
`blocco` `stagnazione` `riflessione` `preparazione` `resistenza` `declino` `separazione`

### Giudizio
Il Ristagno. Persone malvagie non favoriscono la perseveranza del nobile. Il grande se ne va, il piccolo viene.

### Immagine
Cielo e terra non si uniscono: l'immagine del Ristagno. Così il nobile si ritrae nella propria virtù per sfuggire alle difficoltà.

### Interpretazione Moderna
Blocco e difficoltà. Quando tutto si ferma, usa il tempo per riflettere e prepararti.

### Linee Mobili
- **Linea 1 (初六):** Non arrenderti subito; cerca una soluzione.
- **Linea 2 (六二):** Mantieni la calma quando tutto sembra fermo.
- **Linea 3 (六三):** Evita di lamentarti, agisci su ciò che puoi.
- **Linea 4 (九四):** La trasformazione inizia dall'interno.
- **Linea 5 (九五):** Trova risorse alternative, sii creativo.
- **Linea 6 (上九):** Il ristagno non è eterno; preparati al cambiamento.

═══════════════════════════════════════════════════════════════════════════════════


## 13. 同人 La Comunità (Tóng Rén) ䷌

### Struttura
- **Trigramma Superiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Trigramma Inferiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Codifica Binaria:** 101111 (dec: 47)

### Relazioni
- **Opposto:** 7 — L'Esercito
- **Rovesciato:** 14 — Il Possesso Grande
- **Nucleare:** 44 — Il Farsi Incontro

### Tag
`comunità` `unità` `collaborazione` `inclusione` `visione comune` `fratellanza` `apertura`

### Giudizio
Comunità con gli uomini all'aperto. Riuscita. È propizio attraversare la grande acqua. Propizia è la perseveranza del nobile.

### Immagine
Cielo e fuoco insieme: l'immagine della Comunità. Così il nobile organizza i clan e distingue le cose.

### Interpretazione Moderna
La forza dell'unità. Collaborare con gli altri porta vantaggi a lungo termine.

### Linee Mobili
- **Linea 1 (初九):** Inizia creando connessioni sincere.
- **Linea 2 (六二):** Ascolta tutti i membri, favorisci l'inclusione.
- **Linea 3 (九三):** Risolvi i dissidi con dialogo aperto.
- **Linea 4 (九四):** Condividi obiettivi chiari e comuni.
- **Linea 5 (九五):** Guida con l'esempio, stimola l'appartenenza.
- **Linea 6 (上九):** Non trascurare la diversità di prospettive.

═══════════════════════════════════════════════════════════════════════════════════


## 14. 大有 Il Possesso Grande (Dà Yǒu) ䷍

### Struttura
- **Trigramma Superiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Trigramma Inferiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Codifica Binaria:** 111101 (dec: 61)

### Relazioni
- **Opposto:** 8 — La Coesione
- **Rovesciato:** 13 — La Comunità
- **Nucleare:** 43 — Lo Straripamento

### Tag
`abbondanza` `successo` `generosità` `responsabilità` `ricchezza` `influenza` `prosperità`

### Giudizio
Il Possesso Grande. Sublime riuscita.

### Immagine
Il fuoco alto nel cielo: l'immagine del Possesso Grande. Così il nobile reprime il male e promuove il bene, obbedendo alla volontà benevola del cielo.

### Interpretazione Moderna
Successo e abbondanza. Usa la tua influenza con saggezza.

### Linee Mobili
- **Linea 1 (初九):** Non ostentare troppo ciò che possiedi.
- **Linea 2 (九二):** Condividi risorse, crea prosperità collettiva.
- **Linea 3 (九三):** Evita sprechi e investimenti avventati.
- **Linea 4 (九四):** Mantieni l'equilibrio tra potere e umiltà.
- **Linea 5 (六五):** Un leader munifico favorisce fiducia.
- **Linea 6 (上九):** Grande possesso implica grandi responsabilità.

═══════════════════════════════════════════════════════════════════════════════════


## 15. 謙 La Modestia (Qiān) ䷎

### Struttura
- **Trigramma Superiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Trigramma Inferiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Codifica Binaria:** 001000 (dec: 8)

### Relazioni
- **Opposto:** 10 — Il Procedere
- **Rovesciato:** 16 — L'Entusiasmo
- **Nucleare:** 40 — La Liberazione

### Tag
`umiltà` `modestia` `efficacia` `discrezione` `merito` `semplicità` `equilibrio`

### Giudizio
La Modestia crea riuscita. Il nobile porta le cose a compimento.

### Immagine
Dentro la terra c'è una montagna: l'immagine della Modestia. Così il nobile riduce ciò che è troppo e accresce ciò che è troppo poco. Pesa le cose e le rende uguali.

### Interpretazione Moderna
L'umiltà apre più porte del vanto. Mantieni un profilo basso e sii efficace.

### Linee Mobili
- **Linea 1 (初六):** Non confondere modestia con debolezza.
- **Linea 2 (六二):** Riconosci i tuoi meriti ma senza arroganza.
- **Linea 3 (九三):** I troppi onori possono intralciare la crescita.
- **Linea 4 (六四):** Collabora in silenzio, i risultati parleranno.
- **Linea 5 (六五):** Grande influenza si ottiene con discrezione.
- **Linea 6 (上六):** Rimani umile anche al culmine del successo.

═══════════════════════════════════════════════════════════════════════════════════


## 16. 豫 L'Entusiasmo (Yù) ䷏

### Struttura
- **Trigramma Superiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Trigramma Inferiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Codifica Binaria:** 000100 (dec: 4)

### Relazioni
- **Opposto:** 9 — La Forza Domata dal Piccolo
- **Rovesciato:** 15 — La Modestia
- **Nucleare:** 39 — L'Impedimento

### Tag
`entusiasmo` `ispirazione` `motivazione` `energia` `azione` `musica` `slancio`

### Giudizio
L'Entusiasmo. È propizio istituire aiutanti e far marciare eserciti.

### Immagine
Il tuono erompe dalla terra con fragore: l'immagine dell'Entusiasmo. Così gli antichi re facevano musica per onorare il merito e la offrivano con magnificenza al Dio Supremo.

### Interpretazione Moderna
Energia e ispirazione. Se credi in qualcosa, agisci con convinzione.

### Linee Mobili
- **Linea 1 (初六):** Convoglia l'energia iniziale con scopo chiaro.
- **Linea 2 (六二):** Motiva chi ti sta vicino; l'entusiasmo è contagioso.
- **Linea 3 (六三):** Dosalo bene, evitando sbandate.
- **Linea 4 (九四):** L'ispirazione cresce con l'esperienza.
- **Linea 5 (六五):** Guida gli altri con passione ed empatia.
- **Linea 6 (上六):** Non lasciarti travolgere dall'euforia.

═══════════════════════════════════════════════════════════════════════════════════


## 17. 隨 Il Seguimento (Suí) ䷐

### Struttura
- **Trigramma Superiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Trigramma Inferiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Codifica Binaria:** 100110 (dec: 38)

### Relazioni
- **Opposto:** 18 — Il Lavoro sul Deterioramento
- **Rovesciato:** 18 — Il Lavoro sul Deterioramento
- **Nucleare:** 53 — Lo Sviluppo

### Tag
`adattamento` `flusso` `seguire` `flessibilità` `contesto` `apprendimento` `servizio`

### Giudizio
Il Seguimento ha sublime riuscita. Propizia è la perseveranza. Nessuna macchia.

### Immagine
Nel mezzo del lago c'è il tuono: l'immagine del Seguimento. Così il nobile al crepuscolo entra in casa per riposare e ristorarsi.

### Interpretazione Moderna
Adattarsi al flusso è a volte la migliore strategia.

### Linee Mobili
- **Linea 1 (初九):** Seguire non vuol dire perdere la propria identità.
- **Linea 2 (六二):** Cerca di capire il contesto prima di agire.
- **Linea 3 (六三):** Non seguire ciecamente chi non condivide i tuoi valori.
- **Linea 4 (九四):** Impara dai maestri, poi crea la tua via.
- **Linea 5 (九五):** Collaborazione equilibrata, scambio reciproco.
- **Linea 6 (上六):** Se la rotta non funziona più, cerca nuove direzioni.

═══════════════════════════════════════════════════════════════════════════════════


## 18. 蠱 Il Lavoro sul Deterioramento (Gǔ) ䷑

### Struttura
- **Trigramma Superiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Trigramma Inferiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Codifica Binaria:** 011001 (dec: 25)

### Relazioni
- **Opposto:** 17 — Il Seguimento
- **Rovesciato:** 17 — Il Seguimento
- **Nucleare:** 54 — La Ragazza che Si Sposa

### Tag
`riparazione` `rinnovamento` `correzione` `decadimento` `responsabilità` `restauro` `purificazione`

### Giudizio
Il Lavoro sul Deterioramento ha sublime riuscita. È propizio attraversare la grande acqua. Prima dell'inizio: tre giorni. Dopo l'inizio: tre giorni.

### Immagine
Ai piedi della montagna soffia il vento: l'immagine del Deterioramento. Così il nobile scuote il popolo e ne rinforza lo spirito.

### Interpretazione Moderna
Correggi errori passati e rinnova ciò che è rotto.

### Linee Mobili
- **Linea 1 (初六):** Riconosci il problema alla radice.
- **Linea 2 (九二):** Affronta il deterioramento con costanza.
- **Linea 3 (九三):** Evita soluzioni superficiali, agisci in profondità.
- **Linea 4 (六四):** Coordinati con chi può aiutarti a riparare.
- **Linea 5 (六五):** Quando la guarigione procede, rafforza il risultato.
- **Linea 6 (上九):** Non ripetere gli stessi errori.

═══════════════════════════════════════════════════════════════════════════════════


## 19. 臨 L'Avvicinamento (Lín) ䷒

### Struttura
- **Trigramma Superiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Trigramma Inferiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Codifica Binaria:** 110000 (dec: 48)

### Relazioni
- **Opposto:** 33 — La Ritirata
- **Rovesciato:** 20 — La Contemplazione
- **Nucleare:** 24 — Il Ritorno

### Tag
`espansione` `opportunità` `azione` `avvicinamento` `crescita` `apertura` `tempismo`

### Giudizio
L'Avvicinamento ha sublime riuscita. Propizia è la perseveranza. Quando giunge l'ottavo mese, c'è sciagura.

### Immagine
Al di sopra del lago c'è la terra: l'immagine dell'Avvicinamento. Così il nobile è inesauribile nel suo proposito di insegnare e illimitato nel tollerare e proteggere il popolo.

### Interpretazione Moderna
Espansione e opportunità. È il momento giusto per agire.

### Linee Mobili
- **Linea 1 (初九):** Inizia a fare passi verso l'obiettivo.
- **Linea 2 (九二):** Mostra apertura e dialogo.
- **Linea 3 (六三):** Non forzare troppo la crescita, bilancia le risorse.
- **Linea 4 (六四):** Collabora con chi ti offre chance di sviluppo.
- **Linea 5 (六五):** Fase di consolidamento prima del grande salto.
- **Linea 6 (上六):** Preparati a un cambio di rotta se necessario.

═══════════════════════════════════════════════════════════════════════════════════


## 20. 觀 La Contemplazione (Guān) ䷓

### Struttura
- **Trigramma Superiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Trigramma Inferiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Codifica Binaria:** 000011 (dec: 3)

### Relazioni
- **Opposto:** 34 — La Potenza del Grande
- **Rovesciato:** 19 — L'Avvicinamento
- **Nucleare:** 23 — Il Disgregarsi

### Tag
`osservazione` `riflessione` `contemplazione` `visione` `comprensione` `meditazione` `ispirazione`

### Giudizio
La Contemplazione. L'abluzione è avvenuta, ma non ancora l'offerta. Pieni di fiducia guardano in alto verso di lui.

### Immagine
Il vento soffia sulla terra: l'immagine della Contemplazione. Così gli antichi re visitavano le regioni del mondo, contemplavano il popolo e impartivano istruzione.

### Interpretazione Moderna
Osserva prima di agire. La comprensione profonda precede la strategia vincente.

### Linee Mobili
- **Linea 1 (初六):** Metti da parte pregiudizi, osserva con mente aperta.
- **Linea 2 (六二):** Rifletti sulle dinamiche prima di decidere.
- **Linea 3 (六三):** Non restare bloccato in troppa analisi.
- **Linea 4 (六四):** Condividi la tua visione con chi può supportarti.
- **Linea 5 (九五):** La contemplazione deve sfociare in un piano concreto.
- **Linea 6 (上九):** Se hai compreso a fondo, agisci con saggezza.

═══════════════════════════════════════════════════════════════════════════════════


## 21. 噬嗑 Il Morso che Spezza (Shì Kè) ䷔

### Struttura
- **Trigramma Superiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Trigramma Inferiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Codifica Binaria:** 100101 (dec: 37)

### Relazioni
- **Opposto:** 48 — Il Pozzo
- **Rovesciato:** 22 — La Grazia
- **Nucleare:** 39 — L'Impedimento

### Tag
`giustizia` `decisione` `fermezza` `risoluzione` `azione decisa` `legge` `chiarezza`

### Giudizio
Il Morso che Spezza ha riuscita. È propizio lasciare che la giustizia sia amministrata.

### Immagine
Tuono e lampo: l'immagine del Morso che Spezza. Così gli antichi re chiarivano le pene e rafforzavano le leggi.

### Interpretazione Moderna
A volte serve una spinta decisa per risolvere tensioni e contrasti. Agisci con fermezza e giustizia.

### Linee Mobili
- **Linea 1 (初九):** Affronta il problema all'origine, non procrastinare.
- **Linea 2 (六二):** Verifica i fatti prima di passare all'azione.
- **Linea 3 (六三):** Non eccedere nella severità, mantieni l'equilibrio.
- **Linea 4 (九四):** La chiarezza d'intenti accelera la risoluzione.
- **Linea 5 (六五):** Giustizia e compassione possono coesistere.
- **Linea 6 (上九):** Una volta risolta la tensione, evita recriminazioni.

═══════════════════════════════════════════════════════════════════════════════════


## 22. 賁 La Grazia (Bì) ䷕

### Struttura
- **Trigramma Superiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Trigramma Inferiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Codifica Binaria:** 101001 (dec: 41)

### Relazioni
- **Opposto:** 47 — L'Esaurimento
- **Rovesciato:** 21 — Il Morso che Spezza
- **Nucleare:** 40 — La Liberazione

### Tag
`bellezza` `eleganza` `forma` `armonia` `estetica` `stile` `raffinatezza`

### Giudizio
La Grazia ha riuscita. In piccole cose è propizio intraprendere qualcosa.

### Immagine
Ai piedi della montagna c'è il fuoco: l'immagine della Grazia. Così il nobile procede per schiarire le faccende correnti, ma non osa decidere in questo modo questioni controverse.

### Interpretazione Moderna
Valorizza bellezza ed eleganza. Anche i dettagli estetici favoriscono armonia e coesione.

### Linee Mobili
- **Linea 1 (初九):** Semplicità autentica, non appariscenza vuota.
- **Linea 2 (六二):** La grazia interiore conta più di quella esteriore.
- **Linea 3 (九三):** Non cedere all'estetica fine a se stessa.
- **Linea 4 (六四):** Un tocco di stile può risolvere tensioni.
- **Linea 5 (六五):** Armonizza forma e sostanza.
- **Linea 6 (上九):** Resta fedele ai valori anche nella bellezza.

═══════════════════════════════════════════════════════════════════════════════════


## 23. 剝 Il Disgregarsi (Bō) ䷖

### Struttura
- **Trigramma Superiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Trigramma Inferiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Codifica Binaria:** 000001 (dec: 1)

### Relazioni
- **Opposto:** 43 — Lo Straripamento
- **Rovesciato:** 24 — Il Ritorno
- **Nucleare:** 2 — Il Ricettivo

### Tag
`disgregazione` `instabilità` `transizione` `smantellamento` `accettazione` `crisi` `trasformazione`

### Giudizio
Il Disgregarsi. Non è propizio andare in alcun luogo.

### Immagine
La montagna poggia sulla terra: l'immagine del Disgregarsi. Così quelli in alto possono assicurare la loro posizione solo mediante munificenza verso quelli in basso.

### Interpretazione Moderna
Fase di smantellamento e instabilità. Accetta la transizione e prepara la ricostruzione.

### Linee Mobili
- **Linea 1 (初六):** Se le fondamenta cedono, agisci subito.
- **Linea 2 (六二):** Non farti travolgere, conserva ciò che vale.
- **Linea 3 (六三):** Attenzione a chi cerca di sfruttare la crisi.
- **Linea 4 (六四):** Riduci al minimo le perdite.
- **Linea 5 (六五):** Sii pronto a ricostruire su nuove basi.
- **Linea 6 (上九):** Dopo la disgregazione, il cambiamento è necessario.

═══════════════════════════════════════════════════════════════════════════════════


## 24. 復 Il Ritorno (Fù) ䷗

### Struttura
- **Trigramma Superiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Trigramma Inferiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Codifica Binaria:** 100000 (dec: 32)

### Relazioni
- **Opposto:** 44 — Il Farsi Incontro
- **Rovesciato:** 23 — Il Disgregarsi
- **Nucleare:** 2 — Il Ricettivo

### Tag
`ritorno` `rinascita` `rinnovo` `ciclo` `ricominciare` `essenza` `svolta`

### Giudizio
Il Ritorno. Riuscita. Uscita e ingresso senza errore. Amici vengono senza macchia. La via va e viene. Al settimo giorno viene il ritorno. È propizio avere dove andare.

### Immagine
Il tuono dentro la terra: l'immagine del Ritorno. Così gli antichi re al solstizio d'inverno chiudevano i passi. Mercanti e viandanti non si spostavano, e il sovrano non visitava le regioni.

### Interpretazione Moderna
Rientro graduale su un percorso positivo. Ritorna all'essenza, recupera energie e obiettivi.

### Linee Mobili
- **Linea 1 (初九):** Avvio del ritorno, fai il primo passo con fiducia.
- **Linea 2 (六二):** Se hai deviato, correggi la rotta senza timori.
- **Linea 3 (六三):** Non ripetere vecchi errori, agisci su basi rinnovate.
- **Linea 4 (六四):** Ritrova alleati e relazioni autentiche.
- **Linea 5 (六五):** Usa il ritorno per imparare dal passato.
- **Linea 6 (上六):** Il ritorno si compie; non guardare indietro con rimpianto.

═══════════════════════════════════════════════════════════════════════════════════


## 25. 無妄 L'Innocenza (Wú Wàng) ䷘

### Struttura
- **Trigramma Superiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Trigramma Inferiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Codifica Binaria:** 100111 (dec: 39)

### Relazioni
- **Opposto:** 46 — L'Ascendere
- **Rovesciato:** 26 — La Forza Domatrice del Grande
- **Nucleare:** 53 — Lo Sviluppo

### Tag
`innocenza` `sincerità` `autenticità` `spontaneità` `purezza` `verità` `naturalezza`

### Giudizio
L'Innocenza. Sublime riuscita. Propizia è la perseveranza. Chi non è com'è, ha sciagura, e non è propizio intraprendere alcunché.

### Immagine
Sotto il cielo scorre il tuono. Tutte le cose raggiungono lo stato naturale dell'innocenza. Così gli antichi re, ricchi di virtù e in armonia con il tempo, nutrivano tutti gli esseri.

### Interpretazione Moderna
Sincerità e autenticità portano chiarezza. Agisci con spontaneità, senza secondi fini.

### Linee Mobili
- **Linea 1 (初九):** Mantieni cuore puro all'inizio, evita calcoli eccessivi.
- **Linea 2 (六二):** Se sei sincero, attrarrai sostegno.
- **Linea 3 (六三):** Non trasformare l'innocenza in ingenuità.
- **Linea 4 (九四):** Proteggi la tua genuinità dai cinismi esterni.
- **Linea 5 (九五):** Onestà e trasparenza costruiscono fiducia.
- **Linea 6 (上九):** Non abusare della fiducia altrui.

═══════════════════════════════════════════════════════════════════════════════════


## 26. 大畜 La Forza Domatrice del Grande (Dà Chù) ䷙

### Struttura
- **Trigramma Superiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Trigramma Inferiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Codifica Binaria:** 111001 (dec: 57)

### Relazioni
- **Opposto:** 45 — La Raccolta
- **Rovesciato:** 25 — L'Innocenza
- **Nucleare:** 54 — La Ragazza che Si Sposa

### Tag
`contenimento` `accumulo` `strategia` `potenza` `controllo` `saggezza` `riserva`

### Giudizio
La Forza Domatrice del Grande. Propizia è la perseveranza. Non mangiare in casa reca salute. È propizio attraversare la grande acqua.

### Immagine
Il cielo dentro la montagna: l'immagine della Forza Domatrice del Grande. Così il nobile apprende le parole e le gesta del passato, per rafforzare il suo carattere.

### Interpretazione Moderna
Trattenere l'energia per un uso mirato. Crea una strategia prima di sprigionare la tua potenza.

### Linee Mobili
- **Linea 1 (初九):** Non dissipare le tue forze in inizi inutili.
- **Linea 2 (九二):** Canalizza l'energia in obiettivi precisi.
- **Linea 3 (九三):** Evita esplosioni incontrollate, resta focalizzato.
- **Linea 4 (六四):** Preparati a un salto qualitativo.
- **Linea 5 (六五):** Grande potere gestito con saggezza.
- **Linea 6 (上九):** Non trattenere troppo a lungo, l'energia va rilasciata.

═══════════════════════════════════════════════════════════════════════════════════


## 27. 頤 Gli Angoli della Bocca (Yí) ䷚

### Struttura
- **Trigramma Superiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Trigramma Inferiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Codifica Binaria:** 100001 (dec: 33)

### Relazioni
- **Opposto:** 28 — La Preponderanza del Grande
- **Rovesciato:** 27 — Gli Angoli della Bocca (palindromo)
- **Nucleare:** 2 — Il Ricettivo

### Tag
`nutrimento` `cura` `alimentazione` `corpo` `mente` `spirito` `sostentamento`

### Giudizio
Gli Angoli della Bocca. Perseveranza reca salute. Osserva la nutrizione, e ciò di cui una persona cerca di riempire la propria bocca.

### Immagine
Ai piedi della montagna scorre il tuono: l'immagine della Nutrizione. Così il nobile fa attenzione alle sue parole ed è temperante nel mangiare e nel bere.

### Interpretazione Moderna
Nutrimento e cura, sia fisica che spirituale. Ciò che introduci (idee, cibo, energie) influisce sul tuo essere.

### Linee Mobili
- **Linea 1 (初九):** Curare la base: corpo e mente.
- **Linea 2 (六二):** Cerca risorse sane, evita eccessi.
- **Linea 3 (六三):** Non ingurgitare ciecamente informazioni o sostanze.
- **Linea 4 (六四):** Condividi nutrimento e conoscenza.
- **Linea 5 (六五):** Una dieta equilibrata crea stabilità.
- **Linea 6 (上九):** Evita l'avidità, coltiva generosità.

═══════════════════════════════════════════════════════════════════════════════════


## 28. 大過 La Preponderanza del Grande (Dà Guò) ䷛

### Struttura
- **Trigramma Superiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Trigramma Inferiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Codifica Binaria:** 011110 (dec: 30)

### Relazioni
- **Opposto:** 27 — Gli Angoli della Bocca
- **Rovesciato:** 28 — La Preponderanza del Grande (palindromo)
- **Nucleare:** 1 — Il Creativo

### Tag
`eccesso` `sovraccarico` `responsabilità` `pressione` `transizione critica` `peso` `riorganizzazione`

### Giudizio
La Preponderanza del Grande. La trave maestra si incurva fino al punto di rottura. È propizio avere dove andare. Riuscita.

### Immagine
Il lago sommerge gli alberi: l'immagine della Preponderanza del Grande. Così il nobile, quando sta solo, è senza preoccupazioni, e se deve rinunciare al mondo, è imperterrito.

### Interpretazione Moderna
Situazione carica di responsabilità. Se il peso è eccessivo, crea sostegni o riorganizza le risorse.

### Linee Mobili
- **Linea 1 (初六):** Se senti troppo carico, chiedi aiuto.
- **Linea 2 (九二):** Delegare con saggezza evita il collasso.
- **Linea 3 (九三):** Non ignorare i segnali di stress eccessivo.
- **Linea 4 (九四):** Rafforza la struttura prima che ceda.
- **Linea 5 (九五):** La leadership richiede stabilità.
- **Linea 6 (上六):** Un eccesso di peso può spezzare ogni equilibrio.

═══════════════════════════════════════════════════════════════════════════════════


## 29. 坎 L'Abissale (Kǎn) ䷜

### Struttura
- **Trigramma Superiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Trigramma Inferiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Codifica Binaria:** 010010 (dec: 18)

### Relazioni
- **Opposto:** 30 — L'Aderente
- **Rovesciato:** 29 — L'Abissale (palindromo)
- **Nucleare:** 27 — Gli Angoli della Bocca

### Tag
`pericolo` `abisso` `sfida` `profondità` `perseveranza` `acqua` `coraggio`

### Giudizio
L'Abissale ripetuto. Se sei veritiero hai riuscita nel cuore, e ciò che fai ha riuscita.

### Immagine
L'acqua fluisce e raggiunge la meta: l'immagine dell'Abissale ripetuto. Così il nobile cammina in costante virtù e pratica l'insegnamento.

### Interpretazione Moderna
Fase di pericolo o complessità. Mantieni la calma e affronta gli ostacoli uno alla volta.

### Linee Mobili
- **Linea 1 (初六):** Non farti travolgere dalle paure iniziali.
- **Linea 2 (九二):** Fiducia e perseveranza anche nel buio.
- **Linea 3 (六三):** Evita l'ostinazione in situazioni critiche.
- **Linea 4 (六四):** Alleati con chi sa nuotare in acque tempestose.
- **Linea 5 (九五):** Mantieni la rotta, la fine dell'abisso arriverà.
- **Linea 6 (上六):** Superata la prova, ricorda cosa hai imparato.

═══════════════════════════════════════════════════════════════════════════════════


## 30. 離 L'Aderente (Lí) ䷝

### Struttura
- **Trigramma Superiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Trigramma Inferiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Codifica Binaria:** 101101 (dec: 45)

### Relazioni
- **Opposto:** 29 — L'Abissale
- **Rovesciato:** 30 — L'Aderente (palindromo)
- **Nucleare:** 28 — La Preponderanza del Grande

### Tag
`fuoco` `chiarezza` `passione` `illuminazione` `visione` `aderenza` `luce`

### Giudizio
L'Aderente. Propizia è la perseveranza. Essa reca riuscita. Curare la vacca reca salute.

### Immagine
La chiarezza si leva due volte: l'immagine del Fuoco. Così il grande uomo, perpetuando questa chiarezza, illumina le quattro regioni del mondo.

### Interpretazione Moderna
Passione e illuminazione. Segui la tua visione con intensità, ma gestisci bene la tua energia.

### Linee Mobili
- **Linea 1 (初九):** L'inizio del fuoco va sorvegliato, per evitare incendi.
- **Linea 2 (六二):** Alimenta la fiamma con costanza, non con esplosioni.
- **Linea 3 (九三):** Troppa irruenza può bruciare opportunità.
- **Linea 4 (九四):** Usa la luce per fare chiarezza, ma non accecare gli altri.
- **Linea 5 (六五):** Il calore giusto scalda e ispira.
- **Linea 6 (上九):** Se il fuoco divampa, trova un modo per contenerlo.

═══════════════════════════════════════════════════════════════════════════════════


## 31. 咸 L'Attrazione (Xián) ䷞

### Struttura
- **Trigramma Superiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Trigramma Inferiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Codifica Binaria:** 001110 (dec: 14)

### Relazioni
- **Opposto:** 41 — La Diminuzione
- **Rovesciato:** 32 — La Durata
- **Nucleare:** 44 — Il Farsi Incontro

### Tag
`attrazione` `influenza` `sintonia` `relazione` `reciprocità` `empatia` `connessione`

### Giudizio
L'Attrazione. Riuscita. Propizia è la perseveranza. Prendere in moglie una fanciulla reca salute.

### Immagine
Sulla montagna c'è un lago: l'immagine dell'Attrazione. Così il nobile, in virtù della sua apertura, accoglie gli uomini.

### Interpretazione Moderna
Influenza reciproca e sintonia. Coltiva relazioni positive e collabora per un vantaggio comune.

### Linee Mobili
- **Linea 1 (初六):** Un primo contatto sincero crea fiducia.
- **Linea 2 (六二):** Non manipolare i sentimenti altrui.
- **Linea 3 (九三):** L'attrazione deve essere reciproca e genuina.
- **Linea 4 (九四):** Costruisci un legame su valori condivisi.
- **Linea 5 (九五):** Apriti all'empatia e alla comprensione.
- **Linea 6 (上六):** Evita dipendenze emotive o relazionali.

═══════════════════════════════════════════════════════════════════════════════════


## 32. 恆 La Durata (Héng) ䷟

### Struttura
- **Trigramma Superiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Trigramma Inferiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Codifica Binaria:** 011100 (dec: 28)

### Relazioni
- **Opposto:** 42 — L'Accrescimento
- **Rovesciato:** 31 — L'Attrazione
- **Nucleare:** 43 — Lo Straripamento

### Tag
`durata` `perseveranza` `costanza` `stabilità` `coerenza` `continuità` `fedeltà`

### Giudizio
La Durata. Riuscita. Nessuna macchia. Propizia è la perseveranza. È propizio avere dove andare.

### Immagine
Tuono e vento: l'immagine della Durata. Così il nobile sta saldo e non cambia direzione.

### Interpretazione Moderna
Stabilità e perseveranza nel tempo. Se la direzione è giusta, insisti con coerenza.

### Linee Mobili
- **Linea 1 (初六):** Poniti basi solide fin dall'inizio.
- **Linea 2 (九二):** Non scoraggiarti per piccoli ritardi.
- **Linea 3 (九三):** Evita cambi di rotta continui, mantieni la costanza.
- **Linea 4 (九四):** Aggiorna la strategia senza tradire i principi.
- **Linea 5 (六五):** Riconosci i risultati raggiunti, ma continua.
- **Linea 6 (上六):** Troppa rigidità può essere controproducente.

═══════════════════════════════════════════════════════════════════════════════════


## 33. 遯 La Ritirata (Dùn) ䷠

### Struttura
- **Trigramma Superiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Trigramma Inferiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Codifica Binaria:** 001111 (dec: 15)

### Relazioni
- **Opposto:** 19 — L'Avvicinamento
- **Rovesciato:** 34 — La Potenza del Grande
- **Nucleare:** 44 — Il Farsi Incontro

### Tag
`ritirata` `strategia` `distacco` `prudenza` `preparazione` `saggezza` `arretramento`

### Giudizio
La Ritirata. Riuscita. In piccole cose è propizia la perseveranza.

### Immagine
Sotto il cielo c'è la montagna: l'immagine della Ritirata. Così il nobile tiene a distanza l'uomo inferiore, non con ira ma con riserbo.

### Interpretazione Moderna
In certi casi, ritirarsi è una mossa strategica. Allontanati dal conflitto per preparare il passo successivo.

### Linee Mobili
- **Linea 1 (初六):** Riconosci i segnali prima di rimanere intrappolato.
- **Linea 2 (六二):** Non ritirarti per paura, ma per scelta.
- **Linea 3 (九三):** Pianifica il ritiro in modo ordinato, senza caos.
- **Linea 4 (九四):** Usa il tempo guadagnato per riorganizzarti.
- **Linea 5 (九五):** Un ritiro dignitoso può prevenire disastri.
- **Linea 6 (上九):** Conclusa la ritirata, valuta come ripartire.

═══════════════════════════════════════════════════════════════════════════════════


## 34. 大壯 La Potenza del Grande (Dà Zhuàng) ䷡

### Struttura
- **Trigramma Superiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Trigramma Inferiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Codifica Binaria:** 111100 (dec: 60)

### Relazioni
- **Opposto:** 20 — La Contemplazione
- **Rovesciato:** 33 — La Ritirata
- **Nucleare:** 43 — Lo Straripamento

### Tag
`potenza` `forza` `leadership` `etica` `rispetto` `grandezza` `autorità`

### Giudizio
La Potenza del Grande. Propizia è la perseveranza.

### Immagine
Il tuono alto nel cielo: l'immagine della Potenza del Grande. Così il nobile non calca un sentiero che non corrisponda all'ordine.

### Interpretazione Moderna
Forza manifesta e leadership. Usa il tuo potere con etica e rispetto.

### Linee Mobili
- **Linea 1 (初九):** Non ostentare forza quando non necessario.
- **Linea 2 (九二):** Fonda la potenza su principi saldi.
- **Linea 3 (九三):** Evita imposizioni brutali, cerca l'adesione.
- **Linea 4 (九四):** Una leadership illuminata ottiene fiducia.
- **Linea 5 (六五):** Dimostra fermezza nel rispetto degli altri.
- **Linea 6 (上六):** La potenza eccessiva può portare a resistenze.

═══════════════════════════════════════════════════════════════════════════════════


## 35. 晉 Il Progresso (Jìn) ䷢

### Struttura
- **Trigramma Superiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Trigramma Inferiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Codifica Binaria:** 000101 (dec: 5)

### Relazioni
- **Opposto:** 5 — L'Attesa
- **Rovesciato:** 36 — L'Ottenebramento della Luce
- **Nucleare:** 39 — L'Impedimento

### Tag
`progresso` `avanzamento` `successo` `fiducia` `obiettivi` `luce` `promozione`

### Giudizio
Il Progresso. Il potente principe viene onorato con cavalli in gran numero. In un singolo giorno è ricevuto tre volte in udienza.

### Immagine
Il sole si leva sopra la terra: l'immagine del Progresso. Così il nobile illumina egli stesso le sue luminose virtù.

### Interpretazione Moderna
Avanzamento costante e miglioramento. Definisci obiettivi chiari e affrontali con fiducia.

### Linee Mobili
- **Linea 1 (初六):** Inizia con slancio, ma pianifica i passi.
- **Linea 2 (六二):** Cerca alleanze che condividano la tua visione.
- **Linea 3 (六三):** Non lasciarti distrarre dal timore di fallire.
- **Linea 4 (九四):** Ogni traguardo intermedio va consolidato.
- **Linea 5 (六五):** Celebra i successi, ma resta concentrato.
- **Linea 6 (上九):** Se il progresso rallenta, rivaluta la strategia.

═══════════════════════════════════════════════════════════════════════════════════


## 36. 明夷 L'Ottenebramento della Luce (Míng Yí) ䷣

### Struttura
- **Trigramma Superiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Trigramma Inferiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Codifica Binaria:** 101000 (dec: 40)

### Relazioni
- **Opposto:** 6 — Il Conflitto
- **Rovesciato:** 35 — Il Progresso
- **Nucleare:** 40 — La Liberazione

### Tag
`oscurità` `protezione` `resilienza` `astuzia` `speranza` `luce interiore` `avversità`

### Giudizio
L'Ottenebramento della Luce. Nelle avversità è propizio essere perseveranti.

### Immagine
La luce è sprofondata nella terra: l'immagine dell'Ottenebramento della Luce. Così il nobile vive con la grande moltitudine: vela il suo splendore eppure rimane luminoso.

### Interpretazione Moderna
Temporanea oscurità o ostacoli esterni. Proteggi la tua luce interiore, presto tornerà a splendere.

### Linee Mobili
- **Linea 1 (初九):** Non disperare alle prime ombre.
- **Linea 2 (六二):** Conserva la speranza in una fase difficile.
- **Linea 3 (九三):** Evita scontri diretti se sei in svantaggio.
- **Linea 4 (六四):** Coltiva la luce dentro di te, in attesa.
- **Linea 5 (六五):** Usa l'astuzia se la forza non basta.
- **Linea 6 (上六):** La luce riemergerà; abbi fiducia.

═══════════════════════════════════════════════════════════════════════════════════


## 37. 家人 La Casata (Jiā Rén) ䷤

### Struttura
- **Trigramma Superiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Trigramma Inferiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Codifica Binaria:** 101011 (dec: 43)

### Relazioni
- **Opposto:** 40 — La Liberazione
- **Rovesciato:** 38 — L'Opposizione
- **Nucleare:** 64 — Prima del Compimento

### Tag
`famiglia` `coesione` `ruoli` `valori` `organizzazione` `relazioni` `armonia domestica`

### Giudizio
La Casata. Propizia è la perseveranza della donna.

### Immagine
Il vento esce dal fuoco: l'immagine della Casata. Così il nobile ha sostanza nelle sue parole e durata nella sua condotta di vita.

### Interpretazione Moderna
Coesione familiare o di gruppo. Organizza e fai leva sui valori comuni per rafforzare le relazioni.

### Linee Mobili
- **Linea 1 (初九):** Cura le basi affettive e organizzative.
- **Linea 2 (六二):** Rispetta i ruoli e le competenze.
- **Linea 3 (九三):** Evita gerarchie oppressive, favorisci collaborazione.
- **Linea 4 (六四):** Un clima sereno aumenta la produttività.
- **Linea 5 (九五):** Valori condivisi uniscono il gruppo.
- **Linea 6 (上九):** Non trascurare la dimensione emotiva.

═══════════════════════════════════════════════════════════════════════════════════


## 38. 睽 L'Opposizione (Kuí) ䷥

### Struttura
- **Trigramma Superiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Trigramma Inferiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Codifica Binaria:** 110101 (dec: 53)

### Relazioni
- **Opposto:** 39 — L'Impedimento
- **Rovesciato:** 37 — La Casata
- **Nucleare:** 63 — Dopo il Compimento

### Tag
`opposizione` `contrasto` `divergenza` `mediazione` `rispetto` `dualità` `tensione`

### Giudizio
L'Opposizione. In piccole cose, salute.

### Immagine
In alto il fuoco, in basso il lago: l'immagine dell'Opposizione. Così il nobile, in mezzo a tutte le comunanze, mantiene la sua individualità.

### Interpretazione Moderna
Differenze inconciliabili o visioni opposte. Rispetta i contrasti e cerca un terreno neutro se possibile.

### Linee Mobili
- **Linea 1 (初九):** Non esasperare le divergenze.
- **Linea 2 (九二):** Ascolta il punto di vista altrui.
- **Linea 3 (六三):** Se il conflitto è insanabile, mantieni dignità.
- **Linea 4 (九四):** Prova a trovare un punto comune.
- **Linea 5 (六五):** La mediazione richiede pazienza.
- **Linea 6 (上九):** A volte è necessario accettare la distanza.

═══════════════════════════════════════════════════════════════════════════════════


## 39. 蹇 L'Impedimento (Jiǎn) ䷦

### Struttura
- **Trigramma Superiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Trigramma Inferiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Codifica Binaria:** 001010 (dec: 10)

### Relazioni
- **Opposto:** 38 — L'Opposizione
- **Rovesciato:** 40 — La Liberazione
- **Nucleare:** 64 — Prima del Compimento

### Tag
`ostacolo` `blocco` `alternativa` `alleanza` `cambio prospettiva` `impedimento` `sfida`

### Giudizio
L'Impedimento. È propizio il sud-ovest. Non è propizio il nord-est. È propizio vedere il grande uomo. La perseveranza reca salute.

### Immagine
Sulla montagna c'è l'acqua: l'immagine dell'Impedimento. Così il nobile volge la propria persona verso l'interno e coltiva la sua virtù.

### Interpretazione Moderna
Blocco su un percorso. Cambia prospettiva o alleati con altri per superare lo stallo.

### Linee Mobili
- **Linea 1 (初六):** Individua la natura del blocco.
- **Linea 2 (六二):** Non scoraggiarti, cerca soluzioni creative.
- **Linea 3 (九三):** Non combattere gli ostacoli frontalmente se non serve.
- **Linea 4 (六四):** Trova un aiuto esterno.
- **Linea 5 (九五):** Sfrutta la pausa per rivedere il piano.
- **Linea 6 (上六):** Superato l'impedimento, concentra gli sforzi.

═══════════════════════════════════════════════════════════════════════════════════


## 40. 解 La Liberazione (Xiè) ䷧

### Struttura
- **Trigramma Superiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Trigramma Inferiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Codifica Binaria:** 010100 (dec: 20)

### Relazioni
- **Opposto:** 37 — La Casata
- **Rovesciato:** 39 — L'Impedimento
- **Nucleare:** 63 — Dopo il Compimento

### Tag
`liberazione` `sollievo` `rinnovamento` `azione rapida` `perdono` `nuovo inizio` `scioglimento`

### Giudizio
La Liberazione. Il sud-ovest è propizio. Se non c'è più alcun luogo dove andare, il ritorno reca salute. Se c'è ancora un luogo dove andare, la rapidità reca salute.

### Immagine
Tuono e pioggia si sciolgono: l'immagine della Liberazione. Così il nobile perdona gli errori e rimette le colpe.

### Interpretazione Moderna
Dopo le tensioni, arriva la soluzione. Agisci con prontezza e lascia andare il peso del passato.

### Linee Mobili
- **Linea 1 (初六):** Sciogli le prime catene, inizia il rilascio.
- **Linea 2 (九二):** Fai chiarezza sui tuoi obiettivi.
- **Linea 3 (六三):** Non tornare a condizioni che ti opprimono.
- **Linea 4 (九四):** Approfitta della libertà per riorganizzarti.
- **Linea 5 (六五):** Accompagna la liberazione con il rinnovamento.
- **Linea 6 (上六):** Trasforma la vittoria in un nuovo inizio.

═══════════════════════════════════════════════════════════════════════════════════


## 41. 損 La Diminuzione (Sǔn) ䷨

### Struttura
- **Trigramma Superiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Trigramma Inferiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Codifica Binaria:** 110001 (dec: 49)

### Relazioni
- **Opposto:** 31 — L'Attrazione
- **Rovesciato:** 42 — L'Accrescimento
- **Nucleare:** 24 — Il Ritorno

### Tag
`riduzione` `essenzialità` `minimalismo` `efficienza` `sacrificio` `semplicità` `economia`

### Giudizio
La Diminuzione. Se sei veritiero, sublime salute senza macchia. Si può essere perseveranti. È propizio intraprendere qualcosa. Come compierlo? Due piccole ciotole possono essere usate per il sacrificio.

### Immagine
Ai piedi della montagna c'è il lago: l'immagine della Diminuzione. Così il nobile frena la sua ira e reprime i suoi istinti.

### Interpretazione Moderna
Taglia il superfluo e riduci gli eccessi. Un approccio minimalista ti rafforza.

### Linee Mobili
- **Linea 1 (初九):** Parti dalle spese e risorse meno utili.
- **Linea 2 (九二):** Non confondere essenzialità con povertà.
- **Linea 3 (六三):** Bilancia la rinuncia con la necessità.
- **Linea 4 (六四):** Una riduzione mirata genera efficienza.
- **Linea 5 (六五):** Comunica chiaramente i motivi della riduzione.
- **Linea 6 (上九):** Diminuisci per crescere in modo sostenibile.

═══════════════════════════════════════════════════════════════════════════════════


## 42. 益 L'Accrescimento (Yì) ䷩

### Struttura
- **Trigramma Superiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Trigramma Inferiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Codifica Binaria:** 100011 (dec: 35)

### Relazioni
- **Opposto:** 32 — La Durata
- **Rovesciato:** 41 — La Diminuzione
- **Nucleare:** 23 — Il Disgregarsi

### Tag
`crescita` `investimento` `opportunità` `espansione` `generosità` `sviluppo` `beneficio`

### Giudizio
L'Accrescimento. È propizio intraprendere qualcosa. È propizio attraversare la grande acqua.

### Immagine
Vento e tuono: l'immagine dell'Accrescimento. Così il nobile, quando vede il bene, lo imita; quando ha dei difetti, se ne libera.

### Interpretazione Moderna
Investire e aumentare le risorse. Sfrutta le opportunità di crescita con prudenza e impegno.

### Linee Mobili
- **Linea 1 (初九):** Inizia con piccoli incrementi.
- **Linea 2 (六二):** Diversifica gli investimenti.
- **Linea 3 (六三):** Evita crescite troppo repentine e instabili.
- **Linea 4 (六四):** Collabora con chi può potenziare i tuoi sforzi.
- **Linea 5 (九五):** Mantieni una visione a lungo termine.
- **Linea 6 (上九):** L'accrescimento eccessivo può essere controproducente.

═══════════════════════════════════════════════════════════════════════════════════


## 43. 夬 Lo Straripamento (Guài) ䷪

### Struttura
- **Trigramma Superiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Trigramma Inferiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Codifica Binaria:** 111110 (dec: 62)

### Relazioni
- **Opposto:** 23 — Il Disgregarsi
- **Rovesciato:** 44 — Il Farsi Incontro
- **Nucleare:** 1 — Il Creativo

### Tag
`determinazione` `rottura` `decisione` `affermazione` `superamento` `barriera` `svolta`

### Giudizio
Lo Straripamento. Bisogna annunciare la cosa con risolutezza alla corte del re. Sia proclamata in verità. Pericolo. È necessario avvertire la propria città. Non è propizio ricorrere alle armi. È propizio intraprendere qualcosa.

### Immagine
Il lago è salito al cielo: l'immagine dello Straripamento. Così il nobile dispensa ricchezze verso il basso e rifugge dal riposare sulla sua virtù.

### Interpretazione Moderna
Necessità di affermarsi e rompere le barriere. Agisci con decisione, ma mantieni lucidità.

### Linee Mobili
- **Linea 1 (初九):** Identifica ciò che ti frena e agisci.
- **Linea 2 (九二):** Non farti travolgere da un impulso distruttivo.
- **Linea 3 (九三):** La chiarezza d'obiettivo riduce i rischi.
- **Linea 4 (九四):** Unisci forze per superare ostacoli.
- **Linea 5 (九五):** Non abusare del tuo slancio.
- **Linea 6 (上六):** Dopo aver straripato, riporta l'ordine.

═══════════════════════════════════════════════════════════════════════════════════


## 44. 姤 Il Farsi Incontro (Gòu) ䷫

### Struttura
- **Trigramma Superiore:** ☰ Cielo (Qián) — Forza, Creatività | Metallo
- **Trigramma Inferiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Codifica Binaria:** 011111 (dec: 31)

### Relazioni
- **Opposto:** 24 — Il Ritorno
- **Rovesciato:** 43 — Lo Straripamento
- **Nucleare:** 1 — Il Creativo

### Tag
`incontro` `imprevisto` `opportunità` `valutazione` `cautela` `novità` `sorpresa`

### Giudizio
Il Farsi Incontro. La fanciulla è potente. Non bisogna sposare una tale fanciulla.

### Immagine
Sotto il cielo c'è il vento: l'immagine del Farsi Incontro. Così il principe, nel diffondere i suoi ordini, si rivolge a tutte le regioni.

### Interpretazione Moderna
Arrivo di un fattore imprevisto. Potrebbe essere un'opportunità o una sfida; valuta con attenzione.

### Linee Mobili
- **Linea 1 (初六):** Preparati all'imprevisto con mentalità aperta.
- **Linea 2 (九二):** Non respingere subito l'elemento nuovo.
- **Linea 3 (九三):** Se è rischioso, gestiscilo con cautela.
- **Linea 4 (九四):** Un incontro fortunato può portare grandi cambiamenti.
- **Linea 5 (九五):** Evita di farti soggiogare dalle novità.
- **Linea 6 (上九):** Se non si integra, meglio congedarlo.

═══════════════════════════════════════════════════════════════════════════════════


## 45. 萃 La Raccolta (Cuì) ䷬

### Struttura
- **Trigramma Superiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Trigramma Inferiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Codifica Binaria:** 000110 (dec: 6)

### Relazioni
- **Opposto:** 26 — La Forza Domatrice del Grande
- **Rovesciato:** 46 — L'Ascendere
- **Nucleare:** 53 — Lo Sviluppo

### Tag
`raccolta` `unità` `obiettivo` `convergenza` `risorse` `comunità` `concentrazione`

### Giudizio
La Raccolta. Riuscita. Il re si avvicina al suo tempio. È propizio vedere il grande uomo. Questo reca riuscita. Propizia è la perseveranza. Portare grandi offerte crea salute. È propizio intraprendere qualcosa.

### Immagine
Sulla terra c'è il lago: l'immagine della Raccolta. Così il nobile rinnova le sue armi per affrontare l'imprevisto.

### Interpretazione Moderna
Radunare persone e risorse intorno a un obiettivo. L'unità fa la forza.

### Linee Mobili
- **Linea 1 (初六):** Inizia coinvolgendo chi ti è più vicino.
- **Linea 2 (六二):** Crea un obiettivo chiaro e condiviso.
- **Linea 3 (六三):** Evita la frammentazione di interessi.
- **Linea 4 (九四):** Premia chi contribuisce attivamente.
- **Linea 5 (九五):** Mantieni coesione con comunicazione continua.
- **Linea 6 (上六):** Una raccolta ben strutturata produce risultati duraturi.

═══════════════════════════════════════════════════════════════════════════════════


## 46. 升 L'Ascendere (Shēng) ䷭

### Struttura
- **Trigramma Superiore:** ☷ Terra (Kūn) — Ricettività, Devozione | Terra
- **Trigramma Inferiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Codifica Binaria:** 011000 (dec: 24)

### Relazioni
- **Opposto:** 25 — L'Innocenza
- **Rovesciato:** 45 — La Raccolta
- **Nucleare:** 54 — La Ragazza che Si Sposa

### Tag
`ascesa` `progresso` `crescita graduale` `consolidamento` `determinazione` `scalata` `avanzamento`

### Giudizio
L'Ascendere ha sublime riuscita. Bisogna vedere il grande uomo. Non temere! Una spedizione verso sud reca salute.

### Immagine
Dentro la terra cresce il legno: l'immagine dell'Ascendere. Così il nobile, con devozione e dedizione, accumula piccole cose per farne di elevate e grandi.

### Interpretazione Moderna
Graduale ascesa e progresso sicuro. Ogni passo consolidato ti avvicina alla vetta.

### Linee Mobili
- **Linea 1 (初六):** Fai il primo gradino con determinazione.
- **Linea 2 (九二):** Non trascurare i dettagli mentre sali.
- **Linea 3 (九三):** Evita salti troppo ampi, rischi di cadere.
- **Linea 4 (六四):** Chiedi supporto a chi è già più in alto.
- **Linea 5 (六五):** Consolidare ogni tappa rafforza il percorso.
- **Linea 6 (上六):** Raggiunta la vetta, valuta come proseguire.

═══════════════════════════════════════════════════════════════════════════════════


## 47. 困 L'Esaurimento (Kùn) ䷮

### Struttura
- **Trigramma Superiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Trigramma Inferiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Codifica Binaria:** 010110 (dec: 22)

### Relazioni
- **Opposto:** 22 — La Grazia
- **Rovesciato:** 48 — Il Pozzo
- **Nucleare:** 37 — La Casata

### Tag
`esaurimento` `oppressione` `recupero` `priorità` `resilienza` `stanchezza` `resistenza`

### Giudizio
L'Esaurimento. Riuscita. Perseveranza. Il grande uomo opera salute. Nessuna macchia. Se uno ha qualcosa da dire, non gli si crede.

### Immagine
Nel lago non c'è acqua: l'immagine dell'Esaurimento. Così il nobile mette in gioco la sua vita per seguire la sua volontà.

### Interpretazione Moderna
Sensazione di oppressione o mancanza di forze. Focalizzati sul recupero e sulla definizione di priorità.

### Linee Mobili
- **Linea 1 (初六):** Riconosci la stanchezza e concediti una pausa.
- **Linea 2 (九二):** Non perdere la speranza, cerca sostegno.
- **Linea 3 (六三):** Evita di incupirti nella sfiducia.
- **Linea 4 (九四):** Un piccolo aiuto può riaccendere energie.
- **Linea 5 (九五):** Riorganizza i tuoi obiettivi.
- **Linea 6 (上六):** Dopo l'esaurimento, riparti con slancio nuovo.

═══════════════════════════════════════════════════════════════════════════════════


## 48. 井 Il Pozzo (Jǐng) ䷯

### Struttura
- **Trigramma Superiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Trigramma Inferiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Codifica Binaria:** 011010 (dec: 26)

### Relazioni
- **Opposto:** 21 — Il Morso che Spezza
- **Rovesciato:** 47 — L'Esaurimento
- **Nucleare:** 38 — L'Opposizione

### Tag
`fonte` `radici` `valori` `essenza` `profondità` `risorsa` `tradizione`

### Giudizio
Il Pozzo. Si può cambiare la città, ma non si può cambiare il pozzo. Esso non diminuisce né aumenta. Vengono e vanno ad attingere al pozzo.

### Immagine
Sopra il legno c'è l'acqua: l'immagine del Pozzo. Così il nobile incoraggia il popolo al lavoro e lo esorta ad aiutarsi reciprocamente.

### Interpretazione Moderna
La fonte vitale, le radici profonde. Ricorda i tuoi valori essenziali e attingi a essi.

### Linee Mobili
- **Linea 1 (初六):** Se il pozzo è secco, ripulisci le fondamenta.
- **Linea 2 (九二):** Mantieni accessibile la tua fonte interiore.
- **Linea 3 (九三):** Evita sprechi, conserva ciò che è prezioso.
- **Linea 4 (六四):** Condividi l'acqua con chi ne ha bisogno.
- **Linea 5 (九五):** La profondità del pozzo riflette la tua.
- **Linea 6 (上六):** Non dimenticare di rinnovarlo regolarmente.

═══════════════════════════════════════════════════════════════════════════════════


## 49. 革 Il Sovvertimento (Gé) ䷰

### Struttura
- **Trigramma Superiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Trigramma Inferiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Codifica Binaria:** 101110 (dec: 46)

### Relazioni
- **Opposto:** 4 — L'Inesperienza
- **Rovesciato:** 50 — Il Crogiolo
- **Nucleare:** 44 — Il Farsi Incontro

### Tag
`rivoluzione` `cambiamento` `rinnovamento` `coraggio` `trasformazione radicale` `riforma` `sovvertimento`

### Giudizio
Il Sovvertimento. Nel tuo giorno vieni creduto. Sublime riuscita, propizia per la perseveranza. Il pentimento svanisce.

### Immagine
Nel lago c'è il fuoco: l'immagine del Sovvertimento. Così il nobile ordina il computo del tempo e chiarisce le stagioni.

### Interpretazione Moderna
Rivoluzione e cambiamento radicale. Agisci con coraggio per rinnovare lo status quo.

### Linee Mobili
- **Linea 1 (初九):** Pianifica il sovvertimento, non agire in modo impulsivo.
- **Linea 2 (六二):** Cerca consenso prima di ribaltare tutto.
- **Linea 3 (九三):** Distinguere tra rivoluzione costruttiva e distruttiva.
- **Linea 4 (九四):** Coordinati con alleati fidati.
- **Linea 5 (九五):** Guida il cambiamento con visione ampia.
- **Linea 6 (上六):** Dopo il sovvertimento, stabilizza il nuovo ordine.

═══════════════════════════════════════════════════════════════════════════════════


## 50. 鼎 Il Crogiolo (Dǐng) ䷱

### Struttura
- **Trigramma Superiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Trigramma Inferiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Codifica Binaria:** 011101 (dec: 29)

### Relazioni
- **Opposto:** 3 — Difficoltà Iniziale
- **Rovesciato:** 49 — Il Sovvertimento
- **Nucleare:** 43 — Lo Straripamento

### Tag
`trasformazione` `alchimia` `creazione` `raffinamento` `cultura` `nutrimento spirituale` `sacro`

### Giudizio
Il Crogiolo. Sublime salute. Riuscita.

### Immagine
Sopra il legno c'è il fuoco: l'immagine del Crogiolo. Così il nobile consolida il destino rettificando la posizione.

### Interpretazione Moderna
Trasformazione e alchimia interiore. Dai valore a ciò che hai e trasmutalo in qualcosa di migliore.

### Linee Mobili
- **Linea 1 (初六):** Definisci gli elementi base del cambiamento.
- **Linea 2 (九二):** Scalda il crogiolo con costanza e passione.
- **Linea 3 (九三):** Non abbandonare il processo a metà.
- **Linea 4 (九四):** Filtra ciò che è impuro, raffina la materia.
- **Linea 5 (六五):** Una trasformazione riuscita richiede tempo.
- **Linea 6 (上九):** Raggiunta la nuova forma, sfruttala al meglio.

═══════════════════════════════════════════════════════════════════════════════════


## 51. 震 Il Tuono (Zhèn) ䷲

### Struttura
- **Trigramma Superiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Trigramma Inferiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Codifica Binaria:** 100100 (dec: 36)

### Relazioni
- **Opposto:** 57 — Il Vento
- **Rovesciato:** 52 — L'Arresto
- **Nucleare:** 39 — L'Impedimento

### Tag
`shock` `imprevisto` `reazione` `risveglio` `scossa` `tuono` `prontezza`

### Giudizio
Il Tuono. Riuscita. Lo Shock viene — oh, oh! Parole ridenti — ha, ha! Il Tuono spaventa per cento miglia, ma egli non lascia cadere il cucchiaio sacrificale e il calice.

### Immagine
Tuono continuato: l'immagine dello Shock. Così il nobile con timore e tremore rettifica la propria vita ed esamina se stesso.

### Interpretazione Moderna
Evento improvviso e dirompente. Sii pronto a reagire in modo rapido ed efficace.

### Linee Mobili
- **Linea 1 (初九):** Non farti trovare impreparato: anticipa.
- **Linea 2 (六二):** Il timore può essere un alleato se ti mantiene vigile.
- **Linea 3 (六三):** Non perdere la calma nel caos.
- **Linea 4 (九四):** Dopo lo shock, organizza una risposta.
- **Linea 5 (六五):** Impara dall'imprevisto per migliorare.
- **Linea 6 (上六):** Superato il tuono, ritrova la serenità.

═══════════════════════════════════════════════════════════════════════════════════


## 52. 艮 L'Arresto (Gèn) ䷳

### Struttura
- **Trigramma Superiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Trigramma Inferiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Codifica Binaria:** 001001 (dec: 9)

### Relazioni
- **Opposto:** 58 — Il Sereno
- **Rovesciato:** 51 — Il Tuono
- **Nucleare:** 40 — La Liberazione

### Tag
`quiete` `meditazione` `arresto` `calma` `concentrazione` `introspezione` `pausa`

### Giudizio
L'Arresto. Tenere fermo il dorso cosicché egli non senta più il proprio corpo. Va nel suo cortile e non vede il suo popolo. Nessuna macchia.

### Immagine
Montagne una sopra l'altra: l'immagine dell'Arresto. Così il nobile non va coi suoi pensieri oltre la propria posizione.

### Interpretazione Moderna
Calma e meditazione. Fermarsi per un po' può aiutare a ritrovare chiarezza e concentrazione.

### Linee Mobili
- **Linea 1 (初六):** Una sosta precoce può prevenire errori.
- **Linea 2 (六二):** Non scambiare l'arresto per pigrizia.
- **Linea 3 (九三):** Rivedi gli obiettivi prima di ripartire.
- **Linea 4 (六四):** L'immobilità temporanea ricarica energia.
- **Linea 5 (六五):** Medita sulle prossime mosse.
- **Linea 6 (上九):** Troppa stasi può diventare stagnazione.

═══════════════════════════════════════════════════════════════════════════════════


## 53. 漸 Lo Sviluppo (Jiàn) ䷴

### Struttura
- **Trigramma Superiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Trigramma Inferiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Codifica Binaria:** 001011 (dec: 11)

### Relazioni
- **Opposto:** 54 — La Ragazza che Si Sposa
- **Rovesciato:** 54 — La Ragazza che Si Sposa
- **Nucleare:** 64 — Prima del Compimento

### Tag
`sviluppo` `gradualità` `crescita organica` `pazienza` `radici` `maturazione` `costanza`

### Giudizio
Lo Sviluppo. La fanciulla viene data in sposa. Salute. Propizia è la perseveranza.

### Immagine
Sulla montagna c'è un albero: l'immagine dello Sviluppo. Così il nobile dimora in dignità e virtù per migliorare i costumi.

### Interpretazione Moderna
Crescita costante e armoniosa, come un albero che mette radici profonde. Costruisci passo dopo passo.

### Linee Mobili
- **Linea 1 (初六):** Metti radici solide all'inizio.
- **Linea 2 (六二):** Cresci gradualmente, evita salti bruschi.
- **Linea 3 (九三):** Cura le basi per reggere le sfide future.
- **Linea 4 (六四):** Espanditi in modo ordinato.
- **Linea 5 (九五):** Rafforza i rami mentre ti allunghi.
- **Linea 6 (上九):** Compimento: ora puoi dare frutti.

═══════════════════════════════════════════════════════════════════════════════════


## 54. 歸妹 La Ragazza che Si Sposa (Guī Mèi) ䷵

### Struttura
- **Trigramma Superiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Trigramma Inferiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Codifica Binaria:** 110100 (dec: 52)

### Relazioni
- **Opposto:** 53 — Lo Sviluppo
- **Rovesciato:** 53 — Lo Sviluppo
- **Nucleare:** 63 — Dopo il Compimento

### Tag
`adattamento` `integrazione` `nuovi legami` `ruolo` `transizione` `identità` `diplomazia`

### Giudizio
La Ragazza che Si Sposa. Imprese recano sciagura. Nulla che sia propizio.

### Immagine
Sopra il lago c'è il tuono: l'immagine della Ragazza che Si Sposa. Così il nobile comprende il transitorio alla luce dell'eternità della fine.

### Interpretazione Moderna
Situazione di adattamento a un contesto più ampio. Accetta i ruoli e impara dai nuovi legami.

### Linee Mobili
- **Linea 1 (初九):** Comprendi la nuova realtà con umiltà.
- **Linea 2 (九二):** Non temere di imparare costumi diversi.
- **Linea 3 (六三):** Mantenere la propria essenza nelle relazioni.
- **Linea 4 (九四):** Usa la diplomazia per integrarti.
- **Linea 5 (六五):** Equilibrio tra adattamento e identità.
- **Linea 6 (上六):** Consolidati in un ruolo maturo e stabile.

═══════════════════════════════════════════════════════════════════════════════════


## 55. 豐 L'Abbondanza (Fēng) ䷶

### Struttura
- **Trigramma Superiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Trigramma Inferiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Codifica Binaria:** 101100 (dec: 44)

### Relazioni
- **Opposto:** 59 — La Dissoluzione
- **Rovesciato:** 56 — Il Viandante
- **Nucleare:** 28 — La Preponderanza del Grande

### Tag
`abbondanza` `prosperità` `pienezza` `fortuna` `concretizzare` `raccolta` `apice`

### Giudizio
L'Abbondanza ha riuscita. Il re la raggiunge. Non essere triste. Sii come il sole a mezzogiorno.

### Immagine
Tuono e lampo vengono entrambi: l'immagine dell'Abbondanza. Così il nobile decide le cause giudiziarie e applica le pene.

### Interpretazione Moderna
Fortuna, prosperità e pienezza. Sfrutta il periodo favorevole per concretizzare progetti.

### Linee Mobili
- **Linea 1 (初九):** Prepara il terreno per raccogliere i frutti.
- **Linea 2 (六二):** Condividi la prosperità, rafforza le relazioni.
- **Linea 3 (九三):** Evita l'euforia e mantieni organizzazione.
- **Linea 4 (九四):** Approfondisci le opportunità.
- **Linea 5 (六五):** Difendi la tua abbondanza con equilibrio.
- **Linea 6 (上六):** Se saturi, pianifica la continuità.

═══════════════════════════════════════════════════════════════════════════════════


## 56. 旅 Il Viandante (Lǚ) ䷷

### Struttura
- **Trigramma Superiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Trigramma Inferiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Codifica Binaria:** 001101 (dec: 13)

### Relazioni
- **Opposto:** 60 — La Limitazione
- **Rovesciato:** 55 — L'Abbondanza
- **Nucleare:** 28 — La Preponderanza del Grande

### Tag
`viaggio` `mobilità` `adattamento` `distacco` `flessibilità` `esplorazione` `straniero`

### Giudizio
Il Viandante. Riuscita attraverso la piccolezza. La perseveranza del viandante reca salute.

### Immagine
Sulla montagna c'è il fuoco: l'immagine del Viandante. Così il nobile è chiaro e cauto nell'applicare le pene e non protrae i processi.

### Interpretazione Moderna
Mobilità e distacco. Essere stranieri in un nuovo ambiente insegna flessibilità e spirito di adattamento.

### Linee Mobili
- **Linea 1 (初六):** Preparati alle differenze culturali.
- **Linea 2 (六二):** Non portare troppi bagagli, mantieni leggerezza.
- **Linea 3 (九三):** Rispetta le usanze locali senza rinunciare a te stesso.
- **Linea 4 (九四):** Cerca alleanze tra i "nativi".
- **Linea 5 (六五):** L'esperienza del viaggio arricchisce interiormente.
- **Linea 6 (上九):** Quando è ora di ripartire, fallo con gratitudine.

═══════════════════════════════════════════════════════════════════════════════════


## 57. 巽 Il Vento (Xùn) ䷸

### Struttura
- **Trigramma Superiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Trigramma Inferiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Codifica Binaria:** 011011 (dec: 27)

### Relazioni
- **Opposto:** 51 — Il Tuono
- **Rovesciato:** 58 — Il Sereno
- **Nucleare:** 38 — L'Opposizione

### Tag
`penetrazione` `influenza graduale` `costanza` `persuasione` `vento` `pazienza` `dolcezza`

### Giudizio
Il Mite. Riuscita attraverso la piccolezza. È propizio avere dove andare. È propizio vedere il grande uomo.

### Immagine
Venti che si susseguono: l'immagine del Dolcemente Penetrante. Così il nobile diffonde i suoi ordini e porta a termine i suoi affari.

### Interpretazione Moderna
Influenza graduale e costante. Come una brezza che modella il paesaggio, agisci con pazienza.

### Linee Mobili
- **Linea 1 (初六):** Un impatto lieve, ma costante, può produrre grandi effetti.
- **Linea 2 (九二):** Evita azioni improvvise, preferisci la persuasione.
- **Linea 3 (九三):** Aggira gli ostacoli piuttosto che affrontarli di petto.
- **Linea 4 (六四):** La costanza genera cambiamenti profondi.
- **Linea 5 (九五):** Non disperdere le tue energie, concentrale.
- **Linea 6 (上九):** Se il vento diventa tempesta, ricalibra la direzione.

═══════════════════════════════════════════════════════════════════════════════════


## 58. 兌 Il Sereno (Duì) ䷹

### Struttura
- **Trigramma Superiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Trigramma Inferiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Codifica Binaria:** 110110 (dec: 54)

### Relazioni
- **Opposto:** 52 — L'Arresto
- **Rovesciato:** 57 — Il Vento
- **Nucleare:** 37 — La Casata

### Tag
`gioia` `comunicazione` `fiducia` `ottimismo` `dialogo` `serenità` `condivisione`

### Giudizio
Il Sereno. Riuscita. Propizia è la perseveranza.

### Immagine
Laghi che poggiano l'uno sull'altro: l'immagine del Sereno. Così il nobile si unisce ai suoi amici per discutere e per esercitarsi.

### Interpretazione Moderna
Gioia condivisa e comunicazione aperta. Crea un clima di fiducia e collaborazione.

### Linee Mobili
- **Linea 1 (初九):** Inizia con un sorriso, apri il dialogo.
- **Linea 2 (九二):** Non abusare dell'ottimismo, sii realistico.
- **Linea 3 (六三):** Evita chi tenta di spegnere la tua serenità.
- **Linea 4 (九四):** Favorisci scambi costruttivi con gli altri.
- **Linea 5 (九五):** Condividi le tue idee in modo empatico.
- **Linea 6 (上六):** Troppa euforia può generare superficialità.

═══════════════════════════════════════════════════════════════════════════════════


## 59. 渙 La Dissoluzione (Huàn) ䷺

### Struttura
- **Trigramma Superiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Trigramma Inferiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Codifica Binaria:** 010011 (dec: 19)

### Relazioni
- **Opposto:** 55 — L'Abbondanza
- **Rovesciato:** 60 — La Limitazione
- **Nucleare:** 27 — Gli Angoli della Bocca

### Tag
`dissoluzione` `superamento` `chiarezza` `trasparenza` `scioglimento` `liberazione` `fluidità`

### Giudizio
La Dissoluzione. Riuscita. Il re si avvicina al suo tempio. È propizio attraversare la grande acqua. Propizia è la perseveranza.

### Immagine
Il vento soffia sull'acqua: l'immagine della Dissoluzione. Così gli antichi re offrivano sacrifici al Signore e costruivano templi.

### Interpretazione Moderna
Superare barriere e incomprensioni. Sciogli i blocchi emotivi o relazionali per ritrovare chiarezza.

### Linee Mobili
- **Linea 1 (初六):** Individua la fonte dell'incomprensione.
- **Linea 2 (九二):** Non temere la trasparenza, porta liberazione.
- **Linea 3 (六三):** Agisci con decisione, ma con tatto.
- **Linea 4 (六四):** Un aiuto esterno può accelerare la dissoluzione.
- **Linea 5 (九五):** Colloquio aperto per diradare nebbie.
- **Linea 6 (上九):** Quando il blocco si scioglie, costruisci su basi rinnovate.

═══════════════════════════════════════════════════════════════════════════════════


## 60. 節 La Limitazione (Jié) ䷻

### Struttura
- **Trigramma Superiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Trigramma Inferiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Codifica Binaria:** 110010 (dec: 50)

### Relazioni
- **Opposto:** 56 — Il Viandante
- **Rovesciato:** 59 — La Dissoluzione
- **Nucleare:** 27 — Gli Angoli della Bocca

### Tag
`limitazione` `confini` `disciplina` `equilibrio` `regole` `moderazione` `struttura`

### Giudizio
La Limitazione. Riuscita. La limitazione amara non deve essere praticata con perseveranza.

### Immagine
Sopra il lago c'è l'acqua: l'immagine della Limitazione. Così il nobile crea numero e misura e indaga la natura della virtù e della retta condotta.

### Interpretazione Moderna
Fissare confini e regole per mantenere l'equilibrio. L'autodisciplina rafforza il potenziale.

### Linee Mobili
- **Linea 1 (初九):** Stabilisci i limiti minimi di sicurezza.
- **Linea 2 (九二):** Non esagerare con le restrizioni, serve flessibilità.
- **Linea 3 (六三):** Adatta i confini man mano che cresci.
- **Linea 4 (六四):** Rispetta i tuoi stessi limiti.
- **Linea 5 (九五):** Una regola chiara semplifica le relazioni.
- **Linea 6 (上六):** Troppa rigidità genera ribellione.

═══════════════════════════════════════════════════════════════════════════════════


## 61. 中孚 La Veracità Interiore (Zhōng Fú) ䷼

### Struttura
- **Trigramma Superiore:** ☴ Vento (Xùn) — Penetrazione, Dolcezza | Legno
- **Trigramma Inferiore:** ☱ Lago (Duì) — Gioia, Serenità | Metallo
- **Codifica Binaria:** 110011 (dec: 51)

### Relazioni
- **Opposto:** 62 — La Preponderanza del Piccolo
- **Rovesciato:** 61 — La Veracità Interiore (palindromo)
- **Nucleare:** 27 — Gli Angoli della Bocca

### Tag
`verità` `sincerità` `autenticità` `fiducia` `trasparenza` `integrità` `cuore`

### Giudizio
La Veracità Interiore. Porci e pesci. Salute! È propizio attraversare la grande acqua. Propizia è la perseveranza.

### Immagine
Sopra il lago c'è il vento: l'immagine della Veracità Interiore. Così il nobile discute le cause penali per ritardare le esecuzioni capitali.

### Interpretazione Moderna
Trasparenza e sincerità totale. Quando sei autentico, attrai relazioni e risultati genuini.

### Linee Mobili
- **Linea 1 (初九):** Inizia dall'onestà con te stesso.
- **Linea 2 (九二):** La verità costruisce fiducia reciproca.
- **Linea 3 (六三):** Non temere il giudizio altrui se sei sincero.
- **Linea 4 (六四):** Un cuore limpido ispira rispetto.
- **Linea 5 (九五):** La veracità guida decisioni illuminate.
- **Linea 6 (上九):** Non tornare mai all'inganno.

═══════════════════════════════════════════════════════════════════════════════════


## 62. 小過 La Preponderanza del Piccolo (Xiǎo Guò) ䷽

### Struttura
- **Trigramma Superiore:** ☳ Tuono (Zhèn) — Movimento, Incitamento | Legno
- **Trigramma Inferiore:** ☶ Montagna (Gèn) — Arresto, Quiete | Terra
- **Codifica Binaria:** 001100 (dec: 12)

### Relazioni
- **Opposto:** 61 — La Veracità Interiore
- **Rovesciato:** 62 — La Preponderanza del Piccolo (palindromo)
- **Nucleare:** 28 — La Preponderanza del Grande

### Tag
`dettagli` `precisione` `piccoli passi` `cura` `attenzione` `minuzie` `cautela`

### Giudizio
La Preponderanza del Piccolo. Riuscita. Propizia è la perseveranza. Si possono fare piccole cose, non si possono fare grandi cose. L'uccello in volo porta il messaggio: non è bene tendere verso l'alto, è bene rimanere in basso. Grande salute!

### Immagine
Sulla montagna c'è il tuono: l'immagine della Preponderanza del Piccolo. Così il nobile, nella sua condotta, dà preponderanza alla riverenza; nel lutto, dà preponderanza al dolore; nelle sue spese, dà preponderanza alla parsimonia.

### Interpretazione Moderna
È il momento di curare i dettagli. Piccoli passi accurati portano a grandi obiettivi.

### Linee Mobili
- **Linea 1 (初六):** Anche il più piccolo errore può pesare.
- **Linea 2 (六二):** Raffina ogni mossa, procedi con pazienza.
- **Linea 3 (九三):** Non sottovalutare l'impatto delle minuzie.
- **Linea 4 (九四):** Unisci piccoli sforzi per un risultato solido.
- **Linea 5 (六五):** La precisione è la tua forza.
- **Linea 6 (上六):** Se la situazione evolve, adatta i dettagli.

═══════════════════════════════════════════════════════════════════════════════════


## 63. 既濟 Dopo il Compimento (Jì Jì) ䷾

### Struttura
- **Trigramma Superiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Trigramma Inferiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Codifica Binaria:** 101010 (dec: 42)

### Relazioni
- **Opposto:** 64 — Prima del Compimento
- **Rovesciato:** 64 — Prima del Compimento
- **Nucleare:** 64 — Prima del Compimento

### Tag
`compimento` `equilibrio raggiunto` `vigilanza` `consolidamento` `ciclo` `completamento` `transizione`

### Giudizio
Dopo il Compimento. Riuscita nelle piccole cose. Propizia è la perseveranza. All'inizio salute, alla fine disordine.

### Immagine
L'acqua sopra il fuoco: l'immagine dello stato di Dopo il Compimento. Così il nobile riflette sulla sventura e se ne premunisce in anticipo.

### Interpretazione Moderna
Un ciclo si chiude, ma occorre vigilanza per evitare passi falsi. Mantieni la qualità raggiunta.

### Linee Mobili
- **Linea 1 (初九):** Non rilassarti troppo presto.
- **Linea 2 (六二):** Ricalibra le risorse per la nuova fase.
- **Linea 3 (九三):** Evita di scivolare nell'autocompiacimento.
- **Linea 4 (六四):** Resta aperto a miglioramenti ulteriori.
- **Linea 5 (九五):** Consolidare il successo è un atto di responsabilità.
- **Linea 6 (上六):** Pronto a un nuovo inizio, non fermarti.

═══════════════════════════════════════════════════════════════════════════════════


## 64. 未濟 Prima del Compimento (Wèi Jì) ䷿

### Struttura
- **Trigramma Superiore:** ☲ Fuoco (Lí) — Aderenza, Chiarezza | Fuoco
- **Trigramma Inferiore:** ☵ Acqua (Kǎn) — Pericolo, Profondità | Acqua
- **Codifica Binaria:** 010101 (dec: 21)

### Relazioni
- **Opposto:** 63 — Dopo il Compimento
- **Rovesciato:** 63 — Dopo il Compimento
- **Nucleare:** 63 — Dopo il Compimento

### Tag
`incompiuto` `preparazione` `ultimo miglio` `pazienza` `sforzo finale` `nuovo ciclo` `potenziale`

### Giudizio
Prima del Compimento. Riuscita. Ma se la piccola volpe, quando ha quasi compiuto la traversata, si bagna la coda, non c'è nulla che sia propizio.

### Immagine
Il fuoco sopra l'acqua: l'immagine dello stato di Prima del Compimento. Così il nobile è cauto nel distinguere le cose, affinché ciascuna trovi il suo posto.

### Interpretazione Moderna
La meta è vicina, ma ancora incompiuta. Preparati con cura per il finale o per un nuovo inizio.

### Linee Mobili
- **Linea 1 (初六):** Un approccio affrettato può rovinare tutto.
- **Linea 2 (九二):** Controlla i dettagli e verifica la preparazione.
- **Linea 3 (六三):** Non scoraggiarti per un ultimo ostacolo.
- **Linea 4 (九四):** Cerca aiuto se sei in dubbio.
- **Linea 5 (六五):** La tensione pre-finale può essere superata con metodo.
- **Linea 6 (上九):** Concluso l'obiettivo, si apre un nuovo ciclo.

═══════════════════════════════════════════════════════════════════════════════════

--- FINE DATABASE ORACLE ---
