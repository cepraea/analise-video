# Evidência consolidada — extensão do player e do SQLite

- Data: 2026-09-14.
- Branch: `inc-001-player-adjustments`.
- Commit de implementação testado: [`ab82eef23dc48a7fbee9ce23ae132df15574f510`](https://github.com/cepraea/analise-video/commit/ab82eef23dc48a7fbee9ce23ae132df15574f510).
- Pull request: [#2](https://github.com/cepraea/analise-video/pull/2).
- Resultado do gate: **PASS WITH RISKS**.

Esta evidência cobre a extensão experimental executada depois do gate original do INC-001. Ela não transforma `spike_intervals` no modelo canônico de `LANCE` e não altera a evidência histórica do commit `23336f7`.

## Vídeo real e integridade

| Campo | Resultado |
| --- | --- |
| Arquivo | `.local/media/CEPRAEA x COSTA.mp4` |
| Tipo | MP4, vídeo H.264 e áudio AAC |
| Duração | `2182.055` s (`36:22.055`) |
| Tamanho | `854101055` bytes |
| SHA-256 anterior | `ea6607f4d6a0095c1b413722fefa41aa50be57f2e1b6b9bed1fef7ed908c23c9` |
| SHA-256 depois das 30 marcações, exclusões, edição e reinícios | `ea6607f4d6a0095c1b413722fefa41aa50be57f2e1b6b9bed1fef7ed908c23c9` |
| Arquivos em `.local/media` | Somente `CEPRAEA x COSTA.mp4`; nenhum derivado foi criado |

**Resultado:** hash antes = hash depois. O original permaneceu inalterado.

## Teste manual

O operador realizou 30 marcações com o MP4 real e relatou ter exercitado os passos de ±10 s, ±1 s e ±0,1 s, as cinco velocidades, o fluxo de marcação sem mouse, a revisão de prévia e a parada no fim. A revisão não salvou automaticamente: o intervalo somente foi criado após confirmação.

O banco terminou com 30 registros: 23 ativos e 7 excluídos logicamente. Todos os excluídos possuem motivo e data, continuam disponíveis em `GET /spike/intervals/deleted` e não aparecem na lista operacional.

O intervalo 030 foi criado com `554729`–`560923` ms e depois editado para `554729`–`561923` ms. O ID 30, `media_path` e `created_at` foram preservados. A tabela `spike_interval_versions` manteve a versão anterior. Depois de encerrar e reiniciar backend e frontend, o operador reviu o intervalo 030 e confirmou que a correção permaneceu. A API e o SQLite recuperaram o mesmo ID e os limites corrigidos; `PRAGMA quick_check` retornou `ok`.

Detalhes e consultas estão em [INC-001-player-restart-30.md](INC-001-player-restart-30.md), [INC-001-player-shortcuts-smoke.md](INC-001-player-shortcuts-smoke.md) e [INC-001-player-storage-migration.md](INC-001-player-storage-migration.md).

## Verificação automatizada local

Ambiente observado: Python `3.12.3`, Node `v24.14.1`, npm `11.11.0` e SQLite `3.45.1`.

| Comando | Resultado |
| --- | --- |
| `make test` | **Passou**: 11 testes do backend e 24 testes do frontend |
| `make build` | **Passou**: TypeScript e build Vite concluídos |
| `git diff --check` | **Passou** |
| `sha256sum '.local/media/CEPRAEA x COSTA.mp4'` | **Passou**: hash idêntico ao anterior |
| `find .local/media -maxdepth 1 -type f` | **Passou**: somente o original |
| `PRAGMA quick_check` | **Passou**: `ok` |

Os avisos de depreciação emitidos pelo TestClient não causaram falha e não afetaram os resultados.

## CI

O GitHub Actions run [`34873172548`](https://github.com/cepraea/analise-video/actions/runs/34873172548), disparado pelo pull request #2 sobre o commit `ab82eef`, terminou com `success`. O job instalou e testou o backend com Python 3.12, instalou e testou o frontend com Node 22 e executou o build Vite.

## Gate arquitetural

Resultado: **PASS WITH RISKS**.

O fluxo local `MP4 → FastAPI → React → SQLite` suportou marcação explícita, revisão, correção com histórico, exclusão lógica auditável e recuperação após reinício sem modificar o original. React, FastAPI e SQLite continuam adequados como base provisória para o desenvolvimento incremental.

Riscos remanescentes:

- o ensaio perceptivo usou um MP4 real e um navegador;
- as verificações de seek e velocidade dependem do relato operacional e não estabelecem precisão quadro a quadro;
- a lista linear com dezenas de intervalos ainda não representa a experiência final de catálogo;
- `spike_intervals` continua sendo infraestrutura experimental e não o schema canônico de `LANCE`;
- empacotamento da estação e compatibilidade com outras mídias permanecem fora deste gate.

Esses riscos não invalidam o fluxo observado, mas precisam permanecer explícitos antes da aceitação operacional e da definição da stack definitiva.
