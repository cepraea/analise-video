# Política de contexto mínimo

## Objetivo

Carregar o mínimo suficiente para cumprir uma tarefa sem omitir autoridade, dependências, critérios ou evidências.

## Procedimento

1. ler `AGENTS.md`;
2. classificar a tarefa por uma rota de `ROUTES.yaml`;
3. abrir os arquivos `required`;
4. pesquisar IDs e símbolos com `rg` antes de abrir fontes adicionais;
5. abrir itens `optional` apenas quando o gatilho se aplicar;
6. parar diante de conflito, autoridade ausente ou referência quebrada;
7. usar `archive/` apenas por objeto exato em auditoria de proveniência.

## Exclusões

Buscas e pacotes normais excluem `archive/`, `.local/drafts/`, dependências, caches, builds e saídas geradas. A exclusão não apaga nem reduz a autoridade de uma fonte; apenas evita que conteúdo histórico ou pesado polua o contexto operacional.

## Limite de tamanho

Não há meta universal de linhas ou tokens. Cada pacote contém apenas dependências transitivamente necessárias. Se uma rota exigir grandes cópias de texto, a responsabilidade documental deve ser revista.
