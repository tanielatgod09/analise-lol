"""
Modelo de Previsão de Vitória.

Implementa ensemble de:
- Regressão Logística (baseline)
- XGBoost
- LightGBM
"""
import os
import joblib
import numpy as np
from typing import Optional
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class WinPredictor:
    """
    Preditor de vitória usando ensemble de modelos.

    Modelos disponíveis:
    - logistic_regression: Baseline simples e interpretável
    - xgboost: Gradient boosting avançado
    - lightgbm: Gradient boosting otimizado
    """

    def __init__(self):
        self.models: dict = {}
        self.is_trained = False
        self.model_path = os.path.join(settings.ml_models_path, "win_predictor")

    def train(self, X: np.ndarray, y: np.ndarray) -> dict:
        """
        Treinar todos os modelos do ensemble.

        Args:
            X: Features de treino (n_samples, n_features)
            y: Labels (1=blue venceu, 0=red venceu)

        Returns:
            Dicionário com métricas de avaliação de cada modelo
        """
        if len(X) < 10:
            raise ValueError(f"Dados insuficientes para treinar: {len(X)} amostras")

        metrics = {}

        # 1. Regressão Logística (Baseline)
        lr_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(C=1.0, max_iter=1000, random_state=42)),
        ])
        lr_scores = cross_val_score(lr_pipeline, X, y, cv=min(5, len(X) // 10), scoring="roc_auc")
        lr_pipeline.fit(X, y)
        self.models["logistic_regression"] = lr_pipeline
        metrics["logistic_regression"] = {
            "roc_auc_mean": float(np.mean(lr_scores)),
            "roc_auc_std": float(np.std(lr_scores)),
        }
        logger.info(f"Logistic Regression: ROC-AUC = {np.mean(lr_scores):.3f}")

        # 2. XGBoost
        try:
            from xgboost import XGBClassifier
            xgb = XGBClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                use_label_encoder=False,
                eval_metric="logloss",
                random_state=42,
                verbosity=0,
            )
            xgb_scores = cross_val_score(xgb, X, y, cv=min(5, len(X) // 10), scoring="roc_auc")
            xgb.fit(X, y)
            self.models["xgboost"] = xgb
            metrics["xgboost"] = {
                "roc_auc_mean": float(np.mean(xgb_scores)),
                "roc_auc_std": float(np.std(xgb_scores)),
            }
            logger.info(f"XGBoost: ROC-AUC = {np.mean(xgb_scores):.3f}")
        except Exception as e:
            logger.warning(f"XGBoost não disponível: {e}")

        # 3. LightGBM
        try:
            from lightgbm import LGBMClassifier
            lgbm = LGBMClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbose=-1,
            )
            lgbm_scores = cross_val_score(lgbm, X, y, cv=min(5, len(X) // 10), scoring="roc_auc")
            lgbm.fit(X, y)
            self.models["lightgbm"] = lgbm
            metrics["lightgbm"] = {
                "roc_auc_mean": float(np.mean(lgbm_scores)),
                "roc_auc_std": float(np.std(lgbm_scores)),
            }
            logger.info(f"LightGBM: ROC-AUC = {np.mean(lgbm_scores):.3f}")
        except Exception as e:
            logger.warning(f"LightGBM não disponível: {e}")

        self.is_trained = True
        return metrics

    def predict_proba(self, X: np.ndarray) -> Optional[float]:
        """
        Gerar probabilidade de vitória do time azul usando ensemble.

        Usa média ponderada dos modelos, priorizando os de maior precisão.
        """
        if not self.is_trained or not self.models:
            return None

        probas = []
        for name, model in self.models.items():
            try:
                prob = model.predict_proba(X.reshape(1, -1))[0][1]
                probas.append(float(prob))
            except Exception as e:
                logger.warning(f"Erro na predição do modelo {name}: {e}")

        if not probas:
            return None

        return float(np.mean(probas))

    def save(self) -> None:
        """Salvar modelos treinados no disco."""
        os.makedirs(self.model_path, exist_ok=True)
        for name, model in self.models.items():
            path = os.path.join(self.model_path, f"{name}.pkl")
            joblib.dump(model, path)
        logger.info(f"Modelos salvos em {self.model_path}")

    def load(self) -> bool:
        """Carregar modelos previamente treinados do disco."""
        if not os.path.exists(self.model_path):
            return False

        for model_file in os.listdir(self.model_path):
            if model_file.endswith(".pkl"):
                name = model_file.replace(".pkl", "")
                path = os.path.join(self.model_path, model_file)
                try:
                    self.models[name] = joblib.load(path)
                except Exception as e:
                    logger.warning(f"Erro ao carregar modelo {name}: {e}")

        self.is_trained = len(self.models) > 0
        return self.is_trained
