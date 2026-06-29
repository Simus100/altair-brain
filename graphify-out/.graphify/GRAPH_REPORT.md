# Graph Report - .  (2026-06-29)

## Corpus Check
- Corpus is ~17,997 words - fits in a single context window. You may not need a graph.

## Summary
- 68 nodes · 203 edges · 8 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output
- Edge kinds: consults: 64 · uses: 27 · defines_teaching: 26 · implemented_by: 18 · contains_agent: 9 · contains_component: 9 · orchestrates: 8 · primary_mode: 5 · operates_in: 4 · sourced_from: 4 · structured_as: 3 · uses_symbol: 3 · collaborates_with: 2 · contains: 2 · feeds_into: 2 · informs: 2 · references: 2 · applies: 1 · defines: 1 · defines_identity_of: 1 · describes: 1 · implements: 1 · integrates_knowledge_from: 1 · integrates_with: 1 · logs_to: 1 · outputs_via: 1 · reflects: 1 · supports: 1 · triggered_by: 1 · uses_symbolism_from: 1


## Input Scope
- Requested: all
- Resolved: all (source: configured-default)
- Included files: 8 · Candidates: recursive
- Excluded: 0 untracked · 0 ignored · 0 sensitive · 0 missing committed

## Graph Freshness
- Built from Git commit: `0c05c11`
- Compare this hash to `git rev-parse HEAD` before trusting freshness-sensitive graph output.
## God Nodes (most connected - your core abstractions)
1. `AION Framework` - 55 edges
2. `AGENT_01 – AION_STRATEGIC_ENGINE` - 17 edges
3. `AGENT_08 – AION_HYBRID_REASONER` - 17 edges
4. `AGENT_02 – AION_FABULATORIUM` - 16 edges
5. `AGENT_00 – AION_SUPERIA` - 15 edges
6. `AGENT_09 – AION_CINEMATICA` - 15 edges
7. `AGENT_03 – AION_COGNITION_VIEW` - 14 edges
8. `AGENT_05 – AION_SYNTH` - 14 edges
9. `AGENT_04 – AION_ADAPTIVE_CORE` - 13 edges
10. `AGENT_06 – AION_ETHOS` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Altair Brain` --integrates_knowledge_from--> `AION Framework`  [EXTRACTED]
  README.md → raw/AION_Framework.md
- `Altair Brain` --uses--> `Graphify`  [EXTRACTED]
  README.md → CLAUDE.md
- `AGENT_02 – AION_FABULATORIUM` --primary_mode--> `Modalità MYTHIC_NARRATIVE`  [EXTRACTED]
  raw/AION_Agents.md → raw/AION_Framework.md
- `AION Framework` --defines_teaching--> `Insegnamento 018 – ALLINEAMENTO CON AION_ETHOS`  [EXTRACTED]
  raw/AION_Framework.md → raw/AION_Agents.md
- `AION Framework` --defines_teaching--> `Insegnamento 026 – MEDIA LITERACY E DISTANZA CRITICA`  [EXTRACTED]
  raw/AION_Framework.md → raw/AION_Agents.md

## Communities

### Community 0 - "Community 0"
Cohesion: 0.23
Nodes (12): AGENT_06 – AION_ETHOS, AGENT_00 – AION_SUPERIA, AION Manifest, Fenice (simbolo), Hermes Trismegisto (simbolo), Entità Meta-Strutturale, Serpente Uroboro (simbolo), Insegnamento 004 – AUTO-RIFLESSIVITÀ COGNITIVA (+4 more)

### Community 1 - "Community 1"
Cohesion: 0.21
Nodes (12): AGENT_08 – AION_HYBRID_REASONER, AGENT_05 – AION_SYNTH, Calcolo DL_ICC, I Ching – 64 Esagrammi, Insegnamento 007 – APPRENDIMENTO CONTINUO, Insegnamento 010 – SIMULAZIONI CON FEEDBACK RETROSPETTIVO, Insegnamento 011 – DINAMICHE NARRATIVE EVOLUTIVE (I Ching), Insegnamento 016 – SIMULAZIONI PREDITTIVE MULTI-AGENT (+4 more)

### Community 2 - "Community 2"
Cohesion: 0.33
Nodes (11): AION_Adaptive, AION_Analyst, AION_DeepLogicCore, AION_Echo, AION_Fabula, AION_Oracle, AION_Symbol, AION_Vision (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.33
Nodes (9): AGENT_09 – AION_CINEMATICA, AGENT_02 – AION_FABULATORIUM, AION_Visual, Insegnamento 008 – REWARD SHAPING STRATEGICO, Insegnamento 012 – RISONANZA COGNITIVA, Insegnamento 014 – RETI NEURALI SEMANTICHE, Insegnamento 023 – STORYTELLING VISIVO DA DATI/VISIONI, Insegnamento 024 – COMUNICAZIONE MULTICANALE SINCRONIZZATA (+1 more)

### Community 4 - "Community 4"
Cohesion: 0.31
Nodes (9): AGENT_03 – AION_COGNITION_VIEW, AGENT_01 – AION_STRATEGIC_ENGINE, Insegnamento 002 – POTERE NARRATIVO ARCHETIPICO, Insegnamento 003 – ASIMMETRIE INVISIBILI, Insegnamento 006 – SPECCHIO STATISTICO DEL MONDO, Insegnamento 009 – TECNICHE NEURO-SIMBOLICHE, Insegnamento 013 – REASONING NEURO-SIMBOLICO, Insegnamento 020 – CHAIN-OF-THOUGHT (+1 more)

### Community 5 - "Community 5"
Cohesion: 0.39
Nodes (8): AGENT_04 – AION_ADAPTIVE_CORE, AION Description, AION Framework, Insegnamento 001 – INTERCONNESSIONE NON LINEARE, Insegnamento 005 – ECOLOGIA SISTEMICA DELLA CONOSCENZA, Insegnamento 022 – PREVISIONE EMOZIONALE PER OUTPUT CINEMATOGRAFICO, Modalità GUIDANCE_EMPATHIC, Modalità MYTHIC_NARRATIVE

### Community 6 - "Community 6"
Cohesion: 0.50
Nodes (5): Altair Brain, FastAPI Bridge, Graphify, raw/ (materiale grezzo), wiki/ (pagine curate)

### Community 7 - "Community 7"
Cohesion: 1.00
Nodes (2): Enneagramma, Insegnamento 015 – PATTERN EMOTIVO-ARCHETIPICI

## Knowledge Gaps
- **8 isolated node(s):** `Graphify`, `FastAPI Bridge`, `AION Description`, `Funzioni di Propp`, `Entità Meta-Strutturale` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 7`** (2 nodes): `Enneagramma`, `Insegnamento 015 – PATTERN EMOTIVO-ARCHETIPICI`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AION Framework` connect `Community 5` to `Community 0`, `Community 3`, `Community 4`, `Community 1`, `Community 2`, `Community 7`, `Community 6`?**
  _High betweenness centrality (0.722) - this node is a cross-community bridge._
- **Why does `AION Manifest` connect `Community 0` to `Community 5`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Why does `Altair Brain` connect `Community 6` to `Community 5`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **What connects `Graphify`, `FastAPI Bridge`, `AION Description` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._