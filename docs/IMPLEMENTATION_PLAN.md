# IMPLEMENTATION_PLAN.md — INC-000 a INC-007

## Objetivo

Construir somente o primeiro fluxo funcional canônico em incrementos pequenos, verificáveis e reversíveis.

Gate final: `ABRIR VÍDEO → MARCAR LANCE → CAPTURAR TEMPOS → CLASSIFICAR POSSE/FASE → SALVAR → REVER → CLASSIFICAR AÇÕES/ATLETAS → FILTRAR → GERAR COLEÇÃO`.

Portal, IA, renderização, multicâmera avançada e clipe físico não pertencem a este gate.

Todos os incrementos começam como `NOT_IMPLEMENTED`.

## INC-000 — Fundação executável

Resultado esperado: estrutura mínima reproduzível para desenvolvimento e testes, sem comportamento esportivo novo.

Inclui estrutura de frontend/backend compatível com a hipótese do ADR-001, comandos de desenvolvimento/teste, configuração local sem segredo pago obrigatório, diretórios de dados fora do versionamento e um teste mínimo de inicialização.

Aceitação: ambiente inicia de maneira documentada e a suíte mínima de teste executa de forma reproduzível.

## INC-001 — Architecture Spike: vídeo local → intervalo persistido → revisão

Objetivo: testar ADR-001 antes de aprofundar o domínio.

Requisitos associados: RF-005, RF-007, RF-008, RF-009, parte de RF-013, RF-024 e RF-030.

Fluxo de validação: abrir MP4 local; play/pause/seek; capturar início; capturar fim; validar `start < end`; persistir; fechar e reabrir; rever o intervalo salvo.

Aceitação: demonstração com vídeo real, persistência após reinício e original inalterado.

## INC-002 — Catálogo mínimo

Objetivo: representar Competition, Game, VideoSource e Lance/TemporalReference sem dados hardcoded.

Requisitos: RF-001, RF-002, RF-003 em estrutura, RF-005, RF-013 e RF-030.

Invariantes: identidade de lance independente de nome de arquivo; original imutável; uma fonte possui identidade própria; desenho admite múltiplas fontes futuras.

Aceitação: jogo/fonte/lance persistem e o lance mantém rastreabilidade até sua fonte depois do reinício.

## INC-003 — Posse e segmentos de fase

Objetivo: registrar manualmente posse, equipe analisada e fase.

Requisitos: RF-010, RF-011 e RF-012.

Contexto esportivo: fases e fronteiras de `docs/GAME_MODEL.md`.

Valores mínimos: Transição Ofensiva, Ataque Posicionado, Transição Defensiva e Defesa Posicionada.

Invariantes: `equipe_com_posse` e `equipe_analisada` são independentes; um lance pode conter múltiplos segmentos; fases de equipes diferentes podem se sobrepor; o sistema não inventa classificação automática.

Aceitação: um lance registra, por exemplo, Transição Ofensiva → Ataque Posicionado para uma equipe, preservando classificações independentes.

## INC-004 — Revisão e correção de lances

Objetivo: tornar a segmentação utilizável na segunda passagem.

Requisitos: RF-013, RF-024 e RF-031.

Capacidades: listar lances; abrir diretamente o intervalo; rever; corrigir início/fim; alterar posse/fase sem gerar MP4; persistir as correções.

Aceitação: classificação pode mudar sem alterar o original nem criar novo arquivo físico.

## INC-005 — Atletas, participações, ações e comentários

Objetivo: suportar a análise individual mínima.

Requisitos: RF-016, RF-017, RF-018 e RF-019; sustenta CA-003.

Invariantes: várias atletas no mesmo lance; várias ações por atleta; taxonomias de ações/resultados permanecem extensíveis; resultado factual separado de avaliação técnico-tática.

Aceitação: duas atletas com ações distintas são associadas ao mesmo lance sem duplicação do lance.

## INC-006 — Recuperação e filtros

Objetivo: localizar lances pelo catálogo em vez de procurar manualmente em vídeos longos.

Filtros mínimos: atleta, fase, ação, competição e jogo.

Requisitos relacionados: RNF-008, RNF-009, base de RF-023 e CA-006.

Aceitação: seleção de uma atleta retorna seus lances em ordem cronológica com os metadados registrados e acesso direto à revisão.

## INC-007 — Coleções e gate do primeiro fluxo

Objetivo: completar o percurso ponta a ponta.

Requisitos: RF-023; preserva RF-031; sustenta CA-008.

Capacidades: criar coleção por filtro/curadoria; manter uma única identidade de lance em várias coleções; ordenar/revisar coleção; reproduzir clip virtual; nenhum MP4 novo obrigatório.

Gate: com vídeo real, Davi consegue abrir fonte, segmentar e capturar tempos, registrar posse/fase, salvar/reabrir, rever/corrigir, associar atletas/ações, filtrar por atleta e gerar/rever uma coleção.

Somente após evidência desse gate `FIRST_FUNCTIONAL_FLOW` pode mudar para `VERIFIED`.

## Depois de INC-007

A ordem seguinte é reavaliada com a experiência real do primeiro fluxo. Candidatos posteriores incluem clipes físicos/FFmpeg, micro-eventos/análise avançada, goleiras, feedback renderizado, portal e IA assistiva.
