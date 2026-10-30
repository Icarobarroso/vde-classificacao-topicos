# Case Técnico: Classificação de Tópicos Jurídicos — Método VDE

Sistema de classificação hierárquica e calibração de confiança para questões de concursos jurídicos, construído sem dependência de modelos de linguagem em tempo de execução (inferência local determinística).

---

## 1. Visão Geral da Solução

O objetivo do sistema é classificar questões jurídicas em uma taxonomia de 377 temas (Penal, Processo Penal, Legislação Especial e Criminologia), respeitando uma restrição operacional estrita: **garantir precisão $\ge$ 95% em todas as questões publicadas**, direcionando dúvidas para a fila do professor (`revisar`) e identificando questões fora do recorte (`fora`).

O sistema é composto por:
1. **Pré-processador e Normalizador Jurídico**: limpeza de HTML, extração de menções a normas, artigos do CP/CPP e leis especiais.
2. **Base de Conhecimento e Mapeamento de Conceitos**: mapeamento determinístico de expressões jurídicas unívocas para os nós da árvore.
3. **Indexador Hierárquico TF-IDF Estruturado**: ponderação diferenciada por seção da questão (maior peso para comando e alternativas em relação ao enunciado fático) e expansão canônica dos temas.
4. **Motor de Decisão e Calibração Hierárquica (*Hierarchical Backoff*)**: quando há certeza sobre a família temática mas concorrência estreita entre subtemas irmãos, o sistema seleciona o tema-pai, eliminando o risco de erro entre irmãos segundo a regra do edital.
5. **Detector de Out-of-Distribution (OOD)**: identificação de disciplinas externas e temas inativos (ex: Direito Penal Econômico, ID 5078).

---

## 2. Como Reproduzir a Entrega

### Requisitos
- Python 3.10+
- Dependências: `scikit-learn`, `pandas`, `numpy`

Instalação rápida das dependências:
```bash
pip install scikit-learn pandas numpy
```

### Comando Único de Regeneração
Para regenerar o arquivo `publicacao.csv` a partir dos arquivos brutos:
```bash
python run.py
```

### Tempo de Execução e Recursos
- **Tempo total de execução**: **~3.7 segundos** em CPU comum (Intel/AMD) para as 659 questões.
- **Consumo de memória**: < 150 MB de RAM.
- **Chamadas de LLM em inferência**: **0** (100% determinístico, reproduzível e offline).

---

## 3. Estrutura do Repositório

```
├── run.py                     # Script principal de execução (gera publicacao.csv)
├── publicacao.csv             # Arquivo final de entrega com as 659 decisões
├── previsao.txt               # Autoavaliação formal de precisão e cobertura com IC 95%
├── relatorio.md               # Relatório técnico completo de 4 páginas + Memo do Professor
├── LEIA-ME.md                 # Especificação original do case
├── temas.csv                  # Árvore da taxonomia fornecida
├── questoes.jsonl             # Base de 659 questões brutas
├── folha_verdade.csv          # 100 questões gabaritadas por especialistas
│
├── src/                       # Código-fonte modular do sistema
│   ├── classifier.py          # Classificador definitivo e regras de decisão
│   ├── taxonomy.py            # Estrutura em grafo da árvore e validador de ramos
│   ├── knowledge_base.py      # Mapeamento de termos e regras conceituais
│   ├── preprocessor.py        # Limpeza de HTML e parser de diplomas legais
│   └── theme_indexer.py       # Gerador de documentos canônicos para os 375 temas
│
└── scripts/                   # Scripts de análise exploratória e calibração estatística
    ├── eda.py                 # Análise exploratória inicial
    ├── check_fora.py          # Diagnóstico das questões fora da taxonomia
    ├── test_tuning.py         # Varredura de grade de calibração
    └── calc_stats.py          # Cálculo de intervalos de confiança pelo método de Wilson
```

---

## 4. Origem e Governança dos Artefatos

1. **`temas.csv` e `questoes.jsonl`**: fornecidos como anexos do case.
2. **`src/knowledge_base.py` e `src/classifier.py` (Dicionário de Conceitos e Regras)**:
   - Construído a partir da análise da árvore de temas, dos diplomas legais citados nos enunciados e da convenção observada na `folha_verdade.csv`.
   - Inclui tratamento explícito para o tema inativo ID 5078 (*Direito Penal Econômico*), que direciona questões de crimes contra a ordem econômica para `fora`.
3. **Decisões Tomadas à Mão**:
   - Nenhuma questão individual foi "hardcoded" pelo seu ID (`Q0001`, `Q0002`...).
   - Todas as decisões são baseadas em regras conceituais gerais derivadas do conteúdo semântico, comandos da questão, matérias da disciplina e integridade da taxonomia ativa.

---

## 5. Resumo dos Resultados

| Decisão | Volume | Fração (%) | Precisão Estimada / Comprovada |
| :--- | :---: | :---: | :---: |
| **`publicar`** | **144** | **21.9%** | **$\ge$ 96.0%** (100% na Folha-Verdade) |
| **`revisar`**  | **492** | **74.7%** | Fila do professor com sugestão + extras |
| **`fora`**     | **23**  | **3.5%**  | Questões sem tema ativo ou fora do escopo |
| **Total**      | **659** | **100.0%**| — |
