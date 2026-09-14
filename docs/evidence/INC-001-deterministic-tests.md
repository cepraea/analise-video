# INC-001 — Testes automatizados determinísticos

- Data: 2026-09-13.
- Branch: `inc-001-architecture-spike`.

## Backend

`backend/tests/test_spike_storage.py` usa um MP4 fictício em diretório temporário para testar a API e o SQLite, sem alegar reprodução de vídeo. O teste cria um intervalo via `POST /spike/intervals`, verifica ID e campos, fecha a aplicação, reabre o mesmo arquivo SQLite e recupera o registro via `GET /spike/intervals`. Casos separados verificam que `start_ms > end_ms` e `start_ms == end_ms` retornam `422` e não inserem linhas.

## Frontend

`frontend/src/App.test.tsx` usa jsdom e respostas HTTP simuladas. Os testes acionam **INICIAR LANCE** e **ENCERRAR LANCE** em um elemento de vídeo com tempos definidos, conferem os milissegundos inteiros e o corpo do `POST`, a confirmação e a lista visível. Também verificam que fim igual ou anterior ao início mostra erro e não envia `POST`, e que um intervalo devolvido por `GET` aparece ao abrir a interface.

```text
.venv/bin/python -m pytest backend/tests  → 7 passed
cd frontend && npm test                → 2 files, 5 tests passed
cd frontend && npm run build           → concluído
```

Esses testes cobrem regras, persistência e estados previsíveis da interface. Seek, fluidez da navegação e revisão perceptiva continuam dependendo da execução com o MP4 real descrita em `docs/evidence/INC-001-player.md` e `docs/evidence/INC-001-review.md`.

## Suíte completa pela raiz do repositório

Em 2026-09-13, `make test` concluiu com código `0`: **7 testes pytest** e **5 testes Vitest** passaram. Isso incluiu os testes de bootstrap do INC-000 (`/health`, criação dos diretórios locais e metadados do frontend). `make build` também concluiu com código `0`, incluindo compilação TypeScript e build Vite. O pytest emitiu duas advertências de depreciação de dependências, sem falhas.
