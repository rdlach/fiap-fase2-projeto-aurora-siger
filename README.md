# FIAP Fase 2 - Projeto Aurora Siger

Projeto da Fase 2 da FIAP: relatorio operacional de pouso para a atividade **A Aurora Ajusta a Trajetoria na Aproximacao a Marte - MGPEB**.

O prototipo simula um Modulo de Gerenciamento de Pouso e Estabilizacao de Base, organizando modulos de pouso em fila, aplicando regras logicas de autorizacao e classificando o resultado em pousado, espera ou alerta.

## Como executar

```bash
python3 projeto2-grupo/aurora_siger_pt2.py
```

## Conteudo principal

- `projeto2-grupo/aurora_siger_pt2.py`: prototipo em Python com menu, modo base, modo randomico e modo manual.
- `projeto2-grupo/diagramas/diagrama-logico-mgpeb-v3.svg` e `.png`: folha 1, circuito logico da decisao de pouso (portas AND, OR, NOT e NOR). O PNG esta em 2x, para uso no relatorio.
- `projeto2-grupo/diagramas/diagrama-fluxo-mgpeb.svg` e `.png`: folha 2, fluxo da simulacao (cenario, fila FIFO, avaliacao, listas e pilha de alertas).

A versao anterior (`diagrama-logico-mgpeb-v2.svg`) fica so como historico.

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
