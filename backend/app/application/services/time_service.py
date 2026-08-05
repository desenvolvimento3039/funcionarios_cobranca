from typing import List, Optional, Dict, Any
from app.domain.repositories import ICobrancaRepository, IAuditoriaRepository
from app.domain.entities import AuditoriaTroca
from app.application.dto.schemas import TrocaMassaRequest

class TimeService:
    """Serviço responsável pela gestão de Times de Cobrança, PAs, Analytics e Trocas em Massa."""

    def __init__(
        self,
        cobranca_repo: ICobrancaRepository,
        auditoria_repo: IAuditoriaRepository
    ):
        self.cobranca_repo = cobranca_repo
        self.auditoria_repo = auditoria_repo

    def listar_pas(self) -> List[Dict[str, Any]]:
        pas = self.cobranca_repo.list_pas()
        return [{"num_pa": p.num_pa, "nome_pa": p.nome_pa} for p in pas]

    def estatisticas_analytics(self) -> Dict[str, Any]:
        return self.cobranca_repo.get_analytics_stats()

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
