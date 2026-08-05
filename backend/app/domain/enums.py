from enum import Enum

class StatusSubstituicao(str, Enum):
    AGENDADA = "AGENDADA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"

class ModoTrocaMassa(str, Enum):
    TIME = "time"
    PA = "pa"
    COBRADOR = "cobrador"

class PapelSubstituicao(str, Enum):
    ORIGINAL = "ORIGINAL"
    SUBSTITUTO = "SUBSTITUTO"
    COM_SUBSTITUICAO = "COM_SUBSTITUICAO"
    SEM_SUBSTITUICAO = "SEM_SUBSTITUICAO"
