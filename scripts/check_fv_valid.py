import pandas as pd
import json

temas = pd.read_csv('temas.csv').set_index('tema_id')
fv = pd.read_csv('folha_verdade.csv')
questoes = {q['id']: q for q in (json.loads(line) for line in open('questoes.jsonl', encoding='utf-8'))}

fv_dentro = fv[fv['fora_da_taxonomia'] == 0].copy()
fv_dentro['tema_central_id'] = fv_dentro['tema_central_id'].astype(int)

# Inspecionar níveis dos temas atribuídos
niveis = [temas.loc[tid, 'nivel'] for tid in fv_dentro['tema_central_id']]
print("Distribuicao de niveis na Folha Verdade (temas centrais):")
print(pd.Series(niveis).value_counts())

# Inspecionar presenca de extras
tem_extras = fv_dentro['extras_ids'].notna()
print(f"\nQuestoes com extras: {tem_extras.sum()} / {len(fv_dentro)}")

# Comparar assunto de origem com tema central atribuido
match_assunto = 0
for idx, r in fv_dentro.head(15).iterrows():
    qid = r['id']
    q = questoes[qid]
    tid = r['tema_central_id']
    t_row = temas.loc[tid]
    print(f"ID {qid}: Origem='{q.get('assunto_origem')}' --> Real='{t_row['caminho']}'")
