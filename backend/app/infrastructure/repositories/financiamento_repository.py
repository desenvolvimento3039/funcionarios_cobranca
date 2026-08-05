from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.domain.entities import FinanciamentoRural
from app.domain.repositories import IFinanciamentoRepository

class SQLFinanciamentoRepository(IFinanciamentoRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[FinanciamentoRural]:
        sql = text("""
            SELECT id, item, COALESCE(enquadramento, '') AS enquadramento, COALESCE(linha, '') AS linha,
                   COALESCE(isolado, 'Não') AS isolado, COALESCE(status, 1) AS status
            FROM public.financiamento_rural
            WHERE id = :id
        """)
        res = self.db.execute(sql, {"id": id}).mappings().first()
        if not res:
            return None
        return FinanciamentoRural(**dict(res))

    def list_all(self) -> List[FinanciamentoRural]:
        sql = text("""
            SELECT id, item, COALESCE(enquadramento, '') AS enquadramento, COALESCE(linha, '') AS linha,
                   COALESCE(isolado, 'Não') AS isolado, COALESCE(status, 1) AS status
            FROM public.financiamento_rural
            ORDER BY id DESC
        """)
        res = self.db.execute(sql).mappings().all()
        return [FinanciamentoRural(**dict(r)) for r in res]

    def create(self, entity: FinanciamentoRural) -> FinanciamentoRural:
        sql = text("""
            INSERT INTO public.financiamento_rural (item, enquadramento, linha, isolado, status)
            VALUES (:item, :enquadramento, :linha, :isolado, :status)
            RETURNING id, item, COALESCE(enquadramento, '') AS enquadramento, COALESCE(linha, '') AS linha,
                      COALESCE(isolado, 'Não') AS isolado, COALESCE(status, 1) AS status
        """)
        res = self.db.execute(sql, {
            "item": entity.item,
            "enquadramento": entity.enquadramento,
            "linha": entity.linha,
            "isolado": entity.isolado,
            "status": entity.status
        }).mappings().first()
        self.db.commit()
        return FinanciamentoRural(**dict(res))

    def update(self, entity: FinanciamentoRural) -> Optional[FinanciamentoRural]:
        sql = text("""
            UPDATE public.financiamento_rural
            SET item = :item, enquadramento = :enquadramento, linha = :linha, isolado = :isolado, status = :status
            WHERE id = :id
            RETURNING id, item, COALESCE(enquadramento, '') AS enquadramento, COALESCE(linha, '') AS linha,
                      COALESCE(isolado, 'Não') AS isolado, COALESCE(status, 1) AS status
        """)
        res = self.db.execute(sql, {
            "id": entity.id,
            "item": entity.item,
            "enquadramento": entity.enquadramento,
            "linha": entity.linha,
            "isolado": entity.isolado,
            "status": entity.status
        }).mappings().first()
        self.db.commit()
        if not res:
            return None
        return FinanciamentoRural(**dict(res))

    def update_status(self, id: int, status: int) -> Optional[FinanciamentoRural]:
        sql = text("""
            UPDATE public.financiamento_rural
            SET status = :status
            WHERE id = :id
            RETURNING id, item, COALESCE(enquadramento, '') AS enquadramento, COALESCE(linha, '') AS linha,
                      COALESCE(isolado, 'Não') AS isolado, COALESCE(status, 1) AS status
        """)
        res = self.db.execute(sql, {"id": id, "status": status}).mappings().first()
        self.db.commit()
        if not res:
            return None
        return FinanciamentoRural(**dict(res))

    def delete(self, id: int) -> bool:
        sql = text("DELETE FROM public.financiamento_rural WHERE id = :id")
        res = self.db.execute(sql, {"id": id})
        self.db.commit()
        return res.rowcount > 0

    def sync_data_rows(self, rows: List[Tuple[str, str, str, str]]) -> Dict[str, Any]:
        if not rows:
            return {"inserted": 0, "updated": 0, "total": 0}

        stg_sql = text("""
            CREATE TEMP TABLE IF NOT EXISTS stg_financiamento (
                item VARCHAR, enquadramento VARCHAR, linha VARCHAR, isolado VARCHAR
            ) ON COMMIT DROP;
        """)
        self.db.execute(stg_sql)

        insert_stg = text("""
            INSERT INTO stg_financiamento (item, enquadramento, linha, isolado)
            VALUES (:item, :enquadramento, :linha, :isolado)
        """)
        self.db.execute(insert_stg, [{"item": r[0], "enquadramento": r[1], "linha": r[2], "isolado": r[3]} for r in rows])

        update_sql = text("""
            UPDATE public.financiamento_rural t
            SET isolado = s.isolado
            FROM stg_financiamento s
            WHERE t.item = s.item AND t.enquadramento = s.enquadramento AND t.linha = s.linha;
        """)
        res_upd = self.db.execute(update_sql)
        updated = res_upd.rowcount

        insert_sql = text("""
            INSERT INTO public.financiamento_rural (item, enquadramento, linha, isolado)
            SELECT s.item, s.enquadramento, s.linha, s.isolado
            FROM stg_financiamento s
            WHERE NOT EXISTS (
                SELECT 1 FROM public.financiamento_rural t
                WHERE t.item = s.item AND t.enquadramento = s.enquadramento AND t.linha = s.linha
            );
        """)
        res_ins = self.db.execute(insert_sql)
        inserted = res_ins.rowcount

        self.db.commit()
        total = self.db.execute(text("SELECT COUNT(*) FROM public.financiamento_rural")).scalar() or 0
        return {"updated": updated, "inserted": inserted, "total": total}
