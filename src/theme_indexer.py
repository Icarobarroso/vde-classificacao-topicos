import re
import pandas as pd
from typing import Dict, List, Tuple
from src.taxonomy import Taxonomy
from src.preprocessor import LEIS_MAP, extract_legal_entities

# Termos de expansão para temas comuns da árvore
TEMA_EXPANSION = {
    'lei maria da penha': 'lei_maria_da_penha 11340 violencia domestica e familiar contra a mulher medidas protetivas de urgencia lesao corporal ameaca',
    'trafico de drogas': 'lei_de_drogas_trafico 11343 substancia entorpecente drogas porte para consumo associacao para o trafico drogas privilegiado usuario',
    'juizado especial criminal': 'juizado_especial_criminal_jecrim 9099 infracao de menor potencial ofensivo transacao penal composicao civil dos danos termo circunstanciado sursis processual suspensao condicional do processo',
    'lei de execucao penal': 'lei_de_execucao_penal_lep 7210 remicao livramento condicional progressao de regime falta grave regressao rdd saida temporaria livramento',
    'abuso de autoridade': 'abuso_de_autoridade 13869 autoridade agente publico abuso de poder',
    'crimes hediondos': 'crimes_hediondos 8072 hediondo inafiancavel insuscetivel de graca anistia',
    'organizacoes criminosas': 'organizacoes_criminosas 12850 orcrim colaboracao premiada infiltracao de agentes acao controlada',
    'lavagem de dinheiro': 'lavagem_de_dinheiro_capitais 9613 lavagem ocultacao dissimulacao de bens direitos ou valores coaf',
    'tortura': 'crime_de_tortura 9455 tortura prova sofrimento fisico ou mental',
    'estatuto do desarmamento': 'estatuto_do_desarmamento_armas 10826 arma de fogo porte ilegal posse irregular disparo municao acessorio',
    'crimes de transito': 'codigo_de_transito_brasileiro_ctb 9503 ctb embriaguez ao volante direcao perigosa habilitacao homicidio culposo no transito',
    'crimes previstos no cdc': 'codigo_de_defesa_do_consumidor_cdc 8078 consumidor relacao de consumo publicidade enganosa induzir a erro',
    'estatuto de idoso': 'estatuto_do_idoso 10741 idoso pessoa idosa discriminacao apropriacao de proventos',
    'tribunal do juri': 'juri pronuncia impronuncia absolvição sumaria desclassificacao quesitos desaforamento soberania dos veredictos plenário do juri conselho de sentenca',
    'habeas corpus': 'habeas corpus writ paciente coator autoridade coatora constrangimento ilegal liberdade de locomocao trancamento de acao penal trancamento de inquerito',
    'inquerito policial': 'inquerito policial delegacia delegado autoridade policial arquivamento notitia criminis indiciamento sigiloso inquisitivo',
    'acao penal': 'acao penal publica incondicionada condicionada privada queixa-crime denuncia representacao decadencia perempcao perdao',
    'recursos em especies': 'recurso apelacao recurso em sentido estrito rese embargos infringentes embargos de declaracao carta testemunhavel agravos',
    'apelacao': 'apelacao recurso de apelacao 593 sentenca condenatoria absolutoria',
    'recurso em sentido estrito': 'recurso em sentido estrito rese 581 decisao interlocutoria pronuncia',
    'revisao criminal': 'revisao criminal 621 erro judiciario rescisoria penal nova prova absolvicao',
    'prisao preventiva': 'prisao preventiva cautelar garantia da ordem publica conveniencia da instrucao aplicacao da lei penal periculum libertatis fumus comissi delicti 311 312 cpp',
    'prisao em flagrante': 'prisao em flagrante flagrante delito flagrante proprio improprio presumido preparado forjado esperado audiência de custodia relaxamento',
    'competencia': 'competencia jurisdicao ratione materiae ratione loci conexao continencia foro por prerrogativa de funcao desmembramento',
    'nulidades': 'nulidade prejuizo pas de nullite sans grief nulidade absoluta relativa arguição de nulidade cerceamento de defesa',
    'provas em especies': 'prova testemunhal pericia exame de corpo de delito busca e apreensao interrogatorio acareacao reconhecimento confissao documento',
    'dosimetria': 'dosimetria fixacao da pena trifasico circunstâncias judiciais atenuantes agravantes causas de aumento causas de diminuicao culpabilidade antecedentes',
    'prescricao': 'prescricao pretensao punitiva executoria retroativa intercorrente propriamente dita prescricao da pena em abstrato prescricao da pena em concreto termo inicial causa interruptiva suspensiva extinção da punibilidade 109 110 cp',
    'concurso de crimes': 'concurso de crimes concurso material concurso formal crime continuado soma de penas exasperacao',
    'concurso de pessoas': 'concurso de pessoas coautoria participacao autor mediata colateral participacao de menor importancia cooperacao dolosamente distinta',
    'erro de tipo': 'erro de tipo erro sobre elemento constitutivo do tipo essencial acidental vencivel invencivel escusavel inescusavel putativo discriminante putativa',
    'excludentes de ilicitude': 'excludente de ilicitude legitima defesa estado de necessidade estrito cumprimento do dever legal exercicio regular de direito excesso punivel',
    'vitimologia': 'vitimologia vitima vitimizacao primaria secundaria terciaria iter victimae categorizacao de vitimas mendelsohn von hentig',
    'cifras criminais': 'cifras negras cifras douradas cifras cinzas cifras brancas cifras amarelas cifras verdes estatisticas criminais subnotificacao',
    'direito penal do inimigo': 'direito penal do inimigo gunther jakobs punicao do autor estado de perigo antecipacao da tutela penal cidadao vs inimigo',
    'escolas crimonologicas': 'escola classica beccaria carrara escola positiva lombroso ferri garofalo determinismo livre arbitrio metodo empirico indutivo',
    'teorias sociologicas': 'escola de chicago anomia associacao diferencial labelling approach etiquetamento reacao social criminologia critica subcultura delinquente'
}

class ThemeIndexer:
    def __init__(self, taxonomy: Taxonomy):
        self.tax = taxonomy
        self.theme_texts = {} # tid -> texto composto
        self.active_tids = sorted(list(self.tax.active_ids))
        self._build_theme_documents()

    def _build_theme_documents(self):
        for tid in self.active_tids:
            node = self.tax.nodes[tid]
            parts = []
            
            # Título e caminho
            parts.append(node['titulo'])
            parts.append(node['caminho'].replace('>', ' '))
            parts.append(node['disciplina'])
            
            # Descrição do nó
            if node['descricao']:
                parts.append(node['descricao'])
                
            # Textos dos filhos
            child_titles = [self.tax.nodes[cid]['titulo'] for cid in node['children'] if cid in self.tax.nodes]
            if child_titles:
                parts.append(" ".join(child_titles))
                
            # Textos dos pais
            ancestor_titles = [self.tax.nodes[aid]['titulo'] for aid in self.tax.get_ancestors(tid) if aid in self.tax.nodes]
            if ancestor_titles:
                parts.append(" ".join(ancestor_titles))
                
            # Entidades legais e expansões específicas
            text_so_far = " ".join(parts).lower()
            for key, exp in TEMA_EXPANSION.items():
                if key in text_so_far:
                    parts.append(exp)
                    
            entities = extract_legal_entities(" ".join(parts))
            if entities:
                parts.append(" ".join(entities))
                
            self.theme_texts[tid] = " ".join(parts)

    def get_document(self, tid: int) -> str:
        return self.theme_texts.get(tid, "")

if __name__ == "__main__":
    tax = Taxonomy()
    indexer = ThemeIndexer(tax)
    print(f"Indexados {len(indexer.theme_texts)} temas ativos.")
    print("Exemplo tema 4708 (Tráfico de Drogas):")
    print(indexer.get_document(4708)[:250])
