import os
from typing import List, Dict, Any, Union
from app.domain.entities import FuncionarioCobranca
from app.domain.repositories import ICobrancaRepository, IFinanciamentoRepository
from app.infrastructure.utils.excel_utils import parse_excel_bytes_or_path, parse_financiamento_excel_bytes_or_path

class SyncService:
    def __init__(
        self,
        cobranca_repo: ICobrancaRepository,
        financiamento_repo: IFinanciamentoRepository
    ):
        self.cobranca_repo = cobranca_repo
        self.financiamento_repo = financiamento_repo

    def parse_excel_cobranca(self, file_bytes: Union[bytes, None] = None, file_path: Union[str, None] = None):
        return parse_excel_bytes_or_path(file_bytes=file_bytes, file_path=file_path)

    def sync_cobranca_rows(self, rows: List[tuple]) -> Dict[str, Any]:
        if not rows:
            return {"inserted": 0, "total": 0}

        entities = [
            FuncionarioCobranca(
                times_cobranca=r[0] or "",
                num_pa=r[1] or 0,
                matricula=r[2] or 0,
                cobrador=r[3] or "",
                fila=r[4] or "",
                telefone=r[5] if len(r) > 5 else "",
                status=1
            ) for r in rows
        ]
        created = self.cobranca_repo.create_batch(entities)
        return {"inserted": len(created), "total": len(rows)}

    def parse_excel_financiamento(self, file_bytes: Union[bytes, None] = None, file_path: Union[str, None] = None):
        return parse_financiamento_excel_bytes_or_path(file_bytes=file_bytes, file_path=file_path)

    def sync_financiamento_rows(self, rows: List[tuple]) -> Dict[str, Any]:
        return self.financiamento_repo.sync_data_rows(rows)
