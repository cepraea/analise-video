# INC-001 — Evidência parcial da persistência experimental

- Estado do componente: **VERIFIED** localmente em 2026-09-13.
- Estado atual do incremento completo: **VERIFIED** localmente; ver `docs/evidence/INC-001-review.md`.
- Branch: `inc-001-architecture-spike`.

O backend inicializa o SQLite em `.local/data/inc001.sqlite3` e expõe `POST` e `GET /spike/intervals`. A tabela `spike_intervals` tem apenas `id`, `media_path`, `start_ms`, `end_ms` e `created_at`; não é o schema canônico de `LANCE`.

Verificação executada:

```text
.venv/bin/python -m pytest backend/tests
6 passed
```

O teste `test_interval_survives_application_restart` salva um intervalo com o nome relativo de um MP4 em `CEPRAEA_MEDIA_DIR`, encerra o contexto da aplicação, abre outro contexto sobre o mesmo arquivo SQLite e compara o registro recuperado. Também inspeciona as colunas reais via `PRAGMA table_info` e compara os bytes da mídia antes e depois. `test_invalid_interval_is_rejected` confirma que `start_ms >= end_ms` não é salvo.

Um smoke test local adicional iniciou dois processos Python independentes sobre um diretório temporário: o primeiro salvou o intervalo via API, terminou, e o segundo recuperou o mesmo registro. O arquivo SQLite existia no disco e os bytes da mídia de teste permaneceram iguais.

O gate com MP4 real, incluindo reprodução, captura de tempos e revisão após reinício, foi concluído posteriormente em `docs/evidence/INC-001-player.md`, `docs/evidence/INC-001-save.md` e `docs/evidence/INC-001-review.md`.
