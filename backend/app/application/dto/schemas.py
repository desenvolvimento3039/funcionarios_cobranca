from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date

class CobrancaBase(BaseModel):
    times_cobranca: str = Field(..., description="Nome do time de cobrança.")
    num_pa: Optional[int] = Field(default=0, description="Número do Ponto de Atendimento (PA).")
    matricula: int = Field(..., description="Matrícula do cobrador.")
    cobrador: str = Field(..., description="Nome do cobrador.")
    fila: str = Field(..., description="Fila de cobrança.")
    telefone: Optional[str] = Field(default="", description="Telefone de contato.")
    status: Optional[int] = Field(default=1, description="Status do registro (1 = Ativo, 0 = Inativo).")

class CobrancaCreate(CobrancaBase):
    times_cobranca: str = Field(..., max_length=100, description="Nome do time (máximo 100 caracteres).")
    cobrador: str = Field(..., max_length=100, description="Nome do cobrador (máximo 100 caracteres).")
    fila: str = Field(..., max_length=100, description="Fila (máximo 100 caracteres).")
    telefone: Optional[str] = Field(default="", max_length=50, description="Telefone (máximo 50 caracteres).")
    num_pa: Optional[int] = Field(default=0, description="Número do PA individual.")
    num_pas: Optional[List[int]] = Field(default=[], description="Lista de PAs selecionados para criação em lote no Novo Cobrador.")

    is_substituto: Optional[bool] = Field(default=False, description="Indica se é um cobrador substituto.")
    substituto_de_id: Optional[int] = Field(default=None, description="ID do cobrador original sendo substituído.")
    data_inicio_substituicao: Optional[date] = Field(default=None, description="Data de início da substituição.")
    data_fim_substituicao: Optional[date] = Field(default=None, description="Data de fim da substituição.")

class CobrancaResponse(CobrancaBase):
    id: int
    substituto_de_id: Optional[int] = None

class StatusUpdate(BaseModel):
    status: int = Field(..., description="Novo status (1 = Ativo, 0 = Inativo)")

class SubstituicaoEdit(BaseModel):
    data_inicio: date = Field(..., description="Nova data de início.")
    data_fim: date = Field(..., description="Nova data de término.")

class SubstituicaoDirectCreate(BaseModel):
    substituto_id: int = Field(..., description="ID do cobrador substituto.")
    original_id: int = Field(..., description="ID do cobrador original sendo substituído.")
    data_inicio: date = Field(..., description="Data de início da substituição.")
    data_fim: date = Field(..., description="Data de fim da substituição.")

class HistoricoSubstituicaoResponse(BaseModel):
    id: int
    substituto_id: int
    original_id: int
    data_inicio: date
    data_fim: date
    status_substituicao: str
    original_nome: Optional[str] = None
    substituto_nome: Optional[str] = None

class TrocaMassaRequest(BaseModel):
    modo: str = Field(..., description="Modo da troca: 'time', 'pa' ou 'cobrador'.")
    time: Optional[str] = Field(default=None, description="Nome do time de cobrança (se modo=='time').")
    num_pa: Optional[int] = Field(default=None, description="Número do PA (se modo=='pa').")
    cobrador_origem_id: Optional[int] = Field(default=None, description="ID do cobrador de origem (se modo=='cobrador').")
    novo_cobrador: str = Field(..., description="Nome do novo cobrador.")
    nova_matricula: int = Field(..., description="Matrícula do novo cobrador.")
    inativar_origem: Optional[bool] = Field(default=False, description="Se true, inativa o cobrador de origem após a troca.")

class BulkUpdateRequest(BaseModel):
    ids: List[int] = Field(..., description="Lista de IDs afetados.")
    novo_cobrador: Optional[str] = Field(default=None, description="Novo nome de cobrador.")
    nova_matricula: Optional[int] = Field(default=None, description="Nova matrícula.")
    novo_time: Optional[str] = Field(default=None, description="Novo time.")
    novo_pa: Optional[int] = Field(default=None, description="Novo PA.")
    novo_status: Optional[int] = Field(default=None, description="Novo status.")

class SubstituicaoMassaRequest(BaseModel):
    modo: str = Field(..., description="Modo da substituição temporária em massa: 'time', 'pa' ou 'cobrador'.")
    time: Optional[str] = Field(default=None, description="Nome do time de cobrança (se modo=='time').")
    num_pa: Optional[int] = Field(default=None, description="Número do PA (se modo=='pa').")
    cobrador_origem_id: Optional[int] = Field(default=None, description="ID do cobrador de origem (se modo=='cobrador').")
    substituto_id: int = Field(..., description="ID do cobrador substituto.")
    data_inicio: date = Field(..., description="Data de início da substituição.")
    data_fim: date = Field(..., description="Data de fim da substituição.")

class FinanciamentoBase(BaseModel):
    item: str = Field(..., description="Nome do item financiável.")
    enquadramento: Optional[str] = Field(default="", description="Enquadramento / Programa.")
    linha: Optional[str] = Field(default="", description="Linha de crédito.")
    isolado: Optional[str] = Field(default="Não", description="Indica se é isolado (Sim/Não).")
    status: Optional[int] = Field(default=1, description="Status do item (1 = Ativo, 0 = Inativo).")

class FinanciamentoCreate(FinanciamentoBase):
    pass

class FinanciamentoResponse(FinanciamentoBase):
    id: int
