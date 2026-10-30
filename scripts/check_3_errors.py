import pandas as pd
import json
from src.taxonomy import Taxonomy
from scripts.test_tuning import classify_weighted, fv, questoes

tax = Taxonomy('temas.csv')
for _, r in fv.iterrows():
    qid = r['id']
    q = questoes[qid]
    gold_fora = int(r['fora_da_taxonomia'])
    gold_central = int(r['tema_central_id']) if pd.notna(r['tema_central_id']) else None
    gold_extras = [int(x) for x in str(r['extras_ids']).split(';') if x and x != 'nan']
    p = classify_weighted(q, threshold_score=5.0, threshold_margin=10.0)
    if p['decisao'] == 'publicar':
        ok = tax.evaluate_prediction('publicar', p['tema_central_id'], gold_fora, gold_central, gold_extras)
        if not ok:
            pred_cam = tax.nodes[p['tema_central_id']]['caminho']
            gold_cam = tax.nodes[gold_central]['caminho'] if gold_central else "FORA"
            print(f"ERRO: {qid} | Pred: {p['tema_central_id']} ({pred_cam}) | Gold: {gold_central} ({gold_cam})")
