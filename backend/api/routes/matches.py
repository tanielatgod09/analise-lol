"""Rotas para Partidas."""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.match import Match
from backend.models.team import Team
from backend.schemas.match import MatchResponse, UpcomingMatchResponse

router = APIRouter()


@router.get("/upcoming", response_model=list[UpcomingMatchResponse], summary="Partidas agendadas")
def get_upcoming_matches(
    league: Optional[str] = Query(None, description="Filtrar por liga: LCK, LEC, LCS, CBLOL, LPL"),
    hours_ahead: int = Query(48, description="Horas à frente para buscar partidas"),
    db: Session = Depends(get_db),
):
    """Retornar lista de partidas agendadas para as próximas horas."""
    now = datetime.utcnow()
    until = now + timedelta(hours=hours_ahead)

    query = db.query(Match).filter(
        Match.status == "scheduled",
        Match.scheduled_at >= now,
        Match.scheduled_at <= until,
    )

    if league:
        query = query.filter(Match.league == league.upper())

    matches = query.order_by(Match.scheduled_at).all()

    result = []
    for match in matches:
        match_data = UpcomingMatchResponse.model_validate(match)
        if match.team_blue:
            match_data.blue_team_name = match.team_blue.name
            match_data.blue_team_logo = match.team_blue.logo_url
        if match.team_red:
            match_data.red_team_name = match.team_red.name
            match_data.red_team_logo = match.team_red.logo_url
        result.append(match_data)

    return result


@router.get("/live", response_model=list[MatchResponse], summary="Partidas ao vivo")
def get_live_matches(db: Session = Depends(get_db)):
    """Retornar partidas atualmente em andamento."""
    matches = db.query(Match).filter(Match.status == "running").all()
    return matches


@router.get("/{match_id}", response_model=MatchResponse, summary="Detalhes de uma partida")
def get_match(match_id: int, db: Session = Depends(get_db)):
    """Retornar detalhes de uma partida específica."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    return match


@router.get("/", response_model=list[MatchResponse], summary="Listar partidas")
def list_matches(
    league: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Listar partidas com filtros opcionais."""
    query = db.query(Match)
    if league:
        query = query.filter(Match.league == league.upper())
    if status:
        query = query.filter(Match.status == status)
    return query.order_by(Match.scheduled_at.desc()).offset(skip).limit(limit).all()
