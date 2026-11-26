#!/usr/bin/env python3
"""Merge the deal passes, normalise investor names, attach investor types and count who funded what.

Inputs (run from funders/):
  data/ventures_input.csv                    the 640 ventures (PROTOCOL.md)
  data/deal_passes/ventures_*.csv, deals_*.csv   the research passes (append_deals.py)
  data/investor_aliases.csv                  alias -> canonical name (hand-made, after reading the raw names)
  data/investor_types.csv                    canonical name -> type, country, notes (hand-made)
  ../owners/data/core_financials.csv         part 2's status and funding totals for U1, if present

Outputs:
  data/ventures.csv          one row per venture: last version researched, plus input fields
  data/deals.csv             one row per funding event, with canonical investor names
  data/investor_links.csv    one row per investor-venture pair
  data/investors.csv         one row per investor: ventures backed (all, U1, U2, U3), leads, years, types, examples
  data/funders_summary.json  headline counts
"""
import collections, csv, glob, json, os, re

D = "data"
TYPE_ORDER = ["venture_firm", "corporate_venture", "angel", "accelerator", "growth_pe_hedge", "public_investor",
              "philanthropy", "government_grant", "crowdfunding", "crypto_fund_or_dao", "bank_or_debt", "company",
              "other", "unclassified"]


def key_name(s):
    s = s.lower().replace("&", " and ").replace("’", "'")
    s = re.sub(r"\(person\)", "", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\b(the|llc|l l c|lp|l p|llp|inc|ltd|limited|gmbh|ag|sa|sas|bv|plc|co|corp|corporation|fund [ivx]+|"
               r"fund \d+|management)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def load_alias():
    alias = {}
    p = os.path.join(D, "investor_aliases.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            alias[key_name(r["alias"])] = r["canonical"].strip()
    return alias


def load_types():
    t = {}
    p = os.path.join(D, "investor_types.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            t[key_name(r["investor"])] = r
    return t


HEUR = [
    (r"\(person\)$", "angel"),
    (r"kickstarter|indiegogo|crowd ?supply|backers|wefunder|republic\b|startengine|crowdcube|seedrs|crowdfund", "crowdfunding"),
    (r"y combinator|techstars|\bhax\b|sosv|500 (startups|global)|accelerator|incubator|entrepreneur first|antler|"
     r"plug and play|alchemist", "accelerator"),
    (r"national science foundation|\bnsf\b|\bsbir\b|\bsttr\b|darpa|\bnih\b|department of|ministry|european (commission|union|"
     r"innovation council)|\beic\b|horizon (2020|europe)|innovate uk|government|federal|agency|bpifrance|sprind|"
     r"high-tech gr|kfw|\bnasa\b|\bdoe\b|national|council|state of|city of|province", "government_grant"),
    (r"foundation|philanthrop|initiative|trust\b|endowment|institute|charit|fellowship", "philanthropy"),
    (r"\bdao\b|crypto|blockchain|web3|coinbase ventures|binance|pantera|polychain|paradigm|multicoin|a16z crypto|"
     r"electric capital|dragonfly|framework ventures|1kx|placeholder", "crypto_fund_or_dao"),
    (r"bank|debt|lending|credit|hercules|svb|silicon valley bank", "bank_or_debt"),
    (r"growth equity|private equity|tiger global|coatue|d1 capital|dst global|altimeter|thrive|fidelity|t\. ?rowe|"
     r"wellington|blackrock|franklin|goldman sachs|morgan stanley|jp ?morgan|temasek|gic\b|softbank|general atlantic|"
     r"insight partners|tcv|iconiq|vista|thoma bravo|silver lake|kkr|carlyle|blackstone|warburg|summit partners|"
     r"bain capital(?! ventures)|hedge|capital group|baillie gifford|durable", "growth_pe_hedge"),
    (r"ventures? capital|capital|ventures?|partners|vc\b|fund\b|investments?|holdings|equity|seed|angels?\b", "venture_firm"),
]


def heuristic(name):
    n = name.lower()
    for pat, t in HEUR:
        if re.search(pat, n):
            return t
    return "unclassified"


def last_versions():
    """Last version of each venture across the first-wave passes, and its rounds (the last n_rounds deal rows for
    that key). Deepening passes (ids starting with x) add rounds to that version instead of replacing it; a round
    they repeat (same type, date and amount) is kept once."""
    vers, extra = {}, collections.defaultdict(list)
    for vp in sorted(glob.glob(os.path.join(D, "deal_passes", "ventures_*.csv"))):
        pid = re.search(r"ventures_(\w+)\.csv", vp).group(1)
        vrows = list(csv.DictReader(open(vp)))
        dp = os.path.join(D, "deal_passes", f"deals_{pid}.csv")
        drows = list(csv.DictReader(open(dp))) if os.path.exists(dp) else []
        by_key = collections.defaultdict(list)
        for r in drows:
            by_key[r["key"]].append(r)
        for v in vrows:
            n = int(v["n_rounds"] or 0)
            rounds = by_key[v["key"]][-n:] if n else []
            v["pass"] = pid
            if pid.startswith("x"):
                extra[v["key"]].append((v, rounds))
                continue
            prev = vers.get(v["key"])
            if prev and prev[0]["written_utc"] > v["written_utc"]:
                continue
            vers[v["key"]] = (v, rounds)
    for k, adds in extra.items():
        for v, rounds in sorted(adds, key=lambda x: x[0]["written_utc"]):
            if k not in vers:
                vers[k] = (v, rounds)
                continue
            base, brounds = vers[k]
            seen = {(r["type"], r["date"][:7], r["amount_usd"]) for r in brounds}
            add = [r for r in rounds if "adds to existing round" in r["note"].lower() or
                   (r["type"], r["date"][:7], r["amount_usd"]) not in seen or not r["amount_usd"] and
                   (r["lead"] or r["investors"]) and (r["type"], r["date"][:7], r["lead"], r["investors"]) not in
                   {(b["type"], b["date"][:7], b["lead"], b["investors"]) for b in brounds}]
            base = dict(base)
            base["pass"] = base["pass"] + "+" + v["pass"]
            if v["notes"]:
                base["notes"] = (base["notes"] + " | " if base["notes"] else "") + v["notes"]
            if base["funding_found"] != "yes" and add:
                base["funding_found"] = "yes"
            for f in ("status", "country", "founded", "open_basis", "open_url"):
                if not base.get(f) or base.get(f) == "unknown":
                    base[f] = v.get(f, "")
            vers[k] = (base, brounds + add)
    return vers


def main():
    alias, types = load_alias(), load_types()
    inp = {r["key"]: r for r in csv.DictReader(open(os.path.join(D, "ventures_input.csv")))}
    fin = {}
    fp = "../owners/data/core_financials.csv"
    if os.path.exists(fp):
        for r in csv.DictReader(open(fp)):
            fin.setdefault(r.get("owner", ""), r)
    vers = last_versions()

    def canon(raw):
        raw = re.sub(r"\s+", " ", raw).strip()
        person = raw.endswith("(person)")
        k = key_name(raw)
        c = alias.get(k)
        if not c:
            c = re.sub(r"\s*\(person\)$", "", raw).strip()
        return c, person

    ventures, deals, links = [], [], collections.defaultdict(lambda: {"rounds": 0, "led": 0, "dates": [], "types": set(),
                                                                       "sources": set(), "kinds": set()})
    for k, base in inp.items():
        v, rounds = vers.get(k, (None, []))
        f = fin.get(k, {})
        ventures.append({"key": k, "venture": base["venture"], "universe": base["universe"], "category": base["category"],
                         "source_list": base["source_list"], "researched": int(v is not None),
                         "pass": v["pass"] if v else "", "open_ok": v["open_ok"] if v else "",
                         "open_basis": v["open_basis"] if v else "", "open_url": v["open_url"] if v else "",
                         "country": v["country"] if v else "", "founded": v["founded"] if v else "",
                         "status": v["status"] if v else "", "funding_found": v["funding_found"] if v else "",
                         "n_rounds": len(rounds), "n_investors": 0, "notes": v["notes"] if v else "",
                         "part2_status": f.get("status", ""), "part2_total_funding_usd": f.get("total_funding_usd", ""),
                         "part2_ever_1b": f.get("ever_1b", "")})
        invs = set()
        for r in rounds:
            lead = [x for x in r["lead"].split(" | ") if x.strip()]
            oth = [x for x in r["investors"].split(" | ") if x.strip()]
            lc = [canon(x) for x in lead]
            oc = [canon(x) for x in oth]
            deals.append({**{c: r[c] for c in ("key", "venture", "universe", "type", "label", "date", "amount_usd",
                                               "source", "source_kind", "note")},
                          "lead_raw": r["lead"], "investors_raw": r["investors"],
                          "lead": " | ".join(c for c, _ in lc), "investors": " | ".join(c for c, _ in oc)})
            for (c, person), is_lead in [(x, True) for x in lc] + [(x, False) for x in oc]:
                if (c, k) in links and False:
                    pass
                L = links[(c, k)]
                L["person"] = person or L.get("person", False)
                L["rounds"] += 1
                L["led"] += int(is_lead)
                if r["date"]:
                    L["dates"].append(r["date"][:4])
                L["types"].add(r["type"])
                L["sources"].add(r["source"])
                L["kinds"].add(r["source_kind"])
                invs.add(c)
        ventures[-1]["n_investors"] = len(invs)

    link_rows = []
    for (c, k), L in links.items():
        b = inp[k]
        link_rows.append({"investor": c, "person": int(L.get("person", False)), "key": k, "venture": b["venture"],
                          "universe": b["universe"], "category": b["category"], "rounds": L["rounds"], "led": L["led"],
                          "first_year": min(L["dates"]) if L["dates"] else "", "round_types": " | ".join(sorted(L["types"])),
                          "database_only": int(L["kinds"] <= {"database", "wikipedia"}),
                          "sources": " | ".join(sorted(L["sources"]))[:1500]})
    agg = collections.defaultdict(lambda: collections.defaultdict(int))
    ex = collections.defaultdict(list)
    for r in link_rows:
        a = agg[r["investor"]]
        a["ventures"] += 1
        a[r["universe"]] += 1
        a["led_ventures"] += int(r["led"] > 0)
        a["rounds"] += r["rounds"]
        a["person"] = max(a["person"], r["person"])
        a["database_only"] += r["database_only"]
        if r["first_year"]:
            a["first"] = min(a.get("first") or 9999, int(r["first_year"]))
            a["last"] = max(a.get("last") or 0, int(r["first_year"]))
        ex[r["investor"]].append((r["led"] > 0, r["venture"], r["universe"]))
    inv_rows = []
    for c, a in agg.items():
        t = types.get(key_name(c))
        typ = t["type"] if t else ("angel" if a["person"] else heuristic(c))
        names_ = [v for _, v, _ in sorted(ex[c], key=lambda x: (not x[0], x[1]))]
        inv_rows.append({"investor": c, "type": typ, "type_source": "manual" if t else "heuristic",
                         "country": t.get("country", "") if t else "", "ventures": a["ventures"], "U1": a["U1"],
                         "U2": a["U2"], "U3": a["U3"], "led_ventures": a["led_ventures"], "rounds": a["rounds"],
                         "database_only_links": a["database_only"], "first_year": a.get("first") or "",
                         "last_year": a.get("last") or "", "examples": "; ".join(names_[:12]),
                         "notes": t.get("notes", "") if t else ""})
    inv_rows.sort(key=lambda r: (-r["ventures"], -r["led_ventures"], r["investor"]))

    def write(name, rows):
        if not rows:
            return
        with open(os.path.join(D, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    write("ventures.csv", ventures)
    write("deals.csv", deals)
    write("investor_links.csv", sorted(link_rows, key=lambda r: (r["investor"], r["venture"])))
    write("investors.csv", inv_rows)
    res = sum(v["researched"] for v in ventures)
    summ = {"ventures": len(ventures), "researched": res,
            "by_universe": {u: {"ventures": sum(1 for v in ventures if v["universe"] == u),
                                "researched": sum(v["researched"] for v in ventures if v["universe"] == u),
                                "with_funding": sum(1 for v in ventures if v["universe"] == u and v["funding_found"] == "yes"),
                                "none_found": sum(1 for v in ventures if v["universe"] == u and v["funding_found"] == "none_found"),
                                "bootstrapped_stated": sum(1 for v in ventures if v["universe"] == u and v["funding_found"] == "bootstrapped_stated")}
                            for u in ("U1", "U2", "U3")},
            "rounds": sum(1 for d in deals if "adds to existing round" not in d["note"].lower()),
            "investor_venture_links": len(link_rows), "investors": len(inv_rows),
            "investors_by_type": dict(collections.Counter(r["type"] for r in inv_rows)),
            "investors_2plus": sum(1 for r in inv_rows if r["ventures"] >= 2),
            "investors_5plus": sum(1 for r in inv_rows if r["ventures"] >= 5),
            "rounds_by_source_kind": dict(collections.Counter(d["source_kind"] for d in deals))}
    json.dump(summ, open(os.path.join(D, "funders_summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1)[:1500])


if __name__ == "__main__":
    main()
