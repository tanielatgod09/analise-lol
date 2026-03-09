"""
Configuração do pacote analise-lol.
"""
from setuptools import setup, find_packages

setup(
    name="analise-lol",
    version="1.0.0",
    description="Sistema Profissional de Análise de Apostas para League of Legends",
    author="Desenvolvedor",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.111.0",
        "uvicorn[standard]>=0.29.0",
        "sqlalchemy>=2.0.30",
        "alembic>=1.13.1",
        "psycopg2-binary>=2.9.9",
        "scikit-learn>=1.4.2",
        "xgboost>=2.0.3",
        "lightgbm>=4.3.0",
        "scipy>=1.13.0",
        "numpy>=1.26.4",
        "pandas>=2.2.2",
        "httpx>=0.27.0",
        "apscheduler>=3.10.4",
        "python-dotenv>=1.0.1",
        "structlog>=24.1.0",
    ],
)
