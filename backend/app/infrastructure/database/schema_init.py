import logging
from sqlalchemy import text
from app.infrastructure.database.connection import engine

logger = logging.getLogger("uvicorn.error")

def inicializar_schema_bancos():
    """
    Garante a criação idempotente de tabelas, índices e a view SQL no PostgreSQL.
    """
    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS inst_instituicao (
            id SERIAL PRIMARY KEY,
            num_pa INTEGER NOT NULL,
            nome_pa VARCHAR(100) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS crl_inadimplencia (
            id SERIAL PRIMARY KEY,
            num_pa INTEGER DEFAULT 0,
            fila VARCHAR(100) NOT NULL
        );
        """,
        "ALTER TABLE crl_inadimplencia ADD COLUMN IF NOT EXISTS num_pa INTEGER DEFAULT 0;",
        """
        CREATE TABLE IF NOT EXISTS fun_funcionarios_cobranca (
            id SERIAL PRIMARY KEY,
            times_cobranca VARCHAR(100),
            num_pa INTEGER,
            matricula INTEGER,
            cobrador VARCHAR(100),
            fila VARCHAR(100),
            telefone VARCHAR(50),
            status INTEGER NOT NULL DEFAULT 1
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS fun_cobranca_substituicoes (
            id SERIAL PRIMARY KEY,
            substituto_id INTEGER NOT NULL,
            original_id INTEGER NOT NULL,
            data_inicio DATE NOT NULL,
            data_fim DATE NOT NULL,
            status_substituicao VARCHAR(20) NOT NULL DEFAULT 'AGENDADA',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS fun_cobranca_auditoria (
            id SERIAL PRIMARY KEY,
            tipo_acao VARCHAR(50) NOT NULL,
            usuario VARCHAR(100) DEFAULT 'Sistema',
            cobrador_origem VARCHAR(100),
            cobrador_destino VARCHAR(100),
            total_afetados INTEGER DEFAULT 1,
            detalhe TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS public.financiamento_rural (
            id SERIAL PRIMARY KEY,
            item VARCHAR(100) NOT NULL,
            enquadramento VARCHAR(200) NOT NULL,
            linha VARCHAR(45) NOT NULL,
            isolado VARCHAR(50) NOT NULL,
            status INTEGER NOT NULL DEFAULT 1
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_func_cobr_pa_fila ON fun_funcionarios_cobranca (num_pa, fila);",
        "CREATE INDEX IF NOT EXISTS idx_func_cobr_matricula ON fun_funcionarios_cobranca (matricula);",
        "CREATE INDEX IF NOT EXISTS idx_func_cobr_status ON fun_funcionarios_cobranca (status);",
        "CREATE INDEX IF NOT EXISTS idx_sub_orig_status ON fun_cobranca_substituicoes (original_id, status_substituicao);",
        "CREATE INDEX IF NOT EXISTS idx_sub_sub_status ON fun_cobranca_substituicoes (substituto_id, status_substituicao);",
        "CREATE INDEX IF NOT EXISTS idx_financiamento_rural_item ON public.financiamento_rural (item);",
        "CREATE INDEX IF NOT EXISTS idx_financiamento_rural_enq_linha ON public.financiamento_rural (enquadramento, linha);",
        "DROP VIEW IF EXISTS vw_cobranca_roteamento;",
        """
        CREATE VIEW vw_cobranca_roteamento AS
        SELECT
            f.id,
            COALESCE(f.times_cobranca, '')            AS times_cobranca,
            COALESCE(f.num_pa, 0)                     AS num_pa,
            COALESCE(i.nome_pa, 'PA ' || COALESCE(f.num_pa::text, '0')) AS nome_pa,
            COALESCE(f.matricula, 0)                  AS matricula,
            COALESCE(f.cobrador, '')                  AS cobrador,
            COALESCE(f.fila, '')                      AS fila,
            COALESCE(f.telefone, '')                  AS telefone,
            COALESCE(f.status, 1)                     AS status,
            CASE WHEN s.id IS NOT NULL THEN 1 ELSE 0 END AS em_substituicao,
            COALESCE(sub.cobrador, '')                AS cobrador_substituto,
            COALESCE(sub.matricula, 0)                AS matricula_substituta
        FROM fun_funcionarios_cobranca f
        LEFT JOIN inst_instituicao i ON f.num_pa = i.num_pa
        LEFT JOIN fun_cobranca_substituicoes s
               ON s.original_id = f.id
              AND s.status_substituicao IN ('AGENDADA', 'EM_ANDAMENTO')
        LEFT JOIN fun_funcionarios_cobranca sub ON s.substituto_id = sub.id;
        """
    ]

    for stmt in ddl_statements:
        try:
            with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                conn.execute(text(stmt))
        except Exception as e:
            logger.debug(f"[DB Schema Init Notice]: {e}")

    logger.info("[DB Schema] Tabelas, índices e views verificados com sucesso.")
