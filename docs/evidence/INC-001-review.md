# INC-001 — Revisão do intervalo persistido

- Estado do incremento: **VERIFIED localmente** em 2026-09-13.
- Branch: `inc-001-architecture-spike`.

Após salvar o intervalo 001 pela interface, o backend, o frontend e o navegador foram encerrados. Em uma nova execução, `GET /spike/intervals` recuperou o registro do SQLite `.local/data/inc001.sqlite3` e a seção **Revisão** mostrou `Intervalo 001 — CEPRAEA x COSTA.mp4 · 01:15.320 → 01:24.210` com o comando **REVER**. A página carregou com o MP4 real, duração `2182.055` s, sem overlay de erro.

No Chromium, `REVER` buscou `start_ms = 75320`. O evento `seeked` ocorreu em `75.320` s, seguido de `play` e `playing` com `paused=false`. O tempo avançou pelo trecho e a interface pausou em `end_ms = 84210`, com `currentTime=84.210`, `paused=true` e a mensagem `Revisão do intervalo 001 concluída.`. O comando foi repetido e concluiu novamente. A parada usa o tempo corrente do player, com precisão temporal funcional; não há promessa de precisão frame a frame.

Depois da revisão, o SHA-256 do MP4 original continuou `ea6607f4d6a0095c1b413722fefa41aa50be57f2e1b6b9bed1fef7ed908c23c9`, igual ao valor anterior à marcação. `.local/media` continha apenas `CEPRAEA x COSTA.mp4`; nenhum MP4 derivado foi criado. `npm test -- --run` passou (1 teste) e `npm run build` compilou o frontend.

Isso completa localmente o gate observável do ADR-001 para o INC-001: arquivo real → navegação temporal → início/fim → SQLite → encerramento/reabertura → revisão → original preservado. A tabela `spike_intervals` e os milissegundos inteiros continuam experimentais; esta evidência não torna o schema de `LANCE` nem a stack definitivos.

## Reexecução do teste crítico pelo fluxo da interface

Em nova sessão do navegador Chromium, com ambos os servidores inicialmente desligados, a sequência foi executada novamente com um **novo** registro. Os comandos foram acionados na interface pelo `agent-browser`, com observação do player e dos estados exibidos; a conclusão abaixo não se baseia no teste automatizado do backend.

| Etapa | Observação |
| --- | --- |
| Marcar | No MP4 real, **Avançar 10 s** → **INICIAR LANCE** capturou `00:10.000 (10000 ms)`; novo **Avançar 10 s** → **ENCERRAR LANCE** capturou `00:20.000 (20000 ms)`. |
| Salvar | A interface exibiu `Intervalo #2 salvo no SQLite, sem criar outro MP4.`; o backend registrou `POST /spike/intervals` com resposta `201 Created`. |
| Encerrar | Backend e frontend foram encerrados; as portas `8000` e `5173` ficaram sem processos ouvindo. O navegador também foi fechado. |
| Reiniciar e abrir | Backend e frontend foram iniciados em novos processos. Uma nova sessão do navegador recuperou `Intervalo 002 — CEPRAEA x COSTA.mp4 · 00:10.000 → 00:20.000` pela listagem da interface; o backend registrou `GET /spike/intervals` com resposta `200 OK`. |
| Rever | O botão **REVER** do intervalo 002 gerou `seeked` em `10.000` s, seguido de `play`/`playing` com `paused=false`. Durante a revisão, `currentTime=12.433` s; ao concluir, `currentTime=20.000` s, `paused=true` e a mensagem `Revisão do intervalo 002 concluída.`. |

Após o reinício, o SQLite continha os registros `(1, 'CEPRAEA x COSTA.mp4', 75320, 84210)` e `(2, 'CEPRAEA x COSTA.mp4', 10000, 20000)`. O SHA-256 do MP4 original permaneceu `ea6607f4d6a0095c1b413722fefa41aa50be57f2e1b6b9bed1fef7ed908c23c9`, e `.local/media` continha apenas o arquivo original. O gate crítico de persistência passou nesta execução local.
