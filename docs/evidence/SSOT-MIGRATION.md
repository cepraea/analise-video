# Migração da SSOT

## Estado

O gate G0 foi preservado sem reescrita e promovido com completude `HASH_ONLY_PARTIAL`: manifesto e hashes originais estão íntegros, mas oito objetos históricos já não estavam disponíveis pelos bytes atuais.

G0-R2 é a revisão sucessora que registra o estado corrigido. Ela possui manifesto próprio e não altera G0.

Após a publicação de G0-R2, os validadores canônicos adicionados ao repositório passaram a integrar a própria varredura técnica. Conforme `GOV-SRC-001`, G0-R2 não foi sobrescrito: G0-R3 registra a regeneração final sobre essa raiz ampliada.

O endurecimento do próprio validador de baselines passou a verificar também os controles históricos de G0. Essa alteração criou G0-R4; nenhuma revisão anterior foi modificada.

## Decisões aplicadas

- `GOV-001`: arquitetura híbrida;
- `DOC-001`: padrão documental;
- `GOV-SRC-001`: baselines publicados são imutáveis;
- `GOV-SRC-002`: oito controles são preservados sem autoridade de produto.

## Evidências

- índice: [`ssot-migration/BASELINES.yaml`](./ssot-migration/BASELINES.yaml);
- G0: [`ssot-migration/baselines/g0/`](./ssot-migration/baselines/g0/);
- G0-R2: [`ssot-migration/baselines/g0-r2/`](./ssot-migration/baselines/g0-r2/);
- G0-R3: [`ssot-migration/baselines/g0-r3/`](./ssot-migration/baselines/g0-r3/);
- G0-R4: [`ssot-migration/baselines/g0-r4/`](./ssot-migration/baselines/g0-r4/);
- objetos: `archive/ssot/objects/sha256/`.
