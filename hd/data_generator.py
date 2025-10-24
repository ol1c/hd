import argparse
import csv
import os
import random
import string
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import List, Dict, Any

from faker import Faker

fake = Faker("pl_PL")

def with_seed(seed: int | None):
    if seed is not None:
        random.seed(seed)
        try:
            Faker.seed(seed)
        except Exception:
            pass

def rand_time_on(day: date, start_hour=9, end_hour=18) -> datetime:
    hour = random.randint(start_hour, max(start_hour, end_hour - 1))
    minute = random.randrange(0, 60)
    second = random.randrange(0, 60)
    return datetime.combine(day, time(hour, minute, second))

def gen_rooms(n_rooms: int):
    rooms = []
    floors = [0, 1, 2, 3]
    for i in range(1, n_rooms + 1):
        name = f"Sala {fake.color_name()} {random.choice(string.ascii_uppercase)}"
        floor = random.choice(floors)
        rooms.append({
            "room_id": i,
            "name": name,
            "floor": floor,
        })
    return rooms

def gen_exhibitions(n_exh: int, rooms: list[dict]):
    exhibitions = []
    today = date.today()
    for i in range(1, n_exh + 1):
        start = today + timedelta(days=random.randint(-60, 60))
        duration = random.randint(2, 60)
        end = start + timedelta(days=duration)
        name = f"Wystawa {fake.word().title()} {random.randint(1,999)}"
        room = random.choice(rooms)
        exhibitions.append({
            "exhibition_id": i,
            "name": name,
            "exhibition_start": start.isoformat(),
            "exhibition_end": end.isoformat(),
            "room_id": room["room_id"],
        })
    return exhibitions

def gen_exhibits(n_exhibits: int):
    exhibits = []
    for i in range(1, n_exhibits + 1):
        name = f"{fake.word().title()} {fake.word().title()}"
        author = fake.name() if random.random() < 0.85 else None
        exhibits.append({
            "exhibit_id": i,
            "name": name,
            "author": author,
        })
    return exhibits

def gen_exhibit_exhibitions(exhibits: list[dict], exhibitions: list[dict], min_per_exh=5, max_per_exh=20):
    links: list[dict] = []
    exhibit_ids = [e["exhibit_id"] for e in exhibits]
    for exh in exhibitions:
        k = random.randint(min_per_exh, max_per_exh)
        chosen = random.sample(exhibit_ids, k=min(k, len(exhibit_ids)))
        for ex_id in chosen:
            links.append({
                "fk_exhibit_id": ex_id,
                "fk_exhibition_id": exh["exhibition_id"],
            })
    return links

def gen_visitors(n_visitors: int):
    visitors = []
    today = date.today()
    for i in range(1, n_visitors + 1):
        name = fake.name()
        visit_day = today + timedelta(days=random.randint(-30, 30))
        entry = rand_time_on(visit_day, 9, 18)
        stay_minutes = random.randint(30, 240)
        exit_ = entry + timedelta(minutes=stay_minutes)
        # przytnij wyjście do 21:00 tego dnia
        exit_limit = datetime.combine(visit_day, time(21, 0, 0))
        if exit_ > exit_limit:
            exit_ = exit_limit
        visitors.append({
            "visitor_id": i,
            "name": name,
            "visit_date": visit_day.isoformat(),
            "entry_time": entry.isoformat(),
            "exit_time": exit_.isoformat(),
        })
    return visitors

def gen_exhibition_visits(visitors: list[dict], exhibitions: list[dict]):
    visits = []
    visit_id = 1
    # Przerób zakresy dat wystaw na obiekty date dla filtrowania
    exhibitions_idx = [{
        "exhibition_id": e["exhibition_id"],
        "start": date.fromisoformat(e["exhibition_start"]),
        "end": date.fromisoformat(e["exhibition_end"]),
    } for e in exhibitions]

    for v in visitors:
        vdate = date.fromisoformat(v["visit_date"])
        v_entry = datetime.fromisoformat(v["entry_time"])
        v_exit = datetime.fromisoformat(v["exit_time"])

        active = [ex for ex in exhibitions_idx if ex["start"] <= vdate <= ex["end"]]
        if not active:
            continue

        k = random.randint(1, min(5, len(active)))
        picks = random.sample(active, k=k)

        current = v_entry + timedelta(minutes=random.randint(0, 20))
        for ex in picks:
            dur = random.randint(10, 45)
            e_in = current
            e_out = e_in + timedelta(minutes=dur)
            if e_out > v_exit:
                break
            visits.append({
                "visit_id": visit_id,
                "visitor_id": v["visitor_id"],
                "exhibition_id": ex["exhibition_id"],
                "entry_time": e_in.isoformat(),
                "exit_time": e_out.isoformat(),
            })
            visit_id += 1
            current = e_out + timedelta(minutes=random.randint(2, 15))

    return visits

def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

parser = argparse.ArgumentParser(description="VisitorTrack data generator")
parser.add_argument("--out-dir", default="db", help="Katalog wyjściowy na pliki CSV")
parser.add_argument("--rooms", type=int, default=15)
parser.add_argument("--exhibitions", type=int, default=15)
parser.add_argument("--exhibits", type=int, default=15*15)
parser.add_argument("--visitors", type=int, default=15)
parser.add_argument("--min-per-exhibition", type=int, default=5)
parser.add_argument("--max-per-exhibition", type=int, default=20)
parser.add_argument("--seed", type=int, default=None, help="Ustal ziarno RNG dla powtarzalności wyników")
args = parser.parse_args()

with_seed(args.seed)
out_dir = Path(args.out_dir)

rooms = gen_rooms(args.rooms)
exhibitions = gen_exhibitions(args.exhibitions, rooms)
exhibits = gen_exhibits(args.exhibits)
exhibit_exhibitions = gen_exhibit_exhibitions(exhibits, exhibitions, args.min_per_exhibition, args.max_per_exhibition)
visitors = gen_visitors(args.visitors)
exhibition_visits = gen_exhibition_visits(visitors, exhibitions)

write_csv(out_dir / "rooms.csv", rooms, ["room_id", "name", "floor"])
write_csv(out_dir / "exhibitions.csv", exhibitions, ["exhibition_id", "name", "exhibition_start", "exhibition_end", "room_id"])
write_csv(out_dir / "exhibits.csv", exhibits, ["exhibit_id", "name", "author"])
write_csv(out_dir / "exhibit_exhibitions.csv", exhibit_exhibitions, ["fk_exhibit_id", "fk_exhibition_id"])
write_csv(out_dir / "visitors.csv", visitors, ["visitor_id", "name", "visit_date", "entry_time", "exit_time"])
write_csv(out_dir / "exhibition_visits.csv", exhibition_visits, ["visit_id", "visitor_id", "exhibition_id", "entry_time", "exit_time"])

print(f"CSV zapisane do: {out_dir.resolve()}")
