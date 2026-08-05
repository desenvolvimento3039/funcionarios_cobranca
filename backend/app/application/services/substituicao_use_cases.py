from datetime import date
from typing import List, Optional, Dict, Any
from app.domain.entities import Substituicao, AuditoriaTroca
from app.domain.repositories import ISubstituicaoRepository, ICobrancaRepository, IAuditoriaRepository
from app.application.dto.schemas import SubstituicaoMassaRequest

class SubstituicaoService:
    def __init__(
        self,
        substituicao_repo: ISubstituicaoRepository,
        cobranca_repo: ICobrancaRepository,
        auditoria_repo: IAuditoriaRepository
    ):
        self.substituicao_repo = substituicao_repo
        self.cobranca_repo = cobranca_repo
        self.auditoria_repo = auditoria_repo

    def listar_escala(self) -> List[Dict[str, Any]]:
        return self.substituicao_repo.list_escala()

    def atualizar_datas(self, id: int, data_inicio: date, data_fim: date) -> Optional[Dict[str, Any]]:
        updated = self.substituicao_repo.update_dates(id, data_inicio, data_fim)
        if not updated:
            return None
        return {
            "id": updated.id,
            "substituto_id": updated.substituto_id,
            "original_id": updated.original_id,
            "data_inicio": str(updated.data_inicio),
            "data_fim": str(updated.data_fim),
            "status_substituicao": updated.status_substituicao
        }

    def cancelar(self, id: int) -> bool:
        return self.substituicao_repo.cancel(id)

    def criar_direta(self, substituto_id: int, original_id: int, data_inicio: date, data_fim: date) -> Dict[str, Any]:
        hoje = date.today()
        status_sub = "CONCLUIDA" if data_fim < hoje else ("EM_ANDAMENTO" if data_inicio <= hoje <= data_fim else "AGENDADA")
        entity = Substituicao(
            substituto_id=substituto_id,
            original_id=original_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status_substituicao=status_sub
        )
        created = self.substituicao_repo.create(entity)
        return {
            "id": created.id,
            "substituto_id": created.substituto_id,
            "original_id": created.original_id,
            "data_inicio": str(created.data_inicio),
            "data_fim": str(created.data_fim),
            "status_substituicao": created.status_substituicao
        }

    def substituicao_massa(self, data: SubstituicaoMassaRequest) -> Dict[str, Any]:
        result = self.substituicao_repo.create_substituicao_massa(
            modo=data.modo,
            substituto_id=data.substituto_id,
            data_inicio=data.data_inicio,
            data_fim=data.data_fim,
            time=data.time,
            num_pa=data.num_pa,
            cobrador_origem_id=data.cobrador_origem_id
        )

        substituta_nome = "Substituto ID " + str(data.substituto_id)
        sub_cob = self.cobranca_repo.get_by_id(data.substituto_id)
        if sub_cob:
            substituta_nome = sub_cob.cobrador

        self.auditoria_repo.log(AuditoriaTroca(
            tipo_acao="SUBSTITUICAO_MASSA",
            usuario="Sistema",
            cobrador_origem=data.modo.upper(),
            cobrador_destino=substituta_nome,
            total_afetados=result.get("total_criadas", 0),
            detalhe=f"Período: {data.data_inicio} até {data.data_fim}"
        ))
        return result

    def processar_substituicoes_job(self) -> Dict[str, int]:
        return self.substituicao_repo.process_scheduled_substitutions()
