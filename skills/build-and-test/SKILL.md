---
name: build-and-test
description: Escolher e executar as verificações existentes do repositório CEPRAEA conforme os arquivos alterados, registrando evidência e limites.
---

# Verificar alterações

Execute comandos na raiz do repositório. Antes de escolher e executar verificações, abra o manifesto pertinente à alteração: `backend/pyproject.toml` para backend, `frontend/package.json` para frontend ou `scripts/docs/requirements.txt` para ferramentas Python de documentação/contexto. Registre qual foi consultado. Uma referência no guia ou a leitura automática por um script não substitui essa consulta. Não assuma linters ou scripts presentes nos protótipos.

| Alteração | Verificações |
| --- | --- |
| Ferramentas Python de documentação, rotas, seletores, entrada, skills ou fontes/referências de um pacote | `make context-check` e `make test-docs` |
| Código manual `.py`, `.js`, `.jsx`, `.ts` ou `.tsx` | `make context-rules-check`; para revisão preparada, `python3 scripts/docs/check_code_rules.py --source index` |
| Arquivo no corpus de `docs/context/GRAPH.yaml`, configuração ou extrator do grafo | `make graph`, `make graph-check` e `make test-docs` |
| Grafo preparado para commit | `make graph GRAPH_SOURCE=index`, preparar somente o JSON resultante e executar `make graph-check GRAPH_SOURCE=index` |
| Backend | `.venv/bin/python -m pytest backend/tests` |
| Frontend | `npm --prefix frontend test` e `npm --prefix frontend run build` |
| Fluxo de vídeo | testes pertinentes e observação com mídia real segundo o incremento |

Se um pacote ficar desatualizado, regenere com `make context CONTEXT_PACK=INC-002` depois de conferir a fonte alterada. Execute a conferência novamente. Não edite a saída para simular aprovação.

O grafo é pertinente somente quando muda o corpus, `GRAPH.yaml` ou um extrator. `make review-staged` aplica essa mesma seleção aos bytes do índice e não prepara arquivos. Use `make graph-query GRAPH_QUERY=<módulo-ou-símbolo>` para recuperar um subgrafo; não carregue o JSON completo por padrão. Vistas completas e de alto nível são geradas em `.local/generated/context/` com `make graph-views`.

Para uma correção de código, registre o caso que falha antes e passa depois, além das regressões pertinentes. Separe resultados de testes observados de expectativas ou comandos não executados.

Registre comando, resultado e limitação material. Testes estruturais não aprovam significado esportivo, migração semântica ou usabilidade. Consulte `docs/IMPLEMENTATION_STATUS.md` antes de propor mudança de estado.
