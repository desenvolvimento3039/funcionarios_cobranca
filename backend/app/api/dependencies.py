from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.cobranca_repository import SQLCobrancaRepository
from app.infrastructure.repositories.substituicao_repository import SQLSubstituicaoRepository
from app.infrastructure.repositories.auditoria_repository import SQLAuditoriaRepository
from app.infrastructure.repositories.financiamento_repository import SQLFinanciamentoRepository

from app.application.services.funcionario_service import FuncionarioService
from app.application.services.substituicao_use_cases import SubstituicaoService
from app.application.services.time_service import TimeService
from app.application.services.auditoria_service import AuditoriaService
from app.application.services.export_service import ExportService
from app.application.services.financiamento_use_cases import FinanciamentoService
from app.application.services.sync_use_cases import SyncService

def get_cobranca_repo(db: Session = Depends(get_db)) -> SQLCobrancaRepository:
    return SQLCobrancaRepository(db)

def get_substituicao_repo(db: Session = Depends(get_db)) -> SQLSubstituicaoRepository:
    return SQLSubstituicaoRepository(db)

def get_auditoria_repo(db: Session = Depends(get_db)) -> SQLAuditoriaRepository:
    return SQLAuditoriaRepository(db)

def get_financiamento_repo(db: Session = Depends(get_db)) -> SQLFinanciamentoRepository:
    return SQLFinanciamentoRepository(db)

def get_funcionario_service(
    c_repo: SQLCobrancaRepository = Depends(get_cobranca_repo),
    s_repo: SQLSubstituicaoRepository = Depends(get_substituicao_repo),
    a_repo: SQLAuditoriaRepository = Depends(get_auditoria_repo)
) -> FuncionarioService:
    return FuncionarioService(c_repo, s_repo, a_repo)

def get_substituicao_service(
    s_repo: SQLSubstituicaoRepository = Depends(get_substituicao_repo),
    c_repo: SQLCobrancaRepository = Depends(get_cobranca_repo),
    a_repo: SQLAuditoriaRepository = Depends(get_auditoria_repo)
) -> SubstituicaoService:
    return SubstituicaoService(s_repo, c_repo, a_repo)

def get_time_service(
    c_repo: SQLCobrancaRepository = Depends(get_cobranca_repo),
    a_repo: SQLAuditoriaRepository = Depends(get_auditoria_repo)
) -> TimeService:
    return TimeService(c_repo, a_repo)

def get_auditoria_service(
    a_repo: SQLAuditoriaRepository = Depends(get_auditoria_repo)
) -> AuditoriaService:
    return AuditoriaService(a_repo)

def get_export_service(
    c_repo: SQLCobrancaRepository = Depends(get_cobranca_repo)
) -> ExportService:
    return ExportService(c_repo)

def get_financiamento_service(
    f_repo: SQLFinanciamentoRepository = Depends(get_financiamento_repo)
) -> FinanciamentoService:
    return FinanciamentoService(f_repo)

def get_sync_service(
    c_repo: SQLCobrancaRepository = Depends(get_cobranca_repo),
    f_repo: SQLFinanciamentoRepository = Depends(get_financiamento_repo)
) -> SyncService:
    return SyncService(c_repo, f_repo)

# Alias de compatibilidade
def get_cobranca_service(
    c_repo: SQLCobrancaRepository = Depends(get_cobranca_repo),
    s_repo: SQLSubstituicaoRepository = Depends(get_substituicao_repo),
    a_repo: SQLAuditoriaRepository = Depends(get_auditoria_repo)
) -> FuncionarioService:
    return FuncionarioService(c_repo, s_repo, a_repo)
