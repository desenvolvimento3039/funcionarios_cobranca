from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.domain.entities import AuditoriaTroca
from app.domain.repositories import IAuditoriaRepository

class SQLAuditoriaRepository(IAuditoriaRepository):
    def __init__(self, db: Session):
        self.db = db

    def log(self, entity: AuditoriaTroca) -> AuditoriaTroca:
        sql = text("""
            INSERT INTO fun_cobranca_auditoria 
                (tipo_acao, usuario, cobrador_origem, cobrador_destino, total_afetados, detalhe)
            VALUES 
                (:tipo_acao, :usuario, :cobrador_origem, :cobrador_destino, :total_afetados, :detalhe)
            RETURNING id, tipo_acao, usuario, cobrador_origem, cobrador_destino, total_afetados, detalhe, created_at
        """)
        res = self.db.execute(sql, {
            "tipo_acao": entity.tipo_acao,
            "usuario": entity.usuario,
            "cobrador_origem": entity.cobrador_origem,
            "cobrador_destino": entity.cobrador_destino,
            "total_afetados": entity.total_afetados,
            "detalhe": entity.detalhe
        }).mappings().first()
        self.db.commit()
        return AuditoriaTroca(**dict(res))

    def list_historico(self, limit: int = 100) -> List[Dict[str, Any]]:
        sql = text("""
            SELECT 
                id, tipo_acao, usuario, cobrador_origem, cobrador_destino, 
                total_afetados, detalhe, CAST(created_at AS TEXT) AS data_registro
            FROM fun_cobranca_auditoria
            ORDER BY id DESC LIMIT :limit
        """)
        res = self.db.execute(sql, {"limit": limit}).mappings().all()
        return [dict(r) for r in res]
