from typing import Optional, List, Dict, Any, Union
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.repositories.cobranca_repository import SQLCobrancaRepository
from app.infrastructure.repositories.substituicao_repository import SQLSubstituicaoRepository
from app.infrastructure.repositories.auditoria_repository import SQLAuditoriaRepository
from app.application.services.cobranca_use_cases import CobrancaService
from app.application.services.substituicao_use_cases import SubstituicaoService
from app.application.dto.schemas import (
    CobrancaCreate, TrocaMassaRequest, BulkUpdateRequest, SubstituicaoMassaRequest
)

def _get_services():
    db = SessionLocal()
    c_repo = SQLCobrancaRepository(db)
    s_repo = SQLSubstituicaoRepository(db)
    a_repo = SQLAuditoriaRepository(db)
    return (
        CobrancaService(c_repo, s_repo, a_repo),
        SubstituicaoService(s_repo, c_repo, a_repo),
        db
    )

def listar_pas() -> List[Dict[str, Any]]:
    c_svc, _, db = _get_services()
    try:
        return c_svc.listar_pas()
    finally:
        db.close()

def buscar_funcionarios(q: Optional[str] = None) -> List[Dict[str, Any]]:
    c_svc, _, db = _get_services()
    try:
        return c_svc.buscar_funcionarios(q)
    finally:
        db.close()

def estatisticas_analytics() -> Dict[str, Any]:
    c_svc, _, db = _get_services()
    try:
        return c_svc.estatisticas_analytics()
    finally:
        db.close()

def listar_cobranca(
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    search: Optional[str] = None,
    time_cobranca: Optional[str] = None,
    pa: Optional[int] = None,
    status: Optional[int] = None,
    substituicao: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc"
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    c_svc, _, db = _get_services()
    try:
        return c_svc.listar_cobranca(page, per_page, search, time_cobranca, pa, status, substituicao, sort_by, sort_order)
    finally:
        db.close()

def listar_substituicoes_escala() -> List[Dict[str, Any]]:
    _, s_svc, db = _get_services()
    try:
        return s_svc.listar_escala()
    finally:
        db.close()

def criar_cobranca(data: CobrancaCreate):
    c_svc, _, db = _get_services()
    try:
        return c_svc.criar_cobranca(data)
    finally:
        db.close()

def alterar_status(cobranca_id: int, new_status: int):
    c_svc, _, db = _get_services()
    try:
        return c_svc.alterar_status(cobranca_id, new_status)
    finally:
        db.close()

def atualizar_cobranca(cobranca_id: int, data: CobrancaCreate):
    c_svc, _, db = _get_services()
    try:
        return c_svc.atualizar_cobranca(cobranca_id, data)
    finally:
        db.close()

def deletar_cobranca(cobranca_id: int) -> bool:
    c_svc, _, db = _get_services()
    try:
        return c_svc.deletar_cobranca(cobranca_id)
    finally:
        db.close()

def atualizar_datas_substituicao(id: int, data_inicio, data_fim):
    _, s_svc, db = _get_services()
    try:
        return s_svc.atualizar_datas(id, data_inicio, data_fim)
    finally:
        db.close()

def listar_filas_sem_cobradores():
    c_svc, _, db = _get_services()
    try:
        return c_svc.listar_filas_sem_cobradores()
    finally:
        db.close()

def criar_substituicao_direta(substituto_id: int, original_id: int, data_inicio, data_fim):
    _, s_svc, db = _get_services()
    try:
        return s_svc.criar_direta(substituto_id, original_id, data_inicio, data_fim)
    finally:
        db.close()

def substituicao_massa_service(data: SubstituicaoMassaRequest):
    _, s_svc, db = _get_services()
    try:
        return s_svc.substituicao_massa(data)
    finally:
        db.close()

def troca_massa_service(data: TrocaMassaRequest):
    c_svc, _, db = _get_services()
    try:
        return c_svc.troca_massa(data)
    finally:
        db.close()

def bulk_update_service(data: BulkUpdateRequest):
    c_svc, _, db = _get_services()
    try:
        return c_svc.bulk_update(data)
    finally:
        db.close()

def listar_historico_auditoria():
    c_svc, _, db = _get_services()
    try:
        return c_svc.listar_historico_auditoria()
    finally:
        db.close()

def cancelar_substituicao_service(id: int) -> bool:
    _, s_svc, db = _get_services()
    try:
        return s_svc.cancelar(id)
    finally:
        db.close()

def gerar_modelo_excel_service():
    c_svc, _, db = _get_services()
    try:
        return c_svc.gerar_modelo_excel()
    finally:
        db.close()

def exportar_csv_service():
    c_svc, _, db = _get_services()
    try:
        return c_svc.exportar_csv()
    finally:
        db.close()
