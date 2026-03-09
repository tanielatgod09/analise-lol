"""Modelo de Partida (Match)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from backend.database import Base


class Match(Base):
    """Representa uma partida profissional de League of Legends."""

    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True, nullable=True)
    league = Column(String(50), nullable=True)
    tournament = Column(String(200), nullable=True)

    # Times
    team_blue_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team_red_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # Status: scheduled, running, finished, cancelled
    status = Column(String(50), nullable=True)

    # Timestamps
    scheduled_at = Column(DateTime, nullable=True, index=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Meta
    patch = Column(String(20), nullable=True)
    series_type = Column(String(10), nullable=True)  # BO1, BO3, BO5

    # Estatísticas da partida
    blue_kills = Column(Integer, nullable=True)
    red_kills = Column(Integer, nullable=True)
    blue_towers = Column(Integer, nullable=True)
    red_towers = Column(Integer, nullable=True)
    blue_dragons = Column(Integer, nullable=True)
    red_dragons = Column(Integer, nullable=True)
    blue_barons = Column(Integer, nullable=True)
    red_barons = Column(Integer, nullable=True)
    blue_gold = Column(BigInteger, nullable=True)
    red_gold = Column(BigInteger, nullable=True)

    # Dados do draft (JSON completo dos picks e bans)
    draft_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    team_blue = relationship("Team", back_populates="home_matches", foreign_keys=[team_blue_id])
    team_red = relationship("Team", back_populates="away_matches", foreign_keys=[team_red_id])
    odds_list = relationship("Odds", back_populates="match")
    predictions = relationship("Prediction", back_populates="match")
    bet_recommendations = relationship("BetRecommendation", back_populates="match")

    @property
    def total_kills(self) -> int | None:
        """Total de kills da partida."""
        if self.blue_kills is not None and self.red_kills is not None:
            return self.blue_kills + self.red_kills
        return None

    @property
    def duration_minutes(self) -> float | None:
        """Duração da partida em minutos."""
        if self.duration_seconds is not None:
            return self.duration_seconds / 60
        return None

    def __repr__(self) -> str:
        return f"<Match(id={self.id}, league='{self.league}', status='{self.status}')>"
