"""Take a data snapshot: copy a file into data/ and start its README.

    python scripts/snapshot_data.py ../bo/campaign_results.csv
    python scripts/snapshot_data.py /path/to/export.csv --name tensile_tests.csv

Copies the file (never links it), counts its rows, and writes
data/<name>.README.md with the provenance it can find: the source path, its
git repository, branch and short commit if it is in one (and whether the
file has uncommitted changes), its SHA-256, and today's date.  Units and what
one row is are left for you to fill in; make check fails until they are.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
DATA = KIT / "data"


def git(args, cwd):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("--name", help="file name in data/ (default: the source's name)")
    ap.add_argument("--force", action="store_true", help="replace an existing snapshot")
    args = ap.parse_args()

    src = args.source.resolve()
    dst = DATA / (args.name or src.name)
    readme = dst.with_name(dst.stem + ".README.md")
    if dst.exists() and not args.force:
        print(f"data/{dst.name} exists: a new snapshot replaces it only with --force, and then "
              "its README's provenance must be rewritten too")
        return 1
    DATA.mkdir(exist_ok=True)
    shutil.copy2(src, dst)

    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    rows = None
    if dst.suffix.lower() in (".csv", ".tsv"):
        with open(dst, newline="", encoding="utf-8") as f:
            rows = max(0, sum(1 for _ in csv.reader(f, delimiter="\t" if dst.suffix == ".tsv"
                                                    else ",")) - 1)
    top = git(["rev-parse", "--show-toplevel"], src.parent)
    if top:
        remote = git(["config", "--get", "remote.origin.url"], src.parent)
        remote = remote.split("@")[-1].replace("https://", "").removesuffix(".git") if remote else ""
        commit = git(["rev-parse", "--short=7", "HEAD"], src.parent)
        branch = git(["rev-parse", "--abbrev-ref", "HEAD"], src.parent)
        rel = src.relative_to(Path(top).resolve())
        dirty = git(["status", "--porcelain", "--", str(rel)], top)
        where = (f"`{rel}` in `{remote or top}` at commit `{commit}` (branch `{branch}`)"
                 + (" **with uncommitted changes to the file: commit them first, or say what they "
                    "are**" if dirty else ""))
    else:
        where = f"`{src}` (not in a git repository: say which instrument or export made it)"

    readme.write_text(f"""# {dst.name}

FILL: one sentence on what this file is.

- **Units:**
  - FILL: every column, `name`: what it is (unit)
- **n:** {rows if rows is not None else 'FILL'} rows. FILL: what one row is, how many independent
  samples that is, and which rows (if any) are technical replicates.
- **Provenance:** copied on {dt.date.today().isoformat()} from {where}.
  SHA-256 of the source: `{digest}`. FILL: anything done to it on the way
  (none, if it is the file as it was).
""", encoding="utf-8")
    print(f"data/{dst.name} ({rows} rows) and data/{readme.name} written; fill in the FILL lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
