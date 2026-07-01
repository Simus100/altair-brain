#!/usr/bin/env bash
# altair-brain — bootstrap del runtime API sulla VPS (layout a 3 cartelle).
# Esegui come utente 'altair' dalla radice del repo clonato (~/altair-brain).
# Idempotente. Crea:
#   ~/altair-api    runtime separato dal repo (venv, app.py, update script, .env)
#   ~/altair-data   dati scrivibili FUORI dal git (feedback, LESSONS)
# Il repo resta consumatore in sola lettura: l'auto-update fa fetch+reset, mai conflitti.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
API="$HOME/altair-api"
DATA="$HOME/altair-data"
export PATH="$HOME/.local/bin:$PATH"

echo "== 1. cartelle runtime e dati =="
mkdir -p "$API" "$DATA/memory"

echo "== 2. codice API (copiato dal repo, aggiornabile rilanciando il bootstrap) =="
cp "$REPO/server/app.py" "$API/app.py"
cp "$REPO/server/update_brain.sh" "$API/update_brain.sh"
chmod +x "$API/update_brain.sh"

echo "== 3. virtualenv + dipendenze =="
[ -d "$API/.venv" ] || python3 -m venv "$API/.venv"
"$API/.venv/bin/pip" install -q --upgrade pip
"$API/.venv/bin/pip" install -q -r "$REPO/server/requirements.txt"

echo "== 4. graphify (pacchetto PyPI 'graphifyy') =="
if ! command -v graphify >/dev/null 2>&1; then
  if command -v pipx >/dev/null 2>&1; then pipx install graphifyy || true
  elif command -v uv >/dev/null 2>&1; then uv tool install graphifyy || true
  else echo "  ATTENZIONE: installa pipx o uv, poi: pipx install graphifyy"; fi
fi
GBIN="$(command -v graphify || true)"
echo "  graphify: ${GBIN:-NON TROVATO (gli endpoint /query ecc. daranno 503)}"

echo "== 5. $API/.env =="
if [ ! -f "$API/.env" ]; then
  TOKEN="$(openssl rand -hex 32)"
  {
    echo "ALTAIR_API_TOKEN=$TOKEN"
    echo "ALTAIR_REPO_DIR=$REPO"
    [ -n "$GBIN" ] && echo "GRAPHIFY_BIN=$GBIN"
    echo "ALTAIR_MEMORY_DIR=$DATA/memory"
    echo "ALTAIR_LESSONS=$DATA/LESSONS.md"
    echo "ALTAIR_UPDATE_SCRIPT=$API/update_brain.sh"
  } > "$API/.env"
  chmod 600 "$API/.env"
  echo "  creato $API/.env — TOKEN (conservalo): $TOKEN"
else
  echo "  $API/.env gia presente, lasciato invariato."
fi

echo "== bootstrap completato =="
echo "Test:   cd $API && set -a && . ./.env && set +a && ./.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000"
echo "Poi installa le unit systemd (server/systemd/) come root."
