"""
Tarefa de Atualização Automática de Odds.

Coleta odds de casas de apostas via TheOddsAPI e
sincroniza com o banco de dados.
"""
from datetime import datetime
from sqlalchemy.orm import Session

from backend.services.odds_collector import OddsCollector
from backend.models.match import Match
from backend.models.odds import Odds
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class OddsUpdateTask:
    """Tarefa de atualização automática de odds."""

    def __init__(self, db: Session):
        self.db = db
        self.collector = OddsCollector()

    def run(self) -> None:
        """Executar ciclo de atualização de odds."""
        logger.info("Iniciando atualização de odds...")

        raw_odds = self.collector.get_lol_odds()
        if not raw_odds:
            logger.warning("Nenhuma odd retornada pela API")
            return

        parsed_odds = self.collector.parse_odds(raw_odds)
        saved_count = 0

        for odd_data in parsed_odds:
            try:
                # Encontrar a partida pelo identificador externo
                match_external_id = odd_data.get("match_external_id")
                match = self.db.query(Match).filter(
                    Match.external_id == match_external_id
                ).first()

                if not match:
                    # Tentar encontrar pelo nome dos times
                    match = self._find_match_by_teams(
                        odd_data.get("home_team", ""),
                        odd_data.get("away_team", ""),
                    )

                if not match:
                    continue

                # Salvar odd
                odd = Odds(
                    match_id=match.id,
                    bookmaker=odd_data["bookmaker_title"] or odd_data["bookmaker"],
                    market=odd_data["market"],
                    selection=odd_data["selection"],
                    odd_value=odd_data["odd_value"],
                    implied_probability=odd_data["implied_probability"],
                    is_live=False,
                    collected_at=datetime.utcnow(),
                )
                self.db.add(odd)
                saved_count += 1

            except Exception as e:
                logger.warning(f"Erro ao processar odd: {e}")
                continue

        self.db.commit()
        logger.info(f"Odds atualizadas: {saved_count} registros salvos")

    def _find_match_by_teams(self, team1_name: str, team2_name: str) -> Match | None:
        """Tentar encontrar uma partida pelo nome dos times."""
        if not team1_name or not team2_name:
            return None

        from backend.models.team import Team
        from sqlalchemy import or_, and_

        # Buscar times pelos nomes
        t1 = self.db.query(Team).filter(
            or_(
                Team.name.ilike(f"%{team1_name}%"),
                Team.acronym.ilike(f"%{team1_name}%"),
            )
        ).first()

        t2 = self.db.query(Team).filter(
            or_(
                Team.name.ilike(f"%{team2_name}%"),
                Team.acronym.ilike(f"%{team2_name}%"),
            )
        ).first()

        if not t1 or not t2:
            return None

        return self.db.query(Match).filter(
            or_(
                and_(Match.team_blue_id == t1.id, Match.team_red_id == t2.id),
                and_(Match.team_blue_id == t2.id, Match.team_red_id == t1.id),
            ),
            Match.status == "scheduled",
        ).first()
