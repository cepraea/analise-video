# IMPLEMENTATION_STATUS.md

## Estado global

- `REPOSITORY_INITIALIZED`: VERIFIED
- `DOCUMENTATION_BOOTSTRAP`: VERIFIED
- `INC-000`: VERIFIED
- `INC-001`: NOT_IMPLEMENTED
- `INC-002`: NOT_IMPLEMENTED
- `INC-003`: NOT_IMPLEMENTED
- `INC-004`: NOT_IMPLEMENTED
- `INC-005`: NOT_IMPLEMENTED
- `INC-006`: NOT_IMPLEMENTED
- `INC-007`: NOT_IMPLEMENTED
- `FIRST_FUNCTIONAL_FLOW`: NOT_IMPLEMENTED

## Evidência do bootstrap documental

O repositório foi inicializado e os arquivos de documentação do bootstrap foram gravados e relidos no branch `main`: `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/SYSTEM_SPEC.md`, `docs/GAME_MODEL.md`, `docs/architecture/ADR-001.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/TRACEABILITY.md` e este arquivo.

## INC-000 — Fundação executável

`VERIFIED` em 2026-09-13.

Evidência principal: `docs/evidence/INC-000.md`.

A execução do GitHub Actions run `34782679938`, sobre o commit `764e0602836462f6cc75bc73885594ab8aaa7918`, concluiu com `success` após instalar e testar o backend em Python 3.12, instalar e testar o frontend em Node 22.12 e executar o build Vite.

A fundação contém:

- backend Python/FastAPI mínimo com `/health`;
- configuração de diretórios locais de runtime;
- testes mínimos de inicialização/configuração;
- frontend React + TypeScript + Vite mínimo;
- teste Vitest mínimo e build compilável;
- `Makefile` com comandos de bootstrap, teste, build e desenvolvimento;
- `.gitignore` para runtime local, mídia/dados locais e artefatos de build;
- configuração sem API paga, cloud ou segredo obrigatório.

## Evidência funcional do produto

O `INC-000` não constitui evidência do fluxo de análise de vídeo. Ainda não foram comprovados player de vídeo, captura de timestamps, banco de domínio, persistência de lance, classificação de posse/fase, revisão de lances, cadastro de atletas/ações, filtros ou coleções.

## Arquitetura

`ADR-001`: PROPOSTA A VALIDAR.

O sucesso do INC-000 demonstra apenas que a fundação proposta instala, testa e compila. React, FastAPI, SQLite e os demais componentes do ADR ainda não representam stack canônica definitiva. O gate arquitetural ocorre no `INC-001` com um vídeo local real e persistência/revisão do intervalo.

## Próximo gate de código

O próximo incremento é `INC-001 — Architecture Spike: vídeo local → intervalo persistido → revisão`.

## Política de estado

- `NOT_IMPLEMENTED`: nenhuma implementação correspondente.
- `IMPLEMENTED_NOT_VERIFIED`: código/artefato existe, mas ainda não há verificação suficiente.
- `VERIFIED`: critério observável/teste passou com evidência registrada.
- `BLOCKED`: implementação correta depende de decisão ou pré-condição ausente.

Documentação ou plano não constituem evidência de funcionamento do produto.
