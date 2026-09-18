# G0 — Evidência do Baseline de Fontes

## Controle da captura

| Campo | Valor |
| --- | --- |
| Gate | `G0 — Baseline imutável` |
| Estado | `CONCLUÍDO` |
| Branch | `inc-002-minimal-catalog` |
| Commit-base | `3f7d38b3d06cb9db5c10be33e36750360e39bff6` |
| Capturado em | `2026-09-15T23:21:54-03:00` |
| Responsável pela captura | Codex |
| Autoridade de aprovação | Davi |
| Raiz inventariada | `.local/drafts/arquitetura/` |

## Convenção metodológica

`G0-METHOD-001`: o baseline distingue o **corpus de fontes** dos **artefatos de controle da migração**.

- Os 34 arquivos presentes na observação inicial, somados aos dois arquivos surgidos em `contexto/` durante a execução, formam o corpus final de 36 fontes do G0.
- Os oito arquivos de plano e auditoria produzidos para conduzir a migração são contabilizados, mas não são fontes do sistema.
- Os quatro arquivos gerados por este gate em `baseline/` são evidências do G0 e ficam fora do próprio conjunto de entrada para evitar autorreferência.
- Esta convenção não promove conteúdo, não altera autoridade e não resolve decisões de produto, esporte ou arquitetura.

Não há decisão de autoridade bloqueando o G0. A inclusão futura dos oito artefatos de controle no registro canônico `docs/governance/SOURCES.yaml` deve ser decidida no G1. A recomendação é mantê-los como evidência operacional, fora do catálogo canônico de fontes do produto.

## Decisão identificada para registro posterior

| ID provisório | Estado | Decisão necessária | Recomendação | Autoridade | Gate |
| --- | --- | --- | --- | --- | --- |
| `GOV-PENDING-SOURCE-REVISION-001` | `PENDENTE` | Definir como tratar regenerações e novos arquivos do pacote `contexto/` sem destruir a linhagem do baseline. | Cada regeneração deve criar uma nova revisão com novo hash; protótipos e saídas geradas permanecem fora da SSOT do produto e não sobrescrevem silenciosamente a revisão inventariada. | Davi, com recomendação técnica | G1 |
| `GOV-PENDING-SOURCE-SCOPE-002` | `PENDENTE` | Definir se os oito artefatos de controle da migração pertencem ao futuro catálogo canônico de fontes. | Mantê-los como evidência operacional da migração, fora do catálogo de fontes do produto. | Davi, com recomendação técnica | G1 |

Essa decisão foi identificada porque seis arquivos mudaram e dois surgiram durante o G0. Ela deve ser registrada no mecanismo canônico de decisões somente após a criação e aprovação da governança do G1. Nenhuma decisão canônica foi antecipada neste gate.

## Resultado do inventário

| Conjunto | Quantidade | Tratamento |
| --- | ---: | --- |
| Corpus de fontes | 36 | Inventário formal, classificação e SHA-256 |
| Artefatos de controle | 8 | Contabilizados e selados separadamente |
| Evidências produzidas pelo G0 | 4 | Excluídas da entrada do próprio baseline |
| Total observado no fechamento do G0 | 44 | 100% classificado |

O inventário legível por máquina está em [`G0-SOURCES.yaml`](./G0-SOURCES.yaml). Os hashes reproduzíveis do corpus estão em [`G0-SHA256SUMS.txt`](./G0-SHA256SUMS.txt). Os hashes dos artefatos de controle estão em [`G0-CONTROL-SHA256SUMS.txt`](./G0-CONTROL-SHA256SUMS.txt).

## Classificação das fontes

| Classe | Quantidade | Significado no G0 |
| --- | ---: | --- |
| `NOTEBOOKLM_PROPOSAL` | 10 | Proposta derivada do NotebookLM, sem autoridade |
| `TOOL_CONFIG_PROPOSAL` | 4 | Configuração proposta, não instalada |
| `PROTOTYPE_AUTOMATION` | 6 | Código experimental preservado, não operacionalizado |
| `DECISION_HISTORY_SOURCE` | 2 | Histórico usado somente como proveniência |
| `GENERATED_DEMO` | 3 | Saída demonstrativa, não evidência do runtime atual |
| `IMPLEMENTATION_HISTORY_SOURCE` | 1 | Relato histórico de implementação |
| `EXTERNAL_NORMATIVE_SOURCE` | 1 | Regra externa a mapear, sem promoção automática |
| `MIGRATION_SOURCE` | 1 | Fonte principal candidata à migração |
| `SUPERSEDED_SOURCE` | 1 | Versão anterior preservada para comparação |
| `DRAFT_CANDIDATE` | 1 | Rascunho com afirmações candidatas |
| `SUPERSEDED_DRAFT` | 1 | Plano monolítico substituído, mantido como histórico |
| `DOMAIN_SOURCE_CANDIDATE` | 2 | Conteúdo esportivo sujeito à autoridade de Davi |
| `HISTORICAL_WORK_LOG` | 1 | Registro de execução, não especificação |
| `DERIVED_ANALYSIS` | 2 | Análise de agente, sem autoridade própria |

## Inventário humano

| ID | Arquivo | Classe | Escopo | Destino candidato | Bytes | SHA-256 (12) |
| --- | --- | --- | --- | --- | ---: | --- |
| `SRC-NLM-AGENTS-V2` | `contexto/AGENTS-v2.md` | `NOTEBOOKLM_PROPOSAL` | roteamento de agentes | seleção para `AGENTS.md` | 3.801 | `dd8f7f235160` |
| `SRC-NLM-MAKEFILE` | `contexto/Makefile` | `TOOL_CONFIG_PROPOSAL` | automação documental | nenhum antes de validação | 634 | `15570fbdd846` |
| `SRC-NLM-QUICKSTART` | `contexto/QUICKSTART.md` | `NOTEBOOKLM_PROPOSAL` | instalação de ferramentas | nenhum; proposta diferida | 2.559 | `811b30a53c5d` |
| `SRC-NLM-REVIEW` | `contexto/REVIEW.md` | `NOTEBOOKLM_PROPOSAL` | política de revisão | seleção para governança | 2.310 | `cb63dc80132d` |
| `SRC-NLM-NAMES` | `contexto/Regras-Nomes.md` | `NOTEBOOKLM_PROPOSAL` | convenções de nomes | `DOCUMENTATION_STANDARD.md` | 4.327 | `87f0045682a0` |
| `SRC-NLM-CODE-REVIEW-SKILL` | `contexto/SKILL.md` | `NOTEBOOKLM_PROPOSAL` | procedimento de revisão | nenhum; avaliar após piloto | 3.527 | `ec19182b0ca5` |
| `SRC-NLM-ARCH-RULES` | `contexto/architecture-rules.md` | `NOTEBOOKLM_PROPOSAL` | regras arquiteturais | ADR/governança, por seleção | 2.309 | `b9c2269f0b4f` |
| `SRC-NLM-ATLAN-SKILL` | `contexto/atlan-data-context-SKILL.md` | `NOTEBOOKLM_PROPOSAL` | integração Atlan/MCP | nenhum no baseline | 4.870 | `6a8899b24f25` |
| `SRC-NLM-CLAUDEIGNORE` | `contexto/claudeignore` | `TOOL_CONFIG_PROPOSAL` | exclusões de contexto | `.claudeignore`, se aprovado | 456 | `c35a290daa2e` |
| `SRC-NLM-FEATURE-SKILL` | `contexto/feature-workflow-SKILL.md` | `NOTEBOOKLM_PROPOSAL` | fluxo de feature | nenhum; avaliar após piloto | 3.686 | `c6ce6c77425e` |
| `SRC-NLM-GIT-LORE` | `contexto/git-lore-commit.sh` | `PROTOTYPE_AUTOMATION` | metadados de commit | nenhum no baseline | 2.028 | `b9b769e019a7` |
| `SRC-NLM-HISTORY` | `contexto/historico/historico-notebooklm.json` | `DECISION_HISTORY_SOURCE` | proveniência das propostas | fontes/decisões por extração | 129.670 | `611cc0b70935` |
| `SRC-NLM-LLMS` | `contexto/llms.txt` | `NOTEBOOKLM_PROPOSAL` | índice para agentes | nenhum; comparar ao roteador | 1.334 | `7a287349c9d4` |
| `SRC-NLM-AST-MAPPER` | `contexto/map_repo_ast.py` | `PROTOTYPE_AUTOMATION` | grafo AST | nenhum antes de necessidade medida | 17.816 | `9c65abc04237` |
| `SRC-NLM-PACKAGE` | `contexto/package.json` | `TOOL_CONFIG_PROPOSAL` | dependências do protótipo | nenhum no baseline | 393 | `7cba6f692849` |
| `SRC-NLM-PRECOMMIT` | `contexto/pre-commit-review.js` | `PROTOTYPE_AUTOMATION` | hook de revisão | nenhum antes de validação | 4.545 | `d59997c83164` |
| `SRC-NLM-PRECOMMIT-V2` | `contexto/pre-commit-review-v2.js` | `PROTOTYPE_AUTOMATION` | hook de revisão v2 | nenhum antes de validação | 6.098 | `840730023326` |
| `SRC-NLM-COUPLING-REPORT` | `contexto/relatorio-analise-acoplamento.pdf` | `GENERATED_DEMO` | relatório demonstrativo | evidência histórica | 911.812 | `86c6814d940f` |
| `SRC-NLM-GRAPH-V2` | `contexto/repo_architecture_graph-v2.png` | `GENERATED_DEMO` | grafo visual | evidência histórica | 905.750 | `cadeab6a3962` |
| `SRC-NLM-GRAPH-V1` | `contexto/repo_architecture_graph.png` | `GENERATED_DEMO` | grafo visual | evidência histórica | 5.207.005 | `8b43ec06775c` |
| `SRC-NLM-REQUIREMENTS` | `contexto/requirements.txt` | `TOOL_CONFIG_PROPOSAL` | dependências propostas | nenhum no baseline | 120 | `01991adcd0e7` |
| `SRC-NLM-TECH-STACK` | `contexto/tech-stack.md` | `NOTEBOOKLM_PROPOSAL` | stack técnico | ADR, somente após verificação | 1.555 | `9ff8962c11bb` |
| `SRC-NLM-ATLAN-TEST` | `contexto/test-atlan-mcp.js` | `PROTOTYPE_AUTOMATION` | teste de integração Atlan | nenhum no baseline | 4.569 | `8810e4714304` |
| `SRC-NLM-GRAPH-VIEWER` | `contexto/visualize_graph.py` | `PROTOTYPE_AUTOMATION` | visualização de grafo | nenhum antes de necessidade medida | 5.381 | `aee0b24baf4e` |
| `SRC-PLAYER-SQLITE-HISTORY` | `hibrida/Extensão do Player e do SQLite.md` | `IMPLEMENTATION_HISTORY_SOURCE` | player e persistência | evidência/ADR por reconciliação | 19.493 | `8d6e1b2fc49c` |
| `SRC-IHF-RULES-2026-PT` | `hibrida/Regras de Handebol de Praia 2026 - Tradução 29 de maio de 2026.pdf` | `EXTERNAL_NORMATIVE_SOURCE` | regras esportivas externas | `OFFICIAL_RULES_MAPPING.md` | 15.422.591 | `a9af9932e14c` |
| `SRC-SPEC-GD` | `hibrida/analise-videos-cepraea-spec-GD.md` | `MIGRATION_SOURCE` | especificação extensa | `SYSTEM_SPEC.md` | 62.309 | `0e4e360d89ab` |
| `SRC-SPEC-LEGACY` | `hibrida/analise-videos-cepraea-spec.md` | `SUPERSEDED_SOURCE` | especificação anterior | proveniência/comparação | 36.338 | `f1d8c5b3fd98` |
| `SRC-SPEC-V2-DRAFT` | `hibrida/analise-videos-v2.md` | `DRAFT_CANDIDATE` | requisitos e módulos candidatos | SSOTs por afirmação validada | 10.463 | `2837fe8fe591` |
| `SRC-HYBRID-PLAN-MONOLITH` | `hibrida/arquitetura-hibrida.md` | `SUPERSEDED_DRAFT` | plano de migração anterior | nenhum; histórico | 51.245 | `bbec5cc6fd6d` |
| `SRC-GAME-CONCEPTS` | `hibrida/conceitos-jogo.md` | `DOMAIN_SOURCE_CANDIDATE` | conceitos esportivos | `GAME_MODEL.md` | 129.811 | `95999c656d98` |
| `SRC-CEPRAEA-HISTORY` | `hibrida/historico/analise-videos-cepraea-historico.json` | `DECISION_HISTORY_SOURCE` | proveniência histórica | fontes/decisões por extração | 355.254 | `0e2ee6fc27a6` |
| `SRC-EXECUTOR-LOG` | `hibrida/historico/executor.md` | `HISTORICAL_WORK_LOG` | execução histórica | evidência de migração | 11.253 | `dab7c30bd572` |
| `SRC-CODEX-ANALYSIS-001` | `hibrida/resposta-codex-001.md` | `DERIVED_ANALYSIS` | análise documental | nenhum; insumo de auditoria | 16.301 | `7e69d874e27f` |
| `SRC-CODEX-ANALYSIS-002` | `hibrida/resposta-codex-002.md` | `DERIVED_ANALYSIS` | análise de arquitetura | nenhum; insumo de auditoria | 11.286 | `8d9f845ff23b` |
| `SRC-GAME-OVERVIEW` | `hibrida/visao-geral-cepraea.md` | `DOMAIN_SOURCE_CANDIDATE` | visão geral esportiva | `GAME_MODEL.md` e mapeamento | 59.711 | `a222ac0bd53d` |

## Artefatos de controle contabilizados

| Arquivo | Natureza | Bytes | SHA-256 (12) |
| --- | --- | ---: | --- |
| `README.md` | índice operacional | 2.873 | `9b9770b4f59b` |
| `auditoria/notebooklm-contexto.md` | auditoria operacional | 7.651 | `1f880e4e0ec2` |
| `plano/01-governanca-e-decisoes.md` | subplano | 5.919 | `770f92d9e7a3` |
| `plano/02-migracao-ssot.md` | subplano | 4.479 | `0c07eb7eff62` |
| `plano/03-contexto-minimo.md` | subplano | 6.026 | `762bfe71baee` |
| `plano/04-rastreabilidade-e-validacao.md` | subplano | 3.534 | `00855ecc86b6` |
| `plano/05-cutover-e-operacao.md` | subplano | 4.435 | `9e1e5a63ac7` |
| `plano/PLANO-MESTRE.md` | orquestrador | 9.669 | `4f71574a707b` |

## Comparação de cópias e variantes

- Não foi encontrado nenhum par de conteúdo idêntico por SHA-256 entre os 34 arquivos do corpus.
- Não foi encontrado conteúdo idêntico por SHA-256 em outros arquivos do workspace, desconsiderando `.git/`, dependências, ambientes virtuais, builds e a pasta `baseline/`.
- Os nomes genéricos `README.md`, `Makefile` e `package.json` também existem fora da árvore inventariada, mas possuem hashes e funções diferentes; não são cópias.
- `repo_architecture_graph.png` e `repo_architecture_graph-v2.png` são variantes distintas, não duplicatas.
- `analise-videos-cepraea-spec-GD.md`, `analise-videos-cepraea-spec.md` e `analise-videos-v2.md` são variantes sem igualdade binária; a relação semântica será analisada no gate M1, não no G0.
- `conceitos-jogo.md` e `visao-geral-cepraea.md` são fontes complementares do domínio, não cópias binárias.

## Proveniência e limitações

- Todos os 24 arquivos em `contexto/` são derivados ou associados ao pacote produzido pelo NotebookLM; nenhum recebeu autoridade, foi instalado ou executado no G0.
- O PDF de regras informa 55 páginas e data de criação/modificação de 29 de maio de 2026. A autenticidade normativa e a qualidade da tradução ainda precisam de mapeamento e validação.
- O relatório PDF do contexto informa três páginas e foi gerado por ReportLab em 15 de setembro de 2026; ele permanece classificado como demonstração.
- Seis artefatos do pacote `contexto/` mudaram entre a observação preliminar e o fechamento: `Makefile`, `map_repo_ast.py`, `visualize_graph.py`, o relatório PDF e as duas imagens de grafo. O G0 não os editou nem executou. O baseline foi reiniciado após a última alteração observada, e a estabilidade dos hashes finais foi verificada antes do fechamento.
- Quando a origem ou revisão exata não pôde ser comprovada pelos próprios bytes ou metadados disponíveis, o inventário usa `unknown` e registra a lacuna em vez de inferir proveniência.

## Verificação do gate

- [x] Branch, commit-base, data e responsável registrados.
- [x] Os 36 artefatos do corpus final foram inventariados, incluindo os dois surgidos durante a execução.
- [x] SHA-256 integral registrado para cada fonte.
- [x] Tipo, origem, escopo, revisão, tamanho e destino candidato registrados.
- [x] Cópias e variantes foram comparadas.
- [x] Derivados do NotebookLM foram marcados sem promoção.
- [x] PDFs, JSONs, imagens, Markdown e códigos de protótipo permaneceram sem edição.
- [x] Os hashes são reproduzíveis com `sha256sum -c G0-SHA256SUMS.txt` executado a partir de `.local/drafts/arquitetura/`.

Resultado: **G0 aprovado tecnicamente, sem promoção de autoridade e sem decisão bloqueadora**.
