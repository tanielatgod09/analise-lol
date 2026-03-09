"""
Motor de Probabilidades — calcula probabilidades reais de eventos
usando múltiplos fatores estatísticos.
"""
import numpy as np
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.team import Team
from backend.models.match import Match
from backend.services.stats_calculator import StatsCalculator
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ProbabilityEngine:
    """
    Calcula probabilidades reais de vitória e eventos usando:
    - Modelo de Elo adaptado
    - Histórico de confrontos diretos
    - Estatísticas recentes com a line-up atual
    - Estilo de jogo e meta do patch
    """

    def __init__(self, db: Session):
        self.db = db
        self.stats_calc = StatsCalculator(db)

    def calculate_win_probability(
        self,
        match: Match,
        ml_probability: Optional[float] = None,
    ) -> dict:
        """
        Calcular probabilidade de vitória para cada time em uma partida.

        Combina múltiplos fatores para gerar uma estimativa robusta.

        Returns:
            Dict com blue_win_prob, red_win_prob, confidence, method
        """
        blue_team = self.db.query(Team).filter(Team.id == match.team_blue_id).first()
        red_team = self.db.query(Team).filter(Team.id == match.team_red_id).first()

        if not blue_team or not red_team:
            logger.warning(f"Times não encontrados para partida {match.id}")
            return {"blue_win_prob": 0.5, "red_win_prob": 0.5, "confidence": 0.0}

        # 1. Base: winrate com line-up atual
        blue_wr = blue_team.winrate or 0.5
        red_wr = red_team.winrate or 0.5

        # Normalizar winrates para probabilidades relativas
        total_wr = blue_wr + red_wr
        if total_wr > 0:
            base_blue = blue_wr / total_wr
        else:
            base_blue = 0.5

        # 2. Fator de confronto direto (H2H)
        h2h = self.stats_calc.get_head_to_head(match.team_blue_id, match.team_red_id)
        h2h_blue = h2h.get("team1_winrate_h2h", 0.5)
        h2h_weight = min(0.3, h2h.get("total_games", 0) * 0.05)  # Peso máximo 30%

        # 3. Fator de gold por minuto (proxy de força)
        blue_gpm = blue_team.gold_per_minute or 0
        red_gpm = red_team.gold_per_minute or 0
        total_gpm = blue_gpm + red_gpm
        gpm_factor = (blue_gpm / total_gpm - 0.5) * 0.15 if total_gpm > 0 else 0

        # 4. Combinar fatores
        winrate_weight = 1.0 - h2h_weight
        combined = (
            base_blue * winrate_weight
            + h2h_blue * h2h_weight
            + gpm_factor
        )

        # 5. Se modelo ML disponível, combinar com peso maior
        if ml_probability is not None:
            combined = ml_probability * 0.6 + combined * 0.4

        # Limitar entre 5% e 95%
        blue_prob = float(np.clip(combined, 0.05, 0.95))
        red_prob = 1.0 - blue_prob

        # Confiança baseada em número de jogos disponíveis
        min_games = min(
            blue_team.games_played or 0,
            red_team.games_played or 0,
        )
        confidence = min(1.0, min_games / 20.0)  # 20 jogos = confiança máxima

        return {
            "blue_win_prob": round(blue_prob, 4),
            "red_win_prob": round(red_prob, 4),
            "confidence": round(confidence, 4),
            "method": "statistical_composite" if ml_probability is None else "ml_composite",
            "factors": {
                "base_winrate": round(base_blue, 4),
                "h2h_winrate": round(h2h_blue, 4),
                "h2h_games": h2h.get("total_games", 0),
                "gpm_factor": round(gpm_factor, 4),
                "ml_probability": ml_probability,
            },
        }

    def calculate_implied_probability(self, odd: float) -> float:
        """Calcular probabilidade implícita a partir da odd decimal."""
        if odd <= 0:
            raise ValueError(f"Odd inválida: {odd}")
        return round(1 / odd, 4)

    def remove_vig(self, odds: list[float]) -> list[float]:
        """
        Remover a margem da casa de apostas (vig/juice) das odds.

        Retorna probabilidades "true" sem a margem da casa.
        """
        implied_probs = [1 / o for o in odds if o > 0]
        total = sum(implied_probs)
        if total == 0:
            return [1 / len(odds)] * len(odds)
        return [p / total for p in implied_probs]

    def calculate_phase_advantage(self, blue_team: Team, red_team: Team) -> dict:
        """
        Calcular vantagem por fase do jogo com base no estilo dos times.

        Returns:
            Dict com early/mid/late advantage ("blue", "red", ou "equal")
        """

        def get_style_scores(team: Team) -> dict:
            style = (team.playstyle or "").lower()
            if "early" in style:
                return {"early": 0.7, "mid": 0.5, "late": 0.35}
            elif "late" in style:
                return {"early": 0.35, "mid": 0.5, "late": 0.7}
            else:  # mid game
                return {"early": 0.5, "mid": 0.65, "late": 0.45}

        blue_scores = get_style_scores(blue_team)
        red_scores = get_style_scores(red_team)

        def compare(blue_val: float, red_val: float) -> str:
            diff = blue_val - red_val
            if diff > 0.1:
                return "blue"
            elif diff < -0.1:
                return "red"
            return "equal"

        return {
            "early": compare(blue_scores["early"], red_scores["early"]),
            "mid": compare(blue_scores["mid"], red_scores["mid"]),
            "late": compare(blue_scores["late"], red_scores["late"]),
        }
