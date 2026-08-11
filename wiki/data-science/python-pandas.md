---
date: 2026-07-07
area: data-science
source: raw/data-science/PROJECT WORK/Analisi dati magazzino finale/
tags: [python, pandas, pulizia-dati, ricette]
reviewed: 2026-08-11
---
# Python / pandas

Libreria Python per l'analisi via DataFrame: caricamento, pulizia, aggregazione e
trasformazione. Prototipo in [[progetto-hotel-booking]] e [[progetto-insurance]],
pipeline completa in [[progetto-magazzino]]. Di norma dentro [[jupyter]].

## Come si organizzano i notebook

**Un notebook che pulisce, uno che analizza.** Il primo esporta il CSV pulito e
finisce li; il secondo riparte da quel file e non tocca mai il grezzo. Il vantaggio
non e estetico: rieseguire l'analisi non rischia di ripulire due volte, e la pulizia
si rilegge senza scorrere trecento righe di grafici. Il file intermedio e il contratto
tra i due.

## Ricette di pulizia

Le operazioni ricorrenti di [[controlli-qualita-dati]] e [[data-cleaning]], nella forma
pandas verificata sul campo.

```python
# Struttura e tipi: sempre prima di toccare qualsiasi cosa
df.shape; df.columns.tolist(); df.info(); df.describe()

# Nomi di colonna sbagliati all'origine (capita piu spesso di quanto sembri)
df = df.rename(columns={"Catagory": "Category"})

# Valori mancanti: contarli, poi GUARDARE le righe che li contengono
df.isna().sum()
df[df.isna().any(axis=1)]

# Duplicati: righe intere E chiave logica sono due controlli diversi
df.duplicated().sum()
df["Product_ID"].duplicated().sum()

# Spazi di bordo: invisibili, e spezzano ogni raggruppamento
for c in colonne_testo:
    df[c] = df[c].str.strip()

# Valuta in testo -> numero. errors="coerce" trasforma i fallimenti in NaN,
# cosi si CONTANO invece di far esplodere lo script
df["Unit_Price"] = pd.to_numeric(
    df["Unit_Price"].astype(str).str.replace("$", "", regex=False).str.strip(),
    errors="coerce")
print("conversioni non riuscite:", df["Unit_Price"].isna().sum())

# Date: format ESPLICITO. Senza, pandas indovina e su 3/4/2024 sbaglia meta volte
# (vedi anche [[normalizzazione-decimali]] per il problema gemello sui decimali)
df[c] = pd.to_datetime(df[c], format="%m/%d/%Y", errors="coerce")

# Coerenza tra campi: le regole che nessun tipo di dato puo imporre
(df["Expiration_Date"] < df["Date_Received"]).sum()
(df["Stock_Quantity"] < 0).sum()

# Esportazione con date leggibili e senza indice fantasma
df.to_csv("Dataset_pulito.csv", index=False, date_format="%Y-%m-%d")
```

Due abitudini che pagano: **`errors="coerce"` e poi contare i NaN** (un conteggio a
zero e la prova che la conversione ha funzionato, non una speranza), e **imputare
guardando**, non con la media — la categoria mancante di un prodotto si recupera dai
suoi omonimi gia categorizzati, non da una statistica.

## Ricette di analisi

```python
# Classificazione a piu condizioni: np.select legge meglio di if annidati
df["Supply_Status"] = np.select(
    [df["Stock_Quantity"] < df["Reorder_Level"],
     df["Stock_Quantity"] == df["Reorder_Level"]],
    ["Da riordinare", "Sulla soglia"],
    default="Scorta sufficiente")

# Fasce lette dai dati, non scelte a mano ([[quartili-outlier]])
basso, alto = df["Sales_Volume"].quantile([0.33, 0.67])

# Differenze che non devono andare sotto zero
df["Units_To_Reorder_Level"] = (df["Reorder_Level"] - df["Stock_Quantity"]).clip(lower=0)

# Flag 0/1 per far rispondere un totale alla domanda giusta
df["Reorder_Needed_Flag"] = df["Supply_Status"].isin(["Da riordinare", "Sulla soglia"]).astype(int)
df["Reorder_Cost_Required"] = df["Estimated_Reorder_Cost"] * df["Reorder_Needed_Flag"]

# Riepilogo per gruppo, con nomi di colonna espliciti
riepilogo = df.groupby("Supplier_Name").agg(
    Numero_Prodotti=("Product_ID", "count"),
    Valore_Stock=("Inventory_Value", "sum"),
    Costo_Riordino=("Reorder_Cost_Required", "sum")).reset_index()

# Incrocio di due classificazioni: e qui che si trovano le cose
pd.crosstab(df["Demand_Class"], df["Supply_Status"])
```

`crosstab` merita una riga a parte. Guardare due variabili una per volta descrive;
incrociarle spiega. In [[progetto-magazzino]] e l'incrocio — e nient'altro — a rivelare
che il riordino non segue la domanda.

## Verifica finale

Prima di esportare, si controlla che le colonne attese esistano davvero e non abbiano
buchi. Il notebook di magazzino chiude con un elenco esplicito delle 13 colonne derivate
e un conteggio dei NaN su ciascuna: due righe che intercettano il refuso in un nome di
colonna prima che diventi un grafico vuoto.

Collegati:
- [[strumenti]]
- [[jupyter]]
- [[controlli-qualita-dati]]
- [[data-cleaning]]
- [[analisi-esplorativa]]
- [[feature-engineering]]
- [[indicatori-magazzino]]
- [[progetto-magazzino]]
- [[quartili-outlier]]
- [[normalizzazione-decimali]]
