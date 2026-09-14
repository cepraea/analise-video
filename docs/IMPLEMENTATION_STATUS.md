# IMPLEMENTATION_STATUS.md

## Estado global

- `REPOSITORY_INITIALIZED`: VERIFIED
- `DOCUMENTATION_BOOTSTRAP`: VERIFIED
- `INC-000`: VERIFIED
- `INC-001`: VERIFIED (gate local com MP4 real e CI do commit `23336f7`; evidência em `docs/evidence/INC-001.md`)
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

O `INC-000` não constitui evidência do fluxo de análise de vídeo. Naquele incremento não foram comprovados player de vídeo, captura de timestamps, banco de domínio, persistência de lance, classificação de posse/fase, revisão de lances, cadastro de atletas/ações, filtros ou coleções.

## INC-001 — Spike de mídia local e persistência experimental

Evidência consolidada do commit testado, do MP4 real, da suíte, da CI e dos testes no navegador: `docs/evidence/INC-001.md`.

O backend lista e entrega MP4s de `.local/media` por `/spike/media`, com suporte a requisições por faixa de bytes. O Vite encaminha essas rotas ao FastAPI no desenvolvimento. Evidência: `docs/evidence/INC-001-media.md`.

O player React reproduziu um MP4 local real, pausou, buscou para frente e para trás e exibiu o tempo corrente no navegador. Evidência: `docs/evidence/INC-001-player.md`.

Os comandos `INICIAR LANCE` e `ENCERRAR LANCE` capturam tempos em milissegundos inteiros e recusam `start_ms >= end_ms`. Após validar, a interface salva somente a referência temporal no SQLite e mostra o ID retornado. O hash do MP4 real permaneceu idêntico e nenhum derivado foi criado. A escolha por milissegundos não foi promovida a regra canônica. Evidências: `docs/evidence/INC-001-marking.md` e `docs/evidence/INC-001-save.md`.

O backend salva e recupera intervalos em `.local/data/inc001.sqlite3` por meio das rotas `/spike/intervals`. O teste fecha e reabre a aplicação, verifica os cinco campos da tabela e confirma que a mídia original não é alterada. Evidência: `docs/evidence/INC-001-persistence.md`. Essa tabela é descartável e não representa `LANCE` ou `VideoSource` canônicos.

Após encerrar e reabrir a aplicação, a interface recuperou o intervalo 001 do SQLite. O comando **REVER** buscou `75.320` s, reproduziu e pausou em `84.210` s; uma segunda revisão também concluiu. O hash do MP4 permaneceu igual e nenhum derivado foi criado. O gate observável do INC-001 está `VERIFIED` localmente. Evidência: `docs/evidence/INC-001-review.md`.

O teste crítico foi repetido com um novo intervalo 002, marcado e salvo pela interface em `10.000`–`20.000` s. Backend, frontend e navegador foram encerrados; novos processos recuperaram o registro e **REVER** iniciou em `10.000` s e pausou em `20.000` s. O registro permaneceu no SQLite e o original foi preservado. A sequência observada está detalhada na mesma evidência.

Após todos os testes, o SHA-256 do MP4 original foi calculado novamente e coincidiu com o valor registrado antes da marcação; `sha256sum --check` retornou `OK`. A comparação explícita para RF-030/RNF-005 está em `docs/evidence/INC-001-original-integrity.md`.

Os testes determinísticos agora cobrem criação, rejeição de `start_ms >= end_ms`, reabertura do SQLite e recuperação, além dos comandos de marcação e da lista básica no frontend com API simulada. Passaram 7 testes de backend e 5 de frontend, mais o build. A reprodução e a revisão com MP4 real permanecem verificações no navegador. Evidência: `docs/evidence/INC-001-deterministic-tests.md`.

## Arquitetura

`ADR-001`: PROPOSTA A VALIDAR. Resultado do gate com vídeo real: **PASS WITH RISKS** em 2026-09-14.

O sucesso da CI, por si só, não satisfaz o gate. O INC-001 também abriu e reviu um MP4 local real após reinício, persistiu os limites e preservou o hash do original. Os riscos remanescentes e as verificações futuras estão registrados em `docs/architecture/ADR-001.md`. React, FastAPI, SQLite e os demais componentes ainda não representam stack canônica definitiva.

## Próximo gate de código

O próximo incremento planejado é `INC-002`, conforme `docs/IMPLEMENTATION_PLAN.md`.

## Política de estado

- `NOT_IMPLEMENTED`: nenhuma implementação correspondente.
- `IMPLEMENTED_NOT_VERIFIED`: código/artefato existe, mas ainda não há verificação suficiente.
- `VERIFIED`: critério observável/teste passou com evidência registrada.
- `BLOCKED`: implementação correta depende de decisão ou pré-condição ausente.

Documentação ou plano não constituem evidência de funcionamento do produto.
