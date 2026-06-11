#!/usr/bin/env sh
set -eu

DATABASE_PATH="data/app.db"
BACKUP_DIR="backups"

mkdir -p "$BACKUP_DIR"

if [ ! -f "$DATABASE_PATH" ]; then
  echo "Erro: banco nao encontrado em $DATABASE_PATH." >&2
  exit 1
fi

timestamp="$(date '+%Y%m%d-%H%M%S')"
destination="$BACKUP_DIR/app-$timestamp.db"
cp "$DATABASE_PATH" "$destination"

echo "Backup criado em $destination"
