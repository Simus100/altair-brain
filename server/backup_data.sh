#!/usr/bin/env bash
# altair-brain — backup rotante di ~/altair-data (feedback, lezioni, catture inbox):
# e l'UNICO dato non protetto da GitHub. Tiene le ultime 7 copie in ~/backups.
set -euo pipefail

DATA="${ALTAIR_DATA_DIR:-$HOME/altair-data}"
DEST="${ALTAIR_BACKUP_DIR:-$HOME/backups}"
KEEP=7

[ -d "$DATA" ] || { echo "niente da salvare: $DATA non esiste"; exit 0; }
mkdir -p "$DEST"

STAMP="$(date +%Y%m%d_%H%M%S)"
tar czf "$DEST/altair-data_$STAMP.tar.gz" -C "$(dirname "$DATA")" "$(basename "$DATA")"

# rotazione: tieni solo le ultime $KEEP
ls -1t "$DEST"/altair-data_*.tar.gz 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f

echo "[$(date -Is)] backup ok: $DEST/altair-data_$STAMP.tar.gz ($(ls -1 "$DEST"/altair-data_*.tar.gz | wc -l) copie)"

# Off-site opzionale (regola 3-2-1: una copia fuori dalla VPS). Si attiva SOLO se
# ALTAIR_RCLONE_REMOTE e configurata (es. "gdrive:altair-backups" dopo `rclone config`).
# Se rclone manca o la variabile e vuota: nessun effetto.
if [ -n "${ALTAIR_RCLONE_REMOTE:-}" ] && command -v rclone >/dev/null 2>&1; then
  rclone copy "$DEST/altair-data_$STAMP.tar.gz" "$ALTAIR_RCLONE_REMOTE" \
    && echo "[$(date -Is)] off-site ok: $ALTAIR_RCLONE_REMOTE" \
    || echo "[$(date -Is)] off-site FALLITO (backup locale comunque salvo)" >&2
fi
