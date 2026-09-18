# AGENTS.md — Mapa de contexto do projeto

## Autoridade documental

- Requisitos do produto: `docs/SYSTEM_SPEC.md`.
- Significado esportivo: `docs/GAME_MODEL.md`.
- Arquitetura: registros em `docs/architecture/` com status explícito.
- Ordem de desenvolvimento: `docs/IMPLEMENTATION_PLAN.md`.
- Rastreabilidade: `docs/TRACEABILITY.md`.
- Estado comprovado: `docs/IMPLEMENTATION_STATUS.md`, código, testes e evidências.
- Decisões: `docs/governance/DECISIONS.yaml`.
- Fontes e baselines: `docs/governance/SOURCES.yaml`.

## Estados preservados pelo projeto

`DECIDIDO`, `DECIDIDO PARCIALMENTE`, `MODELAGEM ATUAL`, `PROPOSTA TÉCNICA`, `PROPOSTA A VALIDAR`, `PENDENTE`, `FORA DO ESCOPO INICIAL`, `NOT_IMPLEMENTED`, `IMPLEMENTED_NOT_VERIFIED`, `VERIFIED` e `BLOCKED`.

## Invariantes já documentados

- Davi é a autoridade sobre o significado esportivo do modelo CEPRAEA.
- `LANCE` é a unidade canônica e vídeo é fonte.
- Originais são imutáveis; derivados permanecem separados.
- Fatos/timestamps permanecem separados de interpretação e feedback.
- Um lance pode possuir várias atletas, ações, coleções e fontes.
- Fases das equipes são independentes.
- Taxonomias em aberto permanecem extensíveis.
- Código existente, sozinho, não comprova funcionalidade; o estado `VERIFIED` depende de evidência correspondente.

## Contexto mínimo por tipo de trabalho

| Trabalho | Contexto principal |
| --- | --- |
| infraestrutura | plano + ADR relevante |
| requisito de produto | `SYSTEM_SPEC.md` |
| classificação/significado esportivo | `GAME_MODEL.md` |
| incremento em execução | `IMPLEMENTATION_PLAN.md` |
| avaliação do que já funciona | `IMPLEMENTATION_STATUS.md` + testes |
| governança ou auditoria | `docs/SSOT.md` + rota em `docs/context/ROUTES.yaml` |
| manutenção das ferramentas de contexto | guia + política pela rota `context_maintenance` |

## Exclusões de contexto

- Consulte `docs/context/ROUTES.yaml` antes de ampliar o contexto.
- Exclua `archive/` e `.local/drafts/` de buscas normais.
- Acesse `archive/` somente em auditoria, por SHA-256 exato.
- Pare diante de conflito de autoridade, referência quebrada ou documento obrigatório ausente.

## Procedimentos sob demanda

- Implementar incrementos, corrigir defeitos ou manter código e ferramentas de contexto: leia `skills/feature-workflow/SKILL.md` antes de editar.
- Executar verificações, inclusive reproduzir defeitos: leia `skills/build-and-test/SKILL.md` antes de escolher os comandos.
- Revisar alterações: imediatamente antes de revisar o diff, leia `skills/code-review/SKILL.md` e registre `revisão=skills/code-review/SKILL.md consultado`.
- Preparar mensagem de commit: leia `skills/lore-commit/SKILL.md`; revise o índice e registre apenas testes e restrições observados.
- Gerar ou conferir um pacote: consulte `docs/context/README.md`.

Antes de editar, consulte todos os documentos `required` da rota. Opcionais cujo `when` ocorrer devem ser consultados antes da ação dependente; os demais permanecem sob demanda.

Antes da primeira edição, inclusive de testes, confirme em uma linha: `rota=<nome>; required consultados=<caminhos>; opcionais avaliados=<caminho: aplicado|ausente|não aplicável e motivo>; pendências=<nenhuma ou faltas>`. Registre cada opcional da rota; condições baseadas em existência exigem consulta ao filesystem. Havendo falta ou opcional não avaliado, resolva antes de editar.

Memórias e resultados de IA auxiliam a descoberta; confirme decisões e estados nos documentos responsáveis. A presença de um pacote não aprova pendências nem autoriza ampliar o incremento.

Ao final de cada tarefa, entregue a *próxima ação* lógica para alcançar o objetivo (DONE) de forma eficiente.
