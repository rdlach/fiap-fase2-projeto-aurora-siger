"""Gera a Figura 2 do relatorio: altura do modulo em funcao do tempo.

Usa os mesmos parametros de aurora_siger_pt2.py (altInicialM, tempoDescidaS,
altRetroM). Este script e separado do prototipo para que o MGPEB continue sem
bibliotecas avancadas; aqui o matplotlib serve apenas para o relatorio.
"""

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ALT_INICIAL_M = 1200
TEMPO_DESCIDA_S = 80
ALT_RETRO_M = 550
COEF_DESCIDA = ALT_INICIAL_M / (TEMPO_DESCIDA_S * TEMPO_DESCIDA_S)

SAIDA = Path(__file__).parent / "figuras" / "grafico_descida.png"


def altura(t):
    return max(0.0, ALT_INICIAL_M - COEF_DESCIDA * t * t)


def instante_retro():
    # Mesmo criterio do prototipo: primeiro segundo inteiro com altura <= limite.
    for t in range(0, TEMPO_DESCIDA_S + 1):
        if altura(t) <= ALT_RETRO_M:
            return t
    return None


def main():
    ts = [i / 10 for i in range(0, TEMPO_DESCIDA_S * 10 + 1)]
    hs = [altura(t) for t in ts]
    t_retro = instante_retro()
    h_retro = altura(t_retro)

    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)

    ax.plot(ts, hs, color="#202020", linewidth=2.2, label="h(t) = 1200 − 0,1875·t²")
    ax.axhline(ALT_RETRO_M, color="#999999", linestyle="--", linewidth=1.1)
    ax.axvline(t_retro, ymax=h_retro / 1300, color="#999999", linestyle="--", linewidth=1.1)
    ax.text(1.5, ALT_RETRO_M + 25, f"limite de acionamento: {ALT_RETRO_M} m", color="#555555", fontsize=9)
    ax.scatter([t_retro], [h_retro], color="#D20A5C", s=55, zorder=5)
    ax.annotate(
        f"retropropulsores: t = {t_retro} s, h ≈ {h_retro:.0f} m".replace(".", ","),
        xy=(t_retro, h_retro),
        xytext=(t_retro - 37, h_retro - 260),
        fontsize=9.5,
        color="#D20A5C",
        arrowprops={"arrowstyle": "->", "color": "#D20A5C", "lw": 1},
    )

    ax.set_xlim(0, TEMPO_DESCIDA_S)
    ax.set_ylim(0, 1300)
    ax.set_xlabel("tempo t (s)")
    ax.set_ylabel("altura h(t) (m)")
    ax.set_xticks(range(0, TEMPO_DESCIDA_S + 1, 10))
    ax.grid(True, color="#E6E6E6", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)

    SAIDA.parent.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(SAIDA)
    print(f"Grafico salvo em {SAIDA} (t_retro={t_retro}s, h={h_retro:.2f} m, "
          f"t exato={TEMPO_DESCIDA_S * math.sqrt(1 - ALT_RETRO_M / ALT_INICIAL_M):.2f}s)")


if __name__ == "__main__":
    main()
