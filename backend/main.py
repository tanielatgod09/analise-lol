"""
Ponto de entrada principal da aplicação FastAPI.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.utils.logger import get_logger
from backend.api.routes import matches, teams, players, predictions, odds, live, dashboard

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executar tarefas de inicialização e encerramento da aplicação."""
    logger.info("Iniciando Sistema de Análise de Apostas LoL...")

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

# Configurar CORS para o frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
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


@app.get("/", tags=["Health"])
async def root():
    """Verificar se a API está funcionando."""
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
