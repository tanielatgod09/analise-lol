"""
Tarefa de Atualização Automática de Dados.

Coleta dados da PandaScore API e sincroniza com o banco de dados.
"""
from datetime import datetime
from sqlalchemy.orm import Session

from backend.services.data_collector import DataCollector
from backend.services.stats_calculator import StatsCalculator
from backend.services.playstyle_analyzer import PlaystyleAnalyzer
from backend.models.team import Team
from backend.models.match import Match
from backend.utils.logger import get_logger

logger = get_logger(__name__)

LEAGUES_TO_UPDATE = ["LCK", "LEC", "LCS", "CBLOL", "LPL"]


class DataUpdateTask:
    """Tarefa de atualização automática de dados de partidas e times."""

    def __init__(self, db: Session):
        self.db = db
        self.collector = DataCollector()
        self.stats_calc = StatsCalculator(db)
        self.playstyle = PlaystyleAnalyzer(db)

    def run(self) -> None:
        """Executar ciclo completo de atualização de dados."""
        logger.info("Iniciando atualização de dados...")

        for league in LEAGUES_TO_UPDATE:
            try:
                self._update_league(league)
            except Exception as e:
                logger.error(f"Erro ao atualizar liga {league}: {e}")

        # Atualizar estatísticas de todos os times
        self._update_all_team_stats()

        logger.info("Atualização de dados concluída")

    def _update_league(self, league: str) -> None:
        """Atualizar partidas de uma liga específica."""
        matches_data = self.collector.get_upcoming_matches(league=league)
        created = 0
        updated = 0

        for match_data in matches_data:
            external_id = str(match_data.get("id"))
            existing = self.db.query(Match).filter(
                Match.external_id == external_id
            ).first()

            if not existing:
                # Criar nova partida
                match = self._create_match_from_data(match_data, league)
                if match:
                    self.db.add(match)
                    created += 1
            else:
                # Atualizar status
                new_status = self._map_status(match_data.get("status"))
                if existing.status != new_status:
                    existing.status = new_status
                    existing.updated_at = datetime.utcnow()
                    updated += 1

        self.db.commit()
        logger.info(f"Liga {league}: {created} novas, {updated} atualizadas")

    def _create_match_from_data(self, data: dict, league: str) -> Match | None:
        """Criar objeto Match a partir dos dados da PandaScore."""
        try:
            opponents = data.get("opponents", [])
            if len(opponents) < 2:
                return None

            blue_team = self._get_or_create_team(opponents[0].get("opponent", {}), league)
            red_team = self._get_or_create_team(opponents[1].get("opponent", {}), league)

            if not blue_team or not red_team:
                return None

            scheduled_str = data.get("scheduled_at")
            scheduled_at = None
            if scheduled_str:
                try:
                    scheduled_at = datetime.fromisoformat(scheduled_str.replace("Z", "+00:00"))
                    scheduled_at = scheduled_at.replace(tzinfo=None)
                except ValueError:
                    pass

            return Match(
                external_id=str(data.get("id")),
                league=league,
                tournament=data.get("tournament", {}).get("name"),
                team_blue_id=blue_team.id,
                team_red_id=red_team.id,
                status=self._map_status(data.get("status")),
                scheduled_at=scheduled_at,
                series_type=self._detect_series_type(data),
            )
        except Exception as e:
            logger.warning(f"Erro ao criar Match: {e}")
            return None

    def _get_or_create_team(self, team_data: dict, league: str) -> Team | None:
        """Buscar ou criar um time no banco de dados."""
        if not team_data:
            return None

        external_id = str(team_data.get("id", ""))
        if not external_id:
            return None

        existing = self.db.query(Team).filter(Team.external_id == external_id).first()
        if existing:
            return existing

        team = Team(
            external_id=external_id,
            name=team_data.get("name", "Desconhecido"),
            acronym=team_data.get("acronym"),
            league=league,
            logo_url=team_data.get("image_url"),
        )
        self.db.add(team)
        self.db.flush()
        return team

    def _map_status(self, pandascore_status: str) -> str:
        """Mapear status da PandaScore para o formato interno."""
        mapping = {
            "not_started": "scheduled",
            "running": "running",
            "finished": "finished",
            "cancelled": "cancelled",
            "postponed": "scheduled",
        }
        return mapping.get(pandascore_status or "", "scheduled")

    def _detect_series_type(self, data: dict) -> str:
        """Detectar tipo de série (BO1, BO3, BO5)."""
        series = data.get("serie", {})
        if series:
            name = (series.get("name") or "").upper()
            if "BO5" in name or "BEST OF 5" in name:
                return "BO5"
            elif "BO3" in name or "BEST OF 3" in name:
                return "BO3"
        return "BO1"

    def _update_all_team_stats(self) -> None:
        """Atualizar estatísticas de todos os times com dados históricos."""
        teams = self.db.query(Team).all()
        for team in teams:
            try:
                self.stats_calc.save_team_stats(team.id)
                self.playstyle.update_team_classification(team.id)
            except Exception as e:
                logger.warning(f"Erro ao atualizar stats do time {team.name}: {e}")
