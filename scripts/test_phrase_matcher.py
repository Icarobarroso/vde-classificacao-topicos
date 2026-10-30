import json
import re
import unicodedata
import pandas as pd
from typing import Dict, List, Set, Tuple

from src.taxonomy import Taxonomy

tax = Taxonomy('temas.csv')
fv = pd.read_csv('folha_verdade.csv')
questoes = {q['id']: q for q in (json.loads(line) for line in open('questoes.jsonl', encoding='utf-8'))}

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Remover acentos
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    text = text.lower()
    # Substituir pontuacao por espacos
    text = re.sub(r'[^a-z0-9_]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# Criar dicionário de busca para cada tema ativo
# Cada tema terá uma lista de palavras-chave / frases-chave com pesos
theme_keywords = {}
for tid in tax.active_ids:
    node = tax.nodes[tid]
    tit_norm = normalize_text(node['titulo'])
    cam_norm = normalize_text(node['caminho'])
    
    # Frases canônicas do tema
    phrases = []
    # O próprio título se tiver >= 4 chars
    if len(tit_norm) >= 4 and tit_norm not in ['penal', 'processo penal', 'criminologia', 'direito penal']:
        phrases.append((tit_norm, 10.0))
        
    # Se o título tiver partes separadas por vírgula ou 'e'
    parts = re.split(r'[,e/]| e ', node['titulo'])
    for p in parts:
        pn = normalize_text(p)
        if len(pn) >= 4 and pn not in ['penal', 'processo penal', 'criminologia']:
            phrases.append((pn, 8.0))
            
    theme_keywords[tid] = {
        'titulo': tit_norm,
        'caminho': cam_norm,
        'phrases': phrases,
        'disciplina': node['disciplina'],
        'nivel': node['nivel']
    }

print("Dicionário de temas criado.")

# Testar em cada questão da folha verdade
acertos_top1 = 0
acertos_top3 = 0
validos = 0

for _, r in fv.iterrows():
    if r['fora_da_taxonomia'] == 1:
        continue
    validos += 1
    
    qid = r['id']
    q = questoes[qid]
    gold_central = int(r['tema_central_id'])
    gold_extras = [int(x) for x in str(r['extras_ids']).split(';') if x and x != 'nan']
    
    full_text = normalize_text(f"{q.get('enunciado_html','')} {q.get('comando','')} {str(q.get('alternativas',''))}")
    
    # Pontuar temas
    scores = {}
    for tid, data in theme_keywords.items():
        score = 0.0
        # Checar frases
        for ph, weight in data['phrases']:
            if ph in full_text:
                # Contar ocorrencias
                count = full_text.count(ph)
                score += weight * min(count, 3)
                
        if score > 0:
            scores[tid] = score
            
    # Rankear
    sorted_temas = sorted(scores.items(), key=lambda x: -x[1])
    top_tids = [t[0] for t in sorted_temas[:5]]
    
    if top_tids:
        if tax.evaluate_prediction('publicar', top_tids[0], 0, gold_central, gold_extras):
            acertos_top1 += 1
        if any(tax.evaluate_prediction('publicar', t, 0, gold_central, gold_extras) for t in top_tids[:3]):
            acertos_top3 += 1

print(f"Resultado do casamento de frases canônicas puras:")
print(f"Top 1: {acertos_top1} / {validos} ({acertos_top1/validos:.1%})")
print(f"Top 3: {acertos_top3} / {validos} ({acertos_top3/validos:.1%})")
