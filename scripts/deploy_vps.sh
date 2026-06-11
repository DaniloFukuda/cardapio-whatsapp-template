#!/usr/bin/env sh
set -eu

PROJECT_DIR="${PROJECT_DIR:-/opt/cardapio-whatsapp-template}"

cd "$PROJECT_DIR"
git pull --ff-only

if [ ! -f .env ]; then
  echo "Arquivo .env não encontrado em $PROJECT_DIR." >&2
  echo "Crie-o a partir de .env.example antes do deploy." >&2
  exit 1
fi

docker compose up -d --build
docker compose ps
docker image prune -f
