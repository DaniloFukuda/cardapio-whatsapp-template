#!/usr/bin/env sh
set -eu

ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Erro: arquivo .env nao encontrado." >&2
  exit 1
fi

is_defined() {
  awk -F= -v key="$1" '
    /^[[:space:]]*#/ { next }
    {
      name = $1
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", name)
      if (name != key) {
        next
      }

      value = substr($0, index($0, "=") + 1)
      gsub(/^[[:space:]]+|[[:space:]\r]+$/, "", value)
      if (value != "" && value != "\"\"" && value != "\047\047") {
        found = 1
      }
    }
    END { exit(found ? 0 : 1) }
  ' "$ENV_FILE"
}

missing=0
for variable in \
  ADMIN_API_KEY \
  WHATSAPP_VERIFY_TOKEN \
  WHATSAPP_ACCESS_TOKEN \
  WHATSAPP_PHONE_NUMBER_ID \
  DATABASE_URL
do
  if ! is_defined "$variable"; then
    echo "Erro: $variable nao esta definido no .env." >&2
    missing=1
  fi
done

if [ "$missing" -ne 0 ]; then
  exit 1
fi

echo "Smoke test de configuracao concluido com sucesso."
