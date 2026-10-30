import os
import json
import numpy as np
import pandas as pd
from fastembed import TextEmbedding
from sklearn.metrics.pairwise import cosine_similarity

from src.taxonomy import Taxonomy
from src.theme_indexer import ThemeIndexer
from src.preprocessor import prepare_question_text, extract_legal_entities

print("Inicializando modelo de embedding...")
embed_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

tax = Taxonomy('temas.csv')
indexer = ThemeIndexer(tax)
active_tids = indexer.active_tids

# Gerar textos enriquecidos para os temas
print(f"Gerando textos para {len(active_tids)} temas...")
theme_docs = [indexer.get_document(tid) for tid in active_tids]

print("Computando embeddings dos temas...")
theme_embeddings = list(embed_model.embed(theme_docs))
theme_embeddings = np.array(theme_embeddings)
print("Shape embeddings temas:", theme_embeddings.shape)

# Salvar cache dos temas
os.makedirs('cache', exist_ok=True)
np.save('cache/theme_embeddings.npy', theme_embeddings)
np.save('cache/active_tids.npy', np.array(active_tids))

# Carregar questoes da folha verdade
fv = pd.read_csv('folha_verdade.csv')
questoes = {q['id']: q for q in (json.loads(line) for line in open('questoes.jsonl', encoding='utf-8'))}

print(f"Processando {len(fv)} questoes da folha verdade...")
q_texts = [prepare_question_text(questoes[qid]) for qid in fv['id']]

q_embeddings = list(embed_model.embed(q_texts))
q_embeddings = np.array(q_embeddings)
print("Shape embeddings questoes:", q_embeddings.shape)
np.save('cache/fv_q_embeddings.npy', q_embeddings)

# Calcular similaridade de cosseno
sim_matrix = cosine_similarity(q_embeddings, theme_embeddings) # shape: (100, 375)

# Avaliar acuracia top 1 e top 3
top1_ok = 0
top3_ok = 0
top5_ok = 0

for i, row in fv.iterrows():
    qid = row['id']
    gold_fora = int(row['fora_da_taxonomia'])
    gold_central = int(row['tema_central_id']) if pd.notna(row['tema_central_id']) else None
    gold_extras = [int(x) for x in str(row['extras_ids']).split(';') if x and x != 'nan']
    
    scores = sim_matrix[i]
    top_indices = np.argsort(-scores)[:5]
    top_preds = [active_tids[idx] for idx in top_indices]
    
    if gold_fora == 1:
        # Pular por enquanto ou tratar depois
        continue
        
    # Verificar top 1
    if tax.evaluate_prediction('publicar', top_preds[0], gold_fora, gold_central, gold_extras):
        top1_ok += 1
        
    # Verificar top 3
    if any(tax.evaluate_prediction('publicar', p, gold_fora, gold_central, gold_extras) for p in top_preds[:3]):
        top3_ok += 1
        
    # Verificar top 5
    if any(tax.evaluate_prediction('publicar', p, gold_fora, gold_central, gold_extras) for p in top_preds[:5]):
        top5_ok += 1

n_valid = (fv['fora_da_taxonomia'] == 0).sum()
print(f"\n--- Resultados Embeddings Dense puros (sem regras ainda) ---")
print(f"Top 1 Acurácia: {top1_ok} / {n_valid} ({top1_ok / n_valid:.1%})")
print(f"Top 3 Acurácia: {top3_ok} / {n_valid} ({top3_ok / n_valid:.1%})")
print(f"Top 5 Acurácia: {top5_ok} / {n_valid} ({top5_ok / n_valid:.1%})")
