# Reinício e revisão do intervalo 030 — extensão experimental do INC-001

- Data: 2026-09-14.
- Branch: `inc-001-player-adjustments`, ainda sem commit de verificação desta extensão.
- Origem da observação no navegador: relato e logs fornecidos pelo operador após marcar 30 intervalos.
- Escopo: evidência do teste manual com MP4 real; a CI e a consolidação em commit são registradas separadamente.

O operador encerrou e reiniciou o backend com `make dev-backend` e o frontend com `make dev-frontend`. No novo processo, os logs do FastAPI mostraram `GET /spike/media` e `GET /spike/intervals` com `200`, e acesso ao MP4 local com `206 Partial Content`. O operador relatou que abriu e reviu o intervalo 030 após o reinício e encontrou o mesmo trecho.

Uma consulta somente leitura à API em execução recuperou o intervalo 030 com `media_path = CEPRAEA x COSTA.mp4`, `start_ms = 554729`, `end_ms = 560923`, `id = 30` e `created_at = 2026-09-14T16:20:18.649Z`. Consulta independente ao SQLite local retornou os mesmos campos e status `ATIVO`. O banco continha 30 registros: 23 ativos e 7 excluídos logicamente.

O SHA-256 do MP4 calculado após as 30 marcações foi `ea6607f4d6a0095c1b413722fefa41aa50be57f2e1b6b9bed1fef7ed908c23c9`, igual ao valor anterior em [INC-001.md](INC-001.md). `.local/media` continha somente `CEPRAEA x COSTA.mp4`.

Em relato posterior, o operador afirmou ter exercitado durante as 30 marcações todos os seeks e velocidades, o fluxo sem mouse, a revisão da prévia e a parada do trecho, além de excluir intervalos com justificativa. Essas verificações perceptivas são registradas como **relato do operador**; não há aqui medições individuais de cada busca ou velocidade.

Nova consulta somente leitura confirmou sete registros `EXCLUÍDO` (IDs 1–6 e 27), todos com motivo não vazio e data de exclusão. `GET /spike/intervals/deleted` recuperou os sete registros, enquanto a lista operacional contém apenas os 23 ativos. Isso comprova persistência e consulta de auditoria para essas exclusões.

Depois disso, o operador editou um lance já salvo e confirmado. A consulta ao SQLite mostrou que foi o intervalo 030: o ID, o arquivo, o início (`554729` ms) e a data de criação foram preservados; o fim passou de `560923` para `561923` ms. A tabela de versões contém a versão 1 com os limites anteriores `554729`–`560923` ms e data da correção `2026-09-14T16:44:52.680Z`. `PRAGMA quick_check` retornou `ok`.

O operador encerrou e reiniciou backend e frontend depois da edição e reviu novamente o intervalo 030, confirmando que o trecho continuou com o fim corrigido. Os logs do novo processo mostraram carregamento das listas com `200 OK` e acesso ao MP4 por requisições `206 Partial Content`. Uma consulta posterior à API e ao SQLite recuperou o ID 30 com `554729`–`561923` ms; a versão anterior permaneceu intacta e `PRAGMA quick_check` retornou `ok`.

**Resultado do ensaio manual:** passaram a navegação e as velocidades relatadas, o fluxo sem mouse, a revisão da prévia, a parada do trecho, a exclusão lógica auditável e a edição do mesmo ID persistida e revista após reinício. A CI e a evidência consolidada com commit testado ainda permanecem pendentes. O estado da extensão continua `IMPLEMENTED_NOT_VERIFIED` até essa consolidação.
