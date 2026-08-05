# Re-exporting schemas from Application DTO package for backwards compatibility
from app.application.dto.schemas import (
    CobrancaBase,
    CobrancaCreate,
    CobrancaResponse,
    StatusUpdate,
    SubstituicaoEdit,
    SubstituicaoDirectCreate,
    HistoricoSubstituicaoResponse,
    TrocaMassaRequest,
    BulkUpdateRequest,
    SubstituicaoMassaRequest,
    FinanciamentoBase,
    FinanciamentoCreate,
    FinanciamentoResponse,
)

__all__ = [
    "CobrancaBase",
    "CobrancaCreate",
    "CobrancaResponse",
    "StatusUpdate",
    "SubstituicaoEdit",
    "SubstituicaoDirectCreate",
    "HistoricoSubstituicaoResponse",
    "TrocaMassaRequest",
    "BulkUpdateRequest",
    "SubstituicaoMassaRequest",
    "FinanciamentoBase",
    "FinanciamentoCreate",
    "FinanciamentoResponse",
]
