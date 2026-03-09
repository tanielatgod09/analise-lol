"""
Agendador de tarefas — atualiza dados a cada 5 minutos.

Utiliza APScheduler para executar tarefas automáticas em background.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_scheduler: BackgroundScheduler = None


def start_scheduler() -> None:
    """Iniciar o agendador de tarefas em background."""
    global _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")

    # Atualizar dados de partidas e times a cada 5 minutos
    _scheduler.add_job(
        func=_update_data_job,
        trigger=IntervalTrigger(minutes=settings.data_update_interval_minutes),
        id="update_data",
        name="Atualizar dados de partidas e times",
        replace_existing=True,
        misfire_grace_time=60,
    )

    # Atualizar odds a cada 5 minutos
    _scheduler.add_job(
        func=_update_odds_job,
        trigger=IntervalTrigger(minutes=settings.odds_update_interval_minutes),
        id="update_odds",
        name="Atualizar odds das casas de apostas",
        replace_existing=True,
        misfire_grace_time=60,
    )

    _scheduler.start()
    logger.info(
        f"Scheduler iniciado — dados atualizados a cada "
        f"{settings.data_update_interval_minutes} minutos"
    )


def stop_scheduler() -> None:
    """Parar o agendador."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler encerrado")


def _update_data_job() -> None:
    """Job de atualização de dados de partidas."""
    try:
        from backend.tasks.data_update import DataUpdateTask
        from backend.database import SessionLocal
        db = SessionLocal()
        try:
            task = DataUpdateTask(db)
            task.run()
        finally:
            db.close()
    except Exception as exc:
        logger.error(f"Erro no job de atualização de dados: {exc}")


def _update_odds_job() -> None:
    """Job de atualização de odds."""
    try:
        from backend.tasks.odds_update import OddsUpdateTask
        from backend.database import SessionLocal
        db = SessionLocal()
        try:
            task = OddsUpdateTask(db)
            task.run()
        finally:
            db.close()
    except Exception as exc:
        logger.error(f"Erro no job de atualização de odds: {exc}")
