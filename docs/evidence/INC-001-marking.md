# INC-001 — Evidência parcial da marcação em memória

- Estado do componente: **VERIFIED** localmente em 2026-09-13.
- Estado atual do incremento completo: **VERIFIED** localmente; ver `docs/evidence/INC-001-review.md`.
- Branch: `inc-001-architecture-spike`.

No player React, `INICIAR LANCE` lê `HTMLVideoElement.currentTime` e converte segundos para milissegundos inteiros com arredondamento. `ENCERRAR LANCE` faz a mesma captura e aceita somente `start_ms < end_ms`. Essa representação é uma escolha técnica descartável do spike, não um schema ou regra canônica de `LANCE`.

Verificação manual em Chromium via `agent-browser`, com MP4 real servido localmente por FastAPI/Vite:

| Ação | Observação |
| --- | --- |
| Antes de iniciar | `ENCERRAR LANCE` desabilitado |
| Iniciar em `75.32` s | `Início: 01:15.320 (75320 ms)`; encerramento habilitado |
| Encerrar em `84.21` s | `Fim: 01:24.210 (84210 ms)`; intervalo válido |
| Novo início em `84.21` s, fim em `75.32` s | fim recusado, mensagem de erro, nenhum fim registrado |
| Fim igual a `84.21` s | igualmente recusado |
| Avançar para `90` s e encerrar | `Fim: 01:30.000 (90000 ms)`; erro removido |

Esta verificação registrou a primeira etapa, antes da integração com o salvamento: `/spike/intervals` permaneceu vazio. O salvamento pela interface e a revisão após reinício foram verificados depois em `docs/evidence/INC-001-save.md` e `docs/evidence/INC-001-review.md`. `npm test` e `npm run build` passaram.
