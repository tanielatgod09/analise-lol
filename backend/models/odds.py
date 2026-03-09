"""Modelo de Odds."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Odds(Base):
    """Representa uma odd de uma casa de apostas para uma partida."""

    __tablename__ = "odds"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    bookmaker = Column(String(100), nullable=False)   # "Pinnacle", "1xbet", etc.
    market = Column(String(100), nullable=False)       # "match_winner", "first_blood", etc.
    selection = Column(String(200), nullable=False)    # "blue_team", "over_25.5", etc.
    odd_value = Column(Float, nullable=False)
    implied_probability = Column(Float, nullable=True)
    is_live = Column(Boolean, default=False)
    collected_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    match = relationship("Match", back_populates="odds_list")

    def __repr__(self) -> str:
        return (
            f"<Odds(match_id={self.match_id}, bookmaker='{self.bookmaker}', "
            f"market='{self.market}', odd={self.odd_value})>"
        )
