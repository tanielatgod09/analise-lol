"""
Ponto de entrada principal da aplicação FastAPI.
"""
import pathlib
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.config import settings
from backend.utils.logger import get_logger
from backend.api.routes import matches, teams, players, predictions, odds, live, dashboard

logger = get_logger(__name__)

_DASHBOARD_HTML = pathlib.Path(__file__).parent / "templates" / "dashboard.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executar tarefas de inicialização e encerramento da aplicação."""
    logger.info("Iniciando Sistema de Análise de Apostas LoL...")

    # Importar todos os modelos para garantir que estão registrados no metadata
    try:
        from backend.models.team import Team  # noqa: F401
        from backend.models.player import Player  # noqa: F401
        from backend.models.match import Match  # noqa: F401
        from backend.models.champion import Champion  # noqa: F401
        from backend.models.odds import Odds  # noqa: F401
        from backend.models.prediction import Prediction  # noqa: F401
        from backend.models.bet_recommendation import BetRecommendation  # noqa: F401
    except Exception as exc:
        logger.warning(f"Alguns modelos não puderam ser importados: {exc}")

    # Criar tabelas automaticamente no startup
    try:
        from backend.database import create_tables
        create_tables()
        logger.info("Tabelas criadas/verificadas com sucesso")
    except Exception as exc:
        logger.warning(f"Não foi possível criar tabelas: {exc}")

    # Iniciar scheduler de atualização automática de dados
    try:
        from backend.tasks.scheduler import start_scheduler
        start_scheduler()
        logger.info("Scheduler iniciado com sucesso")
    except Exception as exc:
        logger.warning(f"Scheduler não iniciado: {exc}")

    yield

    # Encerramento da aplicação
    try:
        from backend.tasks.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass
    logger.info("Sistema encerrado.")


app = FastAPI(
    title="Sistema de Análise de Apostas LoL",
    description=(
        "Sistema profissional de análise de apostas para League of Legends. "
        "Coleta dados reais de APIs confiáveis, calcula probabilidades e identifica "
        "apostas com Expected Value positivo."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS para o frontend React e Codespaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(matches.router, prefix="/api/v1/matches", tags=["Partidas"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Times"])
app.include_router(players.router, prefix="/api/v1/players", tags=["Jogadores"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["Previsões"])
app.include_router(odds.router, prefix="/api/v1/odds", tags=["Odds"])
app.include_router(live.router, prefix="/api/v1/live", tags=["Live Betting"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"], include_in_schema=False)
async def root():
    """Dashboard visual HTML."""
    return HTMLResponse(content=_DASHBOARD_HTML.read_text(encoding="utf-8"))


@app.get("/api/status", tags=["Health"])
async def api_status():
    """Status da API em formato JSON."""
    return {
        "status": "online",
        "sistema": "Análise de Apostas LoL",
        "versao": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Verificação detalhada de saúde da aplicação."""
    from backend.database import engine
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "online"
    except Exception:
        db_status = "offline"

    return {
        "status": "online",
        "banco_de_dados": db_status,
        "ambiente": settings.app_env,
    }
