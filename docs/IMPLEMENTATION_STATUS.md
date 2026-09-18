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

## Arquitetura de contexto — piloto local

- Geração e conferência estrutural do pacote INC-002: `VERIFIED` localmente.
- Carregamento da entrada e conferência do pacote em sessões novas de Codex e Claude via CLI: `VERIFIED` localmente.
- Correção técnica do seletor Markdown em sessões novas e checkouts da mesma revisão, com três procedimentos, testes e revisão: `VERIFIED` para a tarefa delimitada. Conformidade geral de leitura e eficiência de todo o fluxo permanecem não verificadas.
- Repetição de Claude com consulta a PACKS antes de editar e ao manifesto antes dos testes: `VERIFIED` na segunda tentativa de esclarecimento das skills, para a mesma correção técnica.
- Redução de entrada de 59,79% em três pares Claude com contexto fornecido e cache zero: `VERIFIED` para o controle amplo reconstruído versus recorte técnico, com sucesso em 3/3 técnicas e 2/3 amplas nos mesmos checks. [Medição e limites](./evidence/context-economy.md). Fluxo autônomo e outras tarefas não medidos.
- Redução de entrada total de 53,72% em três pares Codex com os mesmos prompts/revisão da medição Claude: `VERIFIED` para o controle reconstruído desta tarefa. Sucesso 3/3 técnicas e 3/3 amplas nos mesmos checks; zero tokens lidos de cache em todas as execuções, criação não exposta. [Medição Codex e limites](./evidence/context-economy-codex.md).
- Implementação de um incremento completo pelos dois agentes: `IMPLEMENTED_NOT_VERIFIED`.
- Segunda tarefa pela rota `implementation_increment`, com correção do backend INC-001 em cópias isoladas: contrato funcional `VERIFIED`; protocolo completo `VERIFIED` somente no Codex inicial. No Claude, esclarecimentos sucessivos fecharam skills/manifesto, required e confirmação curta em ensaios delimitados. Após explicitar o gatilho ADR, uma sessão nova consultou ADR-001 e confirmou `acesso à mídia INC-001` antes da reprodução/edição, além dos quatro required, e passou em 8 métodos independentes/12 testes backend/83 documentais. Gatilho ADR `VERIFIED` nessa sessão; code-review e conferência do pacote foram omitidos, mantendo o fluxo conjunto `IMPLEMENTED_NOT_VERIFIED`. [Protocolo, tentativas e resultados](./evidence/context-second-route.md). As propostas não foram integradas ao backend operacional.
- Checkpoint de disposição dos opcionais antes da edição: `VERIFIED` na sessão Claude `3cbe8c56-5f91-4783-a834-b4fa043daca2`, que conferiu a ausência do pacote INC-001 no filesystem e a registrou antes de editar. Checkpoint de code-review: `IMPLEMENTED_NOT_VERIFIED`; a skill foi lida antes do diff, mas o registro “consultado” precedeu o resultado da leitura. Plano e rastreabilidade também foram omitidos nessa execução, mantendo o protocolo integral não verificado. O gatilho ADR permaneceu inalterado.
- Regras delimitadas de nomes e tamanho de código: `VERIFIED` localmente para workspace/índice, com alertas de 301–500 linhas, falha acima de 500 sem exceção completa e contratos explícitos de prefixo. O diagnóstico mantém quatro alertas conhecidos; não infere semântica por regex.
- Modelo C4/YAML e vistas Mermaid: `VERIFIED` estruturalmente para geração/validação determinística, referências e integridade de relações. O modelo arquitetural canônico permanece separado do grafo do código observado.
- Grafo local de código A10 e vistas A11: `VERIFIED` localmente para AST Python e TypeScript 7 em Python/TS/TSX/JS/JSX, hashes do corpus/configuração/extratores, consulta limitada, duas vistas Mermaid ligadas ao mesmo hash e freshness seletivo contra os bytes do índice. Seis testes descartáveis cobrem aliases, IDs, endpoints, rename/remoção, índice/workspace, adulteração, dependência ausente e gatilho do pre-commit. PDF continua adiado e as vistas ficam sob demanda.
- Revisão do índice e Lore: `VERIFIED` localmente para scripts, seis testes, hooks reversíveis e alias `git lore-commit`. Nenhum arquivo foi preparado e nenhum commit foi criado por esta implantação.
- Evidência e limites: [context-architecture.md](./evidence/context-architecture.md).
- Ensaio com código e consumo disponível: [context-session-evaluation.md](./evidence/context-session-evaluation.md).

A automação não promove o INC-002 nem comprova a migração documental completa. Os estados do produto acima permanecem sustentados por suas evidências próprias.

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

Na branch `inc-001-player-adjustments`, o novo fluxo está **VERIFIED** no commit `ab82eef`, com resultado **PASS WITH RISKS**: `ENCERRAR LANCE` exibe a prévia sem fazer POST; **REVER** inicia a revisão da prévia; **DESCARTAR** limpa a marcação; **CONFIRMAR E SALVAR** envia uma única criação e preserva a prévia em caso de falha. `Esc` sai da revisão preservando a prévia e, se pressionado novamente, descarta a marcação. Os atalhos de operação `Espaço`, `I`, `O`, `R` e `Enter` estão implementados; `R` exige seleção explícita de um intervalo salvo quando não há prévia. Campos editáveis e controles nativos do vídeo não recebem atalhos globais, e `Espaço`/`Enter` em botões mantêm a ativação nativa.

As setas movem ±1 s, `Shift` + setas ±0,1 s e `Ctrl` + setas ±10 s, com limites no vídeo; as marcações continuam em milissegundos inteiros. O seletor oferece 0,25x, 0,5x, 1x, 1,5x e 2x, inicia em 1x e mantém a escolha ao trocar de MP4. A lista de intervalos ativos agora oferece REVER, EDITAR e EXCLUIR. A edição ajusta cada borda sem trocar o ID, grava o estado anterior na tabela de versões e rejeita limites inválidos na interface; a exclusão exige motivo, oculta o item da lista operacional e mantém o registro para auditoria. A API oferece consultas separadas de versões e excluídos. Os testes locais passaram (11 backend, 24 frontend), o build Vite concluiu e a CI aprovou o commit `ab82eef`. O ensaio com MP4 real confirmou atalhos, revisão, edição persistida e exclusão auditável. A evidência histórica do INC-001 acima continua restrita ao commit `23336f7` e ao comportamento testado nele.

Após 30 marcações, o operador relatou ter exercitado seeks, velocidades, fluxo sem mouse, revisão da prévia, parada do trecho e exclusões com justificativas. Sete exclusões com motivos e datas foram confirmadas no banco e na API de auditoria. O intervalo 030 foi corrigido para `554729`–`561923` ms mantendo identidade e metadados, e a versão anterior foi registrada. Depois de reiniciar backend e frontend, o operador reviu o mesmo ID e confirmou a correção; API e SQLite recuperaram os limites novos, e a integridade do banco permaneceu `ok`. O [ensaio manual](evidence/INC-001-player-restart-30.md), a [evidência consolidada](evidence/INC-001-player-adjustments.md) e a [CI](https://github.com/cepraea/analise-video/actions/runs/34873172548) sustentam o estado `VERIFIED` desta extensão. A evidência histórica do INC-001 permanece vinculada ao commit `23336f7`.

## Arquitetura

`ADR-001`: **APROVADA COM RISCOS** para implementação incremental. Resultado do gate com vídeo real: **PASS WITH RISKS** em 2026-09-14; stack definitiva ainda pendente.

O sucesso da CI, por si só, não satisfaz o gate. O INC-001 foi mantido `VERIFIED` porque também abriu e reviu um MP4 local real após reinício, persistiu os limites e preservou o hash do original. Nenhuma falha significativa foi observada nesse cenário; os riscos remanescentes e as verificações futuras estão registrados em `docs/architecture/ADR-001-primeira-implementacao.md`. React, FastAPI, SQLite e os demais componentes ainda não representam stack canônica definitiva.

## Próximo gate de código

O próximo incremento planejado é `INC-002`, conforme `docs/IMPLEMENTATION_PLAN.md`.

## Política de estado

- `NOT_IMPLEMENTED`: nenhuma implementação correspondente.
- `IMPLEMENTED_NOT_VERIFIED`: código/artefato existe, mas ainda não há verificação suficiente.
- `VERIFIED`: critério observável/teste passou com evidência registrada.
- `BLOCKED`: implementação correta depende de decisão ou pré-condição ausente.

Documentação ou plano não constituem evidência de funcionamento do produto.
