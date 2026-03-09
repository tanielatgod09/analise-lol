"""
Sistema de logs estruturados para o backend.

Usa structlog para logs em formato JSON, facilitando
análise e monitoramento em produção.
"""
import logging
import sys
import structlog
from backend.config import settings


def setup_logging() -> None:
    """Configurar logging estruturado para toda a aplicação."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configurar logging padrão do Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Processadores do structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """Retornar logger estruturado para um módulo."""
    return structlog.get_logger(name)


# Inicializar logging ao importar o módulo
setup_logging()
