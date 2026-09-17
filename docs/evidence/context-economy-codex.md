# Economia de contexto no Codex — comparação controlada

Em 2026-09-17, a entrada média caiu de **30.612 para 14.166 tokens (53,72%)** com o recorte técnico. Foram três pares no Codex, mantendo tarefa, revisão, prompts e configuração dentro do agente. Passaram em todos os checks 3/3 propostas amplas e 3/3 técnicas.

O “antes” continua sendo um controle amplo reconstruído. A medição cobre uma resposta com contexto fornecido; não mede startup histórico, recuperação autônoma de arquivos nem todo o fluxo da arquitetura.

## Protocolo preservado

- Mesmo defeito e contrato do [ensaio Claude](./context-economy.md): seleção de headings Markdown com hashes opcionais de fechamento, preservação do trecho, `C#`, duplicatas, fronteiras/subseções e fences.
- Mesmo snapshot anterior à correção: `baf01f6df8e1b480f306ab4d0bd6ce2e3256ef81`. Cada sessão partiu de uma cópia isolada e limpa.
- Mesmos prompts e hashes do Claude: 25 arquivos no controle amplo e os mesmos 13 técnicos no recorte. Não foram usados docs, código ou skills posteriores ao snapshot.
- Codex CLI `0.144.5`, modelo explicitamente configurado `gpt-5.6-sol`, esforço `medium` e instruções de modelo fixas. O catálogo distribuído com o CLI confirma suporte ao esforço; os comandos, diagnóstico e logs de modelo estão preservados. `codex exec --json` não expõe metadados do modelo da resposta do provedor.
- Três pares novos, ordem AB/BA/AB. Um turno por sessão, sem persistência: `--ephemeral`, `--ignore-user-config`, `--ignore-rules`, configuração estrita e sandbox de leitura.
- Autoload de AGENTS desativado com `project_doc_max_bytes=0`; AGENTS e as três skills já estão no prompt. Skills globais desativadas por overrides. Shell, apps, plugins, hooks, browser, multi-agent e dependências de workspace desativados; MCP vazio. A validade exige **zero chamadas de ferramenta e um turno**, confirmados nos seis logs.
- Autenticação existente forçada para ChatGPT; chaves Anthropic/OpenAI/Codex e identificadores herdados de sessão removidos somente do ambiente dos subprocessos. Configuração global e ambiente do processo principal preservados.
- Mesma adaptação determinística e mesmos checks do Claude: trecho exato único, AST inalterada fora de `section()`, um método de teste, normalização uniforme de fence JSON/indentação. Nenhuma resposta reparada ou repetida por inferência.

O protocolo foi salvo antes da primeira inferência. As [configurações oficiais do Codex](https://learn.chatgpt.com/docs/config-file/config-reference) documentam instruções de modelo, limite do AGENTS, controles de skills e ferramentas; os flags usados foram também conferidos no CLI instalado.

O stderr preserva os diagnósticos do CLI, incluindo erro inicial de leitura do cache de catálogo de modelos e fallback de personalidade para instruções base. O cache de catálogo é separado do cache de prompt. Os flags e instruções de modelo permaneceram iguais, e as execuções encerraram com código zero; os contadores de prompt constam abaixo.

## Cache e consumo

Não foi encontrado um controle confirmado para desativar cache de prompt neste CLI. O mesmo comportamento automático foi mantido em ambos os grupos. Todas as seis execuções informaram **zero tokens lidos do cache**. **Criação de cache não é exposta pelo JSON do CLI** e não foi presumida como zero.

A medida principal é `usage.input_tokens`, que inclui a parcela `cached_input_tokens`. A parcela sem leitura de cache é calculada como total menos cached. Não somamos cache ao total novamente. O protocolo registra ambos os contadores para evitar confundir um hit com redução da quantidade de contexto. A [documentação oficial de prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) diferencia total de entrada e tokens em cache.

`reasoning_output_tokens` é preservado no JSON como detalhe de saída; não é somado novamente a `output_tokens`. Não há estimativa financeira no JSON do CLI: faturamento da assinatura e quota **não medidos**.

## Resultados observados

| Execução | Contexto | Par | Entrada total | Entrada de cache | Saída | Duração (s) | Correção |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| run01 | amplo | 1 | 30.612 | 0 | 2.100 | 49,547 | PASS |
| run02 | técnico | 1 | 14.166 | 0 | 2.315 | 67,554 | PASS |
| run03 | técnico | 2 | 14.166 | 0 | 3.032 | 85,054 | PASS |
| run04 | amplo | 2 | 30.612 | 0 | 2.068 | 40,820 | PASS |
| run05 | amplo | 3 | 30.612 | 0 | 2.562 | 74,788 | PASS |
| run06 | técnico | 3 | 14.166 | 0 | 2.708 | 57,428 | PASS |

| Média por condição | Controle amplo | Recorte técnico | Variação da média |
| --- | ---: | ---: | ---: |
| Entrada total | 30.612 | 14.166 | queda de 53,72% |
| Entrada lida de cache | 0 | 0 | não aplicável |
| Entrada sem leitura de cache | 30.612 | 14.166 | queda de 53,72% |
| Saída | 2.243 | 2.685 | aumento de 19,69% |
| Entrada + saída | 32.855 | 16.851 | queda de 48,71% |
| Duração (s) | 55,05 | 70,01 | aumento de 27,18% |

A economia principal é **53,72% de entrada total**. Os três pares e suas diferenças individuais estão no JSON. Duração inclui inicialização do CLI e espera da inferência, sem os testes posteriores. Diferenças de saída/duração são descritivas, com três repetições de uma tarefa; não estabelecem ganho geral de latência ou superioridade de qualidade.

A duração média passou de **55,05 para 70,01 segundos**: não houve ganho observado de latência nesta amostra. A saída também aumentou, enquanto entrada + saída caiu 48,71%. Isso não converte contadores em faturamento de assinatura.

Os prompts reutilizados têm 109.081 e 42.947 bytes UTF-8, respectivamente. As fontes têm 106.116 e 40.655 bytes, redução de 61,69%; bytes não são tokens. Os required da rota, PACKS acionado pelo gerador, manifesto e skills técnicas permanecem nos dois grupos.

## Correção e revisão

A base apresentou a falha esperada nos oito testes independentes. Todas as propostas foram submetidas a:

1. `make context`;
2. os mesmos oito testes independentes, ocultos das sessões de ambos os agentes;
3. `make context-check`;
4. `make test-docs`, com 81 testes por proposta válida;
5. `git diff --check`.

Nenhuma proposta falhou nos checks definidos.

As revisões estáticas fornecidas pelas sessões, patches e resultados dos checks foram preservados. A inspeção do executor consta em `parent-review.json`; a comparação de AST restringe as alterações ao seletor. O contrato avaliado não comprova conformidade completa com CommonMark.

As soluções do benchmark ficaram nas cópias externas; não substituíram a correção operacional já existente. A auditoria confere o workspace principal e os 33 originais autorais contra hashes anteriores à execução. Estados de incrementos de produto e demais mecanismos de contexto permanecem independentes dessa medição.

## Evidências e reprodução

- [JSON do Codex](./context-economy-codex.json): protocolo, prompts/fontes por SHA-256, configurações, sessões, uso bruto, avaliações, médias, pares e limites.
- [Artefatos externos](/home/davis/backups/analise-video/context-economy-codex-20260917T050454Z): snapshot, seis cópias, prompts, runner, avaliador, oito testes independentes, logs JSONL/stderr, respostas, patches e checks.
- [SHA256SUMS](/home/davis/backups/analise-video/context-economy-codex-20260917T050454Z/SHA256SUMS): hashes dos arquivos diretos; snapshot Git e patches identificam as cópias.
- [Medição Claude](./context-economy.md): evidência anterior preservada separadamente.
- [Sessões com ferramentas](./context-session-evaluation.md): leitura de documentos, implementação, testes e revisão observados anteriormente; não usados como baseline de consumo.

Recalcular, sem novas inferências:

```bash
python3 /home/davis/backups/analise-video/context-economy-codex-20260917T050454Z/analyze_results.py
```

Os seis identificadores de sessão e contadores finais permitem conferir um turno, nenhuma ferramenta e o cache informado. `context_sources` é declaração sobre os textos fornecidos, não um log de leituras nem prova de ordem dos gatilhos da rota.

## Alcance da conclusão

A16/CTX-10 recebem crédito **VERIFIED para redução de entrada neste controle Codex**. Claude e Codex têm modelos, tokenizadores e wrappers diferentes; seus percentuais não formam ranking nem comparação de custos entre agentes. Não foi demonstrada eficiência geral da arquitetura, execução completa de incremento, memória, traces, compactação, hooks ou grafos.

Próxima ação: escolher uma segunda tarefa representativa de outra rota, com critérios e testes fixos, para verificar se o contexto selecionado continua suficiente. Só depois ampliar a medição para o fluxo com ferramentas, separando tamanho inicial, consumo agregado e efeitos de cache.
