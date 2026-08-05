import sys
import logging
from app.infrastructure.database.connection import (
    engine,
    SessionLocal,
    get_engine,
    get_db,
    get_psycopg2_conn,
    DATABASE_URL,
)
from app.infrastructure.database.schema_init import inicializar_schema_bancos
from app.core.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

logger = logging.getLogger("uvicorn.error")

USE_LOCAL_TEST_DB = False
TARGET_DATABASES = [DB_NAME]

def garantir_view_roteamento():
    """Alias de compatibilidade."""
    inicializar_schema_bancos()

def execute_read_dual(func, default=None):
    """Executa func(conn) no banco configurado com tratamento de erros."""
    try:
        with engine.connect() as conn:
            return func(conn)
    except Exception as e:
        sys.stderr.write(f"\n[DB READ ERROR]: {str(e)}\n")
        sys.stderr.flush()
        logger.error(f"[DB Read Error]: {e}")
        return default if default is not None else []

def execute_write_dual(func):
    """Executa func(conn) em uma transação no banco configurado."""
    try:
        with engine.begin() as conn:
            return func(conn)
    except Exception as e:
        sys.stderr.write(f"\n[DB WRITE ERROR]: {str(e)}\n")
        sys.stderr.flush()
        logger.error(f"[DB Write Error]: {e}")
        raise
