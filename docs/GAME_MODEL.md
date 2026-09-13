# GAME_MODEL.md — Snapshot de desenvolvimento do Modelo de Jogo CEPRAEA

## Proveniência

- Fonte canônica: Google Doc `Planejamento completo`
- Google Drive ID: `1OE7R10_BWJUv48Lubdj0hD8V9X1hdTnhK1gRxgDUsr0`
- Guia utilizada: `Conceitos do Jogo — CEPRAEA`
- Tab ID: `t.4k06rsbbpxy`
- Revisão lida: `ANLCKQn2aG-1anCiT8Jo8oCPKCO2aUOgCjZQCNVe6S3wNwBEqqT6uEa3gE17LkkA7nYZ2xo104xPfyo1XWscnuDoaKB5vETxwj66f3n0bak`
- Data da extração: 2026-09-13
- Natureza: snapshot derivado para desenvolvimento; o Planejamento completo permanece canônico.

## Fases do jogo

O modelo CEPRAEA utiliza quatro grandes estados:

1. Transição Ofensiva
2. Ataque Posicionado
3. Transição Defensiva
4. Defesa Posicionada

A fase é definida pelo problema dominante e pela origem da vantagem, não apenas por formação, localização, quantidade de atletas, número de passes ou presença da especialista.

### Fases independentes

As equipes podem atravessar as fases em instantes diferentes. A defesa pode estar funcionalmente estabilizada enquanto o adversário ainda está em transição ofensiva. Por isso, `equipe_com_posse` e `equipe_analisada` são dimensões distintas e segmentos de fase podem se sobrepor entre equipes.

## Fronteiras relevantes

### Transição Ofensiva

Começa com a conquista da posse ou do direito ao reinício. O problema é explorar vulnerabilidade herdada da troca de posse e instalar a organização ofensiva.

### T3 — Ataque instalado

Status no modelo: consolidado conceitualmente. O gate ocorre quando coexistem composição deliberada, funções e ocupações reconhecíveis, bola em zona útil, fim do problema predominante de progressão/entrada/substituição e ausência de vantagem herdada predominante. A próxima vantagem passa a precisar ser construída pelo próprio ataque.

### Teste causal de fronteira

Se a oportunidade desapareceria sem a vulnerabilidade criada pela troca de posse, a vantagem continua herdada e a equipe permanece em transição. Quando a organização está instalada e a próxima oportunidade precisa ser criada pelo sistema ofensivo, começa o ataque posicionado.

### Transição Defensiva e T4

A Transição Defensiva começa com a perda efetiva da posse ou do direito de continuar atacando. T4 representa defesa funcionalmente estabilizada e possui indicadores próprios no documento canônico. T3 e T4 são gates independentes.

## Vantagem e ameaça

### Vantagem CEPRAEA

Status: consolidado conceitualmente. É o estado coletivo, funcional e temporário em que existe possibilidade tática acessível que o adversário não consegue neutralizar no tempo da ação. Pode ser herdada ou construída e possuir mecanismos temporais, espaciais, composicionais, de matchup, informacionais ou organizacionais.

A relação 4x3 representa superioridade nominal e não comprova, sozinha, vantagem funcional.

### Ameaça

Status: consolidado conceitualmente. É estado momentâneo de uma atacante segundo a ação perigosa disponível e o tempo defensivo de resposta.

- `IMEDIATA`: pode decidir na ação atual antes da resposta.
- `EMERGENTE`: pode tornar-se imediata na ação seguinte.
- `CONCEDÍVEL`: pode permanecer temporariamente livre porque a defesa ainda responde a tempo.

### Zona de risco

Status: consolidado conceitualmente. É limiar espacial-funcional exclusivo da portadora em que a ação perigosa passa a ocorrer antes da contenção. Não é uma faixa fixa da quadra.

Relação conceitual registrada: `ameaça individual → zona de risco da portadora → vantagem coletiva`.

## Conceitos ofensivos em fechamento

### Fixação com bola

Definição confirmada, em fechamento. A ameaça da portadora provoca resposta defensiva que nega sua infiltração e compromete a capacidade daquela defensora de cobrir outra atacante. Fixação sem bola continua aberta.

### Livre

Definição confirmada, em fechamento. Disponibilidade para determinada ação. Regra central: `LIVRE ≠ PREPARADA ≠ VANTAGEM`. O modelo já usa livre para receber, finalizar, aérea ou livre com vantagem temporal insuficiente.

### Preparação

Definição confirmada, em fechamento. Quatro dimensões observáveis: profundidade/espaço de aceleração; apoios/inversão de inércia; orientação/campo visual; sincronia da vantagem temporal. Cada dimensão é avaliada separadamente; falha só torna a preparação insuficiente quando compromete a ação pretendida, caso contrário é suficiente com limitação.

### Bola de quebra

Definição confirmada, em fechamento operacional. Sequência de referência: `FIXA → PASSA → RECUPERA POSICIONAMENTO → DEFESA REDISTRIBUI REFERÊNCIAS → RECEBE NOVAMENTE LIVRE → FINALIZA`. Apenas devolver a bola não caracteriza automaticamente o padrão.

### Bola de continuidade

Definição confirmada, em fechamento operacional. Fixações e passes sucessivos transportam a vantagem até uma atacante seguinte receber livre; a finalizadora não precisa fixar antes do arremesso.

## Tomada de decisão

- boa decisão não é sinônimo de resultado positivo;
- estado das alternativas inclui liberdade, preparação, vantagem temporal e ação disponível;
- qualidade da estrutura criada e qualidade da decisão dentro dessa estrutura são avaliações diferentes;
- contexto pode ser local, sequencial dentro do lance ou histórico recente da partida;
- resultado factual e avaliação técnico-tática permanecem separados.

## Limites relevantes para implementação

Forma não é função. 4x3 não é sinônimo de vantagem. Presença da especialista não encerra transição sozinha. Velocidade não classifica fase sozinha. Aparência posicional não comprova ataque posicionado. Uma atleta livre não equivale automaticamente a vantagem.

Os conceitos ofensivos detalhados acima não são pré-condição para o gate INC-000→INC-007; a necessidade imediata é que a estrutura não impeça sua incorporação posterior.
