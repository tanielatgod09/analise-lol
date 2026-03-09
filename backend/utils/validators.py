"""
Validadores de dados do sistema.

Garantem que apenas dados válidos e consistentes sejam
utilizados nas análises e recomendações.
"""
from typing import Any, Optional


def validate_odd(odd: Any) -> float:
    """
    Validar e retornar uma odd decimal.

    Raises:
        ValueError: Se a odd for inválida
    """
    try:
        value = float(odd)
    except (TypeError, ValueError):
        raise ValueError(f"Odd inválida: '{odd}' não é um número")

    if value <= 1.0:
        raise ValueError(f"Odd inválida: {value} — deve ser > 1.0")

    if value > 1000.0:
        raise ValueError(f"Odd suspeita: {value} — valor muito alto")

    return value


def validate_probability(prob: Any, name: str = "probabilidade") -> float:
    """
    Validar e retornar uma probabilidade.

    Raises:
        ValueError: Se a probabilidade for inválida
    """
    try:
        value = float(prob)
    except (TypeError, ValueError):
        raise ValueError(f"{name} inválida: '{prob}' não é um número")

    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} fora do intervalo [0, 1]: {value}")

    return value


def validate_league(league: str) -> str:
    """
    Validar nome de liga.

    Raises:
        ValueError: Se a liga não for suportada
    """
    from backend.utils.constants import SUPPORTED_LEAGUES
    normalized = league.upper().strip()
    if normalized not in SUPPORTED_LEAGUES:
        raise ValueError(
            f"Liga '{league}' não suportada. "
            f"Ligas válidas: {', '.join(SUPPORTED_LEAGUES)}"
        )
    return normalized


def validate_game_state(game_state: dict) -> dict:
    """
    Validar estado do jogo para live betting.

    Retorna dicionário validado com valores padrão para campos ausentes.
    """
    validated = {}

    # Diferença de gold: entre -20.000 e 20.000
    gold_diff = game_state.get("gold_diff", 0)
    try:
        gold_diff = float(gold_diff)
        if abs(gold_diff) > 30000:
            gold_diff = max(-30000, min(30000, gold_diff))
    except (TypeError, ValueError):
        gold_diff = 0
    validated["gold_diff"] = gold_diff

    # Kills: entre 0 e 50
    for key in ["kills_blue", "kills_red"]:
        val = game_state.get(key, 0)
        try:
            val = max(0, min(50, int(val)))
        except (TypeError, ValueError):
            val = 0
        validated[key] = val

    # Objetivos: entre 0 e valores máximos razoáveis
    obj_limits = {
        "dragons_blue": 5, "dragons_red": 5,
        "barons_blue": 3, "barons_red": 3,
        "towers_blue": 11, "towers_red": 11,
    }
    for key, max_val in obj_limits.items():
        val = game_state.get(key, 0)
        try:
            val = max(0, min(max_val, int(val)))
        except (TypeError, ValueError):
            val = 0
        validated[key] = val

    # Tempo de jogo: entre 0 e 60 minutos (3600 segundos)
    game_time = game_state.get("game_time_seconds", 600)
    try:
        game_time = max(0, min(3600, int(game_time)))
    except (TypeError, ValueError):
        game_time = 600
    validated["game_time_seconds"] = game_time

    return validated


def validate_team_stats(stats: dict) -> dict:
    """
    Validar e sanitizar estatísticas de um time.
    """
    validated = {}

    # Winrate: entre 0 e 1
    if "winrate" in stats:
        validated["winrate"] = validate_probability(stats["winrate"], "winrate")

    # Kills por jogo: entre 0 e 30
    for key in ["kills_per_game", "deaths_per_game"]:
        if key in stats:
            try:
                val = float(stats[key])
                validated[key] = max(0.0, min(30.0, val))
            except (TypeError, ValueError):
                pass

    # Taxas de objetivos (first_blood, first_dragon, first_baron): entre 0 e 1
    for key in ["first_blood_rate", "first_dragon_rate", "first_baron_rate"]:
        if key in stats:
            try:
                validated[key] = validate_probability(stats[key], key)
            except ValueError:
                pass

    return validated
