"""make credit: the CRediT statement and table from manuscript/declarations/credit.csv.

credit.csv has one row per CRediT role (the 14 roles of ANSI/NISO
Z39.104-2022, https://credit.niso.org/) and one column per author, in author
order.  Mark a cell with x, or with a degree (lead, equal, supporting).
Every author confirms their own row of marks at G3 (draft to co-authors);
nobody fills in someone else's.

Writes, next to the CSV:
  credit-statement.tex  "A. Author: Conceptualization, Methodology. B. Author: ..."
                        (the form Elsevier, HardwareX, Springer Nature and RSC print)
  credit-table.tex      a roles-by-authors table, for the SI or a cover letter
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
DECL = KIT / "manuscript" / "declarations"

ROLES = ["Conceptualization", "Data curation", "Formal analysis", "Funding acquisition",
         "Investigation", "Methodology", "Project administration", "Resources", "Software",
         "Supervision", "Validation", "Visualization", "Writing – original draft",
         "Writing – review & editing"]
DEGREES = {"x", "lead", "equal", "supporting"}


def tex(s: str) -> str:
    return s.replace("&", r"\&").replace("–", "--")


def main() -> int:
    with open(DECL / "credit.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    authors = header[1:]
    roles = [r[0] for r in body]
    if roles != ROLES:
        print("credit.csv must list the 14 CRediT roles, in order, exactly as named at "
              "https://credit.niso.org/")
        return 1
    marks = {a: [] for a in authors}
    for r in body:
        for a, cell in zip(authors, r[1:] + [""] * (len(authors) - len(r) + 1)):
            cell = cell.strip().lower()
            if cell and cell not in DEGREES:
                print(f"{a}, {r[0]}: {cell!r} is not one of x, lead, equal, supporting")
                return 1
            if cell:
                marks[a].append(r[0] + ("" if cell == "x" else f" ({cell})"))
    unmarked = [a for a, m in marks.items() if not m]

    fill = r"\fillme{roles}"
    lines = ["% Written by scripts/credit.py from credit.csv: edit the CSV, then make credit.",
             " ".join(r"\textbf{" + tex(a) + "}: " + (tex(", ".join(m)) if m else fill) + "."
                      for a, m in marks.items())]
    (DECL / "credit-statement.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    cols = "l" + "c" * len(authors)
    table = [r"% Written by scripts/credit.py from credit.csv: edit the CSV, then make credit.",
             r"\begin{tabular}{@{}" + cols + r"@{}}", r"\toprule",
             "Role & " + " & ".join(tex(a) for a in authors) + r" \\", r"\midrule"]
    for r in body:
        cells = [(c.strip() if c.strip().lower() != "x" else r"\checkmark")
                 for c in (r[1:] + [""] * (len(authors) - len(r) + 1))[:len(authors)]]
        table.append(tex(r[0]) + " & " + " & ".join(cells) + r" \\")
    table += [r"\bottomrule", r"\end{tabular}"]
    (DECL / "credit-table.tex").write_text("\n".join(table) + "\n", encoding="utf-8")
    print(f"credit-statement.tex and credit-table.tex written for {len(authors)} authors"
          + (f"; no roles yet for: {', '.join(unmarked)}" if unmarked else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
