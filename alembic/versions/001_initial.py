"""Migração inicial — criação de todas as tabelas do sistema.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Criar todas as tabelas do sistema."""

    # Tabela de times
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("acronym", sa.String(20), nullable=True),
        sa.Column("league", sa.String(50), nullable=True),
        sa.Column("region", sa.String(50), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("current_lineup_since", sa.DateTime(), nullable=True),
        sa.Column("winrate", sa.Float(), nullable=True),
        sa.Column("games_played", sa.Integer(), nullable=True),
        sa.Column("kills_per_game", sa.Float(), nullable=True),
        sa.Column("deaths_per_game", sa.Float(), nullable=True),
        sa.Column("gold_per_minute", sa.Float(), nullable=True),
        sa.Column("first_blood_rate", sa.Float(), nullable=True),
        sa.Column("first_dragon_rate", sa.Float(), nullable=True),
        sa.Column("first_baron_rate", sa.Float(), nullable=True),
        sa.Column("towers_per_game", sa.Float(), nullable=True),
        sa.Column("avg_game_duration", sa.Float(), nullable=True),
        sa.Column("playstyle", sa.String(50), nullable=True),
        sa.Column("game_pace", sa.String(50), nullable=True),
        sa.Column("patch_performance", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_teams_external_id", "teams", ["external_id"])

    # Tabela de jogadores
    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("real_name", sa.String(200), nullable=True),
        sa.Column("role", sa.String(50), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("kda", sa.Float(), nullable=True),
        sa.Column("kill_participation", sa.Float(), nullable=True),
        sa.Column("avg_kills", sa.Float(), nullable=True),
        sa.Column("avg_deaths", sa.Float(), nullable=True),
        sa.Column("avg_assists", sa.Float(), nullable=True),
        sa.Column("champion_pool", sa.JSON(), nullable=True),
        sa.Column("patch_performance", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_players_external_id", "players", ["external_id"])

    # Tabela de partidas
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("league", sa.String(50), nullable=True),
        sa.Column("tournament", sa.String(200), nullable=True),
        sa.Column("team_blue_id", sa.Integer(), nullable=True),
        sa.Column("team_red_id", sa.Integer(), nullable=True),
        sa.Column("winner_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("patch", sa.String(20), nullable=True),
        sa.Column("series_type", sa.String(10), nullable=True),
        sa.Column("blue_kills", sa.Integer(), nullable=True),
        sa.Column("red_kills", sa.Integer(), nullable=True),
        sa.Column("blue_towers", sa.Integer(), nullable=True),
        sa.Column("red_towers", sa.Integer(), nullable=True),
        sa.Column("blue_dragons", sa.Integer(), nullable=True),
        sa.Column("red_dragons", sa.Integer(), nullable=True),
        sa.Column("blue_barons", sa.Integer(), nullable=True),
        sa.Column("red_barons", sa.Integer(), nullable=True),
        sa.Column("blue_gold", sa.BigInteger(), nullable=True),
        sa.Column("red_gold", sa.BigInteger(), nullable=True),
        sa.Column("draft_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["team_blue_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["team_red_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["winner_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matches_external_id", "matches", ["external_id"])
    op.create_index("ix_matches_scheduled_at", "matches", ["scheduled_at"])

    # Tabela de campeões
    op.create_table(
        "champions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("riot_id", sa.String(100), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("roles", sa.JSON(), nullable=True),
        sa.Column("patch", sa.String(20), nullable=True),
        sa.Column("winrate", sa.Float(), nullable=True),
        sa.Column("pickrate", sa.Float(), nullable=True),
        sa.Column("banrate", sa.Float(), nullable=True),
        sa.Column("avg_kills", sa.Float(), nullable=True),
        sa.Column("avg_deaths", sa.Float(), nullable=True),
        sa.Column("avg_assists", sa.Float(), nullable=True),
        sa.Column("game_style", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    # Tabela de odds
    op.create_table(
        "odds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("bookmaker", sa.String(100), nullable=False),
        sa.Column("market", sa.String(100), nullable=False),
        sa.Column("selection", sa.String(200), nullable=False),
        sa.Column("odd_value", sa.Float(), nullable=False),
        sa.Column("implied_probability", sa.Float(), nullable=True),
        sa.Column("is_live", sa.Boolean(), default=False),
        sa.Column("collected_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_odds_match_id", "odds", ["match_id"])

    # Tabela de previsões
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("blue_win_probability", sa.Float(), nullable=True),
        sa.Column("red_win_probability", sa.Float(), nullable=True),
        sa.Column("predicted_total_kills", sa.Float(), nullable=True),
        sa.Column("kills_std_dev", sa.Float(), nullable=True),
        sa.Column("predicted_duration_seconds", sa.Float(), nullable=True),
        sa.Column("predicted_blue_dragons", sa.Float(), nullable=True),
        sa.Column("predicted_red_dragons", sa.Float(), nullable=True),
        sa.Column("predicted_blue_barons", sa.Float(), nullable=True),
        sa.Column("predicted_red_barons", sa.Float(), nullable=True),
        sa.Column("predicted_blue_towers", sa.Float(), nullable=True),
        sa.Column("predicted_red_towers", sa.Float(), nullable=True),
        sa.Column("early_game_advantage", sa.String(10), nullable=True),
        sa.Column("mid_game_advantage", sa.String(10), nullable=True),
        sa.Column("late_game_advantage", sa.String(10), nullable=True),
        sa.Column("upset_risk_score", sa.Float(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("monte_carlo_simulations", sa.Integer(), nullable=True),
        sa.Column("detailed_results", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Tabela de recomendações de apostas
    op.create_table(
        "bet_recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("prediction_id", sa.Integer(), nullable=True),
        sa.Column("market", sa.String(100), nullable=False),
        sa.Column("selection", sa.String(200), nullable=False),
        sa.Column("bookmaker", sa.String(100), nullable=True),
        sa.Column("odd_value", sa.Float(), nullable=False),
        sa.Column("real_probability", sa.Float(), nullable=False),
        sa.Column("implied_probability", sa.Float(), nullable=False),
        sa.Column("expected_value", sa.Float(), nullable=False),
        sa.Column("classification", sa.String(50), nullable=True),
        sa.Column("confidence_level", sa.Float(), nullable=True),
        sa.Column("is_highlighted", sa.Boolean(), default=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bet_recommendations_match_id", "bet_recommendations", ["match_id"])


def downgrade() -> None:
    """Remover todas as tabelas."""
    op.drop_table("bet_recommendations")
    op.drop_table("predictions")
    op.drop_table("odds")
    op.drop_table("champions")
    op.drop_table("matches")
    op.drop_table("players")
    op.drop_table("teams")
