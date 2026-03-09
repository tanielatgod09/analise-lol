"""
Testes para os modelos de Machine Learning.
"""
import pytest
import numpy as np
from backend.ml.models.win_predictor import WinPredictor
from backend.ml.models.kills_predictor import KillsPredictor
from backend.ml.models.duration_predictor import DurationPredictor
from backend.ml.models.bayesian_model import BayesianModel
from backend.ml.feature_engineering import FEATURE_COLUMNS


def make_sample_data(n=100, seed=42):
    """Gerar dados de treino sintéticos."""
    rng = np.random.default_rng(seed)
    n_features = len(FEATURE_COLUMNS)
    X = rng.random((n, n_features)).astype(np.float32)
    y_win = rng.integers(0, 2, n)
    y_kills = rng.normal(24, 6, n).clip(5, 50)
    y_duration = rng.normal(1900, 300, n).clip(900, 3600)
    return X, y_win, y_kills, y_duration


class TestWinPredictor:
    """Testes do preditor de vitória."""

    def test_treino_retorna_metricas(self):
        predictor = WinPredictor()
        X, y_win, _, _ = make_sample_data(100)
        metrics = predictor.train(X, y_win)
        assert "logistic_regression" in metrics
        assert "roc_auc_mean" in metrics["logistic_regression"]

    def test_predicao_retorna_probabilidade(self):
        predictor = WinPredictor()
        X, y_win, _, _ = make_sample_data(100)
        predictor.train(X, y_win)
        prob = predictor.predict_proba(X[0])
        assert prob is not None
        assert 0.0 <= prob <= 1.0

    def test_sem_treino_retorna_none(self):
        predictor = WinPredictor()
        X, _, _, _ = make_sample_data(10)
        assert predictor.predict_proba(X[0]) is None

    def test_dados_insuficientes_levanta_erro(self):
        predictor = WinPredictor()
        X, y_win, _, _ = make_sample_data(5)
        with pytest.raises(ValueError, match="Dados insuficientes"):
            predictor.train(X, y_win)

    def test_probabilidade_entre_0_e_1(self):
        predictor = WinPredictor()
        X, y_win, _, _ = make_sample_data(100)
        predictor.train(X, y_win)
        for i in range(min(20, len(X))):
            prob = predictor.predict_proba(X[i])
            assert 0.0 <= prob <= 1.0


class TestKillsPredictor:
    """Testes do preditor de kills."""

    def test_treino_retorna_mae(self):
        predictor = KillsPredictor()
        X, _, y_kills, _ = make_sample_data(100)
        metrics = predictor.train(X, y_kills)
        assert "mae_train" in metrics
        assert metrics["mae_train"] >= 0

    def test_predicao_positiva(self):
        predictor = KillsPredictor()
        X, _, y_kills, _ = make_sample_data(100)
        predictor.train(X, y_kills)
        kills = predictor.predict_kills(X[0])
        assert kills is not None
        assert kills >= 0

    def test_over_under_entre_0_e_1(self):
        predictor = KillsPredictor()
        X, _, y_kills, _ = make_sample_data(100)
        predictor.train(X, y_kills)
        for threshold in [20.5, 25.5, 30.5]:
            prob = predictor.predict_over_under(X[0], threshold)
            assert prob is not None
            assert 0.0 <= prob <= 1.0

    def test_over_prob_decrescente_com_threshold(self):
        """Maior threshold = menor probabilidade de over."""
        predictor = KillsPredictor()
        X, _, y_kills, _ = make_sample_data(100)
        predictor.train(X, y_kills)
        p1 = predictor.predict_over_under(X[0], 20.5)
        p2 = predictor.predict_over_under(X[0], 30.5)
        assert p1 >= p2


class TestDurationPredictor:
    """Testes do preditor de duração."""

    def test_treino_retorna_mae(self):
        predictor = DurationPredictor()
        X, _, _, y_duration = make_sample_data(100)
        metrics = predictor.train(X, y_duration)
        assert "mae_train_seconds" in metrics

    def test_predicao_positiva(self):
        predictor = DurationPredictor()
        X, _, _, y_duration = make_sample_data(100)
        predictor.train(X, y_duration)
        duration = predictor.predict_duration(X[0])
        assert duration is not None
        assert duration >= 0

    def test_classify_jogo_curto(self):
        predictor = DurationPredictor()
        assert predictor.classify_game_length(25 * 60) == "jogo_curto"

    def test_classify_jogo_medio(self):
        predictor = DurationPredictor()
        assert predictor.classify_game_length(30 * 60) == "jogo_medio"

    def test_classify_jogo_longo(self):
        predictor = DurationPredictor()
        assert predictor.classify_game_length(40 * 60) == "jogo_longo"


class TestBayesianModel:
    """Testes do modelo bayesiano."""

    def test_probabilidade_com_muitas_vitorias(self):
        model = BayesianModel()
        result = model.calculate_win_probability(wins=18, losses=2)
        assert result["mean_probability"] > 0.8

    def test_probabilidade_equilibrada(self):
        model = BayesianModel()
        result = model.calculate_win_probability(wins=10, losses=10)
        assert 0.45 <= result["mean_probability"] <= 0.55

    def test_intervalo_credibilidade(self):
        model = BayesianModel()
        result = model.calculate_win_probability(wins=10, losses=10)
        assert result["ci_95_low"] < result["mean_probability"] < result["ci_95_high"]

    def test_mais_jogos_intervalo_menor(self):
        """Com mais jogos, intervalo de credibilidade deve ser menor."""
        model = BayesianModel()
        r_small = model.calculate_win_probability(wins=5, losses=5)
        r_large = model.calculate_win_probability(wins=50, losses=50)
        width_small = r_small["ci_95_high"] - r_small["ci_95_low"]
        width_large = r_large["ci_95_high"] - r_large["ci_95_low"]
        assert width_large < width_small

    def test_update_with_evidence(self):
        model = BayesianModel()
        prior = 0.5
        evidence = [{"likelihood_ratio": 2.0, "weight": 1.0}]
        posterior = model.update_with_evidence(prior, evidence)
        assert posterior > prior

    def test_evidence_adversa_reduz_prob(self):
        model = BayesianModel()
        prior = 0.7
        evidence = [{"likelihood_ratio": 0.3, "weight": 1.0}]
        posterior = model.update_with_evidence(prior, evidence)
        assert posterior < prior
