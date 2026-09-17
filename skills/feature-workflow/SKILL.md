---
name: feature-workflow
description: Implementar incrementos do CEPRAEA ou manter suas ferramentas de contexto, usando a rota pertinente, escopo autorizado e verificações reais.
---

# Implementar uma tarefa

Leia `AGENTS.md` e classifique a tarefa usando `docs/context/ROUTES.yaml`. Abra os documentos obrigatórios da rota.

Avalie cada gatilho `when` dos opcionais e registre sua disposição na confirmação anterior à primeira edição: `aplicado`, `ausente` ou `não aplicável`, com o motivo. Quando uma condição ocorrer, consulte o documento correspondente antes da ação dependente. Condições de existência, como `generated_pack_exists`, exigem consulta ao filesystem; não presuma ausência. Documentos sem gatilho permanecem sob demanda.

Em `context_maintenance`, consulte `docs/context/PACKS.yaml` antes de implementar alterações no comportamento do gerador, nos seletores ou na integridade de pacotes. Isso inclui correções na extração de seções pelo gerador. Use código e testes pertinentes; uma correção técnica não exige abrir o contexto inteiro do produto.

Para o INC-002, confira `python3 scripts/docs/build_context_pack.py INC-002 --check` antes de usar `docs/context/packs/INC-002.md` como derivado das fontes.

Para incrementos de produto, o contrato está em `docs/IMPLEMENTATION_PLAN.md`, a arquitetura em ADR aprovada e o estado em `docs/IMPLEMENTATION_STATUS.md`. As decisões e pendências estão em `docs/governance/DECISIONS.yaml`. Pesquise IDs e símbolos com `rg` antes de abrir arquivos adicionais.

Consulte a ADR pertinente antes da ação dependente, inclusive da primeira edição de testes, quando implementar, corrigir ou verificar comportamento governado por ela, ou alterar uma decisão técnica. O gatilho inclui manutenção que preserve a arquitetura, mas afete contratos entre módulos, acesso a dados/mídia, persistência, preservação de originais, dependências ou operação. Localize a ADR pelas referências do plano e das decisões; confira escopo, status e autoridade e leia os trechos pertinentes.

- Fluxo local de vídeo, acesso à mídia ou persistência dos intervalos de INC-001/INC-002: consulte `docs/architecture/ADR-001-primeira-implementacao.md`. Rejeitar nomes de mídia inválidos aciona esse gatilho, mesmo sem mudança de stack.
- Alteração da arquitetura de contexto, como seleção, autoridade, exclusões ou integridade dos pacotes: consulte `docs/architecture/ADR-002-ssot-and-context.md`, conforme o gatilho da rota `context_maintenance`.

Mudanças apenas editoriais ou refatorações sem efeito nos comportamentos/decisões acima dispensam ADR adicional; documentos `required` e opcionais acionados pela rota continuam obrigatórios. Na confirmação antes da primeira edição, acrescente `ADR=<caminho e gatilho, ou não aplicável com motivo>`. Uma referência ou declaração não substitui a consulta. Diante de ADR necessária ausente ou status/autoridade incompatível com a tarefa, pare a ação dependente.

Implemente a tarefa solicitada preservando alterações existentes no workspace. Reproduza o problema e defina o resultado esperado antes da correção. Diante de conflito, referência quebrada ou autoridade ausente, pare a ação dependente, registre os caminhos e IDs envolvidos e prossiga apenas no trabalho independente.

Escolha as verificações de `skills/build-and-test/SKILL.md` conforme a alteração. Para código manual, execute a regra de nomes/tamanho sobre a revisão avaliada; alertas exigem avaliação, enquanto erro bloqueia a aceitação até correção ou exceção explícita. Imediatamente antes de revisar o diff, leia `skills/code-review/SKILL.md` e, depois do resultado da leitura, registre `revisão=skills/code-review/SKILL.md consultado`; somente então examine o diff e aplique seus critérios. Se fontes ou referências de um pacote mudarem, regenere e confira o derivado. Quando houver evidência pertinente a produto, atualize rastreabilidade e estado sem promover requisitos de outros incrementos. Registre decisões normativas no catálogo responsável; memórias e sínteses não substituem esse registro.

Se mudar um arquivo coberto por `docs/context/GRAPH.yaml`, a própria configuração ou um dos extratores, regenere e confira o grafo. Durante desenvolvimento use `make graph` e `make graph-check`. Quando a tarefa autorizar preparar o commit, gere a partir dos bytes já preparados com `make graph GRAPH_SOURCE=index`, prepare somente `docs/context/graph/repo-knowledge-graph.json` e confirme com `make graph-check GRAPH_SOURCE=index`. O fluxo não executa `git add` automaticamente. Use `make graph-query GRAPH_QUERY=<módulo-ou-símbolo>` para recuperação direcionada; vistas ficam sob demanda.

Ao encerrar ou transferir a tarefa, informe escopo concluído, arquivos, verificações, limitações e próximo trabalho autorizado. Preserve caminhos, IDs e erros exatos. Commit, PR e publicação seguem a autorização da tarefa em curso.

Quando houver arquivos preparados para commit, execute `make review-staged` sobre o índice. Para gerar ou validar a mensagem, leia `skills/lore-commit/SKILL.md`; essa etapa não prepara arquivos nem autoriza criar o commit.
