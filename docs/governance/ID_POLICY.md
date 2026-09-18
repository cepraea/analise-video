# Política de identificadores

## Regras

- IDs são estáveis, únicos no repositório e nunca são reutilizados com outro significado.
- `RF-*` e `RNF-*` existentes são preservados; a migração não os renomeia para `FR-*` ou `NFR-*`.
- Novos IDs usam namespace por classe, como `DEC-*`, `ADR-*`, `SRC-*`, `INC-*`, `TAX-*`, `CON-*` e `EVD-*`.
- Um item substituído permanece consultável e aponta para o sucessor com `superseded_by`.
- O sucessor aponta para o anterior com `supersedes`.
- IDs provisórios podem ser encerrados por uma decisão estável, sem serem apagados.
- Um ID não comprova autoridade, implementação ou verificação por si só.

## Dados mínimos de uma decisão

Uma decisão deve registrar `id`, `title`, `status`, `authority`, `decided_at`, `statement`, `provenance`, `affected_documents` e `supersedes`.

## Dados mínimos de uma fonte

Uma fonte deve registrar ID, tipo, localização, hash ou referência de baseline, escopo de autoridade e elegibilidade para sustentar afirmações do produto.

## Identificadores reservados nesta migração

- `GOV-001`: adoção da arquitetura documental híbrida.
- `DOC-001`: padrão documental aprovado.
- `GOV-SRC-001`: imutabilidade de baselines publicados.
- `GOV-SRC-002`: classificação dos oito artefatos de controle.

Os IDs provisórios `GOV-PENDING-SOURCE-REVISION-001` e `GOV-PENDING-SOURCE-SCOPE-002` são substituídos, respectivamente, por `GOV-SRC-001` e `GOV-SRC-002`.
