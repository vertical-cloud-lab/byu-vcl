"""Read listing pages found another way (a web search's results), through the same browser and pace, as cards.

    MARKET_CDP=... python3 direct.py <station> <query label> <url> [<url> ...]
Each page becomes a search card (search.jsonl, site from the host) and a listing-page record (details.jsonl).
"""
import json, sys, time
import browse as B
from crawl import SITES

HOSTS = {"machineseeker.com": "machineseeker", "machinio.com": "machinio", "labx.com": "labx", "exapro.com": "exapro"}


def main():
    station, label, urls = sys.argv[1], sys.argv[2], sys.argv[3:]
    pw, br, ctx, page = B.connect()
    for u in urls:
        site = next((v for k, v in HOSTS.items() if k in u), "")
        r = B.visit(page, u, gap=(5.0, 10.0), scrolls=(1, 3), label=f"direct|{site}|{station}")
        txt = page.evaluate("() => document.body ? document.body.innerText : ''")
        title = r["title"].replace("▷ Used ", "").split(" for sale")[0]
        t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(u, r["status"], r["blocked"], title[:70], flush=True)
        if r["status"] != 200 or r["blocked"]:
            continue
        hdr = txt.split("Basic data")[0][-1500:] if site == "machineseeker" else txt[:1500]
        with open(B.RAW / "search.jsonl", "a") as f:
            f.write(json.dumps(dict(station=station, site=site, query=label, search_url="(web search)", seen_utc=t,
                                    href=u, title=title, text=hdr)) + "\n")
        with open(B.RAW / "details.jsonl", "a") as f:
            f.write(json.dumps(dict(url=u, site=site, station=station, match="", status=r["status"], blocked=None,
                                    error=None, title=r["title"], final_url=r["final_url"], text=txt[:15000], shot="",
                                    t_utc=t)) + "\n")
    pw.stop()


if __name__ == "__main__":
    main()
