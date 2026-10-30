import re
import html
from typing import Dict, Any, List

# Regex para limpar HTML
RE_TAGS = re.compile(r'<[^>]+>')
RE_SPACES = re.compile(r'\s+')

# Dicionário de diplomas legais e expressões jurídicas fortes mapeados para palavras-chave canônicas
LEIS_MAP = {
    r'11\.?340': 'lei_maria_da_penha',
    r'maria\s+da\s+penha': 'lei_maria_da_penha',
    r'11\.?343': 'lei_de_drogas_trafico',
    r'6\.?368/76': 'lei_de_drogas_trafico',
    r'9\.?099': 'juizado_especial_criminal_jecrim',
    r'jecrim': 'juizado_especial_criminal_jecrim',
    r'7\.?210': 'lei_de_execucao_penal_lep',
    r'\blep\b': 'lei_de_execucao_penal_lep',
    r'13\.?869': 'abuso_de_autoridade',
    r'4\.?898/65': 'abuso_de_autoridade',
    r'8\.?072': 'crimes_hediondos',
    r'12\.?850': 'organizacoes_criminosas',
    r'9\.?613': 'lavagem_de_dinheiro_capitais',
    r'9\.?455': 'crime_de_tortura',
    r'10\.?826': 'estatuto_do_desarmamento_armas',
    r'9\.?503': 'codigo_de_transito_brasileiro_ctb',
    r'\bctb\b': 'codigo_de_transito_brasileiro_ctb',
    r'8\.?069': 'estatuto_da_crianca_e_do_adolescente_eca',
    r'\beca\b': 'estatuto_da_crianca_e_do_adolescente_eca',
    r'14\.?344': 'lei_henry_borel',
    r'13\.?260': 'terrorismo',
    r'9\.?296': 'interceptacao_telefonica',
    r'12\.?037': 'identificacao_criminal',
    r'8\.?137': 'crimes_tributarios_ordem_tributaria',
    r'7\.?492': 'crimes_sistema_financeiro_colarinho_branco',
    r'9\.?605': 'crimes_ambientais_meio_ambiente',
    r'7\.?716': 'crimes_de_racismo',
    r'10\.?741': 'estatuto_do_idoso',
    r'1\.?521/51': 'economia_popular',
    r'2\.?889/56': 'genocidio',
    r'11\.?105': 'biosseguranca',
    r'3\.?688/41': 'contravencoes_penais',
    r'8\.?078': 'codigo_de_defesa_do_consumidor_cdc',
    r'7\.?960': 'prisao_temporaria',
}

def clean_html(text: str) -> str:
    if not text:
        return ""
    # Desescapar entidades (&nbsp;, &atilde;, etc.)
    t = html.unescape(text)
    # Substituir quebras e parágrafos por espaço
    t = re.sub(r'</?(p|br|div|tr|li)[^>]*>', ' ', t)
    # Remover tags restantes
    t = RE_TAGS.sub(' ', t)
    # Normalizar espaços
    t = RE_SPACES.sub(' ', t).strip()
    return t

def extract_legal_entities(text: str) -> List[str]:
    entities = []
    text_lower = text.lower()
    for pattern, canonical in LEIS_MAP.items():
        if re.search(pattern, text_lower):
            entities.append(canonical)
    return entities

def prepare_question_text(q: Dict[str, Any]) -> str:
    enunciado = clean_html(q.get('enunciado_html', ''))
    comando = clean_html(q.get('comando', ''))
    
    alts = q.get('alternativas', {})
    alts_text = []
    if isinstance(alts, dict):
        for k, v in alts.items():
            alts_text.append(f"{k}) {clean_html(str(v))}")
    alts_str = " ".join(alts_text)
    
    # Extrair entidades legais
    full_raw = f"{enunciado} {comando} {alts_str}"
    entities = extract_legal_entities(full_raw)
    entities_str = " ".join(entities) if entities else ""
    
    # Combinar tudo de forma limpa e estruturada
    combined = f"{enunciado}\nComando: {comando}\nAlternativas: {alts_str}"
    if entities_str:
        combined = f"{combined}\nEntidades: {entities_str}"
        
    return combined

if __name__ == "__main__":
    import json
    q = json.loads(open('questoes.jsonl', encoding='utf-8').readline())
    print("=== Questao Q0001 processada ===")
    print(prepare_question_text(q))
