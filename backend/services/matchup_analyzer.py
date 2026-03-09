"""
Analisador de Matchups de Lane.

Compara desempenho individual por posição (top vs top, mid vs mid, bot vs bot)
e calcula vantagem de lane para cada confronto.
"""
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.player import Player
from backend.utils.logger import get_logger

logger = get_logger(__name__)

ROLES = ["top", "jungle", "mid", "bot", "support"]


class MatchupAnalyzer:
    """Analisa matchups individuais por posição entre dois times."""

    def __init__(self, db: Session):
        self.db = db

    def analyze_lane_matchups(
        self,
        team_blue_id: int,
        team_red_id: int,
    ) -> dict:
        """
        Comparar jogadores de cada posição entre os dois times.

        Retorna vantagem estimada por lane.
        """
        blue_players = self._get_players_by_role(team_blue_id)
        red_players = self._get_players_by_role(team_red_id)

        matchups = {}
        for role in ROLES:
            blue_p = blue_players.get(role)
            red_p = red_players.get(role)

            if blue_p and red_p:
                advantage = self._compare_players(blue_p, red_p)
                matchups[role] = {
                    "blue_player": blue_p.name,
                    "red_player": red_p.name,
                    "blue_kda": blue_p.kda,
                    "red_kda": red_p.kda,
                    "blue_kill_participation": blue_p.kill_participation,
                    "red_kill_participation": red_p.kill_participation,
                    "advantage": advantage,
                }
            else:
                matchups[role] = {"advantage": "unknown"}

        # Vantagem geral de lane
        advantages = [v.get("advantage") for v in matchups.values() if v.get("advantage") != "unknown"]
        blue_adv = sum(1 for a in advantages if a == "blue")
        red_adv = sum(1 for a in advantages if a == "red")

        overall = "blue" if blue_adv > red_adv else ("red" if red_adv > blue_adv else "equal")

        return {
            "matchups_by_role": matchups,
            "overall_advantage": overall,
            "blue_lanes_won": blue_adv,
            "red_lanes_won": red_adv,
        }

    def _get_players_by_role(self, team_id: int) -> dict:
        """Retornar dicionário de jogadores do time indexado por função."""
        players = self.db.query(Player).filter(Player.team_id == team_id).all()
        return {p.role: p for p in players if p.role}

    def _compare_players(self, blue: Player, red: Player) -> str:
        """
        Comparar dois jogadores da mesma posição.

        Usa KDA e kill participation como métricas principais.
        """
        blue_score = 0.0
        red_score = 0.0

        # KDA
        if blue.kda is not None and red.kda is not None:
            if blue.kda > red.kda * 1.1:  # 10% de margem
                blue_score += 1
            elif red.kda > blue.kda * 1.1:
                red_score += 1

        # Kill participation
        if blue.kill_participation is not None and red.kill_participation is not None:
            if blue.kill_participation > red.kill_participation + 0.05:
                blue_score += 1
            elif red.kill_participation > blue.kill_participation + 0.05:
                red_score += 1

        if blue_score > red_score:
            return "blue"
        elif red_score > blue_score:
            return "red"
        return "equal"
