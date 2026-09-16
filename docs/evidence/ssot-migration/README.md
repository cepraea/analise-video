# Baselines da migração

Os diretórios desta árvore são publicações imutáveis. Uma correção cria um novo ID de revisão; não altera o diretório anterior.

Os manifestos ligam caminhos lógicos a objetos armazenados por SHA-256 em `archive/ssot/objects/sha256/`. O arquivo `BASELINES.yaml` é o índice de revisões.

## Controles de publicação

O validador compara registros e diretórios já publicados com uma revisão Git anterior quando recebe `--base-ref`. O CI usa a base do PR ou o estado anterior ao push; uma validação sem esse argumento verifica hashes e linhagem, mas não comprova imutabilidade entre revisões.

```bash
python scripts/docs/validate_baselines.py --base-ref <revisao-anterior>
python -m unittest discover -s tests/docs -p 'test_*.py' -v
```

Antes de aceitar uma publicação, o validador exige manifestos com caminhos relativos dentro da árvore de baselines, sem travessia por `..` nem escape por links simbólicos. Para cada sucessor, os arquivos de checksums de fontes e controles são obrigatórios e devem corresponder integralmente ao manifesto, sem entradas ausentes, adicionais, duplicadas ou malformadas.

Objetos por SHA-256 devem ser arquivos regulares, sem links simbólicos, dentro do diretório físico do armazenamento. O promotor rejeita links existentes, inclusive links quebrados ou criados durante uma disputa de publicação; o validador também rejeita diretórios de armazenamento redirecionados por symlinks.

O CI executa `scripts/docs/validate_lfs.py` além de `git lfs fsck`. O inventário esperado vem de todos os manifestos de fontes e controles, não apenas da lista de arquivos já rastreados pelo LFS. Cada binário disponível deve aparecer no LFS, ter um pointer correspondente no índice e possuir bytes recuperados com tamanho e SHA-256 corretos. Somente as ausências históricas explicitamente declaradas no G0 são dispensadas. Os objetos são acessados por hashes exatos; não há varredura recursiva de `archive/`.

Os testes usam repositórios temporários e cobrem reescrita de snapshots, remoção de registros, ciclos, herança de classificação, falhas de publicação, numeração de sucessores, localização dos manifestos e integridade dos inventários de checksums. Eles não alteram o archive publicado.

O promotor resolve o predecessor pelo registro versionado, prepara os arquivos em diretório temporário e serializa publicações por lock local no diretório Git. Se a preparação ou o registro falhar, o destino da nova revisão não permanece publicado. Objetos já copiados e verificados podem permanecer no armazenamento por conteúdo e ser reutilizados na nova tentativa; snapshots anteriores nunca são removidos.

O G0 conserva seu esquema histórico com `baseline.gate: G0`; sucessores usam `baseline.id`. O promotor aceita essa diferença sem reescrever o manifesto original e rejeita identificações ausentes ou conflitantes.

Cada publicação atualiza `BASELINES.yaml` e `docs/governance/SOURCES.yaml`, preservando as demais informações de autoridade e classificação do catálogo. Os dois arquivos são preparados antes da substituição; falhas capturadas durante a atualização acionam a reversão das alterações já aplicadas. Se a reversão também falhar, a cópia dos bytes anteriores é preservada no caminho indicado pelo erro para recuperação manual. Essa reversão não é uma transação atômica entre arquivos em caso de interrupção abrupta do processo ou do sistema. O validador usado pelo CI rejeita divergências de IDs ou caminhos e duplicações entre os catálogos; o promotor também bloqueia novas publicações enquanto houver inconsistência prévia ou ausência do catálogo canônico.
