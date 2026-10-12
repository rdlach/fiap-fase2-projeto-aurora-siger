# FIAP Fase 2 - Projeto Aurora Siger

Projeto em Python para a atividade **A Aurora Ajusta a Trajetoria na Aproximacao a Marte - MGPEB**.

O prototipo simula um Modulo de Gerenciamento de Pouso e Estabilizacao de Base, organizando modulos de pouso em fila, aplicando regras logicas de autorizacao e classificando o resultado em pousado, espera ou alerta.

## Como executar

```bash
python3 projeto2-grupo/aurora_siger_pt2.py
```

## Conteudo principal

- `projeto2-grupo/aurora_siger_pt2.py`: prototipo em Python com menu, modo base, modo randomico e modo manual.
- `projeto2-grupo/diagramas/diagrama-logico-mgpeb-v2.svg`: diagrama logico principal.
- `projeto2-grupo/diagramas/diagrama-logico-mgpeb-v2.svg.png`: versao renderizada do diagrama para uso no relatorio.

## Regras logicas

- `AUTORIZAR = A . B . C . D . E`
- `ALERTA = A' + B' + C' + D' + E'`

Onde:

- `A = combCheck`
- `B = atmCheck`
- `C = areaCheck`
- `D = sensCheck`
- `E = massaCheck`
