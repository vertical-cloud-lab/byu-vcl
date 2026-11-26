#!/usr/bin/env python3
"""Every startup in Runa Capital's ROSS Index (the fastest-growing open-source startups by GitHub stars, quarterly
since Q2 2020 and annually since 2022), scraped from runacap.com/ross-index/<period>/.

Each table row gives the repository, the startup, its country, city, founding year, a funding figure (USD millions,
blank when none is known to Runa), the language and the star growth. Writes data/u4/ross_index.csv (one row per
appearance) and prints the number of distinct startups. Run from funders/.
"""
import csv, html, re, time, urllib.request

PERIODS = ([f"q{q}-{y}" for y in range(2020, 2027) for q in range(1, 5)] +
           [f"annual-{y}" for y in range(2022, 2026)])
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}


def fetch(p):
    try:
        return urllib.request.urlopen(urllib.request.Request(f"https://runacap.com/ross-index/{p}/", headers=UA),
                                      timeout=30).read().decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        return ""


def rows_of(h):
    t = re.sub(r"<[^>]+>", " | ", h)
    t = html.unescape(re.sub(r"(\s*\|\s*)+", " | ", t))
    out = []
    # a row starts with "<owner>/<repo> | <Startup> | Repo |"
    for m in re.finditer(r"\| ([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+) \| ([^|]{1,80}) \| Repo \|((?: [^|]{0,60} \|){0,9})", t):
        repo, name, rest = m.group(1), m.group(2).strip(), [x.strip() for x in m.group(3).split("|") if x.strip()]
        country = city = founded = funding = lang = ""
        nums = []
        for x in rest:
            if re.fullmatch(r"(19|20)\d\d", x) and not founded:
                founded = x
            elif re.fullmatch(r"\d+(\.\d+)?", x):
                nums.append(x)
            elif re.fullmatch(r"\d{1,2} [A-Z][a-z]{2} \d{4}", x):
                break
            elif not country and not founded:
                country = x
            elif not city and not founded:
                city = x
            elif founded and not lang and re.fullmatch(r"[A-Za-z+#. ]{1,20}", x):
                lang = x
        # after the founding year the first number is Runa's funding figure (USD M) when present, before the language
        seq = rest[rest.index(founded) + 1:] if founded in rest else rest
        if seq and re.fullmatch(r"\d+(\.\d+)?", seq[0]):
            funding = seq[0]
        out.append({"repo": repo, "startup": name, "country": country, "city": city, "founded": founded,
                    "funding_musd": funding, "language": lang})
    return out


def main():
    allrows = []
    for p in PERIODS:
        h = fetch(p)
        rs = rows_of(h) if h else []
        for r in rs:
            r["period"] = p
        allrows += rs
        print(p, len(rs), flush=True)
        time.sleep(0.5)
    with open("data/u4/ross_index.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["period", "repo", "startup", "country", "city", "founded", "funding_musd",
                                          "language"])
        w.writeheader(); w.writerows(allrows)
    print(len(allrows), "appearances;", len({r["startup"].lower() for r in allrows}), "distinct startups")


if __name__ == "__main__":
    main()
