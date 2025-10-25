import csv
from pathlib import Path
from typing import List, Dict, Any


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def save_exhibits_csv(out_dir: Path, exhibits):
    write_csv(out_dir / "StockCSV.csv", exhibits, ["exhibit_id", "name", "author"])
    print(f"StockCSV zapisane do: {out_dir.resolve() / "StockCSV.csv"}")


def save_csv(out_dir: Path, rooms, exhibitions, exhibits, exhibit_exhibitions, visitors, exhibition_visits):
    write_csv(out_dir / "rooms.csv", rooms, ["room_id", "name", "floor"])
    write_csv(out_dir / "exhibitions.csv", exhibitions,
              ["exhibition_id", "name", "exhibition_start", "exhibition_end", "room_id"])
    write_csv(out_dir / "exhibits.csv", exhibits, ["exhibit_id", "name", "author"])
    write_csv(out_dir / "exhibit_exhibitions.csv", exhibit_exhibitions, ["fk_exhibit_id", "fk_exhibition_id"])
    write_csv(out_dir / "visitors.csv", visitors, ["visitor_id", "name", "visit_date", "entry_time", "exit_time"])
    write_csv(out_dir / "exhibition_visits.csv", exhibition_visits,
              ["visit_id", "visitor_id", "exhibition_id", "entry_time", "exit_time"])

    print(f"CSV zapisane do: {out_dir.resolve()}")

    save_exhibits_csv(out_dir, exhibits)