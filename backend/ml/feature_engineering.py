"""
Feature Engineering — preparação de features para os modelos de ML.

Converte dados brutos de times e partidas em features numéricas
para treinamento e previsão dos modelos.
"""
import numpy as np
import pandas as pd
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.team import Team
from backend.models.match import Match
from backend.utils.logger import get_logger

logger = get_logger(__name__)


FEATURE_COLUMNS = [
    "blue_winrate",
    "red_winrate",
    "blue_kills_per_game",
    "red_kills_per_game",
    "blue_deaths_per_game",
    "red_deaths_per_game",
    "blue_gold_per_minute",
    "red_gold_per_minute",
    "blue_first_blood_rate",
    "red_first_blood_rate",
    "blue_first_dragon_rate",
    "red_first_dragon_rate",
    "blue_first_baron_rate",
    "red_first_baron_rate",
    "blue_towers_per_game",
    "red_towers_per_game",
    "blue_avg_duration",
    "red_avg_duration",
    "winrate_diff",
    "kills_diff",
    "gold_diff",
    "duration_diff",
    "blue_games_played",
    "red_games_played",
]


class FeatureEngineer:
    """Prepara features para os modelos de Machine Learning."""

    def __init__(self, db: Session):
        self.db = db

    def extract_match_features(self, match: Match) -> Optional[np.ndarray]:
        """
        Extrair vetor de features de uma partida para predição.

        Returns:
            Array numpy com as features ou None se dados insuficientes
        """
        blue_team = self.db.query(Team).filter(Team.id == match.team_blue_id).first()
        red_team = self.db.query(Team).filter(Team.id == match.team_red_id).first()

        if not blue_team or not red_team:
            return None

        # Verificar se há jogos suficientes
        min_games = 5
        if (blue_team.games_played or 0) < min_games or (red_team.games_played or 0) < min_games:
            logger.warning(
                f"Dados insuficientes para ML: "
                f"{blue_team.name}={blue_team.games_played}, "
                f"{red_team.name}={red_team.games_played}"
            )
            return None

        features = self._team_features_to_vector(blue_team, red_team)
        return features

    def _team_features_to_vector(
        self, blue_team: Team, red_team: Team
    ) -> np.ndarray:
        """Converter estatísticas dos times em vetor de features."""
        bw = blue_team.winrate or 0.5
        rw = red_team.winrate or 0.5
        bk = blue_team.kills_per_game or 12.0
        rk = red_team.kills_per_game or 12.0
        bd = blue_team.deaths_per_game or 12.0
        rd = red_team.deaths_per_game or 12.0
        bg = blue_team.gold_per_minute or 35000.0
        rg = red_team.gold_per_minute or 35000.0
        bb = blue_team.first_blood_rate or 0.5
        rb = red_team.first_blood_rate or 0.5
        bdr = blue_team.first_dragon_rate or 0.5
        rdr = red_team.first_dragon_rate or 0.5
        bba = blue_team.first_baron_rate or 0.5
        rba = red_team.first_baron_rate or 0.5
        bt = blue_team.towers_per_game or 6.0
        rt = red_team.towers_per_game or 6.0
        bdur = blue_team.avg_game_duration or 1900.0
        rdur = red_team.avg_game_duration or 1900.0
        bgp = float(blue_team.games_played or 0)
        rgp = float(red_team.games_played or 0)

        features = np.array([
            bw, rw,
            bk, rk,
            bd, rd,
            bg, rg,
            bb, rb,
            bdr, rdr,
            bba, rba,
            bt, rt,
            bdur, rdur,
            bw - rw,       # winrate_diff
            bk - rk,       # kills_diff
            bg - rg,       # gold_diff
            bdur - rdur,   # duration_diff
            bgp, rgp,
        ], dtype=np.float32)

        return features

    def build_training_dataset(self, matches: list[Match]) -> tuple:
        """
        Construir dataset completo para treinamento dos modelos.

        Returns:
            Tupla (X, y_win, y_kills, y_duration) onde:
            - X: matriz de features
            - y_win: label binário (1 = blue venceu, 0 = red venceu)
            - y_kills: total de kills da partida
            - y_duration: duração em segundos
        """
        X_list = []
        y_win_list = []
        y_kills_list = []
        y_duration_list = []

        for match in matches:
            if match.status != "finished" or match.winner_id is None:
                continue

            features = self.extract_match_features(match)
            if features is None:
                continue

            X_list.append(features)
            y_win_list.append(1 if match.winner_id == match.team_blue_id else 0)

            total_kills = (match.blue_kills or 0) + (match.red_kills or 0)
            y_kills_list.append(total_kills)
            y_duration_list.append(match.duration_seconds or 0)

        if not X_list:
            return np.array([]), np.array([]), np.array([]), np.array([])

        return (
            np.vstack(X_list),
            np.array(y_win_list),
            np.array(y_kills_list, dtype=float),
            np.array(y_duration_list, dtype=float),
        )

    def get_feature_names(self) -> list[str]:
        """Retornar nomes das features."""
        return FEATURE_COLUMNS
