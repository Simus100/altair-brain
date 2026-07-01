#!/usr/bin/env bash
# altair-brain — bootstrap a livello utente (esegui come utente 'altair' nella radice del repo).
# Idempotente. Fa: venv + dipendenze, installa graphify (pipx), crea server/.env con token
# e GRAPHIFY_BIN assoluto, genera le viste del grafo. NON tocca systemd/caddy (richiedono root).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
export PATH="$HOME/.local/bin:$PATH"

echo "== 1. virtualenv + dipendenze Python =="
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/pip install -q --upgrade pip
./.venv/bin/pip install -q -r server/requirements.txt

echo "== 2. graphify (pacchetto graphifyy) =="
if ! command -v graphify >/dev/null 2>&1; then
  if command -v pipx >/dev/null 2>&1; then
    pipx install graphifyy || true
  elif command -v uv >/dev/null 2>&1; then
    uv tool install graphifyy || true
  else
    echo "  ATTENZIONE: ne pipx ne uv presenti. Installa graphify a mano: pipx install graphifyy"
  fi
fi
GBIN="$(command -v graphify || true)"
echo "  graphify: ${GBIN:-NON TROVATO}"

echo "== 3. server/.env =="
if [ ! -f server/.env ]; then
  TOKEN="$(openssl rand -hex 32)"
  {
    echo "ALTAIR_API_TOKEN=$TOKEN"
    [ -n "$GBIN" ] && echo "GRAPHIFY_BIN=$GBIN"
  } > server/.env
  chmod 600 server/.env
  echo "  creato server/.env (token generato). Conservalo: $TOKEN"
else
  echo "  server/.env gia presente, lasciato invariato."
fi

echo "== 4. generazione viste del grafo =="
if [ -n "$GBIN" ]; then
  graphify update . || true
  graphify reflect --memory-dir graphify-out/memory --graph graphify-out/graph.json || true
fi
./.venv/bin/python tools/altair_compact_view.py || true

echo "== bootstrap completato =="
echo "Avvio di prova:  ./.venv/bin/uvicorn server.app:app --host 127.0.0.1 --port 8000"
