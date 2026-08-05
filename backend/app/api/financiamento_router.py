import os
import io
from typing import List
from fastapi import APIRouter, HTTPException, status, Response, UploadFile, File, Depends
from app.application.dto.schemas import FinanciamentoCreate, FinanciamentoResponse, StatusUpdate
from app.application.services.financiamento_use_cases import FinanciamentoService
from app.application.services.sync_use_cases import SyncService
from app.api.dependencies import get_financiamento_service, get_sync_service
from app.infrastructure.database.connection import get_psycopg2_conn

router = APIRouter(prefix="/api/financiamento", tags=["Financiamento Rural"])

EXCEL_LOCAL_PATHS = [
    "/app/itens_financiaveis/Lista de itens financiados.xlsx",
    "/home/desenvolvimento/itens_financiaveis/Lista de itens financiados.xlsx",
    "/mnt/c/Users/desenvolvimento/OneDrive - Sicoob/Documentos/SUBPROGRAMAS LECOM.xlsx"
]

@router.get("", response_model=List[FinanciamentoResponse])
def listar_financiamento_rural(service: FinanciamentoService = Depends(get_financiamento_service)):
    try:
        return service.listar_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao buscar itens financiáveis: {str(e)}")

@router.get("/health")
def health_check():
    status_dbs = {}
    for dbname in ["SicoobSMO"]:
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

@router.post("", response_model=FinanciamentoResponse, status_code=status.HTTP_201_CREATED)
def criar_item_financiamento(
    data: FinanciamentoCreate,
    service: FinanciamentoService = Depends(get_financiamento_service)
):
    try:
        return service.criar(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao criar item: {str(e)}")

@router.patch("/{id}/status", response_model=FinanciamentoResponse)
@router.put("/{id}/status", response_model=FinanciamentoResponse)
def alterar_status_item(
    id: int,
    data: StatusUpdate,
    service: FinanciamentoService = Depends(get_financiamento_service)
):
    try:
        atualizado = service.alterar_status(id, data.status)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        return atualizado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao alterar status do item: {str(e)}")

@router.put("/{id}", response_model=FinanciamentoResponse)
def atualizar_item_financiamento(
    id: int,
    data: FinanciamentoCreate,
    service: FinanciamentoService = Depends(get_financiamento_service)
):
    try:
        atualizado = service.atualizar(id, data)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        return atualizado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao atualizar item: {str(e)}")

@router.delete("/{id}")
def deletar_item_financiamento(id: int, service: FinanciamentoService = Depends(get_financiamento_service)):
    try:
        sucesso = service.deletar(id)
        if sucesso:
            return {"message": "Item excluído com sucesso"}
        raise HTTPException(status_code=404, detail="Item não encontrado")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao deletar item: {str(e)}")

@router.post("/sincronizar-lecom")
@router.post("/sincronizar")
def sincronizar_banco_lecom(
    service: FinanciamentoService = Depends(get_financiamento_service),
    s_service: SyncService = Depends(get_sync_service)
):
    excel_path = next((p for p in EXCEL_LOCAL_PATHS if os.path.exists(p)), None)
    try:
        if excel_path:
            rows = s_service.parse_excel_financiamento(file_path=excel_path)
            stats = s_service.sync_financiamento_rows(rows)
            return {"status": "success", "message": "Informações processadas e inseridas com sucesso!", "detalhes": stats}
        else:
            items = service.listar_todos()
            rows = [(i["item"], i["enquadramento"], i["linha"], i["isolado"]) for i in items]
            stats = s_service.sync_financiamento_rows(rows)
            return {"status": "success", "message": "Informações processadas e inseridas com sucesso!", "detalhes": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha na sincronização: {str(e)}")

@router.post("/upload")
async def upload_excel_file(
    file: UploadFile = File(...),
    s_service: SyncService = Depends(get_sync_service)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Apenas arquivos no formato Excel (.xlsx) são permitidos.")
    try:
        content = await file.read()
        rows = s_service.parse_excel_financiamento(file_bytes=content)
        stats = s_service.sync_financiamento_rows(rows)
        return {"status": "success", "message": "Informações processadas e inseridas com sucesso!", "detalhes": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha no upload: {str(e)}")

@router.get("/exportar")
def exportar_financiamento_csv(service: FinanciamentoService = Depends(get_financiamento_service)):
    try:
        csv_data = service.exportar_csv()
        return Response(
            content=csv_data.encode("utf-8-sig"),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=financiamento_rural.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Falha ao exportar financiamento rural")
