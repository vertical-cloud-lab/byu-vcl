"""Screenshot the eBay result cards for the given item IDs on the current page, with the
seller line hidden. usage: cardshot.py PREFIX ITEMID [ITEMID ...]"""
import sys
from playwright.sync_api import sync_playwright
prefix, ids = sys.argv[1], sys.argv[2:]
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = b.contexts[0].pages[0]
    page.evaluate("""() => {
      document.querySelectorAll('ul.srp-results > li div.s-card__attribute-row').forEach(r => {
        if (/positive/.test(r.textContent || '')) r.style.visibility = 'hidden';
      });
    }""")
    for i in ids:
        li = page.query_selector(f'ul.srp-results > li:has(a[href*="/itm/{i}"])')
        if not li:
            print("missing", i); continue
        li.scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        li.screenshot(path=f"/tmp/pcshop-out/card_{prefix}_{i}.png")
        print("saved", i)
