"""Rotas para Live Betting (apostas ao vivo)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.match import Match
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/matches", summary="Partidas ao vivo com oportunidades de aposta")
def get_live_opportunities(db: Session = Depends(get_db)):
    """Retornar partidas ao vivo com oportunidades de aposta identificadas."""
    live_matches = db.query(Match).filter(Match.status == "running").all()

    opportunities = []
    for match in live_matches:
        opportunities.append({
            "match_id": match.id,
            "league": match.league,
            "team_blue": match.team_blue.name if match.team_blue else None,
            "team_red": match.team_red.name if match.team_red else None,
            "status": "ao_vivo",
            "live_opportunities": [],  # populado pelo modelo dinâmico
        })

    return opportunities


@router.post("/update/{match_id}", summary="Atualizar probabilidades ao vivo")
def update_live_probabilities(
    match_id: int,
    game_state: dict,
    db: Session = Depends(get_db),
):
    """
    Atualizar probabilidades em tempo real com base no estado atual da partida.

    Parâmetros do game_state:
    - gold_diff: diferença de gold (blue - red)
    - kills_blue: kills do time azul
    - kills_red: kills do time vermelho
    - dragons_blue: dragões do time azul
    - dragons_red: dragões do time vermelho
    - barons_blue: barões do time azul
    - barons_red: barões do time vermelho
    - towers_blue: torres destruídas pelo azul
    - towers_red: torres destruídas pelo vermelho
    - game_time_seconds: tempo de jogo em segundos
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    try:
        from backend.services.live_betting import LiveBettingService
        service = LiveBettingService()
        result = service.update_probabilities(match, game_state)
        return result
    except Exception as exc:
        logger.error(f"Erro ao atualizar probabilidades live: {exc}")
        raise HTTPException(status_code=500, detail=f"Erro ao calcular probabilidades: {str(exc)}")
