"""Modelo de Recomendação de Aposta (BetRecommendation)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class BetRecommendation(Base):
    """Representa uma aposta recomendada pelo sistema."""

    __tablename__ = "bet_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)

    # Detalhes da aposta
    market = Column(String(100), nullable=False)       # "match_winner", "over_kills_25.5"
    selection = Column(String(200), nullable=False)    # "blue_team", "over"
    bookmaker = Column(String(100), nullable=True)     # "Pinnacle"
    odd_value = Column(Float, nullable=False)

    # Probabilidades
    real_probability = Column(Float, nullable=False)     # calculada pelo sistema
    implied_probability = Column(Float, nullable=False)  # 1 / odd

    # Expected Value: EV = (prob_real * odd) - 1
    expected_value = Column(Float, nullable=False)

    # Classificação: "muito_segura", "boa", "moderada", "arriscada"
    classification = Column(String(50), nullable=True)
    confidence_level = Column(Float, nullable=True)  # 0.0 a 1.0

    # Se deve ser destacada (prob > 75%)
    is_highlighted = Column(Boolean, default=False)

    # Justificativa da recomendação
    reasoning = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    match = relationship("Match", back_populates="bet_recommendations")
    prediction = relationship("Prediction", back_populates="bet_recommendations")

    def __repr__(self) -> str:
        return (
            f"<BetRecommendation(match_id={self.match_id}, market='{self.market}', "
            f"EV={self.expected_value:.3f}, class='{self.classification}')>"
        )
