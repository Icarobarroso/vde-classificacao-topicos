import pandas as pd

temas = pd.read_csv('temas.csv')

def find_temas(query):
    return temas[temas['caminho'].str.contains(query, case=False, na=False)][['tema_id', 'nivel', 'caminho', 'status']]

print("=== Busca por drogas ===")
print(find_temas('droga'))

print("\n=== Busca por execucao ===")
print(find_temas('execu'))

print("\n=== Busca por aplicacao da lei ===")
print(find_temas('aplica'))

print("\n=== Busca por pena ===")
print(find_temas('pena').head(15))

print("\n=== Busca por funcionario / responsabilidade ===")
print(find_temas('funcion'))
