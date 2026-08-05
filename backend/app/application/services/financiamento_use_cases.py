import csv
import io
from typing import List, Optional, Dict, Any
from app.domain.entities import FinanciamentoRural
from app.domain.repositories import IFinanciamentoRepository
from app.application.dto.schemas import FinanciamentoCreate

class FinanciamentoService:
    def __init__(self, repo: IFinanciamentoRepository):
        self.repo = repo

    def listar_todos(self) -> List[Dict[str, Any]]:
        items = self.repo.list_all()
        return [
            {
                "id": i.id,
                "item": i.item,
                "enquadramento": i.enquadramento,
                "linha": i.linha,
                "isolado": i.isolado,
                "status": i.status
            } for i in items
        ]

    def criar(self, data: FinanciamentoCreate) -> Dict[str, Any]:
        entity = FinanciamentoRural(
            item=data.item,
            enquadramento=data.enquadramento or "",
            linha=data.linha or "",
            isolado=data.isolado or "Não",
            status=1 if data.status is None else data.status
        )
        created = self.repo.create(entity)
        return {
            "id": created.id,
            "item": created.item,
            "enquadramento": created.enquadramento,
            "linha": created.linha,
            "isolado": created.isolado,
            "status": created.status
        }

    def atualizar(self, id: int, data: FinanciamentoCreate) -> Optional[Dict[str, Any]]:
        entity = FinanciamentoRural(
            id=id,
            item=data.item,
            enquadramento=data.enquadramento or "",
            linha=data.linha or "",
            isolado=data.isolado or "Não",
            status=1 if data.status is None else data.status
        )
        updated = self.repo.update(entity)
        if not updated:
            return None
        return {
            "id": updated.id,
            "item": updated.item,
            "enquadramento": updated.enquadramento,
            "linha": updated.linha,
            "isolado": updated.isolado,
            "status": updated.status
        }

    def alterar_status(self, id: int, new_status: int) -> Optional[Dict[str, Any]]:
        status_val = 1 if new_status == 1 else 0
        updated = self.repo.update_status(id, status_val)
        if not updated:
            return None
        return {
            "id": updated.id,
            "item": updated.item,
            "enquadramento": updated.enquadramento,
            "linha": updated.linha,
            "isolado": updated.isolado,
            "status": updated.status
        }

    def deletar(self, id: int) -> bool:
        return self.repo.delete(id)

    def sincronizar_linhas(self, rows: List[tuple]) -> Dict[str, Any]:
        return self.repo.sync_data_rows(rows)

    def exportar_csv(self) -> str:
        items = self.repo.list_all()
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(["ID", "Item Financiável", "Enquadramento / Programa", "Linha de Crédito", "Isolado", "Status"])
        for i in items:
            status_txt = "Ativo" if i.status == 1 else "Inativo"
            writer.writerow([i.id, i.item, i.enquadramento, i.linha, i.isolado, status_txt])
        return output.getvalue()
