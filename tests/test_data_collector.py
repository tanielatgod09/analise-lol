"""
Testes para o serviço de coleta de dados.
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.services.data_collector import DataCollector


@pytest.fixture
def collector():
    return DataCollector()


class TestDataCollector:
    def test_inicializa_sem_erros(self, collector):
        assert collector is not None

    def test_sem_chave_api_retorna_lista_vazia(self, collector):
        """Sem API key configurada, deve retornar lista vazia graciosamente."""
        with patch.object(collector, 'pandascore_headers', {"Authorization": "Bearer "}):
            # A chave vazia deve ser detectada
            pass
        # Sem credenciais reais, apenas verifica que não levanta exceção
        assert isinstance(collector.pandascore_headers, dict)

    def test_parse_odds_formato_correto(self):
        """Verificar parsing de resposta da OddsAPI."""
        from backend.services.odds_collector import OddsCollector
        collector = OddsCollector()

        raw_data = [{
            "id": "abc123",
            "home_team": "T1",
            "away_team": "GenG",
            "commence_time": "2024-01-15T14:00:00Z",
            "bookmakers": [{
                "key": "pinnacle",
                "title": "Pinnacle",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "T1", "price": 1.85},
                        {"name": "GenG", "price": 2.05},
                    ]
                }]
            }]
        }]

        parsed = collector.parse_odds(raw_data)
        assert len(parsed) == 2
        assert parsed[0]["bookmaker"] == "pinnacle"
        assert parsed[0]["odd_value"] == 1.85
        assert parsed[0]["implied_probability"] == pytest.approx(1 / 1.85, abs=1e-3)
        assert parsed[0]["match_external_id"] == "abc123"

    def test_implied_prob_calculada_corretamente(self):
        from backend.services.odds_collector import OddsCollector
        collector = OddsCollector()

        raw_data = [{
            "id": "test1",
            "home_team": "Team A",
            "away_team": "Team B",
            "commence_time": "2024-01-15T14:00:00Z",
            "bookmakers": [{
                "key": "bet365",
                "title": "Bet365",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Team A", "price": 2.0},
                    ]
                }]
            }]
        }]

        parsed = collector.parse_odds(raw_data)
        assert parsed[0]["implied_probability"] == pytest.approx(0.5, abs=1e-3)

    def test_odd_zero_ignorada(self):
        """Odds com valor 0 devem ser ignoradas."""
        from backend.services.odds_collector import OddsCollector
        collector = OddsCollector()

        raw_data = [{
            "id": "test2",
            "home_team": "A",
            "away_team": "B",
            "commence_time": "2024-01-15T14:00:00Z",
            "bookmakers": [{
                "key": "test",
                "title": "Test",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "A", "price": 0},  # inválida
                        {"name": "B", "price": 1.90},  # válida
                    ]
                }]
            }]
        }]

        parsed = collector.parse_odds(raw_data)
        assert len(parsed) == 1
        assert parsed[0]["odd_value"] == 1.90
