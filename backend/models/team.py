"""Modelo de Time (Team)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class Team(Base):
    """Representa um time profissional de League of Legends."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True, nullable=True)
    name = Column(String(200), nullable=False)
    acronym = Column(String(20), nullable=True)
    league = Column(String(50), nullable=True)
    region = Column(String(50), nullable=True)
    logo_url = Column(String(500), nullable=True)

    # Data em que a line-up atual começou a jogar junta
    current_lineup_since = Column(DateTime, nullable=True)

    # Estatísticas gerais (apenas com a line-up atual)
    winrate = Column(Float, nullable=True)
    games_played = Column(Integer, nullable=True)
    kills_per_game = Column(Float, nullable=True)
    deaths_per_game = Column(Float, nullable=True)
    gold_per_minute = Column(Float, nullable=True)

    # Taxas de objetivos
    first_blood_rate = Column(Float, nullable=True)
    first_dragon_rate = Column(Float, nullable=True)
    first_baron_rate = Column(Float, nullable=True)
    towers_per_game = Column(Float, nullable=True)
    avg_game_duration = Column(Float, nullable=True)  # em segundos

    # Classificação de estilo de jogo
    playstyle = Column(String(50), nullable=True)  # Early/Mid/Late Game Team
    game_pace = Column(String(50), nullable=True)  # muito agressivo, agressivo, equilibrado, lento

    # Performance por patch (JSON: {"14.8": {...}, "14.9": {...}})
    patch_performance = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    players = relationship("Player", back_populates="team", foreign_keys="Player.team_id")
    home_matches = relationship("Match", back_populates="team_blue", foreign_keys="Match.team_blue_id")
    away_matches = relationship("Match", back_populates="team_red", foreign_keys="Match.team_red_id")

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}', league='{self.league}')>"
