# 📦 API de Produtos com CSV

API REST simples para gerenciar produtos com persistência em arquivo CSV.

## 🚀 Tecnologias

- FastAPI
- Pandas
- Uvicorn
- HTTPX

## ⚡ Instalação

```bash
pip install fastapi uvicorn pandas httpx
```

## 🎯 Como Executar

**Terminal 1 - Servidor:**
```bash
uvicorn api:app --reload
```

**Terminal 2 - Testes:**
```bash
python cliente.py
```

## 📋 Rotas

### CRUD
- `POST /api/items` - Criar produto
- `GET /api/items` - Listar todos
- `GET /api/items/{id}` - Buscar por ID
- `DELETE /api/items/{id}` - Deletar produto

### Estatísticas
- `GET /stats/maior` - Produto mais caro
- `GET /stats/menor` - Produto mais barato
- `GET /stats/media` - Média de preços
- `GET /stats/acima-media` - Produtos acima da média
- `GET /stats/abaixo-media` - Produtos abaixo da média

## 📖 Documentação

Acesse: `http://localhost:8000/docs`

## 🧪 Testes Automáticos

O cliente gera 35 produtos automaticamente e testa todas as rotas.

## 📁 Estrutura

```
├── api_comentada.py       # Servidor FastAPI
├── cliente_comentado.py   # Testes automáticos
└── db.csv                 # Banco de dados (auto-gerado)
```
