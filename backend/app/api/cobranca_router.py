import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Response, UploadFile, File, Query, Depends
from app.application.dto.schemas import (
    CobrancaCreate, CobrancaResponse, StatusUpdate, SubstituicaoEdit, 
    SubstituicaoDirectCreate, TrocaMassaRequest, BulkUpdateRequest,
    SubstituicaoMassaRequest
)
from app.application.services.funcionario_service import FuncionarioService
from app.application.services.substituicao_use_cases import SubstituicaoService
from app.application.services.time_service import TimeService
from app.application.services.auditoria_service import AuditoriaService
from app.application.services.export_service import ExportService
from app.application.services.sync_use_cases import SyncService
from app.api.dependencies import (
    get_funcionario_service, get_substituicao_service, get_time_service,
    get_auditoria_service, get_export_service, get_sync_service
)
from app.infrastructure.database.connection import get_psycopg2_conn
from app.core.config import DB_NAME, DB_HOST, DB_PORT, DB_USER

router = APIRouter(prefix="/api/cobranca", tags=["Funcionários de Cobrança"])

EXCEL_LOCAL_PATHS = [
    "/app/funcionarios_cobranca.xlsx",
    "/home/desenvolvimento/funcionarios_cobranca.xlsx",
    "funcionarios_cobranca.xlsx"
]

@router.get("/pas")
def listar_pas(service: TimeService = Depends(get_time_service)):
    return service.listar_pas()

@router.get("/funcionarios-busca")
def buscar_funcionarios(
    q: Optional[str] = Query(None),
    service: FuncionarioService = Depends(get_funcionario_service)
):
    return service.buscar_funcionarios(q)

@router.get("/stats")
def estatisticas_analytics(service: TimeService = Depends(get_time_service)):
    return service.estatisticas_analytics()

@router.get("")
def listar_cobranca(
    page: Optional[int] = Query(None),
    per_page: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    time_cobranca: Optional[str] = Query(None),
    pa: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    substituicao: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("desc"),
    service: FuncionarioService = Depends(get_funcionario_service)
):
    return service.listar_cobranca(page, per_page, search, time_cobranca, pa, status, substituicao, sort_by, sort_order)

@router.get("/substituicoes")
def listar_substituicoes_escala(service: SubstituicaoService = Depends(get_substituicao_service)):
    return service.listar_escala()

@router.get("/health")
def health_check():
    try:
        conn = get_psycopg2_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "healthy", "databases": {DB_NAME: "ok"}}
    except Exception as e:
        return {"status": "degraded", "databases": {DB_NAME: f"ERRO: {str(e)}"}}

@router.get("/debug-db")
def debug_db():
    import traceback
    response_data = {
        "config": {"DB_HOST": DB_HOST, "DB_PORT": DB_PORT, "DB_USER": DB_USER, "DB_NAME": DB_NAME},
        "connected": False, "database_info": None, "tables_found": [], "row_counts": {}, "error_details": None
    }
    try:
        conn = get_psycopg2_conn()
        cur = conn.cursor()
        cur.execute("SELECT current_database(), current_user, version();")
        db_info = cur.fetchone()
        response_data["connected"] = True
        response_data["database_info"] = {"current_database": db_info[0], "current_user": db_info[1], "pg_version": db_info[2]}
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
        tables = [r[0] for r in cur.fetchall()]
        response_data["tables_found"] = tables
        counts = {}
        for table in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{table}";')
                counts[table] = cur.fetchone()[0]
            except Exception as te:
                counts[table] = f"Erro ao contar: {str(te)}"
        response_data["row_counts"] = counts
        cur.close()
        conn.close()
    except Exception as e:
        response_data["connected"] = False
        response_data["error_details"] = {"message": str(e), "error_type": type(e).__name__, "traceback": traceback.format_exc()}
    return response_data

@router.post("", response_model=CobrancaResponse, status_code=status.HTTP_201_CREATED)
def criar_cobranca(data: CobrancaCreate, service: FuncionarioService = Depends(get_funcionario_service)):
    try:
        return service.criar_funcionario(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao criar funcionário: {str(e)}")

@router.patch("/{id}/status", response_model=CobrancaResponse)
@router.put("/{id}/status", response_model=CobrancaResponse)
def alterar_status(id: int, data: StatusUpdate, service: FuncionarioService = Depends(get_funcionario_service)):
    try:
        atualizado = service.alterar_status(id, data.status)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        return atualizado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao alterar status: {str(e)}")

@router.put("/{id}", response_model=CobrancaResponse)
def atualizar_cobranca(id: int, data: CobrancaCreate, service: FuncionarioService = Depends(get_funcionario_service)):
    try:
        atualizado = service.atualizar_funcionario(id, data)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        return atualizado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao atualizar funcionário: {str(e)}")

@router.delete("/{id}")
def deletar_cobranca(id: int, service: FuncionarioService = Depends(get_funcionario_service)):
    try:
        sucesso = service.deletar_funcionario(id)
        if sucesso:
            return {"message": "Funcionário excluído com sucesso"}
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao deletar funcionário: {str(e)}")

@router.put("/substituicao/{id}")
def editar_substituicao(
    id: int,
    data: SubstituicaoEdit,
    service: SubstituicaoService = Depends(get_substituicao_service)
):
    try:
        atualizado = service.atualizar_datas(id, data.data_inicio, data.data_fim)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Substituição não encontrada")
        return atualizado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao atualizar datas de substituição: {str(e)}")

@router.get("/filas-sem-cobradores")
def get_filas_sem_cobradores(service: FuncionarioService = Depends(get_funcionario_service)):
    try:
        return service.listar_filas_sem_cobradores()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar filas sem cobradores: {str(e)}")

@router.post("/substituicao")
def criar_substituicao(
    data: SubstituicaoDirectCreate,
    service: SubstituicaoService = Depends(get_substituicao_service)
):
    try:
        return service.criar_direta(data.substituto_id, data.original_id, data.data_inicio, data.data_fim)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao criar substituição: {str(e)}")

@router.post("/substituicao-massa")
def criar_substituicao_massa(
    data: SubstituicaoMassaRequest,
    service: SubstituicaoService = Depends(get_substituicao_service)
):
    try:
        return service.substituicao_massa(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao realizar substituição em massa: {str(e)}")

@router.post("/troca-massa")
def troca_massa(data: TrocaMassaRequest, service: TimeService = Depends(get_time_service)):
    try:
        return service.troca_massa(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao realizar troca em massa: {str(e)}")

@router.post("/bulk-update")
def bulk_update(data: BulkUpdateRequest, service: FuncionarioService = Depends(get_funcionario_service)):
    try:
        return service.bulk_update(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao realizar atualização em lote: {str(e)}")

@router.get("/historico-auditoria")
def historico_auditoria(service: AuditoriaService = Depends(get_auditoria_service)):
    try:
        return service.listar_historico()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao obter histórico de auditoria: {str(e)}")

@router.post("/sincronizar")
def sincronizar_banco(
    func_service: FuncionarioService = Depends(get_funcionario_service),
    sync_service: SyncService = Depends(get_sync_service)
):
    excel_path = next((p for p in EXCEL_LOCAL_PATHS if os.path.exists(p)), None)
    try:
        if excel_path:
            rows = sync_service.parse_excel_cobranca(file_path=excel_path)
            stats = sync_service.sync_cobranca_rows(rows)
            return {"status": "success", "message": f"{len(rows)} registros processados!", "detalhes": stats}
        else:
            rows_data = func_service.listar_cobranca(page=None, per_page=None)
            rows = [(r["times_cobranca"], r["num_pa"], r["matricula"], r["cobrador"], r["fila"], r["telefone"]) for r in rows_data]
            stats = sync_service.sync_cobranca_rows(rows)
            return {"status": "success", "message": "Sincronização banco-a-banco concluída!", "detalhes": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha na sincronização: {str(e)}")

@router.post("/upload")
async def upload_excel(
    file: UploadFile = File(...),
    sync_service: SyncService = Depends(get_sync_service)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Apenas arquivos Excel são permitidos.")
    try:
        content = await file.read()
        rows = sync_service.parse_excel_cobranca(file_bytes=content)
        stats = sync_service.sync_cobranca_rows(rows)
        return {"status": "success", "message": f"{len(rows)} registros processados!", "detalhes": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha no upload: {str(e)}")

@router.delete("/substituicao/{id}")
@router.post("/substituicao/{id}/cancelar")
def cancelar_substituicao(id: int, service: SubstituicaoService = Depends(get_substituicao_service)):
    try:
        sucesso = service.cancelar(id)
        if sucesso:
            return {"message": "Substituição cancelada com sucesso"}
        raise HTTPException(status_code=404, detail="Substituição não encontrada")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao cancelar substituição: {str(e)}")

@router.get("/modelo-excel")
def baixar_modelo_excel(service: ExportService = Depends(get_export_service)):
    try:
        content = service.gerar_modelo_excel()
        return Response(
            content=content.encode("utf-8-sig"),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=modelo_importacao_cobranca.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao gerar modelo Excel: {str(e)}")

@router.get("/exportar")
def exportar_csv(service: ExportService = Depends(get_export_service)):
    try:
        csv_data = service.exportar_csv()
        return Response(
            content=csv_data.encode("utf-8-sig"),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=fun_funcionarios_cobranca.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao exportar funcionários: {str(e)}")
