from app.domain.repositories import ICobrancaRepository
from app.infrastructure.utils.excel_utils import generate_csv_cobranca, generate_csv_model_cobranca

class ExportService:
    """Serviço responsável por exportações de relatórios e modelos em CSV/Excel."""

    def __init__(self, cobranca_repo: ICobrancaRepository):
        self.cobranca_repo = cobranca_repo

    def exportar_csv(self) -> str:
        rows, _ = self.cobranca_repo.list_paginated(None, None, None, None, None, None, None, "id", "desc")
        return generate_csv_cobranca(rows)

    def gerar_modelo_excel(self) -> str:
        return generate_csv_model_cobranca()
