"""
Constantes do sistema de análise de apostas LoL.
"""

# Ligas suportadas
SUPPORTED_LEAGUES = {
    "LCK",    # League of Legends Champions Korea
    "LEC",    # League of Legends EMEA Championship
    "LCS",    # League Championship Series (América do Norte)
    "CBLOL",  # Campeonato Brasileiro de League of Legends
    "LPL",    # League of Legends Pro League (China)
    "MSI",    # Mid-Season Invitational
    "WORLDS", # World Championship
}

# Mercados de apostas suportados
BET_MARKETS = {
    "match_winner": "Vencedor da partida",
    "first_blood": "Primeiro abate",
    "first_dragon": "Primeiro dragão",
    "first_baron": "Primeiro barão",
    "over_kills": "Mais de X kills",
    "under_kills": "Menos de X kills",
    "total_dragons": "Total de dragões",
    "total_barons": "Total de barões",
    "total_towers": "Total de torres",
    "kills_handicap": "Handicap de kills",
    "map_winner": "Vencedor do mapa",
}

# Casas de apostas monitoradas
BOOKMAKERS = [
    "Pinnacle",
    "1xbet",
    "Bet365",
    "GGbet",
    "Betway",
    "Stake",
    "Parimatch",
]

# Funções de jogadores (posições)
PLAYER_ROLES = ["top", "jungle", "mid", "bot", "support"]

# Estilos de jogo dos times
PLAYSTYLES = ["early_game", "mid_game", "late_game"]

# Ritmos de jogo
GAME_PACES = ["muito_agressivo", "agressivo", "equilibrado", "lento"]

# Classificações de apostas
BET_CLASSIFICATIONS = {
    "muito_segura": (0.85, 1.0),
    "boa": (0.75, 0.85),
    "moderada": (0.65, 0.75),
    "arriscada": (0.0, 0.65),
}

# Limiares de over/under kills comuns em LoL profissional
KILL_THRESHOLDS = [15.5, 20.5, 22.5, 25.5, 27.5, 30.5, 35.5]

# Número mínimo de jogos para usar previsões
MIN_GAMES_FOR_STATS = 5
MIN_GAMES_FOR_ML = 15

# Patches com dados históricos importantes
IMPORTANT_PATCHES = [
    "14.1", "14.2", "14.3", "14.4", "14.5",
    "14.6", "14.7", "14.8", "14.9", "14.10",
]

# Chave da API pública da LoL Esports (chave global conhecida)
LOL_ESPORTS_PUBLIC_API_KEY = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"

# URLs das APIs
PANDASCORE_BASE_URL = "https://api.pandascore.co"
LOL_ESPORTS_API_URL = "https://esports-api.lolesports.com/persisted/gw"
LOL_ESPORTS_FEED_URL = "https://feed.lolesports.com/livestats/v1"
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"

# IDs de ligas na PandaScore API
PANDASCORE_LEAGUE_IDS = {
    "LCK": 293,
    "LEC": 4197,
    "LCS": 4198,
    "CBLOL": 241,
    "LPL": 299,
}

# IDs de ligas na LoL Esports API
LOL_ESPORTS_LEAGUE_IDS = {
    "LCK": "98767991310872058",
    "LEC": "98767991302996019",
    "LCS": "98767991299243165",
    "CBLOL": "98767991332355509",
    "LPL": "98767991314006698",
    "MSI": "98767991355908944",
    "WORLDS": "98767975604431411",
}
