"""
Configuração do ambiente Alembic para migrações de banco de dados.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Adicionar o diretório raiz ao path para importar os modelos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import Base  # noqa: E402
import backend.models  # noqa: E402, F401 — importa todos os modelos para o metadata

config = context.config

# Sobrescrever URL do banco com a variável de ambiente se disponível
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executar migrações no modo offline (sem conexão ao banco)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executar migrações no modo online (com conexão ao banco)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
