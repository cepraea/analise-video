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

Os testes usam repositórios temporários e cobrem reescrita de snapshots, remoção de registros, ciclos, herança de classificação, falhas de publicação, numeração de sucessores, localização dos manifestos e integridade dos inventários de checksums. Eles não alteram o archive publicado.

O promotor resolve o predecessor pelo registro versionado, prepara os arquivos em diretório temporário e serializa publicações por lock local no diretório Git. Se a preparação ou o registro falhar, o destino da nova revisão não permanece publicado. Objetos já copiados e verificados podem permanecer no armazenamento por conteúdo e ser reutilizados na nova tentativa; snapshots anteriores nunca são removidos.
