# INC-001 — Evidência parcial da mídia local

- Estado do componente: **VERIFIED** localmente em 2026-09-13.
- Estado atual do incremento completo: **VERIFIED** localmente; ver `docs/evidence/INC-001-review.md`.
- Branch: `inc-001-architecture-spike`.

O FastAPI expõe apenas MP4s diretamente em `.local/media` (ou `CEPRAEA_MEDIA_DIR`) por `GET /spike/media` e `GET /spike/media/{nome}`. O nome relativo é usado como `media_path` nos intervalos. O Vite encaminha `/spike` ao backend no desenvolvimento. A verificação do player React está em `docs/evidence/INC-001-player.md`.

Verificação executada:

```text
.venv/bin/python -m pytest backend/tests
6 passed
cd frontend && npm test
1 test file passed
cd frontend && npm run build
build concluído
```

O teste `test_local_mp4_is_listed_and_supports_byte_ranges` verifica que apenas MP4 aparece na listagem e que o arquivo responde a `Range` com `206`, `Content-Range` e bytes esperados, sem modificar o original. `test_media_outside_local_directory_is_not_exposed` verifica que um link simbólico para fora do diretório não é listado, servido ou salvo como referência de intervalo.

Nesta etapa, o teste e o build do frontend passaram após configurar o proxy do Vite. O teste visual no navegador foi registrado posteriormente em `docs/evidence/INC-001-player.md` e `docs/evidence/INC-001-review.md`.

Esta evidência cobre a entrega local do MP4; a revisão que concluiu o gate consta em `docs/evidence/INC-001-review.md`.
