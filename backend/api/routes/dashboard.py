"""Rotas do Dashboard principal."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.match import Match
from backend.models.bet_recommendation import BetRecommendation
from backend.models.team import Team

router = APIRouter()


@router.get("/", summary="Dados do dashboard principal")
def get_dashboard(db: Session = Depends(get_db)):
    """Retornar resumo do dashboard com jogos do dia e apostas em destaque."""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # Partidas de hoje
    todays_matches = (
        db.query(Match)
        .filter(Match.scheduled_at >= today_start, Match.scheduled_at < today_end)
        .order_by(Match.scheduled_at)
        .all()
    )

    # Apostas em destaque
    highlighted_bets = (
        db.query(BetRecommendation)
        .filter(BetRecommendation.is_highlighted == True)  # noqa: E712
        .order_by(BetRecommendation.expected_value.desc())
        .limit(10)
        .all()
    )

    # Estatísticas gerais
    total_teams = db.query(func.count(Team.id)).scalar() or 0
    total_matches = db.query(func.count(Match.id)).scalar() or 0
    live_matches = db.query(func.count(Match.id)).filter(Match.status == "running").scalar() or 0

    return {
        "resumo": {
            "total_times": total_teams,
            "total_partidas": total_matches,
            "partidas_ao_vivo": live_matches,
            "partidas_hoje": len(todays_matches),
            "apostas_em_destaque": len(highlighted_bets),
        },
        "partidas_hoje": [
            {
                "id": m.id,
                "liga": m.league,
                "horario": m.scheduled_at.isoformat() if m.scheduled_at else None,
                "time_azul": m.team_blue.name if m.team_blue else None,
                "time_vermelho": m.team_red.name if m.team_red else None,
                "status": m.status,
            }
            for m in todays_matches
        ],
        "apostas_em_destaque": [
            {
                "id": b.id,
                "partida_id": b.match_id,
                "mercado": b.market,
                "selecao": b.selection,
                "casa": b.bookmaker,
                "odd": b.odd_value,
                "probabilidade_real": b.real_probability,
                "ev": b.expected_value,
                "classificacao": b.classification,
            }
            for b in highlighted_bets
        ],
        "atualizado_em": now.isoformat(),
    }


@router.get("/stats", summary="Estatísticas globais do sistema")
def get_global_stats(db: Session = Depends(get_db)):
    """Retornar estatísticas globais do sistema."""
    total_bets = db.query(func.count(BetRecommendation.id)).scalar() or 0
    highlighted_bets = (
        db.query(func.count(BetRecommendation.id))
        .filter(BetRecommendation.is_highlighted == True)  # noqa: E712
        .scalar() or 0
    )
    avg_ev = db.query(func.avg(BetRecommendation.expected_value)).scalar()

    return {
        "total_apostas_recomendadas": total_bets,
        "apostas_em_destaque": highlighted_bets,
        "ev_medio": round(avg_ev, 4) if avg_ev else None,
    }
