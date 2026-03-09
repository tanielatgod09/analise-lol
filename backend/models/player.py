"""Modelo de Jogador (Player)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Player(Base):
    """Representa um jogador profissional de League of Legends."""

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True, nullable=True)
    name = Column(String(200), nullable=False)  # In-game name (IGN)
    real_name = Column(String(200), nullable=True)
    role = Column(String(50), nullable=True)  # top, jungle, mid, bot, support

    # Relacionamento com time
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    nationality = Column(String(100), nullable=True)

    # Estatísticas (apenas com a line-up atual)
    kda = Column(Float, nullable=True)
    kill_participation = Column(Float, nullable=True)  # percentual
    avg_kills = Column(Float, nullable=True)
    avg_deaths = Column(Float, nullable=True)
    avg_assists = Column(Float, nullable=True)

    # Pool de campeões: [{"champion": "Azir", "games": 10, "winrate": 0.7, "kda": 4.5}]
    champion_pool = Column(JSON, nullable=True)

    # Performance por patch: {"14.8": {"kda": 4.2, "winrate": 0.65}}
    patch_performance = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    team = relationship("Team", back_populates="players", foreign_keys=[team_id])

    def __repr__(self) -> str:
        return f"<Player(id={self.id}, name='{self.name}', role='{self.role}')>"
