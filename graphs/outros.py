import os
import re
import glob

import matplotlib.pyplot as plt
import numpy as np


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TXT_PATH = os.path.join(
    BASE_DIR,
    "..",
    "graphs",
    "arvore-5-depth-5-splits"
)


# ============================================================================
# PADRÕES DOS ARQUIVOS
# ============================================================================

FILENAME_PATTERN = re.compile(
    r"^(\d{4})-importancia_variaveis_.*\.txt$"
)

LINE_PATTERN = re.compile(
    r"^([A-Za-zÀ-ÿ0-9_]+)\s*:\s*"
    r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)$"
)


# ============================================================================
# 1. CARREGAR DADOS
# ============================================================================

def carregar_dados(txt_path):

    dados_por_ano = {}

    arquivos = glob.glob(
        os.path.join(txt_path, "*.txt")
    )

    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo .txt encontrado em:\n"
            f"{os.path.abspath(txt_path)}"
        )

    for caminho_arquivo in arquivos:

        nome_arquivo = os.path.basename(caminho_arquivo)

        match = FILENAME_PATTERN.match(nome_arquivo)

        if not match:
            print(
                f"[aviso] Arquivo ignorado: "
                f"{nome_arquivo}"
            )
            continue

        ano = int(match.group(1))

        variaveis = {}

        with open(
            caminho_arquivo,
            "r",
            encoding="utf-8"
        ) as arquivo:

            for linha in arquivo:

                linha = linha.strip()

                match_linha = LINE_PATTERN.match(linha)

                if match_linha:

                    nome_variavel = match_linha.group(1)

                    importancia = float(
                        match_linha.group(2)
                    )

                    variaveis[nome_variavel] = importancia

        if variaveis:

            dados_por_ano[ano] = variaveis

        else:

            print(
                f"[aviso] Nenhuma variável encontrada: "
                f"{nome_arquivo}"
            )

    return dados_por_ano


# ============================================================================
# 2. CALCULAR RANKING E TOP 5
# ============================================================================

def calcular_rankings(dados_por_ano):

    anos = sorted(dados_por_ano.keys())

    rankings = {}
    top5_por_ano = {}

    for ano in anos:

        variaveis = dados_por_ano[ano]

        ordenadas = sorted(
            variaveis.items(),
            key=lambda item: item[1],
            reverse=True
        )

        # Ranking completo
        rankings[ano] = {
            variavel: posicao
            for posicao, (variavel, importancia)
            in enumerate(ordenadas, start=1)
        }

        # Top 5
        top5_por_ano[ano] = [
            variavel
            for variavel, importancia
            in ordenadas[:5]
        ]

    return anos, rankings, top5_por_ano


# ============================================================================
# 3. FREQUÊNCIA NO TOP 5
# ============================================================================

def calcular_frequencia(top5_por_ano):

    frequencia = {}

    for ano, top5 in top5_por_ano.items():

        for variavel in top5:

            frequencia[variavel] = (
                frequencia.get(variavel, 0) + 1
            )

    # Ordenar da maior frequência para a menor
    variaveis = sorted(
        frequencia.keys(),
        key=lambda v: (-frequencia[v], v)
    )

    return variaveis, frequencia


# ============================================================================
# 4. MATRIZ DE PRESENÇA
# ============================================================================

def grafico_matriz_presenca(
    anos,
    variaveis,
    top5_por_ano,
    caminho_saida
):

    matriz = []

    for variavel in variaveis:

        linha = []

        for ano in anos:

            if variavel in top5_por_ano[ano]:

                linha.append(1)

            else:

                linha.append(0)

        matriz.append(linha)

    matriz = np.array(matriz)

    altura = max(
        5,
        len(variaveis) * 0.45
    )

    fig, ax = plt.subplots(
        figsize=(12, altura)
    )

    ax.imshow(
        matriz,
        aspect="auto",
        cmap="Blues",
        vmin=0,
        vmax=1
    )

    ax.set_xticks(
        np.arange(len(anos))
    )

    ax.set_xticklabels(
        anos
    )

    ax.set_yticks(
        np.arange(len(variaveis))
    )

    ax.set_yticklabels(
        variaveis
    )

    ax.set_xlabel("Ano")
    ax.set_ylabel("Variável")

    ax.set_title(
        "Presença das Variáveis no Top 5 por Ano"
    )

    # Escrever Sim / Não
    for i in range(len(variaveis)):

        for j in range(len(anos)):

            texto = (
                "Sim"
                if matriz[i, j] == 1
                else "Não"
            )

            ax.text(
                j,
                i,
                texto,
                ha="center",
                va="center",
                fontsize=8
            )

    plt.tight_layout()

    plt.savefig(
        caminho_saida,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Salvo: {caminho_saida}"
    )


# ============================================================================
# 5. BARRAS HORIZONTAIS
# ============================================================================

def grafico_frequencia(
    variaveis,
    frequencia,
    caminho_saida
):

    valores = [
        frequencia[v]
        for v in variaveis
    ]

    # Inverter para maior ficar no topo
    variaveis_plot = variaveis[::-1]
    valores_plot = valores[::-1]

    fig, ax = plt.subplots(
        figsize=(10, max(5, len(variaveis) * 0.45))
    )

    barras = ax.barh(
        variaveis_plot,
        valores_plot
    )

    ax.set_xlabel(
        "Número de aparições no Top 5"
    )

    ax.set_ylabel(
        "Variável"
    )

    ax.set_title(
        "Frequência das Variáveis no Top 5"
    )

    ax.set_xlim(
        0,
        max(valores) + 1
    )

    # Valores no final das barras
    for barra, valor in zip(
        barras,
        valores_plot
    ):

        ax.text(
            barra.get_width() + 0.1,
            barra.get_y() + barra.get_height() / 2,
            str(valor),
            va="center"
        )

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.4
    )

    plt.tight_layout()

    plt.savefig(
        caminho_saida,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Salvo: {caminho_saida}"
    )


# ============================================================================
# 6. DUMBBELL / RANKING POR TEMPORADA
# ============================================================================

def grafico_dumbbell(
    anos,
    variaveis,
    rankings,
    caminho_saida
):

    fig, ax = plt.subplots(
        figsize=(12, max(6, len(variaveis) * 0.5))
    )

    # Apenas variáveis que apareceram no Top 5
    for i, variavel in enumerate(variaveis):

        posicoes = []

        anos_validos = []

        for ano in anos:

            posicao = rankings[ano].get(
                variavel
            )

            if posicao is not None:

                # Mostrar apenas até posição 5
                if posicao <= 5:

                    posicoes.append(posicao)
                    anos_validos.append(ano)

        if not posicoes:
            continue

        # Linha horizontal conectando primeira e última aparição
        if len(anos_validos) > 1:

            ax.plot(
                [anos_validos[0], anos_validos[-1]],
                [i, i],
                linewidth=2,
                alpha=0.4
            )

        # Pontos
        ax.scatter(
            anos_validos,
            [i] * len(anos_validos),
            s=80
        )

        # Mostrar posição ao lado do ponto
        for ano, posicao in zip(
            anos_validos,
            posicoes
        ):

            ax.text(
                ano,
                i + 0.15,
                str(posicao),
                ha="center",
                va="bottom",
                fontsize=7
            )

    ax.set_yticks(
        np.arange(len(variaveis))
    )

    ax.set_yticklabels(
        variaveis
    )

    ax.set_xticks(
        anos
    )

    ax.set_xlabel(
        "Ano"
    )

    ax.set_ylabel(
        "Variável"
    )

    ax.set_title(
        "Posição das Variáveis no Top 5 por Temporada"
    )

    # Como 1 é melhor que 5
    ax.set_ylim(
        -1,
        len(variaveis)
    )

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.4
    )

    plt.tight_layout()

    plt.savefig(
        caminho_saida,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Salvo: {caminho_saida}"
    )


# ============================================================================
# 7. RANKING POR ANO
# ============================================================================

def grafico_ranking_por_ano(
    anos,
    top5_por_ano,
    caminho_saida
):

    fig, ax = plt.subplots(
        figsize=(12, 8)
    )

    # Cada ano recebe uma posição no eixo X
    x = np.arange(len(anos))

    # Todas as posições do Top 5
    for posicao in range(5):

        y = []

        for ano in anos:

            if len(top5_por_ano[ano]) > posicao:

                variavel = top5_por_ano[ano][posicao]

            else:

                variavel = ""

            y.append(
                variavel
            )

        # Criar uma linha para cada posição
        ax.plot(
            x,
            [posicao] * len(anos),
            marker="o",
            linewidth=1
        )

        # Escrever nome da variável
        for i, variavel in enumerate(y):

            if variavel:

                ax.text(
                    i,
                    posicao,
                    variavel,
                    ha="center",
                    va="center",
                    fontsize=7
                )

    ax.set_xticks(x)

    ax.set_xticklabels(anos)

    ax.set_yticks(
        np.arange(5)
    )

    ax.set_yticklabels(
        [
            "1º",
            "2º",
            "3º",
            "4º",
            "5º"
        ]
    )

    ax.invert_yaxis()

    ax.set_xlabel(
        "Ano"
    )

    ax.set_ylabel(
        "Posição no ranking"
    )

    ax.set_title(
        "Ranking das Variáveis por Temporada"
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    plt.tight_layout()

    plt.savefig(
        caminho_saida,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Salvo: {caminho_saida}"
    )


# ============================================================================
# 8. MATRIZ DE BOLINHAS
# ============================================================================

def grafico_matriz_bolinhas(
    anos,
    variaveis,
    rankings,
    caminho_saida
):

    fig, ax = plt.subplots(
        figsize=(12, max(5, len(variaveis) * 0.5))
    )

    for i, variavel in enumerate(variaveis):

        for j, ano in enumerate(anos):

            posicao = rankings[ano].get(
                variavel
            )

            # Só desenha se estiver no Top 5
            if posicao is not None and posicao <= 5:

                # Quanto melhor a posição,
                # maior a bolinha
                tamanho = (
                    300 - (posicao - 1) * 50
                )

                ax.scatter(
                    ano,
                    i,
                    s=tamanho
                )

                # Mostrar posição dentro da bolinha
                ax.text(
                    ano,
                    i,
                    str(posicao),
                    ha="center",
                    va="center",
                    fontsize=8
                )

    ax.set_xticks(
        anos
    )

    ax.set_yticks(
        np.arange(len(variaveis))
    )

    ax.set_yticklabels(
        variaveis
    )

    ax.set_xlabel(
        "Ano"
    )

    ax.set_ylabel(
        "Variável"
    )

    ax.set_title(
        "Posição das Variáveis no Top 5 por Ano"
    )

    ax.grid(
        linestyle="--",
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        caminho_saida,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Salvo: {caminho_saida}"
    )


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":

    # ------------------------------------------------------------------------
    # Carregar dados
    # ------------------------------------------------------------------------

    dados_por_ano = carregar_dados(
        TXT_PATH
    )

    # ------------------------------------------------------------------------
    # Calcular rankings
    # ------------------------------------------------------------------------

    (
        anos,
        rankings,
        top5_por_ano
    ) = calcular_rankings(
        dados_por_ano
    )

    # ------------------------------------------------------------------------
    # Calcular frequência
    # ------------------------------------------------------------------------

    (
        variaveis,
        frequencia
    ) = calcular_frequencia(
        top5_por_ano
    )

    # ------------------------------------------------------------------------
    # Informações no terminal
    # ------------------------------------------------------------------------

    print(
        f"\nAnos encontrados: {anos}"
    )

    print(
        "\nTOP 5 POR ANO:"
    )

    print(
        "-" * 60
    )

    for ano in anos:

        print(
            f"{ano}: "
            f"{', '.join(top5_por_ano[ano])}"
        )

    print(
        "\nFREQUÊNCIA NO TOP 5:"
    )

    print(
        "-" * 60
    )

    for variavel in variaveis:

        print(
            f"{variavel}: "
            f"{frequencia[variavel]}x"
        )

    # ------------------------------------------------------------------------
    # Pasta de saída
    # ------------------------------------------------------------------------

    PASTA_SAIDA = os.path.join(
        BASE_DIR,
        "graficos_top5"
    )

    os.makedirs(
        PASTA_SAIDA,
        exist_ok=True
    )

    # ------------------------------------------------------------------------
    # 1. Matriz de presença
    # ------------------------------------------------------------------------

    grafico_matriz_presenca(
        anos,
        variaveis,
        top5_por_ano,
        os.path.join(
            PASTA_SAIDA,
            "01_matriz_presenca.png"
        )
    )

    # ------------------------------------------------------------------------
    # 2. Barras horizontais
    # ------------------------------------------------------------------------

    grafico_frequencia(
        variaveis,
        frequencia,
        os.path.join(
            PASTA_SAIDA,
            "02_frequencia_top5.png"
        )
    )

    # ------------------------------------------------------------------------
    # 3. Dumbbell / ranking por temporada
    # ------------------------------------------------------------------------

    grafico_dumbbell(
        anos,
        variaveis,
        rankings,
        os.path.join(
            PASTA_SAIDA,
            "03_dumbbell_ranking.png"
        )
    )

    # ------------------------------------------------------------------------
    # 4. Ranking por ano
    # ------------------------------------------------------------------------

    grafico_ranking_por_ano(
        anos,
        top5_por_ano,
        os.path.join(
            PASTA_SAIDA,
            "04_ranking_por_ano.png"
        )
    )

    # ------------------------------------------------------------------------
    # 5. Matriz de bolinhas
    # ------------------------------------------------------------------------

    grafico_matriz_bolinhas(
        anos,
        variaveis,
        rankings,
        os.path.join(
            PASTA_SAIDA,
            "05_matriz_bolinhas.png"
        )
    )

    print(
        "\nTodos os gráficos foram gerados com sucesso!"
    )

