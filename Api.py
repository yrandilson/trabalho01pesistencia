# Importa as ferramentas necessárias:
from fastapi import FastAPI, HTTPException  # FastAPI para criar a API, HTTPException para erros (ex: 404 não encontrado)
from pydantic import BaseModel  # Pydantic para definir o formato dos dados (validação)
import pandas as pd  # Pandas para manipular a tabela de dados (CSV) facilmente
from threading import Lock  # Lock para evitar problemas quando vários usuários acessam ao mesmo tempo
import os  # OS para verificar se o arquivo CSV existe no sistema

app = FastAPI()  # Cria a aplicação FastAPI
LOCK = Lock()  # Cria um 'cadeado' para controlar o acesso concorrente ao arquivo
CSV = "db.csv"  # Nome do arquivo onde os dados serão salvos

# Define o modelo de dados para um Item (produto)
class Item(BaseModel):
    nome: str    # O item deve ter um nome (texto)
    preco: float # O item deve ter um preço (número decimal)

# Função auxiliar para carregar os dados do CSV para um DataFrame do Pandas
def get_df():
    if not os.path.exists(CSV):  # Se o arquivo CSV NÃO existir...
        # Cria um DataFrame vazio com as colunas 'id', 'nome', 'preco' e salva no arquivo
        pd.DataFrame(columns=["id", "nome", "preco"]).to_csv(CSV, index=False)
    return pd.read_csv(CSV)  # Lê o arquivo CSV e retorna como um DataFrame

# Função auxiliar para salvar o DataFrame de volta no CSV
def save_df(df):
    df.to_csv(CSV, index=False)  # Salva o DataFrame no arquivo CSV, sem incluir o índice do pandas

# --- ROTAS DA API (End-points) ---

# Rota para CRIAR um novo item (POST /api/items)
@app.post("/api/items", status_code=201)  # status_code=201 indica "Criado com sucesso"
def criar(item: Item):
    with LOCK:  # Ativa o cadeado: só uma requisição pode executar este bloco por vez
        df = get_df()  # Carrega os dados atuais
        # Calcula o novo ID: se estiver vazio é 1, senão é o maior ID atual + 1
        novo_id = 1 if df.empty else df["id"].max() + 1
        # Cria um novo DataFrame com o item recebido e o novo ID
        novo_item_df = pd.DataFrame([{"id": novo_id, **item.dict()}])
        # Adiciona o novo item ao DataFrame principal
        df = pd.concat([df, novo_item_df], ignore_index=True)
        save_df(df)  # Salva os dados atualizados no CSV
        return df.iloc[-1].to_dict()  # Retorna o último item adicionado como dicionário

# Rota para LISTAR todos os itens (GET /api/items)
@app.get("/api/items")
def listar():
    # Carrega os dados e converte para uma lista de dicionários (formato JSON)
    return get_df().to_dict(orient="records")

# Rota para OBTER um item específico pelo ID (GET /api/items/{id})
@app.get("/api/items/{id}")
def obter(id: int):
    df = get_df()  # Carrega os dados
    row = df[df["id"] == id]  # Filtra as linhas onde a coluna 'id' é igual ao id solicitado
    if row.empty: raise HTTPException(404)  # Se não encontrou nada, retorna erro 404 Not Found
    return row.iloc[0].to_dict()  # Retorna a primeira (e única) linha encontrada como dicionário

# Rota para DELETAR um item pelo ID (DELETE /api/items/{id})
@app.delete("/api/items/{id}")
def deletar(id: int):
    with LOCK:  # Usa o cadeado para evitar conflitos na deleção
        df = get_df()
        if df[df["id"] == id].empty: raise HTTPException(404)  # Se não existe, erro 404
        # Salva o DataFrame mantendo APENAS as linhas onde o 'id' é DIFERENTE do id solicitado
        save_df(df[df["id"] != id])
        return {"msg": "Deletado"}  # Confirmação de sucesso

# --- SERVIÇOS DE ESTATÍSTICAS (Exigências do Trabalho) ---

# Rota para o produto de MAIOR preço
@app.get("/stats/maior")
def maior_preco():
    df = get_df()
    if df.empty: return {}  # Se não tem dados, retorna vazio
    # Encontra o índice da linha com o preço máximo e retorna essa linha como dicionário
    return df.loc[df["preco"].idxmax()].to_dict()

# Rota para o produto de MENOR preço
@app.get("/stats/menor")
def menor_preco():
    df = get_df()
    if df.empty: return {}
    # Encontra o índice da linha com o preço mínimo e retorna essa linha
    return df.loc[df["preco"].idxmin()].to_dict()

# Rota para a MÉDIA de preços
@app.get("/stats/media")
def media_preco():
    df = get_df()
    # Calcula a média da coluna 'preco'. Se vazio retorna 0.0
    return {"media": 0.0 if df.empty else df["preco"].mean()}

# Rota para lista de produtos ACIMA (ou igual) da média
@app.get("/stats/acima-media")
def acima_media():
    df = get_df()
    if df.empty: return []
    # Filtra: mantém linhas onde 'preco' >= média dos preços
    return df[df["preco"] >= df["preco"].mean()].to_dict(orient="records")

# Rota para lista de produtos ABAIXO da média
@app.get("/stats/abaixo-media")
def abaixo_media():
    df = get_df()
    if df.empty: return []
    # Filtra: mantém linhas onde 'preco' < média dos preços
    return df[df["preco"] < df["preco"].mean()].to_dict(orient="records")