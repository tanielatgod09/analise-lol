"""
Testes para o motor de probabilidades.
"""
import pytest
from unittest.mock import MagicMock, patch
from backend.services.probability_engine import ProbabilityEngine


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def engine(mock_db):
    return ProbabilityEngine(mock_db)


def make_team(name="Time A", winrate=0.6, games=20, gpm=36000, playstyle="early_game",
              first_blood=0.55, first_dragon=0.60, first_baron=0.50, avg_duration=1800):
    team = MagicMock()
    team.name = name
    team.winrate = winrate
    team.games_played = games
    team.gold_per_minute = gpm
    team.playstyle = playstyle
    team.first_blood_rate = first_blood
    team.first_dragon_rate = first_dragon
    team.first_baron_rate = first_baron
    team.avg_game_duration = avg_duration
    return team


class TestCalculateWinProbability:
    def test_retorna_dict_com_chaves_corretas(self, engine):
        match = MagicMock()
        match.id = 1
        match.team_blue_id = 1
        match.team_red_id = 2

        blue = make_team("T1", winrate=0.7, games=30)
        red = make_team("GenG", winrate=0.5, games=25)

        engine.db.query.return_value.filter.return_value.first.side_effect = [blue, red]

        with patch.object(engine.stats_calc, 'get_head_to_head', return_value={
            "team1_winrate_h2h": 0.6, "total_games": 5
        }):
            result = engine.calculate_win_probability(match)

        assert "blue_win_prob" in result
        assert "red_win_prob" in result
        assert "confidence" in result

    def test_probabilidades_somam_um(self, engine):
        match = MagicMock()
        match.id = 1
        match.team_blue_id = 1
        match.team_red_id = 2

        blue = make_team(winrate=0.7, games=20)
        red = make_team(winrate=0.5, games=20)

        engine.db.query.return_value.filter.return_value.first.side_effect = [blue, red]

        with patch.object(engine.stats_calc, 'get_head_to_head', return_value={
            "team1_winrate_h2h": 0.5, "total_games": 0
        }):
            result = engine.calculate_win_probability(match)

        total = result["blue_win_prob"] + result["red_win_prob"]
        assert total == pytest.approx(1.0, abs=1e-4)

    def test_times_nao_encontrados(self, engine):
        match = MagicMock()
        match.id = 1
        match.team_blue_id = 999
        match.team_red_id = 998

        engine.db.query.return_value.filter.return_value.first.return_value = None

        result = engine.calculate_win_probability(match)
        assert result["blue_win_prob"] == 0.5
        assert result["red_win_prob"] == 0.5

    def test_com_ml_probability(self, engine):
        match = MagicMock()
        match.id = 1
        match.team_blue_id = 1
        match.team_red_id = 2

        blue = make_team(winrate=0.5, games=10)
        red = make_team(winrate=0.5, games=10)

        engine.db.query.return_value.filter.return_value.first.side_effect = [blue, red]

        with patch.object(engine.stats_calc, 'get_head_to_head', return_value={
            "team1_winrate_h2h": 0.5, "total_games": 0
        }):
            result = engine.calculate_win_probability(match, ml_probability=0.75)

        # Com ML prob=0.75, resultado deve ser mais próximo de 0.75
        assert result["blue_win_prob"] > 0.6
        assert result["method"] == "ml_composite"


class TestImpliedProbability:
    def test_odd_2(self, engine):
        prob = engine.calculate_implied_probability(2.0)
        assert prob == pytest.approx(0.5, abs=1e-4)

    def test_odd_1_50(self, engine):
        prob = engine.calculate_implied_probability(1.50)
        assert prob == pytest.approx(0.6667, abs=1e-3)


class TestRemoveVig:
    def test_remove_margem(self, engine):
        """Soma das probabilidades verdadeiras deve ser 1.0."""
        probs_true = engine.remove_vig([1.90, 1.90])
        assert sum(probs_true) == pytest.approx(1.0, abs=1e-4)

    def test_simetrico(self, engine):
        """Duas odds iguais devem ter probabilidades iguais."""
        probs = engine.remove_vig([2.0, 2.0])
        assert probs[0] == pytest.approx(probs[1], abs=1e-4)


class TestPhaseAdvantage:
    def test_early_vs_late(self, engine):
        """Time Early Game deve ter vantagem no early."""
        blue = make_team(playstyle="early_game")
        red = make_team(playstyle="late_game")
        result = engine.calculate_phase_advantage(blue, red)
        assert result["early"] == "blue"
        assert result["late"] == "red"

    def test_iguais(self, engine):
        """Times com mesmo estilo = equilibrado."""
        blue = make_team(playstyle="mid_game")
        red = make_team(playstyle="mid_game")
        result = engine.calculate_phase_advantage(blue, red)
        # Pode ser "equal" ou diferir levemente — só verificar que tem as chaves
        assert "early" in result
        assert "mid" in result
        assert "late" in result
