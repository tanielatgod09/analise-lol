"""Schemas Pydantic para Times."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str
    acronym: Optional[str] = None
    league: Optional[str] = None
    region: Optional[str] = None
    logo_url: Optional[str] = None


class TeamCreate(TeamBase):
    external_id: Optional[str] = None


class TeamUpdate(BaseModel):
    winrate: Optional[float] = None
    games_played: Optional[int] = None
    kills_per_game: Optional[float] = None
    deaths_per_game: Optional[float] = None
    gold_per_minute: Optional[float] = None
    first_blood_rate: Optional[float] = None
    first_dragon_rate: Optional[float] = None
    first_baron_rate: Optional[float] = None
    towers_per_game: Optional[float] = None
    avg_game_duration: Optional[float] = None
    playstyle: Optional[str] = None
    game_pace: Optional[str] = None


class TeamResponse(TeamBase):
    id: int
    external_id: Optional[str] = None
    current_lineup_since: Optional[datetime] = None
    winrate: Optional[float] = None
    games_played: Optional[int] = None
    kills_per_game: Optional[float] = None
    deaths_per_game: Optional[float] = None
    gold_per_minute: Optional[float] = None
    first_blood_rate: Optional[float] = None
    first_dragon_rate: Optional[float] = None
    first_baron_rate: Optional[float] = None
    towers_per_game: Optional[float] = None
    avg_game_duration: Optional[float] = None
    playstyle: Optional[str] = None
    game_pace: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
