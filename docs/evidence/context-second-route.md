# Segunda rota e fluxo autônomo — Codex e Claude

No ensaio inicial de 2026-09-17, **as duas propostas passaram no contrato funcional**, mas **somente Codex cumpriu as leituras exigidas no protocolo desta tarefa**. Claude selecionou a rota correta e corrigiu o defeito, porém omitiu três fontes obrigatórias, o manifesto e as três skills. Repetições delimitadas fecharam skills/manifesto, required/confirmação e, após explicitar o gatilho, consulta/confirmação da ADR-001. A última sessão omitiu code-review e conferência do pacote. O fluxo autônomo conjunto permanece `IMPLEMENTED_NOT_VERIFIED`; a arquitetura completa não foi aprovada.

## Tarefa, revisão e protocolo anterior às sessões

A segunda tarefa usa `implementation_increment`, distinta de `context_maintenance` do primeiro ensaio. É manutenção delimitada do spike INC-001: rejeitar nomes de mídia com byte nulo. Na base, `resolve_media("\x00.mp4")` lança `ValueError`, GET `/spike/media/%00.mp4` retorna `500` e POST `/spike/intervals` com esse nome retorna `500`. O resultado esperado é `None`, `404` e `422`, respectivamente, sem gravação inválida ou alteração de mídia.

O snapshot temporário `8db2959576a38c8eb35f0a99066840428bdecd19` preserva **108 arquivos operacionais**, incluindo mudanças locais preexistentes. HEAD do repositório de origem: `571ce15ebefe83684f963e31981b99c13e1277ad`. Não houve commit no projeto. Archive, drafts, caches e dependências não foram copiados como fontes de contexto; dependências do backend foram provisionadas separadamente, offline, em venvs próprias, a partir dos mesmos bytes instalados. O supervisor confirmou que cada processo importava o backend da cópia testada.

O [protocolo inicial](/home/davis/backups/analise-video/context-second-route-20260917T055127Z/PROTOCOL.md), [pedido idêntico](/home/davis/backups/analise-video/context-second-route-20260917T055127Z/task.txt), [oito testes independentes](/home/davis/backups/analise-video/context-second-route-20260917T055127Z/independent_checks.py) e hashes foram salvos antes das sessões. Nenhum corpus documental, solução ou implementação dos testes externos foi fornecido aos agentes. Entrada nativa e ferramentas locais estavam previstas; leitura, implementação, execução de testes e revisão seriam realizadas pelos próprios agentes. O supervisor enviou atualizações públicas durante a execução.

Escopo de edição: `backend/src/cepraea_video/spike_media.py`, `backend/tests/test_spike_media.py` e, se necessário, `backend/tests/test_spike_storage.py`. O pedido proíbe mudanças de requisitos/estados, commit, publicação, chamadas externas e delegação. As propostas permaneceram nas cópias externas: **o backend operacional não recebeu essas correções**.

## Ajustes de ambiente e tentativas preservadas

1. **Codex inicial interrompido após 216,447 s.** O sandbox com sockets restritos fez `TestClient` travar, inclusive em `/health`, e impediu bind local. Um diagnóstico sem inferência confirmou timeout com rede restrita e HTTP 200 com sockets habilitados. A sessão foi preservada em `codex-sockets-blocked*`, com sua alteração parcial e sem contador final de consumo. Uma nova cópia limpa recebeu o mesmo pedido, com `workspace-write` e `sandbox_workspace_write.network_access=true` somente no subprocesso. [Ajuste 01](/home/davis/backups/analise-video/context-second-route-20260917T055127Z/PROTOCOL-AMENDMENT-01.md).
2. **Claude inicial com entrada suprimida.** O executor usou `--setting-sources` vazio. Dois probes curtos, sem ferramentas, observaram `UNKNOWN` nessa configuração e o marcador definido exclusivamente por `CLAUDE.md` → `AGENTS.md` com `project`. Isso confirma o comportamento da versão instalada e coincide com a [documentação oficial das fontes de carregamento](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts#load-claudemd-with-the-sdk). O campo `native_entry_autoload=true` no primeiro run.json era uma intenção incorreta do executor, não prova de carregamento. Essa tentativa passou nos testes funcionais, mas não recebe crédito pela entrada nativa ou conformidade. [Ajuste 02](/home/davis/backups/analise-video/context-second-route-20260917T055127Z/PROTOCOL-AMENDMENT-02.md).
3. **Escritas fora do escopo na tentativa inválida do Claude.** A sessão criou `MEMORY.md` e `project-cepraea.md` no diretório de memória daquele checkout em `~/.claude/projects/`. O evento anterior registrava ausência de memória. Foram preservados os conteúdos completos e hashes; somente os dois arquivos novos foram removidos, restaurando sua ausência. O arquivo de projeto recebeu metadata YAML adicional, com corpo igual ao input Write. [Registro de restauração](/home/davis/backups/analise-video/context-second-route-20260917T055127Z/claude-no-entry-scope-restoration.json). Na sessão seguinte, fonte `project` habilitada, memória automática desativada por settings e variável de ambiente somente do subprocesso; nenhuma nova ferramenta Write fora do escopo foi observada.

Foram, portanto, **duas tentativas de tarefa por agente**, uma Codex interrompida e uma Claude com configuração inválida, além de dois probes de entrada. Não se declara apenas uma sessão total por agente. Pedido, código original e skills não foram ajustados para favorecer a repetição. Configurações globais foram preservadas; hooks, MCP e apps/plugins adicionais ficaram fora do ensaio. Conversas foram novas, sem resume/continue. Isso não constitui isolamento completo do sistema operacional.

## Testes e resultado funcional

| Verificação independente | Base | Codex válido | Claude com entrada válida |
| --- | --- | --- | --- |
| Oito métodos externos | falha em três métodos, com subcasos | 8/8 | 8/8 |
| Suíte backend | 11 aprovados | 12 aprovados | 13 aprovados |
| `make context-check` | aprovado | aprovado | aprovado |
| `make test-docs` | 83 aprovados | 83 aprovados | 83 aprovados |
| `git diff --check` e escopo da cópia | aprovado | aprovado | aprovado |

Os testes externos cobrem resolver/GET/POST com diferentes posições de byte nulo, ranges, Unicode, reinício, caminhos inválidos e symlink externo, preservação de registros/versões e bytes/entradas do diretório de mídia. São métodos com subcasos, não oito fluxos completos de produto. Na base, três subcasos de resolução deram erro e quatro subcasos HTTP falharam; os outros cinco métodos passaram.

Codex acrescentou um teste de integração e ampliou um teste existente para Unicode/espaços, demonstrando a regressão antes da correção. Claude acrescentou dois métodos após reproduzir o defeito. Os próprios agentes executaram a suíte backend e examinaram o diff; o supervisor repetiu os checks definidos, conferiu os patches e verificou que a AST fora de `resolve_media()` permaneceu igual. Não foram encontrados achados funcionais bloqueadores. Ambas as soluções inserem guarda de byte nulo antes das operações `Path` e alteram somente o módulo de acesso à mídia e seus testes. `test_spike_storage.py` permaneceu igual.

## Leituras observadas e ordem

Índices abaixo começam em zero por linha do JSONL. Para Claude, foram conferidos os `tool_result` correspondentes, sem erro. Para Codex, comandos de leitura encerraram com zero e renderizaram o conteúdo. Declarações finais e listagens de nomes não substituem leituras.

| Contexto/procedimento | Codex | Claude com entrada válida |
| --- | --- | --- |
| `ROUTES.yaml` | evento 4 | Read 12, resultado 13 |
| Plano, estado, rastreabilidade e decisões da rota | eventos 10 e 12; decisões lidas em duas partes | somente estado, Read 41; os demais não consultados |
| `ADR-001.md` | evento 10 | não consultada |
| `backend/pyproject.toml` | evento 10, antes da reprodução/testes | não consultado |
| feature-workflow, build-and-test, code-review | evento 4; aplicação, testes e revisão observados | nenhuma das três consultada |
| Primeiro teste pytest | 21, antes da correção | 179, antes da correção |
| Primeira edição | 19, teste; implementação 24 | 185, implementação |
| Revisão do diff | 32 | 201; depois removeu import sem uso e repetiu testes em 285 |

A entrada não foi copiada para o pedido. Codex usou carregamento nativo habilitado, sem abertura explícita de AGENTS por ferramenta; o carregamento/importação Claude foi exercitado separadamente pelo probe. A sessão válida Claude começou pela rota, ao contrário da tentativa com fonte vazia. Isso não prova que todos os conteúdos globais foram mínimos.

INC-001 não possui pacote gerado: o opcional não exige usar INC-002. Codex investigou o gatilho e não usou pacote; Claude também não usou pacote, mas não registrou conferência direta de sua existência. Não há semântica esportiva nova ou alteração de decisões nesta tarefa.

**Resultado do protocolo:** Codex `VERIFIED` para esta tarefa; Claude não aprovado para leituras/procedimentos, apesar da correção funcional. As fontes obrigatórias e skills omitidas não foram entregues por outro caminho no pedido. O primeiro uso de testes e a edição precederam qualquer leitura do manifesto/skills no Claude; nenhuma leitura tardia fechou essas omissões.

## Consumo disponível e limites

| Campo acumulado informado | Codex válido | Claude com entrada válida |
| --- | ---: | ---: |
| Entrada total Codex / `input_tokens` Claude | 426.491 | 17 |
| Leitura de cache | 346.624, contidos no total | 399.632, categoria separada |
| Criação de cache | não exposta | 26.130 |
| Saída | 6.521 | 5.278 |
| Tempo externo | 168,688 s | 112,298 s |
| USD estimado pelo CLI | não exposto | 0,3569556 |

Codex CLI `0.144.5`, modelo configurado `gpt-5.6-sol`, esforço medium; Claude CLI `2.1.179`, principal observado `claude-sonnet-4-6`, esforço medium. O JSON Claude também informa uso auxiliar de Haiku. Os campos completos das tentativas e probes estão no [JSON](./context-second-route.json). A tentativa Claude com fonte vazia informou estimativa de 0,490326 USD, e os dois probes 0,0297748 USD somados; o Codex interrompido não forneceu contador final. Essas são estimativas do CLI, não cobrança adicional comprovada. Autenticações existentes foram usadas, sem configurar nova API ou passar as três chaves Anthropic/OpenAI/Codex do ambiente aos processos.

Não há controle antes/depois de consumo neste ensaio, ranking entre agentes ou ganho geral demonstrado. Contadores acumulados não representam ocupação simultânea da janela. Não foram validados MP4 real/player, incremento completo, grafos, hooks, MCP, memória, Phoenix/traces, compactação ou transferência de estado.

## Preservação, artefatos e próxima ação

Antes da escrita destes registros, **108/108 arquivos operacionais** permaneceram iguais ao manifesto e **33/33 originais históricos** iguais ao inventário. Nenhuma limpeza de fontes foi realizada. Estados globais do produto, correções operacionais anteriores e mudanças preexistentes foram preservados.

[Artefatos completos](/home/davis/backups/analise-video/context-second-route-20260917T055127Z): protocolo e ajustes, snapshot, cópias, pedido, testes, executores, logs, respostas, patches, análise de leituras e resultados. [Codex JSONL](/home/davis/backups/analise-video/context-second-route-20260917T055127Z/codex-events.jsonl), [Claude JSONL](/home/davis/backups/analise-video/context-second-route-20260917T055127Z/claude-events.jsonl) e [análise final](/home/davis/backups/analise-video/context-second-route-20260917T055127Z/final-analysis.json) permitem conferir as conclusões. Os hashes ficam em SHA256SUMS nesse diretório; os scripts originais e ajustados também foram preservados.

Próxima ação definida no ensaio inicial: explicitar na entrada que manutenção de código também aciona feature-workflow e que fontes `required` precedem edição; repetir **somente Claude**, partindo do código anterior à correção, com a entrada ajustada e sem fornecer corpus documental. Essa ação foi executada abaixo; as omissões iniciais permanecem preservadas.

## Repetição do Claude após esclarecer a entrada

Foi acrescentado a `AGENTS.md` que corrigir defeitos/manter código aciona feature-workflow antes de editar, que reproduzir defeitos aciona build-and-test e que todos os `required` precedem edição. A entrada passou a 59 linhas e 3.121 bytes; `CLAUDE.md` e as três skills permaneceram iguais. O pacote foi regenerado a partir das fontes. Nenhum documento obrigatório foi retirado da rota.

O [protocolo congelado antes da sessão](/home/davis/backups/analise-video/context-claude-entry-retest-20260917T064526Z/PROTOCOL.md) usa snapshot `83b3a1e1ea2036f10abd6d665c15a7473551a956`, derivado da base anterior com somente AGENTS e pacote alterados. Código defeituoso, testes originais, skills, pedido e testes independentes têm os mesmos bytes do ensaio anterior. Foi executada **uma sessão nova somente do Claude**, `0e15e315-12ad-4c5c-a047-7873d0387073`, com a mesma configuração válida de entrada `project`, memória automática desativada e principal Sonnet 4.6/medium. Nenhum conteúdo documental ou lembrete de caminhos foi acrescentado ao pedido. Não houve repetição do Codex nem nova tentativa após as omissões.

| Consulta/ação | Evento da ferramenta → resultado no JSONL |
| --- | --- |
| ROUTES | Read 24 → 25, sem erro |
| AGENTS | Read 26 → 27, sem erro |
| feature-workflow | Read 98 → 99, sem erro |
| build-and-test | Read 100 → 101, sem erro |
| code-review | Read 102 → 103, sem erro |
| Manifesto backend | Read 118 → 119, sem erro |
| Plano, estado, rastreabilidade e decisões | **nenhum consultado** |
| ADR-001 / existência do pacote INC-001 | consulta/conferência não observada |
| Primeiro pytest e reprodução resolver/HTTP | 280 → 283; 295 → 296; 320 → 321 |
| Primeira edição, teste de regressão | Edit 395 → 396 |
| Regressão falha antes da correção | Bash 398 → 399, falha esperada |
| Correção | Edit 401 → 402 |
| Backend passa / revisão do diff | Bash 404 → 405; 407 → 408 |

**Resultado funcional:** 8/8 métodos independentes, 12 testes backend e 83 documentais aprovados; context-check e diff-check aprovados. A base continuava passando em 11 testes backend/83 documentais e falhando nos três métodos independentes do defeito. O supervisor conferiu importação da cópia, patch e escopo: somente módulo de mídia e seu teste, sem arquivos novos. A AST fora de `resolve_media()` permaneceu igual; nenhum achado funcional bloqueador. A guarda rejeita byte nulo antes de `Path`, e o teste cobre resolver, GET, POST e ausência de persistência. A proposta permanece externa ao backend operacional.

**Resultado do protocolo:** as três skills e o manifesto foram efetivamente consultados antes das ações dependentes. Entretanto, **a adesão aos required continua reprovada**, agora com quatro omissões. A mera leitura da entrada/skill não comprova cumprimento do procedimento. A hipótese de que esclarecer o gatilho resolveria todas as omissões não foi confirmada por esta execução. A resposta final declarou nenhum opcional aplicável, sem conferir diretamente a existência do pacote; não se atribui crédito por essa declaração.

Uso nativo acumulado: 15 tokens de entrada, 24.562 de criação de cache, 320.594 de leitura de cache e 6.335 de saída; 126,912 s externos e estimativa CLI de USD 0,3397002, incluindo uso auxiliar Haiku. São categorias separadas e acumuladas, não ocupação da janela, cobrança comprovada ou economia controlada. A revisão de entrada não foi repetida no Codex.

Antes de atualizar os registros, o manifesto de 110 arquivos operacionais mostrou alteração somente em AGENTS e pacote; os 33 originais permaneceram iguais e todos os hashes congelados do protocolo/pedido/testes/executores foram conferidos. Não houve limpeza. [Logs nativos](/home/davis/backups/analise-video/context-claude-entry-retest-20260917T064526Z/claude-events.jsonl), [análise estruturada](/home/davis/backups/analise-video/context-claude-entry-retest-20260917T064526Z/final-analysis.json), [testes independentes](/home/davis/backups/analise-video/context-claude-entry-retest-20260917T064526Z/independent_checks.py) e resultados estão no mesmo diretório; o JSON existente preserva o ensaio inicial e acrescenta esta repetição.

Próxima ação definida nessa repetição: investigar a seleção de contexto que levou Claude a ignorar required apesar de ler entrada e skill; avaliar uma confirmação curta das fontes obrigatórias antes de editar, sem fornecer seu conteúdo no pedido. Essa avaliação foi executada abaixo; o resultado negativo anterior permanece preservado.

## Avaliação da confirmação curta antes da primeira edição

**Investigação:** a sessão anterior recebeu ROUTES, AGENTS e feature-workflow com resultados sem erro. Os quatro required existiam, com conteúdo, e não houve tentativa de consultá-los nem recusa de leitura correspondente. Portanto, carregamento ausente da entrada, arquivos ausentes ou erro registrado da ferramenta não explicam aquela omissão. O comportamento observado foi execução parcial do procedimento; a causa interna do modelo não foi estabelecida. [Investigação e hashes das fontes](/home/davis/backups/analise-video/context-claude-required-confirmation-20260917T071025Z/INVESTIGATION.md).

A intervenção acrescenta somente uma frase em AGENTS: antes da primeira edição, inclusive testes, confirmar rota, caminhos required consultados e pendências, consultando as faltas antes de editar. Não enumera documentos da rota na entrada nem fornece conteúdos no pedido. AGENTS passou de 59 linhas/3.121 bytes para 61 linhas/3.320 bytes; o pacote foi regenerado. As três skills, CLAUDE, rotas e obrigações permaneceram iguais.

O [protocolo anterior à sessão](/home/davis/backups/analise-video/context-claude-required-confirmation-20260917T071025Z/PROTOCOL.md) registra snapshot `b52fdd2f3f7cbea7db2e673f4c1a592b12853241`, derivado da base defeituosa anterior. A comparação dos 108 arquivos do snapshot encontrou diferenças somente em AGENTS e pacote. Pedido, código, testes, dependências, skills e configuração Claude são idênticos; nenhum lembrete ou corpus foi fornecido no pedido. Foi executada uma única sessão nova somente do Claude, `566a2e35-7eee-4c0e-98e5-e2bbec0929ac`, Sonnet 4.6/medium. Sem tentativa adicional após o resultado; Codex não foi repetido.

| Consulta/ação | Evento → resultado no log nativo |
| --- | --- |
| ROUTES / feature-workflow | Read 24 → 27 / 25 → 26, sem erro |
| Plano | Read 48 → 49, sem erro |
| Estado | Read 50 → 51, sem erro |
| Rastreabilidade | Read 52 → 53, sem erro |
| Decisões | Read 54 → 55, sem erro |
| build-and-test / code-review | Read 67 → 68 / 69 → 70, sem erro |
| Manifesto backend | Read 91 → 92, sem erro |
| Confirmação curta | mensagem 253, depois das leituras e antes de qualquer edição |
| Existência do pacote INC-001 | Glob 254 → 255, sem correspondência |
| Reprodução da lógica Path / HTTP | Bash 257 → 258 / 289 → 290 |
| Primeira edição / teste acrescentado | Edit 292 → 293 / 295 → 296 |
| Backend / verificação após correção / diff | Bash 298 → 299 / 301 → 302 / 304 → 305 |
| ADR-001 | **não consultada** |

A confirmação no evento 253 informou `rota=implementation_increment`, os caminhos completos dos quatro required e `pendências=nenhuma`. Todos têm resultados de leitura anteriores, sem erro. A declaração recebeu crédito por essa correspondência, não somente por seu texto. A existência do pacote foi conferida antes da edição; INC-002 não foi usado como substituto. A entrada veio pela importação nativa, sem Read explícito de AGENTS nesta sessão.

**Resultado:** confirmação e consulta dos required `VERIFIED` para esta execução; skills/manifesto consultados antes das ações dependentes. Funcionalidade aprovada nos mesmos 8 métodos independentes, 12 testes backend e 83 documentais; context-check, diff-check e escopo aprovados. O agente reproduziu HTTP 500 antes de editar e 404/422 após corrigir; a simulação Path anterior mostrou ValueError, e a chamada direta ao resolver após corrigir retornou None. Acrescentou o teste depois da correção: não se declara execução do novo teste falhando antes dela. A AST fora de resolve_media permaneceu igual, e não houve achado funcional bloqueador. A cobertura independente de Unicode/espaços é do supervisor; a declaração final do agente sobre esses casos nos testes existentes não recebe crédito como execução específica.

**Limite restante:** ADR-001 constava como contexto aplicável no protocolo congelado e não foi consultada. O protocolo completo da sessão e o fluxo conjunto permanecem `IMPLEMENTED_NOT_VERIFIED`. Esta observação favorável à confirmação curta não comprova causa isolada, confiabilidade geral ou nova validação da entrada no Codex.

Uso acumulado nativo: 14 tokens de entrada, 30.103 de criação de cache, 371.985 de leitura de cache, 6.037 de saída; 123,276 s externos. Estimativa CLI USD 0,3838805 incluindo uso auxiliar Haiku; não é cobrança comprovada nem economia de contexto demonstrada. Mesmas autenticações, sem fornecer novas chaves ou instalar dependências.

Antes de atualizar os registros, 110 arquivos operacionais foram conferidos: somente entrada/pacote tinham mudado. Os 33 originais e todos os hashes congelados permaneceram iguais. A correção fica na cópia externa, sem integração ao backend operacional, commit, publicação ou limpeza. [Logs](/home/davis/backups/analise-video/context-claude-required-confirmation-20260917T071025Z/claude-events.jsonl), [análise estruturada](/home/davis/backups/analise-video/context-claude-required-confirmation-20260917T071025Z/final-analysis.json) e testes/resultados estão preservados no mesmo diretório. O JSON existente mantém os ensaios anteriores e acrescenta esta avaliação.

Próxima ação definida nessa avaliação: delimitar o gatilho de consulta à ADR pertinente na skill antes de repetir o protocolo completo. Esse esclarecimento foi aplicado abaixo; a omissão observada permanece preservada.

### Gatilho da ADR explicitado na skill

`skills/feature-workflow/SKILL.md` agora exige consulta antes da ação dependente, inclusive edição de testes, ao implementar, corrigir ou verificar comportamento governado pela ADR, mesmo preservando a arquitetura. Acesso à mídia local, preservação de originais e persistência de intervalos acionam ADR-001; mudanças na arquitetura de contexto acionam ADR-002 conforme a rota. Alterações editoriais ou refatorações sem impacto nesses comportamentos dispensam ADR adicional, mantendo required/opcionais acionados. A confirmação curta inclui caminho/gatilho da ADR ou motivo de não aplicação.

Este esclarecimento documental não reclassifica os resultados anteriores. A validação pedida foi executada abaixo.

### Validação do gatilho ADR em sessão nova

O [protocolo congelado antes da sessão](/home/davis/backups/analise-video/context-claude-adr-trigger-20260917T072734Z/PROTOCOL.md) usou snapshot `a9bc240b57a66b8418881578035d3fec3cf9ffd0`, derivado da base defeituosa anterior. Nos 108 arquivos rastreados, somente feature-workflow e o pacote regenerado diferiam. Pedido, AGENTS, CLAUDE, rotas, código, testes, outras skills, dependências e configuração do Claude eram idênticos. Nenhum corpus documental, solução ou lembrete de caminhos foi incluído no pedido.

Foi executada uma única sessão nova somente do Claude, `984de1c5-260d-44d8-b3e2-50e92b30fedb`, Sonnet 4.6/medium. Memória automática, hooks e MCP permaneceram desativados no subprocesso. Não houve repetição do Codex nem nova tentativa após o resultado.

| Consulta/ação | Evento → resultado no log nativo |
| --- | --- |
| ROUTES / feature-workflow | Read 19 → 20 / 21 → 22, sem erro |
| Plano, estado, rastreabilidade, decisões | Read 98 → 99 / 100 → 101 / 102 → 103 / 104 → 105, sem erro |
| ADR-001 | Read 132 → 133, sem erro |
| build-and-test | Read 146 → 147, sem erro |
| Manifesto backend | Read 157 → 158, sem erro |
| Confirmação de rota, required, ADR e gatilho | mensagem 284 |
| Primeiro teste/reprodução Path/HTTP | Bash 285 → 286 / 303 → 304 / 328 → 329 |
| Primeira edição | Edit 413 → 414 |
| Backend depois da correção / revisão do diff | Bash 421 → 422 / 424 → 425 |
| code-review | **não consultada** |
| Existência do pacote INC-001 | **não conferida** |

O Claude leu ADR-001 antes da primeira reprodução e antes de editar. A confirmação anterior aos testes declarou `ADR=docs/architecture/ADR-001.md (gatilho: acesso à mídia INC-001)`, depois da leitura correspondente sem erro. O próprio agente descreveu que rejeitar nomes inválidos aciona o gatilho mesmo sem mudança de stack. Portanto, **consulta e confirmação do gatilho ADR estão VERIFIED para esta sessão**. Os quatro required também foram lidos e confirmados antes das ações dependentes.

**Resultado funcional:** a base continuava falhando em três dos oito métodos independentes. A proposta passou em 8/8, nos 12 testes backend, 83 documentais, context-check e diff-check; escopo aprovado. A AST fora de `resolve_media()` permaneceu igual e não houve achado funcional bloqueador. O agente reproduziu o `ValueError` antes da edição e o supervisor verificou resolver None, GET 404, POST 422, ausência de persistência, ranges, Unicode/espaços, reinício, caminhos/symlinks, versões e preservação de mídia. A correção e os testes permanecem somente na cópia externa.

**Limites:** a sessão não consultou code-review e não conferiu a existência do pacote INC-001. O diff foi examinado, mas isso não substitui a skill exigida. Por isso o gatilho ADR está aprovado isoladamente e o protocolo integral continua `IMPLEMENTED_NOT_VERIFIED`. A sessão também não testou parada diante de required/ADR ausente, MP4 real ou confiabilidade em outras tarefas.

Uso nativo acumulado: 15 tokens de entrada, 35.699 de criação de cache, 443.929 de leitura de cache e 5.458 de saída; 96,683 s externos. Estimativa CLI USD 0,4303677, incluindo uso auxiliar Haiku. Esses contadores não medem ocupação da janela, cobrança comprovada ou economia controlada.

Antes de atualizar os registros, 110 arquivos operacionais e 33 originais permaneceram iguais aos manifestos; os arquivos congelados do protocolo conservaram seus hashes. [Logs](/home/davis/backups/analise-video/context-claude-adr-trigger-20260917T072734Z/claude-events.jsonl), [análise estruturada](/home/davis/backups/analise-video/context-claude-adr-trigger-20260917T072734Z/final-analysis.json), patch e resultados estão preservados no mesmo diretório.

Próxima ação definida nessa sessão: não ajustar novamente o gatilho ADR, que foi observado corretamente. Investigar por que a leitura de code-review e a conferência do pacote regrediram antes de declarar o protocolo completo estável. A investigação foi realizada abaixo.

### Investigação das duas omissões

A sessão anterior `566a2e35-7eee-4c0e-98e5-e2bbec0929ac`, que executou as duas ações, foi comparada com a sessão ADR `984de1c5-260d-44d8-b3e2-50e92b30fedb`. Pedido, código defeituoso, entrada, rota, build-and-test, code-review, dependências, modelo e configuração eram iguais. O novo gatilho ADR permaneceu inalterado durante esta investigação.

**Code-review:** o arquivo existia nas duas cópias com o mesmo SHA-256 `73f717f9a90aeed2555398e585a12e15fc2983796378be15206d8c53e9a36924`. AGENTS exige sua leitura e o conteúdo de feature-workflow recebido pelo Claude mencionava explicitamente `skills/code-review/SKILL.md`. Não houve tentativa de Read, erro ou recusa de permissão. O processo terminou normalmente, executou `git diff` no evento 424 e produziu uma revisão própria. A omissão é classificada como **adesão procedural seletiva**, sem falha de descoberta/disponibilidade: o modelo substituiu a fonte exigida por sua capacidade genérica. A causa interna não é observável. Falta um checkpoint verificável imediatamente antes da revisão; a confirmação pré-edição cobre required e ADR, não esse procedimento tardio.

**Pacote INC-001:** ele não existia em nenhuma das duas cópias. Na sessão anterior, Glob 254 → 255 comprovou `No files found`; na sessão ADR não houve consulta e a resposta final omitiu o opcional. O contrato `when: generated_pack_exists` depende de uma consulta de existência para ser avaliado, mas a rota/skill não torna essa consulta explícita para incrementos diferentes de INC-002, nem a confirmação curta exige registrar a disposição dos opcionais. A omissão é classificada como **lacuna de executabilidade do gatilho**, além da adesão do agente: assumir “não aplicável” pode parecer coerente sem produzir evidência.

Não há evidência de arquivo ausente/divergente, falha da ferramenta, permissão negada, término anormal ou `--max-turns`. Ambas as sessões informaram 21 turnos, mas isso não demonstra teto causal. Uma única comparação também não demonstra que o texto ADR tenha causado as omissões; variação do modelo ou competição de atenção continuam hipóteses, não conclusões.

[Investigação completa](/home/davis/backups/analise-video/context-claude-adr-trigger-20260917T072734Z/OMISSIONS-INVESTIGATION.md) e [dados comparativos](/home/davis/backups/analise-video/context-claude-adr-trigger-20260917T072734Z/omissions-investigation.json) preservam eventos, hashes e inferências. AGENTS, rotas, skills e pacote não foram modificados pela investigação.

Próxima ação definida nessa investigação: preservar o gatilho ADR e acrescentar, em mudança separada, dois controles curtos: disposição comprovada dos opcionais na confirmação pré-edição e consulta/registro de code-review imediatamente antes da revisão. Os controles foram implementados abaixo.

### Checkpoints de opcionais e revisão

AGENTS e feature-workflow agora exigem que cada opcional da rota apareça antes da primeira edição como `aplicado`, `ausente` ou `não aplicável`, com motivo. Condições baseadas em existência exigem consulta ao filesystem; ausência presumida não atende ao checkpoint. Imediatamente antes de revisar o diff, o agente deve ler code-review e registrar `revisão=skills/code-review/SKILL.md consultado`.

O gatilho ADR não foi alterado. Esta mudança implementa os checkpoints documentalmente, mas não os promove a `VERIFIED`: ainda requer uma sessão nova sobre a mesma base defeituosa, sem corpus manual. A parada diante de fonte obrigatória ausente permanece um cenário separado.

### Validação comportamental dos dois checkpoints

O [protocolo congelado](/home/davis/backups/analise-video/context-claude-checkpoints-20260917T084852Z/PROTOCOL.md) partiu da mesma base defeituosa, pedido, testes, rota, ADR, dependências, modelo e configuração. Somente AGENTS, feature-workflow e o pacote derivado continham os dois checkpoints. Foi executada uma sessão nova do Claude, `3cbe8c56-5f91-4783-a834-b4fa043daca2`, sem corpus ou lembrete de caminhos no pedido e sem repetição automática.

| Controle | Evidência e resultado |
| --- | --- |
| Disposição do pacote opcional | Glob 137, resultado 138 sem correspondência; confirmação 304 registrou `docs/context/packs/INC-001.md: ausente (verificado no filesystem)` antes da primeira edição 401. **VERIFIED nesta sessão.** |
| Leitura de code-review | Read 417, resultado 418 sem erro, antes do diff 419. A leitura anterior à revisão ocorreu. |
| Registro posterior à leitura | A frase `revisão=skills/code-review/SKILL.md consultado` apareceu no evento 416, antes do resultado 418. **NOT_VERIFIED** para a ordem exigida; a alegação prematura não recebe crédito. |
| Required da rota | Estado e decisões foram lidos; plano e rastreabilidade não foram. A confirmação 304 os identificou como “não lido” e, contraditoriamente, declarou `pendências=nenhuma`. **NOT_VERIFIED.** |
| Resultado funcional | 8/8 métodos independentes, 13 testes backend, 83 testes documentais, context-check e diff-check aprovados; alteração limitada ao módulo de mídia e seu teste. **VERIFIED para a correção.** |

O checkpoint de opcionais produziu a evidência pretendida. O checkpoint de revisão induziu a leitura antes do diff, mas não garantiu que o registro viesse depois do resultado; portanto permanece `IMPLEMENTED_NOT_VERIFIED`. A regressão dos required também impede promover o protocolo integral. Isso reforça que um checkpoint textual ajuda a tornar omissões observáveis, mas uma execução funcional correta não comprova aderência estável a toda a rota.

Uso acumulado informado pelo CLI: 17 tokens de entrada, 41.458 de criação de cache, 477.400 de leitura de cache e 6.601 de saída; 153,497 s externos e estimativa CLI de USD 0,492094, incluindo uso auxiliar Haiku. Esses valores não comprovam cobrança nem economia de contexto. Os 33 originais históricos permaneceram idênticos ao inventário; a proposta funcional continua somente na cópia externa. [Análise estruturada](/home/davis/backups/analise-video/context-claude-checkpoints-20260917T084852Z/final-analysis.json), stream, patches, resultados e SHA-256 estão preservados no diretório do ensaio.
