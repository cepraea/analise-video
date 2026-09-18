# Registro de decisões

> Visão gerada de `DECISIONS.yaml`. Nenhuma decisão exclusiva deve ser registrada aqui.

| ID | Status | Data | Autoridade | Decisão |
| --- | --- | --- | --- | --- |
| `DOC-001` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | DOCUMENTATION_STANDARD.md é o padrão normativo para organizar, escrever, versionar e validar a documentação do projeto. |
| `DOC-002` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Os prefixos RF e RNF são preservados. As siglas FR e NFR não devem ser introduzidas sem decisão explícita de migração de IDs. |
| `DOC-003` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | O modelo C4 em YAML é a fonte estruturada e canônica dos elementos arquiteturais e relações. Vistas Mermaid são derivadas e devem ser geradas ou validadas contra o modelo YAML. |
| `DOC-004` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | OpenAPI é o contrato canônico da API HTTP. Gherkin fornece exemplos concretos e critérios de aceitação rastreados aos requisitos. Nenhum deles substitui requisitos de produto nem regras de domínio. |
| `DOC-005` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Three Amigos é aplicado somente quando ambiguidade entre domínio, implementação e verificação justificar a colaboração. Não é cerimônia obrigatória para toda alteração. |
| `GOV-001` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | O projeto adota uma SSOT federada por responsabilidade, com registro central de decisões e fontes, rotas de contexto e evidência versionada. |
| `GOV-002` | `PENDENTE` | — | Davi Sermenho | Pendente (G4/piloto): o Git se torna a autoridade operacional completa do software após a migração validada (G11)? Recomendação técnica — sim, somente após a conclusão do G11. |
| `GOV-003` | `PENDENTE` | — | Davi Sermenho | Pendente (G4/piloto): o Google Drive continua como ambiente de conhecimento esportivo amplo após a migração? Recomendação técnica — sim, com promoção controlada para GAME_MODEL.md. |
| `GOV-004` | `PENDENTE` | — | Davi Sermenho | Pendente (G4/piloto): o NotebookLM permanece disponível para pesquisa e auditoria não normativa? Recomendação técnica — sim, opcional e sem autoridade normativa (ver GOV-NLM-001). |
| `GOV-005` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Rascunhos em .local/drafts/ e históricos em .local/ são fontes imutáveis de migração, não documentação canônica operacional. Uma afirmação contida em rascunho só é promovida após confirmação de sua fonte ou ratificação de Davi. |
| `GOV-006` | `PENDENTE` | — | Davi Sermenho | Pendente: a migração documental completa bloqueia o INC-002? Recomendação técnica — bloquear apenas mudanças de esquema dependentes de requisitos ainda conflitantes. |
| `GOV-007` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | O projeto adota quatro vocabulários de estado independentes — estado do documento, estado da decisão, estado de verificação da afirmação e estado de implementação — conforme definidos em STATES.md. |
| `GOV-NLM-001` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | O NotebookLM não possui autoridade normativa. Seus resultados são hipóteses ou sínteses que precisam ser verificadas na fonte antes de entrar na SSOT. Agentes de código não devem depender do NotebookLM para executar incrementos. |
| `GOV-SRC-001` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Um baseline publicado nunca é sobrescrito; qualquer mudança produz uma revisão sucessora com manifesto e hashes próprios. |
| `GOV-SRC-002` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Os oito arquivos de controle do G0 são integralmente preservados e rastreados como controle operacional, sem autoridade para definir o produto. |
| `ID-001` | `PENDENTE` | — | Davi Sermenho | Pendente (G5): preservar os IDs RF-001 a RF-052 da baseline mais completa, corrigindo por sucessão, nunca por reutilização silenciosa? Recomendação técnica — sim. |
| `ID-002` | `PENDENTE` | — | Davi Sermenho | Pendente (G7): como tratar os namespaces RFP e CAP da especificação da prancheta? Recomendação técnica — manter namespace modular até decisão de incorporação; mapear sem renumerar automaticamente. |
| `INFRA-001` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Nenhuma API paga é dependência obrigatória do primeiro fluxo funcional. A arquitetura utiliza Claude Pro e ChatGPT Plus (assinaturas fixas) como ferramentas de IA, sem chamadas pagas adicionais por uso. |
| `INV-001` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Davi Sermenho é a única autoridade sobre o significado esportivo do modelo CEPRAEA. Nenhuma decisão de classificação ou interpretação esportiva pode ser delegada a agentes de IA ou inferida automaticamente. |
| `INV-002` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | LANCE é a unidade canônica do modelo de dados. O vídeo é a fonte primária da qual os lances são extraídos e identificados. |
| `INV-003` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Arquivos de vídeo e demais fontes originais são imutáveis. Derivados e anotações permanecem em estruturas separadas dos originais, que nunca são modificados. |
| `INV-004` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Fatos observáveis e timestamps permanecem em estruturas separadas de interpretações, classificações e feedback. Essas dimensões nunca são misturadas em um único campo. |
| `INV-005` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Um lance pode possuir várias atletas, várias ações, várias coleções e várias fontes associadas simultaneamente. |
| `INV-006` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | As fases de cada equipe em um lance são independentes entre si e devem ser modeladas e registradas separadamente. |
| `INV-007` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Taxonomias esportivas em aberto permanecem extensíveis. Nenhum valor de classificação em estado pendente ou parcial é tratado como conjunto fechado. |
| `INV-008` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | T3 (ataque instalado / ataque posicionado) exige instalação ofensiva completa e ausência de vantagem herdada predominante. Instalação incompleta redireciona para T1 (transição direta); vantagem herdada predominante redireciona para T2 (transição indireta). |
| `INV-009` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | Código existente, sozinho, não comprova funcionalidade. O estado VERIFIED só pode ser atribuído quando existe evidência reproduzível correspondente (testes passando e registros de evidência referenciados). |
| `PROD-001` | `PENDENTE` | — | Davi Sermenho | Pendente (G7): o produto é somente análise de vídeo ou inclui o cockpit completo de competição (prancheta, portal, assistência por IA, cockpit)? Define o escopo dos módulos a promover. |
| `TECH-001` | `DECIDIDO` | 2026-09-16 | Davi Sermenho | A ADR-001 (monólito modular local-first: React/TypeScript/Vite, FastAPI/Python, SQLite, mídia local, HTTP/JSON) continua sendo a autoridade de arquitetura para o INC-002 até ser substituída por uma ADR aprovada. Propostas de cloud, PWA, serviço gerenciado ou visão computacional permanecem em ADR candidata separada. |
| `TECH-002` | `DECIDIDO` | 2026-09-17 | Davi Sermenho | O projeto adota um grafo local de código para Python, JavaScript e TypeScript, com hashes do corpus e dos extratores, consulta limitada por módulo ou símbolo e conferência dos bytes do índice quando o corpus, a configuração ou um extrator mudar. Vistas são derivadas sob demanda, sem staging automático, API paga ou substituição do modelo C4 canônico. |

Fonte canônica: [`DECISIONS.yaml`](./DECISIONS.yaml).
