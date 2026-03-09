"""
Preditor principal — interface unificada para todos os modelos de ML.

Carrega todos os modelos treinados e fornece uma interface
única para realizar previsões.
"""
from typing import Optional
import numpy as np
from sqlalchemy.orm import Session

from backend.ml.feature_engineering import FeatureEngineer
from backend.ml.models.win_predictor import WinPredictor
from backend.ml.models.kills_predictor import KillsPredictor
from backend.ml.models.duration_predictor import DurationPredictor
from backend.models.match import Match
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MLPredictor:
    """Interface unificada para todos os modelos de Machine Learning."""

    def __init__(self, db: Session):
        self.db = db
        self.feature_engineer = FeatureEngineer(db)
        self.win_predictor = WinPredictor()
        self.kills_predictor = KillsPredictor()
        self.duration_predictor = DurationPredictor()
        self._models_loaded = False

    def load_models(self) -> bool:
        """Carregar todos os modelos treinados do disco."""
        win_ok = self.win_predictor.load()
        kills_ok = self.kills_predictor.load()
        duration_ok = self.duration_predictor.load()

        self._models_loaded = win_ok or kills_ok or duration_ok
        if self._models_loaded:
            logger.info(
                f"Modelos carregados: win={win_ok}, kills={kills_ok}, duration={duration_ok}"
            )
        else:
            logger.warning("Nenhum modelo ML encontrado — usando apenas estatísticas")
        return self._models_loaded

    def predict(self, match: Match) -> dict:
        """
        Realizar todas as previsões para uma partida.

        Returns:
            Dicionário com todas as previsões disponíveis
        """
        features = self.feature_engineer.extract_match_features(match)

        result: dict = {
            "features_available": features is not None,
            "models_loaded": self._models_loaded,
        }

        if features is None:
            logger.warning(f"Sem features para partida {match.id}")
            return result

        # Previsão de vitória
        if self.win_predictor.is_trained:
            win_prob = self.win_predictor.predict_proba(features)
            if win_prob is not None:
                result["blue_win_probability_ml"] = round(win_prob, 4)
                result["red_win_probability_ml"] = round(1 - win_prob, 4)

        # Previsão de kills
        if self.kills_predictor.is_trained:
            kills_pred = self.kills_predictor.predict_kills(features)
            if kills_pred is not None:
                result["predicted_total_kills_ml"] = round(kills_pred, 1)
                # Over/under para limiares comuns
                for threshold in [20.5, 22.5, 25.5, 27.5, 30.5]:
                    prob = self.kills_predictor.predict_over_under(features, threshold)
                    if prob is not None:
                        result[f"over_{threshold}_ml"] = round(prob, 4)

        # Previsão de duração
        if self.duration_predictor.is_trained:
            duration_pred = self.duration_predictor.predict_duration(features)
            if duration_pred is not None:
                result["predicted_duration_seconds_ml"] = round(duration_pred, 0)
                result["predicted_duration_minutes_ml"] = round(duration_pred / 60, 1)
                result["game_length_class_ml"] = self.duration_predictor.classify_game_length(
                    duration_pred
                )

        return result
