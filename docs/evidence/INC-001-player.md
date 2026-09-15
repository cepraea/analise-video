# INC-001 — Evidência parcial do player local

- Estado do componente: **VERIFIED** localmente em 2026-09-13.
- Estado atual do incremento completo: **VERIFIED** localmente; ver `docs/evidence/INC-001-review.md`.
- Branch: `inc-001-architecture-spike`.

Um MP4 real já presente em `.local/media` foi aberto no React pelo proxy local do Vite e pelo `FileResponse` do FastAPI. `ffprobe` identificou vídeo H.264, áudio AAC e duração de `2182.055` segundos. Nenhum upload ou serviço externo participou do fluxo.

Verificação manual no navegador Chromium por `agent-browser`, com o backend em `127.0.0.1:8000` e o frontend em `127.0.0.1:5173`:

| Ação | Observação |
| --- | --- |
| Abrir a página | player carregado, duração `2182.055` s, sem overlay de erro |
| Reproduzir | `paused=false`; tempo corrente avançou e o estado exibiu `Reproduzindo` |
| Pausar | `paused=true`; tempo corrente em `23.208` s, exibindo `00:23.2` |
| Avançar 10 s | tempo corrente `33.208` s, exibindo `00:33.2` |
| Voltar 10 s | tempo corrente `23.208` s, exibindo `00:23.2` |

`npm test` passou (1 arquivo de teste) e `npm run build` concluiu. A captura dos limites, o salvamento e a revisão após reinício foram verificados depois em `docs/evidence/INC-001-marking.md`, `docs/evidence/INC-001-save.md` e `docs/evidence/INC-001-review.md`.
