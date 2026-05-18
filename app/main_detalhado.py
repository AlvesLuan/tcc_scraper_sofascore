import csv
import os
from datetime import datetime, timezone
from scraper import get_classificacao, get_jogos_time, buscar, close
from analysis import get_z4, get_times_na_serie_a, filtrar_jogos_brasileirao
from config import TIME_ALVO, SEASONS

OUTPUT_CSV_DETALHADO = "data/exports/detalhado_c13.csv"


def get_detalhes_jogo(event_id: int) -> dict:
    url = f"https://www.sofascore.com/api/v1/event/{event_id}"
    return buscar(url)


def extrair_detalhes(event: dict, time_nome: str, ano: int) -> dict:
    #Extrai os campos detalhados de um evento.
    details = get_detalhes_jogo(event["id"])
    e = details["event"]

    home = e["homeTeam"]["name"]
    away = e["awayTeam"]["name"]
    home_score = e["homeScore"]["current"]
    away_score = e["awayScore"]["current"]
    placar = f"{home_score}x{away_score}"

    # Mandante
    time_id_alvo = (
        event["homeTeam"]["id"] 
        if event["homeTeam"]["name"] == time_nome 
        else event["awayTeam"]["id"]
        )
    
    mandante = "Sim" if e["homeTeam"]["id"] == time_id_alvo else "Não"

    adversario = away if e["homeTeam"]["name"] == time_nome else home

    # Data
    ts = e.get("startTimestamp", 0)
    data = datetime.fromtimestamp(ts, timezone.utc).strftime("%d/%m/%Y") if ts else ""

    # Estádio
    venue = e.get("venue", {})
    estadio = venue.get("name", "")

    # Rodada
    rodada = e.get("roundInfo", {}).get("round", "")

    return {
        "time":       time_nome,
        "adversario": adversario,
        "temporada":  ano,
        "rodada":     rodada,
        "data":       data,
        "mandante":   mandante,
        "placar":     placar,
        "estadio":    estadio,
    }


def salvar_linha_csv(linha: dict):
    campos = ["time", "adversario", "temporada", "rodada", "data", "mandante", "placar", "estadio"]
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
        page = 0
        while True:
            data = get_jogos_time(time_id, page)
            events = data.get("events", [])
            todos.extend(filtrar_jogos_brasileirao(events, season_id))
            if not data.get("hasNextPage", False):
                break
            page += 1

        # Filtra só jogos contra o Z4
        jogos_vs_z4 = [
            e for e in todos
            if (e["homeTeam"]["id"] == time_id and e["awayTeam"]["id"] in z4_ids)
            or (e["awayTeam"]["id"] == time_id and e["homeTeam"]["id"] in z4_ids)
        ]

        print(f"  Jogos vs Z4: {len(jogos_vs_z4)}")

        for event in jogos_vs_z4:
            winner = event.get("winnerCode")

            home_id = event["homeTeam"]["id"]
            away_id = event["awayTeam"]["id"]

            venceu = (
                (time_id == home_id and winner == 1)
                or
                (time_id == away_id and winner == 2)
            )
            if venceu:
                continue
            try:
                linha = extrair_detalhes(event, time_nome, ano)

                salvar_linha_csv(linha)

                print(
                    f"{linha['data']} | "
                    f"{linha['adversario']} | "
                    f"{linha['placar']} | "
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