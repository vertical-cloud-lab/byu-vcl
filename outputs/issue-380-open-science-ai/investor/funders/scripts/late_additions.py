#!/usr/bin/env python3
"""Ventures added after collection closed, each for a stated reason. Appends them to data/ventures_input.csv (once;
re-running changes nothing). Run from funders/ after build_inputs.py and build_u4.py.

- PeerJ (U2): Edison's review of FUNDERS.md (edison/fund_review_files/review.md, finding 9) pointed out that no
  open-access publisher with a venture-financing history beyond Frontiers was in U2. Its rounds are in pass h01,
  entered by hand from PeerJ's own announcement.
"""
import csv

LATE = [{"key": "peerj", "venture": "PeerJ", "universe": "U2", "category": "open-access publisher",
         "source_list": "added_after_review", "hint": "site https://peerj.com/", "owners": "", "stars": ""}]


def main():
    p = "data/ventures_input.csv"
    rows = list(csv.DictReader(open(p)))
    have = {r["key"] for r in rows}
    add = [r for r in LATE if r["key"] not in have]
    if add:
        with open(p, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=list(rows[0])).writerows(add)
    print(f"{len(add)} late additions appended; {len(rows) + len(add)} ventures in {p}")


if __name__ == "__main__":
    main()
