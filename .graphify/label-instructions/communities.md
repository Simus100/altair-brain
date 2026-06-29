# Community Labeling

Graphify is running in assistant/skill mode (no API key). You are the host
assistant (Claude Code / Codex / Gemini CLI). Read the community listing below
and write 2-5 word plain-language names for each.

## Language

LANGUAGE: each community line ends with a `[lang=…]` marker giving the
language of its source nodes. Write that community's name in EXACTLY that
language. Do not normalize every name to one common language.

## Communities

Community 0: 0cb87b9 Initial commit, a9a44d5 Merge branch 'main' of github.com:Simus100/altair-br, d55c6ea init Altair, main [lang=pt]
Community 1: 3f36d08 primo grafo, bf795d6 aggiunto nuovo file [lang=en]

## Instructions

Write a single JSON object mapping each community id (as a string) to its
2-5 word name to: /sessions/fervent-kind-shannon/mnt/altair-brain/.graphify/label-instructions/communities.json

Example:
```json
{
  "0": "Authentication Flow",
  "1": "Authentication Flow"
}
```

Then re-run `graphify update` (or `graphify label`) to ingest the names.
