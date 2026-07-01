#!/usr/bin/env bash
# altair-brain — aggiornamento del brain sulla VPS (consumatore in sola lettura).
# Il grafo e le viste arrivano GIA GENERATI da git (li committiamo dal dev), quindi qui
# basta un pull pulito: nessuna rigenerazione, nessun conflitto con dati locali.
# Eseguito a mano (POST /admin/update) o dal timer ogni 3 giorni.
set -euo pipefail

REPO="${ALTAIR_REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$REPO"
export PATH="$HOME/.local/bin:$PATH"

echo "[$(date -Is)] update: fetch + reset --hard origin/main (allineamento al remoto)"
git fetch --quiet origin
git reset --hard origin/main

echo "[$(date -Is)] update: allineato a $(git rev-parse --short HEAD)"
