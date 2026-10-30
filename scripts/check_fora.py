import json
import pandas as pd

temas = pd.read_csv('temas.csv')
questoes = {q['id']: q for q in (json.loads(line) for line in open('questoes.jsonl', encoding='utf-8'))}
fv = pd.read_csv('folha_verdade.csv')

print("Exemplos de temas de Penal:")
print(temas[temas['disciplina'] == 'Penal']['caminho'].head(20).tolist())

print("\n--- Analisando detalhadamente as 8 questoes fora da taxonomia ---")
for idx, r in fv[fv['fora_da_taxonomia'] == 1].iterrows():
    qid = r['id']
    q = questoes[qid]
    print(f"=== {qid} ===")
    print("Origem:", q.get('disciplina_origem'), "->", q.get('assunto_origem'))
    print("Enunciado:", q.get('enunciado_html')[:250])
    print("Comando:", q.get('comando'))
    print("Alternativas:", list(q.get('alternativas', {}).values())[:2])
