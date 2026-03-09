"""
Simulação Monte Carlo para partidas de League of Legends.

Executa no mínimo 10.000 simulações por partida para gerar
distribuições de probabilidade robustas.
"""
import numpy as np
from typing import Optional
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MonteCarloSimulator:
    """
    Executa simulações Monte Carlo para estimar probabilidades de eventos
    em partidas de League of Legends.
    """

    def __init__(self, n_simulations: int = None):
        self.n_simulations = n_simulations or settings.monte_carlo_simulations
        logger.info(f"Monte Carlo inicializado com {self.n_simulations} simulações")

    def simulate_match(
        self,
        blue_win_prob: float,
        blue_kills_avg: float,
        red_kills_avg: float,
        blue_kills_std: float = 5.0,
        red_kills_std: float = 5.0,
        duration_avg: float = 1900.0,  # segundos
        duration_std: float = 300.0,
        seed: Optional[int] = None,
    ) -> dict:
        """
        Simular uma partida de LoL usando Monte Carlo.

        Args:
            blue_win_prob: Probabilidade de vitória do time azul [0, 1]
            blue_kills_avg: Média de kills do time azul por jogo
            red_kills_avg: Média de kills do time vermelho por jogo
            blue_kills_std: Desvio padrão de kills do azul
            red_kills_std: Desvio padrão de kills do vermelho
            duration_avg: Duração média em segundos
            duration_std: Desvio padrão da duração
            seed: Semente para reprodutibilidade

        Returns:
            Dicionário com resultados das simulações
        """
        rng = np.random.default_rng(seed)
        n = self.n_simulations

        # --- Simulação de vitória ---
        outcomes = rng.uniform(0, 1, n)
        blue_wins = outcomes < blue_win_prob
        blue_win_rate_mc = float(np.mean(blue_wins))

        # --- Simulação de kills ---
        blue_kills_sim = np.maximum(0, rng.normal(blue_kills_avg, blue_kills_std, n))
        red_kills_sim = np.maximum(0, rng.normal(red_kills_avg, red_kills_std, n))
        total_kills_sim = blue_kills_sim + red_kills_sim

        # --- Simulação de duração ---
        durations_sim = np.maximum(900, rng.normal(duration_avg, duration_std, n))

        # --- Calcular distribuições ---
        kills_percentiles = np.percentile(total_kills_sim, [10, 25, 50, 75, 90])

        # Probabilidades over/under para limiares comuns
        kill_thresholds = [15.5, 20.5, 22.5, 25.5, 27.5, 30.5, 35.5]
        over_probs = {
            f"over_{t}": float(np.mean(total_kills_sim > t))
            for t in kill_thresholds
        }

        # Duração
        duration_thresholds_min = [25, 28, 30, 32, 35]
        duration_probs = {
            f"over_{t}min": float(np.mean(durations_sim > t * 60))
            for t in duration_thresholds_min
        }

        return {
            "n_simulations": n,
            "blue_win_probability": round(blue_win_rate_mc, 4),
            "red_win_probability": round(1 - blue_win_rate_mc, 4),
            "kills": {
                "blue_avg": round(float(np.mean(blue_kills_sim)), 2),
                "red_avg": round(float(np.mean(red_kills_sim)), 2),
                "total_avg": round(float(np.mean(total_kills_sim)), 2),
                "total_std": round(float(np.std(total_kills_sim)), 2),
                "p10": round(float(kills_percentiles[0]), 1),
                "p25": round(float(kills_percentiles[1]), 1),
                "p50": round(float(kills_percentiles[2]), 1),
                "p75": round(float(kills_percentiles[3]), 1),
                "p90": round(float(kills_percentiles[4]), 1),
                **over_probs,
            },
            "duration": {
                "avg_seconds": round(float(np.mean(durations_sim)), 0),
                "avg_minutes": round(float(np.mean(durations_sim)) / 60, 1),
                "std_seconds": round(float(np.std(durations_sim)), 0),
                **duration_probs,
            },
        }

    def simulate_series(
        self,
        blue_win_prob: float,
        series_type: str = "BO3",
        seed: Optional[int] = None,
    ) -> dict:
        """
        Simular uma série BO3 ou BO5.

        Args:
            blue_win_prob: Probabilidade do azul vencer um único jogo
            series_type: "BO1", "BO3", ou "BO5"
            seed: Semente para reprodutibilidade

        Returns:
            Probabilidades de cada resultado possível da série
        """
        rng = np.random.default_rng(seed)
        n = self.n_simulations

        if series_type == "BO1":
            blue_series_wins = np.sum(rng.uniform(0, 1, n) < blue_win_prob)
            return {
                "series_type": "BO1",
                "blue_series_win_probability": round(blue_win_prob, 4),
                "red_series_win_probability": round(1 - blue_win_prob, 4),
            }

        games_needed = 2 if series_type == "BO3" else 3
        max_games = 3 if series_type == "BO3" else 5

        blue_series_wins = 0
        score_counts: dict = {}

        for _ in range(n):
            blue_score = 0
            red_score = 0
            game_count = 0

            while blue_score < games_needed and red_score < games_needed:
                game_count += 1
                if rng.uniform() < blue_win_prob:
                    blue_score += 1
                else:
                    red_score += 1

            score_key = f"{blue_score}-{red_score}"
            score_counts[score_key] = score_counts.get(score_key, 0) + 1
            if blue_score == games_needed:
                blue_series_wins += 1

        return {
            "series_type": series_type,
            "blue_series_win_probability": round(blue_series_wins / n, 4),
            "red_series_win_probability": round(1 - blue_series_wins / n, 4),
            "score_distribution": {
                k: round(v / n, 4) for k, v in sorted(score_counts.items())
            },
        }

    def calculate_poisson_kills(
        self,
        lambda_blue: float,
        lambda_red: float,
        n_simulations: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> dict:
        """
        Simular distribuição de kills usando Poisson adaptada para LoL.

        A distribuição de Poisson é mais adequada para contagem de eventos
        (kills) do que a normal quando os valores são baixos.

        Args:
            lambda_blue: Taxa média de kills do time azul (kills/jogo)
            lambda_red: Taxa média de kills do time vermelho (kills/jogo)
        """
        rng = np.random.default_rng(seed)
        n = n_simulations or self.n_simulations

        blue_kills = rng.poisson(lambda_blue, n)
        red_kills = rng.poisson(lambda_red, n)
        total = blue_kills + red_kills

        thresholds = [15.5, 20.5, 22.5, 25.5, 27.5, 30.5, 35.5]
        return {
            "lambda_blue": lambda_blue,
            "lambda_red": lambda_red,
            "expected_total": lambda_blue + lambda_red,
            "simulated_avg": round(float(np.mean(total)), 2),
            "simulated_std": round(float(np.std(total)), 2),
            "over_probabilities": {
                f"over_{t}": round(float(np.mean(total > t)), 4)
                for t in thresholds
            },
            "under_probabilities": {
                f"under_{t}": round(float(np.mean(total <= t)), 4)
                for t in thresholds
            },
        }
