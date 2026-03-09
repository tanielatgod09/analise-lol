"""Rotas para Previsões e Recomendações de Apostas."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.match import Match
from backend.models.prediction import Prediction
from backend.models.bet_recommendation import BetRecommendation
from backend.schemas.prediction import PredictionResponse, BetRecommendationResponse, FullAnalysisResponse
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/match/{match_id}", response_model=FullAnalysisResponse, summary="Análise completa da partida")
def get_full_analysis(match_id: int, db: Session = Depends(get_db)):
    """Retornar análise completa com previsões e apostas recomendadas."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    prediction = (
        db.query(Prediction)
        .filter(Prediction.match_id == match_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )

    recommendations = (
        db.query(BetRecommendation)
        .filter(BetRecommendation.match_id == match_id)
        .order_by(BetRecommendation.expected_value.desc())
        .all()
    )

    highlighted = [r for r in recommendations if r.is_highlighted]

    return FullAnalysisResponse(
        match_id=match_id,
        prediction=PredictionResponse.model_validate(prediction) if prediction else None,
        bet_recommendations=[BetRecommendationResponse.model_validate(r) for r in recommendations],
        highlighted_bets=[BetRecommendationResponse.model_validate(r) for r in highlighted],
    )


@router.post("/match/{match_id}/generate", summary="Gerar previsões para uma partida")
def generate_prediction(
    match_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Disparar geração de previsões para uma partida em background."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    background_tasks.add_task(_generate_prediction_task, match_id)
    return {"message": f"Geração de previsão iniciada para partida {match_id}", "match_id": match_id}


def _generate_prediction_task(match_id: int) -> None:
    """Tarefa em background para gerar previsões."""
    try:
        from backend.services.bet_recommender import BetRecommender
        from backend.database import SessionLocal
        db = SessionLocal()
        try:
            recommender = BetRecommender(db)
            recommender.generate_recommendations(match_id)
        finally:
            db.close()
    except Exception as exc:
        logger.error(f"Erro ao gerar previsão para partida {match_id}: {exc}")


@router.get("/highlighted", response_model=list[BetRecommendationResponse], summary="Apostas em destaque")
def get_highlighted_bets(
    min_confidence: float = 0.75,
    db: Session = Depends(get_db),
):
    """Retornar apostas recomendadas com probabilidade acima do limiar."""
    bets = (
        db.query(BetRecommendation)
        .filter(
            BetRecommendation.is_highlighted == True,  # noqa: E712
            BetRecommendation.confidence_level >= min_confidence,
        )
        .order_by(BetRecommendation.expected_value.desc())
        .limit(50)
        .all()
    )
    return bets
