# FastAPI Chat (refatorado)

Este repositório contém um chat em tempo real simples usando FastAPI, Motor (MongoDB async) e WebSockets.

Principais mudanças nesta refatoração:

- Código modularizado em arquivos: `config.py`, `database.py`, `models.py`, `ws_manager.py`, `routes/messages.py`.
- Uso de modelos Pydantic (`MessageIn`, `MessageOut`) para validação de entrada/saída.
- Tratamento de erro 400 quando `before_id` inválido.
- Evita persistir mensagens vazias.

## Configuração

1. Crie um cluster no MongoDB Atlas e configure usuário e network access.
2. Crie um arquivo `.env` na raiz do projeto com a variável:

```bash
MONGO_URL="sua-string-de-conexao"
MONGO_DB=chatdb
```

## Executando localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abra o cliente em <http://localhost:8000> e a documentação interativa em <http://localhost:8000/docs>

## Endpoints

- WebSocket: `ws://localhost:8000/ws/{room}`
- Histórico (REST): `GET /rooms/{room}/messages?limit=20`
- Enviar (REST): `POST /rooms/{room}/messages` (use JSON com `username` e `content`)
