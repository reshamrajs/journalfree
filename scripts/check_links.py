#!/usr/bin/env python3
"""Check that every journal URL in data/journals.csv still responds.

Run weekly by GitHub Actions. Prints a Markdown report and exits 1 if any
link is broken, so the workflow can open an issue. Standard library only.
"""
from __future__ import annotations

import csv
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "journals.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JournalFree-linkcheck/1.0)"}
# Publishers often block bots with 403/429; that still means the page exists.
OK_STATUSES = {200, 301, 302, 303, 307, 308, 401, 403, 429}


def check(url: str) -> tuple[str, str]:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return url, f"ok {resp.status}"
        except urllib.error.HTTPError as e:
            if e.code in OK_STATUSES:
                return url, f"ok {e.code}"
            if method == "GET":
                return url, f"BROKEN {e.code}"
        except Exception as e:  # network errors, timeouts
            if method == "GET":
                return url, f"BROKEN {type(e).__name__}"
    return url, "BROKEN"


def main() -> int:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_url = {r["url"]: r["journal"] for r in rows}
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(check, by_url))

    broken = [(u, s) for u, s in results if s.startswith("BROKEN")]
    print(f"## Link check: {len(results) - len(broken)}/{len(results)} OK\n")
    for url, status in broken:
        print(f"- [ ] **{by_url[url]}**: {status} - {url}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
