from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date

class CobrancaBase(BaseModel):
    times_cobranca: str = Field(..., description="Nome do time de cobrança.")
    num_pa: int = Field(..., description="Número do Ponto de Atendimento (PA).")
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
    
    # Novos campos para suporte a substitutos
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
