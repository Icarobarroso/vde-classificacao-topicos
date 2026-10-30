import pandas as pd

temas = pd.read_csv('temas.csv')
for disc in ['Processo Penal', 'Penal']:
    print(f"\n=== Temas Nível 1 de {disc} ===")
    sub = temas[(temas['disciplina'] == disc) & (temas['nivel'] == 1)]
    for _, r in sub.iterrows():
        print(f"ID {r['tema_id']} | {r['caminho']}")
