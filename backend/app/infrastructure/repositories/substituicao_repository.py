from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.domain.entities import Substituicao
from app.domain.repositories import ISubstituicaoRepository

class SQLSubstituicaoRepository(ISubstituicaoRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Substituicao]:
        sql = text("""
            SELECT id, substituto_id, original_id, data_inicio, data_fim, status_substituicao, created_at
            FROM fun_cobranca_substituicoes
            WHERE id = :id
        """)
        res = self.db.execute(sql, {"id": id}).mappings().first()
        if not res:
            return None
        return Substituicao(**dict(res))

    def create(self, entity: Substituicao) -> Substituicao:
        # Cancela substituições ativas/agendadas anteriores do mesmo original_id para evitar duplicidade
        sql_cancel = text("""
            UPDATE fun_cobranca_substituicoes
            SET status_substituicao = 'CANCELADA'
            WHERE original_id = :original_id AND status_substituicao IN ('AGENDADA', 'EM_ANDAMENTO')
        """)
        self.db.execute(sql_cancel, {"original_id": entity.original_id})

        sql = text("""
            INSERT INTO fun_cobranca_substituicoes (substituto_id, original_id, data_inicio, data_fim, status_substituicao)
            VALUES (:substituto_id, :original_id, :data_inicio, :data_fim, :status_substituicao)
            RETURNING id, substituto_id, original_id, data_inicio, data_fim, status_substituicao, created_at
        """)
        res = self.db.execute(sql, {
            "substituto_id": entity.substituto_id,
            "original_id": entity.original_id,
            "data_inicio": entity.data_inicio,
            "data_fim": entity.data_fim,
            "status_substituicao": entity.status_substituicao
        }).mappings().first()
        self.db.commit()
        return Substituicao(**dict(res))

    def update_dates(self, id: int, data_inicio: date, data_fim: date) -> Optional[Substituicao]:
        hoje = date.today()
        status = "CONCLUIDA" if data_fim < hoje else ("EM_ANDAMENTO" if data_inicio <= hoje <= data_fim else "AGENDADA")
        sql = text("""
            UPDATE fun_cobranca_substituicoes
            SET data_inicio = :data_inicio, data_fim = :data_fim, status_substituicao = :status
            WHERE id = :id
            RETURNING id, substituto_id, original_id, data_inicio, data_fim, status_substituicao, created_at
        """)
        res = self.db.execute(sql, {
            "id": id,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "status": status
        }).mappings().first()
        self.db.commit()
        if not res:
            return None
        return Substituicao(**dict(res))

    def cancel(self, id: int) -> bool:
        sql = text("""
            UPDATE fun_cobranca_substituicoes
            SET status_substituicao = 'CANCELADA'
            WHERE id = :id AND status_substituicao IN ('AGENDADA', 'EM_ANDAMENTO')
        """)
        res = self.db.execute(sql, {"id": id})
        self.db.commit()
        return res.rowcount > 0

    def list_escala(self) -> List[Dict[str, Any]]:
        sql = text("""
            SELECT 
                s.id, s.substituto_id, s.original_id,
                CAST(s.data_inicio AS TEXT) AS data_inicio,
                CAST(s.data_fim AS TEXT) AS data_fim,
                s.status_substituicao,
                c_orig.cobrador AS original_nome, c_orig.matricula AS original_matricula,
                c_orig.times_cobranca AS original_time, c_orig.num_pa AS original_pa, c_orig.fila AS original_fila,
                c_sub.cobrador AS substituto_nome, c_sub.matricula AS substituto_matricula,
                c_sub.times_cobranca AS substituto_time, c_sub.num_pa AS substituto_pa, c_sub.fila AS substituto_fila
            FROM fun_cobranca_substituicoes s
            JOIN fun_funcionarios_cobranca c_orig ON c_orig.id = s.original_id
            JOIN fun_funcionarios_cobranca c_sub ON c_sub.id = s.substituto_id
            WHERE s.status_substituicao IN ('AGENDADA', 'EM_ANDAMENTO')
            ORDER BY s.data_inicio ASC
        """)
        res = self.db.execute(sql).mappings().all()
        return [dict(r) for r in res]

    def process_scheduled_substitutions(self) -> Dict[str, int]:
        sql_iniciar = text("""
            UPDATE fun_cobranca_substituicoes
            SET status_substituicao = 'EM_ANDAMENTO'
            WHERE status_substituicao = 'AGENDADA' AND CURRENT_DATE >= data_inicio AND CURRENT_DATE <= data_fim
        """)
        sql_concluir = text("""
            UPDATE fun_cobranca_substituicoes
            SET status_substituicao = 'CONCLUIDA'
            WHERE status_substituicao IN ('AGENDADA', 'EM_ANDAMENTO') AND CURRENT_DATE > data_fim
        """)
        res1 = self.db.execute(sql_iniciar)
        res2 = self.db.execute(sql_concluir)
        self.db.commit()
        return {"iniciadas": res1.rowcount, "concluidas": res2.rowcount}

    def create_substituicao_massa(
        self,
        modo: str,
        substituto_id: int,
        data_inicio: date,
        data_fim: date,
        time: Optional[str] = None,
        num_pa: Optional[int] = None,
        cobrador_origem_id: Optional[int] = None
    ) -> Dict[str, Any]:
        where_clause = "WHERE status = 1"
        params = {}

        if modo == "time" and time:
            where_clause += " AND times_cobranca = :time"
            params["time"] = time
        elif modo == "pa" and num_pa is not None:
            where_clause += " AND num_pa = :num_pa"
            params["num_pa"] = num_pa
        elif modo == "cobrador" and cobrador_origem_id is not None:
            sql_orig = text("SELECT matricula, cobrador FROM fun_funcionarios_cobranca WHERE id = :origem_id")
            orig_row = self.db.execute(sql_orig, {"origem_id": cobrador_origem_id}).mappings().first()
            if orig_row and orig_row["matricula"]:
                where_clause += " AND (matricula = :mat OR cobrador = :cob_nome)"
                params["mat"] = orig_row["matricula"]
                params["cob_nome"] = orig_row["cobrador"]
            else:
                where_clause += " AND id = :origem_id"
                params["origem_id"] = cobrador_origem_id
        else:
            raise ValueError("Modo ou filtro inválido para substituição em massa.")

        sql_originais = text(f"SELECT id FROM fun_funcionarios_cobranca {where_clause}")
        originais = [r[0] for r in self.db.execute(sql_originais, params).fetchall() if r[0] != substituto_id]

        if not originais:
            return {"total_criadas": 0, "mensagem": "Nenhum funcionário ativo encontrado para substituição."}

        # Cancela substituições anteriores dos funcionários afetados para não duplicar na View
        sql_cancel = text("""
            UPDATE fun_cobranca_substituicoes
            SET status_substituicao = 'CANCELADA'
            WHERE original_id IN :originais_tuple AND status_substituicao IN ('AGENDADA', 'EM_ANDAMENTO')
        """)
        self.db.execute(sql_cancel, {"originais_tuple": tuple(originais)})

        hoje = date.today()
        status_sub = "CONCLUIDA" if data_fim < hoje else ("EM_ANDAMENTO" if data_inicio <= hoje <= data_fim else "AGENDADA")

        sql_insert = text("""
            INSERT INTO fun_cobranca_substituicoes (substituto_id, original_id, data_inicio, data_fim, status_substituicao)
            VALUES (:substituto_id, :original_id, :data_inicio, :data_fim, :status_substituicao)
        """)
        insert_params = [{
            "substituto_id": substituto_id,
            "original_id": orig_id,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "status_substituicao": status_sub
        } for orig_id in originais]

        self.db.execute(sql_insert, insert_params)
        self.db.commit()

        return {
            "total_criadas": len(originais),
            "mensagem": f"Substituição em massa temporária agendada com sucesso para {len(originais)} registro(s)!"
        }
