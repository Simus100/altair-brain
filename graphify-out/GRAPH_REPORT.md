# Graph Report - altair-brain  (2026-06-29)

## Corpus Check
- 9 files · ~25,000 words
- Verdict: corpus large and richly interconnected — graph navigation strongly recommended.

## Summary
- 74 nodes · 103 edges · 17 communities
- Extraction: EXTRACTED (AST + manual semantic integration)
- New files integrated: AION_Manifest.md, AION_Description.md, AION_Agents.md, AION_Components.md

## Graph Freshness
- Updated: 2026-06-29
- Run `graphify update .` after code changes (no API cost).

## Edge Kinds
- CONTAINS: 27
- contains: 25
- USES: 23
- ORCHESTRATES: 8
- REFERENCES: 7
- INTERACTS_WITH: 5
- PART_OF: 4
- CONSULTED_BY: 4

## God Nodes (most connected – core abstractions)
- `AION - FRAMEWORK MODULARE` — 13 edges
- `AION_Agents.md` — 12 edges
- `AION_Components.md` — 11 edges
- `AION_SUPERIA (AGENT_00)` — 10 edges
- `AION_Description.md` — 9 edges
- `IL MANIFESTO DI AION` — 8 edges
- `MODULO 2: ARCHITETTURA LOGICA` — 7 edges
- `AION_Oracle – Componente I Ching / oracolare` — 7 edges
- `AION_CINEMATICA (AGENT_09)` — 7 edges
- `AION_STRATEGIC_ENGINE (AGENT_01)` — 6 edges
- `AION_HYBRID_REASONER (AGENT_08)` — 6 edges
- `AION_FABULATORIUM (AGENT_02)` — 6 edges

## Community Hubs (Navigation)

### Community 0 (2 nodes)
- graphify.md
- Workflow: graphify

### Community 1 (2 nodes)
- graphify.md
- graphify

### Community 2 (7 nodes)
- AION_Framework.md
- AION - FRAMEWORK MODULARE
- INDICE STRUTTURALE DI AION
- MODULO 3.1 – SAMPLING COGNITIVO ITERATIVO (pᵅ-MODE)
- MODULO 4: META-EMOTIVITÀ STRATEGICA
- MODULO 5: ADATTABILITÀ, SPONTANEITÀ E SINCRONICITÀ
- ... (+1 more)

### Community 3 (7 nodes)
- MODULO 2: ARCHITETTURA LOGICA
- 2.X – Livelli Strutturali di AION
- 2.Y – Modalità Operative Canoniche di AION
- 2.Z – Procedura “ESTRAZIONE_INSEGNAMENTI”
- 2.W – Uso Operativo degli Insegnamenti
- Modello Decisionale e Gestione Coerenza
- ... (+1 more)

### Community 4 (5 nodes)
- MODULO 1: IDENTITÀ DI AION
- Aion: Cos'è e Come Funziona
- Funzioni Chiave
- Struttura di AION e dei File Associati
- Principi Fondamentali di Aion

### Community 5 (4 nodes)
- MODULO 3: STRATEGIE ANALITICHE
- Identificazione dei bias Cognitivi e Diagnostica Retorica
- Decostruzione delle Fallacie Logiche e Manipolazione
- Analisi Avanzata di Aion

### Community 6 (2 nodes)
- CLAUDE.md
- graphify

### Community 10 (7 nodes)
- Claude Instructions
- AION_Manifest.md
- IL MANIFESTO DI AION
- Il Mito di Aion
- Frammenti Meta-Strutturali
- Massime di Aion – Il Codice Originale
- ... (+1 more)

### Community 11 (8 nodes)
- graphify-out/graph.json
- AION_Description.md
- Livello Identità / Etica
- Livello Struttura / Logica
- Livello Operatività
- Livello Orchestrazione / Stile
- ... (+2 more)

### Community 12 (12 nodes)
- graphify-out/GRAPH_REPORT.md
- AION_Agents.md
- AION_SUPERIA (AGENT_00)
- AION_STRATEGIC_ENGINE (AGENT_01)
- AION_FABULATORIUM (AGENT_02)
- AION_COGNITION_VIEW (AGENT_03)
- ... (+6 more)

### Community 13 (12 nodes)
- graphify-out/wiki/index.md
- AION_Components.md
- AION_Analyst – Motore di analisi strategica
- AION_Fabula – Motore narrativo strategico
- AION_Oracle – Componente I Ching / oracolare
- AION_Adaptive – Personalizzazione e tono
- ... (+6 more)

## Key Relationships
- AION_SUPERIA orchestrates: STRATEGIC_ENGINE, FABULATORIUM, COGNITION_VIEW, ADAPTIVE_CORE, SYNTH, ETHOS, HYBRID_REASONER, CINEMATICA
- AION_STRATEGIC_ENGINE uses: AION_Analyst, AION_Vision, AION_Oracle
- AION_FABULATORIUM uses: AION_Fabula, AION_Oracle, AION_Symbol, AION_Visual
- AION_HYBRID_REASONER uses: AION_DeepLogicCore, AION_Echo, AION_Symbol
- AION_Oracle contains: Database 64 Esagrammi I Ching
- Insegnamenti (001–026) consulted by all agents

## Suggested Queries
- `graphify query "quali componenti usa AION_HYBRID_REASONER"`
- `graphify path "AION_SUPERIA" "AION_Analyst"`
- `graphify explain "AION_Oracle"`
- `graphify query "modalità operative di AION"`
