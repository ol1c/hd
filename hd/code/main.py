import argparse
from to_sql import save_sql
from to_csv import save_csv, save_exhibits_csv
from to_bulk import save_bulk
from data_generator import gen_data
from pathlib import Path


parser = argparse.ArgumentParser(description="VisitorTrack data generator")
parser.add_argument("--csv", default=True, help="Zapis do pliku CSV")
parser.add_argument("--sql", default=False, help="Zapis do pliku SQL")
parser.add_argument("--bulk", default=True, help="Zapis do pliku BULK")
parser.add_argument("--out-csv-dir", default="../csv", help="Katalog wyjściowy na pliki CSV")
parser.add_argument("--out-bulk-dir", default="../bulk", help="Katalog wyjściowy na pliki BULK")
parser.add_argument("--out-sql-dir", default="../sql", help="Ścieżka do pliku .sql")
parser.add_argument("--rooms", type=int, default=15)
parser.add_argument("--exhibitions", type=int, default=15)
parser.add_argument("--exhibits", type=int, default=15 * 15)
parser.add_argument("--visitors", type=int, default=15)
parser.add_argument("--min-per-exhibition", type=int, default=5)
parser.add_argument("--max-per-exhibition", type=int, default=20)
parser.add_argument("--rows-per-insert", type=int, default=500, help="Ile wierszy w jednym INSERT ... VALUES")
parser.add_argument("--seed", type=int, default=None, help="Ustal ziarno RNG dla powtarzalności wyników")
args = parser.parse_args()

rooms, exhibitions, exhibits, exhibit_exhibitions, visitors, exhibition_visits = gen_data(args)

if args.csv:
    save_csv(Path(args.out_csv_dir), rooms, exhibitions, exhibits, exhibit_exhibitions, visitors, exhibition_visits)

if args.bulk:
    save_bulk(Path(args.out_bulk_dir), rooms, exhibitions, exhibits, exhibit_exhibitions, visitors, exhibition_visits)

if args.sql:
    save_sql(args, rooms, exhibitions, exhibits, exhibit_exhibitions, visitors, exhibition_visits)

save_exhibits_csv(Path(".."), exhibits)
