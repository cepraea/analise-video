# TRACEABILITY.md — Matriz inicial

Na criação deste registro, nenhum requisito funcional está comprovadamente implementado.

Estados usados: `NOT_IMPLEMENTED`, `IMPLEMENTED_NOT_VERIFIED`, `VERIFIED`, `BLOCKED`.

| Requisito / critério | Incremento | Evidência esperada | Estado |
|---|---|---|---|
| RF-001 cadastrar competição | INC-002 | persistência e recuperação | NOT_IMPLEMENTED |
| RF-002 cadastrar jogo | INC-002 | persistência + vínculo à competição | NOT_IMPLEMENTED |
| RF-003 múltiplas fontes por jogo | INC-002 | estrutura aceita N fontes | NOT_IMPLEMENTED |
| RF-005 arquivo local | INC-001/002 | MP4 real aberto/referenciado | NOT_IMPLEMENTED |
| RF-007 reproduzir fonte | INC-001 | play/pause/seek | NOT_IMPLEMENTED |
| RF-008 capturar início | INC-001 | tempo corrente persistido | NOT_IMPLEMENTED |
| RF-009 capturar fim | INC-001 | `start < end` + persistência | NOT_IMPLEMENTED |
| RF-010 equipe com posse | INC-003 | salvar e reabrir posse | NOT_IMPLEMENTED |
| RF-011 equipe analisada | INC-003 | registro independente da posse | NOT_IMPLEMENTED |
| RF-012 segmentos de fase | INC-003 | múltiplos segmentos por lance | NOT_IMPLEMENTED |
| RF-013 corrigir limites | INC-004 | editar/rever novo intervalo | NOT_IMPLEMENTED |
| RF-016 múltiplas atletas | INC-005 | duas atletas no mesmo lance | NOT_IMPLEMENTED |
| RF-017 múltiplas ações | INC-005 | várias ações sem duplicar lance | NOT_IMPLEMENTED |
| RF-018 resultado da ação | INC-005 | resultado factual persistido | NOT_IMPLEMENTED |
| RF-019 comentário | INC-005 | persistir/reabrir comentário | NOT_IMPLEMENTED |
| RF-023 coleções por filtros | INC-006/007 | filtro → coleção | NOT_IMPLEMENTED |
| RF-024 clip virtual | INC-001/004/007 | fonte + início/fim reproduzível | NOT_IMPLEMENTED |
| RF-030 original imutável | INC-001→007 | evidência técnica de não alteração | NOT_IMPLEMENTED |
| RF-031 reclassificar sem recorte | INC-004/007 | metadado muda sem alterar mídia | NOT_IMPLEMENTED |
| CA-001 marcar lance local | INC-001 | demonstração com vídeo real | NOT_IMPLEMENTED |
| CA-003 duas atletas/ações | INC-005 | teste de relação | NOT_IMPLEMENTED |
| CA-005 reclassificar sem recortar | INC-004 | mídia preservada | NOT_IMPLEMENTED |
| CA-006 histórico por atleta | INC-006 | filtro + ordenação | NOT_IMPLEMENTED |
| CA-008 um lance em contextos distintos | INC-007 | duas coleções, um lance canônico | NOT_IMPLEMENTED |
| RNF-002 rastreabilidade | INC-002→007 | IDs estáveis fonte/jogo/lance | NOT_IMPLEMENTED |
| RNF-003 sem duplicação física | INC-004/007 | coleções referenciam lances | NOT_IMPLEMENTED |
| RNF-004 taxonomia evolutiva | INC-003/005 | estrutura extensível | NOT_IMPLEMENTED |
| RNF-005 original imutável | INC-001→007 | verificação de preservação | NOT_IMPLEMENTED |
| RNF-006 sem API paga | INC-000→007 | execução sem chave paga | NOT_IMPLEMENTED |
| RNF-007 operável por treinador | gate INC-007 | validação prática | NOT_IMPLEMENTED |
| RNF-008 recuperação por metadados | INC-006 | filtros testados | NOT_IMPLEMENTED |
| RNF-009 cronologia | INC-006/007 | ordenação testada | NOT_IMPLEMENTED |
| RNF-011 não depender de YouTube | INC-001 | fluxo por arquivo local | NOT_IMPLEMENTED |
| RNF-012 sem conexão contínua | INC-001→007 | uso local após mídia disponível | NOT_IMPLEMENTED |

## Preservados fora do gate atual

URL/YouTube, multicâmera/sincronização, destinos avançados individual/goleira/coletivo, clipes físicos/renderização, portal e IA/análise avançada permanecem fora de INC-000→INC-007. A arquitetura inicial não deve inviabilizá-los.

## Atualização

`VERIFIED` pressupõe evidência observável, não apenas existência de código. O registro futuro deve apontar para teste, comando, commit/PR ou outra evidência reproduzível.
