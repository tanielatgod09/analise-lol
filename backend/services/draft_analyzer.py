"""
Analisador de Draft — analisa os picks e bans de uma partida.

Considera:
1. Campeões escolhidos por cada time
2. Counters e matchups
3. Sinergia interna da composição
4. Winrate dos campeões no patch atual
5. Histórico do jogador com cada campeão
"""
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.champion import Champion
from backend.models.player import Player
from backend.services.patch_analyzer import PatchAnalyzer
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Definição simplificada de composições
COMPOSITION_STYLES = {
    "teamfight": {"engage", "aoe", "frontline"},
    "poke": {"poke", "range", "siege"},
    "split_push": {"split", "dueling", "sidelane"},
    "wombo_combo": {"cc", "aoe", "engage"},
    "scaling": {"hypercarry", "scaling", "late_game"},
}

# Counters básicos (simplificado — em produção viria de banco de dados)
HARD_COUNTERS: dict[str, list[str]] = {
    "Yasuo": ["Malzahar", "Pantheon"],
    "Zed": ["Lissandra", "Kayle"],
    "Vayne": ["Caitlyn", "Draven"],
}


class DraftAnalyzer:
    """Analisa o draft de uma partida de League of Legends."""

    def __init__(self, db: Session):
        self.db = db
        self.patch_analyzer = PatchAnalyzer(db)

    def analyze_draft(
        self,
        blue_picks: list[str],
        red_picks: list[str],
        blue_bans: list[str],
        red_bans: list[str],
        patch: str,
        blue_players: Optional[list[dict]] = None,
        red_players: Optional[list[dict]] = None,
    ) -> dict:
        """
        Análise completa do draft.

        Args:
            blue_picks: Campeões escolhidos pelo time azul
            red_picks: Campeões escolhidos pelo time vermelho
            blue_bans: Banimentos do time azul
            red_bans: Banimentos do time vermelho
            patch: Patch atual
            blue_players: Dados dos jogadores do time azul (com histórico por campeão)
            red_players: Dados dos jogadores do time vermelho
        """
        blue_style = self._detect_composition_style(blue_picks)
        red_style = self._detect_composition_style(red_picks)

        blue_synergy = self._calculate_synergy_score(blue_picks)
        red_synergy = self._calculate_synergy_score(red_picks)

        blue_meta_score = self._calculate_meta_score(blue_picks, patch)
        red_meta_score = self._calculate_meta_score(red_picks, patch)

        counter_advantage = self._analyze_counters(blue_picks, red_picks)

        player_comfort_blue = self._calculate_player_comfort(
            blue_picks, blue_players or []
        )
        player_comfort_red = self._calculate_player_comfort(
            red_picks, red_players or []
        )

        # Score geral do draft (0 = vantagem vermelha, 1 = vantagem azul)
        draft_advantage_score = self._calculate_draft_advantage(
            blue_meta_score, red_meta_score,
            blue_synergy, red_synergy,
            counter_advantage,
            player_comfort_blue, player_comfort_red,
        )

        return {
            "patch": patch,
            "blue_team": {
                "picks": blue_picks,
                "bans": blue_bans,
                "composition_style": blue_style,
                "synergy_score": round(blue_synergy, 3),
                "meta_score": round(blue_meta_score, 3),
                "player_comfort_score": round(player_comfort_blue, 3),
            },
            "red_team": {
                "picks": red_picks,
                "bans": red_bans,
                "composition_style": red_style,
                "synergy_score": round(red_synergy, 3),
                "meta_score": round(red_meta_score, 3),
                "player_comfort_score": round(player_comfort_red, 3),
            },
            "counter_advantage": counter_advantage,
            "draft_advantage_score": round(draft_advantage_score, 3),
            "draft_advantage_team": "blue" if draft_advantage_score > 0.52 else (
                "red" if draft_advantage_score < 0.48 else "equal"
            ),
        }

    def _detect_composition_style(self, picks: list[str]) -> str:
        """Detectar estilo predominante da composição."""
        # Implementação simplificada
        # Em produção, consulta banco de dados de campeões com seus estilos
        champion_styles: dict[str, str] = {}
        for pick in picks:
            champ = self.db.query(Champion).filter(
                Champion.name == pick
            ).first()
            if champ and champ.game_style:
                champion_styles[pick] = champ.game_style

        if not champion_styles:
            return "balanced"

        # Detectar estilo majoritário
        style_counts: dict = {}
        for style in champion_styles.values():
            style_counts[style] = style_counts.get(style, 0) + 1

        return max(style_counts, key=style_counts.get) if style_counts else "balanced"

    def _calculate_synergy_score(self, picks: list[str]) -> float:
        """
        Calcular score de sinergia da composição (0.0 a 1.0).

        Composições com boa sinergia (engage + frontline + damage) pontuam mais alto.
        """
        if not picks:
            return 0.5

        # Verificar se tem balanceamento de roles básico
        # (frontline, damage, cc, healing)
        # Simplificado: retorna score baseado em diversidade de estilos
        champion_styles: list[str] = []
        for pick in picks:
            champ = self.db.query(Champion).filter(Champion.name == pick).first()
            if champ and champ.game_style:
                champion_styles.append(champ.game_style)

        if not champion_styles:
            return 0.5

        unique_styles = len(set(champion_styles))
        # Mais diversidade de estilos = melhor sinergia (até certo ponto)
        synergy = min(1.0, 0.3 + (unique_styles / len(picks)) * 0.7)
        return synergy

    def _calculate_meta_score(self, picks: list[str], patch: str) -> float:
        """
        Calcular score do draft em relação ao meta do patch (0.0 a 1.0).
        """
        if not picks:
            return 0.5

        meta_scores = []
        for pick in picks:
            perf = self.patch_analyzer.get_champion_patch_performance(pick, patch)
            if perf.get("available") and perf.get("winrate"):
                meta_scores.append(perf["winrate"])
            else:
                meta_scores.append(0.5)  # Assumir 50% se sem dados

        return sum(meta_scores) / len(meta_scores) if meta_scores else 0.5

    def _analyze_counters(
        self, blue_picks: list[str], red_picks: list[str]
    ) -> dict:
        """Analisar vantagem de counters entre os dois drafts."""
        blue_counter_score = 0
        red_counter_score = 0

        for blue_champ in blue_picks:
            counters = HARD_COUNTERS.get(blue_champ, [])
            for red_champ in red_picks:
                if red_champ in counters:
                    red_counter_score += 1

        for red_champ in red_picks:
            counters = HARD_COUNTERS.get(red_champ, [])
            for blue_champ in blue_picks:
                if blue_champ in counters:
                    blue_counter_score += 1

        total = blue_counter_score + red_counter_score
        if total == 0:
            advantage = "equal"
            score = 0.5
        elif blue_counter_score > red_counter_score:
            advantage = "blue"
            score = blue_counter_score / total
        else:
            advantage = "red"
            score = red_counter_score / total

        return {
            "advantage": advantage,
            "blue_counter_score": blue_counter_score,
            "red_counter_score": red_counter_score,
            "confidence": round(score, 3),
        }

    def _calculate_player_comfort(
        self,
        picks: list[str],
        players: list[dict],
    ) -> float:
        """
        Calcular quão confortáveis os jogadores são com os campeões escolhidos.
        Baseia-se no histórico do jogador com cada campeão.
        """
        if not players or not picks:
            return 0.5

        comfort_scores = []
        for i, pick in enumerate(picks):
            if i < len(players):
                player_data = players[i]
                champion_pool = player_data.get("champion_pool", [])
                # Verificar se o campeão escolhido está no pool do jogador
                for champ_info in champion_pool:
                    if champ_info.get("champion") == pick:
                        games = champ_info.get("games", 0)
                        winrate = champ_info.get("winrate", 0.5)
                        # Mais jogos e maior winrate = mais conforto
                        comfort = min(1.0, (games / 20) * 0.5 + winrate * 0.5)
                        comfort_scores.append(comfort)
                        break
                else:
                    comfort_scores.append(0.4)  # Campeão fora do pool habitual
            else:
                comfort_scores.append(0.5)

        return sum(comfort_scores) / len(comfort_scores) if comfort_scores else 0.5

    def _calculate_draft_advantage(
        self,
        blue_meta: float,
        red_meta: float,
        blue_synergy: float,
        red_synergy: float,
        counter_adv: dict,
        blue_comfort: float,
        red_comfort: float,
    ) -> float:
        """
        Calcular score geral de vantagem de draft para o time azul.
        Retorna valor entre 0 e 1 (>0.5 = vantagem azul).
        """
        # Diferença normalizada por componente
        meta_diff = (blue_meta - red_meta) * 0.35
        synergy_diff = (blue_synergy - red_synergy) * 0.25
        comfort_diff = (blue_comfort - red_comfort) * 0.20

        # Counter advantage
        counter_score = counter_adv.get("blue_counter_score", 0)
        red_counter = counter_adv.get("red_counter_score", 0)
        total_counters = counter_score + red_counter
        counter_diff = (
            (counter_score - red_counter) / total_counters * 0.20
            if total_counters > 0 else 0
        )

        # Score final centrado em 0.5
        score = 0.5 + meta_diff + synergy_diff + comfort_diff + counter_diff
        return max(0.05, min(0.95, score))
