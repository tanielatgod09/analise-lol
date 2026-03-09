"""
Modelo de Probabilidade Dinâmica para Live Betting.

Atualiza probabilidades em tempo real durante a partida usando:
- Diferença de gold
- Kills, dragões, barões, torres
- Controle de visão
- Tempo de jogo

Detecta oportunidades de aposta ao vivo quando probabilidade real
excede a probabilidade implícita das odds disponíveis.
"""
import numpy as np
from typing import Optional
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Pesos para cada fator no modelo de probabilidade live
FACTOR_WEIGHTS = {
    "gold_diff": 0.35,
    "kills_diff": 0.20,
    "dragons_diff": 0.15,
    "barons_diff": 0.15,
    "towers_diff": 0.10,
    "time_factor": 0.05,
}


class LiveBettingService:
    """
    Serviço de apostas ao vivo — atualiza probabilidades em tempo real.
    """

    def update_probabilities(
        self,
        match,
        game_state: dict,
    ) -> dict:
        """
        Recalcular probabilidades com base no estado atual da partida.

        Args:
            match: Objeto Match do banco de dados
            game_state: Estado atual do jogo com as seguintes chaves:
                - gold_diff: diferença de gold (blue - red)
                - kills_blue, kills_red: kills de cada time
                - dragons_blue, dragons_red: dragões de cada time
                - barons_blue, barons_red: barões de cada time
                - towers_blue, towers_red: torres destruídas
                - game_time_seconds: tempo de jogo
                - vision_score_blue, vision_score_red: controle de visão

        Returns:
            Dict com probabilidades atualizadas e oportunidades identificadas
        """
        # Extrair valores do estado do jogo
        gold_diff = game_state.get("gold_diff", 0)
        kills_blue = game_state.get("kills_blue", 0)
        kills_red = game_state.get("kills_red", 0)
        dragons_blue = game_state.get("dragons_blue", 0)
        dragons_red = game_state.get("dragons_red", 0)
        barons_blue = game_state.get("barons_blue", 0)
        barons_red = game_state.get("barons_red", 0)
        towers_blue = game_state.get("towers_blue", 0)
        towers_red = game_state.get("towers_red", 0)
        game_time = game_state.get("game_time_seconds", 600)
        vision_blue = game_state.get("vision_score_blue", 0)
        vision_red = game_state.get("vision_score_red", 0)

        # Normalizar cada fator para [-1, 1] (positivo = vantagem azul)
        gold_factor = self._normalize_gold(gold_diff)
        kills_factor = self._normalize_diff(kills_blue - kills_red, max_val=15)
        dragons_factor = self._normalize_diff(dragons_blue - dragons_red, max_val=4)
        barons_factor = self._normalize_diff(barons_blue - barons_red, max_val=2) * 1.5
        towers_factor = self._normalize_diff(towers_blue - towers_red, max_val=10)

        # Peso do tempo: mais tarde no jogo, objetivos pesam mais
        time_minutes = game_time / 60
        time_weight = min(1.5, 1.0 + time_minutes / 40)

        # Score ponderado
        score = (
            gold_factor * FACTOR_WEIGHTS["gold_diff"]
            + kills_factor * FACTOR_WEIGHTS["kills_diff"]
            + dragons_factor * FACTOR_WEIGHTS["dragons_diff"] * time_weight
            + barons_factor * FACTOR_WEIGHTS["barons_diff"] * time_weight
            + towers_factor * FACTOR_WEIGHTS["towers_diff"]
        )

        # Converter score [-1, 1] para probabilidade [0.05, 0.95]
        # usando função sigmoide
        blue_prob = self._sigmoid(score * 3)
        blue_prob = float(np.clip(blue_prob, 0.05, 0.95))
        red_prob = 1.0 - blue_prob

        # Detectar oportunidades de live betting
        opportunities = self._detect_opportunities(
            match, blue_prob, red_prob, game_state
        )

        return {
            "match_id": match.id if match else None,
            "game_time_seconds": game_time,
            "game_time_minutes": round(time_minutes, 1),
            "blue_win_probability": round(blue_prob, 4),
            "red_win_probability": round(red_prob, 4),
            "state_summary": {
                "gold_diff": gold_diff,
                "kills_blue": kills_blue,
                "kills_red": kills_red,
                "dragons_blue": dragons_blue,
                "dragons_red": dragons_red,
                "barons_blue": barons_blue,
                "barons_red": barons_red,
                "towers_blue": towers_blue,
                "towers_red": towers_red,
            },
            "factor_scores": {
                "gold_factor": round(gold_factor, 3),
                "kills_factor": round(kills_factor, 3),
                "dragons_factor": round(dragons_factor, 3),
                "barons_factor": round(barons_factor, 3),
                "towers_factor": round(towers_factor, 3),
            },
            "live_opportunities": opportunities,
        }

    def _normalize_gold(self, gold_diff: float) -> float:
        """Normalizar diferença de gold para [-1, 1]. Max relevante: 10.000 gold."""
        return float(np.clip(gold_diff / 10000, -1, 1))

    def _normalize_diff(self, diff: float, max_val: float) -> float:
        """Normalizar uma diferença para [-1, 1]."""
        if max_val == 0:
            return 0.0
        return float(np.clip(diff / max_val, -1, 1))

    def _sigmoid(self, x: float) -> float:
        """Função sigmoide para converter score em probabilidade."""
        return float(1 / (1 + np.exp(-x)))

    def _detect_opportunities(
        self,
        match,
        blue_prob: float,
        red_prob: float,
        game_state: dict,
    ) -> list[dict]:
        """
        Detectar oportunidades de aposta ao vivo quando a probabilidade real
        excede a probabilidade implícita das odds disponíveis.
        """
        opportunities = []

        if not match or not hasattr(match, 'odds_list'):
            return opportunities

        for odd_entry in (match.odds_list or []):
            if not odd_entry.is_live:
                continue

            implied_prob = 1 / odd_entry.odd_value if odd_entry.odd_value > 0 else 0

            # Determinar a probabilidade real para esta seleção
            if "blue" in odd_entry.selection.lower() or (
                match.team_blue and match.team_blue.name in odd_entry.selection
            ):
                real_prob = blue_prob
            elif "red" in odd_entry.selection.lower() or (
                match.team_red and match.team_red.name in odd_entry.selection
            ):
                real_prob = red_prob
            else:
                continue

            ev = (real_prob * odd_entry.odd_value) - 1

            if real_prob > implied_prob and ev > 0:
                opportunities.append({
                    "type": "OPORTUNIDADE DE APOSTA AO VIVO",
                    "bookmaker": odd_entry.bookmaker,
                    "market": odd_entry.market,
                    "selection": odd_entry.selection,
                    "odd": odd_entry.odd_value,
                    "real_probability": round(real_prob, 4),
                    "implied_probability": round(implied_prob, 4),
                    "edge": round(real_prob - implied_prob, 4),
                    "ev": round(ev, 4),
                })

        return opportunities
