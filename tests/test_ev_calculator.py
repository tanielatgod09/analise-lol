"""
Testes para o módulo de cálculo de Expected Value.
"""
import pytest
from backend.services.ev_calculator import EVCalculator


@pytest.fixture
def calculator():
    return EVCalculator()


class TestCalculateEV:
    """Testes do cálculo de EV = (prob_real × odd) - 1"""

    def test_ev_positivo(self, calculator):
        """Aposta com probabilidade real maior que a implícita = EV positivo."""
        # Odd 2.0 → implícita 50%, real 60% → EV = (0.60 × 2.0) - 1 = +0.20
        ev = calculator.calculate_ev(0.60, 2.0)
        assert ev == pytest.approx(0.20, abs=1e-4)

    def test_ev_negativo(self, calculator):
        """Aposta com prob real menor que a implícita = EV negativo."""
        # Odd 1.85 → implícita 54%, real 40% → EV = (0.40 × 1.85) - 1 = -0.26
        ev = calculator.calculate_ev(0.40, 1.85)
        assert ev == pytest.approx(-0.26, abs=1e-4)

    def test_ev_neutro(self, calculator):
        """Prob real igual à implícita = EV próximo a zero."""
        # Odd 2.0 → implícita 50% → EV = (0.50 × 2.0) - 1 = 0
        ev = calculator.calculate_ev(0.50, 2.0)
        assert ev == pytest.approx(0.0, abs=1e-4)

    def test_odd_invalida_zero(self, calculator):
        with pytest.raises(ValueError):
            calculator.calculate_ev(0.5, 0.0)

    def test_odd_invalida_negativa(self, calculator):
        with pytest.raises(ValueError):
            calculator.calculate_ev(0.5, -1.5)

    def test_probabilidade_invalida(self, calculator):
        with pytest.raises(ValueError):
            calculator.calculate_ev(1.5, 2.0)

    def test_probabilidade_zero(self, calculator):
        ev = calculator.calculate_ev(0.0, 2.0)
        assert ev == pytest.approx(-1.0, abs=1e-4)

    def test_probabilidade_um(self, calculator):
        """Probabilidade 100% = ganho garantido."""
        ev = calculator.calculate_ev(1.0, 2.0)
        assert ev == pytest.approx(1.0, abs=1e-4)


class TestImpliedProbability:
    """Testes do cálculo de probabilidade implícita."""

    def test_odd_2(self, calculator):
        prob = calculator.calculate_implied_probability(2.0)
        assert prob == pytest.approx(0.5, abs=1e-4)

    def test_odd_1_85(self, calculator):
        prob = calculator.calculate_implied_probability(1.85)
        assert prob == pytest.approx(0.5405, abs=1e-3)

    def test_odd_invalida(self, calculator):
        with pytest.raises(ValueError):
            calculator.calculate_implied_probability(0)


class TestClassifyBet:
    """Testes da classificação de apostas."""

    def test_muito_segura(self, calculator):
        assert calculator.classify_bet(0.90) == "muito_segura"

    def test_boa(self, calculator):
        assert calculator.classify_bet(0.80) == "boa"

    def test_moderada(self, calculator):
        assert calculator.classify_bet(0.70) == "moderada"

    def test_arriscada(self, calculator):
        assert calculator.classify_bet(0.60) == "arriscada"

    def test_limite_muito_segura_boa(self, calculator):
        # 0.85 não é > 0.85, portanto é "boa"
        assert calculator.classify_bet(0.85) == "boa"
        # 0.851 é > 0.85, portanto é "muito_segura"
        assert calculator.classify_bet(0.851) == "muito_segura"

    def test_limite_boa_moderada(self, calculator):
        # 0.75 não é > 0.75, portanto é "moderada"
        assert calculator.classify_bet(0.75) == "moderada"
        # 0.751 é > 0.75, portanto é "boa"
        assert calculator.classify_bet(0.751) == "boa"


class TestKellyCriterion:
    """Testes do critério de Kelly."""

    def test_kelly_positivo(self, calculator):
        """Aposta com EV positivo deve ter Kelly positivo."""
        kelly = calculator.kelly_criterion(0.60, 2.0)
        assert kelly > 0

    def test_kelly_zero_ev_negativo(self, calculator):
        """Aposta sem vantagem não deve ser apostada (Kelly = 0)."""
        kelly = calculator.kelly_criterion(0.40, 2.0)
        assert kelly == 0.0

    def test_kelly_fracionado(self, calculator):
        """Kelly fracionado deve ser menor que o Kelly completo."""
        kelly_full = calculator.kelly_criterion(0.60, 2.0, fraction=1.0)
        kelly_25 = calculator.kelly_criterion(0.60, 2.0, fraction=0.25)
        assert kelly_25 == pytest.approx(kelly_full * 0.25, abs=1e-4)


class TestAnalyzeMarket:
    """Testes da análise de mercado com múltiplas casas."""

    def test_melhor_odd_identificada(self, calculator):
        odds = {
            "Pinnacle": 1.85,
            "1xbet": 1.90,
            "Bet365": 1.88,
        }
        result = calculator.analyze_market(0.60, odds)
        assert result["best_bet"]["bookmaker"] == "1xbet"
        assert result["best_bet"]["ev"] > 0

    def test_sem_value(self, calculator):
        """Quando prob real < todas as implícitas, não há valor."""
        odds = {"Pinnacle": 1.50}
        result = calculator.analyze_market(0.40, odds)
        assert result["best_bet"]["has_value"] is False
