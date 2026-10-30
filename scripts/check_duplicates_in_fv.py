import pandas as pd
import json

temas = pd.read_csv('temas.csv').set_index('tema_id')
fv = pd.read_csv('folha_verdade.csv')

def check_cases(keyword):
    print(f"\n=== Analisando keyword '{keyword}' na folha verdade ===")
    matches = fv[fv['tema_central_caminho'].str.contains(keyword, case=False, na=False)]
    for _, r in matches.iterrows():
        tid = int(r['tema_central_id'])
        extras = r['extras_ids']
        print(f"ID {r['id']} -> Central: {tid} ({temas.loc[tid, 'caminho']}) | Extras: {extras}")

check_cases("droga")
check_cases("execu")
check_cases("maria da penha")
check_cases("organiza")
check_cases("lavagem")
check_cases("abuso")
check_cases("recurso")
check_cases("jri")
