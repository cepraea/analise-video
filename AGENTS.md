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
| governança ou auditoria | `SSOT.md` + rota em `docs/context/ROUTES.yaml` |

## Exclusões de contexto

- Consulte `docs/context/ROUTES.yaml` antes de ampliar o contexto.
- Exclua `archive/` e `.local/drafts/` de buscas normais.
- Acesse `archive/` somente em auditoria, por SHA-256 exato.
- Pare diante de conflito de autoridade, referência quebrada ou documento obrigatório ausente.
