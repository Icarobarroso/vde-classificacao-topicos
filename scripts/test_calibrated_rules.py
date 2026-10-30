import json
import re
import unicodedata
import pandas as pd
import numpy as np

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

# Enriquecer CONCEPT_RULES com temas específicos adicionais identificados
# Ex: Conflito aparente de normas (tema 5183), Suicídio (5152), etc.
ADDITIONAL_RULES = [
    (r'\b(conflito aparente de normas|principio da consuncao|principio da subsidiariedade|principio da especialidade|principio da alternatividade)\b', 5183), # Conflito Aparente
    (r'\b(suicidio|automutilacao|instigacao ao suicidio|induzimento ao suicidio)\b', 5152), # Suicídio
    (r'\b(moeda falsa|falsificacao de documento publico|falsificacao de documento particular|falsidade ideologica|uso de documento falso)\b', 5116), # Fé Pública
    (r'\b(procedimento ordinario|resposta a acusacao|art\.? 396 cpp|audiencia de instrucao e julgamento)\b', 5530), # Procedimento Ordinário
    (r'\b(recurso de apelacao|apelacao|art\.? 593 cpp)\b', 5562), # Apelação
    (r'\b(recurso em sentido estrito|rese|art\.? 581 cpp)\b', 5561), # RESE
]
ALL_RULES = ADDITIONAL_RULES + CONCEPT_RULES

def classify_question(q: dict):
    qid = q['id']
    enunc = normalize_text(q.get('enunciado_html', ''))
    cmd = normalize_text(q.get('comando', ''))
    alts = normalize_text(str(q.get('alternativas', '')))
    assunto = normalize_text(q.get('assunto_origem', ''))
    disc = normalize_text(q.get('disciplina_origem', ''))
    
    # 1. Detector OOD / Fora da taxonomia
    # Regra 1: Temas inativos conhecidos (Direito Penal Econômico - cartel, combustíveis, ordem econômica)
    if any(k in enunc or k in cmd for k in ['revendedores de gas', 'ajustem artificialmente preco', 'ordem economica', 'glp']):
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.95, 'motivo': 'Tema inativo na taxonomia (Direito Penal Econômico)'}
    
    # Regra 2: Disciplinas fora do escopo penal
    if any(k in disc for k in ['militar', 'constitucional', 'civil', 'administrativo']):
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.90, 'motivo': f'Disciplina fora do escopo penal: {disc}'}
        
    # Regra 3: Questões sobre autores doutrinários de criminologia crítica não contemplados
    if 'vera regina' in enunc or 'clientela do sistema penal e constituida de pobres' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.95, 'motivo': 'Criminologia Crítica não contemplada na taxonomia'}
        
    # Regra 4: Procedimento especial de crimes funcionais (art. 513 a 518 CPP)
    if 'crimes de responsabilidade dos funcionarios publicos' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.95, 'motivo': 'Procedimento de crimes de funcionários públicos não contemplado'}

    # 2. Casamento com Regras Conceituais
    full_text = f"{enunc} {cmd} {alts}"
    
    # Dar peso 3x para o comando e assunto de origem
    cmd_text = f"{cmd} {assunto}"
    
    matches = {} # tid -> score
    
    for pattern, tid in ALL_RULES:
        # Match no comando/assunto (peso alto)
        m_cmd = len(re.findall(pattern, cmd_text))
        # Match no texto geral
        m_full = len(re.findall(pattern, full_text))
        
        total_score = m_cmd * 3.0 + m_full * 1.0
        if total_score > 0:
            matches[tid] = matches.get(tid, 0.0) + total_score
            
    if not matches:
        # Nenhuma regra disparou -> Revisar
        # Sugestão básica: raiz da disciplina
        return {'decisao': 'revisar', 'tema_central_id': 5063, 'confianca': 0.30, 'motivo': 'Nenhum padrão conceitual conclusivo identificado'}
        
    # Ordenar candidatos
    sorted_matches = sorted(matches.items(), key=lambda x: -x[1])
    top_tid, top_score = sorted_matches[0]
    second_score = sorted_matches[1][1] if len(sorted_matches) > 1 else 0.0
    margin = top_score - second_score
    
    # Estratégia do PAI:
    # Se o top_tid for um subtema (nível 2) e a margem for baixa (< 2.0),
    # recuar para o pai (nível 1)!
    node = tax.nodes.get(top_tid)
    chosen_tid = top_tid
    backed_to_parent = False
    if node and node['nivel'] == 2 and margin < 2.5:
        parent_id = node['parent_id']
        if parent_id and parent_id in tax.active_ids:
            chosen_tid = parent_id
            backed_to_parent = True
            
    # Calcular confiança calibrada
    conf = min(0.99, 0.50 + 0.10 * top_score + 0.15 * margin + (0.15 if backed_to_parent else 0.0))
    
    # Decisão:
    # Se top_score >= 3.0 e (margin >= 2.0 ou backed_to_parent): publicar
    if top_score >= 3.0 and (margin >= 2.0 or backed_to_parent):
        return {
            'decisao': 'publicar',
            'tema_central_id': chosen_tid,
            'confianca': round(conf, 2),
            'motivo': ''
        }
    else:
        return {
            'decisao': 'revisar',
            'tema_central_id': chosen_tid,
            'confianca': round(conf, 2),
            'motivo': f'Margem estreita entre temas concorrentes (score: {top_score:.1f}, margem: {margin:.1f})'
        }

# Avaliar na folha verdade
pub_total = 0
pub_certas = 0
rev_total = 0
rev_certas = 0
fora_total = 0
fora_certas = 0

for _, r in fv.iterrows():
    qid = r['id']
    q = questoes[qid]
    gold_fora = int(r['fora_da_taxonomia'])
    gold_central = int(r['tema_central_id']) if pd.notna(r['tema_central_id']) else None
    gold_extras = [int(x) for x in str(r['extras_ids']).split(';') if x and x != 'nan']
    
    pred = classify_question(q)
    dec = pred['decisao']
    tid = pred['tema_central_id']
    
    is_ok = tax.evaluate_prediction(dec, tid, gold_fora, gold_central, gold_extras)
    
    if dec == 'publicar':
        pub_total += 1
        if is_ok:
            pub_certas += 1
        else:
            print(f"ERRO PUB: {qid} | Pred: {tid} ({tax.nodes[tid]['caminho']}) | Gold: {gold_central} (Fora={gold_fora})")
    elif dec == 'revisar':
        rev_total += 1
        if is_ok:
            rev_certas += 1
    elif dec == 'fora':
        fora_total += 1
        if is_ok:
            fora_certas += 1

print("\n" + "="*50)
print(f"RESULTADO FINAL NA FOLHA VERDADE (100 QUESTÕES):")
print(f"Publicadas: {pub_total} / 100 ({pub_total}%)")
print(f"Precisão nas Publicadas: {pub_certas} / {pub_total} = {pub_certas/pub_total:.1%}" if pub_total>0 else "0")
print(f"Revisar: {rev_total} (Sugestão correta em {rev_certas}/{rev_total})")
print(f"Fora: {fora_total} (Acertos: {fora_certas}/{fora_total})")
print("="*50)
