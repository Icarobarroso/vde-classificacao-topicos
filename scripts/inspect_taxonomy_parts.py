import pandas as pd
import re

temas = pd.read_csv('temas.csv')
print("=== Temas de Direito Penal - Legislação Especial ===")
leg_esp = temas[temas['disciplina'].str.contains('Especial', case=False, na=False)]
for _, r in leg_esp.iterrows():
    print(f"ID {r['tema_id']} | Nível {r['nivel']} | {r['caminho']}")

print("\n=== Temas de Criminologia ===")
crim = temas[temas['disciplina'] == 'Criminologia']
for _, r in crim.iterrows():
    print(f"ID {r['tema_id']} | Nível {r['nivel']} | {r['caminho']}")
