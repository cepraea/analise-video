---
name: code-review
description: Revisar alterações do CEPRAEA quanto a regressões de dados, vídeo, contratos e autoridade documental, usando o diff efetivo.
---

# Revisar alterações

Identifique o alvo solicitado: diff de trabalho, índice preparado para commit ou revisão Git. Use `git diff`, `git diff --cached` ou a comparação indicada. Examine os bytes dessa revisão; o arquivo no workspace pode diferir do índice.

Leia `AGENTS.md` e os documentos da rota pertinente em `docs/context/ROUTES.yaml`. Confira pacotes usados com `make context-check`. Investigue dependências com `rg`; não use um grafo histórico como evidência da arquitetura implementada.

Em manutenção de contexto, use `context_maintenance` e revise seleção de trechos, preservação dos bytes, referências, exclusões, integridade e comportamento de falha. Investigue riscos do produto quando o diff alcançar essas responsabilidades. Confira se o teste reproduz o problema e se a correção introduz regressões; não altere testes para apenas espelhar o código.

Priorize riscos concretos: alteração do original, perda ou duplicação da identidade do lance, correção sem histórico, divergência entre API e persistência, fatos misturados com interpretação, taxonomia fechada indevidamente, acesso a caminhos fora do escopo e promoção de estado sem evidência. Confira autorização e limites transacionais quando o diff os afetar.

Relate falhas com arquivo/linha, cenário que produz o erro, impacto, prioridade e correção acionável. Distingua achado comprovado de hipótese. Resuma as verificações executadas. Comentários sobre formatação ou nomes só são úteis quando explicam um problema funcional.
