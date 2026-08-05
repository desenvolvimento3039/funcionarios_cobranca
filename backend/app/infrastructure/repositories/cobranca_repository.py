from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.domain.entities import FuncionarioCobranca, InstituicaoPA
from app.domain.repositories import ICobrancaRepository

class SQLCobrancaRepository(ICobrancaRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cobranca_id: int) -> Optional[FuncionarioCobranca]:
        sql = text("""
            SELECT id, times_cobranca, num_pa, matricula, cobrador, fila, telefone, status
            FROM fun_funcionarios_cobranca
            WHERE id = :id
        """)
        res = self.db.execute(sql, {"id": cobranca_id}).mappings().first()
        if not res:
            return None
        return FuncionarioCobranca(
            id=res["id"],
            times_cobranca=res["times_cobranca"] or "",
            num_pa=res["num_pa"] or 0,
            matricula=res["matricula"] or 0,
            cobrador=res["cobrador"] or "",
            fila=res["fila"] or "",
            telefone=res["telefone"] or "",
            status=res["status"] if res["status"] is not None else 1
        )

    def create(self, entity: FuncionarioCobranca) -> FuncionarioCobranca:
        sql = text("""
            INSERT INTO fun_funcionarios_cobranca (times_cobranca, num_pa, matricula, cobrador, fila, telefone, status)
            VALUES (:times_cobranca, :num_pa, :matricula, :cobrador, :fila, :telefone, :status)
            RETURNING id, times_cobranca, num_pa, matricula, cobrador, fila, telefone, status
        """)
        res = self.db.execute(sql, {
            "times_cobranca": entity.times_cobranca,
            "num_pa": entity.num_pa,
            "matricula": entity.matricula,
            "cobrador": entity.cobrador,
            "fila": entity.fila,
            "telefone": entity.telefone,
            "status": entity.status
        }).mappings().first()
        self.db.commit()
        return FuncionarioCobranca(**dict(res))

    def create_batch(self, entities: List[FuncionarioCobranca]) -> List[FuncionarioCobranca]:
        if not entities:
            return []
        sql = text("""
            INSERT INTO fun_funcionarios_cobranca (times_cobranca, num_pa, matricula, cobrador, fila, telefone, status)
            VALUES (:times_cobranca, :num_pa, :matricula, :cobrador, :fila, :telefone, :status)
            RETURNING id, times_cobranca, num_pa, matricula, cobrador, fila, telefone, status
        """)
        params = [{
            "times_cobranca": e.times_cobranca,
            "num_pa": e.num_pa,
            "matricula": e.matricula,
            "cobrador": e.cobrador,
            "fila": e.fila,
            "telefone": e.telefone,
            "status": e.status
        } for e in entities]
        res = self.db.execute(sql, params).mappings().all()
        self.db.commit()
        return [FuncionarioCobranca(**dict(r)) for r in res]

    def update(self, entity: FuncionarioCobranca) -> FuncionarioCobranca:
        sql = text("""
            UPDATE fun_funcionarios_cobranca
            SET times_cobranca = :times_cobranca, num_pa = :num_pa, matricula = :matricula,
                cobrador = :cobrador, fila = :fila, telefone = :telefone, status = :status
            WHERE id = :id
            RETURNING id, times_cobranca, num_pa, matricula, cobrador, fila, telefone, status
        """)
        res = self.db.execute(sql, {
            "id": entity.id,
            "times_cobranca": entity.times_cobranca,
            "num_pa": entity.num_pa,
            "matricula": entity.matricula,
            "cobrador": entity.cobrador,
            "fila": entity.fila,
            "telefone": entity.telefone,
            "status": entity.status
        }).mappings().first()
        self.db.commit()
        return FuncionarioCobranca(**dict(res))

    def update_status(self, cobranca_id: int, new_status: int) -> Optional[FuncionarioCobranca]:
        sql = text("""
            UPDATE fun_funcionarios_cobranca
            SET status = :status
            WHERE id = :id
            RETURNING id, times_cobranca, num_pa, matricula, cobrador, fila, telefone, status
        """)
        res = self.db.execute(sql, {"id": cobranca_id, "status": new_status}).mappings().first()
        self.db.commit()
        if not res:
            return None
        return FuncionarioCobranca(**dict(res))

    def delete(self, cobranca_id: int) -> bool:
        sql = text("DELETE FROM fun_funcionarios_cobranca WHERE id = :id")
        res = self.db.execute(sql, {"id": cobranca_id})
        self.db.commit()
        return res.rowcount > 0

    def list_pas(self) -> List[InstituicaoPA]:
        sql = text("""
            SELECT DISTINCT num_pa, nome_pa
            FROM inst_instituicao
            WHERE num_pa IS NOT NULL
            ORDER BY num_pa ASC
        """)
        res = self.db.execute(sql).mappings().all()
        return [InstituicaoPA(num_pa=r["num_pa"], nome_pa=r["nome_pa"]) for r in res]

    def search_funcionarios(self, query: Optional[str]) -> List[Dict[str, Any]]:
        where_clause = "WHERE f.matricula IS NOT NULL"
        params = {}
        if query and query.strip():
            where_clause += " AND (LOWER(f.nome) LIKE :q OR CAST(f.matricula AS TEXT) LIKE :q OR LOWER(COALESCE(c.fila, '')) LIKE :q)"
            params["q"] = f"%{query.strip().lower()}%"

        try:
            sql = text(f"""
                SELECT DISTINCT 
                    c.id AS cobranca_id,
                    CAST(f.matricula AS INTEGER) AS matricula, 
                    COALESCE(f.nome, '') AS cobrador,
                    COALESCE(c.times_cobranca, '') AS times_cobranca,
                    c.num_pa,
                    COALESCE(c.fila, '') AS fila
                FROM fun_funcionario f
                LEFT JOIN fun_funcionarios_cobranca c ON c.matricula = f.matricula
                {where_clause}
                ORDER BY cobrador ASC LIMIT 50
            """)
            res = self.db.execute(sql, params).mappings().all()
            return [dict(r) for r in res]
        except Exception:
            where_fb = "WHERE matricula IS NOT NULL"
            if query and query.strip():
                where_fb += " AND (LOWER(cobrador) LIKE :q OR CAST(matricula AS TEXT) LIKE :q OR LOWER(COALESCE(fila, '')) LIKE :q)"
            sql_fb = text(f"""
                SELECT DISTINCT 
                    id AS cobranca_id,
                    CAST(matricula AS INTEGER) AS matricula, 
                    cobrador,
                    COALESCE(times_cobranca, '') AS times_cobranca,
                    num_pa,
                    COALESCE(fila, '') AS fila
                FROM fun_funcionarios_cobranca
                {where_fb}
                ORDER BY cobrador ASC LIMIT 50
            """)
            res = self.db.execute(sql_fb, params).mappings().all()
            return [dict(r) for r in res]

    def get_analytics_stats(self) -> Dict[str, Any]:
        sql_time = text("""
            SELECT COALESCE(NULLIF(times_cobranca, ''), 'Sem Time') as label, COUNT(*) as count
            FROM fun_funcionarios_cobranca
            GROUP BY label ORDER BY count DESC
        """)
        sql_pa = text("""
            SELECT COALESCE(num_pa, 0) as pa, COUNT(*) as count
            FROM fun_funcionarios_cobranca
            GROUP BY num_pa ORDER BY count DESC LIMIT 10
        """)
        sql_status = text("""
            SELECT COALESCE(status, 1) as status, COUNT(*) as count
            FROM fun_funcionarios_cobranca
            GROUP BY status
        """)
        sql_sub_ativas = text("""
            SELECT COUNT(*) FROM fun_cobranca_substituicoes 
            WHERE status_substituicao = 'EM_ANDAMENTO' 
               OR (status_substituicao = 'AGENDADA' AND CURRENT_DATE BETWEEN data_inicio AND data_fim)
        """)
        sql_sub_agendadas = text("""
            SELECT COUNT(*) FROM fun_cobranca_substituicoes 
            WHERE status_substituicao = 'AGENDADA' AND data_inicio > CURRENT_DATE
        """)

        res_time = self.db.execute(sql_time).mappings().all()
        res_pa = self.db.execute(sql_pa).mappings().all()
        res_status = self.db.execute(sql_status).mappings().all()
        sub_ativas = self.db.execute(sql_sub_ativas).scalar() or 0
        sub_agendadas = self.db.execute(sql_sub_agendadas).scalar() or 0

        return {
            "por_time": [dict(r) for r in res_time],
            "por_pa": [dict(r) for r in res_pa],
            "por_status": [dict(r) for r in res_status],
            "substituicoes_ativas": sub_ativas,
            "substituicoes_agendadas": sub_agendadas
        }

    def list_paginated(
        self,
        page: Optional[int],
        per_page: Optional[int],
        search: Optional[str],
        time_cobranca: Optional[str],
        pa: Optional[int],
        status: Optional[int],
        substituicao: Optional[str],
        sort_by: str,
        sort_order: str
    ) -> Tuple[List[Dict[str, Any]], int]:
        where_clauses = ["1=1"]
        params = {}

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            where_clauses.append("(LOWER(c.cobrador) LIKE :search OR CAST(c.matricula AS TEXT) LIKE :search OR LOWER(c.fila) LIKE :search OR LOWER(c.times_cobranca) LIKE :search OR LOWER(c.telefone) LIKE :search)")
            params["search"] = term

        if time_cobranca and time_cobranca.strip():
            where_clauses.append("c.times_cobranca = :time_cobranca")
            params["time_cobranca"] = time_cobranca.strip()

        if pa is not None:
            where_clauses.append("c.num_pa = :pa")
            params["pa"] = pa

        if status is not None:
            where_clauses.append("c.status = :status")
            params["status"] = status

        if substituicao == "ORIGINAL":
            where_clauses.append("sub_orig.id IS NOT NULL")
        elif substituicao == "SUBSTITUTO":
            where_clauses.append("sub_as_sub.id IS NOT NULL")
        elif substituicao == "COM_SUBSTITUICAO":
            where_clauses.append("(sub_orig.id IS NOT NULL OR sub_as_sub.id IS NOT NULL)")
        elif substituicao == "SEM_SUBSTITUICAO":
            where_clauses.append("sub_orig.id IS NULL AND sub_as_sub.id IS NULL")

        where_str = " AND ".join(where_clauses)
        from_clause = """
            FROM fun_funcionarios_cobranca c
            LEFT JOIN fun_cobranca_substituicoes sub_orig 
                   ON sub_orig.original_id = c.id 
                  AND sub_orig.status_substituicao IN ('AGENDADA', 'EM_ANDAMENTO')
            LEFT JOIN fun_funcionarios_cobranca c_sub 
                   ON c_sub.id = sub_orig.substituto_id
            LEFT JOIN fun_cobranca_substituicoes sub_as_sub 
                   ON sub_as_sub.substituto_id = c.id 
                  AND sub_as_sub.status_substituicao IN ('AGENDADA', 'EM_ANDAMENTO')
            LEFT JOIN fun_funcionarios_cobranca c_orig 
                   ON c_orig.id = sub_as_sub.original_id
        """

        count_sql = text(f"SELECT COUNT(*) {from_clause} WHERE {where_str}")
        total_records = self.db.execute(count_sql, params).scalar() or 0

        valid_sort_fields = {
            "id": "c.id", "cobrador": "c.cobrador", "matricula": "c.matricula",
            "times_cobranca": "c.times_cobranca", "num_pa": "c.num_pa", "fila": "c.fila", "status": "c.status"
        }
        order_col = valid_sort_fields.get(sort_by, "c.id")
        order_dir = "ASC" if sort_order.lower() == "asc" else "DESC"

        select_fields = """
            c.id, COALESCE(c.times_cobranca, '') AS times_cobranca, 
            COALESCE(c.num_pa, 0) AS num_pa, COALESCE(c.matricula, 0) AS matricula, 
            COALESCE(c.cobrador, '') AS cobrador, COALESCE(c.fila, '') AS fila,
            COALESCE(c.telefone, '') AS telefone, COALESCE(c.status, 1) AS status,
            sub_orig.id AS sub_orig_id,
            sub_orig.substituto_id AS sub_orig_sub_id,
            c_sub.cobrador AS substituto_nome,
            CAST(sub_orig.data_inicio AS TEXT) AS sub_orig_inicio,
            CAST(sub_orig.data_fim AS TEXT) AS sub_orig_fim,
            sub_orig.status_substituicao AS sub_orig_status,
            sub_as_sub.id AS sub_as_sub_id,
            sub_as_sub.original_id AS substituto_de_id,
            c_orig.cobrador AS original_nome,
            CAST(sub_as_sub.data_inicio AS TEXT) AS sub_as_sub_inicio,
            CAST(sub_as_sub.data_fim AS TEXT) AS sub_as_sub_fim,
            sub_as_sub.status_substituicao AS sub_as_sub_status
        """

        pagination_clause = ""
        if page and per_page and page > 0 and per_page > 0:
            offset = (page - 1) * per_page
            pagination_clause = f" LIMIT {per_page} OFFSET {offset}"

        data_sql = text(f"SELECT {select_fields} {from_clause} WHERE {where_str} ORDER BY {order_col} {order_dir} {pagination_clause}")
        res = self.db.execute(data_sql, params).mappings().all()

        formatted = []
        for r in res:
            d = dict(r)
            if d.get("sub_orig_id"):
                d["substituicao_id"] = d["sub_orig_id"]
                d["data_inicio_substituicao"] = d["sub_orig_inicio"]
                d["data_fim_substituicao"] = d["sub_orig_fim"]
                d["status_substituicao"] = d["sub_orig_status"]
                d["papel_substituicao"] = "ORIGINAL"
            elif d.get("sub_as_sub_id"):
                d["substituicao_id"] = d["sub_as_sub_id"]
                d["substituto_nome"] = d["original_nome"]
                d["data_inicio_substituicao"] = d["sub_as_sub_inicio"]
                d["data_fim_substituicao"] = d["sub_as_sub_fim"]
                d["status_substituicao"] = d["sub_as_sub_status"]
                d["papel_substituicao"] = "SUBSTITUTO"
            formatted.append(d)

        return formatted, total_records

    def list_filas_sem_cobradores(self) -> List[Dict[str, Any]]:
        sql = text("""
            SELECT f.id, f.num_pa, f.fila, COALESCE(i.nome_pa, 'PA ' || f.num_pa::text) AS nome_pa
            FROM crl_inadimplencia f
            LEFT JOIN inst_instituicao i ON i.num_pa = f.num_pa
            WHERE NOT EXISTS (
                SELECT 1 FROM fun_funcionarios_cobranca c
                WHERE c.num_pa = f.num_pa AND c.fila = f.fila AND c.status = 1
            )
            ORDER BY f.num_pa, f.fila;
        """)
        res = self.db.execute(sql).mappings().all()
        return [dict(r) for r in res]

    def bulk_update(self, ids: List[int], updates: Dict[str, Any]) -> int:
        if not ids or not updates:
            return 0
        set_clauses = []
        params = {"ids": tuple(ids)}
        for key, val in updates.items():
            if val is not None:
                set_clauses.append(f"{key} = :{key}")
                params[key] = val
        if not set_clauses:
            return 0
        set_str = ", ".join(set_clauses)
        sql = text(f"UPDATE fun_funcionarios_cobranca SET {set_str} WHERE id IN :ids")
        res = self.db.execute(sql, params)
        self.db.commit()
        return res.rowcount

    def troca_massa(
        self,
        modo: str,
        novo_cobrador: str,
        nova_matricula: int,
        inativar_origem: bool,
        time: Optional[str] = None,
        num_pa: Optional[int] = None,
        cobrador_origem_id: Optional[int] = None
    ) -> Dict[str, Any]:
        where_clause = ""
        params = {"novo_cobrador": novo_cobrador, "nova_matricula": nova_matricula}

        if modo == "time" and time:
            where_clause = "WHERE times_cobranca = :time"
            params["time"] = time
        elif modo == "pa" and num_pa is not None:
            where_clause = "WHERE num_pa = :num_pa"
            params["num_pa"] = num_pa
        elif modo == "cobrador" and cobrador_origem_id is not None:
            orig = self.get_by_id(cobrador_origem_id)
            if not orig:
                raise ValueError("Cobrador de origem não encontrado.")
            where_clause = "WHERE matricula = :mat_origem"
            params["mat_origem"] = orig.matricula
        else:
            raise ValueError("Parâmetros inválidos para troca em massa.")

        if inativar_origem:
            self.db.execute(text(f"UPDATE fun_funcionarios_cobranca SET status = 0 {where_clause}"), params)

        sql_update = text(f"""
            UPDATE fun_funcionarios_cobranca 
            SET cobrador = :novo_cobrador, matricula = :nova_matricula, status = 1 
            {where_clause}
        """)
        res = self.db.execute(sql_update, params)
        afetados = res.rowcount
        self.db.commit()
        return {"total_afetados": afetados}
