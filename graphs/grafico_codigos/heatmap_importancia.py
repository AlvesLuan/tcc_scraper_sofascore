"""07 - Heatmap do valor de importância das variáveis do Top 5."""

import matplotlib.pyplot as plt
import numpy as np

from .base import salvar


def heatmap_importancia(anos, variaveis, dados_por_ano, top5_por_ano, frequencia, caminho_saida):
    matriz = np.zeros((len(variaveis), len(anos)))
    for i, variavel in enumerate(variaveis):
        for j, ano in enumerate(anos):
            if variavel in top5_por_ano[ano]:
                matriz[i, j] = dados_por_ano[ano].get(variavel, 0)

    fig, ax = plt.subplots(figsize=(12, max(6, len(variaveis) * 0.45)))
    imagem = ax.imshow(matriz, aspect="auto", cmap="Blues", interpolation="nearest")

    ax.set_xticks(np.arange(len(anos)))
    ax.set_xticklabels(anos)
    ax.set_xlabel("Ano")
    ax.set_yticks(np.arange(len(variaveis)))
    ax.set_yticklabels([f"{v} ({frequencia[v]}x)" for v in variaveis])
    ax.set_ylabel("Variável (nº de aparições no Top 5)")

    for i in range(len(variaveis)):
        for j in range(len(anos)):
            if matriz[i, j] > 0:
                ax.text(j, i, f"{matriz[i, j]:.3f}", ha="center", va="center", fontsize=8)

    cbar = fig.colorbar(imagem, ax=ax)
    cbar.set_label("Importância da variável")
    ax.set_title("Importância das Variáveis no Top 5 por Ano", fontsize=14, pad=15)

    ax.set_xticks(np.arange(-0.5, len(anos), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(variaveis), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)

    salvar(caminho_saida)
