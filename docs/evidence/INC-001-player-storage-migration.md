# Evidência local — migração do SQLite experimental do player

Esta verificação cobre apenas a preservação dos intervalos durante a ampliação do esquema experimental. Ela não altera o gate, o commit ou a evidência já verificados do INC-001. A implementação desta branch ainda não foi consolidada em commit.

- Branch: `inc-001-player-adjustments`.
- Banco local: `.local/data/inc001.sqlite3` (ignorado pelo Git).
- Antes da alteração, `PRAGMA quick_check` retornou `ok`; havia uma tabela `spike_intervals` com cinco colunas e seis registros, IDs `1, 2, 3, 4, 5, 6`.
- Cópia consistente anterior à migração: `.local/data/backups/inc001-pre-migration-20260914T140637Z.sqlite3` (também ignorada pelo Git), verificada com os mesmos seis IDs e `PRAGMA quick_check = ok`.
- Depois da migração, a tabela manteve as cinco colunas originais e recebeu `status`, `deletion_reason` e `deleted_at`; a nova tabela `spike_interval_versions` está vazia, pronta para correções futuras.
- Os seis registros permaneceram `ATIVO`, sem motivo ou data de exclusão. Nenhum ID foi substituído.
- Comparação de todos os campos originais (`id`, `media_path`, `start_ms`, `end_ms`, `created_at`), ordenados por ID: SHA-256 antes = depois = `10e89112a8edcde0b5e90791dcc72e7191c7f6f680c2e2828d5443b3e78b207c`. O resumo foi calculado sobre `json.dumps(rows, ensure_ascii=False, separators=(',', ':'))` em UTF-8.
- Após a migração, `PRAGMA quick_check = ok` e `PRAGMA foreign_key_check` não retornou violações.
- Testes de backend: `.venv/bin/python -m pytest backend/tests` → **8 passed**. O teste de migração cria um banco no esquema antigo, com IDs não contíguos, executa a inicialização duas vezes e verifica valores, IDs e próximo ID.

A atualização de tempos, o histórico efetivo de correções e a exclusão lógica ainda não foram implementados; exigirão testes e evidência próprios. O MP4 original não foi usado nem verificado neste passo.
