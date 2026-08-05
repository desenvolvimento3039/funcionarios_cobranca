from typing import List, Dict, Any
from app.domain.repositories import IAuditoriaRepository

class AuditoriaService:
    """Serviço responsável por registros e consultas de auditoria do sistema."""

    def __init__(self, auditoria_repo: IAuditoriaRepository):
        self.auditoria_repo = auditoria_repo

    def listar_historico(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.auditoria_repo.list_historico(limit)
