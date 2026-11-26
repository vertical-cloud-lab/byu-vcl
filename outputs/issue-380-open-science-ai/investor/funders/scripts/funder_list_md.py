#!/usr/bin/env python3
"""FUNDER_LIST.md: every funder found, grouped by type, with the ventures it backed and a source link for each.

Funders with two or more ventures get a line each, with every venture linked to a page that names the funder in
that venture's round. Funders with one venture are listed compactly at the end of each type. Run from funders/
after build_funders.py.
"""
import collections, csv, re

ORDER = [("venture_firm", "Venture firms"), ("corporate_venture", "Corporate and strategic investors"),
         ("accelerator", "Accelerators, incubators and studios"),
         ("growth_pe_hedge", "Growth, crossover, hedge and private-equity investors"),
         ("public_investor", "State, sovereign and public investors"), ("angel", "People (angels)"),
         ("philanthropy", "Philanthropy (grants to ventures)"), ("government_grant", "Government grants to ventures"),
         ("crowdfunding", "Crowdfunding"), ("crypto_fund_or_dao", "Crypto funds and DAOs"),
         ("bank_or_debt", "Banks and lenders"), ("company", "Companies"), ("other", "Other"),
         ("unclassified", "Not yet classified (typed by name only)")]


def short(v):
    return re.sub(r"\s*\(.*?\)", "", v).strip()


def main():
    inv = {r["investor"]: r for r in csv.DictReader(open("data/investors.csv"))}
    links = list(csv.DictReader(open("data/investor_links.csv")))
    by = collections.defaultdict(list)
    for l in links:
        by[l["investor"]].append(l)
    groups = collections.defaultdict(list)
    for name, r in inv.items():
        groups[r["type"]].append(name)
    n_inv = len(inv)
    out = ["# Every funder found, by type (issue #380, part 3)\n",
           f"{n_inv} funders of {len({l['key'] for l in links})} open-source-minded ventures, from "
           "[`data/investor_links.csv`](data/investor_links.csv). Each venture links to a page that names the funder "
           "in one of its rounds. **Bold** marks a venture where the funder led a round. U1–U4 are the venture groups "
           "in [`PROTOCOL.md`](PROTOCOL.md). Types come from the hand-made table "
           "[`data/investor_types.csv`](data/investor_types.csv), which covers every funder with two or more ventures; "
           "funders with one venture are typed by rules on their names and were read over once by hand (people are typed "
           "as angels). Counts are of ventures, not rounds, and leave out exits, secondary sales and unconfirmed rounds. "
           "Read [`FUNDERS.md`](FUNDERS.md) for what the list shows and its limits.\n"]
    for t, title in ORDER:
        names = groups.get(t, [])
        if not names:
            continue
        names.sort(key=lambda n: (-len(by[n]), n.lower()))
        multi = [n for n in names if len(by[n]) >= 2]
        single = [n for n in names if len(by[n]) == 1]
        out.append(f"\n## {title} ({len(names)})\n")
        for n in multi:
            ls = sorted(by[n], key=lambda l: (-int(l["led"] or 0), l["venture"].lower()))
            u = collections.Counter(l["universe"] for l in ls)
            parts = []
            for l in ls:
                src = l["sources"].split(" | ")[0]
                nm = short(l["venture"])
                parts.append(f"[{'**' + nm + '**' if int(l['led'] or 0) else nm}]({src})")
            out.append(f"- **{n}**: {len(ls)} ventures ({', '.join(f'{k} {v}' for k, v in sorted(u.items()))}). "
                       + ", ".join(parts))
        if single:
            items = []
            for n in single:
                l = by[n][0]
                items.append(f"{n} ([{short(l['venture'])}]({l['sources'].split(' | ')[0]}))")
            out.append(f"\nOne venture each ({len(single)}): " + "; ".join(items) + ".")
    open("FUNDER_LIST.md", "w").write("\n".join(out) + "\n")
    print("FUNDER_LIST.md:", n_inv, "funders")


if __name__ == "__main__":
    main()
