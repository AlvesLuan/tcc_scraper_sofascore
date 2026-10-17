"""02 - Frequência de cada variável no Top 5 (barras horizontais)."""

import matplotlib.pyplot as plt

from .base import salvar


def frequencia_top5(variaveis, frequencia, cores, caminho_saida):
    valores = [frequencia[v] for v in variaveis]
    variaveis_plot = variaveis[::-1]
    valores_plot = valores[::-1]
    cores_plot = [cores[v] for v in variaveis_plot]

    fig, ax = plt.subplots(figsize=(10, max(5, len(variaveis) * 0.45)))
    barras = ax.barh(variaveis_plot, valores_plot, color=cores_plot)

    ax.set_xlabel("Número de aparições no Top 5")
    ax.set_ylabel("Variável")
    ax.set_title("Frequência das Variáveis no Top 5")
    ax.set_xlim(0, max(valores) + 1)

    for barra, valor in zip(barras, valores_plot):
        ax.text(
            barra.get_width() + 0.1,
            barra.get_y() + barra.get_height() / 2,
            str(valor),
            va="center",
        )

    ax.grid(axis="x", linestyle="--", alpha=0.4)
    salvar(caminho_saida)
