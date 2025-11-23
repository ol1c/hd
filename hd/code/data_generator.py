import random
from datetime import datetime, date, time, timedelta
from faker import Faker

fake = Faker("en_GB")
EXHIBIT_TYPES = ["rzeźba", "obraz", "fotografia", "instalacja", "grafika"]


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


def _first_day_of_month(d: date) -> date:
    return date(d.year, d.month, 1)


def _first_day_next_month(d: date) -> date:
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def _month_end(d: date) -> date:
    return _first_day_next_month(d) - timedelta(days=1)


def _overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    # True if ranges [a_start, a_end] and [b_start, b_end] overlap (inclusive)
    return not (a_end < b_start or b_end < a_start)


def _as_date(d: any) -> date:
    """Zwraca datetime.date z wejścia będącego date albo ISO-YYYY-MM-DD string."""
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        return date.fromisoformat(d)
    raise TypeError(f"Unsupported date type: {type(d)!r}")


def gen_rooms(n_rooms: int):
    rooms = []
    floors = [0, 1, 2]
    for i in range(1, n_rooms + 1):
        name = f"Room {i}"
        floor = random.choice(floors)
        rooms.append({
            "room_id": i,
            "name": name,
            "floor": floor,
        })
    return rooms


def gen_exhibitions(n_exh: int, rooms: list[dict]):
    exhibitions = []
    bookings = {room["room_id"]: [] for room in rooms}
    room_ids = [room["room_id"] for room in rooms]

    base_month = _first_day_of_month(date.today())
    prev_start = base_month

    for i in range(1, n_exh + 1):
        candidate_month = prev_start

        while True:
            candidate_start = _first_day_of_month(candidate_month)
            candidate_end = _month_end(candidate_start)

            free_rooms = []

            for rid in room_ids:
                is_free = True
                for b_start, b_end in bookings[rid]:
                    if _overlaps(b_start, b_end, candidate_start, candidate_end):
                        is_free = False
                        break
                if is_free:
                    free_rooms.append(rid)

            if free_rooms:
                assigned_room = random.choice(free_rooms)
                bookings[assigned_room].append((candidate_start, candidate_end))
                exhibitions.append({
                    "exhibition_id": i,
                    "name": f"Exhibition {i}",
                    "exhibition_start": candidate_start.isoformat(),
                    "exhibition_end": candidate_end.isoformat(),
                    "room_id": assigned_room,
                })
                prev_start = candidate_start
                break

            candidate_month = _first_day_next_month(candidate_month)
    return exhibitions


def gen_exhibits(n_exhibits: int):
    exhibits = []
    current_year = date.today().year
    for i in range(1, n_exhibits + 1):
        name = f"{fake.word().title()} {fake.word().title()}"
        author = fake.name() if random.random() < 0.85 else "Pieter Stashkov"
        creation_year = random.randint(1, current_year)
        acquisition_year = random.randint(2014, current_year)
        typ = random.choice(EXHIBIT_TYPES)
        value = round(random.uniform(1, 1_001_000), 2)
        exhibits.append({
            "exhibit_id": i,
            "name": name,
            "author": author,
            "creation_year": creation_year,
            "acquisition_year": acquisition_year,
            "type": typ,
            "value": value,
        })
    return exhibits


def gen_exhibit_exhibitions(exhibits: list[dict], exhibitions: list[dict], min_per_exh=5, max_per_exh=20):
    links: list[dict] = []

    occupied: dict[tuple[int, int], set[int]] = {}
    exhibit_ids = [e["exhibit_id"] for e in exhibits]
    for exh in exhibitions:
        exh_id = exh["exhibition_id"]
        start = _as_date(exh["exhibition_start"])
        month_key = (start.year, start.month)

        occupied.setdefault(month_key, set())

        random.shuffle(exhibit_ids)

        # assigned = False
        k = random.randint(min_per_exh, max_per_exh)
        n = 0
        for e in exhibit_ids:
            if e in occupied[month_key]:
                continue

            links.append({
                "exhibit_id": e,
                "exhibition_id": exh_id,
            })

            occupied[month_key].add(e)
            # assigned = True
            n += 1
            if n >= k:
                break
    return links


def gen_visitors(n_visitors: int, exhibitions: list[dict]):
    visitors = []
    start_date = date.fromisoformat(exhibitions[0]['exhibition_start'])
    end_date = date.fromisoformat(exhibitions[-1]['exhibition_end'])
    span_days = (end_date - start_date).days
    for i in range(1, n_visitors + 1):
        name = fake.name()
        visit_day = start_date + timedelta(days=random.randint(0, span_days))
        entry = rand_time_on(visit_day, 9, 18)
        stay_minutes = random.randint(30, 240)
        exit_ = entry + timedelta(minutes=stay_minutes)

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
    visitors.sort(key=lambda v: v["visit_date"])
    for i in range(0, n_visitors):
        visitors[i]["visitor_id"] = i + 1
    return visitors


def gen_exhibition_visits(visitors: list[dict], exhibitions: list[dict]):
    visits = []
    visit_id = 1

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


def gen_data(args):
    with_seed(args.seed)
    rooms = gen_rooms(args.rooms)
    exhibitions = gen_exhibitions(args.exhibitions, rooms)
    exhibits = gen_exhibits(args.exhibits)
    exhibit_exhibitions = gen_exhibit_exhibitions(exhibits, exhibitions, args.min_per_exhibition,
                                                  args.max_per_exhibition)
    visitors = gen_visitors(args.visitors, exhibitions)
    exhibition_visits = gen_exhibition_visits(visitors, exhibitions)
    return rooms, exhibitions, exhibits, exhibit_exhibitions, visitors, exhibition_visits
