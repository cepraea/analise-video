# Arquitetura de contexto — implementação e auditoria

## Controle

| Campo | Valor |
| --- | --- |
| ID | `EVD-CONTEXT-001` |
| Data | 2026-09-16 |
| Escopo | contexto compartilhado de Codex e Claude; pacote piloto INC-002 |
| Automação local | `VERIFIED` pelas verificações abaixo |
| Entrada e conferência do pacote em sessões novas dos dois agentes via CLI | `VERIFIED` localmente; limites abaixo |
| Autoridade normativa | nenhuma; registro de implementação e evidência |

A implementação verificada abaixo é um piloto, não a implementação integral do desenho histórico. A [checklist de completude](./context-architecture-checklist.md) compara os pedidos do histórico completo com a implementação atual, incluindo nomenclatura, pre-commit, Lore, MCP, grafos e observabilidade.

**Situação posterior à limpeza:** por solicitação de Davi, a pasta original foi recuperada integralmente no mesmo caminho. O [registro por arquivo](./context-file-integration.md) apresenta os 33 originais, destinos atuais, diferenças e pendências; nenhum original foi novamente removido nesta etapa.

## Fontes e direção aplicada

Davi delimitou esta tarefa à arquitetura de contexto para Codex e Claude e corrigiu o histórico de referência para `.local/drafts/arquitetura/contexto/historico/historico-notebooklm.json`. Esse arquivo registra 95 mensagens. O histórico do produto CEPRAEA foi consultado inicialmente, mas não determina o escopo desta implementação.

A direção normativa vem de `GOV-001`, `DOC-001`, `GOV-005`, `GOV-NLM-001`, `INFRA-001` e [ADR-002](../architecture/ADR-002-ssot-and-context.md), com precedência para decisões posteriores no catálogo. O histórico e os protótipos são insumos não canônicos. Davi esclareceu que “Criei” e “corrigi”, nas respostas do NotebookLM, significam entrega efetiva do arquivo correspondente ou de sua revisão. Essas entregas são reconhecidas. A auditoria verifica separadamente integração, funcionamento, eficiência e autoridade das fontes, com conclusões limitadas aos bytes examinados.

O [inventário](./context-source-inventory.json) registra caminho relativo, tamanho e SHA-256 completo dos 33 arquivos de conteúdo examinados em `contexto/`. Dependências em `.venv/` e caches ficam fora desse corpus. Os bytes históricos não foram alterados nem promovidos para a SSOT; a pasta foi preservada em cópia externa antes de sua retirada do workspace, conforme a seção de consolidação abaixo. Baselines publicados permanecem intactos.

## Resultado da verificação dos protótipos

| Grupo | Resultado e tratamento |
| --- | --- |
| `AGENTS (1).md`, `AGENTS-v2.md`, `Regras-Nomes.md` | Regras genéricas de nomenclatura, tamanho e Atlan; não substituem o padrão documental aprovado. A entrada comum conserva a autoridade por responsabilidade. |
| `llms.txt`, `claudeignore`, `QUICKSTART.md`, `REVIEW.md` | Referenciam uma estrutura que não estava instalada na raiz. Índices e critérios locais foram reescritos para caminhos reais; um ignore não foi usado como garantia técnica. |
| `architecture-rules.md`, `tech-stack.md` | Misturam exemplos e alternativas, incluindo Node 20, TypeScript 5, ORMs e linters ausentes dos manifestos reais. Os índices novos apontam para ADR e manifestos, sem duplicar versões. |
| Oito arquivos `*SKILL.md` | Variantes e procedimentos ligados ao protótipo. Três procedimentos compartilhados foram escritos com os comandos e limites do projeto atual. |
| `map_repo_ast.py`, `visualize_graph.py`, `generate_pdf_report.py` | Sintaxe Python válida. O extrator JS/TS usa regex, e não AST dessas linguagens; materializar símbolos externos não comprova resolução das dependências internas. Não foram instalados como dependências operacionais. |
| JSON, PNGs e PDF | Saídas não formam uma revisão coerente. O JSON salvo declara `repository: scratch`, três arquivos do protótipo, 20 nós e 261 arestas; 244 arestas têm pelo menos um extremo ausente. O PDF apresenta outra execução: 18 arquivos, 431 nós e 701 arestas. |
| `Makefile`, `package.json`, `requirements.txt` | Dependências gráficas declaradas, mas execução pressupõe o diretório dos scripts. O npm mapeia `.`; o alvo PDF chama `generate_pdf_sources.py`, ausente da pasta. `.PHONY: test` não fornece uma receita de teste. |
| `pre-commit-review.js`, `pre-commit-review-v2.js`, `commit-msg-lore.js`, `git-lore-commit.sh` | Sintaxe Node/Bash válida. O pre-commit lê arquivos do workspace e aceita a presença do JSON no staging como sinal de atualização, sem comparar seu conteúdo. Erro de Git pode ser tratado como staging vazio. O commit-msg procura trailers em qualquer linha, sem exigir o bloco final. Não foram instalados como hooks. |
| Variantes Atlan e `test-atlan-mcp.js` | Exemplos de integração e simulação não comprovam servidor real, ferramentas disponíveis ou qualidade de metadados. Nenhuma chamada Atlan ou API paga foi efetuada. |
| `historico/historico-notebooklm.json` | Proveniência dos pedidos, propostas, entregas e auditorias; não é autoridade operacional. As mensagens 84 e 88 descrevem falhas; as respostas 85 e 89 correspondem a entregas de revisões corrigidas, conforme esclarecimento de Davi. A integração e o funcionamento dos arquivos correspondentes são verificados separadamente. |

A validação do JSON pelo próprio mapeador retornou código 1 e apontou endpoints ausentes e métricas incompatíveis com o filtro de alto nível. O PDF foi inspecionado com `pdftotext -layout` e `pdfinfo`: duas páginas, com métricas diferentes das do JSON ao lado. A sintaxe dos scripts foi conferida sem executar hooks, chamadas externas ou geração de saídas sobre os originais.

## Implementação entregue

- [AGENTS.md](../../AGENTS.md) indica os procedimentos sob demanda; [CLAUDE.md](../../CLAUDE.md) contém apenas `@AGENTS.md`, removendo a cópia do status antigo da ADR-001.
- Os índices auxiliares da implementação inicial foram consolidados no [guia de contexto](../context/README.md). Os critérios de revisão ficam em [skills/code-review/SKILL.md](../../skills/code-review/SKILL.md).
- [PACKS.yaml](../context/PACKS.yaml) define seletores e dependências; o [gerador](../../scripts/docs/build_context_pack.py) constrói o pacote a partir dessas entradas.
- O pacote [INC-002.md](../context/packs/INC-002.md) contém trechos atuais, linhas da rastreabilidade e decisões com seus estados originais. RF-013 e RF-030 não recebem as descrições incorretas do pacote manual anterior.
- Hashes completos abrangem fontes, referências sob demanda, registros, configuração e geradores. Referências recebem validação e hash sem ter seu conteúdo copiado.
- O [validador de rotas](../../scripts/docs/validate_routes.py) verifica política, entrada comum, obrigatórios, opcionais concretos, exclusões e travessia de caminhos. Fontes operacionais e destinos não podem atravessar links simbólicos.
- `make context`, `make context-check` e `make test-docs` oferecem execução local; o [CI](../../.github/workflows/ci.yml) passa a conferir a reprodução dos pacotes.

Na implementação inicial, o tamanho observado do pacote piloto foi 34.247 bytes, frente a 53.994 bytes dos documentos selecionados completos, incluindo o catálogo de decisões. Após a consolidação dos índices, o pacote tem 33.636 bytes. Trata-se de uma comparação de bytes com fontes específicas, não de um benchmark de tokens, latência ou qualidade dos agentes.

## Verificação reproduzível

Na raiz, com as dependências documentais instaladas:

```bash
python3 scripts/docs/build_context_pack.py INC-002
make context-check
make test-docs
```

Resultado local: geração concluída; rotas e pacote válidos; **80 testes documentais aprovados**, incluindo 16 casos de contexto. Os casos de contexto verificam geração determinística, alteração de fonte, edição manual, fontes e referências ausentes, ciclos, IDs duplicados ou desconhecidos, procedência desconhecida, preservação de decisões pendentes, trechos ausentes, cobertura da rota, exclusões, symlinks e falha antes de iniciar uma geração com várias saídas inválidas.

Os três procedimentos passaram pelo `quick_validate.py` da skill `skill-creator`. Os links dos novos índices e do manifesto do pacote foram conferidos. Os 33 hashes históricos conferem após o trabalho. `git diff --check` não identificou erros de whitespace.

## Consolidação e retirada dos rascunhos

Davi autorizou iniciar a consolidação e a limpeza após a apresentação do caminho de implementação. Foram retirados os cinco arquivos auxiliares `llms.txt`, `REVIEW.md` e os três índices em `memory/`, criados na implementação inicial. Seus caminhos úteis foram reunidos no guia de contexto; os critérios de revisão já estavam na skill compartilhada. As referências em `PACKS.yaml` foram atualizadas e o pacote foi regenerado. Nenhum desses cinco arquivos estava versionado.

A pasta `.local/drafts/arquitetura/contexto` também estava ignorada pelo Git. A cópia recuperável fica fora do repositório: [contexto-20260916T210901929548Z.tar.gz](/home/davis/backups/analise-video/contexto-20260916T210901929548Z.tar.gz), com SHA-256 `3844f0add419497eb0286b11c553365791f6be3bc5249a1e1159164afff960b6`. O arquivo comprimido tem 77.597.596 bytes e possui arquivo `.sha256` ao lado.

A cópia inclui todo o diretório, inclusive `.venv/`, caches e saídas históricas. Foram conferidos o conjunto de caminhos, os alvos dos links simbólicos e os bytes dos 6.005 arquivos regulares, totalizando 206.637.710 bytes de conteúdo; os 33 arquivos do inventário também conferem com seus hashes anteriores. A pasta original foi retirada somente após a conferência da cópia e aprovação dos testes documentais.

Não foram removidos scripts de baselines, fontes, decisões ou evidências pela simples ausência de chamadas de execução: esses arquivos têm função documental ou de auditoria. A remoção preexistente de `gemini-review.yml` continua sendo uma alteração anterior do usuário.

Após a consolidação, foram conferidos 22 links locais da entrada, guia e skills. Esta sessão de Codex leu a entrada compartilhada e utilizou o procedimento de verificações. Naquele momento, as sessões novas ainda não tinham sido observadas e o comando `claude` não era encontrado no PATH. A verificação posterior localizou o executável instalado pela extensão do VS Code e realizou os testes descritos abaixo, sem instalar ferramentas globais ou hooks.

Após a retirada da pasta original, `make context-check` continuou aprovado. Também passaram `validate_baselines.py --base-ref HEAD`, `validate_lfs.py` e a comparação do registro de decisões com sua regeneração em arquivo temporário. Os 12 links locais deste relatório, incluindo a cópia externa, foram conferidos. Os 80 testes documentais passaram após a consolidação e antes da retirada dos rascunhos.

## Recuperação posterior dos originais

Davi solicitou recuperar os originais para comparação e registrar, arquivo por arquivo, o destino e as pendências antes de qualquer nova limpeza. A pasta `.local/drafts/arquitetura/contexto/` foi restaurada do backup externo sem substituir arquivos operacionais. O hash do backup foi conferido antes da extração; os 6.005 arquivos regulares, 206.637.710 bytes e quatro links simbólicos conferem com a cópia, e os 33 arquivos de conteúdo conferem também com o inventário original.

O [registro de integração por arquivo](./context-file-integration.md) distingue adaptação parcial, consolidação da descoberta, documentos relacionados e mecanismos não integrados. Os destinos futuros são propostas explicitamente identificadas; não foram instalados hooks, alias Lore, dependências gráficas ou MCP. O backup e todos os originais recuperados permanecem preservados. A recuperação não transforma entregas históricas em implementação operacional completa.

## Sessões novas de Codex e Claude — verificação posterior

O Claude está instalado em `/home/davis/.vscode-server/extensions/anthropic.claude-code-2.1.179-linux-x64/resources/native-binary/claude`. O nome `claude` não é encontrado pelo shell atual porque esse diretório não está no PATH. A autenticação consultada sem imprimir credenciais confirmou `claude.ai`, provedor `firstParty` e assinatura `pro`. O Codex confirmou login com ChatGPT e provedor `openai`, sem URL de provedor alternativo configurada. Os processos de teste não receberam `ANTHROPIC_API_KEY` nem `OPENAI_API_KEY` do ambiente.

Foram iniciadas sessões distintas, sem `resume` ou `continue`, a partir da raiz do projeto. O prompt pediu identificar as instruções locais já recebidas, localizar o procedimento de conferência e verificar o pacote existente sem regenerar arquivos, fazer commits ou criar outros agentes.

| Agente | Versão | Sessão nova | Observação | Conferência |
| --- | --- | --- | --- | --- |
| Claude Code | 2.1.179 | `6e8533bc-b629-4d1f-adff-f1253244cfb4` | Relatou a importação `CLAUDE.md` → `AGENTS.md`, citou orientações corretas sem abrir esses arquivos por ferramenta e leu o guia de contexto. | `make context-check`: rotas e pacote válidos. |
| Codex CLI | 0.144.5 | `01a0ac15-f71e-7100-99c8-e41102c17eaf` | Identificou `AGENTS.md` e suas orientações antes de usar ferramentas; depois leu guia, rotas, seletores e documentos do incremento. | `python3 scripts/docs/build_context_pack.py INC-002 --check`: código `0`, pacote válido. |

Ambos os processos encerraram com código `0`. A conferência do Claude foi observada no resultado da ferramenta Bash; a do Codex foi observada no evento de execução do comando. Antes de atualizar esta evidência, os hashes dos 101 caminhos operacionais registrados e o estado do Git permaneceram iguais aos anteriores aos testes. Os registros locais da execução ficam em `/tmp/context-session-check-wevesvfe`; esse diretório temporário não é baseline nem armazenamento permanente.

O teste confirma descoberta da entrada compartilhada e execução da conferência estrutural. Não comprova cumprimento completo das rotas em toda tarefa: o Claude identificou os obrigatórios de `implementation_increment`, mas não abriu todos. Também não exercita descoberta nativa das skills, execução de incremento, revisão de código, interface das extensões ou ganho de eficiência. O guia foi usado como procedimento de conferência; os três fluxos de skills não foram exercitados nesses testes.

Mem0 não foi validado nessas sessões. No Claude, as duas buscas foram recusadas pela lista de permissões restrita do próprio teste (`dontAsk`, com leitura e conferência permitidas). No Codex, as duas buscas receberam `Unknown search argument: app_id`: a instrução de adicionar metadados conflita com o schema do conector instalado. Os agentes prosseguiram pelas fontes do repositório, e a conferência do pacote funcionou sem memória. Não foram alteradas configurações globais para esconder essas falhas. O Codex também emitiu avisos de flag de hooks obsoleta e cache de modelos incompatível, sem impedir a conclusão desta conferência.

A execução somente leitura e a descoberta de `AGENTS.md` seguem os mecanismos documentados em [modo não interativo](https://learn.chatgpt.com/docs/non-interactive-mode) e [instruções por AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md). O resultado local acima delimita o que foi efetivamente observado.

## Limites e continuidade

Este resultado verifica a automação, seus controles estruturais e a conferência do pacote em sessões novas via CLI localmente. A execução do novo passo no GitHub Actions e a implementação do mesmo incremento pelos dois agentes ainda não foram observadas. O piloto usa caminhos explícitos em `AGENTS.md`; descoberta nativa de skills não foi configurada.

Somente o INC-002 possui seletores registrados. Novos pacotes exigem curadoria explícita. A ferramenta não infere quais decisões são relevantes, não valida significado esportivo e não comprova completude da migração Drive → Git. As pendências `GOV-002`, `GOV-003`, `GOV-006` e `ID-001` continuam preservadas no pacote.

Grafos AST, hooks Git, Lore e Atlan exigem o tratamento próprio previsto na ADR-002 antes de se tornarem dependências do contexto. O modelo C4/YAML já tem a decisão posterior `DOC-003`; sua materialização não foi confundida com um grafo sintático histórico. Esta tarefa não aprovou novos itens nem alterou requisitos esportivos.

As alterações preexistentes em `DECISIONS.yaml`, `DECISION_LOG.md`, `build_decision_log.py` e a remoção de `gemini-review.yml` foram preservadas. Não houve commit, push ou publicação externa.

## Ensaio posterior com alteração de código — 2026-09-17

O [ensaio de sessões novas](./context-session-evaluation.md) acrescenta evidência de implementação, testes e revisão dos três procedimentos para uma correção do seletor Markdown. Ambos os agentes trabalharam em checkouts da mesma revisão e passaram em oito testes independentes; Codex passou em 83 testes documentais e Claude em 81. A solução do Codex foi integrada. Isso supera a conferência somente leitura anterior, sem verificar um incremento completo, conformidade integral dos agentes, eficiência geral ou a arquitetura histórica inteira. O relatório delimita a omissão de leituras acionadas no Claude e registra consumo e artefatos permanentes.
