#!/usr/bin/env python3
"""Append program or investor-thesis rows (one JSON object per line on stdin) to data/program_passes/programs_<pass>.csv.

Validates every line first and writes nothing if any line is bad. Run from funders/.
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLS = ["funder", "funder_type", "program", "years", "committed_usd", "amount_note", "focus", "recipients",
        "funds_companies", "examples", "access", "status", "source", "source2", "quote", "notes"]
FT = {"foundation", "philanthropist", "donor_advised_or_fiscal_host", "corporate_program", "government_grant",
      "public_investor", "intergovernmental", "crypto_foundation", "dao", "platform", "accelerator", "fellowship",
      "venture_fund", "angel", "other"}
FOCUS = {"science_software", "open_hardware", "open_science", "open_data", "digital_infrastructure", "security", "ai",
         "privacy_internet_freedom", "education", "web3", "general_oss", "other"}


def lst(v):
    if v is None or v == "":
        return []
    if isinstance(v, str):
        v = re.split(r"\s*[|;,]\s*", v)
    return [str(x).strip() for x in v if str(x).strip()]


def main():
    p = sys.argv[1]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", p):
        sys.exit("pass id must be letters, digits, - or _")
    rows, errors = [], []
    for n, line in enumerate(sys.stdin, 1):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            extra = set(d) - set(COLS)
            if extra:
                raise ValueError(f"unknown fields {sorted(extra)}")
            if not str(d.get("funder") or "").strip():
                raise ValueError("funder missing")
            ft = str(d.get("funder_type") or "").strip().lower()
            if ft not in FT:
                raise ValueError(f"funder_type {ft!r} not in {sorted(FT)}")
            foc = [x.lower() for x in lst(d.get("focus"))]
            bad = [x for x in foc if x not in FOCUS]
            if bad:
                raise ValueError(f"focus {bad} not in {sorted(FOCUS)}")
            if not str(d.get("source") or "").startswith("http"):
                raise ValueError("source URL missing")
            amt = re.sub(r"[,$\s]", "", str(d.get("committed_usd") or ""))
            if amt and not re.fullmatch(r"\d+(\.\d+)?", amt):
                raise ValueError(f"committed_usd not plain digits: {amt!r}")
            row = {c: str(d.get(c) or "").strip() for c in COLS}
            row.update(funder_type=ft, focus=" | ".join(foc), examples=" | ".join(lst(d.get("examples"))),
                       committed_usd=str(int(round(float(amt)))) if amt else "")
            rows.append(row)
        except Exception as e:  # noqa: BLE001
            errors.append(f"line {n}: {e}")
    if errors:
        print("NOTHING WRITTEN, fix and resend:\n" + "\n".join(errors))
        sys.exit(1)
    path = os.path.join(HERE, "data", "program_passes", f"programs_{p}.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"appended {len(rows)}; {sum(1 for _ in open(path)) - 1} rows now in {os.path.basename(path)}")


if __name__ == "__main__":
    main()
