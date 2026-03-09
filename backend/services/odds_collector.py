"""
Serviço de coleta automática de odds de casas de apostas.

Utiliza a TheOddsAPI para coletar odds reais de várias casas de apostas.
"""
import httpx
from typing import Optional
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"

# Mercados suportados pela TheOddsAPI para esports
SUPPORTED_MARKETS = ["h2h"]  # head-to-head (vencedor da partida)


class OddsCollector:
    """Coleta odds reais de múltiplas casas de apostas via TheOddsAPI."""

    def __init__(self):
        self.api_key = settings.odds_api_key

    def get_lol_odds(self, region: str = "us") -> list[dict]:
        """
        Buscar odds disponíveis para partidas de LoL.

        Args:
            region: Região da casa de apostas (us, eu, uk, au)
        """
        if not self.api_key:
            logger.warning("ODDS_API_KEY não configurada")
            return []

        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{ODDS_API_BASE_URL}/sports/esports_lol/odds",
                    params={
                        "apiKey": self.api_key,
                        "regions": region,
                        "markets": ",".join(SUPPORTED_MARKETS),
                        "oddsFormat": "decimal",
                    },
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"OddsAPI: {len(data)} eventos encontrados para LoL")
                return data
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                logger.error("ODDS_API_KEY inválida ou expirada")
            elif exc.response.status_code == 422:
                logger.warning("Esporte 'esports_lol' não disponível na TheOddsAPI para esta região")
            else:
                logger.error(f"Erro HTTP ao buscar odds: {exc}")
            return []
        except httpx.HTTPError as exc:
            logger.error(f"Erro de conexão ao buscar odds: {exc}")
            return []

    def parse_odds(self, raw_odds: list[dict]) -> list[dict]:
        """
        Parsear e normalizar dados de odds da TheOddsAPI.

        Retorna lista de dicts com:
        - match_external_id: identificador externo da partida
        - bookmaker: nome da casa de apostas
        - market: mercado (match_winner, etc.)
        - selection: seleção (team_blue, team_red)
        - odd_value: valor decimal da odd
        - implied_probability: probabilidade implícita (1/odd)
        """
        parsed = []
        for event in raw_odds:
            for bookmaker in event.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    for outcome in market.get("outcomes", []):
                        odd_value = outcome.get("price", 0)
                        if odd_value > 0:
                            parsed.append({
                                "match_external_id": event.get("id"),
                                "home_team": event.get("home_team"),
                                "away_team": event.get("away_team"),
                                "commence_time": event.get("commence_time"),
                                "bookmaker": bookmaker.get("key"),
                                "bookmaker_title": bookmaker.get("title"),
                                "market": market.get("key"),
                                "selection": outcome.get("name"),
                                "odd_value": odd_value,
                                "implied_probability": round(1 / odd_value, 4),
                            })
        return parsed

    def get_remaining_requests(self) -> Optional[int]:
        """Verificar quantas requisições restam na cota da API."""
        if not self.api_key:
            return None

        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    f"{ODDS_API_BASE_URL}/sports",
                    params={"apiKey": self.api_key},
                )
                remaining = response.headers.get("x-requests-remaining")
                return int(remaining) if remaining else None
        except Exception:
            return None
