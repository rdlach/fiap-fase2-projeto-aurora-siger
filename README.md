# FIAP Fase 2 - Projeto Aurora Siger

Projeto da Fase 2 da FIAP para a atividade **A Aurora Ajusta a Trajetoria na Aproximacao a Marte - MGPEB**.

O MGPEB (Modulo de Gerenciamento de Pouso e Estabilizacao de Base) simula o pouso dos modulos da colonia: coloca os modulos em fila, aplica as regras de autorizacao e classifica cada um como pousado, em espera ou em alerta.

## Como executar o prototipo

O prototipo so usa o Python e o modulo `random`, que ja vem com ele. Nao precisa instalar nada.

Na pasta raiz do repositorio, rode um destes comandos (o que funcionar no seu computador):

```bash
python projeto2-grupo/aurora_siger_pt2.py     # Windows, macOS ou Linux
py projeto2-grupo/aurora_siger_pt2.py         # Windows
python3 projeto2-grupo/aurora_siger_pt2.py    # macOS ou Linux
```

A opcao **7** do menu roda a demonstracao completa no modo base (cenario, regras, buscas, fila, resultado e modelo de descida). O resultado esperado e: M02 e M01 pousados, M03 em espera, M05 e M04 em alerta.

A opcao **9** reavalia os modulos pendentes sem apagar quem ja pousou nem o historico de alertas. Da para atualizar o ambiente e ajustar os dados de cada modulo. Os modulos em alerta so voltam para a fila se a revisao for confirmada, e todos passam pelas regras de novo. Mudar o combustivel nessa opcao e so trocar um dado do cenario, nao e reabastecer.

Exemplo: rode a **7** e depois a **9**. Mantenha o ambiente, mude o combustivel do M03 para 40% e nao libere os alertas. O resumo passa a mostrar M02, M01 e M03 pousados, com M05 e M04 ainda em alerta. Se o combustivel do M03 nao for alterado, ele continua em espera.

As opcoes **3**, **7** e **8** comecam uma simulacao nova e apagam os resultados anteriores. As opcoes 3 e 7 recarregam o cadastro do cenario escolhido; para voltar ao modo base, use **8** e depois **1**. Os ajustes feitos na opcao 9 nao mudam o cadastro, entao as buscas (opcao 2) continuam mostrando os valores originais.

## Arquivos da entrega

- `projeto2-grupo/aurora_siger_pt2.py`: prototipo em Python, com menu e os modos base, randomico e manual.
- `projeto2-grupo/relatorio/relatorio_mgpeb.pdf`: relatorio tecnico (9 paginas), com o anexo de estruturas de dados.
- `projeto2-grupo/relatorio/relatorio_mgpeb.docx`: o mesmo relatorio em Word, caso seja preciso editar (depois e so salvar como PDF).
- `projeto2-grupo/diagramas/diagrama-logico-mgpeb-v3.svg` e `.png`: folha 1, circuito logico da decisao de pouso (AND, OR, NOT e NOR) com as saidas POUSADO, ESPERA e ALERTA.
- `projeto2-grupo/diagramas/diagrama-fluxo-mgpeb.svg` e `.png`: folha 2, fluxo da simulacao (cenario, fila, avaliacao, listas, reavaliacao dos pendentes e pilha de alertas).
- `projeto2-grupo/diagramas/diagramas-mgpeb.drawio`: as duas folhas para editar no draw.io (https://app.diagrams.net).

## Regras logicas

- `AUTORIZAR = A . B . C . D . E`
- `ALERTA = (A' . K) + D'`, que simplifica para `K + D'`, ja que `K` implica `A'`
- `ESPERA = (AUTORIZAR + ALERTA)'`

Cada modulo cai em uma unica saida.

Onde:

- `A = combCheck` (combustivel >= 35%)
- `B = atmCheck` (atmosfera estavel, vento <= 18 m/s, visibilidade >= 4 km e sem tempestade de poeira)
- `C = areaCheck` (area de pouso livre)
- `D = sensCheck` (sensores funcionais)
- `E = massaCheck` (massa <= 12000 kg)
- `K = combustivel abaixo de 30%` (condicao critica, usada so na regra de alerta)

## Ordem de prioridade

A fila (`ordenarFilaPorPrio`) e a busca de maior prioridade (`buscarMaiorPrio`) usam a mesma regra, que fica em `vemDepois`: menor numero de prioridade, depois maior criticidade e, por ultimo, menor combustivel. No modo base, as duas colocam o M02 na frente do M01.

## Historico e limites da simulacao

- `modsAlerta` tem os modulos que ainda estao retidos. A `pilhaAlertas` e o historico: guarda tambem alertas de modulos que depois foram liberados, e um modulo que falha de novo ganha outro registro.
- O motivo do alerta mostra combustivel critico (abaixo de 30%), falha nos sensores ou os dois. Pousos, esperas e ajustes manuais nao entram na pilha, e o horario guardado e o de chegada a orbita.
- Tudo fica so na memoria e se perde ao reiniciar ou fechar o programa.
- Os cinco modulos ja estao em orbita. Nao ha passagem de tempo, gasto de combustivel na espera nem ocupacao da area depois de um pouso, e todo pouso autorizado e considerado bem-sucedido.
- O modelo de descida (opcao 6) e separado da decisao de pouso: ele sugere acionar os retropropulsores em 59 s, mas nao simula a frenagem.
- No modo manual (opcao 8), digite ESTAVEL/INSTAVEL, LIVRE/OCUPADA e S/N como o programa pede, porque outro texto vira condicao desfavoravel. Na opcao 9, o programa repete a pergunta se a resposta nao for S ou N.

## Testes

Testamos 2.160 combinacoes das regras e dos limites, 100 cenarios aleatorios, buscas com listas vazias, a ordenacao, os tres modos de entrada e a reavaliacao com e sem ajustes, incluindo alertas por combustivel, por sensores e pelos dois. Os casos e resultados estao nas secoes 3.5 a 3.7 do relatorio. Foram testes feitos pela equipe; o projeto nao tem testes automaticos.
