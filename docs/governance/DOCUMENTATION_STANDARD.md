# Padrão de documentação

## Controle

| Campo | Valor |
| --- | --- |
| ID | `DOC-001` |
| Status | `DECIDIDO` |
| Autoridade | Davi Sermenho |
| Aprovado em | 2026-09-16 |
| Escopo | documentação canônica, governança, contexto, contratos e evidências |

## Princípio

Primeiro o domínio deve estar correto; depois o conteúdo recebe uma forma estruturada. Markdown é o hub documental e links, IDs e formatos nativos conectam os demais artefatos.

```text
intenção em linguagem natural controlada
→ conceitos e regras do domínio em Markdown
→ requisitos obrigatórios em EARS com IDs
→ arquitetura em MADR e diagramas textuais
→ contratos em formatos nativos
→ exemplos em Gherkin
→ implementação
→ testes e evidências rastreados
```

## Formatos por responsabilidade

| Formato | Uso autorizado |
| --- | --- |
| Markdown | índice, explicação, domínio, plano e visão humana |
| MADR/ADR | decisão arquitetural, alternativas e consequências |
| EARS | comportamento obrigatório do sistema |
| Mermaid | componentes, classes, ER, estados, sequências, atividades e relações arquiteturais |
| YAML | decisões, fontes, rotas, rastreabilidade, configuração e arquitetura como código |
| JSON | dados estruturados e saídas geradas para máquinas |
| OpenAPI | contrato HTTP quando uma API aprovada o exigir |
| Gherkin | exemplos concretos e critérios de aceitação quando agregarem precisão |
| SQL/schema nativo | contrato persistente executável |

Three Amigos pode ser usado para esclarecer exemplos complexos, sem obrigação cerimonial. ANMS/ANPS/ANGS não são adotados como framework; apenas práticas documentais aprovadas podem ser aproveitadas.

## EARS

Usar EARS quando um comportamento obrigatório for declarado. Os cinco padrões fundamentais são:

```text
O sistema deverá...
Quando ..., o sistema deverá...
Enquanto ..., o sistema deverá...
Se ..., então o sistema deverá...
Onde ..., o sistema deverá...
```

EARS não corrige uma definição de domínio incorreta ou incompleta. Requisitos mantêm IDs `RF-*` e `RNF-*` já existentes.

## Markdown

- manter uma linha em branco antes e depois de cada título;
- manter uma linha em branco antes de listas com `-`;
- usar hierarquia de títulos sem saltos injustificados;
- preferir links relativos entre documentos versionados;
- evitar duplicar definições canônicas; referenciar o ID e o documento responsável;
- declarar status, autoridade, escopo e proveniência quando o documento tiver efeito normativo.

## Nomes e localização

- documentos canônicos de topo usam `UPPER_SNAKE_CASE.md`;
- ADRs usam `ADR-NNN-slug-kebab-case.md`;
- diretórios e documentos auxiliares usam `kebab-case` ASCII;
- scripts usam `snake_case` e extensão nativa;
- novos caminhos canônicos não usam espaços, acentos ou nomes ambíguos;
- o caminho expressa responsabilidade, não a ferramenta que criou o arquivo;
- arquivos originais promovidos conservam o caminho lógico no manifesto, mesmo que seus bytes sejam guardados por hash.

## Tamanho e contexto

Não existe limite universal de linhas, caracteres ou tokens por arquivo. O tamanho é controlado pela responsabilidade e pelo roteamento:

- C0 deve ser curto e estável;
- índices apontam para detalhes em vez de copiá-los;
- documentos são divididos quando misturam autoridades ou motivos de mudança diferentes;
- pacotes são gerados com dependências transitivamente necessárias;
- métricas de tamanho são alertas do piloto, não critérios automáticos de verdade.

## Fontes, derivados e evidências

- originais são imutáveis;
- derivados ficam separados e registram a fonte;
- `.local/drafts/` não é SSOT;
- `archive/` não entra nas buscas normais nem nos pacotes de contexto;
- artefatos gerados são reconstruíveis e não recebem autoridade adicional;
- os oito artefatos de controle do G0 são preservados, mas não podem sustentar afirmações do produto;
- uma revisão publicada nunca é sobrescrita; toda mudança produz uma revisão sucessora.

## Baselines e armazenamento por conteúdo

- cada baseline tem ID, data, commit, manifesto, hashes e estado de completude;
- objetos são armazenados por SHA-256 em `archive/ssot/objects/sha256/`;
- um objeto existente nunca é alterado; colisão de caminho com bytes diferentes é erro fatal;
- o manifesto liga caminho lógico, classificação e hash;
- binários grandes devem usar Git LFS quando o ambiente do repositório o disponibilizar;
- a ausência de Git LFS não autoriza perda de evidência nem sobrescrita.

## Validação

Validadores estruturais podem verificar sintaxe, IDs, referências, caminhos, hashes e estados. Eles não aprovam significado esportivo nem transformam uma proposta em decisão.
