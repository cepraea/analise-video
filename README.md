# CEPRAEA — Sistema de Análise de Vídeo

Repositório de implementação do sistema de análise audiovisual do CEPRAEA.

## Estado

- `INC-000 — Fundação executável`: `VERIFIED`.
- `INC-001`: `VERIFIED` localmente — mídia, reprodução, marcação, SQLite experimental e revisão após reinício testados com MP4 real.
- `INC-002` em diante: `NOT_IMPLEMENTED`.
- Primeiro fluxo funcional: `NOT_IMPLEMENTED`.
- Arquitetura técnica: `ADR-001 — PROPOSTA A VALIDAR`.

Evidência do INC-000: `docs/evidence/INC-000.md` e GitHub Actions run `34782679938`. Evidência consolidada do INC-001: `docs/evidence/INC-001.md`.

Documentação e presença de código não constituem, sozinhas, evidência de funcionamento.

## Pré-requisitos do INC-000

- Python 3.12.
- Node.js 22.12 ou superior.
- npm.
- Linux/macOS ou ambiente compatível com `make` para os comandos de conveniência abaixo.

Não há API paga, cloud ou segredo obrigatório nesta fundação.

## Inicialização local

Na raiz do repositório:

```bash
make bootstrap
```

Esse comando cria `.venv`, instala o backend em modo editável com dependências de teste e instala as dependências do frontend.

## Testes mínimos

```bash
make test
```

A suíte mínima verifica:

1. inicialização da aplicação FastAPI e resposta de `/health`;
2. criação dos diretórios locais de runtime;
3. bootstrap mínimo do frontend com Vitest.

Os testes do INC-001 verificam a leitura local de MP4, criação e rejeição de intervalos, persistência SQLite após reabrir o backend e comandos básicos da interface com API simulada. Eles não verificam a qualidade do seek ou da revisão: esses comportamentos foram observados com MP4 real no navegador. Evidência e limites: `docs/evidence/INC-001-deterministic-tests.md`.

Para verificar também a compilação do frontend:

```bash
make build
```

A CI executou com sucesso esses gates em ambiente limpo no INC-000.

## Desenvolvimento local

Terminal 1:

```bash
make dev-backend
```

Backend: `http://127.0.0.1:8000`  
Health check: `http://127.0.0.1:8000/health`

Terminal 2:

```bash
make dev-frontend
```

Frontend: `http://127.0.0.1:5173`

## Dados locais

Por padrão, runtime e mídia ficam em:

```text
.local/data
.local/media
```

`.local/` é ignorado pelo Git. Os caminhos podem ser alterados pelas variáveis `CEPRAEA_DATA_DIR` e `CEPRAEA_MEDIA_DIR`; `.env.example` documenta os nomes. Nenhum arquivo de vídeo, banco local ou segredo deve ser versionado.

### Mídia local e persistência experimental do INC-001

Coloque um MP4 diretamente em `.local/media` (ou em `CEPRAEA_MEDIA_DIR`). `GET /spike/media` lista os MP4s disponíveis e fornece a URL local de cada um; `GET /spike/media/{nome}` entrega o arquivo com suporte a `Range` para o seek do player. O Vite encaminha `/spike` ao FastAPI durante o desenvolvimento, de modo que o React pode usar essas URLs no mesmo host da interface. Não há upload para cloud, Supabase ou YouTube.

Em `http://127.0.0.1:5173`, selecione o MP4. O player tem play/pause nativos, botões simples de reproduzir/pausar e de avançar/voltar 10 segundos, além da leitura do tempo corrente. O botão **Atualizar lista** encontra arquivos adicionados com a página aberta. Evidência da navegação temporal com MP4 real: `docs/evidence/INC-001-player.md`.

**INICIAR LANCE** captura o tempo corrente; **ENCERRAR LANCE** captura o fim, exige `início < fim` e salva a referência temporal pelo backend. Os valores são milissegundos inteiros, uma escolha técnica do spike e não uma regra canônica de `LANCE`. A interface confirma o ID salvo. Na seção **Revisão**, os intervalos salvos reaparecem após reiniciar a aplicação; **REVER** busca o início e reproduz até o fim marcado. Nenhum MP4 derivado é criado. Evidências: `docs/evidence/INC-001-marking.md`, `docs/evidence/INC-001-save.md` e `docs/evidence/INC-001-review.md`.

Ao iniciar o backend, o spike cria `.local/data/inc001.sqlite3` (ou `inc001.sqlite3` dentro de `CEPRAEA_DATA_DIR`). A tabela `spike_intervals` guarda somente `id`, `media_path`, `start_ms`, `end_ms` e `created_at`. Ela **não é o schema canônico de LANCE**. `media_path` é apenas o nome do MP4 dentro do diretório local; o backend não copia nem altera o original.

Com o backend em execução, consulte a mídia e salve um intervalo por HTTP:

```bash
curl http://127.0.0.1:8000/spike/media
curl -X POST http://127.0.0.1:8000/spike/intervals \
  -H 'Content-Type: application/json' \
  -d '{"media_path":"video.mp4","start_ms":1200,"end_ms":3400}'
curl http://127.0.0.1:8000/spike/intervals
```

O teste do backend fecha e reabre a aplicação antes de reler um intervalo gravado pela API. A revisão pela interface também foi verificada após reiniciar os servidores. Para descartar o experimento, pare o backend e remova o arquivo `inc001.sqlite3` do diretório de dados.

## Estrutura executável atual

```text
backend/
  pyproject.toml
  src/cepraea_video/
    __init__.py
    config.py
    main.py
    spike_media.py
    spike_storage.py
  tests/
    test_bootstrap.py
    test_spike_media.py
    test_spike_storage.py

frontend/
  package.json
  tsconfig.json
  vite.config.ts
  index.html
  src/
    App.tsx
    appMeta.ts
    appMeta.test.ts
    main.tsx
```

O `INC-000` não implementou vídeo, SQLite, entidades esportivas, lances, fases ou coleções. A leitura e reprodução local de MP4 e a persistência SQLite experimental foram adicionadas no INC-001; os demais comportamentos continuam pendentes.

## Fontes canônicas

Os snapshots deste repositório derivam de duas fontes do Google Drive:

1. `CEPRAEA — Sistema de Análise de Vídeo — Especificação Canônica v0.1`.
2. `Planejamento completo`, guia `Conceitos do Jogo — CEPRAEA`.

As fontes do Drive mantêm autoridade superior aos snapshots derivados.

## Primeiro fluxo funcional

`ABRIR VÍDEO → MARCAR LANCE → CAPTURAR TEMPOS → CLASSIFICAR POSSE/FASE → SALVAR → REVER → CLASSIFICAR AÇÕES/ATLETAS → FILTRAR → GERAR COLEÇÃO`

## Mapa da documentação

- `AGENTS.md` — entrada para agentes.
- `CLAUDE.md` — entrada para Claude Code.
- `docs/SYSTEM_SPEC.md` — requisitos necessários ao desenvolvimento inicial.
- `docs/GAME_MODEL.md` — conceitos esportivos relevantes à implementação.
- `docs/architecture/ADR-001.md` — hipótese de arquitetura local-first.
- `docs/IMPLEMENTATION_PLAN.md` — incrementos INC-000 a INC-007.
- `docs/TRACEABILITY.md` — relação entre requisitos, incrementos e evidências.
- `docs/IMPLEMENTATION_STATUS.md` — estado comprovado da implementação.
- `docs/evidence/INC-000.md` — evidência da fundação executável.
