"""
Serviço de coleta de dados de APIs externas.

Fontes suportadas:
- PandaScore API
- LoL Esports API
- Riot Games API
- Oracle's Elixir
"""
import httpx
from typing import Optional
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

PANDASCORE_BASE_URL = "https://api.pandascore.co"
LOL_ESPORTS_BASE_URL = "https://esports-api.lolesports.com/persisted/gw"
LOL_ESPORTS_FEED_URL = "https://feed.lolesports.com/livestats/v1"

# IDs de torneios por liga (PandaScore)
LEAGUE_IDS = {
    "LCK": 293,
    "LEC": 4197,
    "LCS": 4198,
    "CBLOL": 241,
    "LPL": 299,
}


class DataCollector:
    """Coleta dados reais de partidas profissionais de League of Legends."""

    def __init__(self):
        self.pandascore_headers = {
            "Authorization": f"Bearer {settings.pandascore_api_key}",
        }
        self.lol_esports_headers = {
            "x-api-key": settings.lol_esports_api_key,
        }

    # ------------------------------------------------------------------ #
    # PandaScore
    # ------------------------------------------------------------------ #

    def get_upcoming_matches(self, league: Optional[str] = None) -> list[dict]:
        """Buscar partidas agendadas na PandaScore API."""
        if not settings.pandascore_api_key:
            logger.warning("PANDASCORE_API_KEY não configurada")
            return []

        params: dict = {
            "filter[videogame_title]": "League of Legends",
            "sort": "scheduled_at",
            "per_page": 100,
        }
        if league and league.upper() in LEAGUE_IDS:
            params["filter[league_id]"] = LEAGUE_IDS[league.upper()]

        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{PANDASCORE_BASE_URL}/lol/matches/upcoming",
                    headers=self.pandascore_headers,
                    params=params,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Erro ao buscar partidas da PandaScore: {exc}")
            return []

    def get_match_details(self, match_id: str) -> Optional[dict]:
        """Buscar detalhes de uma partida específica."""
        if not settings.pandascore_api_key:
            return None

        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{PANDASCORE_BASE_URL}/lol/matches/{match_id}",
                    headers=self.pandascore_headers,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Erro ao buscar detalhes da partida {match_id}: {exc}")
            return None

    def get_team_stats(self, team_id: str) -> Optional[dict]:
        """Buscar estatísticas de um time."""
        if not settings.pandascore_api_key:
            return None

        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{PANDASCORE_BASE_URL}/lol/teams/{team_id}",
                    headers=self.pandascore_headers,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Erro ao buscar stats do time {team_id}: {exc}")
            return None

    def get_recent_matches(self, team_id: str, limit: int = 20) -> list[dict]:
        """Buscar últimas partidas de um time."""
        if not settings.pandascore_api_key:
            return []

        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{PANDASCORE_BASE_URL}/lol/matches/past",
                    headers=self.pandascore_headers,
                    params={
                        "filter[team_id]": team_id,
                        "sort": "-scheduled_at",
                        "per_page": limit,
                    },
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Erro ao buscar partidas recentes do time {team_id}: {exc}")
            return []

    # ------------------------------------------------------------------ #
    # LoL Esports API
    # ------------------------------------------------------------------ #

    def get_lol_esports_schedule(self, league_id: Optional[str] = None) -> Optional[dict]:
        """Buscar agenda de partidas da LoL Esports API."""
        try:
            params: dict = {"hl": "pt-BR"}
            if league_id:
                params["leagueId"] = league_id

            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{LOL_ESPORTS_BASE_URL}/getSchedule",
                    headers=self.lol_esports_headers,
                    params=params,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Erro ao buscar agenda LoL Esports: {exc}")
            return None

    def get_live_game_data(self, game_id: str) -> Optional[dict]:
        """Buscar dados ao vivo de uma partida via LoL Esports Feed."""
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    f"{LOL_ESPORTS_FEED_URL}/window/{game_id}",
                    params={"startingTime": "0"},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Erro ao buscar dados live do jogo {game_id}: {exc}")
            return None

    # ------------------------------------------------------------------ #
    # Oracle's Elixir (arquivos CSV públicos)
    # ------------------------------------------------------------------ #

    def get_oracles_elixir_data(self, year: int = 2024) -> Optional[object]:
        """
        Buscar dados do Oracle's Elixir.
        Retorna um DataFrame pandas com as estatísticas de todas as partidas.
        """
        import pandas as pd
        url = f"https://oracleselixir-downloadable-match-data.s3-us-west-2.amazonaws.com/{year}_LoL_esports_match_data_from_OraclesElixir.csv"
        try:
            df = pd.read_csv(url)
            logger.info(f"Oracle's Elixir: {len(df)} registros carregados para {year}")
            return df
        except Exception as exc:
            logger.error(f"Erro ao buscar dados do Oracle's Elixir: {exc}")
            return None
