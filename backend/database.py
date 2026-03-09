"""
Configuração da conexão com o banco de dados PostgreSQL via SQLAlchemy.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

# Base para os modelos ORM (não requer conexão)
Base = declarative_base()

# Usar SQLite em memória para testes
_TEST_DB_URL = "sqlite:///:memory:"
_database_url = (
    _TEST_DB_URL
    if os.getenv("TESTING", "false").lower() == "true"
    else settings.database_url
)

# Criar engine de conexão com o banco
_connect_args = {"check_same_thread": False} if _database_url.startswith("sqlite") else {}
engine = create_engine(
    _database_url,
    pool_pre_ping=not _database_url.startswith("sqlite"),
    connect_args=_connect_args,
    echo=settings.app_debug and _database_url.startswith("sqlite"),
)

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
