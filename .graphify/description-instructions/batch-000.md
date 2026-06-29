# Node Description Batch 1 of 1

Graphify is running in assistant/skill mode (no API key). You are the host
assistant (Claude Code / Codex / Gemini CLI). Read the prompt below and write
your JSON answer to the answer file.

## Prompt

You are documenting nodes in a knowledge graph.
For each entry below, write ONE concise factual plain-language sentence
describing what it is or does. Use only the provided context.
For an entity node (any other kind — e.g. a person, place, event, object),
describe what the entity is and its role, grounded in its type, its
relations (neighbors) and the provided citations/evidence — e.g.
"Lady Carfax, a wealthy heiress who disappears en route to Lausanne.".
Ground entity descriptions in the citations/evidence when present; do not
speculate beyond the context, so a node with no supporting context may be
left out of the reply.
Write every description in Portuguese (pt). Do not switch languages.
No marketing language.
Respond ONLY with a JSON object mapping each node id (as a string) to its
one-sentence description — no prose, no markdown fences.

- "branch:repo:github.com/Simus100/altair-brain#main": "main" | kind=Branch | source=git | neighbors=[0cb87b9 Initial commit, 3f36d08 primo grafo, a9a44d5 Merge branch 'main' of github.c…, bf795d6 aggiunto nuovo file, d55c6ea init Altair]
- "commit:repo:github.com/Simus100/altair-brain@a9a44d5cec1dedd0772e553768c5f3d491cf7945": "a9a44d5 Merge branch 'main' of github.com:Simus100/altair-brain" | kind=Commit | source=git | neighbors=[0cb87b9 Initial commit, main, 3f36d08 primo grafo, d55c6ea init Altair]
- "commit:repo:github.com/Simus100/altair-brain@3f36d08cc2d33585ed53b77f7eb5d5f6ac4429f7": "3f36d08 primo grafo" | kind=Commit | source=git | neighbors=[main, bf795d6 aggiunto nuovo file, a9a44d5 Merge branch 'main' of github.c…]
- "commit:repo:github.com/Simus100/altair-brain@0cb87b9d18bd4021b95f8927746addb630be84a8": "0cb87b9 Initial commit" | kind=Commit | source=git | neighbors=[main, a9a44d5 Merge branch 'main' of github.c…]
- "commit:repo:github.com/Simus100/altair-brain@bf795d689f820dd31a179fb87e918861a42d1fa6": "bf795d6 aggiunto nuovo file" | kind=Commit | source=git | neighbors=[3f36d08 primo grafo, main]
- "commit:repo:github.com/Simus100/altair-brain@d55c6eac9abda3ee8497bc9ce837d76a7a7dbce8": "d55c6ea init Altair" | kind=Commit | source=git | neighbors=[main, a9a44d5 Merge branch 'main' of github.c…]

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: /sessions/fervent-kind-shannon/mnt/altair-brain/.graphify/description-instructions/batch-000.json

Keep each description factual and concise (one sentence). No markdown, no prose
outside the JSON object. It is acceptable to omit a node if context is
insufficient — but include every node you can ground confidently.

Example answer format:
```json
{
  "node_id_1": "Resolves the configured ontology profile from graphify.yaml.",
  "node_id_2": "Colonel James Barclay, an antagonist in The Crooked Man."
}
```
