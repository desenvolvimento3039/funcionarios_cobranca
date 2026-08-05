from typing import List, Optional, Dict, Any, Union
from app.domain.entities import FuncionarioCobranca, AuditoriaTroca
from app.domain.repositories import ICobrancaRepository, ISubstituicaoRepository, IAuditoriaRepository
from app.application.dto.schemas import CobrancaCreate, TrocaMassaRequest, BulkUpdateRequest
from app.infrastructure.utils.excel_utils import generate_csv_cobranca, generate_csv_model_cobranca

class CobrancaService:
    def __init__(
        self,
        cobranca_repo: ICobrancaRepository,
        substituicao_repo: ISubstituicaoRepository,
        auditoria_repo: IAuditoriaRepository
    ):
        self.cobranca_repo = cobranca_repo
        self.substituicao_repo = substituicao_repo
        self.auditoria_repo = auditoria_repo

    def listar_pas(self) -> List[Dict[str, Any]]:
        pas = self.cobranca_repo.list_pas()
        return [{"num_pa": p.num_pa, "nome_pa": p.nome_pa} for p in pas]

    def buscar_funcionarios(self, query: Optional[str]) -> List[Dict[str, Any]]:
        return self.cobranca_repo.search_funcionarios(query)

    def estatisticas_analytics(self) -> Dict[str, Any]:
        return self.cobranca_repo.get_analytics_stats()

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

    def criar_cobranca(self, data: CobrancaCreate) -> Dict[str, Any]:
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
            from app.domain.entities import Substituicao
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

    def atualizar_cobranca(self, cobranca_id: int, data: CobrancaCreate) -> Optional[Dict[str, Any]]:
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

    def deletar_cobranca(self, cobranca_id: int) -> bool:
        return self.cobranca_repo.delete(cobranca_id)

    def listar_filas_sem_cobradores(self) -> List[Dict[str, Any]]:
        return self.cobranca_repo.list_filas_sem_cobradores()

    def troca_massa(self, data: TrocaMassaRequest) -> Dict[str, Any]:
        cobrador_origem_nome = None
        if data.modo == "cobrador" and data.cobrador_origem_id:
            orig = self.cobranca_repo.get_by_id(data.cobrador_origem_id)
            if orig:
                cobrador_origem_nome = orig.cobrador

        result = self.cobranca_repo.troca_massa(
            modo=data.modo,
            novo_cobrador=data.novo_cobrador,
            nova_matricula=data.nova_matricula,
            inativar_origem=bool(data.inativar_origem),
            time=data.time,
            num_pa=data.num_pa,
            cobrador_origem_id=data.cobrador_origem_id
        )

        detalhe = f"Modo: {data.modo}"
        if data.modo == "time": detalhe += f" | Time: {data.time}"
        elif data.modo == "pa": detalhe += f" | PA: {data.num_pa}"

        self.auditoria_repo.log(AuditoriaTroca(
            tipo_acao="TROCA_MASSA",
            usuario="Sistema",
            cobrador_origem=cobrador_origem_nome or data.modo.upper(),
            cobrador_destino=data.novo_cobrador,
            total_afetados=result.get("total_afetados", 0),
            detalhe=detalhe
        ))
        return result

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

    def listar_historico_auditoria(self) -> List[Dict[str, Any]]:
        return self.auditoria_repo.list_historico()

    def exportar_csv(self) -> str:
        rows, _ = self.cobranca_repo.list_paginated(None, None, None, None, None, None, None, "id", "desc")
        return generate_csv_cobranca(rows)

    def gerar_modelo_excel(self) -> str:
        return generate_csv_model_cobranca()
