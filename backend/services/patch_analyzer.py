"""
Analisador de Patch e Meta atual.

Analisa quais campeões são mais fortes, mais banidos e têm maior
winrate no patch atual para contexto das previsões.
"""
from sqlalchemy.orm import Session
from backend.models.champion import Champion
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PatchAnalyzer:
    """Analisa o meta do patch atual de League of Legends."""

    def __init__(self, db: Session):
        self.db = db

    def get_current_meta(self, patch: str) -> dict:
        """
        Retornar análise completa do meta do patch informado.

        Args:
            patch: Versão do patch (ex: "14.9")
        """
        champions = (
            self.db.query(Champion)
            .filter(Champion.patch == patch)
            .all()
        )

        if not champions:
            logger.warning(f"Sem dados para o patch {patch}")
            return {"patch": patch, "champions": [], "meta_summary": "Sem dados disponíveis"}

        # Top campeões por winrate
        top_winrate = sorted(
            [c for c in champions if c.winrate],
            key=lambda c: c.winrate,
            reverse=True,
        )[:10]

        # Top campeões por banrate
        top_banrate = sorted(
            [c for c in champions if c.banrate],
            key=lambda c: c.banrate,
            reverse=True,
        )[:10]

        # Top campeões por pickrate
        top_pickrate = sorted(
            [c for c in champions if c.pickrate],
            key=lambda c: c.pickrate,
            reverse=True,
        )[:10]

        return {
            "patch": patch,
            "total_champions": len(champions),
            "top_winrate": [
                {"name": c.name, "winrate": c.winrate, "role": c.roles}
                for c in top_winrate
            ],
            "top_banrate": [
                {"name": c.name, "banrate": c.banrate, "role": c.roles}
                for c in top_banrate
            ],
            "top_pickrate": [
                {"name": c.name, "pickrate": c.pickrate, "role": c.roles}
                for c in top_pickrate
            ],
        }

    def get_champion_patch_performance(
        self, champion_name: str, patch: str
    ) -> dict:
        """Retornar performance de um campeão no patch especificado."""
        champion = (
            self.db.query(Champion)
            .filter(
                Champion.name == champion_name,
                Champion.patch == patch,
            )
            .first()
        )

        if not champion:
            return {"champion": champion_name, "patch": patch, "available": False}

        return {
            "champion": champion.name,
            "patch": patch,
            "available": True,
            "winrate": champion.winrate,
            "pickrate": champion.pickrate,
            "banrate": champion.banrate,
            "game_style": champion.game_style,
        }

    def is_meta_champion(self, champion_name: str, patch: str) -> bool:
        """Verificar se o campeão está em alta no meta do patch."""
        perf = self.get_champion_patch_performance(champion_name, patch)
        if not perf.get("available"):
            return False
        winrate = perf.get("winrate") or 0
        banrate = perf.get("banrate") or 0
        # Consideramos meta se winrate > 52% ou banrate > 20%
        return winrate > 0.52 or banrate > 0.20
