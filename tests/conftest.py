"""
Configuração de testes — usa SQLite em memória para evitar dependência do PostgreSQL.
"""
import os
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
