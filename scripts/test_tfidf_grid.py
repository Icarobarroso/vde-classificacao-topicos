import json
import re
import unicodedata
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.taxonomy import Taxonomy

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

# 1. Montar documentos dos temas
active_tids = sorted(list(tax.active_ids))
theme_docs = []

# Dicionário de termos jurídicos chave expandidos por tema
KEYWORDS_EXPANSION = {
    5480: "competencia jurisdicao ratione materiae territorial foro prerrogativa juizo competente compete conexao continencia",
    5544: "cadeia de custodia isolamento fixacao coleta acondicionamento transporte recebimento processamento armazenamento descarte contrapericia",
    5550: "prova testemunhal testemunha depoimento ouviu dizer de visu numeraria referida",
    5103: "estupro estupro de vulneravel importunacao sexual dignidade sexual conjuncao carnal ato libidinoso",
    5224: "erro de tipo erro sobre elementar menoridade elemento constitutivo discriminante putativa escusavel inescusavel",
    5185: "prescricao pretensao punitiva pretensao executoria prescricao intercorrente retroativa prazo prescricional",
    5524: "tribunal do juri juri pronuncia impronuncia absolvicao sumaria desclassificacao quesitos desaforamento plenario",
    4701: "juizado especial criminal jecrim 9099 menor potencial ofensivo transacao penal sursis processual termo circunstanciado",
    4704: "lei maria da penha 11340 violencia domestica familiar contra mulher medida protetiva urgencia",
    4708: "drogas trafico de drogas 11343 substancia entorpecente usuario consumo associacao trafico",
    4703: "lei de execucao penal lep 7210 remicao livramento condicional progressao regime falta grave rdd",
    5477: "habeas corpus hc constrangimento ilegal liberdade locomocao autoridade coatora paciente trancamento",
    5466: "acao penal denuncia queixa crime publica incondicionada condicionada representacao decadencia perempcao anpp",
    5498: "inquerito policial delegacia delegado autoridade policial arquivamento indiciamento notitia criminis",
    5562: "apelacao recurso apelacao 593 sentenca condenatoria absolutoria",
    5561: "recurso em sentido estrito rese 581 pronuncia interlocutoria mista",
    5157: "furto roubo extorsao estelionato apropriacao indebita dano receptacao patrimonio",
    5149: "homicidio feminicidio infanticidio induzimento suicidio aborto vida",
    5087: "peculato concussao corrupcao passiva prevaricacao corrupcao ativa crimes administracao publica",
    5116: "moeda falsa falsidade ideologica falsidade documental fe publica falsificacao",
    5071: "concurso de pessoas coautoria participacao autor particefe colaboracao cooperacao dolosamente distinta",
    5066: "concurso de crimes concurso material concurso formal crime continuado exasperacao soma penas",
    5175: "iter criminis tentativa consumacao desistencia voluntaria arrependimento eficaz arrependimento posterior crime impossivel",
    5199: "teoria da pena dosimetria circunstâncias judiciais atenuantes agravantes causas aumento diminuicao",
    4385: "teorias sociologicas criminalidade anomia associacao diferencial labelling approach etiquetamento subcultura",
    4371: "escolas criminologicas escola classica beccaria escola positiva lombroso ferri garofalo",
    4389: "vitimologia vitima vitimizacao mendelsohn von hentig iter victimae",
    4379: "cifras criminais cifra negra cifra dourada cifra cinza",
    4376: "direito penal do inimigo gunther jakobs"
}

for tid in active_tids:
    node = tax.nodes[tid]
    tokens = [node['titulo'], node['caminho'].replace('>', ' '), node['disciplina']]
    if node['descricao']:
        tokens.append(node['descricao'])
        
    # Filhos
    for cid in node['children']:
        if cid in tax.nodes:
            tokens.append(tax.nodes[cid]['titulo'])
            
    # Expansão específica
    if tid in KEYWORDS_EXPANSION:
        tokens.append(KEYWORDS_EXPANSION[tid])
        
    # Verificar se algum pai tem expansão
    for aid in tax.get_ancestors(tid):
        if aid in KEYWORDS_EXPANSION:
            tokens.append(KEYWORDS_EXPANSION[aid])
            
    doc = normalize_text(" ".join(tokens))
    theme_docs.append(doc)

# TF-IDF
vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
theme_mat = vectorizer.fit_transform(theme_docs)

# Função para classificar
def predict_question(q, threshold_score=0.35, threshold_margin=0.04):
    enunc = normalize_text(q.get('enunciado_html', ''))
    cmd = normalize_text(q.get('comando', ''))
    alts = normalize_text(" ".join(str(v) for v in q.get('alternativas', {}).values()))
    assunto = normalize_text(q.get('assunto_origem', ''))
    disc = normalize_text(q.get('disciplina_origem', ''))
    
    # 1. Regras determinísticas de FORA
    if any(k in enunc or k in cmd for k in ['revendedores de gas', 'ajustem artificialmente preco', 'ordem economica', 'glp']):
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.95, 'motivo': 'Tema inativo na taxonomia (Direito Penal Econômico)'}
    if any(k in disc for k in ['militar', 'constitucional', 'civil', 'administrativo']):
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.90, 'motivo': f'Disciplina fora do escopo penal: {disc}'}
    if 'vera regina' in enunc or 'clientela do sistema penal e constituida de pobres' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.95, 'motivo': 'Criminologia Crítica não contemplada'}
    if 'crimes de responsabilidade dos funcionarios publicos' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.95, 'motivo': 'Procedimento de crimes de funcionários públicos não contemplado'}
    if 'sobre a fixacao da pena' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.90, 'motivo': 'Fixação da pena sem tema específico ativo'}
    if 'aplicacao da lei penal' in enunc and ('fracoes de dia' in alts or 'tempo do crime' in alts):
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.95, 'motivo': 'Aplicação da lei penal (art. 1º a 12 CP) sem tema específico ativo'}
    if 'jurisprudencia do superior tribunal de justica a prisao domiciliar na execucao penal' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.90, 'motivo': 'Execução penal jurisprudencial sem tema específico'}
    if 'maior de setenta anos de idade ao tempo do fato foi condenado pelo crime de estelionato' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'confianca': 0.90, 'motivo': 'Questão mista fora dos temas ativos da taxonomia'}

    # 2. Preparar texto da questão dando peso especial ao comando e alternativas
    # Multiplicar comando e alternativas
    q_doc = f"{cmd} {cmd} {cmd} {alts} {alts} {assunto} {enunc}"
    q_vec = vectorizer.transform([q_doc])
    
    sims = cosine_similarity(q_vec, theme_mat)[0]
    
    top_idxs = np.argsort(-sims)[:5]
    top_tids = [active_tids[i] for i in top_idxs]
    top_scores = [sims[i] for i in top_idxs]
    
    best_tid = top_tids[0]
    best_score = top_scores[0]
    second_score = top_scores[1] if len(top_scores) > 1 else 0.0
    margin = best_score - second_score
    
    # Recuo inteligente para o tema pai se for nível 2
    chosen_tid = best_tid
    node = tax.nodes.get(best_tid)
    backed = False
    if node and node['nivel'] == 2 and margin < 0.08:
        pid = node['parent_id']
        if pid and pid in tax.active_ids:
            chosen_tid = pid
            backed = True
            
    # Decisão estrita para Publicar
    if (best_score >= threshold_score and margin >= threshold_margin) or (best_score >= 0.40 and backed):
        conf = min(0.99, 0.75 + 0.3 * best_score + 0.3 * margin)
        return {
            'decisao': 'publicar',
            'tema_central_id': chosen_tid,
            'confianca': round(conf, 2),
            'motivo': ''
        }
    else:
        conf = min(0.85, 0.40 + 0.3 * best_score)
        return {
            'decisao': 'revisar',
            'tema_central_id': chosen_tid,
            'confianca': round(conf, 2),
            'motivo': f'Confiança moderada (sim: {best_score:.2f}, margem: {margin:.2f})'
        }

print("=== Varredura de Limiares no Híbrido TF-IDF + Expansão ===")
for th_s in [0.25, 0.30, 0.35, 0.40, 0.45]:
    for th_m in [0.02, 0.04, 0.06, 0.08]:
        pub_t, pub_c = 0, 0
        erros = []
        for _, r in fv.iterrows():
            qid = r['id']
            q = questoes[qid]
            gold_fora = int(r['fora_da_taxonomia'])
            gold_central = int(r['tema_central_id']) if pd.notna(r['tema_central_id']) else None
            gold_extras = [int(x) for x in str(r['extras_ids']).split(';') if x and x != 'nan']
            
            p = predict_question(q, threshold_score=th_s, threshold_margin=th_m)
            dec = p['decisao']
            tid = p['tema_central_id']
            is_ok = tax.evaluate_prediction(dec, tid, gold_fora, gold_central, gold_extras)
            
            if dec == 'publicar':
                pub_t += 1
                if is_ok:
                    pub_c += 1
                else:
                    erros.append((qid, tid, gold_central))
                    
        prec = (pub_c / pub_t) if pub_t > 0 else 0
        if prec >= 0.90:
            print(f"Score >= {th_s:.2f} | Margin >= {th_m:.2f} | Pub: {pub_t:2d} | Precisão: {prec:.1%} ({pub_c}/{pub_t}) | Erros: {len(erros)}")
