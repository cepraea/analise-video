# ADR-002 — SSOT federada e contexto mínimo

## Controle

| Campo | Valor |
| --- | --- |
| Status | `DECIDIDO` |
| Autoridade | Davi Sermenho |
| Data | 2026-09-16 |
| Decisão relacionada | `GOV-001` |

## Contexto

O conhecimento do sistema estava distribuído entre documentos versionados, drafts, históricos, fontes remotas, sínteses de IA e protótipos. Um arquivo único aumentaria custo de contexto e acoplamento editorial; fragmentação sem índice aumentaria omissões e divergências; correções pontuais manteriam a falta de linhagem.

## Decisão

Adotar uma arquitetura híbrida com:

- SSOT federada por responsabilidade;
- `DECISIONS.yaml` e `SOURCES.yaml` como registros centrais legíveis por máquina;
- `SSOT.md` como índice humano de precedência;
- rotas por tipo de tarefa em `ROUTES.yaml`;
- IDs estáveis e rastreabilidade entre fonte, decisão, requisito, implementação, teste e evidência;
- baselines imutáveis com manifestos e objetos endereçados por SHA-256;
- drafts e `archive/` excluídos do contexto operacional normal;
- pacotes de incremento gerados somente com dependências necessárias.

O Git privado é o repositório operacional desses artefatos versionados. Esta ADR não realiza o cutover definitivo das fontes remotas: Google Drive pode continuar como fonte ampla até a promoção controlada e a aprovação previstas no plano. NotebookLM permanece consultivo e não é autoridade.

Os oito artefatos de controle do G0 são preservados e rastreados, mas ficam fora do catálogo de fontes capazes de definir produto ou domínio.

## Não decisões

Esta ADR não adota MCP, Atlan, banco vetorial, grafo AST, hooks Git, Lore Protocol, C4/YAML ou geração de imagens como dependências do contexto mínimo. Cada item exige necessidade mensurada e decisão própria quando afetar a arquitetura.

Evolução posterior: `DOC-003`, aprovada em 2026-09-16, adotou o modelo C4 em YAML como fonte arquitetural canônica e vistas Mermaid como derivados. Essa decisão posterior substitui somente a não adoção de C4/YAML registrada aqui; não adota grafo AST, hooks, Lore, MCP, Atlan ou geração de imagens.

Evolução posterior: `TECH-002`, aprovada em 2026-09-17, adotou o grafo local de código endereçado pelos hashes do corpus e dos extratores, com conferência pertinente do índice e vistas Mermaid sob demanda. O grafo descreve código observado e permanece separado do modelo C4 canônico. A decisão não adota MCP, Atlan, API paga, PDF obrigatório ou staging automático.

## Alternativas consideradas

### Arquivo único

Rejeitado porque amplia contexto irrelevante, conflitos de edição e atenção diluída.

### Fragmentação sem registro central

Rejeitada porque não resolve precedência, descoberta, linhagem nem conflitos.

### Estrutura atual com correções pontuais

Rejeitada porque preserva IDs divergentes, lacunas e ausência de rastreabilidade.

## Consequências

### Positivas

- contexto menor por tarefa;
- autoridade explícita;
- promoção auditável;
- redução de duplicação normativa;
- baselines e decisões historicamente recuperáveis.

### Custos e riscos

- geradores e validadores precisam ser mantidos;
- rotas desatualizadas podem omitir contexto;
- a migração exige reconciliação antes do cutover;
- armazenamento de binários precisa de política de tamanho e, quando disponível, Git LFS.

## Verificação

A decisão é considerada materializada quando os documentos de governança existem, `ROUTES.yaml` é validado, G0 e seu sucessor são publicados separadamente e o plano registra a aprovação.
