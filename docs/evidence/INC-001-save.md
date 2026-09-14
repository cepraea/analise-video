# INC-001 — Evidência parcial de clip virtual salvo

- Estado do componente: **VERIFIED** localmente em 2026-09-13.
- Estado atual do incremento completo: **VERIFIED** localmente; ver `docs/evidence/INC-001-review.md`.
- Branch: `inc-001-architecture-spike`.

`ENCERRAR LANCE`, após validar `start_ms < end_ms`, chama `POST /spike/intervals`. O backend insere somente `media_path`, `start_ms` e `end_ms` na tabela experimental `spike_intervals`; `id` e `created_at` são gerados pelo SQLite. Não há rotina de recorte, exportação ou criação de MP4 derivado.

Verificação no navegador Chromium via `agent-browser`, com o MP4 real em `.local/media`:

| Ação | Observação |
| --- | --- |
| Iniciar em `75.320` s | `start_ms = 75320` |
| Encerrar em `84.210` s | um `POST /spike/intervals`, resposta `201`, confirmação `Intervalo #1 salvo` |
| Tentar fim anterior ao início | erro visível e nenhum segundo POST |
| Consultar SQLite após encerrar o backend | um registro: `id=1`, `media_path=CEPRAEA x COSTA.mp4`, `start_ms=75320`, `end_ms=84210` |
| Listar `.local/media` após salvar | apenas o MP4 original; nenhum `lance-*.mp4` |

O SHA-256 do MP4 original, antes e depois, foi `ea6607f4d6a0095c1b413722fefa41aa50be57f2e1b6b9bed1fef7ed908c23c9`. O banco SQLite está em `.local/data/inc001.sqlite3`, ignorado pelo Git. Os testes do backend passaram (`6 passed`), assim como `npm test` e `npm run build` no frontend.

A aplicação foi reaberta e o intervalo foi revisto pela interface em `docs/evidence/INC-001-review.md`. A tabela continua descartável e não representa o schema canônico de `LANCE`.
