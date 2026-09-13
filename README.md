# CEPRAEA — Sistema de Análise de Vídeo

Repositório de implementação do sistema de análise audiovisual do CEPRAEA.

## Estado

- `INC-000 — Fundação executável`: `VERIFIED`.
- `INC-001` em diante: `NOT_IMPLEMENTED`.
- Primeiro fluxo funcional: `NOT_IMPLEMENTED`.
- Arquitetura técnica: `ADR-001 — PROPOSTA A VALIDAR`.

Evidência do INC-000: `docs/evidence/INC-000.md` e GitHub Actions run `34782679938`.

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

## Estrutura executável atual

```text
backend/
  pyproject.toml
  src/cepraea_video/
    __init__.py
    config.py
    main.py
  tests/
    test_bootstrap.py

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

O `INC-000` não implementa vídeo, SQLite, entidades esportivas, lances, fases ou coleções. Esses comportamentos pertencem aos incrementos posteriores.

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
