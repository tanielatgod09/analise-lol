"""
Calculadora de Expected Value (EV) para apostas.

EV = (probabilidade_real × odd) - 1

Apostas com EV > 0 têm valor esperado positivo.
"""
from typing import Optional
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class EVCalculator:
    """
    Calcula o Expected Value (Valor Esperado) para apostas esportivas.

    O EV positivo indica que a aposta tem vantagem matemática sobre
    a casa de apostas no longo prazo.
    """

    def calculate_ev(self, real_probability: float, odd: float) -> float:
        """
        Calcular o Expected Value de uma aposta.

        Args:
            real_probability: Probabilidade real calculada pelo sistema [0, 1]
            odd: Odd decimal da casa de apostas (ex: 1.85)

        Returns:
            EV da aposta. Positivo indica aposta com valor.

        Exemplo:
            Probabilidade real: 0.60 (60%)
            Odd: 1.85
            EV = (0.60 × 1.85) - 1 = 0.11 → +11% de valor
        """
        if odd <= 0:
            raise ValueError(f"Odd inválida: {odd}")
        if not 0 <= real_probability <= 1:
            raise ValueError(f"Probabilidade inválida: {real_probability}")

        ev = (real_probability * odd) - 1
        return round(ev, 4)

    def calculate_implied_probability(self, odd: float) -> float:
        """Calcular probabilidade implícita a partir da odd decimal."""
        if odd <= 0:
            raise ValueError(f"Odd inválida: {odd}")
        return round(1 / odd, 4)

    def calculate_edge(self, real_probability: float, odd: float) -> float:
        """
        Calcular a vantagem (edge) sobre a casa de apostas.

        Edge = probabilidade_real - probabilidade_implícita

        Edge positivo = a casa subestimou a probabilidade real.
        """
        implied = self.calculate_implied_probability(odd)
        return round(real_probability - implied, 4)

    def classify_bet(self, real_probability: float) -> str:
        """
        Classificar uma aposta pela sua probabilidade real.

        Regras:
        - > 85% → muito segura
        - 75–85% → boa
        - 65–75% → moderada
        - < 65% → arriscada
        """
        if real_probability > 0.85:
            return "muito_segura"
        elif real_probability > 0.75:
            return "boa"
        elif real_probability > 0.65:
            return "moderada"
        else:
            return "arriscada"

    def is_highlighted(self, real_probability: float) -> bool:
        """Verificar se a aposta deve ser destacada (prob > 75%)."""
        return real_probability >= settings.min_highlight_confidence

    def has_value(self, real_probability: float, odd: float) -> bool:
        """Verificar se a aposta tem EV positivo."""
        ev = self.calculate_ev(real_probability, odd)
        return ev > settings.min_ev_threshold

    def kelly_criterion(
        self,
        real_probability: float,
        odd: float,
        fraction: float = 0.25,
    ) -> float:
        """
        Calcular fração de banca a apostar pelo critério de Kelly.

        Usa o Kelly fracionado (padrão: 25% do Kelly completo) para
        reduzir o risco de ruína.

        Args:
            real_probability: Probabilidade real de ganhar
            odd: Odd decimal
            fraction: Fração do Kelly a usar (0.25 = 25%)

        Returns:
            Percentual da banca a apostar (0.0 a 1.0)
        """
        b = odd - 1  # lucro por unidade apostada
        p = real_probability
        q = 1 - p

        kelly_full = (b * p - q) / b if b > 0 else 0
        kelly_fractional = max(0.0, kelly_full * fraction)

        return round(kelly_fractional, 4)

    def analyze_market(
        self,
        real_probability: float,
        odds_by_bookmaker: dict,
    ) -> dict:
        """
        Analisar um mercado comparando a probabilidade real com as
        odds de diferentes casas de apostas.

        Args:
            real_probability: Probabilidade real calculada pelo sistema
            odds_by_bookmaker: {"Pinnacle": 1.85, "1xbet": 1.90, ...}

        Returns:
            Análise completa do mercado com a melhor aposta identificada
        """
        results = []
        for bookmaker, odd in odds_by_bookmaker.items():
            try:
                ev = self.calculate_ev(real_probability, odd)
                implied = self.calculate_implied_probability(odd)
                edge = self.calculate_edge(real_probability, odd)
                kelly = self.kelly_criterion(real_probability, odd)

                results.append({
                    "bookmaker": bookmaker,
                    "odd": odd,
                    "implied_probability": implied,
                    "real_probability": real_probability,
                    "ev": ev,
                    "edge": edge,
                    "kelly_fraction": kelly,
                    "has_value": ev > 0,
                    "classification": self.classify_bet(real_probability),
                    "is_highlighted": self.is_highlighted(real_probability),
                })
            except ValueError:
                continue

        # Ordenar pela melhor odd com EV positivo
        results.sort(key=lambda x: x["ev"], reverse=True)

        best = results[0] if results else None

        return {
            "real_probability": real_probability,
            "classification": self.classify_bet(real_probability),
            "is_highlighted": self.is_highlighted(real_probability),
            "best_bet": best,
            "all_bookmakers": results,
        }
