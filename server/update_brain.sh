#!/usr/bin/env bash
# Aggiornamento del second brain: pull dell'ultima versione + rigenerazione grafo e
# vista compatta. Deterministico, NESSUNA API a pagamento (graphify update e AST-only).
# Eseguito a mano (POST /admin/update) o dal timer ogni 3 giorni.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

echo "[$(date -Is)] update: git pull"
git pull --ff-only

if command -v graphify >/dev/null 2>&1; then
  echo "[$(date -Is)] update: graphify update"
  graphify update .
  echo "[$(date -Is)] update: reflect (lezioni)"
  graphify reflect --memory-dir graphify-out/memory --graph graphify-out/graph.json || true
else
  echo "[$(date -Is)] ATTENZIONE: graphify non disponibile, salto rigenerazione grafo"
fi

echo "[$(date -Is)] update: vista compatta"
python3 tools/altair_compact_view.py || true

echo "[$(date -Is)] update: completato"
