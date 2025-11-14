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


def save_dw_bulk(out_dir: Path, visit, date, time, room, visitor, exhibition, is_visited, exhibit):

    write_bulk(out_dir / "visit.bulk", visit,
               ["visit_id", "date_id", "entry_time", "exit_time", "exhibition_id",
                "room_id", "visitor_id", "visit_duration", "exhibits_total_value", "exhibits_count"])
    write_bulk(out_dir / "date.bulk", date, ["date_id", "year", "quarter", "month", "day", "day_name"])
    write_bulk(out_dir / "time.bulk", time, ["time_id", "hour", "minute", "second"])
    write_bulk(out_dir / "room.bulk", room,
               ["room_id", "name", "number", "flor", "effective_start_date", "effective_end_date"])
    write_bulk(out_dir / "visitor.bulk", visitor, ["visitor_id", "name"])
    write_bulk(out_dir / "exhibition.bulk", exhibition,
               ["exhibition_id", "name", "start_date", "end_date", "average_value"])
    write_bulk(out_dir / "is_visited.bulk", is_visited, ["visit_id", "exhibit_id"])
    write_bulk(out_dir / "exhibit.bulk", exhibit,
               ["exhibit_id", "number", "name", "author", "creation_era", "acquisition_duration",
                "type", "value", "effective_start_date", "effective_end_date"])
    print(f"BULK zapisane do: {out_dir.resolve()}")
