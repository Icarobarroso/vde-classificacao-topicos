import json
import pandas as pd

questoes = {q['id']: q for q in (json.loads(line) for line in open('questoes.jsonl', encoding='utf-8'))}
fv = pd.read_csv('folha_verdade.csv')

erros_ids = ['Q0028', 'Q0077', 'Q0099', 'Q0202', 'Q0208', 'Q0230', 'Q0275', 'Q0286', 'Q0313', 'Q0315', 'Q0316', 'Q0320', 'Q0345']

print("=== Analisando os comandos e perguntas dos erros ===")
for qid in erros_ids:
    q = questoes[qid]
    r = fv[fv['id'] == qid].iloc[0]
    print(f"\n--- {qid} | Real: {r['tema_central_caminho']} (Extras: {r['extras_ids']}) ---")
    print("Origem:", q.get('disciplina_origem'), "->", q.get('assunto_origem'))
    print("Comando:", q.get('comando'))
    alts = list(q.get('alternativas', {}).values())
    print("Exemplos de alternativas:", alts[:2])
