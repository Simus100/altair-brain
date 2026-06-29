# Graph Report - C:\Users\mace\altair-brain  (2026-06-29)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 10 nodes · 10 edges · 2 communities
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a9a44d5c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]

## God Nodes (most connected - your core abstractions)
1. `Graphify Rules` - 3 edges
2. `Claude Instructions` - 3 edges
3. `Altair README` - 2 edges
4. `graphify` - 2 edges
5. `Altair System` - 2 edges
6. `graphify-out/graph.json` - 2 edges
7. `graphify-out/wiki/index.md` - 2 edges
8. `graphify-out/GRAPH_REPORT.md` - 2 edges
9. `Graphify Workflow` - 1 edges
10. `Altair Rules` - 1 edges

## Surprising Connections (you probably didn't know these)
- `Altair Rules` --conceptually_related_to--> `Altair System`  [INFERRED]
  AGENTS.md → README.md
- `Graphify Rules` --references--> `graphify-out/graph.json`  [EXTRACTED]
  .agents/rules/graphify.md → CLAUDE.md
- `Graphify Rules` --references--> `graphify-out/GRAPH_REPORT.md`  [EXTRACTED]
  .agents/rules/graphify.md → CLAUDE.md
- `Graphify Rules` --references--> `graphify-out/wiki/index.md`  [EXTRACTED]
  .agents/rules/graphify.md → CLAUDE.md
- `Graphify Workflow` --references--> `graphify`  [EXTRACTED]
  .agents/workflows/graphify.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Graphify Usage Pattern** — agents_rules_graphify, claude_md, graphify_out_graph_json, graphify_out_wiki_index, graphify_out_graph_report [EXTRACTED 0.90]

## Communities (2 total, 0 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.40
Nodes (5): Altair Rules, Graphify Workflow, Altair System, graphify, Altair README

### Community 1 - "Community 1"
Cohesion: 0.60
Nodes (5): Graphify Rules, Claude Instructions, graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/index.md

## Knowledge Gaps
- **2 isolated node(s):** `Graphify Workflow`, `Altair Rules`
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Graphify Workflow`, `Altair Rules` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._