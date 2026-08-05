from typing import List, Optional, Dict, Any, Union
from app.domain.entities import FuncionarioCobranca, Substituicao
from app.domain.repositories import ICobrancaRepository, ISubstituicaoRepository, IAuditoriaRepository
from app.application.dto.schemas import CobrancaCreate, BulkUpdateRequest
from app.domain.entities import AuditoriaTroca

class FuncionarioService:
    """Serviço responsável exclusivamente pela gestão de funcionários de cobrança."""
    
    def __init__(
        self,
        cobranca_repo: ICobrancaRepository,
        substituicao_repo: ISubstituicaoRepository,
        auditoria_repo: IAuditoriaRepository
    ):
        self.cobranca_repo = cobranca_repo
        self.substituicao_repo = substituicao_repo
        self.auditoria_repo = auditoria_repo

    def buscar_funcionarios(self, query: Optional[str]) -> List[Dict[str, Any]]:
        return self.cobranca_repo.search_funcionarios(query)

    def listar_cobranca(
        self,
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
        formatted_rows, total_records = self.cobranca_repo.list_paginated(
            page, per_page, search, time_cobranca, pa, status, substituicao, sort_by, sort_order
        )
        if page and per_page and page > 0 and per_page > 0:
            import math
            total_pages = math.ceil(total_records / per_page) if per_page > 0 else 1
            return {
                "items": formatted_rows,
                "total": total_records,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages
            }
        return formatted_rows

    def criar_funcionario(self, data: CobrancaCreate) -> Dict[str, Any]:
        pas_para_criar = data.num_pas if (data.num_pas and len(data.num_pas) > 0) else [data.num_pa or 0]
        entities = [
            FuncionarioCobranca(
                times_cobranca=data.times_cobranca,
                num_pa=pa_id,
                matricula=data.matricula,
                cobrador=data.cobrador,
                fila=data.fila,
                telefone=data.telefone or "",
                status=data.status if data.status is not None else 1
            ) for pa_id in pas_para_criar
        ]
        created = self.cobranca_repo.create_batch(entities)
        primeiro = created[0] if created else None
        res_dict = {
            "id": primeiro.id if primeiro else 0,
            "times_cobranca": data.times_cobranca,
            "num_pa": data.num_pa,
            "matricula": data.matricula,
            "cobrador": data.cobrador,
            "fila": data.fila,
            "telefone": data.telefone,
            "status": data.status if data.status is not None else 1,
            "substituto_de_id": None
        }

        if data.is_substituto and data.substituto_de_id and data.data_inicio_substituicao and data.data_fim_substituicao:
            sub = Substituicao(
                substituto_id=primeiro.id,
                original_id=data.substituto_de_id,
                data_inicio=data.data_inicio_substituicao,
                data_fim=data.data_fim_substituicao
            )
            self.substituicao_repo.create(sub)
            res_dict["substituto_de_id"] = data.substituto_de_id

        return res_dict

    def alterar_status(self, cobranca_id: int, new_status: int) -> Optional[Dict[str, Any]]:
        updated = self.cobranca_repo.update_status(cobranca_id, new_status)
        if not updated:
            return None
        return {
            "id": updated.id,
            "times_cobranca": updated.times_cobranca,
            "num_pa": updated.num_pa,
            "matricula": updated.matricula,
            "cobrador": updated.cobrador,
            "fila": updated.fila,
            "telefone": updated.telefone,
            "status": updated.status
        }

    def atualizar_funcionario(self, cobranca_id: int, data: CobrancaCreate) -> Optional[Dict[str, Any]]:
        entity = FuncionarioCobranca(
            id=cobranca_id,
            times_cobranca=data.times_cobranca,
            num_pa=data.num_pa or 0,
            matricula=data.matricula,
            cobrador=data.cobrador,
            fila=data.fila,
            telefone=data.telefone or "",
            status=data.status if data.status is not None else 1
        )
        updated = self.cobranca_repo.update(entity)
        if not updated:
            return None
        return {
            "id": updated.id,
            "times_cobranca": updated.times_cobranca,
            "num_pa": updated.num_pa,
            "matricula": updated.matricula,
            "cobrador": updated.cobrador,
            "fila": updated.fila,
            "telefone": updated.telefone,
            "status": updated.status
        }

    def deletar_funcionario(self, cobranca_id: int) -> bool:
        return self.cobranca_repo.delete(cobranca_id)

    def listar_filas_sem_cobradores(self) -> List[Dict[str, Any]]:
        return self.cobranca_repo.list_filas_sem_cobradores()

    def bulk_update(self, data: BulkUpdateRequest) -> Dict[str, Any]:
        updates = {}
        if data.novo_cobrador is not None: updates["cobrador"] = data.novo_cobrador
        if data.nova_matricula is not None: updates["matricula"] = data.nova_matricula
        if data.novo_time is not None: updates["times_cobranca"] = data.novo_time
        if data.novo_pa is not None: updates["num_pa"] = data.novo_pa
        if data.novo_status is not None: updates["status"] = data.novo_status

        afetados = self.cobranca_repo.bulk_update(data.ids, updates)
        self.auditoria_repo.log(AuditoriaTroca(
            tipo_acao="BULK_UPDATE",
            usuario="Sistema",
            cobrador_origem="LOTE",
            cobrador_destino=data.novo_cobrador or "Vários",
            total_afetados=afetados,
            detalhe=f"Campos atualizados: {list(updates.keys())}"
        ))
        return {"total_afetados": afetados}
