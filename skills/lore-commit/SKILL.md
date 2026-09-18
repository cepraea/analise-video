---
name: lore-commit
description: Produzir e validar uma mensagem de commit a partir do índice e das verificações realmente observadas, sem preparar arquivos automaticamente.
---

# Produzir uma mensagem de commit

Examine somente o índice com `git diff --cached` e execute `make review-staged`. Não use o workspace para descrever bytes diferentes dos preparados e não execute `git add` por este procedimento.

Use título Conventional Commit. Registre `Tested` com comandos que realmente passaram ou `Not-tested` com a limitação concreta. Acrescente `Constraint` e `Rejected` apenas quando a mudança tiver uma restrição ou alternativa relevante; não preencha trailers genéricos.

Gere e mostre a mensagem sem commit com:

```bash
python3 scripts/git/lore_commit.py \
  --title "fix(context): descrição" \
  --tested "comando e resultado"
```

`git lore-commit` usa o mesmo programa com `--commit` depois da instalação reversível por `make hooks-install`. Passe os mesmos argumentos. A criação do commit depende da autorização da tarefa; gerar e validar a mensagem não autoriza o commit.

O hook `commit-msg` valida o arquivo atual recebido pelo Git. Ele exige `Tested` ou `Not-tested` no bloco final e rejeita trailers vazios, genéricos, duplicados, deslocados ou não suportados.
