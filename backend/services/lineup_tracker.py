"""
Serviço de rastreamento de line-ups atuais dos times.

REGRA CRÍTICA: Apenas estatísticas com a line-up atual são utilizadas.
A data de início da line-up é rastreada e utilizada para filtrar
os dados históricos de cada time.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.team import Team
from backend.models.player import Player
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class LineupTracker:
    """
    Rastreia a composição atual de cada time e garante que apenas
    estatísticas da line-up atual sejam utilizadas nas análises.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_current_lineup(self, team_id: int) -> list[Player]:
        """Retornar jogadores da line-up atual de um time."""
        return self.db.query(Player).filter(Player.team_id == team_id).all()

    def get_lineup_start_date(self, team_id: int) -> Optional[datetime]:
        """
        Retornar a data em que a line-up atual começou a jogar junta.

        Esta data é usada para filtrar estatísticas históricas — apenas
        partidas após esta data são consideradas nas análises.
        """
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if team and team.current_lineup_since:
            return team.current_lineup_since
        return None

    def update_lineup(
        self,
        team_id: int,
        players_data: list[dict],
        lineup_start_date: datetime,
    ) -> None:
        """
        Atualizar a line-up de um time.

        Args:
            team_id: ID do time
            players_data: Lista de dicionários com dados dos jogadores
            lineup_start_date: Data em que esta formação começou
        """
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            logger.error(f"Time {team_id} não encontrado")
            return

        old_lineup_date = team.current_lineup_since

        # Atualizar data de início da line-up
        team.current_lineup_since = lineup_start_date
        team.updated_at = datetime.utcnow()

        # Remover jogadores antigos do time
        self.db.query(Player).filter(Player.team_id == team_id).update({"team_id": None})

        # Adicionar/atualizar jogadores da nova line-up
        for p_data in players_data:
            external_id = p_data.get("external_id")
            player = None
            if external_id:
                player = self.db.query(Player).filter(
                    Player.external_id == external_id
                ).first()

            if not player:
                player = Player(
                    external_id=external_id,
                    name=p_data.get("name", "Desconhecido"),
                )
                self.db.add(player)

            player.team_id = team_id
            player.role = p_data.get("role")
            player.real_name = p_data.get("real_name")
            player.nationality = p_data.get("nationality")

        self.db.commit()

        if old_lineup_date != lineup_start_date:
            logger.info(
                f"Line-up do time {team.name} atualizada. "
                f"Nova data de início: {lineup_start_date.date()}"
            )

    def detect_lineup_change(
        self,
        team_id: int,
        current_players: list[str],
    ) -> bool:
        """
        Detectar se houve mudança na line-up comparando com os jogadores atuais.

        Args:
            team_id: ID do time
            current_players: Lista de external_ids dos jogadores atuais

        Returns:
            True se houve mudança na line-up, False caso contrário
        """
        stored_players = self.get_current_lineup(team_id)
        stored_ids = {p.external_id for p in stored_players if p.external_id}
        current_ids = set(current_players)
        return stored_ids != current_ids

    def get_games_with_current_lineup(
        self, team_id: int
    ) -> list:
        """
        Retornar apenas partidas disputadas com a line-up atual do time.
        Filtra pelo campo current_lineup_since.
        """
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team or not team.current_lineup_since:
            return []

        from backend.models.match import Match
        from sqlalchemy import or_

        return (
            self.db.query(Match)
            .filter(
                or_(Match.team_blue_id == team_id, Match.team_red_id == team_id),
                Match.scheduled_at >= team.current_lineup_since,
                Match.status == "finished",
            )
            .order_by(Match.scheduled_at.desc())
            .all()
        )
