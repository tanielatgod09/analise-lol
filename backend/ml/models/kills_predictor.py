"""
Modelo de Previsão de Kills com Distribuição de Poisson.

Usa regressão de Poisson adaptada para LoL para prever
o total de kills em uma partida.
"""
import os
import joblib
import numpy as np
from typing import Optional
from sklearn.linear_model import PoissonRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class KillsPredictor:
    """
    Preditor de kills totais usando regressão de Poisson.

    A distribuição de Poisson é a mais adequada para modelar
    contagem de eventos (kills) em um período de tempo fixo.
    """

    def __init__(self):
        self.model: Optional[Pipeline] = None
        self.is_trained = False
        self.model_path = os.path.join(settings.ml_models_path, "kills_predictor.pkl")

    def train(self, X: np.ndarray, y_kills: np.ndarray) -> dict:
        """
        Treinar modelo de Poisson para kills.

        Args:
            X: Features de treino
            y_kills: Total de kills por partida
        """
        if len(X) < 10:
            raise ValueError(f"Dados insuficientes: {len(X)} amostras")

        # Remover amostras com kills = 0 (provavelmente dados inválidos)
        valid_mask = y_kills > 0
        X_valid = X[valid_mask]
        y_valid = y_kills[valid_mask]

        self.model = Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", PoissonRegressor(alpha=0.1, max_iter=500)),
        ])
        self.model.fit(X_valid, y_valid)
        self.is_trained = True

        # Calcular MAE nos dados de treino
        pred = self.model.predict(X_valid)
        mae = float(np.mean(np.abs(pred - y_valid)))
        logger.info(f"KillsPredictor treinado: MAE = {mae:.2f} kills")

        return {"mae_train": mae, "n_samples": int(len(X_valid))}

    def predict_kills(self, X: np.ndarray) -> Optional[float]:
        """
        Prever total de kills para uma partida.

        Returns:
            Total esperado de kills ou None se modelo não treinado
        """
        if not self.is_trained or self.model is None:
            return None

        try:
            pred = self.model.predict(X.reshape(1, -1))[0]
            return max(0.0, float(pred))
        except Exception as e:
            logger.warning(f"Erro na predição de kills: {e}")
            return None

    def predict_over_under(
        self,
        X: np.ndarray,
        threshold: float = 25.5,
    ) -> Optional[float]:
        """
        Calcular probabilidade de over/under kills usando Poisson.

        Usa a média prevista pelo modelo como lambda da distribuição.
        """
        lambda_pred = self.predict_kills(X)
        if lambda_pred is None:
            return None

        from scipy.stats import poisson
        # Probabilidade de over (total_kills > threshold)
        prob_over = 1 - poisson.cdf(int(threshold), mu=lambda_pred)
        return float(prob_over)

    def save(self) -> None:
        """Salvar modelo no disco."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def load(self) -> bool:
        """Carregar modelo do disco."""
        if not os.path.exists(self.model_path):
            return False
        try:
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            return True
        except Exception as e:
            logger.warning(f"Erro ao carregar KillsPredictor: {e}")
            return False
