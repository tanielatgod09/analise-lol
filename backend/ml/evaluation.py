"""
Avaliação dos modelos de Machine Learning.

Calcula métricas de desempenho para cada modelo.
"""
import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    brier_score_loss,
    mean_absolute_error,
    mean_squared_error,
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ModelEvaluator:
    """Avalia a qualidade dos modelos de ML."""

    def evaluate_classifier(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
    ) -> dict:
        """
        Avaliar modelo de classificação (ex: previsão de vitória).

        Args:
            y_true: Labels verdadeiros (0 ou 1)
            y_pred_proba: Probabilidades previstas [0, 1]
        """
        y_pred = (y_pred_proba >= 0.5).astype(int)
        return {
            "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
            "roc_auc": round(float(roc_auc_score(y_true, y_pred_proba)), 4),
            "brier_score": round(float(brier_score_loss(y_true, y_pred_proba)), 4),
            "n_samples": len(y_true),
        }

    def evaluate_regressor(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        label: str = "target",
    ) -> dict:
        """
        Avaliar modelo de regressão (ex: kills, duração).
        """
        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        return {
            f"{label}_mae": round(mae, 3),
            f"{label}_rmse": round(rmse, 3),
            "n_samples": len(y_true),
        }

    def calibration_test(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        n_bins: int = 10,
    ) -> dict:
        """
        Verificar calibração do modelo (Expected Calibration Error).

        Um modelo bem calibrado tem ECE próximo de 0.
        Isso é crítico para apostas — precisamos de probabilidades confiáveis.
        """
        from sklearn.calibration import calibration_curve
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_true, y_pred_proba, n_bins=n_bins
        )
        ece = float(np.mean(np.abs(fraction_of_positives - mean_predicted_value)))
        return {
            "expected_calibration_error": round(ece, 4),
            "is_well_calibrated": ece < 0.05,
            "calibration_points": list(zip(
                [round(float(x), 3) for x in mean_predicted_value],
                [round(float(y), 3) for y in fraction_of_positives],
            )),
        }
