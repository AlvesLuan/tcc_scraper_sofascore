import csv
import os
from bs4 import BeautifulSoup
from config import PASTAS_FBREF, NOMES_FBREF

# Defino os caminhos do CSV de entrada, do CSV de saída
# e da pasta onde estão os HTMLs baixados do FBref
CSV_ENTRADA = "data/exports/detalhado_c13_geral.csv"
CSV_SAIDA   = "data/exports/detalhado_c13_geral_publico.csv"
HTML_DIR    = "data/fbref-pages-html"


def extrair_publico_html(caminho_html: str) -> dict:
    #Lê um HTML salvo do FBref e retorna {rodada: publico}.
    with open(caminho_html, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    publico_por_rodada = {}
    tabela = soup.find("table", {"id": "matchlogs_for"})
    if not tabela:
        print(f"  Tabela não encontrada em: {caminho_html}")
        return publico_por_rodada

    # Anda nas linhas do corpo da tabela
    for linha in tabela.select("tbody tr"):
        comp = linha.select_one("td[data-stat='comp']")
        if not comp or "Série A" not in comp.text:
            continue

        # Pego a rodada e o público da partida
        rodada_td  = linha.select_one("td[data-stat='round']")
        publico_td = linha.select_one("td[data-stat='attendance']")
        if not rodada_td or not publico_td:
            continue

        #"Matchweek 12" vira "12" e tira a virgula do publicco
        numeroRodada  = rodada_td.text.replace("Matchweek ", "").strip()
        publico = publico_td.text.replace(",", "").strip()

        try:
            publico_por_rodada[int(numeroRodada)] = int(publico) if publico else "N.A"
        except ValueError:
            continue

    return publico_por_rodada


def rodar():
    with open(CSV_ENTRADA, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        linhas = list(reader)
        campos = reader.fieldnames

    # Adiciono uma nova coluna chamada "publico"
    campos_saida = list(campos) + ["publico"]
    cache = {}

    # Percorro todas as linhas do CSV
    for linha in linhas:
        time_nome = linha["time"]
        ano       = int(linha["temporada"])
        rodada    = int(linha["rodada"])

        # Crio uma chave única para o cache
        # Exemplo:
        # ("Atlético Mineiro", 2020)
        chave = (time_nome, ano)
        if chave not in cache:
            pasta        = PASTAS_FBREF.get(time_nome, time_nome)
            nome         = NOMES_FBREF.get(time_nome, time_nome)
            caminho_html = os.path.join(HTML_DIR, pasta, f"{ano} {nome} Stats, Série A _ FBref.com.html")

            if os.path.isfile(caminho_html):
                print(f"  Lendo: {caminho_html}")
                cache[chave] = extrair_publico_html(caminho_html)
            else:
                print(f"  HTML não encontrado: {caminho_html}")
                cache[chave] = {}

        linha["publico"] = cache[chave].get(rodada, "N.A")

    with open(CSV_SAIDA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos_saida)
        writer.writeheader()
        writer.writerows(linhas)

    print(f"\nSalvo em: {CSV_SAIDA}")


if __name__ == "__main__":
    rodar()