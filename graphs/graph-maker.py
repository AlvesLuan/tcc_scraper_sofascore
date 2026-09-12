"""
Gráficos de evolução e ranking da importância das variáveis por ano.

Este script junta e corrige o conteúdo de três scripts anteriores:
- evolucao_importancia.py
- heatmap_top5.py
- outros.py

Lê todos os arquivos "AAAA-importancia_variaveis_*.txt" de uma pasta e gera:
    01_matriz_presenca.png       - Sim/Não no Top 5 por ano
    02_frequencia_top5.png       - quantas vezes cada variável apareceu no Top 5
    03_evolucao_importancia.png  - evolução do valor de importância ao longo dos anos
    04_dumbbell_ranking.png      - posição no Top 5 por ano (uma linha por variável)
    05_bump_chart.png            - "corrida" de posições no Top 5, ano a ano
    06_matriz_bolinhas.png       - posição no Top 5 (bolinhas), uma cor fixa por variável
    07_heatmap_importancia.png   - valor de importância das variáveis do Top 5, em heatmap
"""

import os
import re
import glob

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_PATH = os.path.join(BASE_DIR, "..", "graphs", "arvore-5-depth-5-splits")
PASTA_SAIDA = os.path.join(BASE_DIR, "graficos_top5")

# Nome esperado: "AAAA-importancia_variaveis_....txt"
FILENAME_PATTERN = re.compile(r"^(\d{4})-importancia_variaveis_.*\.txt$")

# Linha esperada: "nome_da_variavel: 0.1234" (aceita notação científica e ".1234")
LINE_PATTERN = re.compile(
    r"^([A-Za-zÀ-ÿ0-9_]+)\s*:\s*"
    r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)$"
)


# ============================================================================
# 1. CARREGAR DADOS
# ============================================================================

def carregar_dados(txt_path):
    """
    Lê todos os arquivos "AAAA-importancia_variaveis_*.txt" e retorna:
        {ano: {variavel: importancia, ...}, ...}
    """
    dados_por_ano = {}
    arquivos = glob.glob(os.path.join(txt_path, "*.txt"))

    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo .txt encontrado em:\n{os.path.abspath(txt_path)}"
        )

    for caminho_arquivo in arquivos:
        nome_arquivo = os.path.basename(caminho_arquivo)
        match = FILENAME_PATTERN.match(nome_arquivo)

        if not match:
            print(f"[aviso] Arquivo ignorado (nome fora do padrão): {nome_arquivo}")
            continue

        ano = int(match.group(1))
        variaveis = {}

        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha_match = LINE_PATTERN.match(linha.strip())
                if linha_match:
                    nome_var, valor = linha_match.groups()
                    variaveis[nome_var] = float(valor)

        if variaveis:
            dados_por_ano[ano] = variaveis
        else:
            print(f"[aviso] Nenhuma variável encontrada em: {nome_arquivo}")

    return dados_por_ano


# ============================================================================
# 2. RANKINGS E TOP 5
# ============================================================================

def calcular_rankings(dados_por_ano):
    """
    Retorna:
        anos: lista de anos em ordem crescente
        rankings: {ano: {variavel: posicao (1 = mais importante)}}
        top5_por_ano: {ano: [variavel_1o, variavel_2o, ..., variavel_5o]}
    """
    anos = sorted(dados_por_ano.keys())
    rankings = {}
    top5_por_ano = {}

    for ano in anos:
        ordenadas = sorted(
            dados_por_ano[ano].items(), key=lambda item: item[1], reverse=True
        )
        rankings[ano] = {
            variavel: posicao
            for posicao, (variavel, _importancia) in enumerate(ordenadas, start=1)
        }
        top5_por_ano[ano] = [variavel for variavel, _imp in ordenadas[:5]]

    return anos, rankings, top5_por_ano


def calcular_frequencia(top5_por_ano):
    """
    Conta quantas vezes cada variável apareceu no Top 5 e devolve a lista de
    variáveis ordenada da mais para a menos frequente.
    """
    frequencia = {}
    for top5 in top5_por_ano.values():
        for variavel in top5:
            frequencia[variavel] = frequencia.get(variavel, 0) + 1

    variaveis = sorted(frequencia.keys(), key=lambda v: (-frequencia[v], v))
    return variaveis, frequencia


def montar_cores(variaveis):
    """
    Define UMA cor fixa por variável, reaproveitada em todos os gráficos.

    Correção: nos scripts originais, cada chamada de scatter()/plot() pegava
    a próxima cor do ciclo padrão do matplotlib, então a MESMA variável podia
    aparecer com cores diferentes de um ano para o outro, ou de um gráfico
    para o outro. Aqui a cor é decidida uma única vez, por variável.
    """
    n = len(variaveis)
    mapa = cm.get_cmap("tab10" if n <= 10 else "tab20", n)
    return {variavel: mapa(i) for i, variavel in enumerate(variaveis)}


def segmentos_consecutivos(anos_validos):
    """
    Recebe uma lista ordenada de anos em que uma variável esteve no Top 5 e
    devolve uma lista de sublistas, cada uma com uma sequência de anos
    consecutivos (sem buracos).

    Correção: os gráficos originais desenhavam uma única linha reta do
    primeiro ao último ano em que a variável aparecia no Top 5, mesmo quando
    ela tinha "sumido" do Top 5 em anos no meio do intervalo. Isso sugeria
    presença contínua onde na verdade havia uma lacuna. Separar em
    segmentos consecutivos faz a linha se interromper nos anos de ausência.
    """
    if not anos_validos:
        return []

    segmentos = [[anos_validos[0]]]
    for ano in anos_validos[1:]:
        if ano == segmentos[-1][-1] + 1:
            segmentos[-1].append(ano)
        else:
            segmentos.append([ano])
    return segmentos


# ============================================================================
# 3. MATRIZ DE PRESENÇA (Sim / Não)
# ============================================================================

def grafico_matriz_presenca(anos, variaveis, top5_por_ano, caminho_saida):
    matriz = np.array(
        [[1 if v in top5_por_ano[ano] else 0 for ano in anos] for v in variaveis]
    )

    altura = max(5, len(variaveis) * 0.45)
    fig, ax = plt.subplots(figsize=(12, altura))

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

    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {caminho_saida}")


# ============================================================================
# 4. FREQUÊNCIA (barras horizontais)
# ============================================================================

def grafico_frequencia(variaveis, frequencia, cores, caminho_saida):
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
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {caminho_saida}")


# ============================================================================
# 5. EVOLUÇÃO DA IMPORTÂNCIA (linha)
# ============================================================================

def grafico_evolucao_importancia(anos, dados_por_ano, variaveis, cores, caminho_saida):
    """
    Mostra o valor bruto de importância (feature_importances_) ao longo dos
    anos, restrito às variáveis que estiveram no Top 5 em pelo menos um ano.

    Correção/consistência: o script original plotava TODAS as variáveis que
    apareciam em qualquer arquivo, mesmo as que nunca chegaram perto de ser
    relevantes (o que lota a legenda e mistura, no mesmo gráfico, duas coisas
    diferentes das demais figuras, que só olham o Top 5). Aqui usamos o
    mesmo recorte de variáveis dos outros gráficos, para que todas as
    figuras do relatório sejam consistentes entre si.
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    for variavel in variaveis:
        valores = [dados_por_ano[ano].get(variavel) for ano in anos]
        # np.nan (e não None) garante que o matplotlib deixe um buraco na
        # linha nos anos em que a variável não aparece, sem erro de tipos.
        valores = [np.nan if v is None else v for v in valores]
        ax.plot(
            anos, valores, marker="o", label=variavel, color=cores[variavel]
        )

    ax.set_title("Evolução da Importância das Variáveis do Top 5")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Importância (feature_importances_)")
    ax.set_xticks(anos)
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {caminho_saida}")


# ============================================================================
# 6. DUMBBELL / POSIÇÃO NO TOP 5 POR TEMPORADA
# ============================================================================

def grafico_dumbbell(anos, variaveis, rankings, cores, caminho_saida):
    """
    Uma linha por variável, ligando os anos em que ela esteve no Top 5.

    Correção: antes a linha ia direto do primeiro ao último ano em que a
    variável aparecia no Top 5, "pulando por cima" de anos em que ela tinha
    saído do Top 5 (sugerindo presença contínua onde havia lacuna). Agora a
    linha é desenhada em segmentos consecutivos, quebrando visualmente nos
    anos em que a variável não esteve no Top 5.
    """
    fig, ax = plt.subplots(figsize=(12, max(6, len(variaveis) * 0.5)))

    for i, variavel in enumerate(variaveis):
        anos_validos = [
            ano
            for ano in anos
            if rankings[ano].get(variavel) is not None
            and rankings[ano][variavel] <= 5
        ]
        if not anos_validos:
            continue

        cor = cores[variavel]

        for segmento in segmentos_consecutivos(anos_validos):
            if len(segmento) > 1:
                ax.plot(segmento, [i] * len(segmento), linewidth=2, alpha=0.5, color=cor)
            ax.scatter(segmento, [i] * len(segmento), s=80, color=cor, zorder=3)
            for ano in segmento:
                ax.text(
                    ano,
                    i + 0.15,
                    str(rankings[ano][variavel]),
                    ha="center",
                    va="bottom",
                    fontsize=7,
                )

    ax.set_yticks(np.arange(len(variaveis)))
    ax.set_yticklabels(variaveis)
    ax.set_xticks(anos)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Variável")
    ax.set_title("Posição das Variáveis no Top 5 por Temporada")
    ax.set_ylim(-1, len(variaveis))
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {caminho_saida}")


# ============================================================================
# 7. BUMP CHART (corrida de posições no Top 5)
# ============================================================================

def grafico_bump_chart(anos, variaveis, rankings, cores, caminho_saida, min_frequencia=2):
    """
    Substitui o antigo "grafico_ranking_por_ano".

    Bug do original: ele desenhava 5 linhas retas e FIXAS (uma para cada
    posição 1º-5º), e só escrevia o nome da variável como texto por cima.
    Como a linha não seguia variável nenhuma (ligava só a posição), o
    desenho sugeria uma continuidade que não existe — o "1º lugar" de 2015
    e o "1º lugar" de 2016 quase sempre são variáveis diferentes, mas
    apareciam ligados pela mesma linha azul.

    Aqui, cada variável ganha sua própria linha (com sua cor fixa), subindo
    ou descendo no eixo Y conforme sua posição no Top 5 mudou de fato, e a
    linha se interrompe nos anos em que ela saiu do Top 5.

    Nota de legibilidade: variáveis que aparecem no Top 5 só uma vez (min_
    frequencia) tendem a ocupar as posições mais baixas (4ª/5ª) de forma
    muito trocadiça — quase uma variável nova a cada ano. Rotular cada uma
    delas dentro do gráfico deixa a figura ilegível, então usamos legenda
    (com as mesmas cores dos outros gráficos) em vez de texto sobreposto,
    e por padrão só entram no gráfico variáveis com pelo menos duas
    aparições no Top 5. As demais continuam visíveis nos outros gráficos
    (matriz de presença, frequência, matriz de bolinhas).
    """
    variaveis_plot = [v for v in variaveis if frequencia_de(v, rankings, anos) >= min_frequencia]

    fig, ax = plt.subplots(figsize=(12, 7))

    for variavel in variaveis_plot:
        anos_validos = [
            ano
            for ano in anos
            if rankings[ano].get(variavel) is not None
            and rankings[ano][variavel] <= 5
        ]
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

    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {caminho_saida}")


def frequencia_de(variavel, rankings, anos):
    return sum(
        1 for ano in anos
        if rankings[ano].get(variavel) is not None and rankings[ano][variavel] <= 5
    )


# ============================================================================
# 8. MATRIZ DE BOLINHAS
# ============================================================================

def grafico_matriz_bolinhas(anos, variaveis, rankings, cores, caminho_saida):
    """
    Correção: no script original, cada chamada de ax.scatter(...) dentro do
    laço avançava sozinha o ciclo de cores padrão do matplotlib. Resultado:
    a MESMA variável aparecia com uma cor diferente em cada ano, sem
    nenhum significado (cor virava ruído visual). Agora cada variável tem
    uma cor fixa, igual à usada nos demais gráficos.
    """
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

    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {caminho_saida}")


# ============================================================================
# 9. HEATMAP DE IMPORTÂNCIA (Top 5)
# ============================================================================

def grafico_heatmap_importancia(anos, variaveis, dados_por_ano, top5_por_ano, frequencia, caminho_saida):
    matriz = np.zeros((len(variaveis), len(anos)))
    for i, variavel in enumerate(variaveis):
        for j, ano in enumerate(anos):
            if variavel in top5_por_ano[ano]:
                matriz[i, j] = dados_por_ano[ano].get(variavel, 0)

    altura = max(6, len(variaveis) * 0.45)
    fig, ax = plt.subplots(figsize=(12, altura))
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

    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {caminho_saida}")


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    dados_por_ano = carregar_dados(TXT_PATH)
    anos, rankings, top5_por_ano = calcular_rankings(dados_por_ano)
    variaveis, frequencia = calcular_frequencia(top5_por_ano)
    cores = montar_cores(variaveis)

    print(f"\nAnos encontrados: {anos}")
    print("\nTOP 5 POR ANO:")
    print("-" * 60)
    for ano in anos:
        print(f"{ano}: {', '.join(top5_por_ano[ano])}")

    print("\nFREQUÊNCIA NO TOP 5:")
    print("-" * 60)
    for variavel in variaveis:
        print(f"{variavel}: {frequencia[variavel]}x")

    os.makedirs(PASTA_SAIDA, exist_ok=True)

    grafico_matriz_presenca(
        anos, variaveis, top5_por_ano,
        os.path.join(PASTA_SAIDA, "01_matriz_presenca.png"),
    )
    grafico_frequencia(
        variaveis, frequencia, cores,
        os.path.join(PASTA_SAIDA, "02_frequencia_top5.png"),
    )
    grafico_evolucao_importancia(
        anos, dados_por_ano, variaveis, cores,
        os.path.join(PASTA_SAIDA, "03_evolucao_importancia.png"),
    )
    grafico_dumbbell(
        anos, variaveis, rankings, cores,
        os.path.join(PASTA_SAIDA, "04_dumbbell_ranking.png"),
    )
    grafico_bump_chart(
        anos, variaveis, rankings, cores,
        os.path.join(PASTA_SAIDA, "05_bump_chart.png"),
    )
    grafico_matriz_bolinhas(
        anos, variaveis, rankings, cores,
        os.path.join(PASTA_SAIDA, "06_matriz_bolinhas.png"),
    )
    grafico_heatmap_importancia(
        anos, variaveis, dados_por_ano, top5_por_ano, frequencia,
        os.path.join(PASTA_SAIDA, "07_heatmap_importancia.png"),
    )

    print("\nTodos os gráficos foram gerados com sucesso!")