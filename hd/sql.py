from datetime import datetime, date
from typing import List, Optional


def sql_str(value: Optional[str]) -> str:
    if value is None:
        return "NULL"
    # escapowanie: podwajamy pojedyncze cudzysłowy i backslash
    s = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{s}'"

def sql_date(d: date) -> str:
    return f"'{d.strftime('%Y-%m-%d')}'"

def sql_datetime(dt: str) -> str:
    # return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
    date, time = dt.split('T')
    return f"{date} {time}"

def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def write_insert(fh, table: str, columns: List[str], rows: List[List[str]], rows_per_insert: int = 500):
    if not rows:
        return
    col_list = ", ".join(f"`{c}`" for c in columns)
    for part in chunked(rows, rows_per_insert):
        values = ",\n  ".join("(" + ", ".join(r) + ")" for r in part)
        fh.write(f"INSERT INTO `{table}` ({col_list}) VALUES\n  {values};\n\n")