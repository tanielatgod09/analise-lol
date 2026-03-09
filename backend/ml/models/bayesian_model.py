"""
Modelo Bayesiano para atualização de probabilidades.

Implementa inferência bayesiana para atualizar crenças sobre
a probabilidade de vitória de cada time com base em evidências.
"""
import numpy as np
from typing import Optional
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class BayesianModel:
    """
    Modelo bayesiano para atualização de probabilidades de vitória.

    Usa distribuição Beta como prior para probabilidade binomial (vitória/derrota).
    Beta(α, β) onde α = vitórias + 1, β = derrotas + 1 (prior de Jeffreys)
    """

    def calculate_win_probability(
        self,
        wins: int,
        losses: int,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0,
    ) -> dict:
        """
        Calcular probabilidade bayesiana de vitória.

        Args:
            wins: Número de vitórias com a line-up atual
            losses: Número de derrotas com a line-up atual
            prior_alpha: Parâmetro alpha do prior Beta (padrão: prior uniforme)
            prior_beta: Parâmetro beta do prior Beta (padrão: prior uniforme)

        Returns:
            Dict com probabilidade média e intervalo de credibilidade 95%
        """
        from scipy.stats import beta as beta_dist

        # Posterior: Beta(α + wins, β + losses)
        alpha_post = prior_alpha + wins
        beta_post = prior_beta + losses

        mean_prob = alpha_post / (alpha_post + beta_post)
        ci_low, ci_high = beta_dist.interval(0.95, alpha_post, beta_post)

        return {
            "mean_probability": round(mean_prob, 4),
            "ci_95_low": round(ci_low, 4),
            "ci_95_high": round(ci_high, 4),
            "alpha_posterior": alpha_post,
            "beta_posterior": beta_post,
            "n_games": wins + losses,
        }

    def update_with_evidence(
        self,
        prior_prob: float,
        evidence_factors: list[dict],
    ) -> float:
        """
        Atualizar probabilidade prior com múltiplos fatores de evidência.

        Args:
            prior_prob: Probabilidade prior (0-1)
            evidence_factors: Lista de fatores de evidência, cada um com:
                - likelihood_ratio: razão de verossimilhança (> 1 favorece blue)
                - weight: peso do fator (0-1)

        Returns:
            Probabilidade posterior atualizada
        """
        # Converter para odds
        if prior_prob <= 0 or prior_prob >= 1:
            return prior_prob

        prior_odds = prior_prob / (1 - prior_prob)
        posterior_odds = prior_odds

        for factor in evidence_factors:
            lr = factor.get("likelihood_ratio", 1.0)
            weight = factor.get("weight", 1.0)
            # Atualização bayesiana ponderada
            posterior_odds *= (lr ** weight)

        # Converter de volta para probabilidade
        posterior_prob = posterior_odds / (1 + posterior_odds)
        return float(np.clip(posterior_prob, 0.05, 0.95))

    def calculate_confidence_interval(
        self,
        wins: int,
        losses: int,
        confidence: float = 0.95,
    ) -> tuple[float, float]:
        """
        Calcular intervalo de credibilidade para a probabilidade de vitória.

        Com menos jogos, o intervalo é mais amplo (maior incerteza).
        """
        from scipy.stats import beta as beta_dist
        alpha_post = 1.0 + wins
        beta_post = 1.0 + losses
        low, high = beta_dist.interval(confidence, alpha_post, beta_post)
        return (round(low, 4), round(high, 4))
