import io
import csv
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Tuple, Union

def parse_excel_bytes_or_path(file_bytes: Union[bytes, None] = None, file_path: Union[str, None] = None) -> List[Tuple[str, int, int, str, str, str]]:
    """
    Lê um arquivo Excel (.xlsx) via zipfile sem depender de pandas/openpyxl,
    retornando tuplas (times_cobranca, num_pa, matricula, cobrador, fila, telefone).
    """
    source = io.BytesIO(file_bytes) if file_bytes else file_path
    if not source:
        return []

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
                    if t_attr == 's' and v is not None and v.isdigit() and int(v) < len(shared_strings):
                        v = shared_strings[int(v)]
                    r.append(v.strip() if v else '')
                else:
                    r.append('')
            rows.append(r)

    parsed_rows = []
    for r in rows[1:]:  # Pula o cabeçalho
        if len(r) >= 5 and any(r):
            times_cobranca = r[0] if len(r) > 0 else ""
            num_pa_raw = r[1] if len(r) > 1 else "0"
            matricula_raw = r[2] if len(r) > 2 else "0"
            cobrador = r[3] if len(r) > 3 else ""
            fila = r[4] if len(r) > 4 else ""
            telefone = r[5] if len(r) > 5 else ""

            try:
                num_pa = int(float(num_pa_raw)) if num_pa_raw else 0
            except ValueError:
                num_pa = 0

            try:
                matricula = int(float(matricula_raw)) if matricula_raw else 0
            except ValueError:
                matricula = 0

            if cobrador or fila:
                parsed_rows.append((times_cobranca[:100], num_pa, matricula, cobrador[:100], fila[:100], telefone[:50]))

    return parsed_rows

def parse_financiamento_excel_bytes_or_path(file_bytes=None, file_path=None) -> List[Tuple[str, str, str, str]]:
    """
    Lê um arquivo Excel para Financiamento Rural, retornando (item, enquadramento, linha, isolado).
    """
    source = io.BytesIO(file_bytes) if file_bytes else file_path
    if not source:
        return []

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
                    if t_attr == 's' and v is not None and v.isdigit() and int(v) < len(shared_strings):
                        v = shared_strings[int(v)]
                    r.append(v.strip() if v else '')
                else:
                    r.append('')
            rows.append(r)

    data_rows = []
    for r in rows[1:]:
        if len(r) >= 4 and any(r):
            item = (r[0] if len(r) > 0 else "")[:100]
            enquadramento = r[1] if len(r) > 1 else ""
            linha = (r[2] if len(r) > 2 else "")[:45]
            isolado = r[3] if len(r) > 3 else "Não"
            if item:
                data_rows.append((item, enquadramento, linha, isolado or "Não"))
    return data_rows

def generate_csv_cobranca(rows: List[dict]) -> str:
    """Gera string CSV formatada em UTF-8 com BOM para download."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["ID", "Time", "PA", "Matrícula", "Cobrador", "Fila", "Telefone", "Status", "Substituto", "Período Substituição"])
    for r in rows:
        status_str = "Ativo" if r.get("status", 1) == 1 else "Inativo"
        sub_nome = r.get("substituto_nome", "") or ""
        periodo = ""
        if r.get("data_inicio_substituicao") and r.get("data_fim_substituicao"):
            periodo = f"{r['data_inicio_substituicao']} até {r['data_fim_substituicao']}"
        writer.writerow([
            r.get("id"), r.get("times_cobranca"), r.get("num_pa"), r.get("matricula"),
            r.get("cobrador"), r.get("fila"), r.get("telefone"), status_str, sub_nome, periodo
        ])
    return output.getvalue()

def generate_csv_model_cobranca() -> str:
    """Gera modelo CSV de importação."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["times_cobranca", "num_pa", "matricula", "cobrador", "fila", "telefone"])
    writer.writerow(["Time Alpha", "1", "1001", "João da Silva", "Fila 01 a 30 Dias", "(49) 99999-0000"])
    writer.writerow(["Time Beta", "2", "1002", "Maria Oliveira", "Fila 31 a 60 Dias", "(49) 98888-1111"])
    return output.getvalue()
