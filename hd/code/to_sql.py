import argparse
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

def save_sql(args, rooms, exhibitions, exhibits, exhibit_exhibitions, visitors, exhibition_visits):
    with open(args.out_sql, "w", encoding="utf-8") as fh:
        fh.write("SET autocommit=0;\nSTART TRANSACTION;\n\n")

        # INSERT-y: zachowujemy kolejność zależności (rooms -> exhibitions -> exhibits -> exhibit_exhibitions -> visitors -> exhibition_visits)
        # rooms
        rooms_cols = ["room_id", "name", "floor"]
        rooms_rows = [[str(r["room_id"]), sql_str(r["name"]), str(r["floor"])] for r in rooms]
        write_insert(fh, "rooms", rooms_cols, rooms_rows, args.rows_per_insert)

        # exhibitions
        ex_cols = ["exhibition_id", "name", "exhibition_start", "exhibition_end", "room_id"]
        ex_rows = [[
            str(e["exhibition_id"]),
            sql_str(e["name"]),
            e["exhibition_start"],
            e["exhibition_end"],
            str(e["room_id"])
        ] for e in exhibitions]
        write_insert(fh, "exhibitions", ex_cols, ex_rows, args.rows_per_insert)

        # exhibits
        eb_cols = ["exhibit_id", "name", "author"]
        eb_rows = [[
            str(x["exhibit_id"]),
            sql_str(x["name"]),
            sql_str(x["author"]) if x["author"] else "NULL"
        ] for x in exhibits]
        write_insert(fh, "exhibits", eb_cols, eb_rows, args.rows_per_insert)

        # exhibit_exhibitions (łącznik)
        link_cols = ["fk_exhibit_id", "fk_exhibition_id"]
        link_rows = [[str(l["fk_exhibit_id"]), str(l["fk_exhibition_id"])] for l in exhibit_exhibitions]
        write_insert(fh, "exhibit_exhibitions", link_cols, link_rows, args.rows_per_insert)

        # visitors
        v_cols = ["visitor_id", "name", "visit_date", "entry_time", "exit_time"]
        v_rows = [[
            str(v["visitor_id"]),
            sql_str(v["name"]),
            v["visit_date"],
            sql_datetime(v["entry_time"]),
            sql_datetime(v["exit_time"])
        ] for v in visitors]
        write_insert(fh, "visitors", v_cols, v_rows, args.rows_per_insert)

        # exhibition_visits
        ev_cols = ["visit_id", "visitor_id", "exhibition_id", "entry_time", "exit_time"]
        ev_rows = [[
            str(ev["visit_id"]),
            str(ev["visitor_id"]),
            str(ev["exhibition_id"]),
            sql_datetime(ev["entry_time"]),
            sql_datetime(ev["exit_time"])
        ] for ev in exhibition_visits]
        write_insert(fh, "exhibition_visits", ev_cols, ev_rows, args.rows_per_insert)

        fh.write("COMMIT;\n")

    print(f"INSERT zapisane do: {args.out_sql}")
