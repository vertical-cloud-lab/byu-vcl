#!/usr/bin/env python3
"""Pick well-funded ventures whose first-pass funding history is thin and split them into deepening passes.

A venture is picked if it raised at least USD 15M (the larger of part 2's total for U1 companies and the sum of the
rounds found) and either fewer than 8 investors were found, or it raised USD 30M+ with no seed, angel, accelerator or
Series A round found, or half or more of its rounds name no investor. U2 ventures (open hardware and science) with
any funding and fewer than 4 investors are always picked, as are the named priority ventures. Writes
data/deal_passes/input_xNN.csv and existing_xNN.md (the rounds already recorded). Run from funders/ after
build_funders.py.
"""
import collections, csv, glob, os, sys

# U4 (young startups from third-party lists) is not deepened: researched lightly by design.
PRIORITY = {"Opentrons", "arduino", "raspberry-pi", "openbci", "sofar-openrov", "framework", "makerbot", "ultimaker",
            "oxide", "sifive", "anaconda", "posit", "kitware", "juliahub", "coiled", "huggingface", "databricks",
            "github", "gitlabhq", "docker", "red-hat", "mysql-ab", "mongodb", "elastic", "confluent", "hashicorp"}
EARLY = {"seed", "pre_seed", "angel", "accelerator", "series_a"}


def main():
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    V = list(csv.DictReader(open("data/ventures.csv")))
    D = list(csv.DictReader(open("data/deals.csv")))
    vin = {r["key"]: r for r in csv.DictReader(open("data/ventures_input.csv"))}
    rounds = collections.defaultdict(list)
    for d in D:
        rounds[d["key"]].append(d)
    done = set()  # ventures already given to a deepening pass (re-running adds only new ones, in new passes)
    for f in glob.glob("data/deal_passes/input_x*.csv"):
        done |= {r["key"] for r in csv.DictReader(open(f))}
    start = len(glob.glob("data/deal_passes/input_x*.csv"))
    pick = []
    for v in V:
        if not v["researched"] or v["key"] in done or v["universe"] == "U4":
            continue
        rs = rounds[v["key"]]
        tot = max(float(v["part2_total_funding_usd"] or 0), sum(float(r["amount_usd"] or 0) for r in rs))
        ninv = int(v["n_investors"] or 0)
        types = {r["type"] for r in rs}
        blank = sum(1 for r in rs if not r["lead"] and not r["investors"])
        why = []
        if tot >= 15e6 and ninv < 8:
            why.append(f"{ninv} investors found for USD {tot / 1e6:.0f}M")
        if tot >= 30e6 and not types & EARLY:
            why.append("no early round found")
        if rs and blank * 2 >= len(rs) and tot >= 15e6:
            why.append(f"{blank} of {len(rs)} rounds name no investor")
        if v["universe"] == "U2" and (v["funding_found"] == "yes" or tot > 0) and ninv < 4:
            why.append("open hardware/science venture with few investors found")
        if v["key"] in PRIORITY and not why:
            why.append("priority venture: check completeness")
        if why:
            pick.append((tot, v, "; ".join(why)))
    pick.sort(key=lambda x: (-x[0]))
    cols = ["key", "venture", "universe", "category", "hint", "why"]
    n = start
    for i in range(0, len(pick), per):
        n += 1
        pid = f"x{n:02d}"
        chunk = pick[i:i + per]
        with open(f"data/deal_passes/input_{pid}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
            for tot, v, why in chunk:
                w.writerow({"key": v["key"], "venture": v["venture"], "universe": v["universe"], "category": v["category"],
                            "hint": vin.get(v["key"], {}).get("hint", "")[:400], "why": why})
        lines = [f"# Rounds already recorded for deepening pass {pid}\n"]
        for tot, v, why in chunk:
            lines.append(f"\n## {v['venture']} (`{v['key']}`, {v['universe']}): {why}\n")
            if v["notes"]:
                lines.append(f"First-pass notes: {v['notes'][:600]}\n")
            for r in sorted(rounds[v["key"]], key=lambda r: r["date"]):
                lines.append(f"- {r['date'] or '?'} {r['type']} {r['label']} · USD {r['amount_usd'] or '?'} · lead: "
                             f"{r['lead_raw'] or '-'} · others: {r['investors_raw'] or '-'} · {r['source']}")
            if not rounds[v["key"]]:
                lines.append("- (no rounds recorded)")
        open(f"data/deal_passes/existing_{pid}.md", "w").write("\n".join(lines) + "\n")
    print(len(pick), "ventures picked into", n - start, "new deepening passes (x%02d to x%02d)" % (start + 1, n))


if __name__ == "__main__":
    main()
