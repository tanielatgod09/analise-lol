"""
Configuração da conexão com o banco de dados PostgreSQL via SQLAlchemy.
Usa SQLite automaticamente quando PostgreSQL não está disponível.
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

logger = logging.getLogger(__name__)

# Base para os modelos ORM (não requer conexão)
Base = declarative_base()

# Usar SQLite em memória para testes
_TEST_DB_URL = "sqlite:///:memory:"
_SQLITE_FALLBACK_URL = "sqlite:///./analise_lol.db"


def _create_engine_with_fallback():
    """Tenta conectar ao PostgreSQL; se falhar, usa SQLite como fallback."""
    if os.getenv("TESTING", "false").lower() == "true":
        logger.info("Modo de teste: usando SQLite em memória")
        return create_engine(
            _TEST_DB_URL,
            connect_args={"check_same_thread": False},
        )

    pg_url = settings.database_url
    if not pg_url.startswith("sqlite"):
        try:
            pg_engine = create_engine(
                pg_url,
                pool_pre_ping=True,
                pool_timeout=5,
                connect_args={"connect_timeout": 5},
            )
            with pg_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Conectado ao PostgreSQL com sucesso")
            return pg_engine
        except Exception as exc:
            logger.warning(
                "PostgreSQL indisponível (%s). Usando SQLite como fallback: %s",
                exc,
                _SQLITE_FALLBACK_URL,
            )

    logger.info("Usando banco de dados SQLite: %s", _SQLITE_FALLBACK_URL)
    return create_engine(
        _SQLITE_FALLBACK_URL,
        connect_args={"check_same_thread": False},
        echo=settings.app_debug,
    )


engine = _create_engine_with_fallback()

# Fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Gerador de sessão do banco de dados para uso como dependência no FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Criar todas as tabelas definidas nos modelos (uso em desenvolvimento)."""
    Base.metadata.create_all(bind=engine)
