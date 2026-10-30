import pandas as pd
import json

temas = pd.read_csv('temas.csv').set_index('tema_id')
fv = pd.read_csv('folha_verdade.csv')

print(f"Total na folha verdade: {len(fv)}")
print(f"Fora da taxonomia: {fv['fora_da_taxonomia'].sum()} ({fv['fora_da_taxonomia'].mean():.1%})")

# Analisar disciplina dos temas centrais
validos = fv[fv['fora_da_taxonomia'] == 0]
discs = [temas.loc[int(tid), 'disciplina'] for tid in validos['tema_central_id']]
print("\nDisciplinas dos temas centrais válidos:")
print(pd.Series(discs).value_counts())

print("\nTemas centrais mais frequentes (Top 10):")
print(validos['tema_central_caminho'].value_counts().head(10))
