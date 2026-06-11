# Cardápio WhatsApp Template

Servidor backend para atendimento e pedidos 100% pelo WhatsApp, usando FastAPI,
SQLite e a WhatsApp Cloud API da Meta.

O projeto não possui mais cardápio público nem carrinho no navegador. O cliente
conversa com o número do restaurante, escolhe uma marmita, seleciona as carnes
disponíveis no dia, finaliza o pedido e recebe a confirmação no WhatsApp.

## Funcionalidades

- Webhook compatível com payloads da WhatsApp Cloud API
- Verificação do webhook pelo token configurado
- Deduplicação de mensagens pelo `wamid`
- Sessão e carrinho persistentes por número de telefone
- Marmitas e carnes do dia configuráveis em `data/cardapio.json`
- Fluxo de tipo de marmita, seleção de carnes, quantidade e checkout
- Validação de uma ou duas carnes conforme a marmita
- Entrega ou retirada, endereço, pagamento e observações
- Pedidos persistidos em SQLite antes da notificação da equipe
- Notificação organizada para o WhatsApp da equipe
- Endpoints JSON para consultar os pedidos
- Docker Compose e script simples de deploy para VPS

## Estrutura

```text
.
├── web_app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── config/
│   └── settings.py
├── core/
│   └── database.py
├── data/
│   └── cardapio.json
├── services/
│   ├── whatsapp_client.py
│   ├── menu_service.py
│   ├── session_service.py
│   └── order_service.py
├── scripts/
│   ├── init_db.py
│   ├── test_whatsapp_flow.py
│   └── deploy_vps.sh
├── tests/
└── legacy_static/
```

`legacy_static/` contém a versão anterior do site. Ela está arquivada apenas
como referência e não é servida pela aplicação FastAPI.

## Requisitos

- Python 3.11 ou mais recente
- Conta Meta Developer com WhatsApp Cloud API configurada
- Número habilitado na Cloud API
- Uma URL HTTPS pública para receber o webhook

## Configuração local

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências e crie a configuração local:

```bash
pip install -r requirements.txt
cp .env.example .env
```

No Windows, o equivalente é:

```powershell
Copy-Item .env.example .env
```

Edite `.env` com os dados da aplicação Meta. Depois inicialize o banco:

```bash
python scripts/init_db.py
```

Suba o servidor:

```bash
uvicorn web_app:app --reload --host 127.0.0.1 --port 8000
```

Teste a saúde em `http://127.0.0.1:8000/health`.

## Variáveis de ambiente

As variáveis disponíveis estão documentadas em `.env.example`:

```dotenv
APP_NAME=Cardapio WhatsApp Template
ENVIRONMENT=development
DATABASE_URL=sqlite:///./data/app.db

WHATSAPP_VERIFY_TOKEN=troque_este_token
WHATSAPP_ACCESS_TOKEN=coloque_o_token_da_meta
WHATSAPP_PHONE_NUMBER_ID=coloque_o_phone_number_id
WHATSAPP_GRAPH_API_VERSION=v23.0

RESTAURANT_NAME=Sabor Brasileiro
RESTAURANT_WHATSAPP_NUMBER=5511999999999
RESTAURANT_STAFF_WHATSAPP_NUMBER=5511999999999
DELIVERY_FEE=5.00

PUBLIC_BASE_URL=https://cardapio.seudominio.com.br
```

Nunca versione `.env`, tokens reais, bancos SQLite ou logs com dados de
clientes. Esses arquivos já estão cobertos pelo `.gitignore`.

## Endpoints

### `GET /health`

Retorna o estado da aplicação, ambiente e conexão com o SQLite.

### `GET /webhook/whatsapp`

Endpoint de verificação da Meta. Lê `hub.mode`, `hub.verify_token` e
`hub.challenge`. Retorna o challenge em texto puro quando o token confere.

### `POST /webhook/whatsapp`

Recebe eventos da Meta, ignora mensagens duplicadas, persiste mensagens de
entrada e processa o atendimento. Eventos sem mensagem são aceitos com HTTP
200. Tipos que não sejam texto recebem uma orientação ao cliente.

### `GET /pedidos`

Lista os pedidos mais recentes em JSON. Aceita `limit` entre 1 e 200.

### `GET /pedidos/{pedido_id}`

Retorna os detalhes de um pedido ou HTTP 404.

Os endpoints `/pedidos` são administrativos e deliberadamente simples nesta
primeira versão. Proteja-os no proxy reverso ou adicione autenticação antes de
expor o serviço publicamente.

## Configurar o webhook na Meta

No painel do aplicativo Meta:

1. Configure a URL como `https://SEU_DOMINIO/webhook/whatsapp`.
2. Use como verify token o valor de `WHATSAPP_VERIFY_TOKEN`.
3. Assine o campo `messages`.
4. Confirme que o domínio possui HTTPS válido e encaminha para a aplicação.

Para desenvolvimento local, use um túnel HTTPS temporário e informe a URL
pública gerada no painel da Meta.

## Cardápio de marmitas do dia

O restaurante trabalha com duas opções:

- Marmita pequena, com exatamente 1 carne, por R$ 21,00.
- Marmita com 2 carnes, com exatamente 2 carnes diferentes, por R$ 23,00.

Edite `data/cardapio.json` para trocar as carnes disponíveis. Cada tipo de
marmita e cada carne deve possuir um `id` estável e único:

```json
{
  "tipos_marmita": [
    {
      "id": "marmita-pequena-1-carne",
      "nome": "Marmita pequena",
      "quantidade_carnes": 1,
      "preco": 21.0
    }
  ],
  "carnes_do_dia": [
    {
      "id": "churrasco",
      "nome": "Churrasco",
      "fixo": true
    },
    {
      "id": "frango",
      "nome": "Frango",
      "fixo": false
    }
  ]
}
```

O churrasco é a opção fixa padrão. Se ele for removido por engano do JSON, o
serviço o inclui novamente na inicialização. As outras carnes podem ser
substituídas diariamente em `carnes_do_dia`.

Reinicie a aplicação depois de editar o arquivo. O serviço lista tipos de
marmita e carnes, busca ambos por número ou ID e aceita escolhas como `1 e 2`,
`1,2`, `1 2` e `1/2`.

Uma evolução futura poderá permitir atualizar o cardápio do dia por painel
administrativo ou por um comando interno e autorizado no próprio WhatsApp.

## Notificação da equipe

Após a confirmação, o pedido é salvo e o servidor tenta enviar o resumo para
`RESTAURANT_STAFF_WHATSAPP_NUMBER`.

A Cloud API não funciona como WhatsApp Web e não envia mensagens para grupos.
Além disso, uma mensagem ativa para a equipe pode ser recusada fora da janela
de atendimento. Em produção, pode ser necessário criar e aprovar um template
da Meta para essa notificação.

Se a Meta recusar o envio:

- o pedido continua salvo;
- `staff_notification_status` fica como `failed`;
- o detalhe é armazenado em `staff_notification_error`.

## Testes

Inicialização e simulação completa sem chamar a API real:

```bash
python scripts/init_db.py
python scripts/test_whatsapp_flow.py
```

Testes unitários:

```bash
pytest
```

Validação de sintaxe:

```bash
python -m compileall .
```

## Docker

Crie o `.env` e execute:

```bash
docker compose up -d --build
```

O serviço fica disponível na porta `8000`. O banco é persistido no volume
Docker `app_data`, em `/app/storage/app.db`.

Consulte os logs sem expor tokens:

```bash
docker compose logs -f app
```

## Deploy em VPS

Fluxo inicial recomendado:

1. Instale Git, Docker Engine e Docker Compose.
2. Clone o repositório em `/opt/cardapio-whatsapp-template`.
3. Copie `.env.example` para `.env` e configure os valores reais.
4. Execute `docker compose up -d --build`.
5. Configure Nginx ou Caddy como proxy reverso com HTTPS.
6. Cadastre a URL pública do webhook na Meta.

Para atualizações:

```bash
chmod +x scripts/deploy_vps.sh
PROJECT_DIR=/opt/cardapio-whatsapp-template scripts/deploy_vps.sh
```

O script usa `git pull --ff-only`, reconstrói os containers e preserva o volume
do SQLite. Faça backup periódico do volume e migre para um banco gerenciado
quando o volume de pedidos justificar.
