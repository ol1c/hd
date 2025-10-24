import argparse
import os
import random
import string
from datetime import datetime, date, time, timedelta

import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

fake = Faker("pl_PL")
rnd = random.Random()

def rand_time_on(day: date, start_hour=9, end_hour=18) -> datetime:
    """Losowa godzina w zakresie [start_hour, end_hour) danego dnia."""
    hour = rnd.randint(start_hour, max(start_hour, end_hour - 1))
    minute = rnd.randrange(0, 60)
    second = rnd.randrange(0, 60)
    return datetime.combine(day, time(hour, minute, second))

def clamp(dt: datetime, start: datetime, end: datetime) -> datetime:
    return min(max(dt, start), end)

def insert_rooms(cur, n_rooms: int):
    floors = [0, 1, 2, 3]
    rows = []
    for i in range(n_rooms):
        name = f"Sala {fake.color_name()} {rnd.choice(string.ascii_uppercase)}"
        floor = rnd.choice(floors)
        rows.append((name, floor))
    execute_values(cur, "INSERT INTO rooms (name, floor) VALUES %s ON CONFLICT DO NOTHING", rows)
    cur.execute("SELECT room_id FROM rooms")
    return [r[0] for r in cur.fetchall()]

def insert_exhibitions(cur, room_ids, n_exh: int, horizon_months: int = 6):
    """Tworzy wystawy o okresach trwania w +- horyzoncie czasowym względem dziś."""
    today = date.today()
    rows = []
    for _ in range(n_exh):
        # Okno wystawy: start w przedziale [-2m, +2m], czas trwania 2-60 dni
        start = today + timedelta(days=rnd.randint(-60, 60))
        duration = rnd.randint(2, 60)
        end = start + timedelta(days=duration)
        name = f"Wystawa {fake.word().title()} {rnd.randint(1,999)}"
        room_id = rnd.choice(room_ids)
        rows.append((name, start, end, room_id))
    execute_values(cur,
        "INSERT INTO exhibitions (name, exhibition_start, exhibition_end, room_id) VALUES %s",
        rows)
    cur.execute("SELECT exhibition_id, exhibition_start, exhibition_end, room_id FROM exhibitions")
    return cur.fetchall()  # list of (id, start, end, room_id)

def insert_exhibits(cur, n_exhibits: int):
    rows = []
    for _ in range(n_exhibits):
        name = f"{fake.word().title()} {fake.word().title()}"
        author = fake.name() if rnd.random() < 0.85 else None
        rows.append((name, author))
    execute_values(cur, "INSERT INTO exhibits (name, author) VALUES %s ON CONFLICT DO NOTHING", rows)
    cur.execute("SELECT exhibit_id FROM exhibits")
    return [r[0] for r in cur.fetchall()]

def link_exhibits(cur, exhibit_ids, exhibitions, min_per_exh=5, max_per_exh=20):
    links = []
    for exh_id, _, _, _ in exhibitions:
        k = rnd.randint(min_per_exh, max_per_exh)
        chosen = rnd.sample(exhibit_ids, k=min(k, len(exhibit_ids)))
        for ex_id in chosen:
            links.append((ex_id, exh_id))
    if links:
        execute_values(cur,
            "INSERT INTO exhibit_exhibitions (fk_exhibit_id, fk_exhibition_id) VALUES %s ON CONFLICT DO NOTHING",
            links)

def insert_visitors(cur, n_visitors: int):
    rows = []
    today = date.today()
    for _ in range(n_visitors):
        name = fake.name()
        # wizyty w oknie +-30 dni
        visit_day = today + timedelta(days=rnd.randint(-30, 30))
        entry = rand_time_on(visit_day, 9, 18)
        stay_minutes = rnd.randint(30, 240)
        exit_ = entry + timedelta(minutes=stay_minutes)
        # przytnij wyjście do 21:00 tego dnia
        exit_limit = datetime.combine(visit_day, time(21, 0, 0))
        exit_ = min(exit_, exit_limit)
        rows.append((name, visit_day, entry, exit_))
    execute_values(cur,
        "INSERT INTO visitors (name, visit_date, entry_time, exit_time) VALUES %s",
        rows)
    cur.execute("SELECT visitor_id, visit_date, entry_time, exit_time FROM visitors")
    return cur.fetchall()  # list of tuples

def insert_exhibition_visits(cur, visitors, exhibitions):
    """Tworzy odwiedziny wystaw przez zwiedzających, spójne z datami wystaw i oknem wizyty."""
    # map wystaw aktywnych danego dnia
    # Uwaga: upraszczamy — wybieramy wystawy gdzie visit_date ∈ [start, end].
    rows = []
    for visitor_id, vdate, v_entry, v_exit in visitors:
        # Wystawy czynne w dniu wizyty
        active = [(exh_id, start, end, room_id)
                  for (exh_id, start, end, room_id) in exhibitions
                  if start <= vdate <= end]
        if not active:
            continue
        # Ten zwiedzający odwiedzi 1..5 wystaw, łączny czas w oknie [v_entry, v_exit]
        k = rnd.randint(1, min(5, len(active)))
        picks = rnd.sample(active, k=k)
        # Ustal harmonogram: krótkie sloty, sekwencyjnie w oknie wizyty
        current = v_entry + timedelta(minutes=rnd.randint(0, 20))
        for exh_id, _, _, _ in picks:
            dur = rnd.randint(10, 45)
            e_in = current
            e_out = e_in + timedelta(minutes=dur)
            if e_out > v_exit:
                break
            rows.append((visitor_id, exh_id, e_in, e_out))
            current = e_out + timedelta(minutes=rnd.randint(2, 15))
    if rows:
        execute_values(cur,
            "INSERT INTO exhibition_visits (visitor_id, exhibition_id, entry_time, exit_time) VALUES %s",
            rows)

load_dotenv()
parser = argparse.ArgumentParser()
parser.add_argument("--db", default=os.getenv("DB_URL", "postgresql://vt_user:vt_pass@localhost:5432/visitortrack"))
parser.add_argument("--rooms", type=int, default=int(os.getenv("ROOMS", "8")))
parser.add_argument("--exhibitions", type=int, default=int(os.getenv("EXHIBITIONS", "12")))
parser.add_argument("--exhibits", type=int, default=int(os.getenv("EXHIBITS", "120")))
parser.add_argument("--visitors", type=int, default=int(os.getenv("VISITORS", "200")))
args = parser.parse_args()

conn = psycopg2.connect(args.db)
conn.autocommit = False
try:
    with conn.cursor() as cur:
        room_ids = insert_rooms(cur, args.rooms)
        exhibitions = insert_exhibitions(cur, room_ids, args.exhibitions)
        exhibit_ids = insert_exhibits(cur, args.exhibits)
        link_exhibits(cur, exhibit_ids, exhibitions)
        visitors = insert_visitors(cur, args.visitors)
        insert_exhibition_visits(cur, visitors, exhibitions)
    conn.commit()
    print("Wygenerowano dane VisitorTrack.")
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()