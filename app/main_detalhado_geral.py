import csv
import os
from datetime import datetime, timezone
from scraper import get_classificacao, get_jogos_time, buscar, close
from analysis import get_z4, get_times_na_serie_a, filtrar_jogos_brasileirao
from config import TIME_ALVO, SEASONS

OUTPUT_CSV_DETALHADO = "data/exports/detalhado_c13_geral.csv"

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

DIAS_SEMANA = {
    0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta",
    4: "Sexta", 5: "Sábado", 6: "Domingo"
}


def get_detalhes_jogo(event_id: int) -> dict:
    url = f"https://www.sofascore.com/api/v1/event/{event_id}"
    return buscar(url)


def extrair_detalhes(event: dict, time_nome: str, ano: int) -> dict:
    details = get_detalhes_jogo(event["id"])
    e = details["event"]

    home = e["homeTeam"]["name"]
    away = e["awayTeam"]["name"]
    home_score = e["homeScore"]["current"]
    away_score = e["awayScore"]["current"]
    winner = event.get("winnerCode")

    # Condição
    time_id_alvo = (
        event["homeTeam"]["id"]
        if event["homeTeam"]["name"] == time_nome
        else event["awayTeam"]["id"]
    )
    condicao = "Mandante" if e["homeTeam"]["id"] == time_id_alvo else "Visitante"

    # Adversário
    adversario = away if e["homeTeam"]["name"] == time_nome else home

    # Gols
    if condicao == "Mandante":
        gols_favor   = home_score
        gols_sofridos = away_score
    else:
        gols_favor   = away_score
        gols_sofridos = home_score

    # Resultado
    if winner == 3:
        resultado = "Empate"
    elif (condicao == "Mandante" and winner == 1) or \
         (condicao == "Visitante" and winner == 2):
        resultado = "Vitória"
    else:
        resultado = "Derrota"

    # Data
    ts = e.get("startTimestamp", 0)
    if ts:
        dt = datetime.fromtimestamp(ts, timezone.utc)
        data       = dt.strftime("%d/%m/%Y")
        dia_semana = DIAS_SEMANA[dt.weekday()]
        mes        = MESES[dt.month]
    else:
        data = dia_semana = mes = ""

    # Árbitro
    arbitro = e.get("referee", {}).get("name", "")

    # Estádio
    estadio = e.get("venue", {}).get("name", "")

    # Rodada
    rodada = e.get("roundInfo", {}).get("round", "")

    return {
        "time":         time_nome,
        "temporada":    ano,
        "rodada":       rodada,
        "data":         data,
        "dia_semana":   dia_semana,
        "mes":          mes,
        "adversario":   adversario,
        "resultado":    resultado,
        "gols_favor":   gols_favor,
        "gols_sofridos":gols_sofridos,
        "condicao":     condicao,
        "arbitro":      arbitro,
        "estadio":      estadio,
    }


def salvar_linha_csv(linha: dict):
    campos = [
        "time", "temporada", "rodada", "data", "dia_semana", "mes",
        "adversario", "resultado", "gols_favor", "gols_sofridos",
        "condicao", "arbitro", "estadio"
    ]
    os.makedirs(os.path.dirname(OUTPUT_CSV_DETALHADO), exist_ok=True)
    arquivo_existe = os.path.isfile(OUTPUT_CSV_DETALHADO)

    with open(OUTPUT_CSV_DETALHADO, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        if not arquivo_existe:
            writer.writeheader()
        writer.writerow(linha)


def rodar_detalhado(time_nome: str, time_id: int):
    for ano, season_id in SEASONS.items():
        print(f"\n[{time_nome}] Processando {ano}...")

        try:
            standings = get_classificacao(season_id)
        except Exception as e:
            print(f"  Erro ao buscar classificação: {e}")
            continue

        z4_ids    = get_z4(standings)
        presentes = get_times_na_serie_a(standings)

        if time_id not in presentes:
            print(f"  {time_nome} não estava na Serie A em {ano}, pulando.")
            continue

        # Busca jogos do time no Brasileirão
        todos = []
        pagina = 0
        while True:
            data = get_jogos_time(time_id, pagina)
            events = data.get("events", [])
            todos.extend(filtrar_jogos_brasileirao(events, season_id))
            if not data.get("hasNextPage", False):
                break
            pagina += 1

        print(f"  Total de jogos: {len(todos)}")

        for event in todos:
            try:
                linha = extrair_detalhes(event, time_nome, ano)
                salvar_linha_csv(linha)
                print(
                    f"{linha['data']} | "
                    f"{linha['adversario']} | "
                    f"{linha['resultado']} | "
                    f"{linha['gols_favor']}x{linha['gols_sofridos']} | "
                    f"{linha['estadio']}"
                )
            except Exception as e:
                print(f"  Erro no evento {event['id']}: {e}")


if __name__ == "__main__":
    time_nome, time_id = TIME_ALVO

    print(f"\n{'='*50}")
    print(f"Detalhado para: {time_nome}")
    print(f"{'='*50}")

    rodar_detalhado(time_nome, time_id)
    close()
    print(f"\nSalvo em: {OUTPUT_CSV_DETALHADO}")