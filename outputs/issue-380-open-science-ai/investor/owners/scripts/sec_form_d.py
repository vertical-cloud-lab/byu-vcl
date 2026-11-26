#!/usr/bin/env python3
"""Capital raised by private US companies, from their SEC Form D filings.

Input: data/form_d_targets.csv with columns owner, legal_name (the issuer name to look for; several separated by
'|'). For each name, EDGAR full-text search finds Form D filings whose issuer name matches after normalization
(case, punctuation, Inc/Corp/LLC suffixes). Every Form D and D/A of a matched CIK is then read from its
primary_doc.xml. An amendment replaces the filing it amends (previousAccessionNumber), so each offering is counted
once, at its latest reported total amount sold.

Writes data/form_d_filings.csv (one row per filing) and data/form_d_by_owner.csv. Run from owners/.
Form D understates capital raised: it covers only Regulation D offerings of the named US issuer.
"""
import re, time, xml.etree.ElementTree as ET
import pandas as pd, requests

UA = {"User-Agent": "open-source-owner-study research-script@example.com"}
S = requests.Session(); S.headers.update(UA)


def get(url, **kw):
    for attempt in range(5):
        r = S.get(url, timeout=60, **kw)
        time.sleep(0.15)  # SEC asks for at most 10 requests a second
        if r.status_code == 200:
            return r
        if r.status_code in (403, 429, 500, 502, 503):
            time.sleep(3 * (attempt + 1)); continue
        return r
    return r


def norm(s):
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    s = re.sub(r"\b(inc|incorporated|corp|corporation|co|company|llc|ltd|limited|lp|plc|gmbh|sa|the)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def find_ciks(name):
    """CIKs of Form D issuers whose normalized name equals the normalized target."""
    out, hits = {}, []
    for q in dict.fromkeys([f'"{name}"', f'"{norm(name)}"']):  # punctuation in the quoted name can block a match
        r = get("https://efts.sec.gov/LATEST/search-index", params={"q": q, "forms": "D"})
        if r.status_code == 200:
            hits += r.json().get("hits", {}).get("hits", [])
    for h in hits:
        src = h["_source"]
        for cik, disp in zip(src.get("ciks", []), src.get("display_names", [])):
            ent = re.sub(r"\s*\([^)]*\)", "", disp).strip()  # drops "(TICKER)" and "(CIK n)"
            if norm(ent) == norm(name):
                out[cik.lstrip("0")] = ent
    return out


def filings(cik):
    r = get(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")
    if r.status_code != 200:
        return []
    j = r.json()
    rec = [j["filings"]["recent"]] + [get(f"https://data.sec.gov/submissions/{f['name']}").json()
                                     for f in j["filings"].get("files", [])]
    out = []
    for blk in rec:
        for form, acc, date, doc in zip(blk["form"], blk["accessionNumber"], blk["filingDate"], blk["primaryDocument"]):
            if form in ("D", "D/A"):
                out.append({"cik": cik, "entity": j.get("name"), "form": form, "accession": acc, "filed": date,
                            "doc": doc})
    return out


def parse(f):
    url = f"https://www.sec.gov/Archives/edgar/data/{f['cik']}/{f['accession'].replace('-', '')}/primary_doc.xml"
    r = get(url)
    f["url"] = url
    if r.status_code != 200:
        f["parse_error"] = r.status_code; return f
    try:
        x = ET.fromstring(r.content)
    except ET.ParseError:
        f["parse_error"] = "xml"; return f
    t = lambda path: (x.findtext(path) or "").strip()
    f.update({"total_offering": t(".//offeringSalesAmounts/totalOfferingAmount"),
              "total_sold": t(".//offeringSalesAmounts/totalAmountSold"),
              "first_sale": t(".//dateOfFirstSale/value"), "industry": t(".//industryGroup/industryGroupType"),
              "revenue_range": t(".//issuerSize/revenueRange"), "state": t(".//issuerAddress/stateOrCountry"),
              "previous_accession": t(".//previousAccessionNumber"),
              "entity_type": t(".//entityType"), "year_of_inc": t(".//yearOfInc/value")})
    return f


def collect(tg):
    rows, matches = [], []
    for _, t in tg.iterrows():
        ciks = {}
        for name in str(t.legal_name).split("|"):
            ciks.update(find_ciks(name.strip()))
        matches.append({"owner": t.owner, "legal_name": t.legal_name, "ciks": "|".join(ciks),
                        "entities": "|".join(ciks.values())})
        for cik in ciks:
            for f in filings(cik):
                f["owner"] = t.owner
                rows.append(parse(f))
        print(t.owner, ciks, flush=True)
    return pd.DataFrame(rows), pd.DataFrame(matches)


def summarize(fd):
    fd = fd.copy()
    fd["total_sold"] = pd.to_numeric(fd["total_sold"], errors="coerce")
    # an amendment supersedes the filing it amends; keep the end of each chain
    superseded = set(fd["previous_accession"].dropna()) - {""}
    live = fd[~fd["accession"].isin(superseded)].copy()
    g = live.groupby("owner").agg(form_d_offerings=("accession", "count"), form_d_total_sold=("total_sold", "sum"),
                                  form_d_first=("filed", "min"), form_d_last=("filed", "max"),
                                  form_d_entities=("entity", lambda s: "|".join(sorted(set(s)))))
    g.to_csv("data/form_d_by_owner.csv")
    print(g.sort_values("form_d_total_sold", ascending=False).to_string())


def main():
    """Without arguments: every target. With --delta <csv>: only those targets, appended to the existing outputs
    (used for legal names the second research pass added)."""
    import sys
    if "--delta" in sys.argv:
        tg = pd.read_csv(sys.argv[sys.argv.index("--delta") + 1])
        fd_new, m_new = collect(tg)
        fd = pd.concat([pd.read_csv("data/form_d_filings.csv"), fd_new], ignore_index=True)
        m = pd.concat([pd.read_csv("data/form_d_matches.csv"), m_new], ignore_index=True)
        pd.concat([pd.read_csv("data/form_d_targets.csv"), tg], ignore_index=True).drop_duplicates(
            "owner", keep="last").to_csv("data/form_d_targets.csv", index=False)
    else:
        fd, m = collect(pd.read_csv("data/form_d_targets.csv"))
    fd.to_csv("data/form_d_filings.csv", index=False)
    m.drop_duplicates("owner", keep="last").to_csv("data/form_d_matches.csv", index=False)
    if not fd.empty:
        summarize(fd)


if __name__ == "__main__":
    main()
