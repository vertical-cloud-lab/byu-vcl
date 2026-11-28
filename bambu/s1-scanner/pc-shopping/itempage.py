"""Open an eBay item, print its condition/specifics and the seller's description text."""
import sys, time, random, subprocess
from playwright.sync_api import sync_playwright
iid = sys.argv[1]
def xdo(*a): subprocess.run(["xdotool", *map(str, a)], env={"DISPLAY": ":99"})
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = b.contexts[0].pages[0]
    page.goto(f"https://www.ebay.com/itm/{iid}", wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)
    for _ in range(2):
        xdo("mousemove", random.randint(500, 1400), random.randint(300, 800)); time.sleep(0.5)
    for _ in range(6): xdo("click", "5"); time.sleep(0.1)
    time.sleep(1.5)
    print("TITLE:", page.title()[:150])
    for sel in ["div.x-price-primary", "div.x-item-condition-text", "div.ux-labels-values--shipping", "div.x-about-this-item", "div[data-testid='ux-layout-section-evo']"]:
        el = page.query_selector(sel)
        if el: print(f"[{sel}]", " ".join(el.inner_text().split())[:1500])
    fr = page.query_selector("iframe#desc_ifr")
    src = fr.get_attribute("src") if fr else None
    if src:
        f = page.frame_locator("iframe#desc_ifr")
        try:
            print("[DESC]", " ".join(f.locator("body").inner_text(timeout=15000).split())[:1500])
        except Exception as e:
            print("desc err", e)
