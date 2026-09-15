# ADR-001 — Arquitetura da primeira implementação

- Status: **APROVADA COM RISCOS para implementação incremental**; stack definitiva pendente na especificação canônica
- Data: 2026-09-13
- Escopo: estação local do treinador e primeiro fluxo funcional
- Resultado do gate INC-001 em 2026-09-14: **PASS WITH RISKS**

## Contexto

A especificação canônica mantém a stack definitiva da estação como decisão técnica pendente. O primeiro fluxo depende principalmente de reprodução de vídeo local, captura de timestamps, persistência, revisão, classificação manual e filtros/coleções.

## Direção técnica para implementação incremental

Estilo: monólito modular local-first.

- Interface: React + TypeScript.
- Ferramenta de desenvolvimento/build: Vite.
- Backend local: Python + FastAPI.
- Persistência inicial: SQLite.
- Mídia: arquivos locais associados a `VideoSource`.
- Inspeção de mídia: ffprobe.
- Derivados futuros: FFmpeg.
- Comunicação entre interface e backend: HTTP/JSON local.
- Cloud: nenhuma dependência no primeiro fluxo.
- Tauri/Electron: adiado.
- Portal: adiado.
- IA: adiada.

Vite é parte do desenvolvimento/build; a hipótese operacional é um processo local capaz de servir a API e o frontend compilado.

## Ingestão e YouTube

O núcleo inicial analisa arquivo local. A proveniência pode ser celular, câmera, arquivo recebido ou YouTube quando existir forma legítima e disponível de obtenção do arquivo.

YouTube não é dependência obrigatória do player inicial. O mecanismo operacional de aquisição de vídeos de terceiros continua pendente.

## Clip virtual

Marcação de lance registra `video_source + início + fim`. A marcação não cria automaticamente um novo MP4. FFmpeg passa a ser relevante quando houver necessidade de materialização de derivado.

## Gate de validação

A proposta arquitetural é testada no INC-001 com um MP4 real:

1. abrir o arquivo;
2. executar play/pause/seek;
3. capturar início pelo tempo corrente;
4. capturar fim;
5. persistir o intervalo;
6. encerrar a aplicação;
7. reabrir a aplicação;
8. selecionar o lance salvo;
9. rever o intervalo;
10. verificar preservação do original.

A exigência inicial é precisão temporal funcional para revisão do lance. Precisão frame a frame não está definida como requisito nesta decisão.

### Resultado observado — PASS WITH RISKS

O gate foi aplicado ao commit [`23336f7`](https://github.com/cepraea/analise-video/commit/23336f737e3ea3cccd8bfe62ef6dc1e83cfffa30), com [evidência consolidada](../evidence/INC-001.md). A [CI](https://github.com/cepraea/analise-video/actions/runs/34796462010) passou, mas não foi usada como substituto do teste com vídeo real. Os dez passos definidos acima foram observados para o arquivo testado:

| Passo | Observação |
| --- | --- |
| 1. Abrir arquivo | MP4 local H.264/AAC de `2182.055` s carregado no Chromium. |
| 2. Play/pause/seek | Reprodução, pausa, busca para frente e para trás e tempo corrente observados. |
| 3. Capturar início | `75.320` s (`75320` ms) capturados pela interface. |
| 4. Capturar fim | `84.210` s (`84210` ms); fim anterior ou igual foi recusado. |
| 5. Persistir | `POST /spike/intervals` retornou `201` e o registro apareceu no SQLite. |
| 6. Encerrar | Backend, frontend e navegador encerrados; portas locais liberadas. |
| 7. Reabrir | Novos processos e nova sessão do navegador iniciados. |
| 8. Selecionar registro | Intervalo 002 reapareceu e seu botão **REVER** foi acionado. |
| 9. Rever | Seek em `10.000` s, reprodução e pausa em `20.000` s. |
| 10. Preservar original | SHA-256 antes = depois; somente o MP4 original no diretório de mídia. |

| Risco remanescente | Consequência e verificação necessária |
| --- | --- |
| Um único MP4 e um navegador foram exercitados. | Compatibilidade, tempos de seek e experiência com outras fontes permanecem desconhecidos; repetir com arquivos representativos e avaliação direta de um treinador antes da aceitação operacional. |
| A revisão pausa por atualização do tempo corrente do player. | O fim é funcional, sem garantia frame a frame; medir a tolerância necessária e revisar o mecanismo se a correção de limites do INC-004 exigir maior precisão. |
| O frontend foi executado pelo Vite com proxy local. | O build passou, mas a hipótese de servir frontend compilado e API como estação operacional única ainda precisa de verificação antes de declarar a arquitetura final. |
| `spike_intervals` é um esquema descartável. | O teste não valida identidade e relações canônicas de `LANCE`/`VideoSource`; definir e testar essas entidades no INC-002. |

**PASS WITH RISKS** autoriza usar React, FastAPI e SQLite como base provisória do próximo incremento. Não valida o esquema de domínio, o empacotamento operacional nem a stack definitiva. Uma mudança substancial no fluxo de vídeo ou na arquitetura operacional exige reavaliar os riscos correspondentes.

### Reavaliação após extensão do player e do SQLite

Em 2026-09-14, o fluxo foi ampliado com confirmação explícita antes do salvamento, três níveis de seek, cinco velocidades, atalhos de operação, edição temporal com histórico e exclusão lógica auditável. O gate foi reaplicado ao commit [`ab82eef`](https://github.com/cepraea/analise-video/commit/ab82eef23dc48a7fbee9ce23ae132df15574f510), com [evidência consolidada](../evidence/INC-001-player-adjustments.md) e [CI aprovada](https://github.com/cepraea/analise-video/actions/runs/34873172548).

O operador exercitou o fluxo durante 30 marcações com o MP4 real, confirmou persistência de exclusões justificadas e editou o intervalo 030. Depois do reinício, o mesmo ID foi recuperado e revisto com os limites corrigidos; a versão anterior permaneceu no SQLite e o hash do original não mudou.

O resultado permanece **PASS WITH RISKS**. A extensão reforça a viabilidade da arquitetura local provisória, mas não remove os riscos de compatibilidade com outras mídias e navegadores, precisão perceptiva, empacotamento operacional ou schema experimental. A lista linear com dezenas de intervalos também evidencia a necessidade do catálogo previsto nos incrementos seguintes.

## Estado

O estado **INC-001 = VERIFIED** é sustentado pelo teste com MP4 real, persistência e revisão após reinício e hash preservado; a CI confirmou que a suíte completa e o build continuam passando. Não houve falha significativa observada de reprodução, seek, acesso local ou persistência no cenário testado. O gate recebeu **PASS WITH RISKS** e esta arquitetura está **APROVADA COM RISCOS** para orientar o INC-002. Os riscos da tabela não bloqueiam o próximo incremento, mas exigem as verificações indicadas antes da aceitação operacional ou de uma decisão de stack definitiva.

A aprovação é limitada ao caminho incremental testado. A especificação canônica ainda deixa a stack definitiva, arquivos grandes e a forma operacional da estação em aberto; o esquema `spike_intervals` e a distribuição não se tornam decisões canônicas por esta aprovação. Se for constatada uma falha significativa de vídeo, seek, acesso local, persistência ou experiência antes do INC-002, reclassificar o INC-001 como `BLOCKED` ou `IMPLEMENTED_NOT_VERIFIED`, retornar este ADR a `PROPOSTA A VALIDAR` e corrigir a arquitetura antes de avançar.
