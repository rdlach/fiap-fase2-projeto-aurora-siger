# FIAP Fase 2 - Projeto Aurora Siger

Projeto da Fase 2 da FIAP: relatorio operacional de pouso para a atividade **A Aurora Ajusta a Trajetoria na Aproximacao a Marte - MGPEB**.

O prototipo simula um Modulo de Gerenciamento de Pouso e Estabilizacao de Base, organizando modulos de pouso em fila, aplicando regras logicas de autorizacao e classificando o resultado em pousado, espera ou alerta.

## Como executar o prototipo

O prototipo usa apenas recursos basicos do Python e o modulo `random`, que ja vem com a linguagem. Nao e preciso instalar nada.

Na pasta raiz do repositorio, use o comando que funcionar na sua instalacao:

```bash
python projeto2-grupo/aurora_siger_pt2.py     # Windows, macOS ou Linux
py projeto2-grupo/aurora_siger_pt2.py         # Windows, pelo inicializador do Python
python3 projeto2-grupo/aurora_siger_pt2.py    # macOS ou Linux
```

No menu, a opcao **7** roda a demonstracao completa no modo base: cenario, regras, buscas, fila, resultado e modelo de descida. Resultado esperado: M02 e M01 em POUSADO, M03 em ESPERA, M05 e M04 em ALERTA.

A opcao **9** reavalia os modulos pendentes sem apagar os pousados nem o historico de alertas. Permite atualizar o ambiente e ajustar os dados operacionais de cada modulo em espera. Modulos em alerta so retornam apos confirmacao de revisao, e todas as regras de seguranca sao aplicadas novamente. Alteracoes de combustivel sao ajustes manuais do cenario, nao reabastecimento automatico. As buscas continuam consultando o cadastro inicial; o resumo mostra o estado operacional.

Exemplo: execute **7**, depois **9**; mantenha o ambiente, ajuste o combustivel de M03 para 40% e preserve seus demais valores. Sem liberar os alertas, o resumo passa a mostrar M02, M01 e M03 pousados, com M05 e M04 ainda em alerta. Sem ajustar o combustivel, M03 continua em espera. As opcoes **3**, **7** e **8** iniciam uma nova simulacao e limpam os resultados anteriores. As opcoes 3 e 7 recarregam o cadastro do cenario selecionado; para restaurar todos os valores base, use **8 -> 1**. Ajustes operacionais da opcao 9 nao sao gravados no cadastro inicial.

## Arquivos da entrega

- `projeto2-grupo/aurora_siger_pt2.py`: prototipo em Python com menu, modo base, modo randomico e modo manual.
- `projeto2-grupo/relatorio/relatorio_mgpeb.pdf`: relatorio tecnico atualizado (9 paginas), com o anexo de estruturas de dados.
- `projeto2-grupo/relatorio/relatorio_mgpeb.docx`: o mesmo relatorio em Word, para editar.
- `projeto2-grupo/diagramas/diagrama-logico-mgpeb-v3.svg` e `.png`: folha 1, circuito logico oficial da decisao de pouso (portas AND, OR, NOT e NOR), com as tres saidas POUSADO, ESPERA e ALERTA.
- `projeto2-grupo/diagramas/diagrama-fluxo-mgpeb.svg` e `.png`: folha 2, fluxo da simulacao e reavaliacao (cenario, fila FIFO, avaliacao, listas, retorno dos pendentes e historico de alertas).
- `projeto2-grupo/diagramas/diagramas-mgpeb.drawio`: as duas folhas em formato editavel do draw.io (uma pagina por folha). Abra em https://app.diagrams.net

## Arquivos auxiliares (opcionais)

Estes scripts so servem para gerar novamente o grafico, o PDF e o Word do relatorio. Eles usam bibliotecas externas, mas **nao fazem parte do prototipo**, que continua sem dependencias.

- `projeto2-grupo/relatorio/relatorio_mgpeb.md`: texto-fonte do relatorio. As correcoes de texto sao feitas aqui.
- `projeto2-grupo/relatorio/gerar_grafico_descida.py`: gera a Figura 2 em `relatorio/figuras/` (usa `matplotlib`).
- `projeto2-grupo/relatorio/gerar_pdf_relatorio.py`: gera o PDF a partir do `.md` (usa `reportlab`).
- `projeto2-grupo/relatorio/gerar_docx_relatorio.py`: gera o Word a partir do `.md`, com as mesmas fontes (embutidas no arquivo), medidas e conteudo do PDF; a paginacao pode variar entre editores (usa `python-docx`, `fonttools` e `reportlab`).

Para gerar tudo de novo, depois de editar o `.md`:

```bash
pip install matplotlib reportlab python-docx fonttools
cd projeto2-grupo/relatorio
python gerar_grafico_descida.py
python gerar_pdf_relatorio.py
python gerar_docx_relatorio.py
```

Os scripts do PDF e do Word usam as fontes DejaVu. Buscam primeiro `MGPEB_FONTES` (se definida) ou o caminho padrao do Linux; quando indisponivel, usam as fontes incluidas no matplotlib. A geracao dos documentos requer as dependencias opcionais acima; o prototipo continua sem dependencias externas.

## Regras logicas

- `AUTORIZAR = A . B . C . D . E`
- `ALERTA = (A' . K) + D'`, que simplifica para `K + D'`, pois `K` ja implica `A'`
- `ESPERA = (AUTORIZAR + ALERTA)'`

As tres saidas sao exclusivas: cada modulo cai em exatamente uma delas.

Onde:

- `A = combCheck` (combustivel >= 35%)
- `B = atmCheck` (atmosfera estavel, vento <= 18 m/s, visibilidade >= 4 km e sem tempestade de poeira)
- `C = areaCheck`
- `D = sensCheck`
- `E = massaCheck`
- `K = combustivel abaixo de 30%` (condicao critica, usada so na regra de alerta)

## Ordem de prioridade

A fila de pouso (`ordenarFilaPorPrio`) e a busca de maior prioridade (`buscarMaiorPrio`) usam a mesma regra, definida em `vemDepois`: menor numero de prioridade, depois maior criticidade e, por ultimo, menor combustivel. No modo base, as duas apontam M02 na frente de M01.


## Historico e limites da simulacao

- `modsAlerta` mostra os modulos ainda retidos; `pilhaAlertas` guarda eventos anteriores, inclusive de modulos ja recuperados. Uma nova falha pode registrar outro evento do mesmo ID.
- Os motivos indicam combustivel critico (valor abaixo de 30%), falha nos sensores ou ambos. Autorizacoes, esperas e ajustes manuais nao entram na pilha. O horario registrado e o de chegada a orbita, nao o da decisao.
- O historico fica apenas na memoria e e apagado ao reiniciar ou encerrar. Nao ha armazenamento permanente nem registro de responsaveis.
- Os cinco modulos ja estao disponiveis em orbita. Nao ha passagem de tempo, consumo de combustivel na espera ou ocupacao dinamica da area. A autorizacao assume pouso bem-sucedido.
- O modelo de descida e uma demonstracao separada: sugere o acionamento em 59 s, sem simular frenagem nem controlar a decisao de pouso.
- No modo manual da opcao 8, respeite ESTAVEL/INSTAVEL, LIVRE/OCUPADA e S/N: textos invalidos viram condicoes desfavoraveis. A opcao 9 repete respostas S/N invalidas.

## Validacao realizada

Foram verificadas 2.160 combinacoes de regras e limites, 100 cenarios aleatorios, buscas vazias, ordenacao, modos de entrada e reavaliacoes com e sem correcao. Os resultados, exemplos de reproducao e limitacoes estao nas secoes 3.5 a 3.7 do relatorio. Apos a atualizacao das mensagens, tambem foram conferidos alertas por combustivel, sensores e ambas as causas, incluindo o registro na pilha. Essas verificacoes locais nao equivalem a certificacao de voo nem a uma suite permanente de testes.
