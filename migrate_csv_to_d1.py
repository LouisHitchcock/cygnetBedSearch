#!/usr/bin/env python3
"""One-time migration: upload existing CSV data to Cloudflare D1 via the Worker API.

Usage:
    python migrate_csv_to_d1.py

Requires:
    BED_API_URL  (env var, e.g. https://your-worker.workers.dev)
    BED_API_TOKEN (env var, same as worker's API_TOKEN secret)
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scraper.api_client import send_to_api

CSV_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "scraper",
    "bed_data.csv",
)


def load_csv_rows(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            print("CSV is empty.")
            return []
        for row in reader:
            if len(row) >= 6:
                name, sex, beds, purpose, date, time = row[:6]
                rows.append([name, sex, int(beds), purpose, date, time])
    return rows


def main():
    if not os.path.exists(CSV_PATH):
        print(f"CSV not found at {CSV_PATH}")
        sys.exit(1)

    rows = load_csv_rows(CSV_PATH)
    print(f"Loaded {len(rows)} rows from CSV")

    if rows:
        send_to_api(rows)
        print("Migration complete!")


if __name__ == "__main__":
    main()
