# Arquivos da arquitetura de contexto — recuperação e integração

## Escopo e resultado

Em 2026-09-16, Davi solicitou recuperar os originais para comparação e registrar o destino e as pendências de cada arquivo antes de qualquer nova limpeza. Posteriormente, solicitou consolidar a classificação revisada e convertê-la em critérios executáveis neste mesmo registro. O documento reúne o estado observado e a proposta de integração; não substitui decisões arquiteturais nem instala os mecanismos descritos.

A pasta `.local/drafts/arquitetura/contexto/` foi restaurada integralmente no caminho original. Foram conferidos **6.005 arquivos regulares**, **206.637.710 bytes**, **4 links simbólicos** e **6.594 entradas** contra a cópia externa. Os **33 arquivos de conteúdo** também conferem com os tamanhos e SHA-256 do [inventário anterior](./context-source-inventory.json). `.venv/` e caches foram recuperados, mas não são arquivos autorais a integrar no projeto.

Origem: [backup completo](/home/davis/backups/analise-video/contexto-20260916T210901929548Z.tar.gz), SHA-256 `3844f0add419497eb0286b11c553365791f6be3bc5249a1e1159164afff960b6`. A recuperação não sobrescreveu arquivos operacionais nem executou os scripts restaurados.

Davi confirmou que “Criei” e “corrigi”, no histórico do NotebookLM, significam entregas efetivas dos arquivos ou revisões. Aqui, **entrega**, **recuperação dos bytes**, **integração operacional** e **funcionamento verificado** são dimensões separadas. A comparação abaixo se refere aos arquivos recuperados; nomes como `v2` não comprovam, por si só, a ordem de todas as revisões entregues.

## Como ler a comparação

- **Adaptado parcialmente:** existe procedimento operacional relacionado, reescrito para o projeto; não é cópia integral nem comprova todos os comportamentos do original.
- **Descoberta consolidada:** a função de índice foi reunida em documentos existentes, com os caminhos de destino explicitados.
- **Referência existente:** o documento atual ajuda a consultar o assunto; isso não significa que todo o conteúdo do original foi promovido.
- **Não integrado:** o arquivo recuperado existe, mas seu mecanismo ou saída não está instalado no fluxo operacional.
- **Preservado como fonte:** histórico recuperado para consulta explícita e auditoria, sem carregamento normal pelos agentes.

Todos os originais abaixo têm o mesmo destino de preservação: o caminho recuperado, acessível pelo link na primeira coluna, e o backup externo. A coluna de destino operacional identifica somente arquivos que existem. Caminhos futuros aparecem explicitamente como **propostos**, sem instalação nesta tarefa. A existência de destinos relacionados não equivale a `VERIFIED` para o desenho histórico completo.

## Comparação dos 33 arquivos

| Nº | Original recuperado | Tratamento atual | Destino operacional existente e diferença | Pendência de integração ou verificação |
| --- | --- | --- | --- | --- |
| 01 | [AGENTS (1).md](<../../.local/drafts/arquitetura/contexto/AGENTS (1).md>) | Adaptado parcialmente | [AGENTS.md](../../AGENTS.md), [CLAUDE.md](../../CLAUDE.md) e [ROUTES.yaml](../context/ROUTES.yaml): entrada comum, autoridade e procedimentos sob demanda. Não reproduzem Atlan obrigatório, Lore, teto de 500 linhas ou `STATE.md`. | Delimitar os itens históricos ainda adotados; resolver a obrigação Atlan conforme `INFRA-001`; verificar o fluxo completo nos dois agentes. Nenhuma substituição literal do `AGENTS.md` atual. |
| 02 | [AGENTS-v2.md](../../.local/drafts/arquitetura/contexto/AGENTS-v2.md) | Adaptado parcialmente | Mesmos destinos da linha 01. Este original permite consulta Atlan como condição para alterar schema; o projeto exige a autoridade documental competente. | Comparar as duas variantes e o histórico antes de escolher uma revisão de trabalho. Manter a autorização de mudanças de schema separada de consulta a ferramenta. |
| 03 | [Makefile](../../.local/drafts/arquitetura/contexto/Makefile) | Não integrado para o pipeline histórico | [Makefile atual](../../Makefile) mantém aplicação e contexto documental, com `context`, `context-check` e `test-docs`; não possui `graph`, `graph-full` ou `pdf`. | Se o pipeline for adotado, acrescentar alvos ao Makefile atual; corrigir localização dos scripts e fallback `\|\| .`; resolver `generate_pdf_sources.py` ausente; fornecer receita de testes; limitar `clean` às saídas próprias. Não substituir o arquivo inteiro. |
| 04 | [QUICKSTART.md](../../.local/drafts/arquitetura/contexto/QUICKSTART.md) | Adaptado parcialmente | [Guia atual](../context/README.md) documenta entrada, rotas e pacotes. Não instala hooks ou alias Lore e não afirma que esses mecanismos estão prontos. | Completar o guia depois de implementar e testar os mecanismos escolhidos. Retirar comandos inexistentes e a instrução genérica `git add .`; documentar a localização real das CLIs e instalação reversível de hooks. |
| 05 | [REVIEW.md](../../.local/drafts/arquitetura/contexto/REVIEW.md) | Adaptado parcialmente | [Skill de revisão](../../skills/code-review/SKILL.md): revisão do diff efetivo, riscos do CEPRAEA e formato acionável. O `REVIEW.md` operacional criado inicialmente foi retirado na consolidação. | Conferir cobertura de autorização, transações, idempotência, contratos e erros em revisão real. A consolidação não demonstra reconhecimento automático por serviços externos de code review. |
| 06 | [Regras-Nomes.md](../../.local/drafts/arquitetura/contexto/Regras-Nomes.md) | Referência existente | [Padrão documental](../governance/DOCUMENTATION_STANDARD.md): formatos e nomes por responsabilidade, scripts em snake_case, sem teto universal. O original pede kebab-case amplo, prefixos funcionais, limites e compactação por percentuais. | Delimitar convenções de código e regras de compactação que continuam adotadas. Não renomear indiscriminadamente arquivos técnicos. Percentuais de economia não estão verificados. |
| 07 | [SKILL.md](../../.local/drafts/arquitetura/contexto/SKILL.md) | Adaptado parcialmente | [Skill de revisão](../../skills/code-review/SKILL.md): procedimento específico do projeto, com frontmatter e revisão dos bytes corretos. Não valida trailers Lore. | Comparar com `skills-code-review-SKILL.md`; consolidar critérios necessários; implementar validação de trailers caso adotada e exercitar a skill em tarefa real. |
| 08 | [architecture-rules.md](../../.local/drafts/arquitetura/contexto/architecture-rules.md) | Descoberta consolidada; conteúdo parcial | [Guia](../context/README.md), [AGENTS.md](../../AGENTS.md) e [ADR-001](../architecture/ADR-001-primeira-implementacao.md) apontam regras e arquitetura atuais. `memory/architecture-rules.md` operacional foi retirado. | Conferir quais regras genéricas de isolamento, tipagem, estado e erros devem ser promovidas. O apontamento para ADR não incorpora automaticamente cada proibição do original; teto de linhas difere de `DOC-001`. |
| 09 | [atlan-data-context-SKILL.md](../../.local/drafts/arquitetura/contexto/atlan-data-context-SKILL.md) | Não integrado | Nenhuma skill operacional Atlan. É idêntico, por SHA-256, ao arquivo da linha 26. | Preservar ambos. Resolver o papel de Atlan sem API paga obrigatória (`INFRA-001`). Uma integração opcional exigiria ferramentas, schemas e custo reais verificados; os payloads locais não comprovam isso. |
| 10 | [claudeignore](../../.local/drafts/arquitetura/contexto/claudeignore) | Exclusões adaptadas parcialmente | [ROUTES.yaml](../context/ROUTES.yaml), [política](../context/CONTEXT_POLICY.md), [validador](../../scripts/docs/validate_routes.py) e [gerador](../../scripts/docs/build_context_pack.py) excluem árvores do contexto documental. Não existe `.claudeignore` operacional instalado. | Comparar categorias do original com as exclusões atuais, inclusive binários e datasets. Não atribuir aos validadores controle sobre toda ferramenta de leitura; qualquer configuração nativa depende de suporte e teste. |
| 11 | [commit-msg-lore.js](../../.local/drafts/arquitetura/contexto/commit-msg-lore.js) | Adaptado e integrado | [Validador Python](../../scripts/git/validate_commit_message.py) e hook versionado conferem a mensagem atual e o bloco final. | Contrato local e instalação reversível verificados; o protótipo JS permanece como fonte e não substitui o script atual. |
| 12 | [feature-workflow-SKILL.md](../../.local/drafts/arquitetura/contexto/feature-workflow-SKILL.md) | Adaptado e integrado | [Skill de incremento](../../skills/feature-workflow/SKILL.md): contexto roteado, escopo, verificações, grafo pertinente contra workspace/índice, revisão e Lore. | A10 é acionado somente por corpus/configuração/extrator; nenhum staging amplo é realizado. |
| 13 | [generate_pdf_report.py](../../.local/drafts/arquitetura/contexto/generate_pdf_report.py) | Não integrado | Nenhum gerador operacional deste PDF. | Destino **proposto**: `scripts/context/generate_pdf_report.py`. Garantir mesma revisão de JSON/PNG/PDF, dependências e execução de subpastas; separar o relatório técnico das regras esportivas embutidas, que dependem de `GAME_MODEL.md` e Davi. |
| 14 | [git-lore-commit.sh](../../.local/drafts/arquitetura/contexto/git-lore-commit.sh) | Adaptado e integrado | [Helper Python](../../scripts/git/lore_commit.py) e alias local `git lore-commit` geram, mostram, validam e opcionalmente usam a mensagem. | O helper exige fatos fornecidos e índice não vazio; commit só ocorre com `--commit`/alias e autorização da tarefa. |
| 15 | [historico/historico-notebooklm.json](../../.local/drafts/arquitetura/contexto/historico/historico-notebooklm.json) | Preservado como fonte | [Relatório](./context-architecture.md) e [checklist](./context-architecture-checklist.md) usam o histórico como proveniência. O conteúdo de 95 mensagens corresponde ao JSON envolvido em `historico-completo.md`. | Nenhuma integração como instrução operacional automática. Relacionar escolhas finais às mensagens sem confundir entrega de arquivo com instalação; conservar os bytes originais. |
| 16 | [llms.txt](../../.local/drafts/arquitetura/contexto/llms.txt) | Descoberta consolidada | [AGENTS.md](../../AGENTS.md) e [guia](../context/README.md): mapa de documentos, manifestos e skills reais. O `llms.txt` operacional criado inicialmente foi retirado. | Manter visível a adaptação do índice. Verificar links e descoberta pelos dois agentes; não descrever `llms.txt` como instalado nem o índice como prova de todos os requisitos históricos. |
| 17 | [map_repo_ast.py](../../.local/drafts/arquitetura/contexto/map_repo_ast.py) | Adaptado e integrado | [Extrator operacional](../../scripts/context/build_code_graph.py) usa AST Python e a API AST TypeScript 7, corpus configurado, IDs por caminho/qualificação, endpoints íntegros e confiança explícita. | O protótipo permanece preservado; não foi copiado porque sua regex JS/TS e corpus histórico não atendiam A10. |
| 18 | [package.json](../../.local/drafts/arquitetura/contexto/package.json) | Adaptado sem manifesto raiz novo | O [Makefile](../../Makefile) oferece a interface; a dependência TypeScript já pertence ao [manifesto frontend](../../frontend/package.json). | Não substituir o manifesto frontend nem criar pacote duplicado. |
| 19 | [pre-commit-review-v2.js](../../.local/drafts/arquitetura/contexto/pre-commit-review-v2.js) | Adaptado e integrado | [Revisor Python](../../scripts/git/review_staged.py), hook e `make review-staged` usam os bytes do índice e conferem freshness do grafo quando o gatilho ocorre. | Não há regex genérica de migração nem staging automático. |
| 20 | [pre-commit-review.js](../../.local/drafts/arquitetura/contexto/pre-commit-review.js) | Consolidado no mecanismo atual | As duas variantes históricas foram preservadas; o revisor Python único cobre índice/workspace divergentes, rename, delete e grafo stale em testes. | Nenhuma limpeza dos originais. |
| 21 | [relatorio-analise-acoplamento.pdf](../../.local/drafts/arquitetura/contexto/relatorio-analise-acoplamento.pdf) | Não integrado; saída histórica preservada | Nenhum PDF operacional correspondente. O relatório atual em Markdown é evidência da auditoria, não substituto binariamente equivalente. | Preservar este PDF. Se geração for adotada, produzir novo relatório em área de derivados, **proposta** `.local/generated/context/`, ligado ao JSON e PNG da mesma execução e com métricas verificadas. |
| 22 | [repo_architecture_graph-v2.png](../../.local/drafts/arquitetura/contexto/repo_architecture_graph-v2.png) | Substituído por derivado Mermaid sob demanda | A vista de alto nível operacional é gerada em `.local/generated/context/code-graph-high-level.mmd` e registra o hash do JSON. | Preservar o PNG histórico; não usar o nome `v2` como prova de atualização. |
| 23 | [repo_architecture_graph.png](../../.local/drafts/arquitetura/contexto/repo_architecture_graph.png) | Substituído por derivado Mermaid sob demanda | A vista completa operacional é gerada em `.local/generated/context/code-graph-full.mmd` a partir do mesmo JSON. | Preservar o PNG histórico e manter a vista fora do contexto padrão. |
| 24 | [repo_knowledge_graph.json](../../.local/drafts/arquitetura/contexto/repo_knowledge_graph.json) | Substituído por artefato operacional validado | [JSON operacional](../context/graph/repo-knowledge-graph.json) registra corpus, hashes, extratores, relações e proveniência. A cópia histórica inválida permanece preservada. | Conferir contra workspace, índice ou commit e não confundir o grafo observado com o C4 canônico de `DOC-003`. |
| 25 | [requirements.txt](../../.local/drafts/arquitetura/contexto/requirements.txt) | Não integrado para o pipeline histórico | [Dependências documentais](../../scripts/docs/requirements.txt) e [backend](../../backend/pyproject.toml) têm outras responsabilidades. A `.venv/` recuperada não foi ativada. | Destino **proposto**: `scripts/context/requirements.txt`, se o pipeline for adotado. Definir versões e instalação reproduzível de NetworkX, Matplotlib e ReportLab, sem substituir dependências do backend ou ativar automaticamente o ambiente histórico. |
| 26 | [skills-atlan-data-context-SKILL.md](../../.local/drafts/arquitetura/contexto/skills-atlan-data-context-SKILL.md) | Não integrado; duplicata exata preservada | Nenhuma skill Atlan operacional; SHA-256 idêntico à linha 09. | Mesma pendência de custo e integração real da linha 09. Identidade de bytes foi comprovada, mas nenhum dos dois originais foi removido. |
| 27 | [skills-build-and-test-SKILL.md](../../.local/drafts/arquitetura/contexto/skills-build-and-test-SKILL.md) | Adaptado parcialmente | [Skill de verificações](../../skills/build-and-test/SKILL.md): comandos existentes de backend, frontend e documentos. Não presume Ruff, Biome ou ESLint instalados. | Exercitar o procedimento nos dois agentes. Linters adicionais dependem de escolha técnica e configuração própria; não usar comandos inexistentes como evidência de qualidade. |
| 28 | [skills-code-review-SKILL.md](../../.local/drafts/arquitetura/contexto/skills-code-review-SKILL.md) | Adaptado parcialmente | [Skill de revisão](../../skills/code-review/SKILL.md) cobre revisão efetiva; o contrato de mensagem fica separado na skill Lore. | Revisão do índice/workspace divergentes tem teste local; aderência autônoma dos agentes continua delimitada pelos ensaios. |
| 29 | [skills-feature-workflow-SKILL.md](../../.local/drafts/arquitetura/contexto/skills-feature-workflow-SKILL.md) | Adaptado e integrado | [Skill de incremento](../../skills/feature-workflow/SKILL.md) integra grafo pertinente, revisão do índice e Lore. | Vistas continuam sob demanda; PDF permanece adiado. |
| 30 | [skills-lore-commit-SKILL.md](../../.local/drafts/arquitetura/contexto/skills-lore-commit-SKILL.md) | Adaptado e integrado | [Skill Lore operacional](../../skills/lore-commit/SKILL.md) delimita trailers, fatos observados, índice e autorização de commit. | Descoberta ocorre por caminho em AGENTS; descoberta nativa continua adiada conforme P05. |
| 31 | [tech-stack.md](../../.local/drafts/arquitetura/contexto/tech-stack.md) | Descoberta consolidada | [Guia](../context/README.md) aponta [backend](../../backend/pyproject.toml), [frontend](../../frontend/package.json) e [ADR-001](../architecture/ADR-001-primeira-implementacao.md). `memory/tech-stack.md` operacional foi retirado. O original lista alternativas genéricas, incluindo TypeScript 5 e Node 20. | Usar manifestos e locks atuais para versões; não promover simultaneamente Fastify/Express/FastAPI, ORMs, Docker ou linters por aparecerem no original. Conservar visível o destino do índice. |
| 32 | [test-atlan-mcp.js](../../.local/drafts/arquitetura/contexto/test-atlan-mcp.js) | Não integrado | Nenhum teste operacional real Atlan. O original transforma erro de conexão/timeout em resposta simulada de sucesso. | Se mantido como demonstração, identificar explicitamente o mock e separá-lo de teste real; custo, endpoint e ferramentas precisam de verificação própria. Não executar chamadas externas nesta recuperação nem exigir Atlan no primeiro fluxo. |
| 33 | [visualize_graph.py](../../.local/drafts/arquitetura/contexto/visualize_graph.py) | Adaptado e integrado | [Gerador de vistas](../../scripts/context/build_code_graph_views.py) valida o JSON e produz Mermaid completo/alto nível com o mesmo hash e manifesto. | O protótipo permanece preservado; derivados ficam separados em `.local/generated/context/`. |

## Adaptações de índices preservadas de forma visível

| Caminho operacional retirado na consolidação anterior | Destino atual da função | Limite |
| --- | --- | --- |
| `llms.txt` | [AGENTS.md](../../AGENTS.md) + [guia de contexto](../context/README.md) | Descoberta consolidada; nome original não instalado. |
| `memory/architecture-rules.md` | [AGENTS.md](../../AGENTS.md), [ADR-001](../architecture/ADR-001-primeira-implementacao.md) e documentos responsáveis apontados pelo guia | Não promove todas as regras genéricas do original. |
| `memory/tech-stack.md` | Manifestos reais apontados pelo guia | Versões e dependências vêm do código e dos locks. |
| `memory/decisions-log.md` | [DECISIONS.yaml](../governance/DECISIONS.yaml) e [vista gerada](../governance/DECISION_LOG.md) | Não há arquivo original `decisions-log.md` entre os 33 itens recuperados; o caminho é definido no histórico e no `llms.txt`. |
| `REVIEW.md` | [Skill de revisão](../../skills/code-review/SKILL.md) | Procedimento local; reconhecimento por serviço externo não comprovado. |

## Classificação revisada dos pedidos

| Dimensão | Registro |
| --- | --- |
| Status da proposta de integração | `PROPOSTA TÉCNICA`; consolidação e elaboração dos critérios solicitadas por Davi |
| Responsável pela consolidação | Codex; autoridade final de adoção: Davi |
| Decisões aprovadas preservadas | `GOV-001`, `DOC-001`, `GOV-005`, `GOV-NLM-001`, `INFRA-001`, `DOC-003` e demais decisões no [catálogo](../governance/DECISIONS.yaml) |
| Proveniência | histórico recuperado, esclarecimento sobre entregas do NotebookLM e revisão dos cinco pontos nesta conversa |
| Limite | classificar e definir aceitação não comprova implementação nem registra automaticamente uma nova decisão canônica |

**Mantido:** preservar o objetivo e o comportamento central. **Adaptado:** preservar o objetivo, delimitando escopo ou mecanismo. **Retirado:** retirar a exigência operacional indicada, conservando a fonte. **Adiado:** deixar fora da próxima etapa, com condição explícita de retomada. Estas classificações não substituem os estados de decisão e implementação do projeto.

A recomendação anterior de retirar limite de linhas, convenções de nomes, faixa de compactação e atualização recorrente do grafo foi revista. Os cinco pontos discutidos, incluindo `.claudeignore`, ficam **adaptados**. Isso reconhece as regras efetivamente entregues e separa sua adoção como política do projeto de uma alegação de validade científica universal.

`P01`–`P40` identificam grupos locais de pedidos e objetivos relacionados; repetições e perguntas explicativas foram consolidadas. `A01`–`A16` identificam critérios locais de aceitação neste documento, sem criar requisitos RF/RNF ou decisões novas. As referências `Mnnn` usam os índices de mensagem definidos na [checklist](./context-architecture-checklist.md#referências-do-histórico). Mem0/Phoenix aparecem na análise consultiva do assistente em M091, e C4 tem aprovação posterior em `DOC-003`; não são apresentados como pedidos diretos equivalentes a todos os demais.

| Pedido | Classificação | Escopo recomendado e condição de retomada quando adiado | Origem e aceitação |
| --- | --- | --- | --- |
| P01 — Entrada comum AGENTS | Mantido | Mapa curto de autoridade e procedimentos; detalhes sob demanda. | M003, M011; A01 |
| P02 — CLAUDE importar AGENTS | Mantido | Somente `@AGENTS.md`, sem cópia divergente de regras. | M003; A01 |
| P03 — Separar procedimentos e fontes | Mantido | Skills para execução; docs e manifestos para decisões, domínio e dependências. | M009, M015, M017; A01, A04 |
| P04 — Três skills compartilhadas | Mantido | Implementação, testes e revisão com comandos reais e escopo da tarefa. | M015, M023, M068; A01, A16 |
| P05 — Descoberta nativa das skills | Adiado | Retomar se a leitura por caminho falhar ou gerar repetição mensurável; testar suporte nas versões instaladas. | M015 e interpretação estrutural posterior; A01, A16 |
| P06 — Índice llms.txt | Adaptado | Função consolidada em AGENTS e guia atual; preservar o mapeamento de destino acima. | M011, M038; A01 |
| P07 — Camada memory/ | Adaptado | Descoberta de arquitetura, stack e decisões pelas fontes atuais; sem duplicação normativa. | M017, M034, M056; A01, A07 |
| P08 — REVIEW separado | Adaptado | Critérios locais na skill de revisão; arquivo específico só se um consumidor comprovadamente o exigir. | M019, M021, M023; A01, A08 |
| P09 — QUICKSTART | Adaptado | Guia existente com comandos instalados, localização das CLIs e instalação reversível quando houver hooks. | M033; A01, A08, A09 |
| P10 — Nomes intencionais | Mantido | Nomes por responsabilidade; evitar nomes opacos sem impor proibição cega por substring. | M001, M006, M013; A02 |
| P11 — Kebab-case e prefixos | Adaptado | Kebab-case nos caminhos aplicáveis, convenções nativas e prefixos funcionais onde correspondam ao comportamento. | M006, M010, M013; A02 |
| P12 — Faixa 300–500 linhas | Adaptado | Alerta acima de 300, limite proposto de 500 para código manual e exceções explícitas; não aplicar como teto documental universal. | M006, M010, M034; A03 |
| P13 — Rotas e pesquisa direcionada | Mantido | Required pertinente, opcionais por gatilho, busca de IDs/símbolos antes de ampliar leitura. | M005, M009, M038; A04 |
| P14 — Excluir conteúdo irrelevante | Mantido | Histórico, dependências, builds, logs e binários fora de buscas e pacotes normais; acesso explícito quando pertinente. | M005, M011, M013; A05 |
| P15 — .claudeignore | Adaptado | Preservar as exclusões; comprovar o mecanismo efetivo por agente e versão, sem atribuir efeito ao arquivo por seu nome. | M011, M015; A05 |
| P16 — Pacotes reproduzíveis | Mantido | Seletores necessários à tarefa, estados/IDs preservados, referências e hashes conferíveis. | M009, M038, GOV-001; A04 |
| P17 — Pacotes para todos os incrementos | Adiado | Criar seletores quando um incremento ou rota entrar em execução e precisar de pacote; não gerar antecipadamente cópias de tudo. | expansão posterior do roteamento; A04 |
| P18 — Compactação em 40–60% | Adaptado | Considerar a partir de 40% e compactar até 60% nas sessões com medição e mecanismo suportados; política inicial a validar. | M010, M013; A06 |
| P19 — Preservação exata de identificadores | Mantido | Caminhos, IDs, erros e comandos devem sobreviver à compactação/transferência; preservar o resultado das verificações. | M009, M010, M013; A06, A07 |
| P20 — Estado externalizado | Adaptado | Estado da tarefa antes de compactação, interrupção ou transferência; separado de decisões permanentes e estado do produto. | M010, M013; A07 |
| P21 — Delegação automática | Adiado | Retomar quando autorizada e houver subtarefas independentes com benefício observado; não tornar toda tarefa dependente de subagentes. | M013/M014, sugestão M091; A16 |
| P22 — Revisão pre-commit local | Adaptado | Checagens rápidas e pertinentes sobre o índice, sem consulta obrigatória a IA ou staging amplo automático. | M025, M080, M082; A08 |
| P23 — Regex como prova de semântica | Retirado | Retirar regex genérica como prova de tipagem, tratamento de erro ou autorização de migração; usar análise adequada e revisão contextual. | protótipos M025–M028, falhas M084/M088; A08 |
| P24 — Lore, skill, hook e comando | Adaptado | Mensagem a partir do diff efetivo, trailers conforme a mudança e fatos realmente observados. | M027, M029, M031; A09 |
| P25 — Grafo local de código | Adaptado | Mapa confiável de arquivos/imports/símbolos e recuperação por módulo; aproximações distinguidas de relações resolvidas. | M058, M062, M070, M078; A10 |
| P26 — Grafo antes do commit | Adaptado | Regenerar/conferir quando houver alteração no corpus ou extrator; validar bytes do índice. Alteração apenas documental fora do corpus não exige staging de grafo/PNG. | M068, M080, M082; A08, A10 |
| P27 — PNG completo e filtrado | Adaptado | Vistas sob demanda, da mesma revisão do JSON, sem carregar imagens em toda sessão. | M064, M072, M074; A11 |
| P28 — PDF de acoplamento | Adiado | Retomar após o grafo ser confiável e haver necessidade de exportação; sem impedir tarefas de código por falta de PDF. | M076, M086; A11 |
| P29 — C4/YAML e Mermaid | Mantido | Decisão posterior já aprovada; modelo de arquitetura separado do grafo do código existente. | DOC-003; A12 |
| P30 — Atlan obrigatório | Retirado | Retirar a obrigatoriedade do núcleo; preservar entregas. Qualquer uso opcional depende de custo, necessidade e integração real comprovados. | M042, M044, M046; M054/INFRA-001 prevalecem; A15 |
| P31 — Simulador Atlan | Adiado | Retomar somente para demonstração/teste explicitamente mockado; falha real não pode ser reportada como conexão bem-sucedida. | M048, M052; A15 |
| P32 — MCP reproduzível por checkout | Adiado | Retomar para um conector concretamente necessário; documentar instalação, isolamento e custo sem presumir apps globais em outra máquina. | M042–M048 e análise M090/M091; A15 |
| P33 — Mem0 | Adaptado | Descoberta focada, isolamento verificável e compatibilidade com o schema instalado; fontes do repo sustentam decisões. | sugestões M091/M093 e configuração da estação; A13 |
| P34 — Phoenix | Adaptado | Diagnóstico e medição com traces por sessão comprovados; leitura de traces sob demanda. | sugestões M091/M093 e configuração da estação; A14 |
| P35 — Memória/observabilidade portáteis | Adiado | Retomar após prova local de captura/recuperação e necessidade de outra estação; não copiar ambientes históricos como instalação. | sugestões M091; A13, A14 |
| P36 — Auditoria e catálogo de fontes | Adaptado | Preservar catálogo; conferir fonte individual quando sustentar uma regra/decisão. Não exigir leitura de todas as fontes em tarefas normais. | M008, M036, M092; A15 |
| P37 — PDF do catálogo | Adiado | Retomar quando houver necessidade de exportação; independente do PDF de acoplamento. | M094; A15 |
| P38 — Custo e preservação | Mantido | Assinaturas fixas, nenhuma API paga adicional obrigatória, originais intactos e derivados separados. | M054, GOV-005, INFRA-001; A15 |
| P39 — Sessões novas nos dois agentes | Mantido | Executar tarefa real, testes e revisão; separar teste estrutural de conformidade completa do fluxo. | M003 e verificações posteriores; A16 |
| P40 — Medir suficiência e eficiência | Mantido | Comparação reproduzível de recuperação, correção, tokens e latência; sem tratar bytes ou percentuais externos como ganho local. | M005, M009, M090; A16 |

## Critérios executáveis de aceitação

Cada critério define gatilho, procedimento/casos e resultado de aprovação ou falha. **Executável** significa que um implementador ou avaliador consegue reproduzir o caso e observar o resultado; não significa que a automação já esteja instalada. Os testes futuros devem usar checkout/índice temporário isolado, sem preparar ou descartar alterações do workspace atual. Registrar versão, revisão examinada, comando, código de saída e evidência no critério correspondente.

### A01 — Entrada, skills e índices

**Gatilho:** alteração em entrada, guia ou skill; sessão nova de qualquer dos dois agentes.

**Procedimento:** conferir que CLAUDE contém somente `@AGENTS.md`; abrir os três caminhos SKILL indicados em AGENTS e seus links. Em sessão nova, solicitar uma tarefa de cada procedimento e observar qual skill foi lida. Conferir os cinco destinos da tabela de consolidação, incluindo a ausência do original `decisions-log.md` no inventário. Testar um link obrigatório quebrado em cópia isolada.

**Aceitação:** entrada compartilhada descoberta, skill pertinente carregada, nenhum índice divergente e link obrigatório quebrado produz parada da ação dependente. Leitura explícita é suficiente para o piloto; descoberta nativa só pode ser declarada quando testada. Não exigir leitura integral deste registro em sessões normais.

### A02 — Nomenclatura e prefixos por responsabilidade

**Gatilho:** novo caminho ou identificador público, rename ou mudança relevante de comportamento.

**Procedimento:** delimitar caminhos documentais/auxiliares em kebab-case, scripts e módulos Python em snake_case, documentos canônicos em UPPER_SNAKE_CASE, ADRs com ID e slug, componentes React em PascalCase e configurações reservadas pelo nome nativo. Delimitar prefixos de funções: `async_` ou sufixo `Async` para operação assíncrona, `query_`/`find_` para consulta, `handle_` para evento e `mutate_` para mutação, com exceções para interfaces externas/convenções nativas. Testar cada padrão válido, nome incompatível, nome opaco e exceção registrada.

**Aceitação:** caminhos inválidos ou prefixos incompatíveis são reportados; uma exceção aplicável passa. Nomes/prefixos não substituem tipos ou prova dos efeitos da função. Planejar o slug de ADR-001 com atualização de referências e pacote; não renomear baselines ou originais.

### A03 — Tamanho de código e exceções

**Gatilho:** alteração em arquivo manual `.py`, `.ts`, `.tsx`, `.js` ou `.jsx`, inclusive testes; antes de aceitar a revisão.

**Procedimento:** contar linhas físicas com `splitlines()`, incluindo comentários e linhas vazias, sobre os bytes da revisão avaliada. Casos: 300 passa sem alerta; 301–500 passa com avaliação/alerta de modularização; 501 falha sem exceção. Excluir dependências, builds e código gerado identificado explicitamente. Exceção registra caminho, motivo, limite específico, responsável e condição de revisão; testar exceção válida e limite excedido. Inventariar arquivos existentes acima de 500 sem refatoração automática.

**Aceitação:** exceção explícita é respeitada e não funciona como liberação genérica de diretório. O limite é proposta para código manual; documentos/índices continuam sob `DOC-001`, sem teto universal. Enquanto não houver harmonização da política responsável, o levantamento é diagnóstico e não instala um bloqueio novo silenciosamente.

### A04 — Rotas, pacotes e leitura suficiente

**Gatilho:** tarefa nova, alteração de fonte/seletor ou uso de pacote.

**Procedimento:** rodar `make context-check` na raiz. Em cópia isolada, testar fonte ausente, estado pendente, pacote editado e fonte alterada; os casos inválidos devem falhar sem escrever a saída. Na tarefa real, registrar a rota, required lidos e a disposição de cada opcional (`aplicado`, `ausente` ou `não aplicável`, com motivo); condição baseada em existência exige consulta ao filesystem. Pesquisar IDs/símbolos antes de ampliar leitura. Uma checagem estrutural deve usar o procedimento técnico pertinente, sem fingir implementação de incremento; criação/revisão de feature deve cumprir a rota do incremento.

**Aceitação:** pacote válido corresponde às fontes e não transforma pendências em aprovação. Nenhum required da rota aplicável é omitido. Antes da primeira edição, inclusive testes, a confirmação curta de rota, caminhos consultados, disposição comprovada dos opcionais e pendências deve corresponder às leituras/consultas observadas anteriores; declaração sem evidência não atende o critério. Imediatamente antes de revisar o diff, code-review deve ser lida e registrada. Seletores novos só são criados quando necessários; o ganho de tamanho não comprova suficiência sem o teste A16.

### A05 — Exclusões comprovadas por ferramenta

**Gatilho:** busca normal, montagem de pacote ou mudança de configuração de exclusão.

**Procedimento:** em cópia isolada, criar marcadores inofensivos em dependência, build, log, binário e histórico; repetir tarefa normal em cada agente. Registrar resultado por ferramenta disponível: leitura direta, busca, glob, shell e MCP, sem presumir equivalência. Testar também consulta explicitamente solicitada a uma fonte histórica pertinente. `make context-check` cobre gerador/rotas, não toda leitura do agente.

**Aceitação:** marcadores irrelevantes não entram na tarefa normal; consulta histórica autorizada permanece possível e delimitada. Documentar mecanismo/configuração e versão efetivamente usados. `.claudeignore` somente recebe crédito quando seu suporte e efeito forem observados; instrução de busca, filtro e bloqueio de leitura têm garantias distintas. Um caminho de ferramenta não testado permanece `IMPLEMENTED_NOT_VERIFIED`, sem alegação de bloqueio universal.

### A06 — Faixa de compactação e retomada

**Gatilho:** sessão longa com utilização observável ou sinal de degradação/transferência.

**Procedimento:** registrar percentual e seu denominador: janela total, janela efetiva de compactação ou orçamento definido pelo harness. Não comparar percentuais de bases diferentes. Testar 39%, 40%, 59%, 60% e 85%: abaixo de 40 não há obrigação de compactar; a partir de 40 considerar; ao alcançar 60 salvar A07 e disparar o mecanismo suportado; em 85 realizar recuperação imediata. Sem telemetria, registrar a indisponibilidade e usar marco de tarefa/transferência, sem inventar percentual. Retomar após compactação e conferir objetivo, caminhos, IDs, erros e testes.

**Aceitação:** a política inicial de 40–60% opera sobre medida definida, com mecanismo testado por agente/versão; compactação não perde informação necessária. A variável Claude `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` é candidata a verificar, não configuração instalada por este registro nem prova de mecanismo equivalente no Codex. Não prometer preservação byte a byte de toda conversa por instrução textual.

### A07 — Estado da tarefa e transferência

**Gatilho:** antes de compactação, interrupção ou passagem de tarefa longa.

**Procedimento:** registrar objetivo ativo, escopo, referências das decisões, arquivos alterados e revisão avaliada, comandos/resultados das verificações, limitações e próximo passo autorizado. Destino local **proposto**: `.local/session-state/<id-da-sessao>.md`; o nome `STATE.md` não é exigido. Em sessão nova, reconstruir a tarefa desse registro e conferir as referências nas fontes responsáveis.

**Aceitação:** retomada identifica corretamente alterações e próximo passo, sem inventar testes ou tratar o estado de sessão como nova decisão. Usar um registro por tarefa/sessão, sem carregar todos os estados antigos. Material transitório continua separado de evidência permanente e fontes canônicas.

### A08 — Pre-commit e revisão do índice

**Gatilho:** alterações relevantes preparadas para commit, quando o mecanismo for implementado.

**Procedimento:** fornecer uma interface local para revisar o índice e fazê-la retornar zero apenas para os bytes válidos. Em repositório temporário testar: válido no índice/inválido no workspace e o inverso; staging parcial; rename; delete; subpasta; erro de Git. Instalar hook reversível preservando os hooks LFS existentes e repetir os casos via tentativa de commit nesse repositório temporário. Usar análise adequada para regras semânticas; proteger segredos sem reproduzir seus valores nos logs.

**Aceitação:** workspace não altera a conclusão sobre o índice; erro de Git falha explicitamente; nada é adicionado automaticamente ao staging. Checagens são locais e pertinentes, sem API ou IA obrigatória. Mudança de migração exige o contexto/autorização aplicável, não proibição por regex de todo arquivo em `migrations/`. Quando o corpus mudar, A10 é obrigatório; somente documentação fora dele não exige grafo ou PNG.

### A09 — Lore, mensagem atual e comando

**Gatilho:** geração ou validação de mensagem quando Lore fizer parte do fluxo adotado.

**Procedimento:** definir contrato: título Conventional Commit; `Tested` com verificações reais ou ausência explicitada; `Constraint` e `Rejected` quando houver restrição/alternativa relevante, sem inventar justificativa; `Not-tested` quando pertinente; demais trailers opcionais e valores delimitados. Validar o arquivo recebido pelo hook commit-msg e o bloco final. Testar mensagem válida, trailer fora do bloco final, vazio, valor genérico, opcional inválido e mensagem divergente da COMMIT_EDITMSG anterior. O helper deve mostrar a mensagem e registrar sucesso/falha da geração com cada CLI disponível.

**Aceitação:** contrato aplicável é respeitado, testes não executados não aparecem como aprovados, mensagem atual determina o resultado e geração não confunde abrir um agente com concluir um commit. Omitir trailer não aplicável é permitido pelo contrato adaptado. Commit segue a autorização da tarefa; não usar staging amplo automático nem chamada paga adicional.

### A10 — Grafo correto e atualizado para a revisão

**Gatilho:** uso do grafo ou alteração de código/configuração que mude corpus, parser ou resolução.

**Procedimento:** definir corpus operacional com exclusões de A05 e manifestar caminho/hash de cada arquivo analisado, configuração, versão do extrator e tipo de revisão: workspace, índice ou commit. Em fixtures Python/TS/TSX/JS/JSX testar imports, aliases aplicáveis, nomes iguais em módulos diferentes, chamadas não resolvidas, remoção e rename. Distinguir AST de regex e relação resolvida de aproximação. Testar endpoints inexistentes, JSON válido porém stale, grafo no staging desatualizado e divergência entre índice/workspace. Gerar/conferir na raiz e de subpasta.

**Aceitação:** IDs únicos, endpoints íntegros, corpus correto, relações com método/confiança explícitos e hashes correspondentes à revisão avaliada. Antes do commit pertinente, regenerar/conferir contra o índice; comparar conteúdo, não somente presença no staging. Grafo do workspace não prova validade do commit. Documentação fora do corpus não dispara obrigação de regeneração. Recuperação retorna apenas o subgrafo/trechos pertinentes; não enviar o JSON inteiro por padrão.

### A11 — Vistas e relatórios derivados

**Gatilho:** solicitação de PNG ou, após retomada de P28, exportação de PDF.

**Procedimento:** gerar vistas completa/alto nível do mesmo JSON validado, registrando seu hash e filtro. Quando PDF for implementado, recalcular métricas da mesma execução e associar a imagem correspondente. Testar imagem/JSON de revisões diferentes, filtro inválido, dependência ausente e execução em subpasta. Saídas ficam separadas dos originais; PDF não declara regras esportivas extraídas de um grafo de imports.

**Aceitação:** as saídas apontam a mesma origem, métricas conferem com o JSON e erro não vira relatório aparentemente válido. PNG/PDF são sob demanda e não impedem commits apenas por não terem sido exportados. Falta de gerador do catálogo não pode ser ocultada usando PDF de acoplamento.

### A12 — Arquitetura C4 e vistas Mermaid

**Gatilho:** mudança arquitetural ou consulta de uma vista aprovada.

**Procedimento:** materializar o modelo YAML conforme `DOC-003`, com IDs de elementos, relações e referências a decisões. Gerar ou validar vistas Mermaid contra esse modelo. Testar relação com elemento ausente, ID duplicado e vista divergente. Harmonizar a antiga lista de não decisões de ADR-002 com `DOC-003` sem reescrever sua história nem alterar a aprovação já existente.

**Aceitação:** YAML é a fonte dos elementos arquiteturais e Mermaid é derivado coerente; código atual, proposta futura e semântica esportiva permanecem distintos. Consultar a vista pertinente, não todas as vistas em cada tarefa. Aprovação de C4 não comprova implementação do grafo A10.

### A13 — Memória auxiliar confiável

**Gatilho:** consulta de trabalho anterior ou captura de aprendizado, quando Mem0 estiver disponível.

**Procedimento:** comparar instruções com schema efetivamente exposto; testar consulta válida e argumento não suportado sem acrescentar campos inválidos. Em teste controlado, capturar marcador não sensível, recuperar em Codex/Claude e demonstrar isolamento por projeto/usuário pelos mecanismos realmente suportados. Testar memória contraditória com documento canônico e serviço indisponível. Caso ferramenta de gravação não esteja exposta, registrar isso; captura automática só pode receber crédito com recuperação observada.

**Aceitação:** consultas focadas recuperam a informação correta, isolamento é comprovado e documentos responsáveis prevalecem. Falha da memória não bloqueia execução com fontes locais. Não prometer gravação manual por ferramenta inexistente nem suporte automático a `mem0.md`; instruções e configuração nativa são verificadas por versão.

### A14 — Observabilidade por sessão

**Gatilho:** diagnóstico, avaliação A16 ou mudança de hooks/harness.

**Procedimento:** executar uma tarefa pequena com identificador conhecido em cada agente e localizar traces ligados às sessões. Conferir ferramentas, tempos e resultados observados contra os registros locais; testar serviço indisponível e ausência de spans. Descrever a cobertura efetiva por agente, sem equiparar hooks Mem0 do Codex a exportação Phoenix.

**Aceitação:** spans são encontrados e associados à sessão/revisão corretas; endpoint healthz sozinho comprova apenas disponibilidade. Tarefa local pode continuar quando observabilidade auxiliar falhar. Retomar portabilidade só depois da prova local; ler traces sob demanda e limitar dados capturados.

### A15 — Fontes, custo, conectores e preservação

**Gatilho:** adoção de regra baseada em fonte, proposta de dependência ou nova limpeza.

**Procedimento:** para a fonte usada, registrar identidade/URL ou hash, trecho relevante, garantia, limitação e classificação da conclusão como evidência, orientação ou inferência. Conferir original contra inventário antes de qualquer migração/remoção e identificar destino/derivado. Executar geração/conferência documental local com ferramentas remotas indisponíveis. Para conector opcional, documentar necessidade e custo real antes de adoção; custo desconhecido não atende ausência de custo adicional obrigatório. Se simulador Atlan for retomado, uma conexão falha deve ser reportada como falha ou mock explícito.

**Aceitação:** fontes e originais preservados, nenhuma API paga adicional obrigatória, catálogo não carregado integralmente em tarefas comuns e mock não confundido com conexão real. `300–500`, `40–60` e ganhos publicados não são garantias universais de desempenho. PDF de catálogo só é aceito quando exportar o catálogo correspondente com proveniência; não é dependência do núcleo.

### A16 — Tarefa real, suficiência e medição

**Gatilho:** aceitação do núcleo compartilhado ou ampliação de infraestrutura de contexto.

**Procedimento:** escolher tarefa pequena com solução e testes verificáveis; executar em sessões novas independentes de Codex e Claude sobre a mesma revisão, sem API paga adicional. Observar rota, leituras, skill de implementação/testes/revisão, alteração produzida, resultado dos testes e transferência A07 quando necessária. Validar resultado funcional, sem alterar regras esportivas. Comparar configuração atual e candidata com mesma tarefa/revisão/modelo dentro de cada agente; registrar tokens, latência, leituras irrelevantes e repetidas, correção e repetições do experimento. Se não houver contador, declarar consumo não medido; separar tokens de contexto de consumo agregado.

**Aceitação:** ambos concluem o escopo corretamente com fontes suficientes, testes e revisão observáveis. Checagem de pacote não substitui execução de incremento. Ganho de eficiência só pode ser declarado com comparação e limites registrados; experimento único não estabelece percentual geral. Delegação só é exercitada quando autorizada, com tarefa independente e comparação pertinente.

## Associação entre originais e critérios

As linhas da tabela dos 33 arquivos conservam o tratamento observado. A associação abaixo acrescenta a recomendação sem converter arquivo existente em mecanismo verificado. Um original pode conter pedidos de classificações diferentes.

| Linhas dos originais | Pedidos relacionados | Critérios |
| --- | --- | --- |
| 01, 02 — AGENTS | P01–P03, P07, P10–P15, P18–P20, P24, P30, P38 | A01–A07, A09, A15 |
| 03 — Makefile | P09, P22, P25–P28 | A01, A08, A10, A11 |
| 04 — QUICKSTART | P04–P09, P22, P24–P28 | A01, A08–A11 |
| 05, 07, 28 — revisão | P04, P08, P22–P24 | A01, A08, A09, A16 |
| 06 — nomes | P06, P07, P10–P15, P18–P21 | A01–A07, A16 |
| 08 — regras de arquitetura | P07, P12, P19, P23 | A03, A07, A08, A15 |
| 09, 26 — skills Atlan | P30, P32 | A15 |
| 10 — claudeignore | P14, P15 | A05 |
| 11, 14, 30 — Lore | P24 | A09 |
| 12, 29 — workflow | P04, P12, P22, P24–P27, P39 | A01, A03, A08–A11, A16 |
| 13, 21 — gerador/PDF | P28 | A11 |
| 15 — histórico | todos os pedidos nele registrados; sugestões posteriores distinguidas acima | A15 |
| 16 — llms | P06, P07 | A01 |
| 17, 24 — extrator/JSON | P25, P26 | A10 |
| 18 — package | P25, P27 | A10, A11 |
| 19, 20 — pre-commit | P12, P22, P23, P26 | A03, A08, A10 |
| 22, 23, 33 — PNG/visualizador | P27 | A11 |
| 25 — dependências | P25, P27, P28, P38 | A10, A11, A15 |
| 27 — testes | P04, P39 | A01, A16 |
| 31 — stack | P07, P38 | A01, A15 |
| 32 — simulador | P31 | A15 |

P17, P21, P29 e P33–P37 incluem expansão de escopo, decisões posteriores ou sugestões consultivas; não presumir que exista um arquivo autoral separado para cada item entre os 33 recuperados.

## Interfaces e estado dos critérios

| Interface | Disponibilidade | Uso |
| --- | --- | --- |
| `make context-check` | existente | A04 e parte de A05; confere rotas/pacotes sem escrita |
| `make test-docs` | existente | regressões dos validadores/gerador; não prova conformidade completa dos agentes |
| `make context-rules-check` | existente | A02/A03: convenções, contagem e exceções do workspace; a CLI aceita também índice ou commit |
| `make review-staged` | existente; hook local instalado de forma reversível | A08: revisão dos bytes do índice, whitespace, regras de código e segredos sem expor valores |
| `make lore-check COMMIT_MESSAGE=<arquivo>` | existente; hook e alias local instalados | A09: mensagem atual, bloco final e contrato adaptado |
| `make graph` / `make graph-check` | existentes | A10: gerar/conferir workspace por padrão ou `GRAPH_SOURCE=index/commit` explicitamente |
| `make graph-query GRAPH_QUERY=<termo>` | existente | A10: recuperar subgrafo limitado por módulo, caminho ou símbolo |
| `make graph-views` / `make graph-views-check` | existentes | A11: vistas Mermaid completa/alto nível ligadas ao mesmo hash validado |
| `make architecture` / `make architecture-check` | existentes | A12: gerar e validar vistas Mermaid contra o modelo C4/YAML canônico |
| exportação PDF | adiada, sem comando operacional declarado | A11/P28 e A15/P37 têm finalidades diferentes |

Comandos marcados como existentes possuem implementação e teste local. A01/A04–A07/A13–A16 também exigem procedimentos observados nos agentes; validação estrutural sozinha não atende seus resultados semânticos.

| Critérios | Estado atual do mecanismo/escopo | Evidência ou lacuna |
| --- | --- | --- |
| A01 | `VERIFIED` para leitura e execução dos três procedimentos na correção técnica; `IMPLEMENTED_NOT_VERIFIED` para todos os cenários | ensaio de 2026-09-17 registrado abaixo; parada de agentes diante de referência quebrada ainda não exercitada neste ensaio |
| A02, A03 | `VERIFIED` para o verificador local delimitado | `CODE_RULES.yaml` e `check_code_rules.py` validam nomes por linguagem/responsabilidade, contratos explícitos de prefixo, faixas físicas, exceções completas e bytes de workspace/índice/commit. Cinco testes cobrem limites, nomes, prefixos, exceções e divergência índice/workspace; inferência semântica automática permanece fora do escopo |
| A04, A05 | `IMPLEMENTED_NOT_VERIFIED` para critério completo | gerador/rotas verificados; omissões de PACKS/manifesto no Claude superadas na segunda repetição de contexto. Na [segunda rota](./context-second-route.md), Codex cumpriu o protocolo. Ensaios Claude separados fecharam skills/manifesto, required/confirmação e gatilho ADR-001. O ensaio dos checkpoints verificou a disposição do opcional por consulta ao filesystem; code-review foi lida antes do diff, mas registrada prematuramente, e dois required foram omitidos. Suficiência geral e matriz de ferramentas não comprovadas |
| A06, A07 | `NOT_IMPLEMENTED` como mecanismos locais definidos aqui | preservação é orientada, mas faixa medida e transferência estruturada não foram implementadas/testadas |
| A08, A09 | `VERIFIED` localmente para scripts/hooks | revisão usa bytes do índice, não prepara staging, falha em erros e omite valores de segredo. Hook/alias são reversíveis e preservam colisões; Lore valida mensagem atual e fatos fornecidos. Seis testes cobrem índice/workspace, segredo, rename/delete/subpasta, mensagens e instalação |
| A10, A11 | `VERIFIED` localmente para o escopo adotado | AST Python/TypeScript, hashes, consulta, índice e vistas Mermaid possuem seis testes descartáveis; PDF permanece adiado |
| A12 | `VERIFIED` estruturalmente | `C4_MODEL.yaml` materializa elementos/relações com fontes e estado; duas vistas Mermaid são derivadas determinísticas. Três testes cobrem divergência, ID duplicado, endpoint ausente e visibilidade de relações; não equivale ao grafo de código A10 |
| A13, A14 | `IMPLEMENTED_NOT_VERIFIED` de ponta a ponta | ferramentas/hooks na estação com falhas ou cobertura pendente; nenhum crédito por captura não observada |
| A15 | `IMPLEMENTED_NOT_VERIFIED` para abrangência completa | recuperação/inventário e geração local verificados; fontes externas e custos de integrações opcionais não integralmente verificados |
| A16 | `VERIFIED` para tarefas delimitadas e redução de entrada nos controles Claude/Codex; `IMPLEMENTED_NOT_VERIFIED` para eficiência geral | três pares de contexto fornecido por agente: Claude 59,79%; Codex 53,72%, com cache discriminado e critérios preservados. [Segunda tarefa](./context-second-route.md) funcional aprovada nas cópias e repetições Claude. Protocolo completo aprovado somente no Codex inicial; required/confirmação e gatilho ADR aprovados em sessões Claude separadas, sem estabilidade do protocolo integral. Economia do fluxo autônomo não medida |

Os estados completos acima não anulam evidências específicas já verificadas. Nenhum critério novo foi promovido a `VERIFIED` apenas por sua redação neste registro.

## Fundamentação dos cinco pontos revisados

| Ponto | Fonte e limite da conclusão |
| --- | --- |
| P12 — linhas | originais 01/02/08 contêm a regra; [Agent Retrieval Bench, §8.6](https://arxiv.org/html/2607.24882v1#S8.SS6) examina arquivos grandes e evidência em trechos, sem estabelecer corte universal de 500 linhas. A03 define uma política de engenharia proposta para código manual. |
| P11 — nomes | originais 01/02/06 prescrevem convenções; [AI-Readable Naming Rules](https://ai-native-development.gitbook.io/archived/patterns/ai-friendly-naming-convention) recomenda nomes descritivos e lowercase/camelCase, sem exigir kebab-case universal. A02 delimita convenções e exceções. |
| P18 — compactação | [guia, §23](https://github.com/vasilyevdm/ai-agent-handbook/blob/main/COMPREHENSIVE_AGENT_ENGINEERING_GUIDE_2026.md) contém a regra de 40–60%; [variáveis oficiais do Claude](https://code.claude.com/docs/en/env-vars) documentam compactação antecipada. A06 exige base de medição e suporte testados, sem extrapolar para todos os modelos/agentes. |
| P15 — exclusões | original 10 fornece padrões; [permissões oficiais](https://code.claude.com/docs/en/permissions) e [discussão no repo oficial](https://github.com/anthropics/claude-code/issues/579) sustentam verificar o mecanismo real. A05 não presume efeito nativo só porque `.claudeignore` foi criado. |
| P25/P26 — grafo | [Knowledge Graph Based Repository-Level Code Generation](https://arxiv.org/html/2505.14394v1) publica 36,36% para Claude 3.5 Sonnet em 275 tarefas Python, sem estudar obrigação de staging em todo commit. Original 19 exige JSON quando há mudança de código e apenas recomenda PNG. A10 mantém atualização pertinente e exige correspondência com a revisão avaliada. |

Referências externas foram consultadas na revisão anterior desta conversa; seu conteúdo sustenta somente as afirmações delimitadas acima. Não há benchmark local comprovando os ganhos percentuais dessas fontes.

## Ordem de integração e conclusão

1. Integrar o núcleo de instruções/skills e executar A01/A04/A16 em uma tarefa pequena real nos dois agentes, com os destinos dos índices preservados.
2. Harmonizar/implementar A02/A03/A05–A07 conforme os limites aqui propostos; coletar as evidências e registrar as mudanças normativas no documento responsável quando houver decisão correspondente.
3. Manter A08–A11 sob testes e usar vistas A11 sob demanda. C4/A12 conserva escopo próprio; PDF continua adiado.
4. Corrigir e verificar A13/A14 se usados; retomar itens adiados somente pelos gatilhos da classificação. Medir benefício antes de ampliar infraestrutura.
5. Considerar limpeza somente depois de A15: destino e evidência por arquivo, originais recuperáveis e nenhuma perda de fonte. Esta consolidação não autoriza nova remoção.

## Limites da operação e continuidade

Nenhum arquivo operacional foi substituído por um original nesta recuperação. Hooks, alias, dependências gráficas e chamadas MCP não foram instalados ou executados. O diretório restaurado continua ignorado pelo Git e excluído do contexto normal; acesso a seus originais nesta tarefa foi explicitamente solicitado por Davi. O backup externo continua preservado.

A restrição `INFRA-001` permanece: nenhuma API paga adicional é dependência obrigatória. `DOC-003` já aprova o modelo C4/YAML; sua materialização não equivale à instalação do extrator de símbolos. Os destinos propostos desta tabela são recomendações de localização, não novas decisões de adoção.

Antes de qualquer nova limpeza, confrontar o arquivo correspondente com esta tabela, resolver as pendências pertinentes e registrar o destino efetivamente integrado e sua evidência. Nesta etapa, todos os originais permanecem recuperados, inclusive as variantes e a duplicata exata Atlan. A lista de funcionalidades e verificações continua na [checklist da arquitetura](./context-architecture-checklist.md).

## Conferências realizadas na recuperação

- SHA-256 completo do backup antes da extração; validação dos caminhos e tipos das entradas, sem extração por ancestrais simbólicos.
- Extração para diretório temporário no mesmo local e restauração do diretório `contexto` somente após conferência de cada arquivo, diretório e alvo simbólico.
- Comparação byte a byte por SHA-256 dos 6.005 arquivos regulares contra o backup; comparação dos 33 arquivos de conteúdo também contra o inventário anterior.
- Comparação dos textos e comandos recuperados com os destinos atuais; identificação da duplicata Atlan por hash e distinção entre adaptação funcional e cópia literal.
- Conferência automatizada da tabela: **33/33 arquivos** do inventário presentes, numerados sem lacunas; os 12 pares de originais/destinos adaptados ou consolidados têm bytes diferentes, conforme a reescrita documentada.
- **120 links locais válidos** no registro por arquivo, relatório e checklist. `make context-check` aprovado, com rotas e pacote INC-002 válidos; `git diff --check` aprovado. A recuperação não exigiu regenerar o pacote nem alterar suas fontes.

Não foram repetidos testes de aplicação ou os 80 testes documentais anteriores: nesta etapa foram recuperadas fontes ignoradas e alterados somente os três registros de evidência, sem mudanças no código operacional.

Essas conferências verificam recuperação e a correspondência registrada; não promovem mecanismos não instalados a `VERIFIED`.

## Conferências da consolidação revisada

Nesta atualização foi alterado somente este registro. A conferência dos hashes dos 102 arquivos operacionais capturados antes da edição confirmou que os demais permaneceram iguais; os 33 originais recuperados continuam idênticos ao inventário anterior.

Foram conferidos automaticamente:

- **40 grupos de pedidos**, sem lacunas: 13 mantidos, 17 adaptados, 2 retirados e 8 adiados. P11, P12, P15, P18 e P26 estão adaptados, conforme a revisão dos cinco pontos.
- **16 critérios**, todos com gatilho, procedimento/casos e resultado de aceitação; cada grupo de pedidos está associado a critérios existentes.
- Associação dos **33 arquivos originais**, sem omissões ou duplicações na cobertura por linha; os tamanhos e SHA-256 continuam válidos.
- Tabelas Markdown com colunas consistentes e **122 links locais válidos** neste registro, relatório e checklist.
- `make context-check` aprovado: rotas e pacote INC-002 válidos. `git diff --check` aprovado.

As verificações acima validam a consolidação documental. Os cenários funcionais A01–A16 permanecem com os estados delimitados na tabela; comandos futuros, hooks, parsers, configurações de compactação e serviços não foram implementados ou testados por esta edição. Não houve necessidade de regenerar o pacote ou repetir testes de aplicação/documentação sem mudança de código ou fontes do pacote.

## Ensaio executável posterior — 2026-09-17

Foi concluída uma correção técnica em sessões novas e checkouts isolados de Codex e Claude, com mesma revisão/prompt. Ambos leram e exercitaram as três skills, reproduziram o defeito, implementaram, testaram e revisaram. Passaram respectivamente 83 e 81 testes documentais, e oito testes independentes para cada resultado. A solução do Codex foi integrada; o pacote foi regenerado pelas fontes finais.

O [relatório do ensaio](./context-session-evaluation.md) e seu [registro JSON](./context-session-evaluation.json) preservam contexto observado, alterações, revisões, versões, sessões, consumo disponível e hashes dos artefatos externos. A01/A16 recebem crédito somente nesse escopo. A04 permanece parcial: Claude abriu os required, mas não PACKS pelo gatilho de geração/integridade nem o manifesto pertinente. Não há comprovação de eficiência geral, exclusão universal, compactação, memória, traces ou execução de incremento de produto.

Os 33 originais recuperados continuam idênticos ao inventário. Não houve nova limpeza nem instalação de hooks, grafos ou APIs adicionais. A classificação P01–P40 e a cobertura dos originais foram preservadas.

## Repetição das leituras no Claude

As duas skills foram esclarecidas e o defeito original foi repetido em sessões novas, com o mesmo prompt e código anterior à correção. A primeira repetição consultou requirements, mas ainda omitiu PACKS. Após separar a orientação na skill de implementação, a segunda confirmou PACKS antes de editar e o manifesto antes dos testes, com resultados Read sem erro. Ambas passaram nos 81 testes documentais e oito testes independentes e realizaram revisão.

O [relatório de sessões](./context-session-evaluation.md#repetição-do-claude-após-esclarecer-as-skills) e o [JSON](./context-session-evaluation.json) preservam ambas as tentativas, ordem das consultas, patches, testes e consumo disponível. A lacuna específica de leitura está fechada para a segunda execução; A04 continua não verificado em seu escopo geral. Os 33 originais permanecem preservados, e nenhuma nova limpeza ou instalação de mecanismos históricos foi realizada. A classificação P01–P40 e os demais critérios foram mantidos.

## Comparação controlada de economia — 2026-09-17

O [relatório](./context-economy.md) e o [JSON](./context-economy.json) registram três pares independentes no Claude Sonnet 4.6, com mesma tarefa/revisão/configuração e cache desativado e confirmado. O controle reconstruído fornece 25 arquivos; o recorte técnico fornece 13, mantendo os mesmos documentos técnicos, required, PACKS, manifesto e três skills. A entrada média caiu 59,79%. As seis propostas foram submetidas a 81 testes documentais, oito testes independentes, integridade do pacote e diff-check. Passaram em todos os checks 3/3 propostas técnicas e 2/3 amplas; run04 ampla falhou no caso de fechamento precedido por tab, sem reparo/repetição da resposta.

P40/A16 recebem crédito apenas pela redução de entrada nesse experimento de contexto fornecido, com uma resposta por sessão. Não há medição retroativa do startup, comparação controlada no Codex nem comprovação do consumo de todo o fluxo autônomo. `context_sources` é declaração do modelo, não leitura observada por ferramenta; o cumprimento das leituras acionadas continua sustentado pelo ensaio anterior, separado. Latência e estimativas em dólares são descritivas, sem promessa geral nem equivalência à cobrança de assinatura.

Os 33 originais e o código operacional foram preservados. As propostas permaneceram nas cópias externas e não substituíram a correção já integrada. A classificação dos 40 grupos históricos e o destino dos índices foram mantidos; nenhuma nova limpeza, hook, grafo ou API foi adotada.

## Repetição controlada no Codex — 2026-09-17

O [relatório Codex](./context-economy-codex.md) e o [JSON](./context-economy-codex.json) preservam três pares com os mesmos prompts/fontes e revisão da comparação Claude, sem chaves de API adicionais. Modelo configurado gpt-5.6-sol, esforço medium, configuração constante dentro dos grupos, sessões novas sem persistência. Codex: redução de 53,72% na entrada total, 3/3 propostas técnicas e 3/3 amplas aprovadas nos mesmos checks; zero tokens lidos de cache em todas as execuções, criação de cache não exposta.

A16/P40/CTX-10 recebem crédito pela redução de entrada no controle reconstruído desta tarefa, não pela eficiência geral da arquitetura. A entrada total inclui a parcela em cache; não é um contador apenas dos arquivos. Nenhuma ferramenta foi chamada e houve um turno por execução. Não há comprovação de leitura/ordem dos gatilhos neste ensaio de texto fornecido, de todo o fluxo com ferramentas, custos cobrados, startup histórico ou outras rotas. Os percentuais dos dois agentes não estabelecem ranking, pois modelo/tokenizador e wrapper diferem.

Os 33 originais autorais, os 40 grupos históricos, os destinos dos índices e o código operacional foram preservados. Propostas do benchmark permaneceram nas cópias externas. Nenhuma nova limpeza ou integração de hooks, grafos, compactação, MCP ou API foi realizada.
