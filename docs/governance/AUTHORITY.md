# Autoridade documental

## Regra geral

A autoridade pertence ao conteúdo e à pessoa ou ao processo que pode aprová-lo. Formato, ferramenta, localização ou geração por IA não criam autoridade.

## Matriz de autoridade

| Classe | Fonte canônica | Autoridade |
| --- | --- | --- |
| significado esportivo CEPRAEA | `docs/GAME_MODEL.md` | Davi Sermenho |
| requisitos do produto | `docs/SYSTEM_SPEC.md` | Davi Sermenho, com rastreabilidade à origem |
| arquitetura | ADR com status explícito em `docs/architecture/` | decisão registrada pela autoridade indicada na ADR |
| ordem de implementação | `docs/IMPLEMENTATION_PLAN.md` | planejamento aprovado por Davi Sermenho |
| estado comprovado | `docs/IMPLEMENTATION_STATUS.md`, testes e evidências | evidência reproduzível; código isolado não basta |
| decisões | `docs/governance/DECISIONS.yaml` | autoridade registrada em cada decisão |
| fontes | `docs/governance/SOURCES.yaml` e baselines | proveniência; uma fonte não se torna decisão por existir |

## Limites

- Davi Sermenho é a autoridade final sobre o significado esportivo do modelo CEPRAEA.
- Agentes, NotebookLM e outros sistemas de IA podem sintetizar e apontar conflitos, mas não aprovam decisões.
- Arquivos em `.local/drafts/` são insumos de migração, não SSOT.
- Artefatos de controle operacional comprovam processo; não definem o produto.
- Fontes originais e referências de proveniência não são apagadas durante a promoção.

## Conflitos

Quando duas fontes elegíveis divergem, o item permanece `PENDENTE` ou `BLOCKED` até decisão da autoridade competente. O agente deve registrar o conflito e não escolher silenciosamente uma interpretação.
