import csv
import math
import os
from datetime import datetime, timezone, timedelta
from scraper import get_classificacao, get_jogos_time, buscar, close
from analysis import get_z4, get_times_na_serie_a, filtrar_jogos_brasileirao
from config import TIMES_ALVO, SEASONS

OUTPUT_CSV_DETALHADO = "data/exports/base_detalhada_geral_vs_z4.csv"

BR = timezone(timedelta(hours=-3))

#MESES = {
#    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
#    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
#    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
#}

DIAS_SEMANA = {
    0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta",
    4: "Sexta", 5: "Sábado", 6: "Domingo"
}


def get_detalhes_jogo(event_id: int) -> dict:
    url = f"https://www.sofascore.com/api/v1/event/{event_id}"
    return buscar(url)


def get_lineup_jogo(event_id: int) -> dict:
    url = f"https://www.sofascore.com/api/v1/event/{event_id}/lineups"
    return buscar(url)


def calcular_stats_titulares(players: list, data_jogo: datetime) -> dict:
    '''Calcula média de idade, média de altura dos 11 titulares e o desvio padrao de cada media.'''
    titulares = [p for p in players if not p.get("substitute", True)]

    idades, alturas = [], []

    for p in titulares:
        jogador = p.get("player", {})

        # Idade
        dob = jogador.get("dateOfBirthTimestamp")
        if dob:
            nascimento = datetime.fromtimestamp(dob, BR)
            idade = (data_jogo - nascimento).days / 365.25
            idades.append(idade)

        # Altura
        altura = jogador.get("height")
        if altura:
            alturas.append(altura)


    def desvio(valores):
        if len(valores) < 2:
            return "N.A"
        media = sum(valores) / len(valores)
        variancia = sum((x - media) ** 2 for x in valores) / len(valores)
        return round(math.sqrt(variancia), 1)

    return {
        "idade_media":      round(sum(idades) / len(idades), 1) if idades else "N.A",
        "desvio_idade":     desvio(idades),
        "altura_media":     round(sum(alturas) / len(alturas), 1) if alturas else "N.A",
        "desvio_altura":    desvio(alturas),
    }


def extrair_detalhes(event: dict, time_nome: str, time_id: int, ano: int) -> dict:
    details = get_detalhes_jogo(event["id"])
    e = details["event"]

    home = e["homeTeam"]["name"]
    away = e["awayTeam"]["name"]
    home_id = e["homeTeam"]["id"]
    home_score = e["homeScore"]["current"]
    away_score = e["awayScore"]["current"]
    winner = event.get("winnerCode")

    # Condição
    condicao = "Mandante" if home_id == time_id else "Visitante"
    adversario = away if home_id == time_id else home

    # Gols
    if condicao == "Mandante":
        gols_favor, gols_sofridos = home_score, away_score
    else:
        gols_favor, gols_sofridos = away_score, home_score

    # Resultado
    if winner == 3:
        resultado = "Empate"
    elif (condicao == "Mandante" and winner == 1) or \
         (condicao == "Visitante" and winner == 2):
        resultado = "Vitória"
    else:
        resultado = "Derrota"

    # Data e hora
    ts = e.get("startTimestamp", 0)
    if ts:
        dt = datetime.fromtimestamp(ts, BR)
        data       = dt.strftime("%d/%m/%Y")
        horario    = dt.strftime("%H:%M")
        dia_semana = DIAS_SEMANA[dt.weekday()]
        mes = (f"{dt.month:02d}")
        #mes        = MESES[dt.month]
    else:
        data = horario = dia_semana = mes = ""
        dt = None

    # Árbitro e estádio
    arbitro = e.get("referee", {}).get("name", "")
    estadio = e.get("venue", {}).get("name", "")
    rodada  = e.get("roundInfo", {}).get("round", "")

    # Lineup
    stats_time = stats_adv = {"idade_media": "N.A", "altura_media": "N.A"}
    if dt:
        try:
            lineup = get_lineup_jogo(event["id"])
            lado_time = "home" if home_id == time_id else "away"
            lado_adv  = "away" if home_id == time_id else "home"
            stats_time = calcular_stats_titulares(lineup[lado_time]["players"], dt)
            stats_adv  = calcular_stats_titulares(lineup[lado_adv]["players"], dt)
        except Exception:
            pass

    return {
        "time":                        time_nome,
        "temporada":                   ano,
        "rodada":                      rodada,
        "data":                        data,
        "horario":                     horario,
        "dia_semana":                  dia_semana,
        "mes":                         mes,
        "adversario":                  adversario,
        "resultado":                   resultado,
        "gols_favor":                  gols_favor,
        "gols_sofridos":               gols_sofridos,
        "condicao":                    condicao,
        "arbitro":                     arbitro,
        "idade_media_titular_time":    stats_time["idade_media"],
        "desvio_idade_media_time":     stats_time["desvio_idade"],
        "altura_media_titular_time":   stats_time["altura_media"],
        "desvio_altura_media_time":    stats_time["desvio_altura"],
        "idade_media_titular_adv":     stats_adv["idade_media"],
        "desvio_idade_media_adv":      stats_adv["desvio_idade"],
        "altura_media_titular_adv":    stats_adv["altura_media"],
        "desvio_altura_media_adv":     stats_adv["desvio_altura"],
        "estadio":                     estadio,
    }


def salvar_linha_csv(linha: dict):
    campos = [
        "time", "temporada", "rodada", "data", "horario", "dia_semana", "mes",
        "adversario", "resultado", "gols_favor", "gols_sofridos", "condicao",
        "arbitro", "idade_media_titular_time", "desvio_idade_media_time", 
        "altura_media_titular_time", "desvio_altura_media_time",
        "idade_media_titular_adv", "desvio_idade_media_adv",
        "altura_media_titular_adv", "desvio_altura_media_adv", "estadio"
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

        todos = []
        pagina = 0
        while True:
            data = get_jogos_time(time_id, pagina)
            events = data.get("events", [])
            todos.extend(filtrar_jogos_brasileirao(events, season_id))
            if not data.get("hasNextPage", False):
                break
            pagina += 1

        # Organizar as rodadas pra ficar em ordem (1 a 38)
        todos.sort(key=lambda e: e.get("startTimestamp", 0))

        jogos_vs_z4 = [
            e for e in todos
            if (e["homeTeam"]["id"] == time_id and e["awayTeam"]["id"] in z4_ids)
            or (e["awayTeam"]["id"] == time_id and e["homeTeam"]["id"] in z4_ids)
        ]

        print(f"  Jogos vs Z4: {len(jogos_vs_z4)}")

        for event in jogos_vs_z4:
            winner  = event.get("winnerCode")
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
                linha = extrair_detalhes(event, time_nome, time_id, ano)
                salvar_linha_csv(linha)
                print(
                    f"{linha['data']} {linha['horario']} | "
                    f"{linha['adversario']} | "
                    f"{linha['resultado']} | "
                    f"{linha['gols_favor']}x{linha['gols_sofridos']} | "
                    f"{linha['estadio']}"
                )
            except Exception as e:
                print(f"  Erro no evento {event['id']}: {e}")


if __name__ == "__main__":
    for time_nome, time_id in TIMES_ALVO:
        print(f"\n{'='*50}")
        print(f"Detalhado para: {time_nome}")
        print(f"{'='*50}")

        rodar_detalhado(time_nome, time_id)
    
    close()
    print(f"\nSalvo em: {OUTPUT_CSV_DETALHADO}")