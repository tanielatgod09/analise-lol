"""Rotas para Times."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.team import Team
from backend.schemas.team import TeamResponse

router = APIRouter()


@router.get("/", response_model=list[TeamResponse], summary="Listar times")
def list_teams(
    league: Optional[str] = Query(None, description="Filtrar por liga"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Listar todos os times cadastrados."""
    query = db.query(Team)
    if league:
        query = query.filter(Team.league == league.upper())
    return query.offset(skip).limit(limit).all()


@router.get("/{team_id}", response_model=TeamResponse, summary="Detalhes de um time")
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Retornar detalhes de um time específico."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    return team


@router.get("/{team_id}/stats", summary="Estatísticas detalhadas do time")
def get_team_stats(team_id: int, db: Session = Depends(get_db)):
    """Retornar estatísticas detalhadas do time com a line-up atual."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Time não encontrado")

    return {
        "id": team.id,
        "name": team.name,
        "league": team.league,
        "current_lineup_since": team.current_lineup_since,
        "games_played": team.games_played,
        "winrate": team.winrate,
        "kills_per_game": team.kills_per_game,
        "deaths_per_game": team.deaths_per_game,
        "gold_per_minute": team.gold_per_minute,
        "first_blood_rate": team.first_blood_rate,
        "first_dragon_rate": team.first_dragon_rate,
        "first_baron_rate": team.first_baron_rate,
        "towers_per_game": team.towers_per_game,
        "avg_game_duration_minutes": (team.avg_game_duration or 0) / 60 if team.avg_game_duration else None,
        "playstyle": team.playstyle,
        "game_pace": team.game_pace,
        "patch_performance": team.patch_performance,
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "role": p.role,
                "kda": p.kda,
                "kill_participation": p.kill_participation,
            }
            for p in (team.players or [])
        ],
    }
