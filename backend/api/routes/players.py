"""Rotas para Jogadores."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.player import Player
from backend.schemas.player import PlayerResponse

router = APIRouter()


@router.get("/", response_model=list[PlayerResponse], summary="Listar jogadores")
def list_players(
    role: Optional[str] = Query(None, description="Filtrar por função: top, jungle, mid, bot, support"),
    team_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Listar todos os jogadores cadastrados."""
    query = db.query(Player)
    if role:
        query = query.filter(Player.role == role.lower())
    if team_id:
        query = query.filter(Player.team_id == team_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{player_id}", response_model=PlayerResponse, summary="Detalhes de um jogador")
def get_player(player_id: int, db: Session = Depends(get_db)):
    """Retornar detalhes de um jogador específico."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    return player
