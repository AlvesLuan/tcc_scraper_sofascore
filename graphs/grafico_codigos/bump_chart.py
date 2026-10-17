"""05 - Bump chart: corrida de posições das variáveis no Top 5."""

import matplotlib.pyplot as plt
import numpy as np

from .analise import anos_no_top5, frequencia_de, segmentos_consecutivos
from .base import salvar


def bump_chart(anos, variaveis, rankings, cores, caminho_saida, min_frequencia=2):
    """
    Cada variável tem sua própria linha (cor fixa), subindo/descendo conforme
    sua posição no Top 5, e a linha se interrompe nos anos em que ela saiu.

    Por legibilidade, só entram variáveis com pelo menos `min_frequencia`
    aparições no Top 5; as demais continuam nos outros gráficos.
    """
    variaveis_plot = [
        v for v in variaveis if frequencia_de(v, rankings, anos) >= min_frequencia
    ]

    fig, ax = plt.subplots(figsize=(12, 7))

    for variavel in variaveis_plot:
        anos_validos = anos_no_top5(variavel, anos, rankings)
        if not anos_validos:
            continue

        cor = cores[variavel]
        primeiro_segmento = True

        for segmento in segmentos_consecutivos(anos_validos):
            posicoes = [rankings[ano][variavel] for ano in segmento]
            ax.plot(
                segmento, posicoes, marker="o", color=cor, linewidth=2,
                label=variavel if primeiro_segmento else None,
            )
            primeiro_segmento = False

    ax.set_yticks(np.arange(1, 6))
    ax.set_yticklabels(["1º", "2º", "3º", "4º", "5º"])
    ax.invert_yaxis()
    ax.set_xticks(anos)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Posição no ranking")
    ax.set_title("Corrida de Posições das Variáveis no Top 5")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))

    salvar(caminho_saida)
