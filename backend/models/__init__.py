"""Pacote de modelos do banco de dados."""
from backend.models.team import Team
from backend.models.player import Player
from backend.models.match import Match
from backend.models.champion import Champion
from backend.models.odds import Odds
from backend.models.prediction import Prediction
from backend.models.bet_recommendation import BetRecommendation

__all__ = [
    "Team",
    "Player",
    "Match",
    "Champion",
    "Odds",
    "Prediction",
    "BetRecommendation",
]
