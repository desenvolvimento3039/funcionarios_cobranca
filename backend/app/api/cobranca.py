import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Response, UploadFile, File, Query
from app.models.schemas import CobrancaCreate, CobrancaResponse, StatusUpdate, SubstituicaoEdit, HistoricoSubstituicaoResponse, SubstituicaoDirectCreate
from app.services import cobranca_service, sync_service
from app.core.database import get_psycopg2_conn

router = APIRouter(prefix="/api/cobranca", tags=["Funcionários de Cobrança"])

EXCEL_LOCAL_PATHS = [
    "/app/funcionarios_cobranca.xlsx",
    "/home/desenvolvimento/funcionarios_cobranca.xlsx",
    "funcionarios_cobranca.xlsx"
]

@router.get("/pas")
def listar_pas():
    return cobranca_service.listar_pas()

@router.get("/funcionarios-busca")
def buscar_funcionarios(q: Optional[str] = Query(None)):
    return cobranca_service.buscar_funcionarios(q)

@router.get("/stats")
def estatisticas_analytics():
    return cobranca_service.estatisticas_analytics()

@router.get("")
def listar_cobranca(
    page: Optional[int] = Query(None),
    per_page: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    time_cobranca: Optional[str] = Query(None),
    pa: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("desc")
):
    return cobranca_service.listar_cobranca(page, per_page, search, time_cobranca, pa, status, sort_by, sort_order)

@router.get("/health")
def health_check():
    status_dbs = {}
    for dbname in ["SicoobSMO", "LeCom"]:
        try:
            conn = get_psycopg2_conn(dbname)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            status_dbs[dbname] = "ok"
        except Exception as e:
            status_dbs[dbname] = f"ERRO: {str(e)}"
    all_ok = all(v == "ok" for v in status_dbs.values())
    return {
        "status": "healthy" if all_ok else "degraded",
        "databases": status_dbs
    }

@router.post("", response_model=CobrancaResponse, status_code=status.HTTP_201_CREATED)
def criar_cobranca(data: CobrancaCreate):
    try:
        novo = cobranca_service.criar_cobranca(data)
        if novo:
            return novo
        raise HTTPException(status_code=500, detail="Erro interno ao criar")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao criar funcionário: {str(e)}")

@router.patch("/{id}/status", response_model=CobrancaResponse)
@router.put("/{id}/status", response_model=CobrancaResponse)
def alterar_status(id: int, data: StatusUpdate):
    try:
        atualizado = cobranca_service.alterar_status(id, data.status)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        return atualizado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao alterar status: {str(e)}")

@router.put("/{id}", response_model=CobrancaResponse)
def atualizar_cobranca(id: int, data: CobrancaCreate):
    try:
        atualizado = cobranca_service.atualizar_cobranca(id, data)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        return atualizado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao atualizar funcionário: {str(e)}")

@router.delete("/{id}")
def deletar_cobranca(id: int):
    try:
        sucesso = cobranca_service.deletar_cobranca(id)
        if sucesso:
            return {"message": "Funcionário excluído com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao deletar funcionário: {str(e)}")

@router.put("/substituicao/{id}")
def editar_substituicao(id: int, data: SubstituicaoEdit):
    try:
        atualizado = cobranca_service.atualizar_datas_substituicao(id, data.data_inicio, data.data_fim)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Substituição não encontrada")
        return atualizado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao atualizar datas de substituição: {str(e)}")

@router.get("/filas-sem-cobradores")
def get_filas_sem_cobradores():
    try:
        return cobranca_service.listar_filas_sem_cobradores()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar filas sem cobradores: {str(e)}")

@router.post("/substituicao")
def criar_substituicao(data: SubstituicaoDirectCreate):
    try:
        novo = cobranca_service.criar_substituicao_direta(data.substituto_id, data.original_id, data.data_inicio, data.data_fim)
        if novo:
            return novo
        raise HTTPException(status_code=500, detail="Erro interno ao criar substituição")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao criar substituição: {str(e)}")

@router.post("/sincronizar")
def sincronizar_banco():
    excel_path = next((p for p in EXCEL_LOCAL_PATHS if os.path.exists(p)), None)
    try:
        if excel_path:
            rows = sync_service.parse_excel_cobranca_bytes(file_path=excel_path)
            stats = sync_service.sync_cobranca_rows_to_dbs(rows)
            return {"status": "success", "message": f"{len(rows)} registros processados!", "detalhes": stats}
        else:
            from app.core.database import get_engine
            from sqlalchemy import text
            engine = get_engine("SicoobSMO")
            with engine.connect() as conn:
                res = conn.execute(text("SELECT times_cobranca, num_pa, matricula, cobrador, fila, COALESCE(telefone, '') as telefone FROM public.fun_funcionarios_cobranca"))
                rows = [tuple(r) for r in res.fetchall()]
            stats = sync_service.sync_cobranca_rows_to_dbs(rows)
            return {"status": "success", "message": "Sincronização banco-a-banco concluída!", "detalhes": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha na sincronização: {str(e)}")

@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Apenas arquivos Excel são permitidos.")
    try:
        content = await file.read()
        rows = sync_service.parse_excel_cobranca_bytes(file_bytes=content)
        stats = sync_service.sync_cobranca_rows_to_dbs(rows)
        return {"status": "success", "message": f"{len(rows)} registros processados!", "detalhes": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha no upload: {str(e)}")

@router.get("/exportar")
def exportar_csv():
    try:
        csv_data = cobranca_service.exportar_csv_service()
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=fun_funcionarios_cobranca.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Falha ao exportar funcionários")
