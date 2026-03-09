"""Schemas Pydantic para Jogadores."""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class PlayerBase(BaseModel):
    name: str
    real_name: Optional[str] = None
    role: Optional[str] = None
    nationality: Optional[str] = None


class PlayerCreate(PlayerBase):
    external_id: Optional[str] = None
    team_id: Optional[int] = None


class PlayerResponse(PlayerBase):
    id: int
    external_id: Optional[str] = None
    team_id: Optional[int] = None
    kda: Optional[float] = None
    kill_participation: Optional[float] = None
    avg_kills: Optional[float] = None
    avg_deaths: Optional[float] = None
    avg_assists: Optional[float] = None
    champion_pool: Optional[Any] = None
    patch_performance: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
