from config import UNIQUE_TOURNAMENT_ID

def get_z4(standings_json: dict) -> set[int]:
    """Retorna IDs dos 4 rebaixados (promotion.text == 'Relegation')."""
    z4 = set()
    for row in standings_json["standings"][0]["rows"]:
        if row.get("promotion", {}).get("text") == "Relegation":
            z4.add(row["team"]["id"])
    return z4

def get_times_na_serie_a(standings_json: dict) -> set[int]:
    """Retorna IDs de todos os times da edição."""
    return {row["team"]["id"] for row in standings_json["standings"][0]["rows"]}

def filtrar_jogos_brasileirao(events: list[dict], season_id: int) -> list[dict]:
    """Filtra apenas jogos do Brasileirão da season correta."""
    return [
        e for e in events
        if e.get("tournament", {}).get("uniqueTournament", {}).get("id") == UNIQUE_TOURNAMENT_ID
        and e.get("season", {}).get("id") == season_id
        and e.get("status", {}).get("type") == "finished"
    ]

def parse_jogos(events: list[dict], time_id: int, z4_ids: set[int]) -> dict:
    """Contabiliza vitórias, empates e derrotas contra o Z4."""
    resultado = {
        "vitorias": 0,
        "empates": 0, 
        "derrotas": 0, 
        "total": 0,
        "pontos_perdidos": 0,
    }

    for event in events:
        home_id = event["homeTeam"]["id"]
        away_id = event["awayTeam"]["id"]
        winner  = event.get("winnerCode")

        if time_id == home_id and away_id in z4_ids:
            perspectiva = "home"
        elif time_id == away_id and home_id in z4_ids:
            perspectiva = "away"
        else:
            continue

        resultado["total"] += 1

        if winner == 3:
            resultado["empates"] += 1
            resultado["pontos_perdidos"] += 2
        
        elif (perspectiva == "home" and winner == 1) or \
            (perspectiva == "away" and winner == 2):
            resultado["vitorias"] += 1
        
        else:
            resultado["derrotas"] += 1
            resultado["pontos_perdidos"] += 3
    return resultado


def calcular_aproveitamento(resultado: dict) -> float:
    pontos_ganhos = resultado["vitorias"] * 3 + resultado["empates"]

    total_possivel = resultado["total"] * 3

    if total_possivel == 0:
        return 0

    return round((pontos_ganhos / total_possivel) * 100, 2)

    