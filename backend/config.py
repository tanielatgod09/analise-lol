"""
Configurações da aplicação carregadas via variáveis de ambiente.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações carregadas do arquivo .env ou variáveis de ambiente."""

    # Aplicação
    app_env: str = "development"
    app_secret_key: str = "chave_secreta_desenvolvimento"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Banco de dados
    database_url: str = "postgresql://postgres:senha@localhost:5432/analise_lol"

    # APIs de dados
    riot_api_key: str = ""
    pandascore_api_key: str = ""
    lol_esports_api_key: str = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
    odds_api_key: str = ""

    # Cache
    cache_ttl_seconds: int = 300

    # Scheduler
    data_update_interval_minutes: int = 5
    odds_update_interval_minutes: int = 5

    # Machine Learning
    ml_models_path: str = "./ml_models"
    ml_min_games_for_prediction: int = 5

    # Apostas
    min_ev_threshold: float = 0.0
    min_confidence_threshold: float = 0.65
    min_highlight_confidence: float = 0.75

    # Monte Carlo
    monte_carlo_simulations: int = 10000

    # Logs
    log_level: str = "INFO"
    log_format: str = "json"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Retornar instância única (singleton) das configurações."""
    return Settings()


settings = get_settings()
