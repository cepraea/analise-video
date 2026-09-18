# Contexto compartilhado de Codex e Claude

## Entrada e autoridade

Esta implementação materializa o roteamento aprovado em `GOV-001` e [ADR-002](../architecture/ADR-002-ssot-and-context.md). [AGENTS.md](../../AGENTS.md) é a entrada comum; [CLAUDE.md](../../CLAUDE.md) importa essa entrada. Os documentos responsáveis continuam sendo as fontes; pacotes auxiliam a descoberta.

Os procedimentos versionados em [skills/](../../skills/) são lidos sob demanda pelos caminhos indicados em `AGENTS.md`. O piloto usa leitura desses arquivos pelos agentes; não configura descoberta automática, contas, plugins ou ferramentas globais.

## Fontes sob demanda

- Arquitetura local e riscos: [ADR-001](../architecture/ADR-001-primeira-implementacao.md).
- Autoridade e precedência: [SSOT.md](../SSOT.md) e [AUTHORITY.md](../governance/AUTHORITY.md).
- Decisões: [DECISIONS.yaml](../governance/DECISIONS.yaml); vista humana gerada: [DECISION_LOG.md](../governance/DECISION_LOG.md).
- Significado esportivo: [GAME_MODEL.md](../GAME_MODEL.md).
- Dependências: [backend/pyproject.toml](../../backend/pyproject.toml), [frontend/package.json](../../frontend/package.json) e [scripts/docs/requirements.txt](../../scripts/docs/requirements.txt).
- Ambiente e comandos: [README.md](../../README.md), [Makefile](../../Makefile) e [CI](../../.github/workflows/ci.yml).
- Critérios de revisão: [skills/code-review/SKILL.md](../../skills/code-review/SKILL.md).
- Modelo arquitetural canônico: [C4_MODEL.yaml](../architecture/C4_MODEL.yaml); vistas derivadas em [views/](../architecture/views/).

Abra esses arquivos conforme a tarefa e os gatilhos de [ROUTES.yaml](./ROUTES.yaml). Confirme tecnologias nos manifestos, sem assumir ferramentas descritas em rascunhos. Memórias de agentes auxiliam a pesquisa; não substituem as fontes.

Manutenção de scripts, testes e roteamento de contexto usa a rota `context_maintenance`: este guia e a política são obrigatórios; opcionais seguem seus gatilhos. Consulte o código, seus testes e manifestos pertinentes. Uma manutenção técnica não é execução do INC-002; documentos de produto entram quando a tarefa efetivamente alterar comportamento do produto ou usar significado esportivo.

## Pacotes reproduzíveis

[PACKS.yaml](./PACKS.yaml) declara documentos, trechos, linhas de tabela, decisões e dependências. [ROUTES.yaml](./ROUTES.yaml) determina o contexto obrigatório. O gerador resolve dependências, exige cobertura da rota, copia os trechos sem reinterpretar requisitos e conserva os estados do catálogo de decisões.

Na raiz, com Python e `scripts/docs/requirements.txt` instalados:

```bash
make context
make context-check
make context-rules-check
make architecture-check
make test-docs
```

`context-rules-check` lê [CODE_RULES.yaml](./CODE_RULES.yaml) e examina os bytes do workspace. O script também aceita `--source index` ou `--source commit --revision <ref>` para que a conclusão corresponda à revisão avaliada. Arquivos manuais com 301–500 linhas geram alerta; acima de 500 falham sem exceção explícita com caminho, limite, motivo, responsável e condição de revisão. Convenções nativas por linguagem prevalecem; contratos de prefixo são declarados por função, sem usar regex como prova de efeitos semânticos.

`architecture-check` valida IDs, decisões, fontes, hierarquia, relações e vistas do modelo C4/YAML e compara os Mermaid derivados integralmente. `make architecture` regenera as vistas de forma determinística; o grafo de código permanece outro artefato.

## Grafo local de código

[GRAPH.yaml](./GRAPH.yaml) define o corpus e as exclusões do grafo observado. O extrator usa a AST nativa de Python e a API AST do TypeScript 7 para TS, TSX, JS e JSX. O JSON versionado em [graph/repo-knowledge-graph.json](./graph/repo-knowledge-graph.json) registra SHA-256 de cada arquivo, da configuração e dos extratores; relações resolvidas e chamadas não resolvidas conservam método e confiança distintos.

    make graph
    make graph-check
    make graph-query GRAPH_QUERY=cepraea_video.main
    make graph-views
    make graph-views-check

graph-query devolve somente o subgrafo selecionado e aceita profundidade de zero a três pela CLI Python. As vistas completa e de alto nível ficam em .local/generated/context/, fora do contexto normal, e registram o mesmo graph_sha256.

Antes de um commit que altere o corpus, GRAPH.yaml ou um extrator, prepare primeiro os arquivos pretendidos, execute `make graph GRAPH_SOURCE=index`, examine e prepare somente o JSON resultante, e então execute `make graph-check GRAPH_SOURCE=index` e `make review-staged`. A conferência lê o código e o próprio grafo do índice; divergências posteriores no workspace não mudam sua conclusão. Nenhum comando prepara arquivos automaticamente. Mudança documental fora do corpus não aciona o grafo.

## Revisão do índice e Lore

Os hooks versionados são instalados sem sobrescrever hooks existentes:

```bash
make hooks-install
make hooks-check
make hooks-uninstall
```

`pre-commit` executa `make review-staged` sobre os bytes do índice; não prepara arquivos. `commit-msg` valida a mensagem atual e seu bloco final. A instalação cria o alias local reversível `git lore-commit`, que mostra a mensagem construída antes de pedir ao Git que crie o commit. A [skill Lore](../../skills/lore-commit/SKILL.md) exige `Tested` com fatos observados ou `Not-tested` com limitação concreta; `Constraint` e `Rejected` são opcionais e não recebem valores fictícios. Criar o commit continua dependendo da autorização da tarefa.

O pacote piloto é [INC-002.md](./packs/INC-002.md). Outros incrementos devem ganhar seletores explícitos antes de serem gerados:

```bash
make context CONTEXT_PACK=INC-002
python3 scripts/docs/build_context_pack.py INC-002 --check
```

Cada pacote registra SHA-256 completo de suas fontes, catálogo de fontes, configuração, rotas e geradores. `--check` compara a saída inteira com uma regeneração em memória e falha se houver desatualização ou edição manual. Não escreve arquivos. A saída não depende da data, do caminho absoluto da estação ou de chamadas externas.

Referências declaradas são verificadas e recebem hash, mas seu conteúdo só é aberto sob demanda. Elas não entram como cópias no pacote.

Entrada, guia, skills, rotas e geradores também participam da integridade do pacote. Se um desses arquivos mudar, confira as fontes e regenere com `make context` antes de `make context-check`; não edite hashes ou saídas manualmente para simular validade.

Links no manifesto são relativos ao pacote. Links dentro de trechos cercados por fences conservam o contexto do documento original. Os documentos completos permanecem acessíveis no manifesto para uma investigação direcionada.

## Limites do piloto

Os seletores são curados; a ferramenta não descobre relevância semântica nem valida significado esportivo. A aprovação do primeiro fluxo, da migração e do cutover continua dependendo dos gates e da autoridade documentados. As fontes locais de requisitos ainda são snapshots e o pacote preserva essa ressalva.

O relatório [context-architecture.md](../evidence/context-architecture.md) registra o tratamento dos protótipos históricos. `TECH-002` adota somente o grafo local descrito acima; Atlan e APIs pagas não são dependências. Hooks Git e Lore têm contratos locais próprios. Um arquivo de ignore isolado não é usado como garantia de exclusão; o gerador e o validador rejeitam árvores excluídas e links simbólicos. As regras executáveis de código e o grafo não aprovam semântica esportiva, autoridade ou estado do produto.
