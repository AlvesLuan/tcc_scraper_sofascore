"""01 - Matriz de presença (Sim/Não) no Top 5 por ano."""

import matplotlib.pyplot as plt
import numpy as np

from .base import salvar


def matriz_presenca(anos, variaveis, top5_por_ano, caminho_saida):
    matriz = np.array(
        [[1 if v in top5_por_ano[ano] else 0 for ano in anos] for v in variaveis]
    )

    fig, ax = plt.subplots(figsize=(12, max(5, len(variaveis) * 0.45)))

    ax.imshow(matriz, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(anos)))
    ax.set_xticklabels(anos)
    ax.set_yticks(np.arange(len(variaveis)))
    ax.set_yticklabels(variaveis)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Variável")
    ax.set_title("Presença das Variáveis no Top 5 por Ano")

    for i in range(len(variaveis)):
        for j in range(len(anos)):
            texto = "Sim" if matriz[i, j] == 1 else "Não"
            ax.text(j, i, texto, ha="center", va="center", fontsize=8)

    salvar(caminho_saida)
