from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

@dataclass
class FuncionarioCobranca:
    id: Optional[int] = None
    times_cobranca: str = ""
    num_pa: int = 0
    matricula: int = 0
    cobrador: str = ""
    fila: str = ""
    telefone: str = ""
    status: int = 1

    def is_ativo(self) -> bool:
        return self.status == 1

    def inativar(self):
        self.status = 0

    def ativar(self):
        self.status = 1

@dataclass
class Substituicao:
    id: Optional[int] = None
    substituto_id: int = 0
    original_id: int = 0
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    status_substituicao: str = "AGENDADA"
    created_at: Optional[datetime] = field(default_factory=datetime.now)

    def is_ativa_hoje(self, hoje: Optional[date] = None) -> bool:
        hoje = hoje or date.today()
        if not self.data_inicio or not self.data_fim:
            return False
        return self.status_substituicao in ("AGENDADA", "EM_ANDAMENTO") and (self.data_inicio <= hoje <= self.data_fim)

@dataclass
class AuditoriaTroca:
    id: Optional[int] = None
    tipo_acao: str = ""
    usuario: str = "Sistema"
    cobrador_origem: Optional[str] = None
    cobrador_destino: Optional[str] = None
    total_afetados: int = 1
    detalhe: Optional[str] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)

@dataclass
class FinanciamentoRural:
    id: Optional[int] = None
    item: str = ""
    enquadramento: str = ""
    linha: str = ""
    isolado: str = "Não"
    status: int = 1

@dataclass
class InstituicaoPA:
    id: Optional[int] = None
    num_pa: int = 0
    nome_pa: str = ""
