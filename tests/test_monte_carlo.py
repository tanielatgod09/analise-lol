"""
Testes para o Simulador Monte Carlo.
"""
import pytest
import numpy as np
from backend.services.monte_carlo import MonteCarloSimulator


@pytest.fixture
def simulator():
    """Simulador com apenas 1.000 simulações para testes rápidos."""
    return MonteCarloSimulator(n_simulations=1000)


class TestSimulateMatch:
    """Testes da simulação de partidas."""

    def test_resultado_retorna_chaves_corretas(self, simulator):
        result = simulator.simulate_match(
            blue_win_prob=0.6,
            blue_kills_avg=13.0,
            red_kills_avg=10.0,
            seed=42,
        )
        assert "blue_win_probability" in result
        assert "red_win_probability" in result
        assert "kills" in result
        assert "duration" in result
        assert result["n_simulations"] == 1000

    def test_probabilidades_somam_um(self, simulator):
        result = simulator.simulate_match(
            blue_win_prob=0.65,
            blue_kills_avg=12.0,
            red_kills_avg=11.0,
            seed=42,
        )
        total = result["blue_win_probability"] + result["red_win_probability"]
        assert total == pytest.approx(1.0, abs=1e-4)

    def test_prob_favorito_maior(self, simulator):
        """Time com maior probabilidade deve ganhar mais frequentemente."""
        result = simulator.simulate_match(
            blue_win_prob=0.80,
            blue_kills_avg=15.0,
            red_kills_avg=8.0,
            seed=123,
        )
        assert result["blue_win_probability"] > result["red_win_probability"]

    def test_kills_nao_negativos(self, simulator):
        result = simulator.simulate_match(
            blue_win_prob=0.5,
            blue_kills_avg=5.0,
            red_kills_avg=5.0,
            seed=42,
        )
        assert result["kills"]["blue_avg"] >= 0
        assert result["kills"]["red_avg"] >= 0
        assert result["kills"]["total_avg"] >= 0

    def test_over_under_kills(self, simulator):
        """Probabilidades de over/under devem estar entre 0 e 1."""
        result = simulator.simulate_match(
            blue_win_prob=0.5,
            blue_kills_avg=14.0,
            red_kills_avg=12.0,
            seed=42,
        )
        kills = result["kills"]
        for key, val in kills.items():
            if key.startswith("over_"):
                assert 0.0 <= val <= 1.0, f"{key} fora do intervalo: {val}"

    def test_over_probabilidade_decrescente(self, simulator):
        """Over threshold maior = prob menor."""
        result = simulator.simulate_match(
            blue_win_prob=0.5,
            blue_kills_avg=14.0,
            red_kills_avg=11.0,
            seed=42,
        )
        kills = result["kills"]
        # over_20.5 deve ser maior que over_30.5
        assert kills.get("over_20.5", 1) >= kills.get("over_30.5", 0)

    def test_reproducibilidade_com_seed(self, simulator):
        """Mesma seed deve produzir mesmo resultado."""
        r1 = simulator.simulate_match(0.5, 12.0, 12.0, seed=999)
        r2 = simulator.simulate_match(0.5, 12.0, 12.0, seed=999)
        assert r1["blue_win_probability"] == r2["blue_win_probability"]
        assert r1["kills"]["total_avg"] == r2["kills"]["total_avg"]


class TestSimulateSeries:
    """Testes da simulação de séries BO3 e BO5."""

    def test_bo1_retorna_prob_direta(self, simulator):
        result = simulator.simulate_series(0.70, "BO1")
        assert result["blue_series_win_probability"] == pytest.approx(0.70, abs=0.01)

    def test_bo3_prob_favorito_maior(self, simulator):
        result = simulator.simulate_series(0.70, "BO3", seed=42)
        assert result["blue_series_win_probability"] > 0.70

    def test_bo5_prob_favorito_maior_que_bo3(self, simulator):
        """Em BO5, o favorito tem ainda mais vantagem que no BO3."""
        r3 = simulator.simulate_series(0.70, "BO3", seed=42)
        r5 = simulator.simulate_series(0.70, "BO5", seed=42)
        assert r5["blue_series_win_probability"] >= r3["blue_series_win_probability"]

    def test_bo3_soma_um(self, simulator):
        result = simulator.simulate_series(0.60, "BO3", seed=42)
        total = result["blue_series_win_probability"] + result["red_series_win_probability"]
        assert total == pytest.approx(1.0, abs=1e-4)

    def test_score_distribution_bo3(self, simulator):
        """Distribuição de placar deve conter apenas resultados válidos."""
        result = simulator.simulate_series(0.60, "BO3", seed=42)
        valid_scores = {"2-0", "2-1", "0-2", "1-2"}
        for score in result["score_distribution"]:
            assert score in valid_scores


class TestPoissonKills:
    """Testes da distribuição de Poisson para kills."""

    def test_retorna_chaves_corretas(self, simulator):
        result = simulator.calculate_poisson_kills(13.0, 11.0, n_simulations=500, seed=42)
        assert "expected_total" in result
        assert "over_probabilities" in result
        assert "under_probabilities" in result

    def test_expected_total(self, simulator):
        result = simulator.calculate_poisson_kills(13.0, 11.0, n_simulations=5000, seed=42)
        assert result["expected_total"] == pytest.approx(24.0, abs=0.1)

    def test_over_under_complementares(self, simulator):
        """Para um threshold inteiro, over + under ≈ 1."""
        result = simulator.calculate_poisson_kills(13.0, 11.0, n_simulations=10000, seed=42)
        over = result["over_probabilities"].get("over_22.5", 0)
        under = result["under_probabilities"].get("under_22.5", 0)
        assert over + under == pytest.approx(1.0, abs=0.01)
