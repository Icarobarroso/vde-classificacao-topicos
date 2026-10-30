import json
import pandas as pd
import numpy as np

from src.taxonomy import Taxonomy
from src.classifier import ClassifierEngine

tax = Taxonomy('temas.csv')
clf = ClassifierEngine('temas.csv')

fv = pd.read_csv('folha_verdade.csv')
questoes = {q['id']: q for q in (json.loads(line) for line in open('questoes.jsonl', encoding='utf-8'))}

print("=== Testando ClassifierEngine nas 100 questoes da Folha Verdade ===")

for threshold in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]:
    pub_count = 0
    pub_correct = 0
    rev_count = 0
    fora_count = 0
    fora_correct = 0
    
    erros_pub = []
    
    for idx, row in fv.iterrows():
        qid = row['id']
        q = questoes[qid]
        
        gold_fora = int(row['fora_da_taxonomia'])
        gold_central = int(row['tema_central_id']) if pd.notna(row['tema_central_id']) else None
        gold_extras = [int(x) for x in str(row['extras_ids']).split(';') if x and x != 'nan']
        
        pred = clf.predict(q, pub_threshold=threshold)
        dec = pred['decisao']
        tid = pred['tema_central_id']
        
        is_ok = tax.evaluate_prediction(dec, tid, gold_fora, gold_central, gold_extras)
        
        if dec == 'publicar':
            pub_count += 1
            if is_ok:
                pub_correct += 1
            else:
                erros_pub.append((qid, tid, gold_central, gold_fora, pred['confianca']))
        elif dec == 'revisar':
            rev_count += 1
        elif dec == 'fora':
            fora_count += 1
            if is_ok:
                fora_correct += 1
                
    prec_pub = pub_correct / pub_count if pub_count > 0 else 0.0
    print(f"Limiar: {threshold:.2f} | Publicar: {pub_count:2d} (Precisão: {prec_pub:.1%}) | Revisar: {rev_count:2d} | Fora: {fora_count:2d} (Acertos Fora: {fora_correct}) | Erros Pub: {len(erros_pub)}")

