"""Schemas Pydantic para Partidas."""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class MatchBase(BaseModel):
    league: Optional[str] = None
    tournament: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    patch: Optional[str] = None
    series_type: Optional[str] = None


class MatchCreate(MatchBase):
    external_id: Optional[str] = None
    team_blue_id: Optional[int] = None
    team_red_id: Optional[int] = None


class MatchResponse(MatchBase):
    id: int
    external_id: Optional[str] = None
    team_blue_id: Optional[int] = None
    team_red_id: Optional[int] = None
    winner_id: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    blue_kills: Optional[int] = None
    red_kills: Optional[int] = None
    blue_towers: Optional[int] = None
    red_towers: Optional[int] = None
    blue_dragons: Optional[int] = None
    red_dragons: Optional[int] = None
    blue_barons: Optional[int] = None
    red_barons: Optional[int] = None
    draft_data: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpcomingMatchResponse(MatchResponse):
    """Partida agendada com informações dos times."""
    blue_team_name: Optional[str] = None
    red_team_name: Optional[str] = None
    blue_team_logo: Optional[str] = None
    red_team_logo: Optional[str] = None
