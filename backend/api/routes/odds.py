"""Rotas para Odds."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.odds import Odds
from backend.schemas.odds import OddsResponse, OddsComparisonResponse

router = APIRouter()


@router.get("/match/{match_id}", response_model=list[OddsResponse], summary="Odds de uma partida")
def get_match_odds(match_id: int, db: Session = Depends(get_db)):
    """Retornar todas as odds disponíveis para uma partida."""
    odds = db.query(Odds).filter(Odds.match_id == match_id).order_by(Odds.collected_at.desc()).all()
    return odds


@router.get("/match/{match_id}/comparison", summary="Comparação de odds entre casas de apostas")
def get_odds_comparison(match_id: int, market: Optional[str] = None, db: Session = Depends(get_db)):
    """Comparar odds de diferentes casas de apostas para um mercado."""
    query = db.query(Odds).filter(Odds.match_id == match_id)
    if market:
        query = query.filter(Odds.market == market)

    odds_list = query.order_by(Odds.odd_value.desc()).all()

    # Agrupar por mercado e seleção
    markets: dict = {}
    for odd in odds_list:
        key = f"{odd.market}_{odd.selection}"
        if key not in markets:
            markets[key] = {
                "market": odd.market,
                "selection": odd.selection,
                "bookmakers": [],
                "best_odd": odd.odd_value,
                "best_bookmaker": odd.bookmaker,
            }
        markets[key]["bookmakers"].append({
            "bookmaker": odd.bookmaker,
            "odd": odd.odd_value,
            "implied_prob": round(1 / odd.odd_value, 4) if odd.odd_value > 0 else None,
            "collected_at": odd.collected_at.isoformat(),
        })
        if odd.odd_value > markets[key]["best_odd"]:
            markets[key]["best_odd"] = odd.odd_value
            markets[key]["best_bookmaker"] = odd.bookmaker

    return list(markets.values())
