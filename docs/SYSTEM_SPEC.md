# SYSTEM_SPEC.md — Snapshot de desenvolvimento

## Proveniência

- Fonte canônica: `CEPRAEA — Sistema de Análise de Vídeo — Especificação Canônica v0.1`
- Google Drive ID: `1bC1-BEMV06iQ23JUJoJadYdJJ1TJYFXLsmNINHkT2Ck`
- Revisão lida: `ANLCKQl-87kz-xfubUzkOifKKDKR0OUgDLDLP7BYcQAPPVHJ_742zWVhOkHjaPAyziATwU_KW_Bmj6kGEvg8ynTZ15bg37HRcmOjj3gLj9s`
- Data da extração: 2026-09-13
- Natureza: snapshot derivado para desenvolvimento; a fonte no Google Drive permanece canônica.

## Primeiro fluxo funcional

`ABRIR VÍDEO → MARCAR LANCE → CAPTURAR TEMPOS AUTOMATICAMENTE → CLASSIFICAR POSSE/FASE → SALVAR → REVER LANCES → CLASSIFICAR AÇÕES/ATLETAS → FILTRAR POR ATLETA → GERAR UMA COLEÇÃO`

Esse fluxo não depende de clipe físico, portal ou classificação automática por IA.

## Modelo mínimo

- `LANCE` é a unidade canônica; vídeo é fonte.
- O vídeo original é imutável.
- Atleta, fase, ação, resultado, comentário, competição, jogo e perspectiva são metadados relacionados ao lance.
- Um lance pode se relacionar a várias atletas, ações, coleções e fontes.
- Timestamps, fonte, jogo e participantes permanecem separados de interpretação e feedback.
- Pastas podem existir como visões ou exportações, mas não são a base lógica do sistema.
- Taxonomias ainda abertas precisam permanecer extensíveis.

## Entidades necessárias ao fluxo inicial

`COMPETIÇÃO`, `JOGO`, `FONTE_DE_VIDEO`, `LANCE`, `SEGMENTO_DE_FASE`, `ATLETA`, `PARTICIPACAO_NO_LANCE`, `ACAO` e `COLECAO`.

## Requisitos associados

RF-001, RF-002, RF-003, RF-005, RF-007, RF-008, RF-009, RF-010, RF-011, RF-012, RF-013, RF-016, RF-017, RF-018, RF-019, RF-023, RF-024, RF-030 e RF-031.

## Critérios especialmente relevantes

- `CA-001`: vídeo local aberto, início/fim capturados sem digitação manual e lance salvo.
- `CA-003`: duas atletas podem possuir ações diferentes no mesmo lance sem duplicar a identidade do lance.
- `CA-005`: reclassificação não exige novo recorte do original.
- `CA-006`: lances de uma atleta podem ser recuperados cronologicamente com metadados.
- `CA-008`: um mesmo lance pode aparecer em diferentes contextos/coleções mantendo identidade única.

## Clip virtual

A primeira representação de um trecho é `fonte + tempo inicial + tempo final`. A criação imediata de um novo MP4 não é necessária.

## Restrições não funcionais relevantes

O fluxo inicial deve minimizar trabalho manual, preservar rastreabilidade e original, evitar duplicação física desnecessária, funcionar sem API paga de inferência, permitir operação local sem conexão contínua e manter taxonomias evolutivas.

## Fora do gate inicial

Clipes físicos, feedback renderizado, portal, IA, reconhecimento frame a frame e sincronização multicâmera avançada não bloqueiam o primeiro fluxo.

## Estado técnico

A stack definitiva da estação, banco local definitivo, backup, tratamento operacional de YouTube, arquivos grandes e tecnologias de portal/renderização continuam tecnicamente abertos na fonte canônica.
