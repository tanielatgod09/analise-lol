"""
Modelo de Previsão de Objetivos (dragões, barões, torres).
"""
import os
import joblib
import numpy as np
from typing import Optional
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ObjectivesPredictor:
    """Prevê objetivos (dragões, barões, torres) de cada time."""

    def __init__(self):
        self.model: Optional[MultiOutputRegressor] = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = os.path.join(settings.ml_models_path, "objectives_predictor.pkl")

    def train(
        self,
        X: np.ndarray,
        y_blue_dragons: np.ndarray,
        y_red_dragons: np.ndarray,
        y_blue_barons: np.ndarray,
        y_red_barons: np.ndarray,
        y_blue_towers: np.ndarray,
        y_red_towers: np.ndarray,
    ) -> dict:
        """Treinar modelo multi-saída para objetivos."""
        Y = np.column_stack([
            y_blue_dragons, y_red_dragons,
            y_blue_barons, y_red_barons,
            y_blue_towers, y_red_towers,
        ])

        valid_mask = np.all(Y >= 0, axis=1)
        X_valid = X[valid_mask]
        Y_valid = Y[valid_mask]

        if len(X_valid) < 10:
            raise ValueError("Dados insuficientes para treinar objetivos")

        X_scaled = self.scaler.fit_transform(X_valid)
        base_model = GradientBoostingRegressor(
            n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42
        )
        self.model = MultiOutputRegressor(base_model)
        self.model.fit(X_scaled, Y_valid)
        self.is_trained = True

        pred = self.model.predict(X_scaled)
        mae = float(np.mean(np.abs(pred - Y_valid)))
        logger.info(f"ObjectivesPredictor treinado: MAE médio = {mae:.2f}")
        return {"mae_train": mae}

    def predict_objectives(self, X: np.ndarray) -> Optional[dict]:
        """Prever objetivos para uma partida."""
        if not self.is_trained or self.model is None:
            return None
        try:
            X_scaled = self.scaler.transform(X.reshape(1, -1))
            pred = self.model.predict(X_scaled)[0]
            return {
                "blue_dragons": max(0.0, round(float(pred[0]), 1)),
                "red_dragons": max(0.0, round(float(pred[1]), 1)),
                "blue_barons": max(0.0, round(float(pred[2]), 1)),
                "red_barons": max(0.0, round(float(pred[3]), 1)),
                "blue_towers": max(0.0, round(float(pred[4]), 1)),
                "red_towers": max(0.0, round(float(pred[5]), 1)),
            }
        except Exception as e:
            logger.warning(f"Erro na predição de objetivos: {e}")
            return None

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({"model": self.model, "scaler": self.scaler}, self.model_path)

    def load(self) -> bool:
        if not os.path.exists(self.model_path):
            return False
        try:
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.is_trained = True
            return True
        except Exception as e:
            logger.warning(f"Erro ao carregar ObjectivesPredictor: {e}")
            return False
