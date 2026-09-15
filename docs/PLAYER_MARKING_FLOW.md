# Fluxo experimental de marcação e revisão da prévia

- Estado: **VERIFIED** — fluxo e atalhos verificados com MP4 real, testes automatizados e CI; evidência em `docs/evidence/INC-001-player-adjustments.md`.
- Escopo: ajuste posterior ao gate do INC-001 para o player local. Não redefine o resultado ou a evidência do INC-001 e não estabelece o modelo canônico de `LANCE`.

O fim de um intervalo cria uma prévia, não um registro no banco. O operador decide se quer rever, descartar ou confirmar e salvar. A revisão de um intervalo já salvo é um fluxo separado desta prévia.

## Estados da marcação

| Estado | O que a interface mantém | Persistência |
| --- | --- | --- |
| **Sem marcação** | Nenhum intervalo em preparação. | Nenhuma alteração. |
| **Início marcado** | MP4 selecionado e tempo inicial capturado. | Nenhuma alteração. |
| **Prévia válida** | Início e fim exibidos; `início < fim`. Revisar, descartar e confirmar estão disponíveis. | Nenhuma alteração. |
| **Revisão da prévia** | Os mesmos limites da prévia; reprodução apenas do trecho marcado. | Nenhuma alteração. |
| **Salvando** | Prévia preservada enquanto a confirmação aguarda resposta. | Uma requisição de criação em andamento. |
| **Salvo** | Resultado da confirmação; o registro recebe ID e aparece na lista. | Intervalo persistido. |
| **Descartado** | Resultado do descarte; tempos locais são limpos. | Nenhuma alteração. |

**Salvo** e **Descartado** são resultados transitórios: depois deles, a marcação volta a **Sem marcação**. Um registro salvo continua disponível na lista de revisão.

## Transições esperadas

| Estado atual | Comando ou evento | Próximo estado e efeito |
| --- | --- | --- |
| Sem marcação | `I` ou **INICIAR LANCE** | Início marcado; capturar o tempo corrente em milissegundos inteiros. |
| Início marcado | `O` ou **ENCERRAR LANCE**, com `início < fim` | Prévia válida; capturar e exibir o fim, sem enviar dados ao backend. |
| Início marcado | Encerrar com `início >= fim` | Permanecer em Início marcado e explicar o erro; nada é salvo. |
| Início marcado | `Esc` ou **DESCARTAR** | Descartado; limpar o início e voltar a Sem marcação. |
| Prévia válida | `R` ou **REVER** | Revisão da prévia; buscar o início e reproduzir até o fim. |
| Revisão da prévia | O trecho chega ao fim | Pausar e voltar a Prévia válida, preservando os dois tempos. |
| Revisão da prévia | `Esc` | Parar a revisão e voltar a Prévia válida, preservando os dois tempos. |
| Prévia válida | `Esc` ou **DESCARTAR** | Descartado; limpar ambos os tempos e voltar a Sem marcação. |
| Prévia válida | `Enter` ou **CONFIRMAR E SALVAR** | Salvando; enviar uma única requisição de criação. |
| Salvando | Resposta de sucesso | Salvo; mostrar o ID, atualizar a lista e voltar a Sem marcação. |
| Salvando | Falha no salvamento | Prévia válida; manter os tempos, mostrar o erro e permitir nova confirmação. |
| Salvando | Novo `Enter` ou `Esc` antes da resposta | Permanecer em Salvando; evitar duplicação ou descarte ambíguo. |

Assim, o primeiro `Esc` durante a revisão **só sai da revisão**. Um segundo `Esc`, já na prévia, **descarta a marcação**. Descartar nunca envia uma requisição de criação e não remove registros anteriormente salvos.

## Seleção e foco pelo teclado

- `R` revê a prévia válida enquanto existir uma marcação em preparação. Sem prévia, revê apenas o intervalo salvo selecionado explicitamente na lista; sem seleção, pede que o operador escolha um intervalo.
- `Tab` até **SELECIONAR PARA R** ou **REVER** seleciona aquele intervalo salvo. A seleção é visível e pode ser cancelada com `Esc` quando não houver marcação ou revisão ativa. Após salvar uma nova prévia, o novo intervalo fica selecionado.
- Uma área de atalhos focável por `Tab` permite usar `Espaço` e `Enter` sem ativar botões. Quando um botão está focado, essas duas teclas seguem a ativação nativa do botão; atalhos globais não interceptam campos editáveis nem os controles nativos do vídeo.
- `Espaço` alterna reprodução e pausa; `I` marca o início; `O` captura o fim; `R` inicia a revisão; `Enter` confirma e salva a prévia válida; `Esc` sai da revisão ou descarta/cancela conforme o estado. Repetição de tecla não repete operações, exceto a navegação por setas.

## Critérios de aceitação

- Exibir início e fim da prévia com precisão de milissegundos, mantendo `início < fim`.
- Não gravar o intervalo ao encerrar nem ao rever; gravar apenas após confirmação explícita.
- Preservar a prévia após revisão interrompida, revisão concluída ou falha de salvamento.
- Bloquear confirmações duplicadas enquanto uma gravação estiver em andamento.
- Testar com MP4 real a busca, a parada no fim e os dois usos consecutivos de `Esc`; a descrição deste fluxo não substitui essa evidência.
