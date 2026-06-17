# ======================================================
# TIME ALVO — descomente apenas os times que quer rodar (tirado de https://www.sofascore.com/api/v1/unique-tournament/325/season/(id da temporada)/standings/total?cacheBust)
# ======================================================
TIMES_ALVO = [
    # ("Flamengo",         5981),
    # ("São Paulo",        1981),
    # ("Palmeiras",        1963),
    # ("Santos",           1968),
    # ("Corinthians",      1957),
    # ("Botafogo",         1958),
    # ("Vasco da Gama",    1974),
    # ("Fluminense",       1961),
    ("Atlético Mineiro", 1977),
    # ("Cruzeiro",         1954),
    # ("Grêmio",           5926),
    # ("Internacional",    1966),
]


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

# ======================================================
# SCRAPING
# ======================================================

REQUEST_DELAY = 3  # segundos entre requisições

# ======================================================
# OUTPUT
# ======================================================

OUTPUT_CSV = "data/exports/resultados_vs_z4_geral.csv"
OUTPUT_CSV_DETALHADO = "data/exports/base_detalhada_geral.csv"




# ======================================================
# FBREF — pastas e nomes dos arquivos HTML salvos
# ======================================================
PASTAS_FBREF = {
    "Atlético Mineiro": "Atletico-Mineiro",
    "Internacional":    "Internacional",
    "Palmeiras":        "Palmeiras",
    "Fluminense":       "Fluminense",
    "Vasco da Gama":    "Vasco-da-Gama",
    "Cruzeiro":         "Cruzeiro",
    "Santos":           "Santos",
    "Flamengo":         "Flamengo",
    "São Paulo":        "Sao-Paulo",
    "Bahia":            "Bahia",
    "Grêmio":           "Gremio",
    "Botafogo":         "Botafogo",
    "Corinthians":      "Corinthians",
}

NOMES_FBREF = {
    "Atlético Mineiro": "Atlético Mineiro",
    "Internacional":    "Internacional",
    "Palmeiras":        "Palmeiras",
    "Fluminense":       "Fluminense",
    "Vasco da Gama":    "Vasco da Gama",
    "Cruzeiro":         "Cruzeiro",
    "Santos":           "Santos",
    "Flamengo":         "Flamengo",
    "São Paulo":        "São Paulo",
    "Bahia":            "Bahia",
    "Grêmio":           "Grêmio",
    "Botafogo":         "Botafogo",
    "Corinthians":      "Corinthians",
}