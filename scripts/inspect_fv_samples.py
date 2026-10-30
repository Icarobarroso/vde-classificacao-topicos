import json
import pandas as pd
from src.taxonomy import Taxonomy
from src.preprocessor import clean_html

tax = Taxonomy('temas.csv')
fv = pd.read_csv('folha_verdade.csv')
questoes = {q['id']: q for q in (json.loads(line) for line in open('questoes.jsonl', encoding='utf-8'))}

print("=== Inspecionando 10 questões da Folha Verdade e seus temas reais ===")
for idx, r in fv.head(10).iterrows():
    qid = r['id']
    q = questoes[qid]
    tid = r['tema_central_id']
    caminho = r['tema_central_caminho']
    fora = r['fora_da_taxonomia']
    
    enunc = clean_html(q.get('enunciado_html', ''))[:160]
    cmd = clean_html(q.get('comando', ''))
    assunto = q.get('assunto_origem', '')
    
    print(f"[{qid}] Fora={fora} | Gabarito: {caminho}")
    print(f"   Origem: {assunto}")
    print(f"   Comando: {cmd}")
    print(f"   Enunciado: {enunc}...")
    print("-" * 70)
