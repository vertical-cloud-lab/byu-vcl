"""Check that every buy link in bom.csv still resolves, and record what came back.

Writes link-check.json: per URL, the HTTP status, the final URL after redirects and the time.
Digi-Key, Fisher, OnlineMetals, Ace and Zoro answer a script with 403, and Sigma never answers:
from the runner and from the CubXL Pi's residential IP alike (2026-10-19), so that is bot
protection, not a broken link. `--label` names where a run happened.

    python check_links.py                      # from wherever you are
    python check_links.py --label pi --only-blocked   # rerun just the 403s, e.g. from a lab Pi
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def fetch(url: str) -> tuple[int | str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                                               "Accept-Language": "en-US,en;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            r.read(65536)
            return r.status, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.geturl() or url
    except Exception as e:  # DNS, TLS, timeout
        return type(e).__name__, url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="runner")
    ap.add_argument("--only-blocked", action="store_true", help="only the URLs whose last result was not 200")
    a = ap.parse_args()
    out_path = HERE / "link-check.json"
    prev = json.loads(out_path.read_text()) if out_path.exists() else {"runs": {}}
    urls = {}
    for row in csv.DictReader((HERE / "bom.csv").open()):
        for col in ("url", "alt_url"):
            u = (row.get(col) or "").strip()
            if u.startswith("http"):
                urls.setdefault(u, []).append(row["id"])
    if a.only_blocked:
        last = {k: v for run in prev["runs"].values() for k, v in run["results"].items()}
        urls = {u: ids for u, ids in urls.items() if last.get(u, {}).get("status") != 200}
    results = {}
    for u, ids in urls.items():
        status, final = fetch(u)
        results[u] = {"ids": ids, "status": status, "final_url": final if final != u else None}
        print(f"{status!s:>5}  {','.join(ids):10s} {u}")
        time.sleep(1.0)
    prev["runs"][a.label] = {"when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"), "results": results}
    out_path.write_text(json.dumps(prev, indent=1) + "\n")
    ok = sum(1 for r in results.values() if r["status"] == 200)
    print(f"{ok} of {len(results)} returned 200")


if __name__ == "__main__":
    main()
