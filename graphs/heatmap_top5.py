import os
import re
import glob
import matplotlib.pyplot as plt
import numpy as np

# ----------------------------------------------------------------------------
# CONFIGURAÇÃO
# ----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_PATH = os.path.join(BASE_DIR, "..", "graphs", "arvore-5-depth-5-splits")

# Padrão esperado do nome do arquivo:
# "AAAA-importancia_variaveis_....txt"
FILENAME_PATTERN = re.compile(
    r"^(\d{4})-importancia_variaveis_.*\.txt$"
)

# Padrão de cada linha:
# "nome_da_variavel: 0.1234"
LINE_PATTERN = re.compile(
    r"^([A-Za-zÀ-ÿ0-9_]+)\s*:\s*([-+]?\d*\.?\d+)$"
)


def carregar_dados(txt_path):
    """
    Lê todos os arquivos "AAAA-importancia_variaveis_*.txt"
    e retorna:

        {
            ano: {
                variavel: importancia,
                ...
            },
            ...
        }
    """

    dados_por_ano = {}

    arquivos = glob.glob(os.path.join(txt_path, "*.txt"))

    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo .txt encontrado em: "
            f"{os.path.abspath(txt_path)}"
        )

    for caminho_arquivo in arquivos:

        nome_arquivo = os.path.basename(caminho_arquivo)

        match = FILENAME_PATTERN.match(nome_arquivo)

        if not match:
            print(
                f"[aviso] Arquivo ignorado "
                f"(nome fora do padrão): {nome_arquivo}"
            )
            continue

        ano = int(match.group(1))
        variaveis = {}

        with open(caminho_arquivo, "r", encoding="utf-8") as f:

            for linha in f:

                linha = linha.strip()

                linha_match = LINE_PATTERN.match(linha)

                if linha_match:
                    nome_var, valor = linha_match.groups()
                    variaveis[nome_var] = float(valor)

        if not variaveis:
            print(
                f"[aviso] Nenhuma variável encontrada "
                f"em: {nome_arquivo}"
            )
            continue

        dados_por_ano[ano] = variaveis

    return dados_por_ano


def montar_heatmap(dados_por_ano):
    """
    Monta a matriz de importância para o heatmap.

    São consideradas somente as variáveis que apareceram
    no Top 5 em pelo menos um ano.

    As variáveis são ordenadas pela quantidade de vezes
    que apareceram no Top 5.
    """

    anos = sorted(dados_por_ano.keys())

    # ------------------------------------------------------------------------
    # Descobrir quais variáveis estiveram no Top 5 em cada ano
    # ------------------------------------------------------------------------
    top5_por_ano = {}

    for ano in anos:

        variaveis = dados_por_ano[ano]

        ordenadas = sorted(
            variaveis.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top5_por_ano[ano] = {
            variavel
            for variavel, importancia in ordenadas[:5]
        }

    # ------------------------------------------------------------------------
    # Contar quantas vezes cada variável apareceu no Top 5
    # ------------------------------------------------------------------------
    frequencia_top5 = {}

    for ano in anos:

        for variavel in top5_por_ano[ano]:

            frequencia_top5[variavel] = (
                frequencia_top5.get(variavel, 0) + 1
            )

    # ------------------------------------------------------------------------
    # Ordenar:
    # 1º - maior frequência no Top 5
    # 2º - nome da variável
    # ------------------------------------------------------------------------
    variaveis = sorted(
        frequencia_top5.keys(),
        key=lambda x: (-frequencia_top5[x], x)
    )

    # ------------------------------------------------------------------------
    # Montar matriz
    # ------------------------------------------------------------------------
    matriz = []

    for variavel in variaveis:

        linha = []

        for ano in anos:

            # Se a variável não existir naquele ano, considera 0
            importancia = dados_por_ano[ano].get(
                variavel,
                0
            )

            # Se não estiver no Top 5, também deixa 0
            if variavel not in top5_por_ano[ano]:
                importancia = 0

            linha.append(importancia)

        matriz.append(linha)

    return (
        anos,
        variaveis,
        np.array(matriz),
        frequencia_top5
    )


def plotar_heatmap(
    anos,
    variaveis,
    matriz,
    frequencia_top5,
    caminho_saida=None
):
    """
    Gera o heatmap.

    A intensidade da célula representa a importância
    da variável naquele ano.

    Células com valor 0 significam que a variável
    não esteve no Top 5 naquele ano.
    """

    # Altura proporcional à quantidade de variáveis
    altura = max(6, len(variaveis) * 0.45)

    fig, ax = plt.subplots(
        figsize=(12, altura)
    )

    # ------------------------------------------------------------------------
    # Heatmap
    # ------------------------------------------------------------------------
    imagem = ax.imshow(
        matriz,
        aspect="auto",
        cmap="Blues",
        interpolation="nearest"
    )

    # ------------------------------------------------------------------------
    # Eixo X
    # ------------------------------------------------------------------------
    ax.set_xticks(
        np.arange(len(anos))
    )

    ax.set_xticklabels(
        anos
    )

    ax.set_xlabel(
        "Ano"
    )

    # ------------------------------------------------------------------------
    # Eixo Y
    # ------------------------------------------------------------------------
    ax.set_yticks(
        np.arange(len(variaveis))
    )

    ax.set_yticklabels(
        [
            f"{variavel} ({frequencia_top5[variavel]}x)"
            for variavel in variaveis
        ]
    )

    ax.set_ylabel(
        "Variável (nº de aparições no Top 5)"
    )

    # ------------------------------------------------------------------------
    # Valores dentro das células
    # ------------------------------------------------------------------------
    for i in range(len(variaveis)):

        for j in range(len(anos)):

            valor = matriz[i, j]

            if valor > 0:

                ax.text(
                    j,
                    i,
                    f"{valor:.3f}",
                    ha="center",
                    va="center",
                    fontsize=8
                )

    # ------------------------------------------------------------------------
    # Barra de escala
    # ------------------------------------------------------------------------
    cbar = fig.colorbar(
        imagem,
        ax=ax
    )

    cbar.set_label(
        "Importância da variável"
    )

    # ------------------------------------------------------------------------
    # Título
    # ------------------------------------------------------------------------
    ax.set_title(
        "Importância das Variáveis no Top 5 por Ano",
        fontsize=14,
        pad=15
    )

    # ------------------------------------------------------------------------
    # Grade
    # ------------------------------------------------------------------------
    ax.set_xticks(
        np.arange(-0.5, len(anos), 1),
        minor=True
    )

    ax.set_yticks(
        np.arange(-0.5, len(variaveis), 1),
        minor=True
    )

    ax.grid(
        which="minor",
        color="white",
        linestyle="-",
        linewidth=1
    )

    ax.tick_params(
        which="minor",
        bottom=False,
        left=False
    )

    plt.tight_layout()

    # ------------------------------------------------------------------------
    # Salvar
    # ------------------------------------------------------------------------
    if caminho_saida:

        plt.savefig(
            caminho_saida,
            dpi=200,
            bbox_inches="tight"
        )

        print(
            f"Gráfico salvo em: {caminho_saida}"
        )

    plt.show()


# ----------------------------------------------------------------------------
# EXECUÇÃO
# ----------------------------------------------------------------------------

if __name__ == "__main__":

    # Carrega os arquivos
    dados_por_ano = carregar_dados(
        TXT_PATH
    )

    # Monta matriz do heatmap
    (
        anos,
        variaveis,
        matriz,
        frequencia_top5
    ) = montar_heatmap(
        dados_por_ano
    )

    # Informações no terminal
    print(
        f"Anos encontrados: {anos}"
    )

    print("\nVariáveis consideradas:")
    print("-" * 60)

    for variavel in variaveis:

        print(
            f"{variavel}: "
            f"{frequencia_top5[variavel]} "
            f"vez(es) no Top 5"
        )

    # Caminho de saída
    caminho_saida = os.path.join(
        BASE_DIR,
        "heatmap_importancia_top5.png"
    )

    # Gera gráfico
    plotar_heatmap(
        anos,
        variaveis,
        matriz,
        frequencia_top5,
        caminho_saida
    )

