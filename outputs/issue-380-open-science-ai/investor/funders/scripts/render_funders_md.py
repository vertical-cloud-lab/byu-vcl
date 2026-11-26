#!/usr/bin/env python3
"""Render FUNDERS.md from FUNDERS.template.md: {{path.to.number}} placeholders are filled from
data/funders_numbers.json, and <!-- TABLE:name.md --> markers are replaced by data/tables/name.md (optionally
truncated: <!-- TABLE:name.md:25 --> keeps the first 25 rows). Run from funders/ after funders_tables.py and
funders_numbers.py, so the text and the tables always come from the same data."""
import json, re

num = json.load(open("data/funders_numbers.json"))


def lookup(path):
    cur = num
    for p in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(p)]
        else:
            cur = cur[p]
    if isinstance(cur, float):
        return f"{100 * cur:.0f}%" if cur <= 1 else f"{cur:,.0f}"
    if isinstance(cur, int):
        return f"{cur:,}"
    return str(cur)


def table(m):
    name, n = m.group(1), m.group(2)
    lines = open(f"data/tables/{name}").read().rstrip("\n").split("\n")
    if n:
        lines = lines[:2 + int(n)]
    return "\n".join(lines)


t = open("FUNDERS.template.md").read()
t = re.sub(r"<!-- TABLE:([\w.]+?\.md)(?::(\d+))? -->", table, t)
t = re.sub(r"\{\{([\w.\-]+)\}\}", lambda m: lookup(m.group(1)), t)
open("FUNDERS.md", "w").write(t)
print("FUNDERS.md written,", len(t), "characters")
