# Configuração do Git LFS

## Escopo

Git LFS configurado antes do primeiro commit dos baselines, por solicitação de Davi Sermenho em 2026-09-16.

- padrões `*.pdf` e `*.png` usam LFS;
- dez objetos binários sem extensão em `archive/` usam regras por SHA-256 exato;
- 49 objetos textuais continuam no Git normal;
- os bytes do working tree e os manifestos publicados não são alterados;
- o Git armazena pointers LFS no commit e o LFS preserva os bytes correspondentes.

## Instalação local

Git LFS 3.4.1 instalado em `/home/davis/.local/bin/git-lfs` a partir do pacote Ubuntu `git-lfs=3.4.1-1ubuntu0.4`. Filtros e hook `pre-push` configurados com `git lfs install --local`, somente neste repositório.

Outras máquinas devem instalar Git LFS e executar `git lfs install` antes de trabalhar com os binários. Se o checkout contiver apenas pointers, executar `git lfs pull`.

## Novos objetos sem extensão

Antes de cada commit que acrescente objetos ao archive:

1. consultar o manifesto e selecionar o objeto por SHA-256 exato;
2. confirmar se seus bytes são binários;
3. executar `git lfs track --filename archive/ssot/objects/sha256/<sha256>` apenas para o objeto binário;
4. revisar `.gitattributes` e `git check-attr filter diff merge text -- <caminho>`;
5. após staging autorizado, confirmar o pointer no índice e executar `git lfs status`.

Nenhuma migração de histórico é necessária: os objetos ainda não foram commitados. Esta configuração não resolve as oito lacunas históricas já declaradas no G0 e não modifica revisões publicadas.

## Verificação executada

- dez binários passaram por `clean` e `smudge` com recuperação idêntica dos bytes;
- pointers contêm o SHA-256 e o tamanho esperados;
- o filtro efetivo de `git hash-object --path` corresponde ao pointer LFS;
- os objetos locais em `.git/lfs/objects/` possuem hashes válidos;
- 49 objetos textuais não possuem filtro LFS;
- rotas e baselines continuam válidos;
- staging permanece vazio; nenhum commit ou push foi executado.

Upload, autenticação e disponibilidade de armazenamento LFS remoto serão verificados no push autorizado, não nesta configuração local.
