import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import get_engine, USE_LOCAL_TEST_DB, garantir_view_roteamento

def init_db():
    print(f"Inicializando banco de dados de teste local (USE_LOCAL_TEST_DB={USE_LOCAL_TEST_DB})...")
    engine = get_engine()
    
    with engine.begin() as conn:
        # Tabela de PAs (Instituição)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS inst_instituicao (
                id SERIAL PRIMARY KEY,
                num_pa INTEGER NOT NULL,
                nome_pa VARCHAR(100) NOT NULL
            );
        """))

        # Tabela de Funcionários Gerais
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fun_funcionario (
                id SERIAL PRIMARY KEY,
                matricula INTEGER NOT NULL,
                nome VARCHAR(100) NOT NULL
            );
        """))

        # Tabela de Inadimplência / Filas
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crl_inadimplencia (
                id SERIAL PRIMARY KEY,
                fila VARCHAR(100) NOT NULL
            );
        """))

        # Tabela de Funcionários de Cobrança
        conn.execute(text("""
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
        """))

        # Tabela de Substituições
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fun_cobranca_substituicoes (
                id SERIAL PRIMARY KEY,
                substituto_id INTEGER NOT NULL,
                original_id INTEGER NOT NULL,
                data_inicio DATE NOT NULL,
                data_fim DATE NOT NULL,
                status_substituicao VARCHAR(20) NOT NULL DEFAULT 'AGENDADA',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # Tabela de Histórico de Auditoria de Trocas
        conn.execute(text("""
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
        """))

        # Povoar PAs
        conn.execute(text("DELETE FROM inst_instituicao;"))
        pas_data = [
            (1, "PA Sede - Chapecó"), (2, "PA Centro - São Miguel"), (3, "PA Pinhalzinho"),
            (4, "PA Maravilha"), (5, "PA Palmitos"), (6, "PA Itapiranga"),
            (7, "PA Xaxim"), (8, "PA Xanxerê"), (9, "PA Joaçaba"), (10, "PA Concórdia")
        ]
        for pa in pas_data:
            conn.execute(text("INSERT INTO inst_instituicao (num_pa, nome_pa) VALUES (:num_pa, :nome_pa)"), {"num_pa": pa[0], "nome_pa": pa[1]})

        # Povoar Filas de Inadimplência
        conn.execute(text("DELETE FROM crl_inadimplencia;"))
        filas_data = [
            "Fila 01 a 30 Dias", "Fila 31 a 60 Dias", "Fila 61 a 90 Dias", "Fila 91 a 120 Dias",
            "Fila 121 a 180 Dias", "Fila Acima 180 Dias", "Fila Pré-Judicial", "Fila Jurídico",
            "Fila Restituição", "Fila Veículos", "Fila Imóveis", "Fila Cartões", "Fila Cheque Especial",
            "Fila Empréstimo Pessoal", "Fila Crédito Rural"
        ]
        for fila in filas_data:
            conn.execute(text("INSERT INTO crl_inadimplencia (fila) VALUES (:fila)"), {"fila": fila})

        # Povoar Funcionários de Cobrança Fictícios
        conn.execute(text("DELETE FROM fun_funcionarios_cobranca;"))
        cobradores_mock = [
            ("Time Alpha", 1, 1001, "Carlos Eduardo Silva", "Fila 01 a 30 Dias", "(49) 99811-1001", 1),
            ("Time Alpha", 1, 1002, "Ana Paula Santos", "Fila 31 a 60 Dias", "(49) 99811-1002", 1),
            ("Time Alpha", 2, 1003, "Roberto Mendes", "Fila 61 a 90 Dias", "(49) 99811-1003", 1),
            ("Time Beta", 2, 1004, "Mariana Costa", "Fila 91 a 120 Dias", "(49) 99811-1004", 1),
            ("Time Beta", 3, 1005, "Lucas Ferreira", "Fila 121 a 180 Dias", "(49) 99811-1005", 1),
            ("Time Beta", 3, 1006, "Juliana Lima", "Fila Acima 180 Dias", "(49) 99811-1006", 1),
            ("Time Gamma", 4, 1007, "Fernanda Oliveira", "Fila Pré-Judicial", "(49) 99811-1007", 1),
            ("Time Gamma", 4, 1008, "Gabriel Souza", "Fila Jurídico", "(49) 99811-1008", 1),
            ("Time Delta", 5, 1009, "Camila Rodrigues", "Fila Restituição", "(49) 99811-1009", 1),
            ("Time Delta", 6, 1010, "Thiago Martins", "Fila Veículos", "(49) 99811-1010", 1),
            ("Time Epsilon", 7, 1011, "Patricia Ribeiro", "Fila Imóveis", "(49) 99811-1011", 1),
            ("Time Epsilon", 8, 1012, "Rodrigo Barbosa", "Fila Cartões", "(49) 99811-1012", 1),
        ]

        for item in cobradores_mock:
            conn.execute(text("""
                INSERT INTO fun_funcionarios_cobranca (times_cobranca, num_pa, matricula, cobrador, fila, telefone, status)
                VALUES (:times, :pa, :mat, :cob, :fila, :tel, :st)
            """), {
                "times": item[0], "pa": item[1], "mat": item[2],
                "cob": item[3], "fila": item[4], "tel": item[5], "st": item[6]
            })

    # Cria/Garante a View SQL vw_cobranca_roteamento
    garantir_view_roteamento()

    print("Banco de dados local semeado com sucesso! View 'vw_cobranca_roteamento' criada e pronta.")

if __name__ == "__main__":
    init_db()
