"""
Detector de Upsets — calcula o risco de o time considerado azarão vencer.

Upset Risk Score (0–100):
- 0–30  → risco baixo
- 30–60 → risco moderado
- 60–100 → alto risco de upset
"""
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.team import Team
from backend.models.match import Match
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class UpsetDetector:
    """Calcula o risco de upset em uma partida."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_upset_risk(
        self,
        match: Match,
        predicted_winner_id: int,
        win_probability: float,
    ) -> dict:
        """
        Calcular o risco de upset para o time considerado azarão.

        Args:
            match: Partida a analisar
            predicted_winner_id: ID do time com maior probabilidade de vencer
            win_probability: Probabilidade do favorito (0-1)

        Returns:
            Dict com upset_risk_score (0-100) e classificação
        """
        upset_risk = 0.0

        # Fator 1: Quanto menor a probabilidade do favorito, maior o risco
        # (1 - win_prob) × 100 como base
        base_risk = (1 - win_probability) * 100

        # Fator 2: Forma recente do azarão
        underdog_id = (
            match.team_red_id if predicted_winner_id == match.team_blue_id
            else match.team_blue_id
        )
        underdog = self.db.query(Team).filter(Team.id == underdog_id).first()
        favorite = self.db.query(Team).filter(Team.id == predicted_winner_id).first()

        recent_form_boost = 0.0
        if underdog and underdog.winrate and (underdog.winrate > 0.50):
            recent_form_boost = (underdog.winrate - 0.50) * 30

        # Fator 3: Jogos recentes com linha de uptick
        momentum_boost = 0.0
        recent_matches = self._get_last_n_matches(underdog_id, 5)
        if recent_matches:
            recent_wins = sum(1 for m in recent_matches if m.winner_id == underdog_id)
            momentum = recent_wins / len(recent_matches)
            if momentum > 0.6:
                momentum_boost = (momentum - 0.6) * 25

        # Fator 4: Estilo de jogo — late game vs early game pode ser upset
        style_boost = 0.0
        if underdog and favorite:
            underdog_style = (underdog.playstyle or "").lower()
            favorite_style = (favorite.playstyle or "").lower()
            # Late game underdog vs Early game favorite = maior risco de upset
            if "late" in underdog_style and "early" in favorite_style:
                style_boost = 10.0

        upset_risk = min(100.0, base_risk + recent_form_boost + momentum_boost + style_boost)

        if upset_risk <= 30:
            classification = "baixo"
        elif upset_risk <= 60:
            classification = "moderado"
        else:
            classification = "alto"

        # Fator de redução de confiança para apostas quando risco alto
        confidence_reduction = 0.0
        if classification == "alto":
            confidence_reduction = 0.20
        elif classification == "moderado":
            confidence_reduction = 0.10

        return {
            "upset_risk_score": round(upset_risk, 1),
            "classification": classification,
            "confidence_reduction": confidence_reduction,
            "underdog_id": underdog_id,
            "underdog_name": underdog.name if underdog else None,
            "factors": {
                "base_risk": round(base_risk, 1),
                "recent_form_boost": round(recent_form_boost, 1),
                "momentum_boost": round(momentum_boost, 1),
                "style_boost": round(style_boost, 1),
            },
        }

    def _get_last_n_matches(self, team_id: int, n: int) -> list:
        """Buscar as últimas N partidas de um time."""
        from sqlalchemy import or_
        return (
            self.db.query(Match)
            .filter(
                or_(Match.team_blue_id == team_id, Match.team_red_id == team_id),
                Match.status == "finished",
            )
            .order_by(Match.scheduled_at.desc())
            .limit(n)
            .all()
        )
