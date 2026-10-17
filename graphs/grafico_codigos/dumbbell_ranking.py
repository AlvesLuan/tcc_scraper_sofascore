"""04 - Dumbbell: posição no Top 5 por temporada (uma linha por variável)."""

import matplotlib.pyplot as plt
import numpy as np

from .analise import anos_no_top5, segmentos_consecutivos
from .base import salvar


def dumbbell_ranking(anos, variaveis, rankings, cores, caminho_saida):
    """
    Liga os anos em que a variável esteve no Top 5, em segmentos
    consecutivos: a linha se quebra nos anos em que ela saiu do Top 5.
    """
    fig, ax = plt.subplots(figsize=(12, max(6, len(variaveis) * 0.5)))

    for i, variavel in enumerate(variaveis):
        anos_validos = anos_no_top5(variavel, anos, rankings)
        if not anos_validos:
            continue

        cor = cores[variavel]

        for segmento in segmentos_consecutivos(anos_validos):
            if len(segmento) > 1:
                ax.plot(segmento, [i] * len(segmento), linewidth=2, alpha=0.5, color=cor)
            ax.scatter(segmento, [i] * len(segmento), s=80, color=cor, zorder=3)
            for ano in segmento:
                ax.text(
                    ano, i + 0.15, str(rankings[ano][variavel]),
                    ha="center", va="bottom", fontsize=7,
                )

    ax.set_yticks(np.arange(len(variaveis)))
    ax.set_yticklabels(variaveis)
    ax.set_xticks(anos)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Variável")
    ax.set_title("Posição das Variáveis no Top 5 por Temporada")
    ax.set_ylim(-1, len(variaveis))
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    salvar(caminho_saida)
