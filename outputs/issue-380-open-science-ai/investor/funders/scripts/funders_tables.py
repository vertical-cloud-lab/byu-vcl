#!/usr/bin/env python3
"""Tables for FUNDERS.md from data/investors.csv, investor_links.csv, ventures.csv and the program passes.

Writes data/tables/*.md (markdown tables pasted into FUNDERS.md) and data/programs.csv (all program rows, merged).
Run from funders/ after build_funders.py.
"""
import collections, csv, glob, os, re

D = "data"
T = os.path.join(D, "tables")
TYPE_LABEL = {"venture_firm": "venture firm", "corporate_venture": "corporate / strategic", "angel": "person (angel)",
              "accelerator": "accelerator / studio", "growth_pe_hedge": "growth, crossover or PE",
              "public_investor": "state or sovereign investor", "philanthropy": "philanthropy",
              "government_grant": "government grant", "crowdfunding": "crowdfunding", "crypto_fund_or_dao": "crypto fund or DAO",
              "bank_or_debt": "bank or lender", "company": "company (non-investor)", "other": "other", "unclassified": "unclassified"}


def rd(p):
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def md_table(rows, cols, heads):
    out = ["| " + " | ".join(heads) + " |", "| " + " | ".join("---" for _ in heads) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")).replace("|", "/") for c in cols) + " |")
    return "\n".join(out) + "\n"


def main():
    os.makedirs(T, exist_ok=True)
    inv = rd(os.path.join(D, "investors.csv"))
    links = rd(os.path.join(D, "investor_links.csv"))
    ven = {v["key"]: v for v in rd(os.path.join(D, "ventures.csv"))}
    by_inv = collections.defaultdict(list)
    for l in links:
        by_inv[l["investor"]].append(l)

    def top(filter_link, n, min_v=2, types=None):
        cnt = collections.Counter(); led = collections.Counter(); ex = collections.defaultdict(list)
        for l in links:
            if not filter_link(l):
                continue
            cnt[l["investor"]] += 1
            led[l["investor"]] += int(l["led"]) > 0
            ex[l["investor"]].append((int(l["led"]) > 0, l["venture"]))
        tmap = {r["investor"]: r for r in inv}
        rows = []
        for name, c in cnt.most_common():
            if c < min_v:
                break
            t = tmap.get(name, {})
            if types and t.get("type") not in types:
                continue
            exs = [re.sub(r"\s*\(.*?\)", "", v) for _, v in sorted(ex[name], key=lambda x: (not x[0], x[1]))]
            rows.append({"investor": name, "type": TYPE_LABEL.get(t.get("type", ""), t.get("type", "")), "ventures": c,
                         "led": led[name], "examples": ", ".join(exs[:8]) + (" …" if len(exs) > 8 else "")})
            if len(rows) >= n:
                break
        return rows

    cols = ["investor", "type", "ventures", "led", "examples"]
    heads = ["Funder", "Type", "Ventures backed", "Led a round in", "Ventures (led first)"]
    core = lambda l: l["universe"] in ("U1", "U2", "U3")
    tables = {
        "top_all_u123.md": top(core, 60, 3),
        "top_u1.md": top(lambda l: l["universe"] == "U1", 40, 2),
        "top_u2.md": top(lambda l: l["universe"] == "U2", 40, 2),
        "top_u3.md": top(lambda l: l["universe"] == "U3", 40, 2),
        "top_u4.md": top(lambda l: l["universe"] == "U4", 30, 2),
        "top_angels.md": top(core_or_u4 := (lambda l: True), 40, 2, {"angel"}),
        "top_corporate.md": top(lambda l: True, 40, 2, {"corporate_venture"}),
        "top_accelerators.md": top(lambda l: True, 25, 1, {"accelerator"}),
        "top_growth.md": top(lambda l: True, 30, 2, {"growth_pe_hedge", "public_investor"}),
        "grants_and_crowd.md": top(lambda l: True, 40, 1, {"philanthropy", "government_grant", "crowdfunding",
                                                         "crypto_fund_or_dao"}),
    }
    for name, rows in tables.items():
        open(os.path.join(T, name), "w").write(md_table(rows, cols, heads))
    # AI subset (U3 open-weight / AI companies and U1 AI companies by category/basis keywords)
    ai_keys = {k for k, v in ven.items() if re.search(r"\b(ai|model|weights|llm|inference|agent)\b", (v["category"] + " " + v["open_basis"]).lower())}
    open(os.path.join(T, "top_ai.md"), "w").write(md_table(top(lambda l: l["key"] in ai_keys, 30, 2), cols, heads))
    hw_keys = {k for k, v in ven.items() if re.search(r"hardware|3d print|robot|drone|instrument|lab|silicon|risc|sdr|camera|printer",
                                                    (v["category"] + " " + v["open_basis"]).lower())}
    open(os.path.join(T, "top_hardware_lab.md"), "w").write(md_table(top(lambda l: l["key"] in hw_keys, 40, 1), cols, heads))

    # open hardware, open science and science software: U2 plus the U1 companies found through GitHub's science topics
    fin = {r["owner"]: r for r in rd("../owners/data/finance_passes/input_all.csv")}
    sci = {k for k, v in ven.items() if v["universe"] == "U2" or (v["universe"] == "U1" and "B" in fin.get(k, {}).get("frames", ""))}
    open(os.path.join(T, "top_science_hardware.md"), "w").write(md_table(top(lambda l: l["key"] in sci, 60, 2), cols, heads))
    deals = rd(os.path.join(D, "deals.csv"))
    by_v = collections.defaultdict(list)
    for d in deals:
        by_v[d["key"]].append(d)
    vrows = []
    for k in sorted(sci, key=lambda k: ven[k]["venture"].lower()):
        v = ven[k]
        if v["funding_found"] != "yes":
            continue
        leads_, others, kinds = [], [], set()
        for d in sorted(by_v[k], key=lambda d: d["date"]):
            kinds.add(d["type"])
            for n in [x for x in d["lead"].split(" | ") if x]:
                if n not in leads_:
                    leads_.append(n)
            for n in [x for x in d["investors"].split(" | ") if x]:
                if n not in others and n not in leads_:
                    others.append(n)
        others = [n for n in others if n not in leads_]
        first = sorted(by_v[k], key=lambda d: d["date"])
        src = first[-1]["source"] if first else ""
        vrows.append({"venture": f"[{re.sub(r'\s*\(.*?\)', '', v['venture'])}]({src})" if src else v["venture"],
                      "group": v["universe"], "open": (v["open_basis"] or v["category"])[:70],
                      "funders": ", ".join([f"**{n}**" for n in leads_] + others) or "(amount only, funders not named)",
                      "kinds": ", ".join(sorted(kinds))})
    open(os.path.join(T, "science_hardware_ventures.md"), "w").write(md_table(
        vrows, ["venture", "group", "open", "funders", "kinds"],
        ["Venture (link: latest round's source)", "Group", "What is open", "Funders (leads in bold)", "Kinds of funding"]))
    # early rounds (pre-seed, seed, angel, accelerator, Series A): who leads them and who joins them, U1-U4
    early = {"pre_seed", "seed", "angel", "accelerator", "series_a"}
    tmap2 = {r["investor"]: r.get("type", "") for r in inv}
    alias_rows = rd(os.path.join(D, "investor_aliases.csv"))
    def canon_early(n):
        return n
    lead_c, part_c, ex_e = collections.Counter(), collections.Counter(), collections.defaultdict(set)
    for d in rd(os.path.join(D, "deals.csv")):
        if d["type"] not in early:
            continue
        for n in [x for x in d["lead"].split(" | ") if x]:
            lead_c[n] += 1; ex_e[n].add(re.sub(r"\s*\(.*?\)", "", d["venture"]))
        for n in [x for x in d["investors"].split(" | ") if x]:
            part_c[n] += 1; ex_e[n].add(re.sub(r"\s*\(.*?\)", "", d["venture"]))
    names = sorted(set(lead_c) | set(part_c), key=lambda n: (-(lead_c[n] + part_c[n]), -lead_c[n], n))
    erows = [{"investor": n, "type": TYPE_LABEL.get(tmap2.get(n, ""), tmap2.get(n, "")), "early_rounds": lead_c[n] + part_c[n],
              "led": lead_c[n], "examples": ", ".join(sorted(ex_e[n])[:8])} for n in names[:40]]
    open(os.path.join(T, "top_early.md"), "w").write(md_table(erows, ["investor", "type", "early_rounds", "led", "examples"],
                                                              ["Funder", "Type", "Early rounds joined", "Of which led", "Ventures"]))
    # corporate groups: distinct ventures across a parent's arms (e.g. Alphabet = GV, CapitalG, Gradient, Google)
    grp = collections.defaultdict(set)
    gmembers = collections.defaultdict(set)
    tt = {r["investor"]: r for r in rd(os.path.join(D, "investor_types.csv"))}
    for l in links:
        g = tt.get(l["investor"], {}).get("group", "")
        if g:
            grp[g].add(l["venture"]); gmembers[g].add(l["investor"])
    rows = [{"group": g, "arms": ", ".join(sorted(gmembers[g])), "ventures": len(v),
             "examples": ", ".join(sorted(re.sub(r"\s*\(.*?\)", "", x) for x in v)[:10])}
            for g, v in sorted(grp.items(), key=lambda x: -len(x[1]))]
    open(os.path.join(T, "corporate_groups.md"), "w").write(md_table(rows, ["group", "arms", "ventures", "examples"],
                                                                      ["Group", "Arms found", "Ventures", "Examples"]))
    # programs, merged
    prog = []
    for p in sorted(glob.glob(os.path.join(D, "program_passes", "programs_*.csv"))):
        pid = re.search(r"programs_(\w+)\.csv", p).group(1)
        for r in rd(p):
            r["pass"] = pid
            prog.append(r)
    if prog:
        with open(os.path.join(D, "programs.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(prog[0])); w.writeheader(); w.writerows(prog)
    # type mix by universe
    tmap = {r["investor"]: r["type"] for r in inv}
    mix = collections.defaultdict(collections.Counter)
    for l in links:
        mix[l["universe"]][tmap.get(l["investor"], "unclassified")] += 1
    rows = []
    for u in ("U1", "U2", "U3", "U4"):
        tot = sum(mix[u].values()) or 1
        row = {"universe": u, "links": tot}
        for t in TYPE_LABEL:
            row[t] = f"{100 * mix[u][t] / tot:.0f}%" if mix[u][t] else ""
        rows.append(row)
    keep = [t for t in TYPE_LABEL if any(r[t] for r in rows)]
    open(os.path.join(T, "type_mix.md"), "w").write(md_table(rows, ["universe", "links"] + keep,
                                                             ["Universe", "Investor-venture links"] + [TYPE_LABEL[t] for t in keep]))
    print("tables:", sorted(os.listdir(T)))


if __name__ == "__main__":
    main()
