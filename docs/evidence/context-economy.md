# Economia de contexto — comparação controlada no Claude

A repetição no Codex foi concluída e está no [relatório próprio](./context-economy-codex.md). Este documento preserva a medição Claude.

Em 2026-09-17, o recorte técnico reduziu a média de entrada de **35.291 para 14.189 tokens (59,79%)** no Claude Sonnet 4.6. Houve três repetições por condição; 2/3 soluções amplas e 3/3 soluções técnicas passaram nos mesmos testes. Este resultado verifica uma seleção de contexto para uma correção técnica delimitada.

O “antes” é um **controle reconstruído de leitura ampla**, não uma medição retroativa das sessões históricas. O experimento compara contexto fornecido em uma resposta, não todo o funcionamento autônomo da arquitetura de Codex e Claude.

## Protocolo

- Mesma tarefa: corrigir a seleção de um heading Markdown com hashes opcionais de fechamento, preservando o trecho original, títulos literais como `C#`, duplicatas normalizadas, subseções e fences.
- Mesmo código anterior à correção e mesmos documentos técnicos, no snapshot Git `baf01f6df8e1b480f306ab4d0bd6ce2e3256ef81`. Cada execução recebeu um checkout isolado da revisão.
- Claude Code `2.1.179`, modelo explícito `claude-sonnet-4-6`, esforço `medium` e o mesmo system prompt.
- Seis sessões novas e independentes, sem histórico persistido. Ordem previamente fixada: amplo/técnico, técnico/amplo, amplo/técnico (AB/BA/AB).
- Documentos fornecidos integralmente no prompt. Uma resposta JSON por sessão, contendo substituição exata de código, teste e revisão estática; o avaliador aplicou e testou cada proposta posteriormente.
- Ferramentas desativadas, MCP vazio e estrito, settings locais desativados e safe-mode. Os eventos init confirmaram o mesmo modelo, `tools=[]` e `mcp_servers=[]`; nenhuma chamada de ferramenta ocorreu.
- `DISABLE_PROMPT_CACHING=1` em ambos os lados. Todas as seis respostas registraram **zero tokens de criação e de leitura de cache**. A variável é documentada na [configuração oficial do Claude Code](https://code.claude.com/docs/en/model-config#prompt-caching-configuration).
- Autenticação existente; chaves de API Anthropic/OpenAI/Codex removidas do ambiente dos subprocessos. Nenhuma API paga adicional foi exigida.

O protocolo, hashes das fontes, prompts e ordem das sessões foram salvos antes da primeira inferência. Não houve novas inferências para corrigir respostas nem seleção posterior dos melhores resultados.

## Contexto fornecido

| Medida | Antes: controle amplo | Depois: recorte técnico | Redução |
| --- | ---: | ---: | ---: |
| Arquivos | 25 | 13 | 48,00% |
| Bytes UTF-8 das fontes | 106.116 | 40.655 | 61,69% |
| Bytes com delimitadores do contexto | 107.467 | 41.333 | 61,54% |
| Bytes do prompt completo | 109.081 | 42.947 | 60,63% |

Bytes e tokens são medidas distintas. `input_tokens` mede a entrada da inferência, incluindo texto fornecido e a parte fixa do CLI; não é um contador exclusivo dos arquivos. Como a tarefa e configuração são mantidas, a diferença observada permite medir o efeito deste recorte.

Ambas as condições receberam os mesmos 13 arquivos técnicos, incluindo os required de `context_maintenance`, PACKS pelo gatilho do gerador, o manifesto pertinente e as três skills:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/context/README.md`
- `docs/context/CONTEXT_POLICY.md`
- `docs/context/ROUTES.yaml`
- `docs/context/PACKS.yaml`
- `skills/feature-workflow/SKILL.md`
- `skills/build-and-test/SKILL.md`
- `skills/code-review/SKILL.md`
- `scripts/docs/requirements.txt`
- `Makefile`
- `scripts/docs/build_context_pack.py`
- `tests/docs/test_context.py`

O controle amplo acrescentou os mesmos 12 documentos operacionais completos em suas três repetições:

- `docs/SYSTEM_SPEC.md`
- `docs/GAME_MODEL.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/TRACEABILITY.md`
- `docs/governance/DECISIONS.yaml`
- `docs/SSOT.md`
- `docs/governance/AUTHORITY.md`
- `docs/architecture/ADR-001.md`
- `docs/architecture/ADR-002-ssot-and-context.md`
- `docs/governance/SOURCES.yaml`
- `docs/governance/DOCUMENTATION_STANDARD.md`

Nenhuma condição recebeu arquivos de `archive/`, `.local/drafts/`, dependências ou caches. A inclusão dos documentos adicionais serve ao controle; não os declara irrelevantes para tarefas de produto ou auditoria.

## Resultados observados

Tokens e estimativa de custo são os campos finais do CLI; duração é tempo de parede medido pelo executor, incluindo inicialização e espera. Os testes posteriores não entram nessa duração.

| Execução | Condição | Par | Entrada | Saída | Duração (s) | Estimativa CLI (US$) | Correção |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| run01 | antes — amplo | 1 | 35.291 | 6.731 | 95.633 | 0.241456 | PASS |
| run02 | depois — técnico | 1 | 14.189 | 6.075 | 91.690 | 0.147213 | PASS |
| run03 | depois — técnico | 2 | 14.189 | 4.694 | 77.550 | 0.126483 | PASS |
| run04 | antes — amplo | 2 | 35.291 | 8.894 | 139.820 | 0.273891 | FAIL |
| run05 | antes — amplo | 3 | 35.291 | 8.298 | 115.635 | 0.264971 | PASS |
| run06 | depois — técnico | 3 | 14.189 | 5.650 | 77.407 | 0.140813 | PASS |

| Média por condição | Antes | Depois | Redução da média |
| --- | ---: | ---: | ---: |
| Tokens de entrada | 35.291  | 14.189  | 59,79% |
| Tokens de saída | 7.974  | 5.473  | 31,37% |
| Tokens totais da resposta | 43.265  | 19.662  | 54,55% |
| Duração de uma sessão | 117.029 s | 82.216 s | 29,75% |
| Estimativa CLI | 0.260106 US$ | 0.138170 US$ | 46,88% |

| Par | Tokens de entrada poupados | Redução |
| --- | ---: | ---: |
| 1 | 21.102 | 59,79% |
| 2 | 21.102 | 59,79% |
| 3 | 21.102 | 59,79% |

A redução de entrada é a medida principal de economia de contexto. Saída e duração também dependem da geração e da infraestrutura; diferenças destas seis execuções são descritivas. A estimativa em dólares não é fatura da assinatura nem medição de quota. Não foi demonstrado ganho geral de latência, qualidade superior ou economia faturada.

## Correção, testes e revisão

O código da base falhou como esperado nos testes independentes (oito métodos, uma falha e seis erros de subcasos). A falha comprova que as sessões receberam o defeito, embora o gerador ainda conseguisse produzir o pacote com os títulos comuns existentes.

Cada resposta foi aplicada exatamente uma vez por um adaptador comum: remoção uniforme de fence JSON, se presente, e normalização da indentação do método de teste. A substituição deveria ocorrer uma única vez e a AST deveria permanecer igual fora de `section()`. Respostas foram preservadas sem reparo adicional.

Todas as seis propostas foram submetidas às mesmas verificações:

1. `make context` na cópia isolada;
2. oito testes independentes preexistentes, ocultos das sessões;
3. `make context-check`;
4. 81 testes documentais, incluindo o método de regressão proposto;
5. `git diff --check`.

Os oito testes independentes cobrem fechamento opcional, hashes literais e combinação com `C#`, tabs/Unicode, duplicatas, subseções/fronteiras, fences de ambos os tipos e títulos comuns/ausentes. Houve revisão estática fornecida por cada sessão e inspeção dos patches pelo executor.

**Falha preservada: run04, controle amplo.** A normalização `re.sub(r" +#+$", "", ...)` aceita espaços, mas não tab antes dos hashes de fechamento. O caso `## Ação\t### ` continuou lançando ValueError. Os 81 testes documentais passaram; o teste independente de tab/Unicode detectou a lacuna. A proposta não foi reparada ou repetida e permanece como FAIL.

A resolução foi aprovada em 2/3 execuções amplas e 3/3 técnicas. Esta amostra não demonstra superioridade geral de qualidade; o contrato testado também não valida conformidade completa com CommonMark.

As mudanças ficaram restritas ao gerador, teste e hash do pacote em cada cópia. As propostas do benchmark **não substituíram** a correção já integrada no workspace principal.

## Evidências reproduzíveis

- [Registro estruturado](./context-economy.json): protocolo, sessões, contadores brutos, checks, hashes, médias, pares e limites.
- [Artefatos externos](/home/davis/backups/analise-video/context-economy-20260917T044514Z): `setup.json`, prompts, runner, avaliador, testes independentes, seis logs JSONL, seis propostas, seis patches e logs de cada check.
- [Manifesto SHA-256](/home/davis/backups/analise-video/context-economy-20260917T044514Z/SHA256SUMS): integridade dos artefatos diretos. Os checkouts têm revisão de base e patches identificados, não entram como dependências do contexto operacional.
- [Ensaio anterior com ferramentas](./context-session-evaluation.md): validação separada de leituras, alterações, testes e revisão nos dois agentes. Seus contadores não foram utilizados como baseline desta comparação.

Para recalcular os resultados a partir das seis avaliações já salvas:

```bash
python3 /home/davis/backups/analise-video/context-economy-20260917T044514Z/analyze_results.py
```

A inspeção dos eventos pode confirmar ausência de cache e ferramentas. `context_sources` é apenas a declaração da sessão sobre os textos considerados; não é um log de Read. Este ensaio não confirma a ordem das leituras acionadas pela rota.

## Estado e limites

- **VERIFIED:** redução de entrada neste controle reconstruído, no Claude, para esta tarefa, com três pares e correções aprovadas nos mesmos checks.
- **Não verificado neste ensaio Claude:** consumo de todo o fluxo autônomo, tarefas de produto, desempenho em outras rotas, startup histórico e comportamento com cache ativo.
- **Não generalizar:** três repetições de uma única tarefa não estabelecem percentual universal, suficiência para todo o produto, superioridade de qualidade ou significância estatística de latência.
- Estados A16/CTX-10 recebem crédito apenas para este recorte. INC-002, grafos, hooks, compactação automática, memória e traces conservam seus estados próprios.

## Continuação no Codex — 2026-09-17

Codex: redução de 53,72% na entrada total, 3/3 propostas técnicas e 3/3 amplas aprovadas nos mesmos checks; zero tokens lidos de cache em todas as execuções, criação de cache não exposta. Os mesmos prompts e código-base foram reutilizados; consulte o [relatório](./context-economy-codex.md) e o [JSON](./context-economy-codex.json). Cada percentual compara os dois grupos dentro de seu agente, sem ranking entre modelos.

Próxima ação: avaliar uma segunda tarefa representativa de outra rota com critérios/testes fixos, antes de generalizar suficiência ou medir todo o fluxo com ferramentas.
