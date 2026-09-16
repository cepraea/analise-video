# Estados controlados

## Estado de decisão e documento

| Estado | Significado | Transição mínima |
| --- | --- | --- |
| `DECIDIDO` | autoridade competente aprovou o conteúdo | autoridade, data, declaração e proveniência registradas |
| `DECIDIDO PARCIALMENTE` | parte delimitada foi aprovada | partes decididas e pendentes identificadas |
| `MODELAGEM ATUAL` | representação vigente, sujeita a confirmação | origem e limites explícitos |
| `PROPOSTA TÉCNICA` | alternativa técnica ainda não aprovada | responsável e critério de decisão identificados |
| `PROPOSTA A VALIDAR` | conteúdo aguarda validação da autoridade | autoridade e pergunta de validação identificadas |
| `PENDENTE` | informação ou decisão necessária está ausente | lacuna e responsável identificados |
| `FORA DO ESCOPO INICIAL` | item reconhecido, mas excluído do primeiro fluxo | limite de escopo registrado |

## Estado de implementação

| Estado | Significado | Evidência exigida |
| --- | --- | --- |
| `NOT_IMPLEMENTED` | comportamento não foi implementado | nenhuma evidência de execução aceita |
| `IMPLEMENTED_NOT_VERIFIED` | há código, mas falta comprovação suficiente | referência ao código e lacuna de teste/evidência |
| `VERIFIED` | comportamento foi comprovado | teste ou procedimento reproduzível e evidência correspondente |
| `BLOCKED` | progresso depende de condição externa ou decisão | bloqueio, responsável e condição de saída |

## Completude de baseline

Esta dimensão não substitui estados de implementação:

| Estado | Significado |
| --- | --- |
| `COMPLETE` | manifesto, hashes e bytes de todos os itens estão preservados |
| `HASH_ONLY_PARTIAL` | o manifesto e os hashes existem, mas ao menos um byte histórico não pôde ser recuperado |

Nenhum estado pode ser promovido apenas por inferência do agente. Mudanças exigem evidência ou aprovação compatível com a matriz de autoridade.
