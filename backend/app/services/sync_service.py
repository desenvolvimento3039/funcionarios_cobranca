import io
import zipfile
import xml.etree.ElementTree as ET
from psycopg2.extras import execute_values
from app.core.database import get_psycopg2_conn

def parse_excel_cobranca_bytes(file_bytes=None, file_path=None):
    """Lê o Excel de cobrança e retorna lista de tuplas (times_cobranca, num_pa, matricula, cobrador, fila, telefone)."""
    source = io.BytesIO(file_bytes) if file_bytes else file_path

    with zipfile.ZipFile(source) as z:
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for t in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                text_content = ''.join([node.text for node in t.iter() if node.text])
                shared_strings.append(text_content)

        sheet_xml = z.read('xl/worksheets/sheet1.xml')
        tree = ET.fromstring(sheet_xml)
        rows = []
        for row in tree.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            r = []
            for cell in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                val = cell.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                t_attr = cell.attrib.get('t')
                if val is not None:
                    v = val.text
                    if t_attr == 's' and v is not None:
                        v = shared_strings[int(v)]
                    r.append(v.strip() if v else '')
                else:
                    r.append('')
            rows.append(r)

    data_rows = []
    for r in rows[1:]:
        if len(r) >= 5 and any(r):
            times_cobranca = str(r[0]).strip() if r[0] else ""
            try:
                num_pa = int(float(r[1])) if r[1] else 0
            except (ValueError, TypeError):
                num_pa = 0
            try:
                matricula = int(float(r[2])) if r[2] else 0
            except (ValueError, TypeError):
                matricula = 0
            cobrador = str(r[3]).strip() if len(r) > 3 and r[3] else ""
            fila = str(r[4]).strip()[:100] if len(r) > 4 and r[4] else ""
            telefone = str(r[5]).strip()[:50] if len(r) > 5 and r[5] else ""

            if times_cobranca and cobrador and fila:
                data_rows.append((times_cobranca, num_pa, matricula, cobrador, fila, telefone))
    return data_rows

def sync_cobranca_rows_to_dbs(rows, target_dbs=None):
    """Sincroniza registros de cobrança na tabela fun_funcionarios_cobranca via upsert."""
    if target_dbs is None:
        target_dbs = ["SicoobSMO", "LeCom"]
    results = {}
    for dbname in target_dbs:
        conn = None
        try:
            conn = get_psycopg2_conn(dbname)
            cur = conn.cursor()

            # Criação da tabela de funcionários
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.fun_funcionarios_cobranca (
                    times_cobranca VARCHAR(100) NULL,
                    num_pa INTEGER NULL,
                    matricula INTEGER NULL,
                    cobrador VARCHAR(100) NULL,
                    fila VARCHAR(100) NULL,
                    telefone VARCHAR(50) NULL,
                    status INTEGER NOT NULL DEFAULT 1
                );
            """)
            cur.execute("ALTER TABLE public.fun_funcionarios_cobranca ADD COLUMN IF NOT EXISTS id SERIAL;")
            cur.execute("ALTER TABLE public.fun_funcionarios_cobranca ADD COLUMN IF NOT EXISTS status INTEGER NOT NULL DEFAULT 1;")
            
            # Garante a restrição UNIQUE para a FK (ou PRIMARY KEY) para referenciar
            try:
                cur.execute("ALTER TABLE public.fun_funcionarios_cobranca ADD PRIMARY KEY (id);")
            except Exception:
                pass # Caso já exista
                
            cur.execute("CREATE INDEX IF NOT EXISTS idx_func_cobr_matricula ON public.fun_funcionarios_cobranca (matricula);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_func_cobr_pa_fila ON public.fun_funcionarios_cobranca (num_pa, fila);")

            # Criação da tabela de histórico de substituições
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.fun_cobranca_substituicoes (
                    id SERIAL PRIMARY KEY,
                    substituto_id INTEGER NOT NULL REFERENCES public.fun_funcionarios_cobranca(id) ON DELETE CASCADE,
                    original_id INTEGER NOT NULL REFERENCES public.fun_funcionarios_cobranca(id) ON DELETE CASCADE,
                    data_inicio DATE NOT NULL,
                    data_fim DATE NOT NULL,
                    status_substituicao VARCHAR(20) NOT NULL DEFAULT 'AGENDADA',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

            # Processo de UPSERT
            cur.execute("""
                CREATE TEMP TABLE stg_cobranca (
                    times_cobranca varchar, num_pa integer, matricula integer,
                    cobrador varchar, fila varchar, telefone varchar
                ) ON COMMIT DROP;
            """)
            execute_values(cur, "INSERT INTO stg_cobranca VALUES %s", rows)

            cur.execute("""
                UPDATE public.fun_funcionarios_cobranca t
                SET times_cobranca = s.times_cobranca,
                    cobrador = s.cobrador,
                    telefone = s.telefone
                FROM stg_cobranca s
                WHERE t.matricula = s.matricula AND t.num_pa = s.num_pa AND t.fila = s.fila;
            """)
            updated = cur.rowcount

            cur.execute("""
                INSERT INTO public.fun_funcionarios_cobranca (times_cobranca, num_pa, matricula, cobrador, fila, telefone)
                SELECT s.times_cobranca, s.num_pa, s.matricula, s.cobrador, s.fila, s.telefone
                FROM stg_cobranca s
                WHERE NOT EXISTS (
                    SELECT 1 FROM public.fun_funcionarios_cobranca t
                    WHERE t.matricula = s.matricula AND t.num_pa = s.num_pa AND t.fila = s.fila
                );
            """)
            inserted = cur.rowcount
            conn.commit()

            cur.execute("SELECT count(*) FROM public.fun_funcionarios_cobranca;")
            total = cur.fetchone()[0]
            results[dbname] = {"updated": updated, "inserted": inserted, "total": total}
        except Exception as e:
            if conn: conn.rollback()
            raise e
        finally:
            if conn: conn.close()
    return results
