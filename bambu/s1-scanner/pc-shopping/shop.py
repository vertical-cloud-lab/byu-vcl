"""Drive the headed Chrome (rig.sh, traffic via the CubXL Pi) for one page visit.

usage: python3 shop.py URL NAME [--scrolls N] [--sel CSS] [--max N]
Saves /tmp/pcshop-out/NAME.png (viewport) and NAME.txt (visible text, or the text of each
element matching --sel). Mouse movement and scrolling go through xdotool on the virtual
display, so the page sees ordinary pointer and wheel events.
"""
import argparse, random, subprocess, time
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("url"); ap.add_argument("name")
ap.add_argument("--scrolls", type=int, default=3)
ap.add_argument("--sel", default=None)
ap.add_argument("--max", type=int, default=40)
ap.add_argument("--wait", type=float, default=4.0)
a = ap.parse_args()

def xdo(*args):
    subprocess.run(["xdotool", *map(str, args)], env={"DISPLAY": ":99"}, check=False)

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.bring_to_front()
    try:
        page.goto(a.url, wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print("goto error:", e)
    time.sleep(a.wait)
    # A few human-paced pointer moves, then wheel scrolls to trigger lazy loading.
    for _ in range(3):
        xdo("mousemove", random.randint(400, 1500), random.randint(250, 900))
        time.sleep(random.uniform(0.3, 0.8))
    for _ in range(a.scrolls):
        for _ in range(5):
            xdo("click", "5")
            time.sleep(0.08)
        time.sleep(random.uniform(0.8, 1.5))
    shot = f"/tmp/pcshop-out/{a.name}.png"
    page.screenshot(path=shot)
    print("title:", page.title()); print("url:", page.url)
    if a.sel:
        els = page.query_selector_all(a.sel)
        print("matches:", len(els))
        txt = "\n=====\n".join((e.inner_text() or "").strip() for e in els[: a.max])
    else:
        txt = page.inner_text("body")
    open(f"/tmp/pcshop-out/{a.name}.txt", "w").write(txt)
    print("chars:", len(txt))
