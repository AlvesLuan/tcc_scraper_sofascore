"""03 - Evolução do valor de importância ao longo dos anos (linhas)."""

import matplotlib.pyplot as plt
import numpy as np

from .base import salvar


def evolucao_importancia(anos, dados_por_ano, variaveis, cores, caminho_saida):
    """
    Valor bruto de importância (feature_importances_) por ano, restrito às
    variáveis que estiveram no Top 5 em pelo menos um ano (mesmo recorte dos
    demais gráficos).
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    for variavel in variaveis:
        valores = [dados_por_ano[ano].get(variavel) for ano in anos]
        # np.nan deixa um buraco na linha nos anos em que a variável não aparece
        valores = [np.nan if v is None else v for v in valores]
        ax.plot(anos, valores, marker="o", label=variavel, color=cores[variavel])

    ax.set_title("Evolução da Importância das Variáveis do Top 5")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Importância (feature_importances_)")
    ax.set_xticks(anos)
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))
    ax.grid(True, linestyle="--", alpha=0.5)

    salvar(caminho_saida)
