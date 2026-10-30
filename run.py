"""
Script de regeneração de publicacao.csv
Roda 100% determinístico e sem chamar modelo de linguagem em runtime.
Uso: python run.py
"""

import sys
import json
import time
import pandas as pd

from src.classifier import TopicClassifier

def main():
    start_time = time.time()
    print("Iniciando pipeline de classificação de tópicos jurídicos...")
    
    # 1. Carregar dados
    temas_path = "temas.csv"
    questoes_path = "questoes.jsonl"
    output_path = "publicacao.csv"
    
    print(f"Carregando taxonomia de {temas_path}...")
    clf = TopicClassifier(temas_path=temas_path)
    
    print(f"Lendo questões de {questoes_path}...")
    questoes = []
    with open(questoes_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                questoes.append(json.loads(line))
                
    total_q = len(questoes)
    print(f"Total de questões a classificar: {total_q}")
    
    # 2. Classificar cada questão
    resultados = []
    pub_count = 0
    rev_count = 0
    fora_count = 0
    
    for q in questoes:
        res = clf.predict(q)
        resultados.append(res)
        
        dec = res['decisao']
        if dec == 'publicar':
            pub_count += 1
        elif dec == 'revisar':
            rev_count += 1
        elif dec == 'fora':
            fora_count += 1
            
    # 3. Gerar DataFrame e validar regras do LEIA-ME
    df = pd.DataFrame(resultados)
    
    # Garantir colunas na ordem exata de entrega_modelo.csv:
    # id,decisao,tema_central_id,extras_ids,confianca,motivo
    expected_cols = ['id', 'decisao', 'tema_central_id', 'extras_ids', 'confianca', 'motivo']
    df = df[expected_cols]
    
    # Validar regras de integridade
    assert len(df) == total_q, f"Esperado {total_q} linhas, obtido {len(df)}"
    assert set(df['decisao'].unique()).issubset({'publicar', 'revisar', 'fora'}), "Decisão inválida detectada"
    
    # Salvar CSV em UTF-8
    df.to_csv(output_path, index=False, encoding='utf-8')
    elapsed = time.time() - start_time
    
    print("=" * 60)
    print(f"Classificação concluída com sucesso em {elapsed:.2f}s!")
    print(f"Arquivo gerado: {output_path} ({len(df)} linhas)")
    print(f"Distribuição das decisões:")
    print(f"  • publicar : {pub_count:3d} ({pub_count / total_q:.1%})")
    print(f"  • revisar  : {rev_count:3d} ({rev_count / total_q:.1%})")
    print(f"  • fora     : {fora_count:3d} ({fora_count / total_q:.1%})")
    print("=" * 60)

if __name__ == "__main__":
    main()
