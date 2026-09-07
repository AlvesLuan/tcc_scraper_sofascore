import os
import re
import glob
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------
# CONFIGURAÇÃO
# ----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_PATH = os.path.join(BASE_DIR, "..", "graphs", "arvore-5-depth-5-splits")

# Padrão esperado do nome do arquivo: "AAAA-importancia_variaveis_....txt"
FILENAME_PATTERN = re.compile(r"^(\d{4})-importancia_variaveis_.*\.txt$")

# Padrão de cada linha de dado dentro do arquivo: "nome_da_variavel: 0.1234"
LINE_PATTERN = re.compile(r"^([A-Za-zÀ-ÿ0-9_]+)\s*:\s*([-+]?\d*\.?\d+)$")


def carregar_dados(txt_path):
    """
    Lê todos os arquivos "AAAA-importancia_variaveis_*.txt" dentro de txt_path
    e retorna um dicionário: { ano(int): {variavel: importancia(float), ...}, ... }
    """
    dados_por_ano = {}

    arquivos = glob.glob(os.path.join(txt_path, "*.txt"))
    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo .txt encontrado em: {os.path.abspath(txt_path)}"
        )

    for caminho_arquivo in arquivos:
        nome_arquivo = os.path.basename(caminho_arquivo)
        match = FILENAME_PATTERN.match(nome_arquivo)

        if not match:
            print(f"[aviso] Arquivo ignorado (nome fora do padrão): {nome_arquivo}")
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
            print(f"[aviso] Nenhuma variável encontrada em: {nome_arquivo}")
            continue

        dados_por_ano[ano] = variaveis

    return dados_por_ano


def montar_series(dados_por_ano):
    """
    Reorganiza os dados por ano em séries por variável, já ordenadas
    cronologicamente (2015, 2016, 2017, ...).

    Retorna:
        anos_ordenados: lista de anos em ordem crescente
        series: dict {variavel: [valor_ano1, valor_ano2, ...]} (None quando o
                ano não tiver aquela variável)
    """
    anos_ordenados = sorted(dados_por_ano.keys())

    # Descobre todas as variáveis que aparecem em pelo menos um ano
    todas_variaveis = set()
    for variaveis in dados_por_ano.values():
        todas_variaveis.update(variaveis.keys())

    series = {}
    for variavel in sorted(todas_variaveis):
        series[variavel] = [
            dados_por_ano[ano].get(variavel) for ano in anos_ordenados
        ]

    return anos_ordenados, series


def plotar_grafico(anos_ordenados, series, caminho_saida=None):
    plt.figure(figsize=(11, 6))

    for variavel, valores in series.items():
        plt.plot(anos_ordenados, valores, marker="o", label=variavel)

    plt.title("Evolução da Importância das Variáveis por Ano")
    plt.xlabel("Ano")
    plt.ylabel("Importância (feature_importances_)")
    plt.xticks(anos_ordenados)
    plt.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    if caminho_saida:
        plt.savefig(caminho_saida, dpi=150)
        print(f"Gráfico salvo em: {caminho_saida}")

    plt.show()


if __name__ == "__main__":
    dados_por_ano = carregar_dados(TXT_PATH)
    anos_ordenados, series = montar_series(dados_por_ano)

    print(f"Anos encontrados: {anos_ordenados}")
    print(f"Variáveis encontradas: {list(series.keys())}")

    caminho_saida = os.path.join(BASE_DIR, "evolucao_importancia_variaveis.png")
    plotar_grafico(anos_ordenados, series, caminho_saida)