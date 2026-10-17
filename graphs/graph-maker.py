"""
Gráficos de evolução e ranking da importância das variáveis por ano.

Lê todos os arquivos "AAAA-importancia_variaveis_*.txt" de uma pasta e gera
os PNGs abaixo. Cada gráfico agora vive no seu próprio módulo, dentro da
pasta `graficos/`; este arquivo só configura os caminhos e chama cada um:

    01_matriz_presenca.png        graficos/matriz_presenca.py
    02_frequencia_top5.png        graficos/frequencia_top5.py
    03_evolucao_importancia.png   graficos/evolucao_importancia.py
    04_dumbbell_ranking.png       graficos/dumbbell_ranking.py
    05_bump_chart.png             graficos/bump_chart.py
    06_matriz_bolinhas.png        graficos/matriz_bolinhas.py
    07_heatmap_importancia.png    graficos/heatmap_importancia.py
    08_boxplot_variaveis.png      graficos/boxplot_importancia.py
    09_boxplot_grupos.png         graficos/boxplot_importancia.py

Uso:
    python graph-maker.py                      # usa as pastas padrão abaixo
    python graph-maker.py PASTA_TXT PASTA_OUT  # pastas informadas na linha de comando
"""

import os
import sys

from grafico_codigos import (
    boxplot_grupos,
    boxplot_importancia,
    bump_chart,
    calcular_frequencia,
    calcular_rankings,
    carregar_dados,
    dumbbell_ranking,
    evolucao_importancia,
    frequencia_top5,
    heatmap_importancia,
    matriz_bolinhas,
    matriz_presenca,
    montar_cores,
)

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_PATH = os.path.join(BASE_DIR, "..", "graphs", "01-arvore-5-depth-5-splits")
PASTA_SAIDA = os.path.join(BASE_DIR, "resultados/01-graficos_top5")

if len(sys.argv) >= 2:
    TXT_PATH = sys.argv[1]
if len(sys.argv) >= 3:
    PASTA_SAIDA = sys.argv[2]


def saida(nome_arquivo):
    return os.path.join(PASTA_SAIDA, nome_arquivo)


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

    # --- Chamadas: comente/descomente a linha do gráfico que quiser ---------
    #matriz_presenca(anos, variaveis, top5_por_ano, saida("01_matriz_presenca.png"))
    #frequencia_top5(variaveis, frequencia, cores, saida("02_frequencia_top5.png"))
    #evolucao_importancia(anos, dados_por_ano, variaveis, cores, saida("03_evolucao_importancia.png"))
    #dumbbell_ranking(anos, variaveis, rankings, cores, saida("04_dumbbell_ranking.png"))
    #bump_chart(anos, variaveis, rankings, cores, saida("05_bump_chart.png"))
    #matriz_bolinhas(anos, variaveis, rankings, cores, saida("06_matriz_bolinhas.png"))
    #heatmap_importancia(anos, variaveis, dados_por_ano, top5_por_ano, frequencia, saida("07_heatmap_importancia.png"))
    boxplot_importancia(anos, dados_por_ano, cores, saida("08_boxplot_variaveis.png"))
    boxplot_grupos(anos, dados_por_ano, saida("09_boxplot_grupos.png"))

    print("\nTodos os gráficos foram gerados com sucesso!")
