"""Renumber citations into first-appearance order and lint a manuscript.

Usage:
    python tools/check_manuscript.py manuscript-v3.md            # report only
    python tools/check_manuscript.py manuscript-v3.md --renumber # rewrite in place

Citations are numeric <sup>...</sup> tags after the "## Abstract" heading and
before "## References" (the author block's affiliation superscripts are never
touched). New references can be added with any unused number, e.g. 101, and
--renumber moves them into place: it rewrites every citation, compresses runs
into RSC style (1-3 with an en dash, 5,6 with a comma), and reorders the list.

The report also checks that every reference is cited, that figures are
numbered in order of first appearance and exist on disk, and lists the
SIGN-OFF anchors and TO SUPPLY placeholders still in the text.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SUP = re.compile(r"<sup>([0-9][0-9,–\- ]*)</sup>")
REF_LINE = re.compile(r"^(\d+)\. (.*)$")


def expand(body: str) -> list[int]:
    out: list[int] = []
    for part in body.replace(" ", "").split(","):
        if not part:
            continue
        if "–" in part or "-" in part:
            a, b = re.split("[–-]", part)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def compress(nums: list[int]) -> str:
    nums = sorted(set(nums))
    runs: list[list[int]] = []
    for n in nums:
        if runs and n == runs[-1][-1] + 1:
            runs[-1].append(n)
        else:
            runs.append([n])
    parts = []
    for r in runs:
        if len(r) >= 3:
            parts.append(f"{r[0]}–{r[-1]}")
        else:
            parts.extend(str(n) for n in r)
    return ",".join(parts)


def split(text: str) -> tuple[str, str, str, str]:
    a = text.index("\n## Abstract")
    r = text.index("\n## References")
    end = text.find("\n---", r + 1)
    end = len(text) if end == -1 else end
    return text[:a], text[a:r], text[r:end], text[end:]


def main() -> int:
    path = Path(sys.argv[1])
    renumber = "--renumber" in sys.argv
    text = path.read_text()
    head, body, refs, tail = split(text)

    order: list[int] = []
    for m in SUP.finditer(body):
        for n in expand(m.group(1)):
            if n not in order:
                order.append(n)

    entries: dict[int, str] = {}
    for line in refs.splitlines():
        m = REF_LINE.match(line)
        if m:
            entries[int(m.group(1))] = m.group(2)

    problems = []
    for n in order:
        if n not in entries:
            problems.append(f"citation {n} has no reference entry")
    for n in entries:
        if n not in order:
            problems.append(f"reference {n} is never cited")

    mapping = {old: new for new, old in enumerate(order, start=1)}
    if renumber and not problems:
        body = SUP.sub(lambda m: f"<sup>{compress([mapping[n] for n in expand(m.group(1))])}</sup>", body)
        lines = [f"{mapping[n]}. {entries[n]}" for n in sorted(entries, key=lambda k: mapping[k])]
        refs = "\n## References\n\n" + "\n".join(lines) + "\n"
        path.write_text(head + body + refs + tail)
        text = path.read_text()
        print(f"renumbered {len(mapping)} references "
              f"({sum(1 for k, v in mapping.items() if k != v)} moved)")
    elif renumber:
        print("not renumbering until these are fixed:")

    # figures: numbered in order of first appearance, files exist
    figs = re.findall(r"!\[Figure (\d+)\]\(([^)]+)\)", text)
    nums = [int(n) for n, _ in figs]
    if nums != list(range(1, len(nums) + 1)):
        problems.append(f"figures out of order: {nums}")
    for n, f in figs:
        if not (path.parent / f).exists():
            problems.append(f"Figure {n}: missing file {f}")
    tables = [int(n) for n in re.findall(r"\*\*Table (\d+)\.", text)]
    if tables != list(range(1, len(tables) + 1)):
        problems.append(f"tables out of order: {tables}")

    signoffs = sorted(set(re.findall(r"\b(ALL|SGB|SL|BP|LDP|TV|TB|JEH|NP|OM|P7)-(\d+)\b", text)),
                      key=lambda t: (t[0], int(t[1])))
    supply = re.findall(r"\[TO SUPPLY:[^\]]*\]", text)
    needed = re.findall(r"\[NEEDED[^\]]*\]", text)

    print(f"references: {len(entries)} | cited: {len(order)} | figures: {len(figs)} | tables: {len(tables)}")
    print(f"sign-off IDs referenced: {', '.join(a + '-' + b for a, b in signoffs)}")
    print(f"TO SUPPLY placeholders ({len(supply)}):")
    for s in supply:
        print("  ", s)
    print(f"legacy [NEEDED] markers: {len(needed)}")
    for p in problems:
        print("PROBLEM:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
