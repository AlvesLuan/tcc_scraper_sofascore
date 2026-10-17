"""06 - Matriz de bolinhas: posição no Top 5, uma cor fixa por variável."""

import matplotlib.pyplot as plt
import numpy as np

from .base import salvar


def matriz_bolinhas(anos, variaveis, rankings, cores, caminho_saida):
    fig, ax = plt.subplots(figsize=(12, max(5, len(variaveis) * 0.5)))

    for i, variavel in enumerate(variaveis):
        cor = cores[variavel]
        for ano in anos:
            posicao = rankings[ano].get(variavel)
            if posicao is not None and posicao <= 5:
                tamanho = 300 - (posicao - 1) * 50
                ax.scatter(ano, i, s=tamanho, color=cor)
                ax.text(
                    ano, i, str(posicao), ha="center", va="center",
                    fontsize=8, color="white",
                )

    ax.set_xticks(anos)
    ax.set_yticks(np.arange(len(variaveis)))
    ax.set_yticklabels(variaveis)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Variável")
    ax.set_title("Posição das Variáveis no Top 5 por Ano")
    ax.grid(linestyle="--", alpha=0.3)

    salvar(caminho_saida)
