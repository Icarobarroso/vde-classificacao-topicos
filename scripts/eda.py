import json
import pandas as pd

temas = pd.read_csv('temas.csv')
print("=== Temas inativos ===")
print(temas[temas['status'] == 'inactive'][['tema_id', 'titulo', 'caminho']])

fv = pd.read_csv('folha_verdade.csv')
questoes = {q['id']: q for q in (json.loads(line) for line in open('questoes.jsonl', encoding='utf-8'))}

print("\n=== Questoes fora da taxonomia na folha verdade (fora_da_taxonomia == 1) ===")
for idx, r in fv[fv['fora_da_taxonomia'] == 1].iterrows():
    qid = r['id']
    q = questoes[qid]
    enunc = q.get('enunciado_html', '').replace('<br>', ' ').replace('<p>', ' ')[:140]
    print(f"ID: {qid} | Orig: {q.get('disciplina_origem')} -> {q.get('assunto_origem')}")
    print(f"   Enunciado: {enunc}...")
    print("-" * 60)
