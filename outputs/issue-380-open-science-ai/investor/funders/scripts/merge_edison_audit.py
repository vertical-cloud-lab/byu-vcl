#!/usr/bin/env python3
"""Add the rounds Edison's blind audit found (edison/fund_deal_audit_files/funders_audit.csv) to the deal data as
pass `xed`, after the audit comparison has been computed on the data without them.

Low-confidence rows are left out; high and medium rows are added like a deepening pass (rounds already recorded
are not duplicated by build_funders.py). Each round keeps Edison's source URL and its confidence in the note.
Run from funders/; writes through append_deals.py so the same checks apply.
"""
import csv, json, re, subprocess, sys

TYPES = {"pre_seed", "seed", "series_a", "series_b", "series_c", "series_d", "series_e", "series_f_plus", "growth",
         "venture_unspecified", "angel", "accelerator", "corporate_strategic", "convertible_note", "grant_philanthropic",
         "grant_government", "prize", "crowdfunding_reward", "crowdfunding_equity", "token_sale", "debt", "secondary", "other"}


def main():
    sample = {r["key"]: r for r in csv.DictReader(open("edison/uploads/funders_audit_sample.csv"))}
    by = {}
    for r in csv.DictReader(open("edison/fund_deal_audit_files/funders_audit.csv")):
        if r["type"] == "none_found" or r.get("confidence", "").lower() == "low":
            continue
        k = r["key"] if r["key"] in sample else next((s for s, v in sample.items() if v["venture"] == r["venture"]), None)
        if not k or not r.get("source_url", "").startswith("http"):
            continue
        t = r["type"] if r["type"] in TYPES else "other"
        by.setdefault(k, []).append({"type": t, "label": r.get("label", "")[:80], "date": r.get("date", ""),
                                     "amount_usd": re.sub(r"[^0-9.]", "", r.get("amount_usd", "") or "").strip(".") or "", "lead": r.get("lead", ""),
                                     "investors": r.get("investors", ""), "source": r["source_url"], "source_kind": "other",
                                     "note": f"from Edison's blind audit ({r.get('confidence', '')} confidence)"})
    lines = [json.dumps({"key": k, "venture": sample[k]["venture"], "universe": sample[k]["universe"], "status": "unknown",
                         "funding_found": "yes", "rounds": rs, "notes": "rounds added from Edison's blind audit"})
             for k, rs in by.items()]
    out = subprocess.run([sys.executable, "scripts/append_deals.py", "xed"], input="\n".join(lines), text=True,
                         capture_output=True)
    print(out.stdout.strip() or out.stderr.strip())


if __name__ == "__main__":
    main()
