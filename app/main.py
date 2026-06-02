import csv
import os
from scraper import (
    get_classificacao,
    get_jogos_time,
    close
)

from analysis import (
    get_z4,
    get_times_na_serie_a,
    filtrar_jogos_brasileirao,
    contabilizar_jogos,
    calcular_aproveitamento,
    calcular_media,
    calcular_desvio_padrao,
)

from config import (
    TIMES_ALVO,
    SEASONS,
    OUTPUT_CSV
)


def buscar_todos_eventos_brasileirao(team_id: int, season_id: int) -> list[dict]:
    
    '''Percorre as páginas de eventos do time e retorna apenas os jogos do Brasileirão da season especificada.'''
    
    todos = []
    page = 0
    while True:
        data = get_jogos_time(team_id, page)
        events = data.get("events", [])

        # Filtra só Brasileirão da season correta
        jogos_serie_a = filtrar_jogos_brasileirao(events, season_id)
        todos.extend(jogos_serie_a)

        # Para quando não há mais páginas ou saímos do período
        if not data.get("hasNextPage", False):
            break

        page += 1

    return todos


def salvar_csv(time_nome: str, resultado: dict):
    campos = [
        "time", 
        "vitorias_vs_z4", 
        "empates_vs_z4",
        "derrotas_vs_z4", 
        "total_partidas_vs_z4",
        "total_pontos_perdidos_vs_z4",
        "aproveitamento_vs_z4",
        "media_pontos_perdidos_por_jogo",
        "desvio_padrao_pontos_perdidos_por_temporada",
    ]
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    # Lê linhas existentes e remove o time atual se já existir
    linhas = []
    if os.path.isfile(OUTPUT_CSV):
        with open(OUTPUT_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            linhas = [row for row in reader if row["time"] != time_nome]

    # Reescreve o arquivo com todas as linhas + a nova
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)
        writer.writerow({
            "time":                            time_nome,
            "vitorias_vs_z4":                  resultado["vitorias"],
            "empates_vs_z4":                   resultado["empates"],
            "derrotas_vs_z4":                  resultado["derrotas"],
            "total_partidas_vs_z4":            resultado["total"],
            "total_pontos_perdidos_vs_z4":     resultado["pontos_perdidos"],
            "aproveitamento_vs_z4":            resultado["aproveitamento"],
            "media_pontos_perdidos_por_jogo":  resultado["media"],
            "desvio_padrao_pontos_perdidos_por_temporada":   resultado["desvio_padrao"],
        })
    print(f"\n  Resultado salvo em: {OUTPUT_CSV}")


def rodar_time(time_nome: str, time_id: int) -> dict:
    acumulado = {
            "vitorias": 0, 
            "empates": 0, 
            "derrotas": 0, 
            "total": 0,
            "pontos_perdidos": 0,
    }
    pontos_perdidos_temporada = []
    pontos_perdidos_por_jogo = []

    for ano, season_id in SEASONS.items():
        print(f"\n[{time_nome}] Processando {ano} (season_id={season_id})...")

        # 1. Classificação: Z4 e times presentes
        try:
            classificacao = get_classificacao(season_id)
        except Exception as e:
            print(f"  Erro ao buscar classificação: {e}")
            continue

        z4_ids    = get_z4(classificacao)
        presentes = get_times_na_serie_a(classificacao)
        print(f"    Z4: {z4_ids}")

        # 2. Verifica se o time estava na Serie A
        if time_id not in presentes:
            print(f"    {time_nome} não estava na Serie A em {ano}, pulando.")
            continue

        # 3. Busca jogos do time filtrando só Brasileirão
        jogos = buscar_todos_eventos_brasileirao(time_id, season_id)
        print(f"    Jogos do Brasileirão {ano} encontrados: {len(jogos)}")

        # 4. Contabiliza confrontos vs Z4
        resultado_ano = contabilizar_jogos(jogos, time_id, z4_ids)
        pontos_perdidos_temporada.append(resultado_ano["pontos_perdidos"])

        if resultado_ano["total"] > 0:
            pontos_perdidos_por_jogo.append(
                resultado_ano["pontos_perdidos"] / resultado_ano["total"]
            )

        print(f"    vs Z4: {resultado_ano}")

        for chave in acumulado:
            acumulado[chave] += resultado_ano[chave]

    acumulado["media"] = round(calcular_media(pontos_perdidos_por_jogo), 2)
    acumulado["desvio_padrao"] = round(calcular_desvio_padrao(pontos_perdidos_temporada), 2)

    return acumulado


if __name__ == "__main__":
    from scraper import close

    for time_nome, time_id in TIMES_ALVO:
        print(f"\n{'='*50}")
        print(f"Rodando para: {time_nome} (id={time_id})")
        print(f"{'='*50}")

        resultado = rodar_time(time_nome, time_id)

        resultado["aproveitamento"] = calcular_aproveitamento(resultado)

        print(f"\n{'='*50}")
        print(f"Resultado final — {time_nome} (2015–2025):")
        print(f"  Vitórias vs Z4:  {resultado['vitorias']}")
        print(f"  Empates vs Z4:   {resultado['empates']}")
        print(f"  Derrotas vs Z4:  {resultado['derrotas']}")
        print(f"  Total partidas:  {resultado['total']}")
        print(f"  Pontos perdidos: {resultado['pontos_perdidos']}")
        print(f"  Aproveitamento:  {resultado['aproveitamento']}%")
        print(f"  Média de pontos perdidos por jogo:  {resultado['media']}")
        print(f"  Desvio padrão: {resultado['desvio_padrao']}")
        print(f"{'='*50}")

        salvar_csv(time_nome, resultado)
        
    close()
