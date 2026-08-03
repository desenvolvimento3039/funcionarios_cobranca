import io
import csv
from typing import Optional, Dict
from sqlalchemy import text
from app.core.database import get_engine
from app.models.schemas import CobrancaCreate

def listar_pas() -> list:
    for dbname in ["SicoobSMO", "LeCom"]:
        try:
            engine = get_engine(dbname)
            with engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT DISTINCT num_pa, nome_pa
                    FROM public.inst_instituicao
                    WHERE num_pa IS NOT NULL
                    ORDER BY num_pa ASC
                """))
                return [dict(r) for r in res.mappings()]
        except Exception:
            continue
    return []

def buscar_funcionarios(q: Optional[str] = None) -> list:
    for dbname in ["SicoobSMO", "LeCom"]:
        try:
            engine = get_engine(dbname)
            with engine.connect() as conn:
                sql = """
                    SELECT DISTINCT CAST(matricula AS INTEGER) AS matricula, nome AS cobrador
                    FROM public.fun_funcionario
                    WHERE matricula IS NOT NULL
                """
                params = {}
                if q and q.strip():
                    sql += " AND (LOWER(nome) LIKE :q OR CAST(matricula AS TEXT) LIKE :q)"
                    params["q"] = f"%{q.strip().lower()}%"
                sql += " ORDER BY nome ASC LIMIT 50"

                res = conn.execute(text(sql), params)
                return [dict(r) for r in res.mappings()]
        except Exception:
            continue
    return []

def estatisticas_analytics() -> dict:
    for dbname in ["SicoobSMO", "LeCom"]:
        try:
            engine = get_engine(dbname)
            with engine.connect() as conn:
                res_time = conn.execute(text("""
                    SELECT COALESCE(NULLIF(times_cobranca, ''), 'Sem Time') as label, COUNT(*) as count
                    FROM public.fun_funcionarios_cobranca
                    GROUP BY label ORDER BY count DESC
                """))
                por_time = [dict(r) for r in res_time.mappings()]

                res_pa = conn.execute(text("""
                    SELECT COALESCE(num_pa, 0) as pa, COUNT(*) as count
                    FROM public.fun_funcionarios_cobranca
                    GROUP BY num_pa ORDER BY count DESC LIMIT 10
                """))
                por_pa = [dict(r) for r in res_pa.mappings()]

                res_status = conn.execute(text("""
                    SELECT COALESCE(status, 1) as status, COUNT(*) as count
                    FROM public.fun_funcionarios_cobranca
                    GROUP BY status
                """))
                por_status = [dict(r) for r in res_status.mappings()]

                return {
                    "por_time": por_time,
                    "por_pa": por_pa,
                    "por_status": por_status
                }
        except Exception:
            continue
    return {"por_time": [], "por_pa": [], "por_status": []}

def listar_cobranca(page: Optional[int], per_page: Optional[int], search: Optional[str],
                    time_cobranca: Optional[str], pa: Optional[int], status: Optional[int],
                    sort_by: str, sort_order: str) -> dict | list:
    for dbname in ["SicoobSMO", "LeCom"]:
        try:
            engine = get_engine(dbname)
            with engine.connect() as conn:
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

                where_str = " AND ".join(where_clauses)

                select_fields = """
                    c.id, COALESCE(c.times_cobranca, '') AS times_cobranca, 
                    COALESCE(c.num_pa, 0) AS num_pa, COALESCE(c.matricula, 0) AS matricula, 
                    COALESCE(c.cobrador, '') AS cobrador, COALESCE(c.fila, '') AS fila,
                    COALESCE(c.telefone, '') AS telefone, COALESCE(c.status, 1) AS status,
                    (SELECT original_id FROM public.fun_cobranca_substituicoes s WHERE s.substituto_id = c.id AND s.status_substituicao IN ('AGENDADA', 'EM_ANDAMENTO') LIMIT 1) as substituto_de_id
                """

                if page is None and per_page is None:
                    sql_full = f"""
                        SELECT {select_fields}
                        FROM public.fun_funcionarios_cobranca c
                        WHERE {where_str}
                        ORDER BY c.id DESC
                    """
                    result = conn.execute(text(sql_full), params)
                    return [dict(r) for r in result.mappings()]

                p = max(1, page or 1)
                pp = max(1, min(100, per_page or 25))
                offset = (p - 1) * pp

                valid_cols = {"id": "c.id", "times_cobranca": "c.times_cobranca", "num_pa": "c.num_pa", 
                              "matricula": "c.matricula", "cobrador": "c.cobrador", "fila": "c.fila", "status": "c.status"}
                order_col = valid_cols.get(sort_by, "c.id")
                order_dir = "ASC" if str(sort_order).lower() == "asc" else "DESC"

                count_res = conn.execute(text(f"SELECT COUNT(*) FROM public.fun_funcionarios_cobranca c WHERE {where_str}"), params)
                total = count_res.scalar() or 0

                sql_paginated = f"""
                    SELECT {select_fields}
                    FROM public.fun_funcionarios_cobranca c
                    WHERE {where_str}
                    ORDER BY {order_col} {order_dir}
                    LIMIT :limit OFFSET :offset
                """
                params["limit"] = pp
                params["offset"] = offset

                items_res = conn.execute(text(sql_paginated), params)
                items = [dict(r) for r in items_res.mappings()]

                total_pages = (total + pp - 1) // pp if total > 0 else 1

                return {
                    "items": items,
                    "total": total,
                    "page": p,
                    "per_page": pp,
                    "total_pages": total_pages
                }
        except Exception:
            continue
    return [] if (page is None and per_page is None) else {"items": [], "total": 0, "page": 1, "per_page": 25, "total_pages": 1}

def criar_cobranca(data: CobrancaCreate) -> Optional[dict]:
    novo = None
    for dbname in ["SicoobSMO", "LeCom"]:
        engine = get_engine(dbname)
        try:
            with engine.begin() as conn:
                res = conn.execute(text("""
                    INSERT INTO public.fun_funcionarios_cobranca
                        (times_cobranca, num_pa, matricula, cobrador, fila, telefone, status)
                    VALUES
                        (:times_cobranca, :num_pa, :matricula, :cobrador, :fila, :telefone, :status)
                    RETURNING id, times_cobranca, num_pa, matricula, cobrador, fila,
                              COALESCE(telefone, '') AS telefone, COALESCE(status, 1) AS status
                """), {
                    "times_cobranca": data.times_cobranca,
                    "num_pa": data.num_pa,
                    "matricula": data.matricula,
                    "cobrador": data.cobrador,
                    "fila": data.fila,
                    "telefone": data.telefone or "",
                    "status": 1 if data.status is None else data.status
                })
                row = dict(res.mappings().first())
                if not novo:
                    novo = row
                
                # Se for um substituto, cria o histórico
                if data.is_substituto and data.substituto_de_id and data.data_inicio_substituicao and data.data_fim_substituicao:
                    conn.execute(text("""
                        INSERT INTO public.fun_cobranca_substituicoes
                            (substituto_id, original_id, data_inicio, data_fim, status_substituicao)
                        VALUES
                            (:substituto_id, :original_id, :data_inicio, :data_fim, 'AGENDADA')
                    """), {
                        "substituto_id": row["id"],
                        "original_id": data.substituto_de_id,
                        "data_inicio": data.data_inicio_substituicao,
                        "data_fim": data.data_fim_substituicao
                    })
        except Exception as e:
            raise e
    return novo

def alterar_status(id: int, status_val: int) -> Optional[dict]:
    novo_status = 1 if status_val == 1 else 0
    atualizado = None
    for dbname in ["SicoobSMO", "LeCom"]:
        engine = get_engine(dbname)
        try:
            with engine.begin() as conn:
                res = conn.execute(text("""
                    UPDATE public.fun_funcionarios_cobranca
                    SET status = :status
                    WHERE id = :id
                    RETURNING id, times_cobranca, num_pa, matricula, cobrador, fila,
                              COALESCE(telefone, '') AS telefone, COALESCE(status, 1) AS status
                """), {"status": novo_status, "id": id})
                row = res.mappings().first()
                if row and not atualizado:
                    atualizado = dict(row)
        except Exception as e:
            raise e
    return atualizado

def atualizar_cobranca(id: int, data: CobrancaCreate) -> Optional[dict]:
    atualizado = None
    for dbname in ["SicoobSMO", "LeCom"]:
        engine = get_engine(dbname)
        try:
            with engine.begin() as conn:
                res = conn.execute(text("""
                    UPDATE public.fun_funcionarios_cobranca
                    SET times_cobranca = :times_cobranca, num_pa = :num_pa, matricula = :matricula,
                        cobrador = :cobrador, fila = :fila, telefone = :telefone, status = :status
                    WHERE id = :id
                    RETURNING id, times_cobranca, num_pa, matricula, cobrador, fila,
                              COALESCE(telefone, '') AS telefone, COALESCE(status, 1) AS status
                """), {
                    "times_cobranca": data.times_cobranca,
                    "num_pa": data.num_pa,
                    "matricula": data.matricula,
                    "cobrador": data.cobrador,
                    "fila": data.fila,
                    "telefone": data.telefone or "",
                    "status": 1 if data.status is None else data.status,
                    "id": id
                })
                row = res.mappings().first()
                if row and not atualizado:
                    atualizado = dict(row)
        except Exception as e:
            raise e
    return atualizado

def deletar_cobranca(id: int) -> bool:
    sucesso = False
    for dbname in ["SicoobSMO", "LeCom"]:
        engine = get_engine(dbname)
        try:
            with engine.begin() as conn:
                res = conn.execute(text("DELETE FROM public.fun_funcionarios_cobranca WHERE id = :id"), {"id": id})
                if res.rowcount > 0:
                    sucesso = True
        except Exception as e:
            raise e
    return sucesso

def exportar_csv_service() -> str:
    engine = get_engine("SicoobSMO")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, times_cobranca, num_pa, matricula, cobrador, fila,
                   COALESCE(telefone, '') AS telefone,
                   COALESCE(status, 1) AS status
            FROM public.fun_funcionarios_cobranca
            ORDER BY id ASC
        """))
        rows = result.mappings().all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["ID", "Times de Cobrança", "Num PA", "Matrícula", "Cobrador", "Fila", "Telefone", "Status"])

    for r in rows:
        status_txt = "Ativo" if r["status"] == 1 else "Inativo"
        writer.writerow([r["id"], r["times_cobranca"], r["num_pa"], r["matricula"],
                         r["cobrador"], r["fila"], r["telefone"], status_txt])

    return output.getvalue()

def atualizar_datas_substituicao(sub_id: int, data_inicio, data_fim) -> Optional[dict]:
    atualizado = None
    for dbname in ["SicoobSMO", "LeCom"]:
        engine = get_engine(dbname)
        try:
            with engine.begin() as conn:
                res = conn.execute(text("""
                    UPDATE public.fun_cobranca_substituicoes
                    SET data_inicio = :data_inicio, data_fim = :data_fim
                    WHERE id = :id
                    RETURNING id, substituto_id, original_id, data_inicio, data_fim, status_substituicao
                """), {
                    "id": sub_id,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim
                })
                row = res.mappings().first()
                if row and not atualizado:
                    atualizado = dict(row)
        except Exception:
            continue
    return atualizado

def listar_filas_sem_cobradores() -> list:
    for dbname in ["SicoobSMO", "LeCom"]:
        engine = get_engine(dbname)
        try:
            with engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT DISTINCT fila 
                    FROM public.crl_inadimplencia 
                    WHERE fila IS NOT NULL AND TRIM(fila) != ''
                      AND fila NOT IN (
                          SELECT DISTINCT fila 
                          FROM public.fun_funcionarios_cobranca 
                          WHERE status = 1 AND fila IS NOT NULL AND TRIM(fila) != ''
                      )
                    ORDER BY fila ASC
                """))
                return [r[0] for r in res.fetchall()]
        except Exception:
            continue
    return []

def criar_substituicao_direta(sub_id: int, orig_id: int, data_ini, data_f) -> Optional[dict]:
    novo = None
    for dbname in ["SicoobSMO", "LeCom"]:
        engine = get_engine(dbname)
        try:
            with engine.begin() as conn:
                res = conn.execute(text("""
                    INSERT INTO public.fun_cobranca_substituicoes
                        (substituto_id, original_id, data_inicio, data_fim, status_substituicao)
                    VALUES
                        (:sub_id, :orig_id, :data_ini, :data_f, 'AGENDADA')
                    RETURNING id, substituto_id, original_id, data_inicio, data_fim, status_substituicao
                """), {
                    "sub_id": sub_id,
                    "orig_id": orig_id,
                    "data_ini": data_ini,
                    "data_f": data_f
                })
                row = res.mappings().first()
                if row and not novo:
                    novo = dict(row)
        except Exception as e:
            raise e
    return novo
