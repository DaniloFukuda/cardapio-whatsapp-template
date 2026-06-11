# Deploy em VPS

Este guia prepara uma instalacao nova em Ubuntu, com o app acessivel apenas
localmente na porta 8000 e publicado por HTTPS atraves do Caddy.

## 1. Criar a VPS

Crie uma VPS Ubuntu, associe o dominio ao IP publico com um registro DNS do
tipo `A` e libere no firewall apenas SSH, HTTP e HTTPS:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 2. Instalar Docker

Instale o Docker Engine e o plugin Compose pelo repositorio oficial do Docker:

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Saia da sessao SSH e entre novamente para aplicar o grupo `docker`.

## 3. Instalar Caddy

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl gnupg
curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/gpg.key \
  | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt \
  | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

## 4. Clonar e configurar

```bash
sudo mkdir -p /opt/cardapio-whatsapp-template
sudo chown "$USER":"$USER" /opt/cardapio-whatsapp-template
git clone https://github.com/DaniloFukuda/cardapio-whatsapp-template.git \
  /opt/cardapio-whatsapp-template
cd /opt/cardapio-whatsapp-template
git switch feature/whatsapp-only-orders-server
cp .env.production.example .env
```

Edite `.env` e substitua todos os valores de exemplo. Gere uma
`ADMIN_API_KEY` longa e aleatoria. Para este Compose, mantenha:

```dotenv
ENVIRONMENT=production
DATABASE_URL=sqlite:////app/data/app.db
```

Valide a configuracao sem imprimir os segredos:

```bash
sh scripts/smoke_production.sh
```

## 5. Subir a aplicacao

```bash
docker compose -f docker-compose.production.yml up -d --build
docker compose -f docker-compose.production.yml ps
curl http://127.0.0.1:8000/health
```

A porta 8000 fica vinculada somente a `127.0.0.1`, portanto nao fica exposta
diretamente na internet.

## 6. Configurar o Caddy

Copie `deploy/Caddyfile.example` para `/etc/caddy/Caddyfile` e troque
`pedidos.seudominio.com.br` pelo dominio real:

```bash
sudo cp deploy/Caddyfile.example /etc/caddy/Caddyfile
sudo editor /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
curl https://SEU_DOMINIO/health
```

O Caddy obtem e renova automaticamente o certificado TLS quando o DNS aponta
para a VPS e as portas 80 e 443 estao acessiveis.

## 7. Configurar o webhook da Meta

No painel da Meta, configure:

- URL: `https://SEU_DOMINIO/webhook/whatsapp`
- Verify token: o mesmo valor de `WHATSAPP_VERIFY_TOKEN`
- Campo assinado: `messages`

O `/health` e o webhook sao publicos. Para consultar `/pedidos`, envie a chave
somente no header `X-Admin-API-Key`.

## 8. Backup

Execute um backup manual a partir da raiz do repositorio:

```bash
sh scripts/backup_db.sh
```

O arquivo sera criado em `backups/app-YYYYMMDD-HHMMSS.db`. Copie os backups
periodicamente para outro servidor ou armazenamento externo.

Para executar diariamente as 03:00, abra `crontab -e` e adicione:

```cron
0 3 * * * cd /opt/cardapio-whatsapp-template && /bin/sh scripts/backup_db.sh >> /var/log/cardapio-backup.log 2>&1
```

Garanta que o usuario do cron tenha permissao de leitura em `data/app.db` e
escrita em `backups/`. Monitore o log e teste regularmente a restauracao.
