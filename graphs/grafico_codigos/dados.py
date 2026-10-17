"""Leitura dos arquivos "AAAA-importancia_variaveis_*.txt"."""

import glob
import os
import re

# Nome esperado: "AAAA-importancia_variaveis_....txt"
FILENAME_PATTERN = re.compile(r"^(\d{4})-importancia_variaveis_.*\.txt$")

# Linha esperada: "nome_da_variavel: 0.1234" (aceita notação científica e ".1234")
LINE_PATTERN = re.compile(
    r"^([A-Za-zÀ-ÿ0-9_]+)\s*:\s*"
    r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)$"
)


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
