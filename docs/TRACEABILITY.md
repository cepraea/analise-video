# TRACEABILITY.md — Matriz inicial

O `INC-000 — Fundação executável` está `VERIFIED`, mas nenhum requisito funcional do fluxo de análise de vídeo foi promovido a implementado por causa disso.

Estados usados: `NOT_IMPLEMENTED`, `IMPLEMENTED_NOT_VERIFIED`, `VERIFIED`, `BLOCKED`.

## Gates de incremento

| Gate | Evidência | Estado |
|---|---|---|
| INC-000 — fundação instala, testa e compila em ambiente limpo | `docs/evidence/INC-000.md`; GitHub Actions run `34782679938` | VERIFIED |
| INC-001 — vídeo local → intervalo persistido → revisão | `docs/evidence/INC-001.md` (consolidada) e registros detalhados em `docs/evidence/INC-001-*.md` | VERIFIED |
| FIRST_FUNCTIONAL_FLOW | demonstração ponta a ponta definida em `IMPLEMENTATION_PLAN.md` | NOT_IMPLEMENTED |

## Requisitos e critérios do produto

| Requisito / critério | Incremento | Evidência esperada | Estado |
|---|---|---|---|
| RF-001 cadastrar competição | INC-002 | persistência e recuperação | NOT_IMPLEMENTED |
| RF-002 cadastrar jogo | INC-002 | persistência + vínculo à competição | NOT_IMPLEMENTED |
| RF-003 múltiplas fontes por jogo | INC-002 | estrutura aceita N fontes | NOT_IMPLEMENTED |
| RF-005 arquivo local | INC-001/002 | MP4 real aberto/referenciado; `docs/evidence/INC-001-player.md` | VERIFIED |
| RF-007 reproduzir fonte | INC-001 | play/pause/seek; `docs/evidence/INC-001-player.md` | VERIFIED |
| RF-008 capturar início | INC-001 | tempo corrente persistido pela interface; `docs/evidence/INC-001-save.md` | VERIFIED |
| RF-009 capturar fim | INC-001 | `start < end` + persistência; `docs/evidence/INC-001-save.md` | VERIFIED |
| RF-010 equipe com posse | INC-003 | salvar e reabrir posse | NOT_IMPLEMENTED |
| RF-011 equipe analisada | INC-003 | registro independente da posse | NOT_IMPLEMENTED |
| RF-012 segmentos de fase | INC-003 | múltiplos segmentos por lance | NOT_IMPLEMENTED |
| RF-013 corrigir limites | INC-004 | editar/rever novo intervalo | NOT_IMPLEMENTED |
| RF-016 múltiplas atletas | INC-005 | duas atletas no mesmo lance | NOT_IMPLEMENTED |
| RF-017 múltiplas ações | INC-005 | várias ações sem duplicar lance | NOT_IMPLEMENTED |
| RF-018 resultado da ação | INC-005 | resultado factual persistido | NOT_IMPLEMENTED |
| RF-019 comentário | INC-005 | persistir/reabrir comentário | NOT_IMPLEMENTED |
| RF-023 coleções por filtros | INC-006/007 | filtro → coleção | NOT_IMPLEMENTED |
| RF-024 clip virtual | INC-001/004/007 | fonte + início/fim salvos e revistos sem recorte no INC-001; `docs/evidence/INC-001-review.md`; demais incrementos pendentes | IMPLEMENTED_NOT_VERIFIED |
| RF-030 original imutável | INC-001→007 | SHA-256 antes = depois e `sha256sum --check: OK` no INC-001; `docs/evidence/INC-001-original-integrity.md`; demais incrementos pendentes | IMPLEMENTED_NOT_VERIFIED |
| RF-031 reclassificar sem recorte | INC-004/007 | metadado muda sem alterar mídia | NOT_IMPLEMENTED |
| CA-001 marcar lance local | INC-001 | marcação salva com vídeo real; `docs/evidence/INC-001-save.md` | VERIFIED |
| CA-003 duas atletas/ações | INC-005 | teste de relação | NOT_IMPLEMENTED |
| CA-005 reclassificar sem recortar | INC-004 | mídia preservada | NOT_IMPLEMENTED |
| CA-006 histórico por atleta | INC-006 | filtro + ordenação | NOT_IMPLEMENTED |
| CA-008 um lance em contextos distintos | INC-007 | duas coleções, um lance canônico | NOT_IMPLEMENTED |
| RNF-002 rastreabilidade | INC-002→007 | IDs estáveis fonte/jogo/lance | NOT_IMPLEMENTED |
| RNF-003 sem duplicação física | INC-004/007 | coleções referenciam lances | NOT_IMPLEMENTED |
| RNF-004 taxonomia evolutiva | INC-003/005 | estrutura extensível | NOT_IMPLEMENTED |
| RNF-005 original imutável | INC-001→007 | SHA-256 antes = depois e `sha256sum --check: OK` no INC-001; `docs/evidence/INC-001-original-integrity.md`; demais incrementos pendentes | IMPLEMENTED_NOT_VERIFIED |
| RNF-006 sem API paga | INC-000→007 | execução sem chave paga em cada incremento | IMPLEMENTED_NOT_VERIFIED |
| RNF-007 operável por treinador | gate INC-007 | validação prática | NOT_IMPLEMENTED |
| RNF-008 recuperação por metadados | INC-006 | filtros testados | NOT_IMPLEMENTED |
| RNF-009 cronologia | INC-006/007 | ordenação testada | NOT_IMPLEMENTED |
| RNF-011 não depender de YouTube | INC-001 | fluxo completo por arquivo local, sem URL externa; `docs/evidence/INC-001-review.md` | VERIFIED |
| RNF-012 sem conexão contínua | INC-001→007 | uso local após mídia disponível | NOT_IMPLEMENTED |

### Nota sobre RNF-006

O INC-000 foi verificado sem chave paga, cloud ou segredo obrigatório. O requisito permanece `IMPLEMENTED_NOT_VERIFIED` no escopo INC-000→007 porque deve continuar verdadeiro nos incrementos seguintes; não é promovido globalmente a `VERIFIED` antes do gate do primeiro fluxo.

## Preservados fora do gate atual

URL/YouTube, multicâmera/sincronização, destinos avançados individual/goleira/coletivo, clipes físicos/renderização, portal e IA/análise avançada permanecem fora de INC-000→INC-007. A arquitetura inicial não deve inviabilizá-los.

## Atualização

`VERIFIED` pressupõe evidência observável, não apenas existência de código. Cada promoção de estado deve apontar para teste, workflow, commit/PR ou outra evidência reproduzível.
