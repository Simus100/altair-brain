# Graph Report - .  (2026-06-29)

## Corpus Check
- Corpus is ~6,422 words - fits in a single context window. You may not need a graph.

## Summary
- 6 nodes · 9 edges · 2 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output
- Edge kinds: ON_BRANCH: 5 · PARENT_OF: 4


## Input Scope
- Requested: auto
- Resolved: committed (source: cli)
- Included files: 9 · Candidates: 38
- Excluded: 12 untracked · 0 ignored · 0 sensitive · 0 missing committed
- Recommendation: Use --scope all or graphify.yaml inputs.corpus for a knowledge-base folder.

## Graph Freshness
- Built from Git commit: `bf795d6`
- Compare this hash to `git rev-parse HEAD` before trusting freshness-sensitive graph output.
## God Nodes (most connected - your core abstractions)

## Surprising Connections (you probably didn't know these)
- `3f36d08 primo grafo` --ON_BRANCH--> `main`  [EXTRACTED]
  git → git  _Bridges community 1 → community 0_

## Communities

### Community 0 - "Community 0"
Cohesion: 0.83
Nodes (4): 0cb87b9 Initial commit, a9a44d5 Merge branch 'main' of github.com:Simus100/altair-brain, d55c6ea init Altair, main

### Community 1 - "Community 1"
Cohesion: 1.00
Nodes (2): 3f36d08 primo grafo, bf795d6 aggiunto nuovo file

## Knowledge Gaps
- **Thin community `Community 1`** (2 nodes): `3f36d08 primo grafo`, `bf795d6 aggiunto nuovo file`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Not enough signal to generate questions. This usually means the corpus has no AMBIGUOUS edges, no bridge nodes, no INFERRED relationships, and all communities are tightly cohesive. Add more files or run with --mode deep to extract richer edges._