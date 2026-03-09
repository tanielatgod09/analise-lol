"""
Analisador de Estilo de Jogo dos Times.

Classifica times como Early Game, Mid Game ou Late Game.
Analisa também o ritmo (pace) de cada time.
"""
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.team import Team
from backend.services.lineup_tracker import LineupTracker
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PlaystyleAnalyzer:
    """
    Classifica o estilo de jogo e ritmo de cada time com base em
    estatísticas reais das suas partidas com a line-up atual.
    """

    def __init__(self, db: Session):
        self.db = db
        self.lineup_tracker = LineupTracker(db)

    def classify_playstyle(self, team: Team) -> str:
        """
        Classificar o estilo de jogo como Early, Mid ou Late Game.

        Critérios:
        - Early Game Team: alto first_blood_rate, alto first_dragon_rate,
          curto avg_game_duration
        - Late Game Team: baixo first_blood_rate, longo avg_game_duration,
          alto gold_per_minute
        - Mid Game Team: equilíbrio entre os dois
        """
        if not team:
            return "unknown"

        score_early = 0.0
        score_late = 0.0

        # First blood rate alto = early game
        if team.first_blood_rate is not None:
            if team.first_blood_rate > 0.55:
                score_early += 2
            elif team.first_blood_rate < 0.45:
                score_late += 1

        # Duração média curta = early game
        if team.avg_game_duration is not None:
            duration_min = team.avg_game_duration / 60
            if duration_min < 29:
                score_early += 2
            elif duration_min > 33:
                score_late += 2

        # First dragon rate alto = early game (objetivos precoces)
        if team.first_dragon_rate is not None:
            if team.first_dragon_rate > 0.60:
                score_early += 1
            elif team.first_dragon_rate < 0.40:
                score_late += 1

        if score_early >= 3:
            return "early_game"
        elif score_late >= 3:
            return "late_game"
        else:
            return "mid_game"

    def classify_game_pace(self, team: Team) -> str:
        """
        Classificar o ritmo de jogo do time.

        Categorias: muito_agressivo, agressivo, equilibrado, lento
        """
        if not team:
            return "unknown"

        # Usamos kills_per_game como proxy principal do ritmo
        kills = team.kills_per_game or 0

        if kills >= 16:
            return "muito_agressivo"
        elif kills >= 13:
            return "agressivo"
        elif kills >= 9:
            return "equilibrado"
        else:
            return "lento"

    def analyze_pace_metrics(self, matches: list) -> dict:
        """
        Calcular métricas de ritmo de jogo a partir de uma lista de partidas.

        Retorna:
        - kills_per_minute
        - dragons_per_minute
        - barons_per_minute
        - towers_per_minute
        """
        if not matches:
            return {}

        import numpy as np

        kpm_list = []
        dpm_list = []
        bpm_list = []
        tpm_list = []

        for match in matches:
            dur_min = match.duration_seconds / 60 if match.duration_seconds else None
            if not dur_min or dur_min <= 0:
                continue

            total_kills = (match.blue_kills or 0) + (match.red_kills or 0)
            total_dragons = (match.blue_dragons or 0) + (match.red_dragons or 0)
            total_barons = (match.blue_barons or 0) + (match.red_barons or 0)
            total_towers = (match.blue_towers or 0) + (match.red_towers or 0)

            kpm_list.append(total_kills / dur_min)
            dpm_list.append(total_dragons / dur_min)
            bpm_list.append(total_barons / dur_min)
            tpm_list.append(total_towers / dur_min)

        return {
            "kills_per_minute": round(float(np.mean(kpm_list)), 4) if kpm_list else None,
            "dragons_per_minute": round(float(np.mean(dpm_list)), 4) if dpm_list else None,
            "barons_per_minute": round(float(np.mean(bpm_list)), 4) if bpm_list else None,
            "towers_per_minute": round(float(np.mean(tpm_list)), 4) if tpm_list else None,
        }

    def update_team_classification(self, team_id: int) -> None:
        """Atualizar classificação de estilo de jogo no banco de dados."""
        from datetime import datetime
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return

        team.playstyle = self.classify_playstyle(team)
        team.game_pace = self.classify_game_pace(team)
        team.updated_at = datetime.utcnow()
        self.db.commit()
        logger.info(
            f"Time {team.name}: playstyle={team.playstyle}, pace={team.game_pace}"
        )
