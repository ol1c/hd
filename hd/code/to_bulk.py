from pathlib import Path
from typing import List, Dict, Any, Optional

from to_csv import save_exhibits_csv


def tsv_escape(value: Optional[Any]) -> str:
    if value is None:
        return r"\N"
    else:
        s = str(value)
    # nie wiem co się dzieje ale buja
    s = s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")
    return s


def write_bulk(path: Path, rows: List[Dict[str, Any]], columns: List[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        for r in rows:
            line = "|".join(tsv_escape(r.get(col)) for col in columns)
            f.write(line + "\n")


def save_bulk(out_dir: Path, rooms, exhibitions, exhibits, exhibit_exhibitions, visitors, exhibition_visits):
    write_bulk(out_dir / "rooms.bulk", rooms, ["room_id", "name", "floor"])
    write_bulk(out_dir / "exhibitions.bulk", exhibitions,
               ["exhibition_id", "name", "exhibition_start", "exhibition_end", "room_id"])
    write_bulk(out_dir / "exhibits.bulk", exhibits, ["exhibit_id", "name", "author"])
    write_bulk(out_dir / "exhibit_exhibitions.bulk", exhibit_exhibitions, ["fk_exhibit_id", "fk_exhibition_id"])
    write_bulk(out_dir / "visitors.bulk", visitors, ["visitor_id", "name", "visit_date", "entry_time", "exit_time"])
    write_bulk(out_dir / "exhibition_visits.bulk", exhibition_visits,
               ["visit_id", "visitor_id", "exhibition_id", "entry_time", "exit_time"])

    print(f"BULK zapisane do: {out_dir.resolve()}")

    save_exhibits_csv(out_dir, exhibits)
