#!/usr/bin/env python3
"""Append researched company rows to a finance-pass CSV, one JSON object per line on stdin.

Usage (run from owners/):
    python scripts/append_finance_rows.py data/finance_passes/output_3.csv <<'JSON'
    {"owner": "grafana", "entity": "Grafana Labs", "status": "private", ...}
    JSON

Writes the header if the file is new, quotes fields properly, strips "$" and thousands separators from the number
columns, and refuses rows with an unknown column, a status outside the allowed set, or a number with a URL missing.
Rows for an owner already in the file replace the earlier row when the pass is merged (the last row wins).
"""
import csv, json, os, re, sys

COLS = ["owner", "entity", "status", "status_date", "ticker", "acquirer", "exit_value_usd", "exit_source",
        "total_funding_usd", "funding_asof", "funding_source", "last_valuation_usd", "valuation_date",
        "valuation_source", "peak_value_usd", "peak_value_date", "peak_source", "ever_1b", "legal_name", "notes"]
NUM_SRC = {"exit_value_usd": "exit_source", "total_funding_usd": "funding_source",
           "last_valuation_usd": "valuation_source", "peak_value_usd": "peak_source"}
STATUS = {"listed", "acquired", "private", "shut_down", "unknown"}


def clean_num(v):
    v = re.sub(r"[,$\s]", "", str(v or ""))
    if not v:
        return ""
    if not re.fullmatch(r"\d+(\.\d+)?", v):
        raise ValueError(f"not a plain number: {v!r}")
    return str(int(round(float(v))))


def main():
    path = sys.argv[1]
    rows, errors = [], []
    for n, line in enumerate(sys.stdin, 1):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            extra = set(d) - set(COLS)
            if extra:
                raise ValueError(f"unknown columns {sorted(extra)}")
            if not d.get("owner"):
                raise ValueError("owner missing")
            d["status"] = str(d.get("status") or "unknown").strip().lower().replace(" ", "_")
            if d["status"] not in STATUS:
                raise ValueError(f"status {d['status']!r} not in {sorted(STATUS)}")
            d["ever_1b"] = str(d.get("ever_1b") or "unknown").strip().lower()
            if d["ever_1b"] not in {"yes", "no", "unknown"}:
                raise ValueError("ever_1b must be yes, no or unknown")
            for c, src in NUM_SRC.items():
                d[c] = clean_num(d.get(c))
                if d[c] and not str(d.get(src) or "").startswith("http"):
                    raise ValueError(f"{c} given without a URL in {src}")
            rows.append({c: ("" if d.get(c) is None else str(d.get(c)).strip()) for c in COLS})
        except Exception as e:  # noqa: BLE001
            errors.append(f"line {n}: {e}")
    if errors:
        print("NOT WRITTEN, fix and resend:\n" + "\n".join(errors))
        sys.exit(1)
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new:
            w.writeheader()
        w.writerows(rows)
    with open(path, newline="") as f:
        done = [r["owner"] for r in csv.DictReader(f)]
    print(f"appended {len(rows)}; {len(set(done))} owners now in {path}")


if __name__ == "__main__":
    main()
