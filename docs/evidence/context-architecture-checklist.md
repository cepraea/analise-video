# Checklist da arquitetura de contexto — histórico e implementação

## Resultado da auditoria

**A arquitetura final adaptada continua parcialmente implementada.** Entrada compartilhada, procedimentos, pacote piloto, regras, hooks/Lore, modelo C4 e o grafo local A10 com vistas A11 estão presentes. PDF, MCP/Atlan, portabilidade da observabilidade, compactação e validação integral do fluxo nos dois agentes permanecem fora do estado `VERIFIED`.

Na [segunda rota com ferramentas](./context-second-route.md), ambas as propostas passaram nos testes funcionais. Codex cumpriu o protocolo; Claude inicialmente omitiu fontes/manifesto/skills. Repetições delimitadas verificaram skills/manifesto, required/confirmação e consulta/confirmação do gatilho ADR-001. O ensaio dos dois checkpoints verificou a disposição do pacote opcional e a leitura de code-review antes do diff, mas o registro da revisão precedeu o resultado da leitura e dois required regrediram; o fluxo autônomo conjunto permanece parcialmente não verificado.

| Campo | Valor |
| --- | --- |
| Data | 2026-09-16 |
| Escopo | arquitetura de contexto para Codex e Claude; arquivos, pastas, skills, memória, hooks, MCP, grafos e observabilidade |
| Fonte histórica | [historico-completo.md](../../.local/drafts/arquitetura/historico-completo.md) — 95 mensagens |
| SHA-256 da fonte | `f2f2ba7ae4a761792091e7b641c5976c72ef491ecfa25699ffad1092df3ebeb1` |
| Comparação de origem | As 95 mensagens são iguais às do JSON original preservado na cópia externa de `contexto/`. |
| Evidência anterior | [context-architecture.md](./context-architecture.md) |
| Autoridade deste documento | nenhuma; checklist de auditoria, sem alteração de decisões ou instalação de mecanismos |

Os pedidos diretos do usuário no histórico são objetivos a verificar. Davi esclareceu que, quando o NotebookLM diz “Criei” ou “corrigi”, o arquivo correspondente foi efetivamente entregue a ele. Esta auditoria reconhece essas entregas de arquivos e revisões. Avalia separadamente sua integração no repositório e a verificação de funcionamento dos bytes examinados; não presume que a cópia examinada contenha todas as revisões entregues. As recomendações do assistente também não se tornam decisões automaticamente. Para a implementação vigente, prevalecem [DECISIONS.yaml](../governance/DECISIONS.yaml), [DOCUMENTATION_STANDARD.md](../governance/DOCUMENTATION_STANDARD.md) e as ADRs com suas decisões posteriores.

Para cada artefato, distinguir três perguntas: **foi entregue pelo NotebookLM?**, **foi integrado ao projeto?** e **seu funcionamento foi verificado?** As entregas indicadas por “Criei” ou “corrigi” estão confirmadas pelo usuário; os estados da checklist abaixo descrevem os critérios de integração e verificação, conforme o escopo de cada item.

Uma caixa marcada significa que o critério específico foi observado, inclusive quando o texto delimita uma adaptação posterior. Uma caixa vazia pode indicar ausência, implementação parcial, verificação pendente ou proposta não adotada; o estado e a explicação distinguem os casos. Não há percentual global: esses itens têm escopos diferentes.

## Resumo por área

| Área | Estado observado |
| --- | --- |
| Entrada AGENTS/CLAUDE | `VERIFIED` em sessões novas via CLI, para carregamento e conferência do pacote |
| Nomes de arquivos e diretórios | conformidade parcial; histórico e padrão atual não são iguais |
| Skills compartilhadas | três procedimentos lidos e exercitados na correção técnica do ensaio de 2026-09-17; descoberta nativa permanece não configurada |
| Contexto mínimo suficiente | política e pacote piloto presentes; suficiência semântica, conformidade dos agentes e eficiência não comprovadas |
| Pre-commit de revisão | `VERIFIED` localmente, inclusive freshness seletivo do grafo contra o índice |
| Lore/commit-msg/comando Git | `VERIFIED` localmente |
| Grafo AST e vistas | A10 e vistas Mermaid de A11 `VERIFIED` localmente; PDF permanece adiado |
| Atlan MCP | `NOT_IMPLEMENTED`; a obrigatoriedade histórica conflita com a restrição posterior de custo |
| Mem0 | instalado na estação, com falhas observadas nas consultas das sessões de teste |
| Phoenix | serviço local respondendo e configuração de hooks na estação; cobertura das sessões não verificada nesta auditoria |
| C4/YAML | decisão `DOC-003` materializada em modelo YAML e duas vistas Mermaid validadas |

## 1. Entrada, estrutura e descoberta

Origens: M003–M004, M009–M018, M021–M024, M033–M035.

- [x] **ENT-01 — Centralizar as instruções do projeto em AGENTS.md — VERIFIED.** [AGENTS.md](../../AGENTS.md) é a entrada comum e aponta as fontes responsáveis; não concentra toda a SSOT em um arquivo.
- [x] **ENT-02 — CLAUDE.md conter somente `@AGENTS.md` — VERIFIED.** [CLAUDE.md](../../CLAUDE.md) tem uma linha. A sessão nova de Claude identificou a importação e citou orientações corretas sem abrir esses arquivos por ferramenta.
- [x] **ENT-03 — Entrada curta, sem manuais completos ou logs — VERIFIED para tamanho e conteúdo observado.** Após acrescentar os checkpoints em 2026-09-17, AGENTS tem 61 linhas e 3.614 bytes; CLAUDE tem uma linha e 11 bytes. Isso não mede todo o contexto inicial dos agentes.
- [x] **ENT-04 — Organizar os três procedimentos em `skills/<nome>/SKILL.md` — VERIFIED estruturalmente.** Existem `build-and-test`, `feature-workflow` e `code-review`, com nome e descrição no frontmatter.
- [x] **ENT-05 — Separar instruções de execução das fontes de arquitetura e domínio — VERIFIED estruturalmente.** Procedimentos ficam em `skills/`; fontes ficam em `docs/` e manifestos nativos. Leitura sob demanda é indicada em AGENTS.
- [x] **ENT-06 — Dispor de índice de descoberta — adaptado na consolidação posterior.** [docs/context/README.md](../context/README.md) reúne os caminhos úteis. O `llms.txt` literal do histórico foi retirado; não se deve afirmar que esse arquivo continua instalado.
- [x] **ENT-07 — Preservar descoberta das regras, stack e decisões — adaptado na consolidação posterior.** O guia aponta ADR, manifestos e catálogo de decisões. A pasta `memory/` literal foi retirada; Mem0 não substitui essas fontes.
- [x] **ENT-08 — Preservar os critérios locais de revisão — adaptado na consolidação posterior.** Estão em [skills/code-review/SKILL.md](../../skills/code-review/SKILL.md). O arquivo `REVIEW.md` literal foi retirado.
- [ ] **ENT-09 — Descoberta nativa automática das skills nos dois agentes — NOT_IMPLEMENTED no piloto.** O uso instalado é por caminhos em AGENTS, não por registro nativo do projeto. Verificar esse mecanismo antes de prometer invocação automática.
- [x] **ENT-10 — Guia operacional do desenho adotado — VERIFIED.** [docs/context/README.md](../context/README.md) documenta contexto, hooks, Lore, grafo, consulta, vistas e conferência do índice. Itens históricos retirados ou adiados não são apresentados como instalados.

## 2. Nomes de arquivos, pastas e subpastas

Origens: M001–M014. Norma vigente: `DOC-001`. Inventário anterior à criação desta checklist: 100 arquivos operacionais existentes e 29 diretórios ancestrais, incluindo arquivos ainda não versionados. Foram excluídos `archive/`, `.local/`, dependências e caches. Não houve renomeação nesta auditoria.

- [x] **NOM-01 — Caminhos operacionais sem espaços ou caracteres não ASCII — VERIFIED no inventário.** Nenhuma ocorrência nos caminhos examinados.
- [x] **NOM-02 — Diretórios documentais e auxiliares em kebab-case — VERIFIED no inventário.** Exemplos: `docs/context`, `docs/evidence/ssot-migration`, `skills/build-and-test`. Nomes técnicos reservados, como `.github`, são tratados à parte.
- [ ] **NOM-03 — Todos os diretórios obedecerem literalmente à regra genérica histórica — não atendido.** `backend/src/cepraea_video` usa underscore como pacote Python. A regra genérica deve reconhecer convenções técnicas, em vez de impor uma renomeação incompatível com imports.
- [ ] **NOM-04 — Todos os arquivos obedecerem literalmente a lowercase-kebab-case — não atendido e não adotado como regra universal atual.** Há `App.tsx`, `appMeta.ts`, `spike_storage.py`, nomes canônicos em maiúsculas e arquivos reservados. O próprio histórico também usa AGENTS, CLAUDE e SKILL em maiúsculas. Documentar convenções por responsabilidade e linguagem.
- [x] **NOM-05 — Scripts documentais em snake_case — VERIFIED.** Os scripts atuais em `scripts/docs/` atendem ao padrão vigente; o histórico chamava os protótipos Node/Bash com hífens.
- [x] **NOM-06 — ADRs no padrão `ADR-NNN-slug-kebab-case.md` — VERIFIED.** [ADR-001](../architecture/ADR-001-primeira-implementacao.md) e [ADR-002](../architecture/ADR-002-ssot-and-context.md) possuem ID e slug; a migração atualizou referências e pacote sem alterar o conteúdo da decisão.
- [x] **NOM-07 — Documentos canônicos de topo em UPPER_SNAKE_CASE — VERIFIED nos exemplos responsáveis.** SYSTEM_SPEC, GAME_MODEL, IMPLEMENTATION_PLAN e IMPLEMENTATION_STATUS seguem o padrão vigente, que difere da regra genérica do histórico.
- [x] **NOM-08 — Exceções de nomes técnicos e artefatos por ID explicitamente delimitadas — VERIFIED no verificador local.** `CODE_RULES.yaml` e `check_code_rules.py` reconhecem snake_case Python, camelCase/PascalCase JS/TS, documentos canônicos, auxiliares e IDs; baselines imutáveis ficam excluídos. Exceções exigem caminho, motivo, responsável e condição de revisão.
- [x] **NOM-09 — Ausência dos nomes genéricos explicitamente proibidos no manifesto histórico — VERIFIED no inventário.** Não foram encontrados `utils.ts`, `helpers.py`, `common.js` ou `stuff.go`. Isso não prova que todos os nomes sejam semanticamente ideais.
- [x] **NOM-10 — Prefixos funcionais históricos adaptados por contrato explícito — VERIFIED para o mecanismo delimitado.** Prefixos não são universais: cada função coberta declara comportamento e prefixos aceitos. O verificador usa AST Python para presença/nome e não trata o prefixo como prova do efeito; casos compatível e incompatível têm teste.
- [x] **NOM-11 — Validação automática da nomenclatura — VERIFIED para os caminhos e contratos configurados.** `make context-rules-check` examina o workspace; a CLI também examina índice ou commit. A exceção de ADR-001 permanece visível como alerta até a migração coordenada.

## 3. Contexto mínimo suficiente e compactação

Origens: M005–M014, M038–M041, M054–M061, M090–M091.

- [x] **CTX-01 — Política de contexto e seleção por tarefa — VERIFIED estruturalmente.** [CONTEXT_POLICY.md](../context/CONTEXT_POLICY.md) e [ROUTES.yaml](../context/ROUTES.yaml) existem e o registro de rotas é validado.
- [x] **CTX-02 — Excluir históricos, dependências e builds dos pacotes — VERIFIED no gerador e validador.** Há rejeição de árvores excluídas, travessia de caminho e symlinks. Esses controles não são um bloqueio universal de todas as ferramentas do agente.
- [ ] **CTX-03 — `.claudeignore` instalado e exclusão nativa equivalente comprovada nos dois agentes — NOT_IMPLEMENTED/NOT_VERIFIED.** O arquivo literal não existe na raiz. As instruções e controles do gerador cumprem parte da finalidade; a proteção nativa exige comprovação própria, não apenas criar um arquivo de ignore.
- [ ] **CTX-04 — Bloquear logs, binários e grandes volumes em qualquer leitura do agente — NOT_VERIFIED.** Há política de busca e exclusões, mas não foi instalado guardrail que intercepte toda leitura, Bash ou MCP.
- [x] **CTX-05 — Pacote reproduzível com dependências declaradas — VERIFIED para INC-002.** [PACKS.yaml](../context/PACKS.yaml) e [build_context_pack.py](../../scripts/docs/build_context_pack.py) resolvem dependências explícitas; a relevância não é descoberta automaticamente.
- [x] **CTX-06 — Preservar trechos, IDs, estados e hashes sem reinterpretar requisitos — VERIFIED estruturalmente no piloto.** A evidência anterior registra 16 casos de contexto e 80 testes documentais aprovados. `--check` compara a saída completa com uma regeneração em memória.
- [ ] **CTX-07 — Cobrir todos os incrementos e tipos de tarefa com pacotes — NOT_IMPLEMENTED.** Somente INC-002 está configurado; novos seletores não são inferidos pelo gerador.
- [ ] **CTX-08 — Provar cumprimento das rotas pelos agentes — NOT_VERIFIED de forma geral.** Na manutenção de contexto, esclarecer as skills fechou PACKS/manifesto além dos required. Na rota implementation_increment, esclarecimentos separados verificaram skills/manifesto, required/confirmação e consulta/confirmação da ADR-001. O ensaio posterior verificou a disposição do opcional por consulta ao filesystem; code-review foi lida antes do diff, porém seu registro ocorreu antes do resultado da leitura, e plano/rastreabilidade não foram consultados. O protocolo conjunto continua instável. Evidências: [primeira tarefa](./context-session-evaluation.md) e [segunda rota](./context-second-route.md).
- [x] **CTX-09 — Contexto suficiente para a correção técnica avaliada — VERIFIED nesse escopo.** Ambos corrigiram o mesmo defeito a partir da mesma revisão, executaram testes e revisão e passaram em oito testes independentes. Isso não verifica suficiência para um incremento de produto ou qualquer tarefa futura.
- [ ] **CTX-10 — Provar economia de tokens, latência e qualidade — VERIFIED para redução de entrada nos controles Claude/Codex; NOT_VERIFIED de forma geral.** Três pares por agente, mesmos prompts/revisão, modelo/configuração fixos dentro de cada agente: redução média Claude 59,79% e Codex 53,72%. No Codex, passaram em todos os mesmos checks 3/3 propostas técnicas e 3/3 amplas; zero tokens lidos de cache em todas as execuções, criação não exposta. O “antes” é amplo reconstruído, com uma resposta e contexto fornecido. Fluxo autônomo, outras tarefas, custo cobrado e ganho geral de latência não verificados. [Claude](./context-economy.md) e [Codex](./context-economy-codex.md).
- [x] **CTX-11 — Faixa 300–500 aplicada a código manual, sem universalização — VERIFIED no verificador local.** Até 300 linhas passa; 301–500 alerta; acima de 500 falha sem exceção completa. `App.tsx`, `App.test.tsx` e `test_baselines.py` têm limites específicos e condição de revisão; `promote_baseline.py` permanece alerta de modularização. Documentos, gerados, dependências e baselines não recebem esse teto.
- [ ] **CTX-12 — Monitoramento da faixa de 40–60% e compactação proativa — NOT_IMPLEMENTED como mecanismo do projeto.** Não há política executável que monitore essa faixa e dispare a ação. Recursos nativos dos agentes não foram validados para esse critério.
- [ ] **CTX-13 — Microcompactação automática e preservação verbatim garantida — NOT_VERIFIED.** Há orientações de preservação de caminhos e erros, mas não uma ferramenta local testada que imponha essa transformação a todo histórico.
- [ ] **CTX-14 — Externalização estruturada de tarefa antes de compactação — NOT_IMPLEMENTED no formato histórico.** Não há STATE.md ou mecanismo equivalente do projeto com objetivo ativo, decisões, arquivos alterados e próximos passos. O estado do produto e os relatórios não cumprem automaticamente essa função de sessão.
- [ ] **CTX-15 — Delegação como estratégia mensurada de isolamento — PROPOSTA TÉCNICA não verificada.** Não foi avaliada como requisito deste piloto. Uma recomendação histórica não autoriza delegação automática em qualquer tarefa.
- [ ] **CTX-16 — Contrato das cinco camadas de contexto — parcialmente descrito, não verificado.** Entrada, sessão, memória, artefatos e busca sob demanda têm elementos correspondentes, mas não há validação conjunta de quais dados entram em cada camada, precedência, atualização e orçamento. A explicação conceitual de Atlan em M039/M041 não é uma instalação dessas camadas.

## 4. Skills, revisão e pre-commit

Origens: M015–M035, M068–M069, M078–M089.

- [x] **REV-01 — Procedimento de testes com comandos reais — VERIFIED documentalmente.** [build-and-test](../../skills/build-and-test/SKILL.md) aponta manifestos e verificações por escopo, sem assumir linters ou ORM do protótipo.
- [x] **REV-02 — Critérios de revisão que priorizam riscos concretos — VERIFIED documentalmente.** [code-review](../../skills/code-review/SKILL.md) cobre originais, identidade, contratos, fatos/interpretação e evidência; distingue workspace de staging.
- [x] **REV-03 — Exercitar implementação, testes e revisão nos dois agentes — VERIFIED para a correção técnica do ensaio de 2026-09-17.** As três skills foram lidas e aplicadas. Isso não verifica um incremento completo de produto, descoberta nativa ou todos os cenários dos procedimentos.
- [x] **REV-04 — Workflow atualizar grafo e preparar Lore — VERIFIED estruturalmente.** Feature-workflow aciona A10 somente para corpus/configuração/extrator, orienta a geração contra o índice e não prepara arquivos automaticamente.
- [x] **REV-05 — Script de revisão pre-commit operacional — VERIFIED localmente.** `scripts/git/review_staged.py`, alvo `make review-staged` e hook versionado substituem os protótipos Node sem chamadas a IA/API.
- [x] **REV-06 — Hook pre-commit efetivamente ativado — VERIFIED nesta estação.** O instalador reversível criou links somente para `pre-commit` e `commit-msg`, sem tocar `pre-push`/LFS; colisões são preservadas e produzem erro explícito.
- [x] **REV-07 — Validar os bytes do índice, inclusive staging parcial — VERIFIED em teste.** O caso índice válido/workspace inválido e o inverso produzem conclusões baseadas apenas no índice.
- [x] **REV-08 — Rejeitar erros de Git e testar cenários de commit — VERIFIED para o mecanismo local.** Leitura/enumeração Git falha explicitamente; testes cobrem rename, delete, execução com raiz descoberta e instalação reversível. Nenhum arquivo é adicionado ao staging.
- [x] **REV-09 — Regras executáveis de nomes, tamanho e segredos — VERIFIED no escopo adotado.** Nomes/tamanho usam política e AST para contratos explícitos; segredos são detectados sem reproduzir valores. Tipagem, autorização de migração e efeitos semânticos permanecem na revisão contextual, sem regex genérica como prova.
- [ ] **REV-10 — Linters/formatadores integrados ao fluxo — NOT_IMPLEMENTED nos manifestos atuais.** Não há scripts de lint no frontend nem ferramentas correspondentes declaradas no backend. ORM, Alembic, Docker ou linters citados pelo assistente em M091 são sugestões; não são requisitos automaticamente aprovados da arquitetura de contexto.

## 5. Lore e mensagens de commit

Origens: M010, M027–M035, M068–M069, M082–M089.

- [x] **LOR-01 — Escopo e conjunto estável de trailers — VERIFIED no contrato local.** `Tested` ou `Not-tested` é obrigatório; `Constraint` e `Rejected` são opcionais. Valores vazios/genéricos, duplicados, deslocados e trailers Lore não suportados falham.
- [x] **LOR-02 — Hook commit-msg instalado — VERIFIED nesta estação.** O hook versionado recebe o arquivo atual do Git e a instalação é reversível.
- [x] **LOR-03 — Validar mensagem atual e bloco final — VERIFIED em testes.** O validador não lê COMMIT_EDITMSG anterior e confere título Conventional Commit e bloco contíguo final.
- [x] **LOR-04 — Skill `skills/lore-commit/SKILL.md` operacional — VERIFIED estruturalmente.** A skill descreve índice, fatos observados e autorização separada para commit.
- [x] **LOR-05 — Comando `git lore-commit` disponível — VERIFIED nesta estação.** O alias local aponta para o helper versionado e é removido por `make hooks-uninstall`.
- [x] **LOR-06 — Gerar e revisar mensagem a partir do índice — VERIFIED para o helper local.** O programa exige alterações preparadas, mostra a mensagem, valida trailers e somente chama `git commit` com `--commit`; não inventa testes nem executa staging.

## 6. Grafo de código, diagramas e relatório

Origens: M058–M089. A auditoria anterior dos protótipos continua registrada em context-architecture.md; a cópia externa foi consultada por membros exatos, sem executar hooks ou alterar originais.

- [x] **GRF-01 — Mapeador instalado para a raiz real do repo — VERIFIED.** `scripts/context/build_code_graph.py`, `GRAPH.yaml` e os alvos `graph`/`graph-check` usam raízes explícitas do repositório.
- [x] **GRF-02 — Extração Python e TypeScript/TSX confiável — VERIFIED para o escopo sintático.** Python usa `ast`; TS/TSX/JS/JSX usam a API AST do TypeScript 7, sem regex. Fixtures cobrem aliases, namespace imports, funções, métodos e arrow functions. A ferramenta não alega resolução semântica completa de tipos.
- [x] **GRF-03 — IDs e relações semanticamente delimitados — VERIFIED.** IDs incluem caminho e nome qualificado; relações registram método/confiança. Chamadas não resolvidas terminam em nós externos explícitos com confiança zero, sem serem apresentadas como resolvidas.
- [x] **GRF-04 — Integridade de endpoints e corpus atual — VERIFIED no artefato operacional.** Todos os endpoints existem e cada arquivo do corpus possui SHA-256. O JSON histórico inválido permanece preservado como evidência e não foi promovido.
- [x] **GRF-05 — Dependências e execução reproduzível do pipeline — VERIFIED localmente.** O pipeline usa Python/PyYAML e o TypeScript 7 já declarado no frontend; dependência ausente falha explicitamente. Testes executam a validação a partir de subpasta com raiz explícita.
- [x] **GRF-06 — Comandos de mapeamento e vistas completa/alto nível — VERIFIED no desenho adaptado.** Make oferece geração, check, consulta e duas vistas Mermaid sob demanda em `.local/generated/context/`. PNG histórico não é usado como prova e não é obrigatório.
- [ ] **GRF-07 — PDF regenerável da mesma revisão do grafo — NOT_IMPLEMENTED.** Faltam um comando funcional, métricas dinâmicas, diagramas sincronizados e proveniência comum. O Makefile do protótipo auditado chamava um gerador ausente.
- [x] **GRF-08 — Separar código existente, arquitetura proposta e significado esportivo — VERIFIED estruturalmente.** O JSON observado e suas vistas ficam em `docs/context/graph`/`.local/generated`; C4/YAML continua canônico para arquitetura e `GAME_MODEL.md` para significado esportivo.
- [x] **GRF-09 — Usar grafo para recuperação direcionada — VERIFIED.** `graph-query` seleciona caminho, módulo ou símbolo e limita expansão a profundidade 0–3; o JSON integral não é contexto padrão.
- [x] **GRF-10 — Comprovar freshness em relação à revisão — VERIFIED.** Configuração, extratores e cada arquivo do corpus possuem hash; o checker valida o hash interno e compara o conteúdo reconstruído com workspace, índice ou commit.
- [x] **GRF-11 — Integrar grafo ao workflow, pre-commit e CI — VERIFIED estrutural e localmente.** O revisor dispara somente por corpus/configuração/extrator e lê o índice; a CI confere o commit. Nenhum mecanismo executa staging automático.
- [x] **GRF-12 — Modelo C4/YAML e vistas coerentes — VERIFIED estruturalmente.** [C4_MODEL.yaml](../architecture/C4_MODEL.yaml) é a fonte de elementos/relações; [context.mmd](../architecture/views/context.mmd) e [containers.mmd](../architecture/views/containers.mmd) são derivados determinísticos. O validador rejeita IDs duplicados, endpoints ausentes, fontes/decisões inválidas e relações fora da vista. ADR-002 registra a evolução posterior de DOC-003. O grafo de código mantém responsabilidade separada.

## 7. MCP, memória, observabilidade e custo

Origens: M036–M057, M090–M093. Autoridade posterior relevante: GOV-NLM-001 e INFRA-001.

- [ ] **MCP-01 — Integração real de Atlan — NOT_IMPLEMENTED.** Não há configuração, skill operacional ou ferramentas Atlan disponíveis nesta sessão. Os nomes de ferramentas e payloads do histórico não comprovam um servidor real.
- [ ] **MCP-02 — Simulador local explicitamente separado da integração real — protótipo preservado, não operacional.** O teste com fallback mock não é validação de conexão, schema real ou linhagem.
- [ ] **MCP-03 — Consultas obrigatórias Atlan sem custo adicional — proposta histórica incompatível com a restrição posterior.** M054 proíbe API paga adicional. Não tornar Atlan dependência do fluxo; escolher uma alternativa local ou deixar a integração real fora do escopo, sem marcar mock como integração concluída.
- [ ] **MCP-04 — Configuração MCP reproduzível por checkout — NOT_IMPLEMENTED como arquitetura do projeto.** Há apps/plugins da estação, mas não foi encontrada configuração MCP local do repo. Disponibilidade nesta máquina não garante disponibilidade em outra estação.
- [ ] **MEM-01 — Consultas Mem0 funcionando nos dois agentes — parcialmente implementado, com falhas verificadas.** No teste Claude, a allowlist restrita recusou as buscas. No Codex, o conector recusou `app_id` com `Unknown search argument: app_id`. Harmonizar instruções e schema instalado; não alterar o pedido da ferramenta com campos inválidos.
- [ ] **MEM-02 — Captura e recuperação corretas entre agentes — NOT_VERIFIED de ponta a ponta.** Memórias foram recuperadas nesta auditoria, mas não houve teste controlado de captura, isolamento por usuário/projeto e recuperação da mesma decisão nos dois agentes.
- [ ] **MEM-03 — Política de memória versionada e aplicável — PROPOSTA TÉCNICA não implementada.** Não existe `mem0.md` no repo. Antes de adotar esse nome, confirmar seu suporte na versão instalada; o histórico descreve v0.2.15 e o Codex usa plugin v0.3.1.
- [x] **MEM-04 — Memórias como auxílio, sem autoridade normativa — VERIFIED documentalmente.** AGENTS e o guia exigem confirmação nas fontes responsáveis; GOV-NLM-001 também retira autoridade normativa das sínteses NotebookLM.
- [x] **OBS-01 — Phoenix local disponível — VERIFIED para disponibilidade.** `http://localhost:6006/healthz` respondeu HTTP 200 nesta auditoria. Isso não prova ingestão de spans.
- [ ] **OBS-02 — Captura completa dos dois agentes por sessão — IMPLEMENTED_NOT_VERIFIED nesta auditoria.** Há hooks Arize/Phoenix no settings global do Claude e hooks Mem0 no arquivo global do Codex. Não foi consultado um conjunto de spans para confirmar a cobertura das duas sessões novas.
- [ ] **OBS-03 — Implantação portátil da observabilidade — NOT_IMPLEMENTED no repo.** O harness está em `/home/davis/.arize/harness`, fora do projeto. Faltam configuração reproduzível e teste de associação entre execução, sessão e tool calls.
- [x] **CST-01 — Gerar e conferir o pacote sem dependência de API paga — VERIFIED para a automação local.** Gerador e validador usam arquivos locais. Os testes das sessões confirmaram autenticação Claude Pro e ChatGPT; não receberam chaves de API pagas do ambiente.
- [ ] **CST-02 — Garantir ausência de custo adicional em toda a estação — NOT_VERIFIED.** Não houve auditoria de faturamento dos plugins e serviços. Não estender o resultado offline do gerador a todas as integrações MCP ou à estação inteira.

## 8. Fontes e artefatos do caderno

Origens: M008–M010, M092–M094. Estes resultados documentais não são dependências obrigatórias de toda tarefa de código.

- [x] **FON-01 — Registros de fontes e decisões com responsabilidade — VERIFIED estruturalmente.** [SOURCES.yaml](../governance/SOURCES.yaml), DECISIONS, SSOT e os validadores de baselines existem. Isso não promove automaticamente as 42 fontes citadas pelo NotebookLM.
- [ ] **FON-02 — Auditoria de cada fonte com garantia, limitação, escopo e método — NOT_VERIFIED integralmente.** O histórico contém uma matriz consultiva; a revisão dos protótipos está documentada. Não foram recuperadas e verificadas todas as fontes externas nem confirmados seus percentuais e benchmarks.
- [ ] **FON-03 — Catálogo de fontes fiel e completo — NOT_VERIFIED.** A resposta M093 enumera 42 fontes, mas citações internas `[i]` não comprovam disponibilidade atual, conteúdo ou classificação. Reconciliar com as fontes efetivamente acessíveis antes de afirmar completude; não substituir SOURCES pelo texto do assistente.
- [ ] **FON-04 — PDF do catálogo pedido em M094 — não encontrado como entrega operacional.** Não há um gerador ou saída correspondente no fluxo atual. Esse PDF é diferente do relatório de acoplamento dos grafos.

## 9. Preservação e conclusão do escopo

- [x] **FIN-01 — Preservar os protótipos antes de limpar — VERIFIED na operação anterior.** [Inventário de 33 fontes](./context-source-inventory.json), cópia completa fora do repo e conferência dos 6.005 arquivos regulares foram registrados. Posteriormente, a pasta original foi restaurada integralmente a pedido de Davi, com hashes conferidos. O [registro por arquivo](./context-file-integration.md) identifica destinos e pendências dos 33 itens antes de qualquer nova limpeza. O histórico completo atual permanece disponível e não foi alterado por esta auditoria.
- [x] **FIN-02 — Separar histórico de contexto operacional — VERIFIED estruturalmente.** A pasta `contexto/` foi retirada do workspace após a cópia; `.local/drafts/` e `archive/` continuam excluídos de buscas normais e pacotes.
- [ ] **FIN-03 — Todo o desenho histórico estar integrado e funcional no projeto — NOT_IMPLEMENTED.** Os itens abertos acima impedem essa conclusão. As entregas históricas do NotebookLM são reconhecidas; a expressão “piloto verificado” descreve somente o escopo integrado e testado.
- [x] **FIN-04 — Nomes harmonizados segundo convenções por responsabilidade — VERIFIED para o escopo operacional.** O verificador local cobre linguagens, documentos, IDs e exceções; ADR-001 recebeu slug com referências regeneradas. Arquivos de framework e baselines imutáveis permanecem sob suas convenções próprias.
- [ ] **FIN-05 — Execução integral do fluxo nos dois agentes — NOT_VERIFIED.** A tarefa técnica real já tem contexto, implementação, testes e revisão registrados. Permanecem a conformidade integral das leituras e um incremento de produto; os mecanismos locais de índice, grafo e mensagem possuem testes próprios, mas ainda precisam ser observados no fluxo autônomo conjunto.

## Ordem prática para continuar

1. Corrigir as instruções/schema de memória e verificar recuperação entre os dois agentes.
2. Manter A10 e as vistas adotadas de A11 com os checks do índice/CI; retomar PDF somente por necessidade medida.
3. Exercitar o fluxo completo nos dois agentes e medir suficiência, qualidade e consumo. Usar Phoenix como evidência de observabilidade apenas quando os spans forem encontrados e associados às sessões corretas.

Essa ordem não exige publicar uma nova baseline para cada arquivo de desenvolvimento. Não instala Atlan, ORM ou um serviço remoto de revisão por causa de sugestões do histórico.

## Verificações desta auditoria

Foram extraídas as 95 mensagens sem modificar a fonte; a igualdade com o JSON histórico preservado foi confirmada. Foram inventariados caminhos operacionais, hooks Git efetivos, nomes/configurações de MCP e hooks da estação, sem imprimir credenciais. O JSON histórico inválido permanece preservado. Após A10/A11, 103 testes documentais passaram; seis exercitam diretamente o grafo e suas vistas em repositórios descartáveis.

## Referências do histórico

M000–M094 são índices zero-based da sequência JSON, permitindo localizar exatamente a mensagem sem tratar as citações numéricas internas do NotebookLM como fontes recuperadas nesta auditoria.

| Mensagens | Localização e conteúdo |
| --- | --- |
| M003 | [linha 51](../../.local/drafts/arquitetura/historico-completo.md#L51): pedido explícito de AGENTS compartilhado e CLAUDE como ponteiro |
| M006–M014 | [linha 96](../../.local/drafts/arquitetura/historico-completo.md#L96): manifesto, nomes, estrutura, compactação, llms e ignore |
| M015–M018 | [linha 231](../../.local/drafts/arquitetura/historico-completo.md#L231): organização das skills e memória documental |
| M021–M028 | [linha 321](../../.local/drafts/arquitetura/historico-completo.md#L321): revisão, script pre-commit e commit-msg Lore |
| M029–M035 | [linha 441](../../.local/drafts/arquitetura/historico-completo.md#L441): skill Lore, comando Git, QUICKSTART e invariantes |
| M042–M049 | [linha 636](../../.local/drafts/arquitetura/historico-completo.md#L636): Atlan MCP, regras, skill e simulador |
| M054 | [linha 816](../../.local/drafts/arquitetura/historico-completo.md#L816): restrição explícita a custos adicionais e APIs pagas |
| M062–M069 | [linha 936](../../.local/drafts/arquitetura/historico-completo.md#L936): extrator AST, PNG, Makefile e workflow |
| M072–M077 | [linha 1086](../../.local/drafts/arquitetura/historico-completo.md#L1086): diagrama, filtro de alto nível e relatório PDF |
| M080–M083 | [linha 1206](../../.local/drafts/arquitetura/historico-completo.md#L1206): integração do grafo ao pre-commit |
| M084–M089 | [linha 1266](../../.local/drafts/arquitetura/historico-completo.md#L1266): problemas, auditorias e entregas de revisões corrigidas; integração e funcionamento exigem verificação dos arquivos correspondentes |
| M090–M093 | [linha 1356](../../.local/drafts/arquitetura/historico-completo.md#L1356): Mem0, Phoenix, inventário de ferramentas e catálogo consultivo de fontes |
| M094 | [linha 1416](../../.local/drafts/arquitetura/historico-completo.md#L1416): pedido de PDF do catálogo; publicação do catálogo é um artefato documental separado do pipeline de contexto |
