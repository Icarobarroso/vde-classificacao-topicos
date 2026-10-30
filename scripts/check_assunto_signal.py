import json
import pandas as pd
from src.taxonomy import Taxonomy

tax = Taxonomy('temas.csv')
fv = pd.read_csv('folha_verdade.csv')
questoes = {q['id']: q for q in (json.loads(line) for line in open('questoes.jsonl', encoding='utf-8'))}

# Verificar se o assunto_origem ou disciplina_origem casa com o título do tema
match_direto = 0
match_mesmo_ramo = 0
total_valid = 0

for _, r in fv[fv['fora_da_taxonomia'] == 0].iterrows():
    total_valid += 1
    qid = r['id']
    q = questoes[qid]
    
    gold_central = int(r['tema_central_id'])
    gold_extras = [int(x) for x in str(r['extras_ids']).split(';') if x and x != 'nan']
    
    assunto = str(q.get('assunto_origem', '')).strip().lower()
    disc = str(q.get('disciplina_origem', '')).strip().lower()
    
    # Procurar nós em temas.csv que contenham o assunto_origem
    candidatos = []
    for tid in tax.active_ids:
        node = tax.nodes[tid]
        tit = node['titulo'].lower()
        if assunto and (assunto in tit or tit in assunto):
            candidatos.append(tid)
            
    # Verificar se algum candidato é compatível com o gabarito
    certo = any(tax.evaluate_prediction('publicar', c, 0, gold_central, gold_extras) for c in candidatos)
    if certo:
        match_mesmo_ramo += 1
        
print(f"Total válidos: {total_valid}")
print(f"Questões onde assunto_origem casa diretamente com o tema certo (mesmo ramo): {match_mesmo_ramo} / {total_valid} ({match_mesmo_ramo/total_valid:.1%})")
