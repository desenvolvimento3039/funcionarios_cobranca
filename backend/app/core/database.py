import urllib.parse
from typing import Dict, Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import psycopg2
from app.core.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

engines: Dict[str, Any] = {}
session_makers: Dict[str, sessionmaker] = {}

def get_engine(dbname: str = None):
    target_db = dbname if dbname else DB_NAME
    if target_db not in engines:
        encoded_pass = urllib.parse.quote_plus(DB_PASSWORD)
        url = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{target_db}"
        engines[target_db] = create_engine(
            url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=1800
        )
        session_makers[target_db] = sessionmaker(autocommit=False, autoflush=False, bind=engines[target_db])
    return engines[target_db]

def get_db(dbname: str = None) -> Generator[Session, None, None]:
    """Dependência para injeção de sessão do SQLAlchemy no FastAPI."""
    engine = get_engine(dbname)
    target_db = dbname if dbname else DB_NAME
    SessionLocal = session_makers[target_db]
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_psycopg2_conn(dbname: str = None):
    target_db = dbname if dbname else DB_NAME
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=target_db,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=10
    )
