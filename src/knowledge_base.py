"""
Base de Conhecimento Jurídico Especializada para a Taxonomia de 375 Temas Ativos.
Mapeia conceitos, termos técnicos, artigos de lei e súmulas para os nós da árvore.
"""

# Mapeamento de termos conceituais de alta especificidade para tema_ids
CONCEPT_RULES = [
    # CRIMINOLOGIA
    (r'\b(mendelsohn|von hentig|vitimizacao|vitimologia|iter victimae|processo de vitimizacao|vitima ideal|vitima nata)\b', 4389), # Vitimologia
    (r'\b(cifra negra|cifras negras|cifra dourada|cifras douradas|cifra cinza|cifras cinzas|cifra branca|cifras brancas|cifra amarela|cifra rosa)\b', 4379), # Cifras Criminais
    (r'\b(criminalizacao primaria|criminalizacao secundaria)\b', 4378), # Criminalização Primária e Secundária
    (r'\b(teoria da anomia|associacao diferencial|labelling approach|etiquetamento|rotulacao|reacao social|escola de chicago|subcultura delinquente|teorias sociologicas)\b', 4385), # Teorias Sociológicas
    (r'\b(escola classica|escola positiva|lombroso|ferri|garofalo|beccaria|positivismo criminologico)\b', 4371), # Etapas Evolutivas e Escolas
    (r'\b(direito penal do inimigo|gunther jakobs|jakobs)\b', 4376), # Direito Penal do Inimigo
    (r'\b(prevencao primaria|prevencao secundaria|prevencao terciaria|modelos de reacao|modelo restaurativo|modelo dissuasorio|modelo ressocializador)\b', 4368), # Criminologia Estado Dem.
    (r'\b(teorias legitimadoras da pena|retributiva|teoria absoluta|teoria relativa|prevencao geral|prevencao especial)\b', 4384), # Teorias Legitimadoras da Pena
    (r'\b(objeto da criminologia|metodo empirico|interdisciplinar|delito vitima controle social)\b', 4380), # Teoria Geral da Criminologia
    (r'\b(sindrome de estocolmo|sindrome de londres|sindrome da mulher espancada)\b', 4383), # Teorias com Enfoque nas Vítimas

    # LEGISLAÇÃO PENAL ESPECIAL
    (r'\b(11\.?340|maria da penha|violencia domestica|medida protetiva de urgencia)\b', 4704), # Lei Maria da Penha
    (r'\b(11\.?343|drogas|entorpecente|substancia entorpecente|maconha|cocaina|trafico privilegiado|art\.? 33 da lei|art\.? 28 da lei)\b', 4708), # Tráfico de Drogas
    (r'\b(9\.?099|juizado especial criminal|juizados especiais criminais|infracao de menor potencial ofensivo|termo circunstanciado|transacao penal|composicao dos danos civis)\b', 4701), # JECRIM
    (r'\b(7\.?210|execucao penal|livramento condicional|remicao|remir|falta grave|regressao de regime|progressao de regime|rdd|regime disciplinar diferenciado|saida temporaria)\b', 4703), # LEP
    (r'\b(13\.?869|abuso de autoridade|4\.?898)\b', 4684), # Abuso de Autoridade
    (r'\b(8\.?072|crime hediondo|crimes hediondos)\b', 4693), # Crimes Hediondos
    (r'\b(12\.?850|organizacao criminosa|organizacoes criminosas|colaboracao premiada|delacao premiada|infiltracao de policiais|acao controlada)\b', 4705), # Organizações Criminosas
    (r'\b(9\.?613|lavagem de capitais|lavagem de dinheiro|ocultacao de bens|coaf)\b', 4702), # Lavagem de Dinheiro
    (r'\b(9\.?455|tortura|crime de tortura)\b', 4707), # Tortura
    (r'\b(10\.?826|estatuto do desarmamento|arma de fogo|porte ilegal|posse irregular|porte de arma|posse de arma)\b', 4697), # Estatuto do Desarmamento
    (r'\b(9\.?503|ctb|codigo de transito|embriaguez ao volante|direcao de veiculo automotor|homicidio culposo na direcao)\b', 4691), # Crimes de Trânsito
    (r'\b(8\.?078|codigo de defesa do consumidor|cdc|relacao de consumo|afirmacao falsa ou enganosa)\b', 4694), # CDC
    (r'\b(10\.?741|estatuto do idoso|pessoa idosa|proventos de idoso)\b', 4696), # Estatuto do Idoso
    (r'\b(9\.?296|interceptacao telefonica|gravacao clandestina|escuta telefonica)\b', 4700), # Interceptação Telefônica
    (r'\b(12\.?037|identificacao criminal|perfil genetico|banco de dados de perfis)\b', 4699), # Identificação Criminal
    (r'\b(13\.?260|terrorismo|ato terrorista)\b', 4706), # Terrorismo
    (r'\b(9\.?605|meio ambiente|crime ambiental|fauna|flora|poluicao)\b', 4688), # Crimes Ambientais
    (r'\b(7\.?716|racismo|preconceito de raca|cor|etnia|injuria racial)\b', 4690), # Racismo
    (r'\b(8\.?137|tributario|ordem tributaria|sonegacao fiscal)\b', 4695), # Crimes Tributários
    (r'\b(7\.?492|sistema financeiro nacional|colarinho branco|gestao fraudulenta|evasao de divisas)\b', 4689), # Sistema Financeiro
    (r'\b(3\.?688|contravencao penal|contravencoes penais|jogo de bicho|porte de arma branca|pertubacao do sossego)\b', 4686), # Contravenções Penais
    (r'\b(8\.?069|estatuto da crianca|eca|crianca e adolescente|pedofilia|pornografia infantil)\b', 4709), # ECA

    # PROCESSO PENAL - TRIBUNAL DO JÚRI
    (r'\b(tribunal do juri|desaforamento|impronuncia|pronuncia|absolvicao sumaria|desclassificacao|quesitos|soberania dos veredictos|conselho de sentenca|plenario do juri|art\.? 413|art\.? 414|art\.? 415|art\.? 419|art\.? 406 do cpp)\b', 5524), # Procedimento Tribunal do Júri
    
    # PROCESSO PENAL - RECURSOS E AÇÕES AUTÔNOMAS
    (r'\b(habeas corpus|hc|paciente|autoridade coatora|trancamento de acao penal|writ)\b', 5477), # Habeas Corpus
    (r'\b(revisao criminal|acao de revisao criminal|art\.? 621 cpp)\b', 5478), # Revisão Criminal
    (r'\b(recurso de apelacao|apelacao criminal|art\.? 593|interpor apelacao)\b', 5562), # Apelação
    (r'\b(recurso em sentido estrito|rese|art\.? 581)\b', 5561), # RESE
    (r'\b(embargos infringentes|embargos de declaracao|carta testemunhavel|correicao parcial)\b', 5560), # Recursos em Espécies
    
    # PROCESSO PENAL - PRISÕES E MEDIDAS CAUTELARES
    (r'\b(prisao preventiva|art\.? 312|art\.? 311|garantia da ordem publica|fumus comissi|periculum libertatis)\b', 5521), # Prisão Preventiva
    (r'\b(prisao em flagrante|flagrante delito|flagrante proprio|flagrante improprio|flagrante presumido|flagrante preparado|audiencia de custodia)\b', 5520), # Prisão em Flagrante
    (r'\b(prisao temporaria|7\.?960)\b', 5522), # Prisão Temporária
    (r'\b(prisao domiciliar)\b', 5519), # Prisão Domiciliar
    (r'\b(relaxamento da prisao|liberdade provisoria|fianca)\b', 5584), # Teoria Geral das Prisões
    
    # PROCESSO PENAL - INQUÉRITO E AÇÃO
    (r'\b(inquerito policial|notitia criminis|indiciamento|arquivamento do inquerito|delegado de policia|policia judiciaria)\b', 5498), # Inquérito Policial
    (r'\b(acao penal publica incondicionada|acao penal publica condicionada|representacao|queixa crime|acao penal privada|perempcao|decadencia|renuncia|perdao do ofendido)\b', 5466), # Ação Penal
    (r'\b(acordo de nao persecucao penal|anpp|art\.? 28-a cpp)\b', 5466), # Ação Penal (ANPP)
    
    # PROCESSO PENAL - PROVAS E PROCEDIMENTOS
    (r'\b(cadeia de custodia|exame de corpo de delito|prova testemunhal|reconhecimento de pessoas|pericia|busca e apreensao|interceptacao)\b', 5543), # Provas em Espécies
    (r'\b(prova ilicita|frutos da arvore envenenada|teoria dos frutos|prova ilegal|prova emprestada)\b', 5590), # Teoria Geral das Provas
    (r'\b(incompetencia|suspeicao|impedimento|excecao de suspeicao|excecao de incompetencia)\b', 5490), # Questões e Processos Incidentes
    (r'\b(competencia territorial|foro por prerrogativa de funcao|conexao|continencia|competencia penal)\b', 5480), # Competência
    (r'\b(nulidade absoluta|nulidade relativa|prejuizo|pas de nullite sans grief)\b', 5509), # Nulidades
    (r'\b(juiz das garantias|sistema acusatorio|sistema inquisitivo)\b', 5580), # Sistemas e Princípios
    (r'\b(sentenca penal|emendatio libelli|mutatio libelli)\b', 5572), # Sentença Penal
    (r'\b(citacao por edital|citacao por hora certa|citacao pessoal|comunicacao dos atos processuais)\b', 5487), # Comunicação dos Atos

    # PENAL - PARTE GERAL
    (r'\b(tempo do crime|lugar do crime|territorialidade|extraterritorialidade|retroatividade da lei penal|lei penal no tempo)\b', 5180), # Lei Penal no Tempo e Espaço
    (r'\b(erro de tipo|discriminante putativa|erro acidental|erro sobre a pessoa|aberratio ictus|aberratio delicti)\b', 5227), # Erro de Tipo
    (r'\b(legitima defesa|estado de necessidade|estrito cumprimento do dever legal|exercicio regular de direito|excludente de ilicitude)\b', 5228), # Teoria do Crime: Ilicitude
    (r'\b(inimputabilidade|imputabilidade|doenca mental|menoridade|embriaguez involuntaria|emocao e paixao)\b', 5214), # Inimputabilidade
    (r'\b(potencial consciencia da ilicitude|erro de proibicao|inexigibilidade de conduta diversa|coacao moral irresistivel|obediencia hierarquica)\b', 5211), # Teoria do Crime: Culpabilidade
    (r'\b(coautoria|participacao|autoria mediata|concurso de pessoas|cooperacao dolosamente distinta)\b', 5071), # Concurso de Pessoas
    (r'\b(concurso material|concurso formal|crime continuado|concurso de crimes)\b', 5066), # Concurso de Crimes
    (r'\b(iter criminis|tentativa|crime consumado|desistencia voluntaria|arrependimento eficaz|arrependimento posterior|crime impossivel)\b', 5175), # Iter Criminis
    (r'\b(dosimetria da pena|circunstancias judiciais|atenuante|agravante|reincidencia|causa de aumento|causa de diminuicao|regime fechado|regime semiaberto|regime aberto|penas restritivas de direitos|multa)\b', 5199), # Teoria da Pena
    (r'\b(medida de seguranca|internacao|tratamento ambulatorial|inimputavel)\b', 5184), # Medida de Segurança
    (r'\b(prescricao da pretensao punitiva|prescricao da pretensao executoria|prescricao retroativa|prescricao intercorrente|causas interruptivas da prescricao|prescricao penal)\b', 5185), # Prescrição
    (r'\b(anistia|graca|indulto|abolitio criminis|extincao da punibilidade)\b', 5191), # Punibilidade

    # PENAL - CRIMES EM ESPÉCIE
    (r'\b(homicidio|homicidio qualificado|feminicidio|infanticidio|induzimento ao suicidio|aborto)\b', 5149), # Crimes Contra a Vida
    (r'\b(lesao corporal|lesao corporal grave|lesao corporal seguidade morte)\b', 5077), # Lesões Corporais
    (r'\b(furto|furto qualificado|roubo|roubo majorado|latrocinio|extorsao|estelionato|apropriacao indebita|dano|receptacao)\b', 5157), # Crimes Contra o Patrimônio
    (r'\b(estupro|estupro de vulneravel|importunacao sexual|assedio sexual)\b', 5102), # Crimes Contra a Dignidade Sexual
    (r'\b(calunia|difamacao|injuria|crimes contra a honra)\b', 5120), # Crimes Contra a Honra
    (r'\b(peculato|concussao|corrupcao passiva|prevaricacao|corrupcao ativa|desacato|desobediencia|crimes contra a administracao publica)\b', 5087), # Crimes Contra Adm Pública
    (r'\b(moeda falsa|falsidade ideologica|falsidade documental|falso testemunho|crimes contra a fe publica)\b', 5116), # Crimes Contra a Fé Pública
]
