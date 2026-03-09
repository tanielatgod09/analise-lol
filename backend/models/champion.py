"""Modelo de Campeão (Champion)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from backend.database import Base


class Champion(Base):
    """Representa um campeão de League of Legends com dados do patch atual."""

    __tablename__ = "champions"

    id = Column(Integer, primary_key=True, index=True)
    riot_id = Column(String(100), nullable=True)
    name = Column(String(100), nullable=False)
    title = Column(String(200), nullable=True)
    roles = Column(JSON, nullable=True)  # ["mid", "support"]

    # Patch dos dados
    patch = Column(String(20), nullable=True)

    # Estatísticas no esports profissional
    winrate = Column(Float, nullable=True)
    pickrate = Column(Float, nullable=True)
    banrate = Column(Float, nullable=True)
    avg_kills = Column(Float, nullable=True)
    avg_deaths = Column(Float, nullable=True)
    avg_assists = Column(Float, nullable=True)

    # Estilo de jogo: "early_game", "scaling", "teamfight", "poke", "split_push"
    game_style = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Champion(id={self.id}, name='{self.name}', patch='{self.patch}')>"
