# ======================================================
# TIME ALVO — descomente apenas o time que quer rodar (tirado de https://www.sofascore.com/api/v1/unique-tournament/325/season/(id da temporada)/standings/total?cacheBust)
# ======================================================
#TIME_ALVO = ("Flamengo",        5981)
#TIME_ALVO = ("São Paulo",       1981)
#TIME_ALVO = ("Palmeiras",       1963)
#TIME_ALVO = ("Santos",          1968)
#TIME_ALVO = ("Corinthians",     1957)
#TIME_ALVO = ("Botafogo",        1958)
#TIME_ALVO = ("Vasco da Gama",   1974)
TIME_ALVO = ("Fluminense",      1961)
#TIME_ALVO = ("Atlético Mineiro",  1977)
#TIME_ALVO = ("Cruzeiro",        1954)
#TIME_ALVO = ("Grêmio",           5926)
#TIME_ALVO = ("Internacional",    1966)
#TIME_ALVO = ("Bahia",            1955)


# ======================================================
# Codigo da Temporada (https://www.sofascore.com/api/v1/unique-tournament/325/seasons)
# ======================================================
# Mapa ano -> season_id do Sofascore
SEASONS = {
    2015: 10173,
    2016: 11429,
    2017: 13100,
    2018: 16183,
    2019: 22931,
    2020: 27591,  # edição 20/21 (pandemia)
    2021: 36166,
    2022: 40557,
    2023: 48982,
    2024: 58766,
    2025: 72034,
}

# ======================================================
# TOURNAMENTS
# ======================================================

UNIQUE_TOURNAMENT_ID = 325  # Brasileirão Serie A
#TOURNAMENT_ID        = 83   # ID regular (usado nos eventos por rodada)

# ======================================================
# SCRAPING
# ======================================================

REQUEST_DELAY = 3  # segundos entre requisições

# ======================================================
# OUTPUT
# ======================================================

OUTPUT_CSV = "data/exports/resultados_c13.csv"
OUTPUT_CSV_DETALHADO = "data/exports/detalhado_c13.csv"
