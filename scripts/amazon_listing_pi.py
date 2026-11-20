"""Read an Amazon listing from a Pi in headed Chromium, driven by the mouse.

Amazon blocks plain requests from GitHub runners, and headless browsers are what its
bot checks look for. So run this on a Pi (residential IP), in a real Chromium window on
an Xvfb display, moving the mouse over the gallery thumbnails the way a person would.

Set up on the CubXL Pi on 2026-10-29 (no sudo; Chromium and Xvfb were already there):

    python3 -m venv ~/.venvs/pw && ~/.venvs/pw/bin/pip install playwright

Run, from the runner:

    scp scripts/amazon_listing_pi.py "$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME":/tmp/
    ssh "$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME" 'mkdir -p /tmp/amz && \
        xvfb-run -a -s "-screen 0 1366x900x24" ~/.venvs/pw/bin/python \
        /tmp/amazon_listing_pi.py B0FVFTDYYH /tmp/amz'
    scp "$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME":'/tmp/amz/*' <local dir>

Writes the title, price and stock line to meta.json, the page text to page.txt, a
screenshot per gallery thumbnail, and the gallery's full-size images (hires_NN.jpg).
Product photos are the seller's: read them, don't commit them.
"""

import json
import re
import sys
import time

from playwright.sync_api import sync_playwright

asin, out = sys.argv[1], sys.argv[2]

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/usr/bin/chromium",
        headless=False,
        args=["--no-sandbox", "--window-size=1366,900",
              "--disable-blink-features=AutomationControlled"],
    )
    pg = browser.new_page(viewport={"width": 1366, "height": 860}, locale="en-US")
    pg.goto("https://www.amazon.com/", timeout=60000)
    time.sleep(4)
    btn = pg.locator("button:has-text('Continue shopping')")  # first-visit interstitial
    if btn.count():
        bb = btn.first.bounding_box()
        pg.mouse.move(bb["x"] + 20, bb["y"] + 10, steps=15)
        pg.mouse.click(bb["x"] + 20, bb["y"] + 10)
        time.sleep(3)

    pg.goto(f"https://www.amazon.com/dp/{asin}", timeout=60000)
    time.sleep(5)
    pg.mouse.move(400, 300, steps=20)
    pg.screenshot(path=f"{out}/00_top.png")

    # The page has a hidden <input id="productTitle"> as well as the visible span.
    title = pg.locator("span#productTitle").first.inner_text().strip()
    thumbs = pg.locator("#altImages li.imageThumbnail")
    for i in range(thumbs.count()):
        bb = thumbs.nth(i).bounding_box()
        if not bb:
            continue
        pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2, steps=10)
        time.sleep(1.2)
        pg.screenshot(path=f"{out}/thumb_{i:02d}.png")

    html = pg.content()
    hires = list(dict.fromkeys(re.findall(
        r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"', html)))
    for i, url in enumerate(hires):
        open(f"{out}/hires_{i:02d}.jpg", "wb").write(pg.request.get(url).body())

    for _ in range(6):
        pg.mouse.wheel(0, 700)
        time.sleep(0.8)
    text = pg.locator("body").inner_text()
    open(f"{out}/page.txt", "w").write(text)

    price = pg.locator("#corePrice_feature_div .a-offscreen").first
    stock = re.search(r"Only \d+ left in stock[^\n]*|In Stock|Currently unavailable", text)
    json.dump({
        "asin": asin,
        "title": title,
        "price": price.inner_text() if price.count() else None,
        "stock": stock.group(0) if stock else None,
        "hires": hires,
        "checked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, open(f"{out}/meta.json", "w"), indent=1)
    browser.close()
