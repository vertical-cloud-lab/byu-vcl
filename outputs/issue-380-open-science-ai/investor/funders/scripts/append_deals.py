#!/usr/bin/env python3
"""Append researched ventures (one JSON object per line on stdin) to a deal pass.

Usage (run from funders/):
    python3 scripts/append_deals.py <pass> <<'JSON'
    {"key": "...", "venture": "...", "universe": "U1", ..., "rounds": [{...}, ...]}
    JSON

Writes data/deal_passes/ventures_<pass>.csv (one row per venture) and data/deal_passes/deals_<pass>.csv (one row
per funding event). Validates every line first and writes nothing if any line is bad. A venture sent again
replaces its earlier rows when the passes are merged (the last version wins; see build_funders.py).
"""
import csv, datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "deal_passes")
V_COLS = ["key", "venture", "universe", "open_basis", "open_url", "open_ok", "country", "founded", "status",
          "funding_found", "n_rounds", "notes", "notes_url", "written_utc"]
D_COLS = ["key", "venture", "universe", "type", "label", "date", "amount_usd", "lead", "investors", "source",
          "source_kind", "note"]
TYPES = {"pre_seed", "seed", "series_a", "series_b", "series_c", "series_d", "series_e", "series_f_plus", "growth",
         "venture_unspecified", "angel", "accelerator", "corporate_strategic", "convertible_note",
         "grant_philanthropic", "grant_government", "prize", "crowdfunding_reward", "crowdfunding_equity",
         "token_sale", "debt", "secondary", "other"}
KINDS = {"company", "investor", "news", "filing", "database", "wikipedia", "other"}
STATUS = {"private", "acquired", "listed", "shut_down", "nonprofit", "unknown"}
FOUND = {"yes", "none_found", "bootstrapped_stated"}


def names(v):
    if v is None or v == "":
        return []
    if isinstance(v, str):
        v = re.split(r"\s*[|;]\s*", v)
    out = []
    for x in v:
        x = re.sub(r"\s+", " ", str(x)).strip().strip(",")
        if x and x.lower() not in {"existing investors", "others", "other investors", "undisclosed"}:
            out.append(x)
    return out


def money(v):
    v = re.sub(r"[,$\s]", "", str(v or ""))
    if not v:
        return ""
    if not re.fullmatch(r"\d+(\.\d+)?", v):
        raise ValueError(f"amount_usd not plain digits: {v!r}")
    return str(int(round(float(v))))


def main():
    p = sys.argv[1]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", p):
        sys.exit("pass id must be letters, digits, - or _")
    vrows, drows, errors = [], [], []
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for n, line in enumerate(sys.stdin, 1):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            for k in ("key", "venture", "universe"):
                if not str(d.get(k) or "").strip():
                    raise ValueError(f"{k} missing")
            st = str(d.get("status") or "unknown").strip().lower().replace(" ", "_")
            if st not in STATUS:
                raise ValueError(f"status {st!r} not in {sorted(STATUS)}")
            ff = str(d.get("funding_found") or "").strip().lower()
            rounds = d.get("rounds") or []
            if ff not in FOUND:
                raise ValueError(f"funding_found {ff!r} not in {sorted(FOUND)}")
            if ff == "yes" and not rounds:
                raise ValueError("funding_found is yes but no rounds given")
            ok = str(d.get("open_ok") or "yes").strip().lower()
            if ok not in {"yes", "no", "partial"}:
                raise ValueError("open_ok must be yes, no or partial")
            for i, r in enumerate(rounds, 1):
                t = str(r.get("type") or "").strip().lower()
                if t not in TYPES:
                    raise ValueError(f"round {i}: type {t!r} not allowed")
                src = str(r.get("source") or "").strip()
                if not src.startswith("http"):
                    raise ValueError(f"round {i}: source URL missing")
                kind = str(r.get("source_kind") or "other").strip().lower()
                if kind not in KINDS:
                    raise ValueError(f"round {i}: source_kind {kind!r} not in {sorted(KINDS)}")
                lead, inv = names(r.get("lead")), names(r.get("investors"))
                inv = [x for x in inv if x not in lead]
                drows.append({"key": d["key"], "venture": d["venture"], "universe": d["universe"], "type": t,
                              "label": str(r.get("label") or ""), "date": str(r.get("date") or ""),
                              "amount_usd": money(r.get("amount_usd")), "lead": " | ".join(lead),
                              "investors": " | ".join(inv), "source": src, "source_kind": kind,
                              "note": str(r.get("note") or "")})
            vrows.append({"key": d["key"], "venture": d["venture"], "universe": d["universe"],
                          "open_basis": str(d.get("open_basis") or ""), "open_url": str(d.get("open_url") or ""),
                          "open_ok": ok, "country": str(d.get("country") or ""), "founded": str(d.get("founded") or ""),
                          "status": st, "funding_found": ff, "n_rounds": len(rounds),
                          "notes": str(d.get("notes") or ""), "notes_url": str(d.get("notes_url") or ""),
                          "written_utc": now})
        except Exception as e:  # noqa: BLE001
            errors.append(f"line {n}: {e}")
    if errors:
        print("NOTHING WRITTEN, fix and resend:\n" + "\n".join(errors))
        sys.exit(1)
    os.makedirs(OUT, exist_ok=True)
    for path, cols, rows in ((os.path.join(OUT, f"ventures_{p}.csv"), V_COLS, vrows),
                             (os.path.join(OUT, f"deals_{p}.csv"), D_COLS, drows)):
        new = not os.path.exists(path) or os.path.getsize(path) == 0
        with open(path, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            if new:
                w.writeheader()
            w.writerows(rows)
    with open(os.path.join(OUT, f"ventures_{p}.csv"), newline="") as f:
        done = {r["key"] for r in csv.DictReader(f)}
    print(f"appended {len(vrows)} ventures, {len(drows)} rounds; {len(done)} ventures now in pass {p}")


if __name__ == "__main__":
    main()
