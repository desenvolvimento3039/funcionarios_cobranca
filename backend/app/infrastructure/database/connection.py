import urllib.parse
from typing import Generator
import logging
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

logger = logging.getLogger("uvicorn.error")

_encoded_pass = urllib.parse.quote_plus(DB_PASSWORD)
DATABASE_URL = f"postgresql://{DB_USER}:{_encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_engine(dbname: str = None):
    """Retorna o engine SQLAlchemy padrão ou específico por nome."""
    return engine

def get_db(dbname: str = None) -> Generator[Session, None, None]:
    """Dependência do FastAPI para injetar a sessão do SQLAlchemy."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_psycopg2_conn(dbname: str = None):
    """Conexão psycopg2 direta para operações em lote pesadas."""
    target = dbname if dbname else DB_NAME
    return psycopg2.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        database=target,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=10,
    )
