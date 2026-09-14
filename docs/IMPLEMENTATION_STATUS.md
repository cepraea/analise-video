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

## Extensão experimental do player após o gate INC-001

Na branch `inc-001-player-adjustments`, o novo fluxo está **IMPLEMENTED_NOT_VERIFIED**: `ENCERRAR LANCE` exibe a prévia sem fazer POST; **REVER** inicia a revisão da prévia; **DESCARTAR** limpa a marcação; **CONFIRMAR E SALVAR** envia uma única criação e preserva a prévia em caso de falha. `Esc` sai da revisão preservando a prévia e, se pressionado novamente, descarta a marcação. Os atalhos de operação `Espaço`, `I`, `O`, `R` e `Enter` estão implementados; `R` exige seleção explícita de um intervalo salvo quando não há prévia. Campos editáveis e controles nativos do vídeo não recebem atalhos globais, e `Espaço`/`Enter` em botões mantêm a ativação nativa.

As setas movem ±1 s, `Shift` + setas ±0,1 s e `Ctrl` + setas ±10 s, com limites no vídeo; as marcações continuam em milissegundos inteiros. O seletor oferece 0,25x, 0,5x, 1x, 1,5x e 2x, inicia em 1x e mantém a escolha ao trocar de MP4. A lista de intervalos ativos agora oferece REVER, EDITAR e EXCLUIR. A edição ajusta cada borda sem trocar o ID, grava o estado anterior na tabela de versões e rejeita limites inválidos na interface; a exclusão exige motivo, oculta o item da lista operacional e mantém o registro para auditoria. A API oferece consultas separadas de versões e excluídos. Os testes locais passaram (11 backend, 24 frontend) e o build Vite concluiu. Um [ensaio local de atalhos com MP4 real](evidence/INC-001-player-shortcuts-smoke.md) confirmou foco, revisão e ausência de dupla ativação nos casos exercitados; a verificação perceptiva completa das novas operações e a nova CI continuam pendentes. A evidência do INC-001 acima continua restrita ao commit `23336f7` e ao comportamento testado nele.

Após 30 marcações, o operador relatou ter exercitado seeks, velocidades, fluxo sem mouse, revisão da prévia, parada do trecho e exclusões com justificativas. Sete exclusões com motivos e datas foram confirmadas no banco e na API de auditoria. O intervalo 030 foi corrigido para `554729`–`561923` ms mantendo identidade e metadados, e a versão anterior foi registrada. Depois de reiniciar backend e frontend, o operador reviu o mesmo ID e confirmou a correção; API e SQLite recuperaram os limites novos, e a integridade do banco permaneceu `ok`. O [ensaio manual da extensão](evidence/INC-001-player-restart-30.md) está concluído. A CI e a evidência consolidada com commit testado ainda mantêm a extensão em `IMPLEMENTED_NOT_VERIFIED`.

## Arquitetura

`ADR-001`: **APROVADA COM RISCOS** para implementação incremental. Resultado do gate com vídeo real: **PASS WITH RISKS** em 2026-09-14; stack definitiva ainda pendente.

O sucesso da CI, por si só, não satisfaz o gate. O INC-001 foi mantido `VERIFIED` porque também abriu e reviu um MP4 local real após reinício, persistiu os limites e preservou o hash do original. Nenhuma falha significativa foi observada nesse cenário; os riscos remanescentes e as verificações futuras estão registrados em `docs/architecture/ADR-001.md`. React, FastAPI, SQLite e os demais componentes ainda não representam stack canônica definitiva.

## Próximo gate de código

O próximo incremento planejado é `INC-002`, conforme `docs/IMPLEMENTATION_PLAN.md`.

## Política de estado

- `NOT_IMPLEMENTED`: nenhuma implementação correspondente.
- `IMPLEMENTED_NOT_VERIFIED`: código/artefato existe, mas ainda não há verificação suficiente.
- `VERIFIED`: critério observável/teste passou com evidência registrada.
- `BLOCKED`: implementação correta depende de decisão ou pré-condição ausente.

Documentação ou plano não constituem evidência de funcionamento do produto.
