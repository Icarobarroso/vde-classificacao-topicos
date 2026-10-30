import json
import re
import unicodedata
import pandas as pd

from src.taxonomy import Taxonomy
from src.knowledge_base import CONCEPT_RULES

tax = Taxonomy('temas.csv')
fv = pd.read_csv('folha_verdade.csv')
questoes = {q['id']: q for q in (json.loads(line) for line in open('questoes.jsonl', encoding='utf-8'))}

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    text = text.lower()
    text = re.sub(r'[^a-z0-9_]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

acertos = 0
validos = 0
disparadas = 0

erros = []

for _, r in fv.iterrows():
    if r['fora_da_taxonomia'] == 1:
        continue
    validos += 1
    qid = r['id']
    q = questoes[qid]
    
    gold_central = int(r['tema_central_id'])
    gold_extras = [int(x) for x in str(r['extras_ids']).split(';') if x and x != 'nan']
    
    full_text = normalize_text(f"{q.get('enunciado_html','')} {q.get('comando','')} {str(q.get('alternativas',''))}")
    
    # Avaliar regras conceituais
    matched_tids = []
    for pattern, tid in CONCEPT_RULES:
        matches = re.findall(pattern, full_text)
        if matches:
            matched_tids.append((tid, len(matches)))
            
    if matched_tids:
        disparadas += 1
        # Pegar o tid com maior número de ocorrências
        best_tid = max(matched_tids, key=lambda x: x[1])[0]
        
        is_ok = tax.evaluate_prediction('publicar', best_tid, 0, gold_central, gold_extras)
        if is_ok:
            acertos += 1
        else:
            erros.append((qid, best_tid, gold_central, tax.nodes[best_tid]['caminho'], tax.nodes[gold_central]['caminho']))

print(f"Total válidos: {validos}")
print(f"Questões onde regras conceituais dispararam: {disparadas} / {validos} ({disparadas/validos:.1%})")
print(f"Acertos nas que dispararam: {acertos} / {disparadas} ({acertos/disparadas:.1%})")
print(f"Acerto absoluto na base inteira: {acertos} / {validos} ({acertos/validos:.1%})")

print(f"\nExemplo de erros ({len(erros)}):")
for qid, pred_tid, gold_tid, pred_cam, gold_cam in erros[:5]:
    print(f"[{qid}] Predito: {pred_cam} | Real: {gold_cam}")
