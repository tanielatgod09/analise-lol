"""Schemas Pydantic para Odds."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class OddsBase(BaseModel):
    bookmaker: str
    market: str
    selection: str
    odd_value: float
    is_live: bool = False


class OddsCreate(OddsBase):
    match_id: int


class OddsResponse(OddsBase):
    id: int
    match_id: int
    implied_probability: Optional[float] = None
    collected_at: datetime

    class Config:
        from_attributes = True


class OddsComparisonResponse(BaseModel):
    """Comparação de odds entre casas de apostas para um mercado."""
    market: str
    selection: str
    bookmakers: list[dict]  # [{"bookmaker": "Pinnacle", "odd": 1.85, "implied_prob": 0.541}]
    best_odd: float
    best_bookmaker: str
