#!/usr/bin/env python3
"""Validate data/journals.csv and build public/journals.json.

Usage:
    python scripts/build_data.py            # validate + write JSON
    python scripts/build_data.py --check    # validate only (used in CI)

Exits with status 1 and prints every problem if the CSV is invalid.
Standard library only, so contributors need nothing installed.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "journals.csv"
JSON_PATH = ROOT / "public" / "journals.json"

COLUMNS = [
    "id", "journal", "publisher", "subjects", "access_model", "indexing",
    "quartile", "impact_factor", "if_verified", "speed", "green_oa", "url", "notes",
]
REQUIRED = ["id", "journal", "publisher", "subjects", "access_model", "quartile", "url"]
QUARTILES = {"Q1", "Q1/Q2", "Q2"}
SPEEDS = {"Fast", "Moderate", "Slow", ""}
YES_NO = {"yes", "no"}


def validate_rows(rows: list[dict[str, str]], header: list[str]) -> list[str]:
    """Return a list of human-readable problems (empty list = valid)."""
    errors: list[str] = []
    if header != COLUMNS:
        errors.append(f"header must be exactly: {','.join(COLUMNS)}")
        return errors

    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for line_no, row in enumerate(rows, start=2):  # line 1 is the header
        where = f"line {line_no} ({row.get('journal') or '?'})"
        for col in REQUIRED:
            if not (row.get(col) or "").strip():
                errors.append(f"{where}: '{col}' is empty")

        rid = row["id"].strip()
        if rid and not rid.isdigit():
            errors.append(f"{where}: id must be a whole number")
        if rid in seen_ids:
            errors.append(f"{where}: duplicate id {rid}")
        seen_ids.add(rid)

        name = row["journal"].strip().lower()
        if name in seen_names:
            errors.append(f"{where}: journal listed twice")
        seen_names.add(name)

        if row["quartile"] and row["quartile"] not in QUARTILES:
            errors.append(f"{where}: quartile must be one of {sorted(QUARTILES)}")
        if row["speed"] not in SPEEDS:
            errors.append(f"{where}: speed must be Fast, Moderate, Slow or empty")
        if row["if_verified"] not in YES_NO:
            errors.append(f"{where}: if_verified must be 'yes' or 'no'")

        impact = row["impact_factor"].strip()
        if impact:
            try:
                float(impact)
            except ValueError:
                errors.append(f"{where}: impact_factor must be a number like 6.3")

        url = urlparse(row["url"].strip())
        if row["url"] and (url.scheme != "https" or not url.netloc):
            errors.append(f"{where}: url must start with https://")
    return errors


def to_record(row: dict[str, str]) -> dict:
    impact = row["impact_factor"].strip()
    return {
        "id": int(row["id"]),
        "journal": row["journal"].strip(),
        "publisher": row["publisher"].strip(),
        "subjects": [s.strip() for s in row["subjects"].split(";") if s.strip()],
        "accessModel": row["access_model"].strip(),
        "indexing": row["indexing"].strip(),
        "quartile": row["quartile"].strip(),
        "impactFactor": float(impact) if impact else None,
        "ifVerified": row["if_verified"] == "yes",
        "speed": row["speed"].strip() or None,
        "greenOA": row["green_oa"].strip(),
        "url": row["url"].strip(),
        "notes": row["notes"].strip(),
    }


def load(path: Path = CSV_PATH) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [{k: (v or "") for k, v in r.items()} for r in reader]
        return list(reader.fieldnames or []), rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate only")
    args = parser.parse_args()

    header, rows = load()
    errors = validate_rows(rows, header)
    if errors:
        print(f"{len(errors)} problem(s) in {CSV_PATH.relative_to(ROOT)}:")
        for e in errors:
            print("  -", e)
        return 1

    print(f"OK: {len(rows)} journals valid")
    if not args.check:
        records = sorted((to_record(r) for r in rows), key=lambda r: r["journal"].lower())
        JSON_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {JSON_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
