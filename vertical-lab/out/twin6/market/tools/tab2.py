"""A second tab for vendor and GSA pages, so the crawl's tab is never touched."""
import json, sys, time
import browse as B
from playwright.sync_api import sync_playwright

def run(urls, shots=False, textlen=3000):
    pw = sync_playwright().start()
    br = pw.chromium.connect_over_cdp(B.CDP)
    ctx = br.contexts[0]
    page = ctx.new_page()
    out = []
    try:
        for u in urls:
            r = B.visit(page, u, label="tab2 " + u[:80], gap=(3.0, 7.0), scrolls=(1, 3))
            txt = page.evaluate("() => document.body ? document.body.innerText : ''")
            r["text"] = txt[:textlen]
            out.append(r)
            if shots:
                B.shot(page, "tab2_" + str(abs(hash(u)) % 10**8) + ".png")
    finally:
        page.close()
        pw.stop()
    return out

if __name__ == "__main__":
    n = int(sys.argv[1]) if sys.argv[1].isdigit() else 3000
    urls = sys.argv[2:] if sys.argv[1].isdigit() else sys.argv[1:]
    for r in run(urls, textlen=n):
        print("=" * 100)
        print(r["url"], r["status"], r["blocked"], r["title"][:90])
        print(r["text"])
