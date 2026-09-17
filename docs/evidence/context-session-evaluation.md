# Ensaio de contexto em sessões novas — 2026-09-17

Continuação em outra rota: [segunda tarefa e fluxo autônomo](./context-second-route.md). As propostas de backend passaram no contrato externo, mas a sessão Claude com entrada válida omitiu fontes, manifesto e skills. Essa nova evidência não anula a conformidade delimitada da segunda repetição técnica abaixo; mostra que ela não se generalizou para manutenção do backend.

Os dois agentes corrigiram o mesmo defeito do seletor Markdown, executaram testes e revisaram suas alterações em sessões novas. Ambos passaram em oito testes independentes. Os três procedimentos compartilhados foram lidos e exercitados nessa tarefa técnica. O cumprimento completo das leituras e a economia de contexto continuam parcialmente não verificados.

A repetição descrita ao final fechou as omissões de PACKS/manifesto na tarefa avaliada: a primeira tentativa de esclarecimento ainda omitiu PACKS; a segunda confirmou as leituras antes das ações dependentes. As tabelas iniciais abaixo preservam o resultado do primeiro ensaio.

## Preparação e revisão comum

Foram conferidos [AGENTS.md](../../AGENTS.md), [CLAUDE.md](../../CLAUDE.md), [guia](../context/README.md) e as três skills. CLAUDE continua contendo somente `@AGENTS.md`.

Correções anteriores aos testes dos agentes:

- referência `SSOT.md` corrigida para `docs/SSOT.md` na entrada;
- rota `context_maintenance` adicionada em [ROUTES.yaml](../context/ROUTES.yaml), com guia e política obrigatórios e opcionais por gatilho;
- implementação técnica separada da execução de um incremento nas instruções; reprodução do defeito, testes pertinentes e leitura da skill de revisão explicitados;
- guia esclarece regeneração após mudança de fontes/referências; procedimentos usam manifestos pertinentes e distinguem resultados observados de expectativas;
- a asserção de não incorporar o conteúdo da skill no pacote foi atualizada para seu título atual.

A preparação passou em `make context-check`, nos **80 testes documentais** e no `quick_validate.py` das três skills. O pacote foi regenerado pelas fontes.

A revisão comum é o snapshot temporário `598800a94f7638aa78b1a7db910de2686d70abb1`, criado fora do repositório a partir de **102 arquivos operacionais**, incluindo as alterações locais existentes. Seu HEAD de origem era `571ce15ebefe83684f963e31981b99c13e1277ad`; portanto, os testes não usaram apenas o último commit do projeto. O manifesto tem SHA-256 `24ab3ace5544c19f01d149ea80b99e362937d871124d53ea17b0cee28c292394`.

Os checkouts `codex/` e `claude/` foram clonados desse snapshot, com o mesmo prompt, sem reutilização de conversa, `resume` ou `continue`. Histórico, archive, dependências e caches não foram copiados. Nenhum commit foi criado no repositório original. Autenticações existentes foram usadas, sem passar `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` ou `CODEX_API_KEY` aos processos e sem configurar APIs adicionais.

Codex executou com `workspace-write` e aprovação `never`; Claude com `dontAsk` e permissões para as seis ferramentas locais Read/Edit/Write/Glob/Grep/Bash. Isso isola checkouts e conversas; não constitui isolamento completo do sistema operacional. Configurações globais dos CLIs permaneceram presentes e não foram alteradas. As interfaces usadas são documentadas em [Codex não interativo](https://learn.chatgpt.com/docs/non-interactive-mode), [entrada AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) e [Claude programático](https://code.claude.com/docs/en/headless).

## Tarefa e resultados

Antes, `section("## Alvo ###\n\nConteúdo.\n\n## Seguinte\n\nOutro.\n", "Alvo")` levantava `ValueError`. Depois, retorna `## Alvo ###` e o conteúdo correspondente, preservando o título original. Hashes opcionais são removidos apenas da representação usada na comparação. Offsets, fronteiras, fences e o tratamento existente de whitespace no final do trecho permanecem preservados.

| Item | Codex | Claude |
| --- | --- | --- |
| CLI | 0.144.5 | 2.1.179, binário da extensão; fora do PATH |
| Modelo observado | gpt-5.6-sol | claude-sonnet-4-6 |
| Sessão | `01a0ad7b-3efa-7351-83b5-d33b7ba6e4af` | `3ffb6c57-190f-4445-8a2e-49fbd77f7c01` |
| Saída do processo | 0 | 0 |
| Testes documentais | 83 aprovados | 81 aprovados |
| Testes independentes | 8/8 aprovados | 8/8 aprovados |
| Conferência de contexto | rotas e pacote válidos | rotas e pacote válidos |
| Revisão pelo agente | sem achados relatados; diff e whitespace conferidos | sem achados relatados; diff conferido |
| Revisão independente | sem achados bloqueadores de correção | sem achados bloqueadores de correção |
| Arquivos alterados | gerador, teste de contexto e pacote | gerador, teste de contexto e pacote |

Os agentes reproduziram o defeito antes da correção. Codex também executou seus três testes novos antes da implementação, com falha. Claude reproduziu a chamada e executou a suíte original antes; acrescentou um método com vários cenários após a implementação.

Os oito testes externos foram preparados sem entregar suas implementações aos agentes. Na base, seis casos deram erro e um falhou. Após cada solução, passaram: título com fechamento e preservação exata do trecho, hashes literais, `C#` seguido de fechamento, tab/Unicode, colisão entre títulos normalizados, subseções/fronteiras, fences com backticks e tildes, título simples e ausência. Oito métodos podem conter vários casos.

A revisão independente também executou `make context-check`, `make test-docs` e `git diff --check` em cada resultado, conferindo escopo e ausência de arquivos novos não ignorados. Não houve mudanças além dos três arquivos permitidos nos checkouts.

## Contexto efetivamente consultado

Os dois agentes relataram AGENTS como entrada. Não houve abertura explícita de AGENTS/CLAUDE pelas ferramentas nesta tarefa; essa entrada é disponibilizada pelo mecanismo nativo, já observado no ensaio anterior. As leituras abaixo estão nos comandos e eventos, e não apenas no resumo dos agentes.

| Arquivos | Codex | Claude |
| --- | --- | --- |
| `docs/context/ROUTES.yaml` | leitura por shell | Read |
| `docs/context/README.md` e `CONTEXT_POLICY.md` | leitura por shell | Read |
| `skills/feature-workflow/SKILL.md` | leitura e implementação | Read e implementação |
| `skills/build-and-test/SKILL.md` | leitura e verificações | Read e verificações |
| `skills/code-review/SKILL.md` | leitura e revisão | Read e revisão |
| gerador e `tests/docs/test_context.py` | leitura por shell | Read |
| `docs/context/PACKS.yaml` | lido pelo gatilho de geração/integridade | não aberto explicitamente |
| `scripts/docs/requirements.txt` e `Makefile` | lidos | não abertos explicitamente |
| pacote gerado | trechos/diff conferidos | diff conferido |

Nenhum documento de produto foi aberto explicitamente pelos agentes. As ferramentas de geração/teste podem ler suas fontes como dados; isso não equivale a incorporar esses documentos na conversa. Claude cumpriu os required desta rota e os três procedimentos, mas omitiu a leitura opcional acionada e a consulta ao manifesto pertinente. O resultado correto não transforma essa omissão em conformidade integral. Não foi avaliada descoberta nativa das skills; o piloto continua usando caminhos explícitos.

## Consumo disponível

| Medida informada | Codex | Claude |
| --- | --- | --- |
| Tempo externo, incluindo inicialização/testes | 270,207 s | 199,981 s |
| Entrada total informada | 825.358 tokens | categorias abaixo; não é somente `input_tokens` |
| Entrada em cache | 767.488 tokens, contidos na entrada total | 713.295 tokens de leitura de cache |
| Criação de cache | campo não fornecido | 64.040 tokens |
| Entrada fora de cache | diferença: 57.870 tokens | `input_tokens`: 15 tokens, além da criação de cache |
| Saída | 10.197 tokens | 10.263 tokens |
| Raciocínio informado separadamente | 5.163 tokens | campo equivalente não fornecido |
| USD | campo não fornecido | `total_cost_usd`: 0,7522185; estimativa do CLI |
| Quota restante/cobrança da assinatura | não observadas | não observadas |

Os campos originais estão no [registro JSON](./context-session-evaluation.json). Esses valores acumulam requisições ao longo da sessão e releituras em cache; não representam utilização simultânea da janela nem permitem inferir porcentagem para compactação. A estimativa em USD não comprova cobrança adicional da assinatura. Um ensaio por agente, com modelos/configurações/cache distintos, não demonstra que um agente é mais econômico ou rápido, nem mede ganho antes/depois da arquitetura. Ferramentas/plugins globais participaram do contexto disponível; instruções mínimas do repositório não garantem contexto global mínimo.

## Integração e preservação

Foi integrada a solução do Codex em [build_context_pack.py](../../scripts/docs/build_context_pack.py) e [test_context.py](../../tests/docs/test_context.py): normalização restrita a espaços/tabs e três métodos de regressão, com igualdade exata do trecho e duplicidade entre título simples e fechado. A solução do Claude também passou no contrato independente, mas seu teste agrupado é menos específico. O pacote é regenerado das fontes finais do repositório, incluindo esta atualização de estado. A conferência final do repositório passou nos **83 testes documentais**, nos **oito testes independentes**, em `make context-check`, `git diff --check` e na validação das três skills.

Até a integração, hashes dos **102 arquivos** e o estado do Git original permaneceram iguais aos da preparação. Os **33 originais históricos** conferem com o inventário e continuam restaurados; nenhuma limpeza foi realizada. Alterações preexistentes do usuário permanecem preservadas.

Logs, prompt, snapshot, patches, scripts reexecutáveis e verificações ficam em [context-evaluation-20260917T034833Z](/home/davis/backups/analise-video/context-evaluation-20260917T034833Z). A relação de hashes está em [SHA256SUMS](/home/davis/backups/analise-video/context-evaluation-20260917T034833Z/SHA256SUMS). Não se trata de baseline canônico. Para repetir a verificação independente de um resultado preservado:

```bash
python3 /home/davis/backups/analise-video/context-evaluation-20260917T034833Z/verify_candidate.py codex
python3 /home/davis/backups/analise-video/context-evaluation-20260917T034833Z/verify_candidate.py claude
```

Uma repetição atualiza os logs de verificação e exige renovar seus hashes; streams e patches originais devem permanecer preservados.

## Pendências delimitadas

A01 e A16 possuem evidência funcional para esta correção. A04 permanece parcial para o cumprimento completo de leituras. A05, A06, hooks/Lore, grafos, MCP, Phoenix, descoberta nativa e incrementos de produto não foram validados por este ensaio.

Mem0 retornou `Memory search failed` nas consultas do Codex; no Claude as buscas foram negadas pela lista de permissões locais do teste. O escopo inferido pelos plugins foi o projeto temporário do clone, não `analise-video`. Essas observações não comprovam memória compartilhada entre agentes nem falha de serviço do Claude. No agente supervisor, buscas também falharam e a ferramenta `add_memory` não está exposta; não se declara gravação manual realizada. Phoenix não recebeu verificação de traces por sessão. Avisos de cache de modelos/flag de hooks do Codex permaneceram visíveis nos logs.

A próxima validação deve focalizar o cumprimento dos gatilhos e a consulta ao manifesto no Claude. Uma avaliação de economia requer controle das configurações globais, uma comparação antes/depois e repetições, sem instalar mecanismos históricos adicionais apenas para este ensaio.

## Repetição do Claude após esclarecer as skills

Foram ajustadas [feature-workflow](../../skills/feature-workflow/SKILL.md) e [build-and-test](../../skills/build-and-test/SKILL.md): quando `when` ocorre, o opcional deve ser consultado antes da ação dependente; o manifesto pertinente deve ser aberto antes de escolher/executar verificações. Uma referência no guia ou leitura automática pelo gerador não substitui a consulta pelo agente.

Na primeira tentativa, essas instruções permaneceram no parágrafo inicial da skill de implementação. Claude abriu o manifesto antes dos testes e concluiu a correção, mas não abriu PACKS. O resultado foi preservado como falha do requisito de leitura. A orientação de PACKS foi então separada em parágrafo próprio, explicitando que correções na extração de seções também afetam o comportamento do gerador.

As duas sessões receberam o **mesmo prompt original**, SHA-256 `3e2b676fc90686ab11abda1a81eccb6672416083aded3b745ff659b94aa64fb7`, sem incluir lembrete dos nomes dos documentos omitidos no prompt. Partiram do código/testes do snapshot anterior à correção, com as duas skills ajustadas e os hashes do pacote regenerados. Não receberam a solução já integrada ao repositório. O diff de preparação de cada snapshot contém somente essas duas skills e o pacote.

| Item | Primeira repetição | Segunda repetição |
| --- | --- | --- |
| Modelo / CLI | Sonnet 4.6 / 2.1.179 | Sonnet 4.6 / 2.1.179 |
| Sessão nova | `d01d6eb7-e58f-4bf3-9f85-f29adb37edd0` | `0d736dd8-9150-4774-8ede-beb04167a3c3` |
| Snapshot de partida | `f4475dfd9dea236caef33afb1ed4c42c0cc6e0ac` | `baf01f6df8e1b480f306ab4d0bd6ce2e3256ef81` |
| PACKS antes de editar | não consultado | consulta concluída com sucesso |
| requirements antes dos testes | consulta concluída com sucesso | consulta concluída com sucesso |
| Required / três skills | lidos | lidos |
| Testes documentais | 81 aprovados | 81 aprovados |
| Testes independentes | 8/8 aprovados | 8/8 aprovados |
| Processo / contexto / whitespace | código 0 / válido / válido | código 0 / válido / válido |
| Duração externa | 199.529 s | 247.63 s |

A primeira base passou nos 80 testes existentes e continuou falhando no contrato externo do defeito. Os bytes do gerador/testes da segunda base são idênticos aos da base original; sua integridade de contexto também foi conferida. Ambas as sessões reproduziram o defeito antes da alteração, implementaram correção e regressão e revisaram o diff. A revisão independente conferiu os patches e executou os oito testes externos, a suíte documental, a integridade e whitespace; não encontrou falha bloqueadora de correção. Somente gerador, teste de contexto e pacote foram alterados pelos agentes.

Na segunda sessão, os eventos de consulta comprovam:

- PACKS: Read no evento 155, resultado sem erro no evento 157, anterior à primeira edição;
- requirements: Read no evento 159, resultado sem erro no evento 161, anterior à primeira execução de testes;
- leitura com sucesso das três skills e dos required de `context_maintenance`.

Os índices de evento são baseados em zero, por linha do stream JSON. O [JSON de análise](/home/davis/backups/analise-video/context-claude-retest-20260917T042230Z/claude-analysis.json) registra IDs das ferramentas, resultados e a comparação de ordem. Isso verifica a consulta efetiva, em vez de apenas a alegação na resposta final.

| Consumo acumulado informado pelo CLI | Primeira repetição | Segunda repetição |
| --- | --- | --- |
| `input_tokens` | 13 | 15 |
| Criação de cache | 32702 | 34318 |
| Leitura de cache | 657686 | 799591 |
| Saída | 11639 | 12641 |
| `total_cost_usd`, estimativa | 0.5681418 | 0.6354453 |

As ressalvas de consumo do primeiro ensaio continuam aplicáveis: campos acumulados não são ocupação simultânea da janela; USD estimado não comprova cobrança adicional da assinatura; modelos/configurações/caches e variabilidade de sessões não permitem declarar economia ou efeito universal da redação. As permissões/auth foram mantidas e não foram configuradas APIs adicionais. As buscas Mem0 continuaram recusadas pela lista local do ensaio; Phoenix e memória não foram validados.

Artefatos completos: [primeira repetição](/home/davis/backups/analise-video/context-claude-retest-20260917T041834Z) e [segunda repetição](/home/davis/backups/analise-video/context-claude-retest-20260917T042230Z), com prompt, snapshots, patches, streams, scripts de análise/verificação e SHA256SUMS em cada diretório. O [registro JSON](./context-session-evaluation.json) preserva o ensaio inicial e acrescenta `claude_followups`.

Os 104 arquivos operacionais do repositório permaneceram iguais aos da preparação da segunda sessão até a atualização dos registros. Na primeira sessão, a única mudança do coordenador nesse intervalo foi o esclarecimento adicional da skill para a segunda tentativa. A correção anterior do Codex permanece integrada no repositório; os patches das repetições ficam nos checkouts de ensaio. Os ajustes desta etapa são as duas skills, seus derivados e evidências. Os originais recuperados permanecem preservados.

A conferência final do repositório passou em `make context-check`, nos **83 testes documentais** e em `git diff --check`. Foram conferidos os 33 originais, a cobertura dos 40 grupos/16 critérios e os links locais; o pacote regenerado tem 33.887 bytes.

**Resultado de aceitação:** leitura de PACKS e manifesto, correção, testes e revisão **VERIFIED para a segunda repetição desta tarefa**. A01/A04/A16 recebem somente esse crédito delimitado; conformidade geral, casos negativos de parada, demais rotas, eficiência, hooks/grafos/MCP e incrementos de produto continuam com suas pendências anteriores.

**Próxima ação:** definir uma comparação de contexto antes/depois, com configurações globais/modelo controlados, critérios de correção iguais e repetições, para medir economia sem deduzi-la deste ensaio único.
