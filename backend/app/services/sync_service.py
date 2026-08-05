from typing import List, Dict, Any, Union
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.repositories.cobranca_repository import SQLCobrancaRepository
from app.infrastructure.repositories.financiamento_repository import SQLFinanciamentoRepository
from app.application.services.sync_use_cases import SyncService

def parse_excel_cobranca_bytes(file_bytes=None, file_path=None):
    db = SessionLocal()
    try:
        svc = SyncService(SQLCobrancaRepository(db), SQLFinanciamentoRepository(db))
        return svc.parse_excel_cobranca(file_bytes=file_bytes, file_path=file_path)
    finally:
        db.close()

def sync_cobranca_rows_to_dbs(rows: List[tuple], target_dbs=None) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        svc = SyncService(SQLCobrancaRepository(db), SQLFinanciamentoRepository(db))
        return svc.sync_cobranca_rows(rows)
    finally:
        db.close()
