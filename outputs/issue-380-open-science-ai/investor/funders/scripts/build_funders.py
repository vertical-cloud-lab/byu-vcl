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


UNCONFIRMED = re.compile(r"(in talks|potential investors?|rumou?r|not yet closed|has not closed|raise in progress|"
                         r"not officially confirmed|"
                         r"in progress per sources|not confirmed by (the )?company|aggregator snippets only|"
                         r"reported by bloomberg, not confirmed)", re.I)
NOT_A_FUNDER = {"business angels", "angel investors", "individual investors", "private investors", "strategic investors"}
EXIT = re.compile(r"(acqui|buyout|buy-out|take[- ]private|taken private|\bipo\b|initial public offering|\bmerger\b|"
                  r"merged with|sold to|tender offer|\bspac\b|went public|delist|public offering|\blisting\b)", re.I)
HEUR = [
    (r"\(person\)$", "angel"),
    (r"kickstarter|indiegogo|crowd ?supply|backers|wefunder|republic\b|startengine|crowdcube|seedrs|crowdfund", "crowdfunding"),
    (r"y combinator|techstars|\bhax\b|sosv|500 (startups|global)|accelerator|incubator|entrepreneur first|antler|"
     r"plug and play|alchemist", "accelerator"),
    (r"national science foundation|\bnsf\b|\bsbir\b|\bsttr\b|darpa|\bnih\b|department of|ministry|european (commission|union|"
     r"innovation council)|\beic\b|horizon (2020|europe)|innovate uk|government|federal|agency|bpifrance|sprind|"
     r"high-tech gr|kfw|\bnasa\b|\bdoe\b|\bnational\b|council|state of|city of|province", "government_grant"),
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
    # same company under two keys: move the duplicate's rounds to the canonical venture (data/venture_aliases.csv)
    vdup = {r["duplicate_key"]: r["canonical_key"] for r in csv.DictReader(open(os.path.join(D, "venture_aliases.csv")))} \
        if os.path.exists(os.path.join(D, "venture_aliases.csv")) else {}
    for dup, can in vdup.items():
        if dup in vers and can in vers:
            cv, cr = vers[can]
            dv, dr = vers[dup]
            vers[can] = (cv, cr + [dict(r, key=can, venture=inp[can]["venture"], universe=inp[can]["universe"],
                                        note=(r["note"] + " | recorded under duplicate entry " + dup).strip(" |"))
                                   for r in dr])
            vers[dup] = (dv, [])
    oos = {r["key"]: r["reason"] for r in csv.DictReader(open(os.path.join(D, "out_of_scope.csv")))} \
        if os.path.exists(os.path.join(D, "out_of_scope.csv")) else {}
    seen_rows = set()
    # the same name meaning a different firm in one venture's rounds (data/contextual_aliases.csv)
    ctx = {(r["key"], r["name"]): r["canonical"] for r in csv.DictReader(open(os.path.join(D, "contextual_aliases.csv")))} \
        if os.path.exists(os.path.join(D, "contextual_aliases.csv")) else {}
    rex = list(csv.DictReader(open(os.path.join(D, "round_exclusions.csv")))) \
        if os.path.exists(os.path.join(D, "round_exclusions.csv")) else []

    def excluded(k, r):
        for e in rex:
            if e["key"] == k and r["date"].startswith(e["date"]) and e["label_contains"].lower() in r["label"].lower():
                return e["reason"]
        return ""
    dropped = set()
    vp = os.path.join(D, "verify", "verdicts.csv")
    if os.path.exists(vp):
        for r in csv.DictReader(open(vp)):
            if r["verdict"] == "not_supported":
                dropped.add((r["key"], r["name"].strip(), r["source"].strip()))

    def canon0(raw):
        raw = re.sub(r"\s+", " ", raw).strip()
        person = raw.endswith("(person)")
        k = key_name(raw)
        c = alias.get(k)
        if not c:
            c = re.sub(r"\s*\(person\)$", "", raw).strip()
        return c, person

    # one display name per normalised name, so case and punctuation variants (ZhenFund / Zhenfund) are one funder:
    # the name in investor_types.csv if there is one, else the most common spelling
    forms = collections.defaultdict(collections.Counter)
    for _v, _rs in vers.values():
        for _r in _rs:
            for _x in _r["lead"].split(" | ") + _r["investors"].split(" | "):
                if _x.strip():
                    _c, _ = canon0(_x)
                    forms[key_name(_c)][_c] += 1
    display = {kn: types[kn]["investor"] if kn in types else sorted(cnt.items(), key=lambda x: (-x[1], x[0]))[0][0]
               for kn, cnt in forms.items()}

    def canon(raw):
        c, person = canon0(raw)
        return display.get(key_name(c), c), person

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
        out_reason = ("duplicate of " + vdup[k]) if k in vdup else oos.get(k) or (
            "main product not open" if v and v.get("open_ok") == "no" else "")
        ventures[-1]["in_scope"] = "no: " + out_reason if out_reason else "yes"
        for r in rounds:
            lead = [x for x in r["lead"].split(" | ") if x.strip()]
            oth = [x for x in r["investors"].split(" | ") if x.strip()]
            # group labels that name no funder ("business angels") are not funders
            lead = [x for x in lead if key_name(x) not in NOT_A_FUNDER]
            oth = [x for x in oth if key_name(x) not in NOT_A_FUNDER]
            drop = [x for x in lead + oth if (k, x.strip(), r["source"].strip()) in dropped]
            lead = [x for x in lead if x not in drop]
            oth = [x for x in oth if x not in drop]
            lead = [ctx.get((k, x.strip()), x) for x in lead]
            oth = [ctx.get((k, x.strip()), x) for x in oth]
            lc = [canon(x) for x in lead]
            oc = [canon(x) for x in oth]
            # a round reported as talks, rumour or unconfirmed keeps its row but names no funders in the counts;
            # so do exits, IPOs and secondary sales, which put no money into the venture (PROTOCOL.md)
            unconf = bool(UNCONFIRMED.search(r["note"] or "") or UNCONFIRMED.search(r["label"] or "") or
                          re.search(r"nearing completion|if completed", r["label"] or "", re.I))
            is_exit = r["type"] == "secondary" or (r["type"] in ("other", "growth") and
                                                   bool(EXIT.search(r["label"] or "") or EXIT.search(r["note"] or "")))
            transfer = excluded(k, r)
            dup_row = (k, r["type"], r["date"], r["amount_usd"], r["lead"], r["investors"], r["source"]) in seen_rows
            seen_rows.add((k, r["type"], r["date"], r["amount_usd"], r["lead"], r["investors"], r["source"]))
            deals.append({**{c: r[c] for c in ("key", "venture", "universe", "type", "label", "date", "amount_usd",
                                               "source", "source_kind", "note")},
                          "lead_raw": r["lead"], "investors_raw": r["investors"],
                          "lead": " | ".join(c for c, _ in lc), "investors": " | ".join(c for c, _ in oc),
                          "counted": ("no (venture out of scope: " + out_reason + ")" if out_reason else
                                      "no (exact duplicate row)" if dup_row else
                                      "no (exit, IPO or secondary sale)" if is_exit else
                                      "no (" + transfer + ")" if transfer else
                                      "no (reported as unconfirmed)" if unconf else "yes"),
                          "dropped_after_check": " | ".join(drop)})
            if unconf or is_exit or dup_row or out_reason or transfer:
                continue
            for (c, person), is_lead in [(x, True) for x in lc] + [(x, False) for x in oc]:
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

    # round_id: rows that describe the same round (same venture and type, and the same amount within 5% with dates at
    # most six months apart, or the same month where one amount is missing) share an id, so a round reported by two
    # sources counts once. "adds to existing round" rows join the nearest round of their type and never start one.
    def month(d):
        m = re.match(r"(\d{4})(?:-(\d{2}))?", d or "")
        return (int(m.group(1)), int(m.group(2)) if m.group(2) else None) if m else None

    def same_round(a, b):
        if a["type"] != b["type"]:
            return False
        ma, mb = month(a["date"]), month(b["date"])
        xa, xb = float(a["amount_usd"] or 0), float(b["amount_usd"] or 0)
        if ma and mb and ma[1] and mb[1]:
            gap = abs((ma[0] * 12 + ma[1]) - (mb[0] * 12 + mb[1]))
        elif ma and mb:
            gap = 0 if ma[0] == mb[0] else 99
        else:
            gap = None
        if xa and xb:
            return abs(xa - xb) <= 0.05 * max(xa, xb) and (gap is None or gap <= 6)
        return gap == 0 and bool(ma and mb and ma[1] and mb[1]) if (ma and mb and ma[1] and mb[1]) else False

    by_key = collections.defaultdict(list)
    for d in deals:
        d["round_id"] = ""
        if d["counted"] == "yes":
            by_key[d["key"]].append(d)
    for k, rows in by_key.items():
        groups = []
        for d in sorted(rows, key=lambda d: ("adds to existing round" in d["note"].lower(), d["date"] or "9999")):
            g = next((g for g in groups if any(same_round(d, x) for x in g)), None)
            if g is None and "adds to existing round" in d["note"].lower():
                g = next((g for g in groups if g[0]["type"] == d["type"]), None)
            if g is None:
                g = []
                groups.append(g)
            g.append(d)
        for i, g in enumerate(groups, 1):
            for d in g:
                d["round_id"] = f"{k}#{i}"

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
    # stated open-source thesis (program pass p4): the investor's own words, matched to canonical names
    thesis = {}
    pp = os.path.join(D, "program_passes", "programs_p4.csv")
    if os.path.exists(pp):
        for r in csv.DictReader(open(pp)):
            if not r.get("quote"):
                continue
            base = re.sub(r"\s*\(.*?\)", "", r["funder"]).split(":")[0].strip()
            for cand in (r["funder"], base):
                cn = alias.get(key_name(cand)) or cand
                thesis.setdefault(key_name(cn), (r["quote"], r["source"]))
    tk = {r["investor"]: r["kind"] for r in csv.DictReader(open(os.path.join(D, "thesis_kinds.csv")))} \
        if os.path.exists(os.path.join(D, "thesis_kinds.csv")) else {}
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
                         "stated_open_source_thesis": thesis.get(key_name(c), ("", ""))[0],
                         "thesis_source": thesis.get(key_name(c), ("", ""))[1],
                         "thesis_kind": tk.get(c, "") if thesis.get(key_name(c)) else "",
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
                            for u in ("U1", "U2", "U3", "U4")},
            "round_records_counted": sum(1 for d in deals if d["counted"] == "yes" and "adds to existing round" not in d["note"].lower()),
            "rounds": len({d["round_id"] for d in deals if d["round_id"] and not all(
                "adds to existing round" in x["note"].lower() for x in deals if x["round_id"] == d["round_id"])}),
            "investor_venture_links": len(link_rows), "investors": len(inv_rows),
            "investors_by_type": dict(collections.Counter(r["type"] for r in inv_rows)),
            "investors_2plus": sum(1 for r in inv_rows if r["ventures"] >= 2),
            "investors_5plus": sum(1 for r in inv_rows if r["ventures"] >= 5),
            "rounds_by_source_kind": dict(collections.Counter(d["source_kind"] for d in deals))}
    json.dump(summ, open(os.path.join(D, "funders_summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1)[:1500])


if __name__ == "__main__":
    main()
