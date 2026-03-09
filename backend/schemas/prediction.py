"""Schemas Pydantic para Previsões e Recomendações de Apostas."""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class PredictionResponse(BaseModel):
    id: int
    match_id: int
    blue_win_probability: Optional[float] = None
    red_win_probability: Optional[float] = None
    predicted_total_kills: Optional[float] = None
    kills_std_dev: Optional[float] = None
    predicted_duration_seconds: Optional[float] = None
    predicted_blue_dragons: Optional[float] = None
    predicted_red_dragons: Optional[float] = None
    early_game_advantage: Optional[str] = None
    mid_game_advantage: Optional[str] = None
    late_game_advantage: Optional[str] = None
    upset_risk_score: Optional[float] = None
    confidence_score: Optional[float] = None
    model_used: Optional[str] = None
    monte_carlo_simulations: Optional[int] = None
    detailed_results: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BetRecommendationResponse(BaseModel):
    id: int
    match_id: int
    market: str
    selection: str
    bookmaker: Optional[str] = None
    odd_value: float
    real_probability: float
    implied_probability: float
    expected_value: float
    classification: Optional[str] = None
    confidence_level: Optional[float] = None
    is_highlighted: bool = False
    reasoning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FullAnalysisResponse(BaseModel):
    """Análise completa de uma partida."""
    match_id: int
    prediction: Optional[PredictionResponse] = None
    bet_recommendations: list[BetRecommendationResponse] = []
    highlighted_bets: list[BetRecommendationResponse] = []
    draft_analysis: Optional[dict] = None
    upset_analysis: Optional[dict] = None
    playstyle_analysis: Optional[dict] = None
