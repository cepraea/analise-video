# Índice da SSOT

## Precedência

1. decisão explícita da autoridade competente registrada em `DECISIONS.yaml`;
2. documento canônico responsável pelo conteúdo;
3. rastreabilidade e estado comprovado;
4. fontes originais e baselines para auditoria;
5. drafts, sínteses e protótipos apenas como insumos.

Formato mais estruturado, data mais recente ou geração por IA não vencem a autoridade definida.

## Responsabilidades

| Conteúdo | Documento |
| --- | --- |
| requisitos do produto | [`SYSTEM_SPEC.md`](./SYSTEM_SPEC.md) |
| significado esportivo | [`GAME_MODEL.md`](./GAME_MODEL.md) |
| arquitetura | [`architecture/`](./architecture/) |
| ordem de desenvolvimento | [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md) |
| rastreabilidade | [`TRACEABILITY.md`](./TRACEABILITY.md) |
| estado comprovado | [`IMPLEMENTATION_STATUS.md`](./IMPLEMENTATION_STATUS.md) e `evidence/` |
| decisões | [`governance/DECISIONS.yaml`](./governance/DECISIONS.yaml) |
| fontes | [`governance/SOURCES.yaml`](./governance/SOURCES.yaml) |
| contexto mínimo | [`context/ROUTES.yaml`](./context/ROUTES.yaml) |

## Resolução de conflito

O agente deve identificar os IDs e as fontes concorrentes, consultar a rota aplicável e interromper qualquer promoção que exija uma autoridade ausente. A fonte histórica é preservada; a resolução é registrada como nova decisão, sem reescrever o passado.
