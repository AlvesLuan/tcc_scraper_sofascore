"""08 e 09 - Boxplots da importância (distribuição ao longo dos anos).

Como encaixar um boxplot nestes dados: cada ano gera UM valor de importância
por variável. O boxplot então resume, para cada variável, como esse valor
variou entre as temporadas (mediana, quartis e dispersão). Variáveis estáveis
têm caixa estreita; variáveis que oscilam muito têm caixa larga.

Cuidado: são no máximo ~11 pontos por variável (um por ano), então a caixa é
uma síntese pobre se mostrada sozinha. Por isso os pontos reais (um por ano)
são desenhados por cima, e o rótulo mostra "n" (anos em que a variável entrou
no modelo / apareceu no arquivo).
"""

import matplotlib.pyplot as plt
import numpy as np

from .analise import grupo_da_variavel
from .base import salvar

COR_PADRAO = "#8c8c8c"


def _desenhar_boxplot(ax, series, rotulos, cores_caixas, horizontal=True):
    """Boxplot + pontos individuais (jitter) para séries de tamanhos diferentes."""
    posicoes = np.arange(1, len(series) + 1)
    opcoes = dict(
        positions=posicoes, patch_artist=True, widths=0.55, showfliers=False,
        medianprops={"color": "black", "linewidth": 1.8},
    )
    try:
        # matplotlib >= 3.10: `orientation` (o parâmetro `vert` está obsoleto)
        caixas = ax.boxplot(
            series, orientation="horizontal" if horizontal else "vertical", **opcoes
        )
    except TypeError:
        # matplotlib < 3.10 não conhece `orientation`
        caixas = ax.boxplot(series, vert=not horizontal, **opcoes)

    for caixa, cor in zip(caixas["boxes"], cores_caixas):
        caixa.set_facecolor(cor)
        caixa.set_alpha(0.45)

    rng = np.random.default_rng(0)  # jitter reprodutível
    for pos, valores, cor in zip(posicoes, series, cores_caixas):
        jitter = rng.uniform(-0.14, 0.14, size=len(valores))
        if horizontal:
            ax.scatter(valores, pos + jitter, s=22, color=cor, edgecolor="black",
                       linewidth=0.5, zorder=3)
        else:
            ax.scatter(pos + jitter, valores, s=22, color=cor, edgecolor="black",
                       linewidth=0.5, zorder=3)

    if horizontal:
        ax.set_yticks(posicoes)
        ax.set_yticklabels(rotulos)
        ax.grid(axis="x", linestyle="--", alpha=0.4)
    else:
        ax.set_xticks(posicoes)
        ax.set_xticklabels(rotulos, rotation=20, ha="right")
        ax.grid(axis="y", linestyle="--", alpha=0.4)


def boxplot_importancia(anos, dados_por_ano, cores, caminho_saida, min_anos=3):
    """
    Um boxplot por variável: distribuição da importância entre os anos em que
    ela aparece nos arquivos. Variáveis com menos de `min_anos` observações
    ficam de fora (uma caixa com 1-2 pontos não diz nada).
    Ordenado pela mediana (mais importante no topo).
    """
    por_variavel = {}
    for ano in anos:
        for variavel, valor in dados_por_ano[ano].items():
            por_variavel.setdefault(variavel, []).append(valor)

    incluidas = {v: vals for v, vals in por_variavel.items() if len(vals) >= min_anos}
    excluidas = sorted(set(por_variavel) - set(incluidas))

    # Em boxplot horizontal a posição 1 fica embaixo: ordem crescente de
    # mediana deixa a variável mais importante no topo.
    ordem = sorted(incluidas, key=lambda v: np.median(incluidas[v]))
    series = [incluidas[v] for v in ordem]
    rotulos = [f"{v} (n={len(incluidas[v])})" for v in ordem]
    cores_caixas = [cores.get(v, COR_PADRAO) for v in ordem]

    fig, ax = plt.subplots(figsize=(10, max(5, len(ordem) * 0.6)))
    _desenhar_boxplot(ax, series, rotulos, cores_caixas, horizontal=True)

    ax.set_xlabel("Importância (feature_importances_)")
    ax.set_ylabel("Variável (n = anos com a variável no modelo)")
    ax.set_title("Distribuição da Importância das Variáveis entre os Anos")

    if excluidas:
        ax.annotate(
            f"Omitidas (menos de {min_anos} anos): {', '.join(excluidas)}",
            xy=(0, -0.2), xycoords="axes fraction", fontsize=8, color="dimgray",
        )

    salvar(caminho_saida)


def boxplot_grupos(anos, dados_por_ano, caminho_saida):
    """
    Um boxplot por GRUPO de variáveis (idade, altura, público, condição,
    calendário...). Em cada ano soma-se a importância das variáveis do grupo
    (útil p/ juntar as dummies de dia da semana) e o boxplot resume essas
    11 somas anuais.

    Atenção: um grupo sem nenhuma variável no arquivo de um ano conta como 0
    naquele ano (o modelo não a usou), o que puxa a mediana para baixo.
    """
    # Primeiro descobre TODOS os grupos de TODOS os anos; assim, um grupo que
    # só aparece a partir de certo ano (ex.: Calendário, a partir de 2017)
    # também recebe 0 nos anos anteriores e fica sempre com um ponto por ano.
    todos_grupos = {
        grupo_da_variavel(v) for ano in anos for v in dados_por_ano[ano]
    }
    grupos = {g: [] for g in todos_grupos}
    for ano in anos:
        somas_ano = {}
        for variavel, valor in dados_por_ano[ano].items():
            g = grupo_da_variavel(variavel)
            somas_ano[g] = somas_ano.get(g, 0.0) + valor
        for g in todos_grupos:
            grupos[g].append(somas_ano.get(g, 0.0))

    ordem = sorted(grupos, key=lambda g: np.median(grupos[g]), reverse=True)
    series = [grupos[g] for g in ordem]

    mapa = plt.get_cmap("Set2")
    cores_caixas = [mapa(i % 8) for i in range(len(ordem))]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    _desenhar_boxplot(ax, series, ordem, cores_caixas, horizontal=False)

    ax.set_ylabel("Importância somada do grupo no ano")
    ax.set_xlabel("Grupo de variáveis")
    ax.set_title(f"Distribuição da Importância por Grupo de Variáveis ({anos[0]}-{anos[-1]})")

    salvar(caminho_saida)