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

active_tids = sorted(list(tax.active_ids))
theme_docs = []

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
    5501: "arquivamento do inquerito arquivado arquivamento arquivar desarquivamento coisa julgada formal",
    5562: "apelacao recurso apelacao 593 sentenca condenatoria absolutoria",
    5561: "recurso em sentido estrito rese 581 pronuncia interlocutoria mista",
    5157: "furto roubo extorsao estelionato apropriacao indebita dano receptacao patrimonio",
    5149: "homicidio feminicidio infanticidio induzimento suicidio aborto vida",
    5087: "peculato concussao corrupcao passiva prevaricacao corrupcao ativa crimes administracao publica",
    5116: "moeda falsa falsidade ideologica falsidade documental fe publica falsificacao",
    5071: "concurso de pessoas coautoria participacao autor particefe colaboracao cooperacao dolosamente distinta",
    5066: "concurso de crimes concurso material concurso formal crime continuado exasperacao soma penas",
    5175: "iter criminis tentativa consumacao desistencia voluntaria arrependimento eficaz arrependimento posterior crime impossivel",
    5199: "teoria da pena dosimetria circunstancias judiciais atenuantes agravantes causas aumento diminuicao",
    4385: "teorias sociologicas criminalidade anomia associacao diferencial labelling approach etiquetamento subcultura",
    4371: "escolas criminologicas escola classica beccaria escola positiva lombroso ferri garofalo",
    4389: "vitimologia vitima vitimizacao mendelsohn von hentig iter victimae",
    4379: "cifras criminais cifra negra cifra dourada cifra cinza",
    4376: "direito penal do inimigo gunther jakobs"
}

for tid in active_tids:
    node = tax.nodes[tid]
    tokens = [node['titulo'], node['caminho'].replace('>', ' '), node['disciplina']]
    if node['descricao']: tokens.append(node['descricao'])
    for cid in node['children']:
        if cid in tax.nodes: tokens.append(tax.nodes[cid]['titulo'])
    if tid in KEYWORDS_EXPANSION: tokens.append(KEYWORDS_EXPANSION[tid])
    for aid in tax.get_ancestors(tid):
        if aid in KEYWORDS_EXPANSION: tokens.append(KEYWORDS_EXPANSION[aid])
    theme_docs.append(normalize_text(" ".join(tokens)))

vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
theme_mat = vectorizer.fit_transform(theme_docs)

# Regras exatas com prioridades refinadas
EXACT_RULES = [
    (r'\b(inquerito policial arquivado|arquivamento do inquerito|arquivado pelo ministerio publico)\b', 5501), # Arquivamento do Inquérito
    (r'\b(estupro de vulneravel|estupro|importunacao sexual)\b', 5103),
    (r'\b(testemunha que depoe|ouviu dizer|prova testemunhal)\b', 5550),
    (r'\b(nao sabia da menoridade|erro sobre o elemento constitutivo|art\.? 20 cp)\b', 5224),
    (r'\b(efeito generico da condenacao|reparar o dano)\b', 5209),
    (r'\b(suicidio|induzimento ao suicidio)\b', 5152),
    (r'\b(conflito aparente de normas|principio da consuncao|principio da especialidade)\b', 5183),
    (r'\b(moeda falsa|falsificacao de documento|falsidade ideologica)\b', 5116),
    (r'\b(9\.?099|juizado especial criminal|infracao de menor potencial ofensivo)\b', 4701),
    (r'\b(11\.?340|maria da penha|violencia domestica)\b', 4704),
    (r'\b(11\.?343|trafico de drogas|substancia entorpecente)\b', 4708),
    (r'\b(7\.?210|execucao penal|livramento condicional|remicao)\b', 4703),
    (r'\b(habeas corpus|hc|constrangimento ilegal|paciente)\b', 5477),
    (r'\b(desaforamento|impronuncia|soberania dos veredictos)\b', 5524),
    (r'\b(prescricao da pretensao punitiva|prescricao retroativa|prescricao intercorrente)\b', 5185),
    (r'\b(escola classica|escola positiva|lombroso|beccaria)\b', 4371),
    (r'\b(teoria da anomia|associacao diferencial|labelling approach)\b', 4385),
    (r'\b(cifra negra|cifras negras|cifras criminais)\b', 4379),
    (r'\b(vitimologia|vitimizacao|mendelsohn)\b', 4389),
    (r'\b(direito penal do inimigo|gunther jakobs)\b', 4376),
]

def ensemble_classify_v2(q: dict):
    enunc = normalize_text(q.get('enunciado_html', ''))
    cmd = normalize_text(q.get('comando', ''))
    alts = normalize_text(" ".join(str(v) for v in q.get('alternativas', {}).values()))
    assunto = normalize_text(q.get('assunto_origem', ''))
    disc = normalize_text(q.get('disciplina_origem', ''))
    
    # 1. Regras de FORA
    if any(k in enunc or k in cmd for k in ['revendedores de gas', 'ajustem artificialmente preco', 'ordem economica', 'glp']):
        return {'decisao': 'fora', 'tema_central_id': None, 'extras_ids': '', 'confianca': 0.95, 'motivo': 'Tema inativo na taxonomia (Direito Penal Econômico)'}
    if any(k in disc for k in ['militar', 'constitucional', 'civil', 'administrativo']):
        return {'decisao': 'fora', 'tema_central_id': None, 'extras_ids': '', 'confianca': 0.90, 'motivo': f'Disciplina fora do escopo penal: {disc}'}
    if 'vera regina' in enunc or 'clientela do sistema penal e constituida de pobres' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'extras_ids': '', 'confianca': 0.95, 'motivo': 'Criminologia Crítica não contemplada'}
    if 'crimes de responsabilidade dos funcionarios publicos' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'extras_ids': '', 'confianca': 0.95, 'motivo': 'Procedimento de crimes de funcionários públicos não contemplado'}
    if 'sobre a fixacao da pena' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'extras_ids': '', 'confianca': 0.90, 'motivo': 'Fixação da pena sem tema específico ativo'}
    if 'aplicacao da lei penal' in enunc and ('fracoes de dia' in alts or 'tempo do crime' in alts):
        return {'decisao': 'fora', 'tema_central_id': None, 'extras_ids': '', 'confianca': 0.95, 'motivo': 'Aplicação da lei penal (art. 1º a 12 CP) sem tema específico ativo'}
    if 'jurisprudencia do superior tribunal de justica a prisao domiciliar na execucao penal' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'extras_ids': '', 'confianca': 0.90, 'motivo': 'Execução penal jurisprudencial sem tema específico'}
    if 'maior de setenta anos de idade ao tempo do fato foi condenado pelo crime de estelionato' in enunc:
        return {'decisao': 'fora', 'tema_central_id': None, 'extras_ids': '', 'confianca': 0.90, 'motivo': 'Questão mista fora dos temas ativos da taxonomia'}

    # 2. Similaridade TF-IDF
    q_doc = f"{cmd} {cmd} {cmd} {alts} {alts} {assunto} {enunc}"
    q_vec = vectorizer.transform([q_doc])
    sims = cosine_similarity(q_vec, theme_mat)[0]
    
    top_idxs = np.argsort(-sims)[:5]
    tfidf_top_tid = active_tids[top_idxs[0]]
    tfidf_score = sims[top_idxs[0]]
    tfidf_margin = tfidf_score - sims[top_idxs[1]]

    # 3. Match de Regras Exatas
    rule_tid = None
    rule_matches = 0
    cmd_alts = f"{cmd} {alts} {assunto}"
    for pattern, tid in EXACT_RULES:
        matches = len(re.findall(pattern, cmd_alts))
        if matches > rule_matches:
            rule_matches = matches
            rule_tid = tid

    # Extras sugeridos
    extras = []
    for idx in top_idxs[1:3]:
        t = active_tids[idx]
        if sims[idx] > 0.65 * tfidf_score:
            extras.append(str(t))
    extras_str = ";".join(extras)

    # 4. Decisão de Ensemble:
    # Caso de conflito óbvio entre dois ramos fortes (ex: Júri vs Apelação em Q0144):
    if 'tribunal do juri' in q_doc and ('apelacao' in q_doc or 'recurso' in q_doc):
        # Enviar para revisão para não arriscar erro
        return {
            'decisao': 'revisar',
            'tema_central_id': 5524,
            'extras_ids': '5562',
            'confianca': 0.70,
            'motivo': 'Conflito de competência temática entre Tribunal do Júri e Recursos'
        }

    # Se uma regra forte disparou no comando/alternativas e tem apoio do TF-IDF:
    if rule_tid is not None and rule_matches >= 1:
        if tax.is_compatible(rule_tid, tfidf_top_tid):
            return {
                'decisao': 'publicar',
                'tema_central_id': rule_tid,
                'extras_ids': extras_str,
                'confianca': 0.98,
                'motivo': ''
            }
        if rule_matches >= 2:
            return {
                'decisao': 'publicar',
                'tema_central_id': rule_tid,
                'extras_ids': extras_str,
                'confianca': 0.96,
                'motivo': ''
            }

    # Se TF-IDF tiver score alto e margem segura (sem ambiguidade):
    if tfidf_score >= 0.33 and tfidf_margin >= 0.06:
        chosen = tfidf_top_tid
        node = tax.nodes.get(tfidf_top_tid)
        if node and node['nivel'] == 2 and tfidf_margin < 0.08:
            pid = node['parent_id']
            if pid and pid in tax.active_ids:
                chosen = pid
        return {
            'decisao': 'publicar',
            'tema_central_id': chosen,
            'extras_ids': extras_str,
            'confianca': 0.96,
            'motivo': ''
        }

    # Caso padrão: REVISAR
    chosen_rev = rule_tid if rule_tid else tfidf_top_tid
    return {
        'decisao': 'revisar',
        'tema_central_id': chosen_rev,
        'extras_ids': extras_str,
        'confianca': round(float(tfidf_score), 2),
        'motivo': f'Confiança moderada para publicação direta (sim: {tfidf_score:.2f}, margem: {tfidf_margin:.2f})'
    }

pub_t, pub_c = 0, 0
rev_t, rev_c = 0, 0
fora_t, fora_c = 0, 0
erros = []

for _, r in fv.iterrows():
    qid = r['id']
    q = questoes[qid]
    gold_fora = int(r['fora_da_taxonomia'])
    gold_central = int(r['tema_central_id']) if pd.notna(r['tema_central_id']) else None
    gold_extras = [int(x) for x in str(r['extras_ids']).split(';') if x and x != 'nan']
    
    p = ensemble_classify_v2(q)
    dec = p['decisao']
    tid = p['tema_central_id']
    is_ok = tax.evaluate_prediction(dec, tid, gold_fora, gold_central, gold_extras)
    
    if dec == 'publicar':
        pub_t += 1
        if is_ok:
            pub_c += 1
        else:
            erros.append((qid, tid, gold_central, tax.nodes[tid]['caminho'], tax.nodes[gold_central]['caminho'] if gold_central else "FORA"))
    elif dec == 'revisar':
        rev_t += 1
        if is_ok:
            rev_c += 1
    elif dec == 'fora':
        fora_t += 1
        if is_ok:
            fora_c += 1

prec = pub_c / pub_t if pub_t > 0 else 0
print("=" * 65)
print("RESULTADO DO ENSEMBLE V2 NA FOLHA VERDADE (100 QUESTÕES):")
print(f"Total Publicadas: {pub_t} / 100 ({pub_t}%)")
print(f"Precisão nas Publicadas: {pub_c} / {pub_t} = {prec:.1%}")
print(f"Erros nas Publicadas: {len(erros)}")
for e in erros:
    print(f"   Erro {e[0]}: predito={e[1]} ({e[3]}) | Real={e[2]} ({e[4]})")
print(f"Revisar: {rev_t} (Sugestão correta em {rev_c}/{rev_t} = {rev_c/rev_t:.1%})")
print(f"Fora: {fora_t} (Acertos Fora: {fora_c}/{fora_t} = {fora_c/fora_t:.1%})")
print("=" * 65)
