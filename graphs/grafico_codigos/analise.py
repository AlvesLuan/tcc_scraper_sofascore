"""Cálculos reaproveitados pelos gráficos: rankings, Top 5, frequência, cores."""

import matplotlib as mpl


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


def frequencia_de(variavel, rankings, anos):
    """Quantos anos a variável ficou entre as 5 mais importantes."""
    return sum(
        1 for ano in anos
        if rankings[ano].get(variavel) is not None and rankings[ano][variavel] <= 5
    )


def montar_cores(variaveis):
    """
    Define UMA cor fixa por variável, reaproveitada em todos os gráficos.

    (Nos scripts originais cada scatter()/plot() pegava a próxima cor do
    ciclo padrão, então a mesma variável mudava de cor entre anos/gráficos.)
    """
    n = len(variaveis)
    mapa = mpl.colormaps["tab10" if n <= 10 else "tab20"].resampled(n)
    return {variavel: mapa(i) for i, variavel in enumerate(variaveis)}


def segmentos_consecutivos(anos_validos):
    """
    Recebe uma lista ordenada de anos em que uma variável esteve no Top 5 e
    devolve sublistas de anos consecutivos, para a linha do gráfico se
    interromper nos anos de ausência em vez de ligar por cima da lacuna.
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


def anos_no_top5(variavel, anos, rankings):
    """Lista dos anos (ordenados) em que a variável esteve no Top 5."""
    return [
        ano for ano in anos
        if rankings[ano].get(variavel) is not None and rankings[ano][variavel] <= 5
    ]


def grupo_da_variavel(nome):
    """
    Agrupa variáveis relacionadas (inclusive as dummies de dia da semana),
    para comparar famílias de variáveis em vez de colunas individuais.
    """
    if nome == "idade_media_titular_time":
        return "Idade (time)"
    if nome == "idade_media_titular_adv":
        return "Idade (adversário)"
    if nome == "altura_media_titular_time":
        return "Altura (time)"
    if nome == "altura_media_titular_adv":
        return "Altura (adversário)"
    if nome == "publico":
        return "Público"
    if nome.startswith("condicao_"):
        return "Condição (mandante/visitante)"
    if nome in ("rodada", "mes") or nome.startswith("dia_semana_"):
        return "Calendário (rodada, mês, dia)"
    return "Outras"
