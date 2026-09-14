# Verificação local dos atalhos do player — extensão do INC-001

- Data: 2026-09-14.
- Branch: `inc-001-player-adjustments`, com alterações ainda não consolidadas em commit.
- Ambiente: frontend Vite local em `127.0.0.1:5173`, FastAPI local em `127.0.0.1:8000`, navegação com `agent-browser` e MP4 local `CEPRAEA x COSTA.mp4`.
- Escopo: checagem funcional de foco e atalhos no navegador. Não substitui o gate manual completo, a CI ou a verificação de todos os arquivos e navegadores.

| Ação observada | Resultado |
| --- | --- |
| `Tab` até a área de atalhos | A área recebeu foco sem mouse; `Espaço` iniciou e pausou o player. |
| Seta `→`, `I` e `O` na área de atalhos | A prévia foi capturada em `1.500`–`2.500` s, sem salvar. |
| `R` na prévia | O player buscou `1.500` s, reproduziu e pausou em `2.500` s; a prévia permaneceu disponível. |
| `Esc` após a revisão da prévia | A marcação foi descartada, sem POST. |
| `Tab` na lista com seis intervalos | O foco selecionou explicitamente o intervalo 004; `R` buscou `216.069` s, o início desse registro, e `Esc` interrompeu a revisão. |
| `Enter` no botão **CONFIRMAR E SALVAR** focado | Uma única chamada POST foi observada em uma resposta simulada apenas no navegador; a interface recebeu o ID fictício 999. |
| `Espaço` no botão **Reproduzir** focado e no elemento nativo do vídeo | Cada foco alternou reprodução/pausa uma vez, sem dupla ativação observada. |

Depois da sessão, a consulta somente leitura ao SQLite local retornou os mesmos IDs `1, 2, 3, 4, 5, 6`; o ID fictício 999 não foi gravado. A sessão de navegador foi encerrada.

Os testes determinísticos do frontend passaram (21 testes) e o build Vite concluiu. Permanecem pendentes o ensaio perceptivo completo com MP4 real, a verificação de todas as velocidades e combinações de foco, a nova CI e o registro de um commit testado.
