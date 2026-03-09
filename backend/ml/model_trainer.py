"""
Treinador dos Modelos de Machine Learning.

Orquestra o treinamento de todos os modelos usando dados históricos.
"""
from sqlalchemy.orm import Session
from backend.ml.feature_engineering import FeatureEngineer
from backend.ml.models.win_predictor import WinPredictor
from backend.ml.models.kills_predictor import KillsPredictor
from backend.ml.models.duration_predictor import DurationPredictor
from backend.ml.models.objectives_predictor import ObjectivesPredictor
from backend.models.match import Match
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ModelTrainer:
    """Treina e salva todos os modelos de ML."""

    def __init__(self, db: Session):
        self.db = db
        self.feature_engineer = FeatureEngineer(db)
        self.win_predictor = WinPredictor()
        self.kills_predictor = KillsPredictor()
        self.duration_predictor = DurationPredictor()
        self.objectives_predictor = ObjectivesPredictor()

    def train_all_models(self) -> dict:
        """
        Treinar todos os modelos usando dados históricos do banco.

        Returns:
            Dicionário com métricas de avaliação de cada modelo
        """
        logger.info("Iniciando treinamento de todos os modelos...")

        # Buscar partidas finalizadas
        matches = (
            self.db.query(Match)
            .filter(Match.status == "finished", Match.winner_id.isnot(None))
            .order_by(Match.scheduled_at.desc())
            .limit(5000)
            .all()
        )
        logger.info(f"{len(matches)} partidas disponíveis para treinamento")

        if len(matches) < 50:
            logger.warning("Dados insuficientes para treinar modelos (mínimo: 50 partidas)")
            return {"status": "insufficient_data", "n_matches": len(matches)}

        # Construir dataset
        X, y_win, y_kills, y_duration = self.feature_engineer.build_training_dataset(matches)

        if len(X) == 0:
            return {"status": "no_features_extracted"}

        logger.info(f"Dataset: {len(X)} amostras com {X.shape[1]} features")

        results = {}

        # Treinar modelo de vitória
        try:
            results["win_predictor"] = self.win_predictor.train(X, y_win)
            self.win_predictor.save()
        except Exception as e:
            logger.error(f"Erro ao treinar WinPredictor: {e}")
            results["win_predictor"] = {"error": str(e)}

        # Treinar modelo de kills
        try:
            results["kills_predictor"] = self.kills_predictor.train(X, y_kills)
            self.kills_predictor.save()
        except Exception as e:
            logger.error(f"Erro ao treinar KillsPredictor: {e}")
            results["kills_predictor"] = {"error": str(e)}

        # Treinar modelo de duração
        try:
            results["duration_predictor"] = self.duration_predictor.train(X, y_duration)
            self.duration_predictor.save()
        except Exception as e:
            logger.error(f"Erro ao treinar DurationPredictor: {e}")
            results["duration_predictor"] = {"error": str(e)}

        logger.info("Treinamento concluído")
        results["status"] = "success"
        results["n_training_samples"] = len(X)
        return results
