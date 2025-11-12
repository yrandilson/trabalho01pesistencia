import httpx   # Biblioteca para fazer requisições HTTP (como um navegador)
import random  # Biblioteca para gerar números aleatórios (para os preços)
import os      # Para operações do sistema (usado para limpar o arquivo antigo antes do teste)

URL = "http://localhost:8000"  # Endereço onde a API está rodando

def testar():
    # Abre um cliente HTTP que será fechado automaticamente ao final do bloco 'with'
    with httpx.Client(base_url=URL, timeout=10) as client:
        
        print(">>> 1. Gerando 35 registros...")
        # Loop de 1 a 35 para garantir que temos mais de 30 registros (exigência)
        for i in range(1, 36):
            # Gera um preço aleatório entre 10.0 e 1000.0, arredondado para 2 casas decimais
            preco = round(random.uniform(10.0, 1000.0), 2)
            # Faz um POST para criar o produto
            client.post("/api/items", json={"nome": f"Produto {i:02d}", "preco": preco})
        
        # Verifica quantos itens foram criados fazendo um GET na lista total
        total = len(client.get("/api/items").json())
        print(f"OK. Total de produtos no banco: {total}")

        print("\n>>> 2. Testando Estatísticas (Exigências)...")
        # Testa e imprime o resultado de cada rota de estatística
        print("Maior Preço:", client.get("/stats/maior").json())
        print("Menor Preço:", client.get("/stats/menor").json())
        
        media = client.get("/stats/media").json()['media']
        print(f"Média Preços: {media:.2f}")
        
        acima = client.get("/stats/acima-media").json()
        # Mostra a quantidade e um exemplo de produto que está acima da média
        print(f"Qtd Acima/Igual Média: {len(acima)} (Exemplo: {acima[0]['nome']} - R${acima[0]['preco']})")
        
        abaixo = client.get("/stats/abaixo-media").json()
        # Mostra a quantidade e um exemplo de produto que está abaixo da média
        print(f"Qtd Abaixo Média: {len(abaixo)} (Exemplo: {abaixo[0]['nome']} - R${abaixo[0]['preco']})")

        print("\n>>> 3. Teste de Concorrência (Lock)...")
        # Faz 5 requisições seguidas rapidamente para ver se o servidor aguenta (testa o Lock)
        for _ in range(5):
            client.post("/api/items", json={"nome": "Item Concorrente", "preco": 999.99})
        print("Finalizado sem erros de acesso simultâneo.")

# Bloco principal que executa quando rodamos o arquivo
if __name__ == "__main__":
    # Tenta remover o arquivo 'db.csv' antigo para começar o teste do zero
    try:
        if os.path.exists("db.csv"):
            os.remove("db.csv")
            print("Banco de dados anterior limpo.")
    except Exception as e:
        print(f"Aviso: Não foi possível limpar o banco antigo ({e})")
    
    # Chama a função de teste
    testar()