"""Modelo de Previsão (Prediction)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Prediction(Base):
    """Armazena as previsões do sistema para uma partida."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)

    # Probabilidades de vitória
    blue_win_probability = Column(Float, nullable=True)
    red_win_probability = Column(Float, nullable=True)

    # Previsões de kills
    predicted_total_kills = Column(Float, nullable=True)
    kills_std_dev = Column(Float, nullable=True)

    # Previsão de duração
    predicted_duration_seconds = Column(Float, nullable=True)

    # Previsões de objetivos
    predicted_blue_dragons = Column(Float, nullable=True)
    predicted_red_dragons = Column(Float, nullable=True)
    predicted_blue_barons = Column(Float, nullable=True)
    predicted_red_barons = Column(Float, nullable=True)
    predicted_blue_towers = Column(Float, nullable=True)
    predicted_red_towers = Column(Float, nullable=True)

    # Vantagem por fase do jogo
    early_game_advantage = Column(String(10), nullable=True)   # "blue", "red", "equal"
    mid_game_advantage = Column(String(10), nullable=True)
    late_game_advantage = Column(String(10), nullable=True)

    # Métricas de qualidade
    upset_risk_score = Column(Float, nullable=True)  # 0-100
    confidence_score = Column(Float, nullable=True)  # 0-1
    model_used = Column(String(100), nullable=True)
    monte_carlo_simulations = Column(Integer, nullable=True)

    # Resultados detalhados do Monte Carlo e ML
    detailed_results = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    match = relationship("Match", back_populates="predictions")
    bet_recommendations = relationship("BetRecommendation", back_populates="prediction")

    def __repr__(self) -> str:
        return (
            f"<Prediction(match_id={self.match_id}, "
            f"blue_win={self.blue_win_probability:.2%})>"
        )
