"""
Modelo de Previsão de Duração de Partidas.

Classifica partidas como: jogo curto, jogo médio, jogo longo.
"""
import os
import joblib
import numpy as np
from typing import Optional
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Limites de classificação (em segundos)
SHORT_GAME_MAX = 27 * 60      # até 27 minutos
MEDIUM_GAME_MAX = 34 * 60     # até 34 minutos
# Acima de 34 minutos = jogo longo


class DurationPredictor:
    """Prevê a duração esperada de uma partida."""

    def __init__(self):
        self.model: Optional[Pipeline] = None
        self.is_trained = False
        self.model_path = os.path.join(settings.ml_models_path, "duration_predictor.pkl")

    def train(self, X: np.ndarray, y_duration: np.ndarray) -> dict:
        """
        Treinar modelo de previsão de duração.

        Args:
            X: Features de treino
            y_duration: Duração das partidas em segundos
        """
        valid_mask = y_duration > 0
        X_valid = X[valid_mask]
        y_valid = y_duration[valid_mask]

        if len(X_valid) < 10:
            raise ValueError(f"Dados insuficientes: {len(X_valid)} amostras")

        self.model = Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", GradientBoostingRegressor(
                n_estimators=100,
                max_depth=3,
                learning_rate=0.1,
                random_state=42,
            )),
        ])
        self.model.fit(X_valid, y_valid)
        self.is_trained = True

        pred = self.model.predict(X_valid)
        mae = float(np.mean(np.abs(pred - y_valid)))
        logger.info(f"DurationPredictor treinado: MAE = {mae/60:.1f} minutos")
        return {"mae_train_seconds": mae, "mae_train_minutes": mae / 60}

    def predict_duration(self, X: np.ndarray) -> Optional[float]:
        """Prever duração da partida em segundos."""
        if not self.is_trained or self.model is None:
            return None
        try:
            pred = self.model.predict(X.reshape(1, -1))[0]
            return max(0.0, float(pred))
        except Exception as e:
            logger.warning(f"Erro na predição de duração: {e}")
            return None

    def classify_game_length(self, duration_seconds: float) -> str:
        """
        Classificar a duração prevista do jogo.

        Returns:
            "jogo_curto", "jogo_medio", ou "jogo_longo"
        """
        if duration_seconds <= SHORT_GAME_MAX:
            return "jogo_curto"
        elif duration_seconds <= MEDIUM_GAME_MAX:
            return "jogo_medio"
        else:
            return "jogo_longo"

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def load(self) -> bool:
        if not os.path.exists(self.model_path):
            return False
        try:
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            return True
        except Exception as e:
            logger.warning(f"Erro ao carregar DurationPredictor: {e}")
            return False
