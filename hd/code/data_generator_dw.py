import random
from datetime import datetime, date, time, timedelta
from faker import Faker

fake = Faker("en_GB")
EXHIBIT_TYPES = ["rzeźba", "obraz", "fotografia", "instalacja", "grafika"]
EXHIBIT_VALUES = ["<10 000", "<100 000", "<1 000 000", ">1 000 000"]
CREATION_ERAS = ["prehistoria", "starożytność", "średniowiecze", "nowożytność", "czasy współczesne"]
ACQUISITION_DURATIONS = ["<1", "<5", "<10", ">=10"]
DAY_NAMES = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
MAP_VALUES = {
    "<10 000": 5_000,
    "<100 000": 55_000,
    "<1 000 000": 550_000,
    ">1 000 000": 1_500_000,
}


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
    """True if ranges [a_start, a_end] and [b_start, b_end] overlap (inclusive)"""
    return not (a_end < b_start or b_end < a_start)


def _as_date(d: any) -> date:
    """Zwraca datetime.date z wejścia będącego date albo ISO-YYYY-MM-DD string."""
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        return date.fromisoformat(d)
    raise TypeError(f"Unsupported date type: {type(d)!r}")


def _as_time(d: any) -> datetime:
    """Zwraca datetime.datetime z wejścia będącego datetime albo ISO-YYYY-MM-DD HH:MM:SS string."""
    if isinstance(d, datetime):
        return d
    if isinstance(d, str):
        s = d.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(s)
        except ValueError as e:
            raise ValueError(f"Invalid ISO datetime string: {d!r}") from e
    raise TypeError(f"Unsupported datetime type: {type(d)!r}")


def gen_date(start_date: date, end_date: date):
    dates = []
    current = start_date
    idx = 1
    while current <= end_date:
        month = current.month
        quarter = (month - 1) // 3 + 1  # 1..4
        dates.append({
            "date_id": idx,
            "year": current.year,
            "quarter": quarter,
            "month": month,
            "day": current.day,
            "day_name": DAY_NAMES[current.weekday()],
        })
        current += timedelta(days=1)
        idx += 1
    return dates


def gen_time():
    time = []
    for hour in range(0, 24):
        for minute in range(0, 60):
            for second in range(0, 60):
                time.append({
                    "time_id": hour * 3600 + minute * 60 + second + 1,
                    "hour": hour,
                    "minute": minute,
                    "second": second,
                })
    return time


def gen_rooms(n_rooms: int, n_rooms_changed: int, start_date: date, end_date: date):
    rooms = []
    floors = [0, 1, 2]
    for i in range(1, n_rooms + 1):
        name = f"Room {i}"
        floor = random.choice(floors)
        rooms.append({
            "room_id": i,
            "number": i,
            "name": name,
            "floor": floor,
            "effective_start_date": start_date.isoformat(),
            "effective_end_date": end_date.isoformat(),
        })
    new_date = start_date + timedelta(days=random.randint(1, (end_date - start_date).days // 2))
    for i in range(1, n_rooms_changed + 1):
        room_id = random.randrange(0, len(rooms))
        rooms[room_id]["effective_end_date"] = new_date - timedelta(days=1)
        rooms.append({
            "room_id": i + n_rooms,
            "number": rooms[room_id]['number'],
            "name": f"Room {i + n_rooms}",
            "floor": rooms[room_id]['floor'],
            "effective_start_date": new_date.isoformat(),
            "effective_end_date": end_date.isoformat(),
        })
        remaining = (end_date - new_date).days
        if remaining < 1:
            break
        new_date = new_date + timedelta(days=random.randint(1, remaining))
    return rooms


def gen_exhibitions(n_exh: int, n_rooms: int):
    exhibitions = []
    bookings = {i: [] for i in range(1, n_rooms + 1)}
    room_ids = [i for i in range(1, n_rooms + 1)]

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
                    "room_number": assigned_room,
                    "start_date": None,
                    "end_date": None,
                    "average_value": None,
                    "exhibits_count": 0,
                    "exhibits_total_value": 0,
                })
                prev_start = candidate_start
                break

            candidate_month = _first_day_next_month(candidate_month)
    return exhibitions


def gen_exhibits(n_exhibits: int, n_exhibits_changed: int, start_date: date, end_date: date):
    exhibits = []
    for i in range(1, n_exhibits + 1):
        name = f"{fake.word().title()} {fake.word().title()}"
        author = fake.name() if random.random() < 0.85 else "Pieter Stashkov"
        creation_era = random.choice(CREATION_ERAS)
        acquisition_duration = random.choice(ACQUISITION_DURATIONS)
        typ = random.choice(EXHIBIT_TYPES)
        value = random.choice(EXHIBIT_VALUES)
        exhibits.append({
            "exhibit_id": i,
            "number": i,
            "name": name,
            "author": author,
            "creation_era": creation_era,
            "acquisition_duration": acquisition_duration,
            "type": typ,
            "value": value,
            "effective_start_date": start_date.isoformat(),
            "effective_end_date": end_date.isoformat(),
        })
    new_date = start_date + timedelta(days=random.randint(1, (end_date - start_date).days // 2))
    for i in range(1, n_exhibits_changed + 1):
        exhibit_id = random.randrange(0, len(exhibits))
        exhibits[exhibit_id]["effective_end_date"] = new_date - timedelta(days=1)
        new_value = random.choice(EXHIBIT_VALUES)
        while new_value == exhibits[exhibit_id]["value"]:
            new_value = random.choice(EXHIBIT_VALUES)
        exhibits.append({
            "exhibit_id": i + n_exhibits,
            "number": exhibits[exhibit_id]['number'],
            "name": exhibits[exhibit_id]["name"],
            "author": exhibits[exhibit_id]['author'],
            "creation_era": exhibits[exhibit_id]['creation_era'],
            "acquisition_duration": exhibits[exhibit_id]['acquisition_duration'],
            "type": exhibits[exhibit_id]['type'],
            "value": new_value,
            "effective_start_date": new_date.isoformat(),
            "effective_end_date": end_date.isoformat(),
        })
        remaining = (end_date - new_date).days
        if remaining < 1:
            break
        new_date = new_date + timedelta(days=random.randint(1, remaining))

    return exhibits


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


def _covers_entire_period(versions: list[dict], start: date, end: date) -> list[dict]:
    """Zwraca liste wszystkich obiektów aktywnych w danym przedziale czasu"""
    n = len(versions)
    if n == 0:
        return []

    # znajdź wersję aktywną na start
    idx = None
    for i, v in enumerate(versions):
        v_start = _as_date(v["effective_start_date"])
        v_end = _as_date(v["effective_end_date"])
        if v_start <= start <= v_end:
            idx = i
            break
    if idx is None:
        return []

    chain = [versions[idx]]
    cur_end = _as_date(versions[idx]["effective_end_date"])
    if cur_end >= end:
        return chain

    i = idx
    while cur_end < end:
        i += 1
        if i >= n:
            return []
        nxt = versions[i]
        nxt_start = _as_date(nxt["effective_start_date"])
        nxt_end = _as_date(nxt["effective_end_date"])

        # Dopuszczamy overlap (nxt_start <= cur_end + 1). Jeśli jest luka (nxt_start > cur_end + 1), nie da się pokryć.
        if nxt_start > (cur_end + timedelta(days=1)):
            return []

        chain.append(nxt)
        cur_end = max(cur_end, nxt_end)

    return chain


def gen_exhibit_exhibitions(exhibits: list[dict], exhibitions: list[dict], min_per_exh=5, max_per_exh=20):
    links: list[dict] = []
    by_number: dict[int, list[dict]] = {}
    for ex in exhibits:
        num = ex["number"]
        by_number.setdefault(num, []).append(ex)
    for num in by_number:
        by_number[num].sort(key=lambda v: _as_date(v["effective_start_date"]))

    occupied: dict[tuple[int, int], set[int]] = {}
    all_numbers = list(by_number.keys())

    for exh in exhibitions:
        exh_id = exh["exhibition_id"]
        start = _as_date(exh["exhibition_start"])
        end = _as_date(exh["exhibition_end"])
        month_key = (start.year, start.month)

        occupied.setdefault(month_key, set())

        random.shuffle(all_numbers)

        # assigned = False
        k = random.randint(min_per_exh, max_per_exh)
        n = 0
        for num in all_numbers:
            if num in occupied[month_key]:
                continue

            versions = by_number[num]
            chain = _covers_entire_period(versions, start, end)
            if chain is None:
                continue

            # dodaj linki dla każdej wersji użytej w trakcie wystawy
            for v in chain:
                links.append({
                    "exhibit_id": v["exhibit_id"],
                    "exhibition_id": exh_id,
                })
                exh["exhibits_count"] += 1

            occupied[month_key].add(num)
            # assigned = True
            n += 1
            if n >= k:
                break

    return links


def _add_avg_value_to_exhibitions(exhibitions, exhibits, links):
    """
    Uzupełnia w miejscu pole 'average_value' na podstawie przypisanych eksponatów.
    - links zawiera rekordy {"exhibit_id", "exhibition_id"}.
    """
    exhibits_by_id = {e["exhibit_id"]: e for e in exhibits}
    ids_by_exh = {}
    for link in links:
        ids_by_exh.setdefault(link["exhibition_id"], []).append(link["exhibit_id"])

    for exhibition in exhibitions:
        vals = []
        for eid in ids_by_exh.get(exhibition["exhibition_id"], []):
            cat = exhibits_by_id[eid]["value"]
            if cat in MAP_VALUES:
                vals.append(MAP_VALUES[cat])
        if not vals:
            exhibition["average_value"] = None
            continue
        sum_vals = sum(vals)
        avg = sum_vals / len(vals)
        exhibition["exhibits_total_value"] = sum_vals
        exhibition["average_value"] = (
            "<10000" if avg < 10_000 else
            "<100 000" if avg < 100_000 else
            "<1 000 000" if avg < 1_000_000 else
            ">1 000 000"
        )


def _get_date_id(link: date, dates: list[dict]):
    """
        Zwraca date_id (YYYYMMDD) dla podanej daty 'link', jeśli znajduje się w liście 'dates'.
        Rzuca ValueError, jeśli nie ma takiej daty w liście.
        """
    y, m, d = link.year, link.month, link.day
    for rec in dates:
        if rec["year"] == y and rec["month"] == m and rec["day"] == d:
            # jeśli gen_date nie dodał date_id, policz na podstawie pól
            return rec["date_id"]
    raise ValueError(f"Data {link.isoformat()} nie występuje w przekazanej liście 'dates'.")


def _get_time_id(link: datetime):
    """
    Zwraca time_id w zakresie 1..86400 dla podanego czasu.
    Nie używa listy, bo id jest deterministyczne: 1 dla 00:00:00, 86400 dla 23:59:59.
    """
    h = link.hour
    m = link.minute
    s = link.second
    if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
        raise ValueError(f"Nieprawidłowy czas: {h:02d}:{m:02d}:{s:02d}")
    return h * 3600 + m * 60 + s + 1


def _add_date_id_to_exhibitions(exhibitions, dates):
    for exhibition in exhibitions:
        exhibition["start_date"] = _get_date_id(_as_date(exhibition["exhibition_start"]), dates)
        exhibition["end_date"] = _get_date_id(_as_date(exhibition["exhibition_end"]), dates)


def _get_time_duration(entry_time: datetime, exit_time: datetime) -> int:
    """
        Zwraca czas trwania w sekundach między entry_time a exit_time.
        Gdy exit_time < entry_time, zwraca 0.
        Wymaga spójności tzinfo (oba naiwne albo oba świadome).
        """
    if (entry_time.tzinfo is None) != (exit_time.tzinfo is None):
        raise ValueError("entry_time i exit_time muszą być oba naiwne albo oba strefowo-świadome (tzinfo).")
    seconds = int((exit_time - entry_time).total_seconds())
    return max(0, seconds)


def _get_room_id(rooms: list[dict], room_number: int, at_date: date):
    for r in rooms:
        if r.get("number") == room_number:
            start = _as_date(r["effective_start_date"])
            end = _as_date(r["effective_end_date"])
            if start <= at_date <= end:
                return r["room_id"]
    return None


def gen_visits(exhibitions: list[dict], rooms: list[dict], dates: list[dict], visitors: list[dict], is_exhibited: list[dict], visiting: list[dict]) -> list[dict]:
    visits: list[dict] = []
    for idx in range(1, len(visiting) + 1):
        visit = visiting[idx-1]
        entry_time = _as_time(visit["entry_time"])
        exit_time = _as_time(visit["exit_time"])
        exhibition_id = visit["exhibition_id"]
        visits.append({
            "visit_id": idx,
            "date_id": _get_date_id(_as_date(visitors[visit["visitor_id"]-1]["visit_date"]), dates),
            "entry_time": _get_time_id(entry_time),
            "exit_time": _get_time_id(exit_time),
            "exhibition_id": exhibition_id,
            "room_id": _get_room_id(rooms, exhibitions[exhibition_id-1]["room_number"], _as_date(visitors[visit["visitor_id"]-1]["visit_date"])),
            "visitor_id": visit["visitor_id"],
            "visit_duration": _get_time_duration(entry_time, exit_time),
            "exhibits_total_value": exhibitions[exhibition_id-1]["exhibits_total_value"],
            "exhibits_count": exhibitions[exhibition_id-1]["exhibits_count"],
        })
    return visits


def gen_is_visited(visits: list[dict], links: list[dict]) -> list[dict]:
    is_visited: list[dict] = []
    for visit in visits:
        filtered = [link for link in links if link.get("exhibition_id") == visit["exhibition_id"]]
        for is_exhibited in filtered:
            is_visited.append({
                "visit_id": visit["visit_id"],
                "exhibit_id": is_exhibited["exhibit_id"],
            })
    return is_visited


def gen_data_dw(args):
    with_seed(args.seed)

    exhibitions = gen_exhibitions(args.exhibitions, args.rooms)

    start_date = _first_day_of_month(date.today())
    end_date = _as_date(exhibitions[-1]['exhibition_end'])

    dates = gen_date(start_date, end_date)
    times = gen_time()
    rooms = gen_rooms(args.rooms, args.rooms_changed, start_date, end_date)
    exhibits = gen_exhibits(args.exhibits, args.exhibits_changed, start_date, end_date)
    exhibit_exhibitions = gen_exhibit_exhibitions(exhibits, exhibitions, args.min_per_exhibition,
                                                  args.max_per_exhibition)

    visitors = gen_visitors(args.visitors, exhibitions)

    _add_avg_value_to_exhibitions(exhibitions, exhibits, exhibit_exhibitions)
    _add_date_id_to_exhibitions(exhibitions, dates)

    exhibition_visits = gen_exhibition_visits(visitors, exhibitions)

    visits = gen_visits(exhibitions, rooms, dates, visitors, exhibit_exhibitions, exhibition_visits)

    is_visited = gen_is_visited(visits, exhibit_exhibitions)
    return visits, dates, times, rooms, visitors, exhibitions, is_visited, exhibits
