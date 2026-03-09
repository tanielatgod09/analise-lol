"""
Serviço de cálculo de estatísticas dos times.

Calcula estatísticas detalhadas usando apenas as partidas
disputadas com a line-up atual.
"""
from typing import Optional
from sqlalchemy.orm import Session
import numpy as np

from backend.models.team import Team
from backend.models.match import Match
from backend.services.lineup_tracker import LineupTracker
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class StatsCalculator:
    """Calcula estatísticas avançadas de times usando apenas a line-up atual."""

    def __init__(self, db: Session):
        self.db = db
        self.lineup_tracker = LineupTracker(db)

    def calculate_team_stats(self, team_id: int) -> dict:
        """
        Calcular estatísticas completas de um time com a line-up atual.

        Retorna um dicionário com todas as estatísticas calculadas.
        """
        matches = self.lineup_tracker.get_games_with_current_lineup(team_id)

        if not matches:
            logger.warning(f"Nenhuma partida encontrada para o time {team_id} com a line-up atual")
            return {}

        wins = 0
        kills_list = []
        deaths_list = []
        gold_pm_list = []
        durations = []
        first_bloods = 0
        first_dragons = 0
        first_barons = 0
        towers_list = []
        dragons_list = []
        barons_list = []

        for match in matches:
            is_blue = match.team_blue_id == team_id

            # Vitória
            if match.winner_id == team_id:
                wins += 1

            # Kills e mortes
            if is_blue:
                if match.blue_kills is not None:
                    kills_list.append(match.blue_kills)
                if match.red_kills is not None:
                    deaths_list.append(match.red_kills)
                if match.blue_towers is not None:
                    towers_list.append(match.blue_towers)
                if match.blue_dragons is not None:
                    dragons_list.append(match.blue_dragons)
                if match.blue_barons is not None:
                    barons_list.append(match.blue_barons)
                # Gold por minuto
                if match.blue_gold and match.duration_seconds:
                    gold_pm_list.append(match.blue_gold / (match.duration_seconds / 60))
            else:
                if match.red_kills is not None:
                    kills_list.append(match.red_kills)
                if match.blue_kills is not None:
                    deaths_list.append(match.blue_kills)
                if match.red_towers is not None:
                    towers_list.append(match.red_towers)
                if match.red_dragons is not None:
                    dragons_list.append(match.red_dragons)
                if match.red_barons is not None:
                    barons_list.append(match.red_barons)
                if match.red_gold and match.duration_seconds:
                    gold_pm_list.append(match.red_gold / (match.duration_seconds / 60))

            # Duração
            if match.duration_seconds:
                durations.append(match.duration_seconds)

            # Objetivos first (dados do draft_data se disponível)
            draft = match.draft_data or {}
            if is_blue:
                if draft.get("first_blood_team") == "blue":
                    first_bloods += 1
                if draft.get("first_dragon_team") == "blue":
                    first_dragons += 1
                if draft.get("first_baron_team") == "blue":
                    first_barons += 1
            else:
                if draft.get("first_blood_team") == "red":
                    first_bloods += 1
                if draft.get("first_dragon_team") == "red":
                    first_dragons += 1
                if draft.get("first_baron_team") == "red":
                    first_barons += 1

        n = len(matches)
        stats = {
            "games_played": n,
            "winrate": wins / n if n > 0 else 0.0,
            "kills_per_game": float(np.mean(kills_list)) if kills_list else None,
            "deaths_per_game": float(np.mean(deaths_list)) if deaths_list else None,
            "gold_per_minute": float(np.mean(gold_pm_list)) if gold_pm_list else None,
            "avg_game_duration": float(np.mean(durations)) if durations else None,
            "first_blood_rate": first_bloods / n if n > 0 else None,
            "first_dragon_rate": first_dragons / n if n > 0 else None,
            "first_baron_rate": first_barons / n if n > 0 else None,
            "towers_per_game": float(np.mean(towers_list)) if towers_list else None,
            "dragons_per_game": float(np.mean(dragons_list)) if dragons_list else None,
            "barons_per_game": float(np.mean(barons_list)) if barons_list else None,
        }

        return stats

    def save_team_stats(self, team_id: int) -> None:
        """Calcular e salvar estatísticas do time no banco de dados."""
        stats = self.calculate_team_stats(team_id)
        if not stats:
            return

        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return

        for key, value in stats.items():
            if hasattr(team, key) and value is not None:
                setattr(team, key, value)

        from datetime import datetime
        team.updated_at = datetime.utcnow()
        self.db.commit()
        logger.info(f"Estatísticas do time {team.name} atualizadas")

    def get_head_to_head(self, team1_id: int, team2_id: int) -> dict:
        """
        Calcular histórico de confrontos diretos entre dois times,
        considerando apenas partidas com as line-ups atuais.
        """
        from sqlalchemy import and_, or_
        from datetime import datetime

        t1 = self.db.query(Team).filter(Team.id == team1_id).first()
        t2 = self.db.query(Team).filter(Team.id == team2_id).first()

        if not t1 or not t2:
            return {}

        # Data mais recente de mudança de line-up entre os dois times
        lineup_date = None
        for team in [t1, t2]:
            if team.current_lineup_since:
                if lineup_date is None or team.current_lineup_since > lineup_date:
                    lineup_date = team.current_lineup_since

        query = self.db.query(Match).filter(
            or_(
                and_(Match.team_blue_id == team1_id, Match.team_red_id == team2_id),
                and_(Match.team_blue_id == team2_id, Match.team_red_id == team1_id),
            ),
            Match.status == "finished",
        )

        if lineup_date:
            query = query.filter(Match.scheduled_at >= lineup_date)

        h2h_matches = query.order_by(Match.scheduled_at.desc()).limit(20).all()

        t1_wins = sum(1 for m in h2h_matches if m.winner_id == team1_id)
        t2_wins = sum(1 for m in h2h_matches if m.winner_id == team2_id)
        total = len(h2h_matches)

        return {
            "team1_id": team1_id,
            "team1_name": t1.name if t1 else None,
            "team2_id": team2_id,
            "team2_name": t2.name if t2 else None,
            "total_games": total,
            "team1_wins": t1_wins,
            "team2_wins": t2_wins,
            "team1_winrate_h2h": t1_wins / total if total > 0 else 0.5,
        }
