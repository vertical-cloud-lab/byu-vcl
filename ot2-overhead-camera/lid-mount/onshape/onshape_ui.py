#!/usr/bin/env python3
"""Path B2: build the lid-mount base in Onshape through the browser.

Drives the Onshape web UI the way a person would, with Playwright. It signs in,
creates a document, draws sketches with mouse drags, picks edges with the mouse,
types every dimension, and extrudes, cuts and mirrors features. A screenshot is
saved after every step to ./screenshots, so a failed run shows where it stopped.

> Onshape's Terms of Use, section 4(a)(ix), forbid "any robot, spider, scraper or
> other automated means to access the Service". The REST API (onshape_api.py) is
> the sanctioned route; run this only on an account whose owner accepts that.

    ONSHAPE_USERNAME, ONSHAPE_PASSWORD   an Onshape login (email + password, no 2FA)

    python onshape_ui.py --signin-only                 # load the sign-in page and stop (no login)
    python onshape_ui.py --cdp http://127.0.0.1:9222   # drive a browser that is already running
    python onshape_ui.py --headed --slow 300           # launch one here and watch it
    python onshape_ui.py --document-url URL            # build in an existing, empty Part Studio

The run of 2026-09-25 drove a headed Chromium on a Raspberry Pi's virtual display,
so that it signed in from the Pi's residential IP, attached over an SSH tunnel with
--cdp. pi/README.md has that setup.

It builds the geometry that meets the lid, as native features on the Top plane
with every dimension typed in mm:

    Sketch 1 / Extrude 1   plate: centre-point rectangle on the origin, 112 x 112, 6 deep
    Sketch 2 / Extrude 2   collar: O52 circle on the origin, 20 deep, added
    Sketch 3 / Extrude 3   lens aperture: O46 circle on the origin, cut through all
    Sketch 4 / Extrude 4   one 10 x 10 post at (47, 47), 99.66 tall, added
    Mirror 1, Mirror 2     the post across Right, then both across Front: four posts
    Sketch 5 / Extrude 5   one O4.5 bolt hole at (33, 33), cut through all
    Mirror 3, Mirror 4     the bolt hole, the same way

then reads the part's volume back from Onshape's mass properties panel. The same
base built over the REST API, and in CadQuery, is 108,840.3 mm^3.

How it knows where to click. With the view square to the Top plane and zoomed to
fit a model that is symmetric about the origin, the origin sits at the centre of
the canvas. Each sketch entity is drawn with a drag of a known number of pixels,
and when a dimension box opens, Onshape pre-fills the length it actually drew.
That gives pixels per millimetre for the current view, without reading the WebGL
canvas at all. What the live run added:

  * Hover before clicking. Onshape picks what it has pre-selected under the
    cursor, and with software WebGL that takes most of a second.
  * Never pick on the axes. Seen from the Top, the Right and Front planes are
    edge-on as the two axis lines, so a click on an edge's midpoint picks a plane.
  * Those lines are also how sketches are located: an edge or a centre point is
    dimensioned to the Right and Front planes, picked on the canvas inside the lens
    aperture where nothing else is. The dimension tool ignores a plane, or the
    Origin, picked from the feature list.
  * A through-all cut from the Top plane has to be Symmetric. Remove flips the
    default direction, away from the part.
  * Place dimensions clear of other geometry, or the placement click becomes a
    second pick.
"""
from __future__ import annotations

import argparse
import asyncio
import math
import os
import re
import sys
import time
from pathlib import Path

from playwright.async_api import Page, TimeoutError as PWTimeout, async_playwright

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cad"))
from lid_mount import Params  # noqa: E402

SHOTS = HERE / "screenshots"
BASE_URL = os.environ.get("ONSHAPE_BASE_URL", "https://cad.onshape.com")
EXPECTED_MM3 = 108840.279          # the same base in CadQuery and over the REST API

# Default shortcuts from https://cad.onshape.com/help/Content/Home/keyboard_shortcuts_and_hotkeys.htm
# (all used live on 2026-09-25). Kept in one place so a change on Onshape's side is a one-line fix.
KEYS = {
    "sketch": "Shift+S",          # new sketch; inside an open sketch Shift+S is Point instead
    "extrude": "Shift+E",
    "center_rectangle": "r",      # "g" is the corner rectangle
    "circle": "c",
    "dimension": "d",
    "top_view": "Shift+5",
    "isometric": "Shift+7",
    "zoom_fit": "f",
    "search_tools": "Alt+c",      # tool search, for features with no shortcut (Mirror)
    "escape": "Escape",
}

# Selectors from Onshape's web client, all checked live on 2026-09-25.
SEL = {
    "email": "input[name='username']",
    "continue": "button.continue-button",
    "password": "input[name='password']",
    "signin": "button.os-signin-button",
    "totp": "input[name='totpCode']",
    "create": "button#create-new-type",
    "create_document": "button.create-new-document",
    "document_name": "input#document-name-input",
    "document_ok": "button#model-name-dialog-ok",
    "canvas": "#viewerdiv canvas#canvas",
    "tree_item": ".os-list-item-name",
    "dialog_ok": ".ns-dialog-button-ok",
    "dimension_box": ".quantity-autocomplete-holder input.os-param-number",
    "mass_properties": "button.mass-properties",
}


class Ui:
    def __init__(self, page: Page, slow_ms: int = 0):
        self.page = page
        self.slow = slow_ms
        self.n = 0
        self.cx = self.cy = 0.0            # canvas centre = origin, once zoomed to fit
        self.span = 800.0                  # shorter side of the canvas, px

    async def shot(self, label: str) -> None:
        self.n += 1
        SHOTS.mkdir(exist_ok=True)
        slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        await self.page.screenshot(path=SHOTS / f"{self.n:02d}-{slug}.png")
        print(f"[{self.n:02d}] {label}", flush=True)

    async def wait(self, ms: int = 400) -> None:
        await self.page.wait_for_timeout(ms + self.slow)

    async def key(self, name: str) -> None:
        await self.page.keyboard.press(KEYS.get(name, name))
        await self.wait(350)

    async def click(self, x: float, y: float) -> None:
        await self.page.mouse.move(x, y)
        await self.wait(250)
        await self.page.mouse.click(x, y)
        await self.wait(250)

    async def pick(self, x: float, y: float, settle: int = 900) -> None:
        """Click on the canvas. Onshape picks what it has pre-selected under the
        cursor, so approach the point and hover until the pre-selection catches up."""
        m = self.page.mouse
        await m.move(x - 12, y + 6)
        await self.wait(250)
        await m.move(x, y)
        await self.wait(settle)
        await m.click(x, y)
        await self.wait(600)

    async def drag(self, x0: float, y0: float, x1: float, y1: float) -> None:
        m = self.page.mouse
        await m.move(x0, y0)
        await self.wait(250)
        await m.down()
        for i in range(1, 13):              # move in steps so Onshape sees a drag
            await m.move(x0 + (x1 - x0) * i / 12, y0 + (y1 - y0) * i / 12)
            await self.page.wait_for_timeout(25)
        await m.up()
        await self.wait(500)

    async def tree(self, name: str):
        """A feature-list row (Top, Front, Right, Sketch 1, Extrude 3, Part 1, ...)."""
        loc = self.page.locator(SEL["tree_item"], has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))
        await loc.first.wait_for(state="visible", timeout=20000)
        return loc.first

    async def click_tree(self, name: str) -> None:
        box = await (await self.tree(name)).bounding_box()
        await self.click(box["x"] + 15, box["y"] + box["height"] / 2)

    async def pick_into(self, param: str, name: str) -> None:
        """Pick a feature-list row into a feature dialog's query field, and wait until the
        field shows it. A pick lands after a round trip to Onshape, over a second from a
        GitHub runner; activate another field before then and the pick is lost. That is
        how Mirror 1 of the 2026-09-26 recording ended up with nothing to mirror."""
        field = self.page.locator(f"[data-parameter-id='{param}']").first
        for _ in range(2):
            await self.click_tree(name)
            for _ in range(32):                     # 8 s
                if re.search(rf"\b{re.escape(name)}\b", await field.inner_text()):
                    return
                await self.page.wait_for_timeout(250)
            print(f"  {name} did not reach {param}; picking again", flush=True)
        raise RuntimeError(f"{name} did not reach the {param} field (see the screenshots)")

    async def accept(self) -> None:
        """Click the green check of the open sketch or feature dialog. Enter does
        not close a sketch, so this always clicks."""
        box = await self.page.locator(SEL["dialog_ok"]).first.bounding_box()
        await self.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        await self.wait(1500)

    async def centre_on_origin(self) -> None:
        """Square to the Top plane and zoom to fit. With a model symmetric about
        the origin, that puts the origin at the canvas centre."""
        await self.key("top_view")
        await self.wait(800)
        await self.key("zoom_fit")
        await self.wait(1500)
        box = await self.page.locator(SEL["canvas"]).bounding_box()
        self.cx, self.cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        self.span = min(box["width"], box["height"])

    def right_plane(self) -> tuple[float, float]:
        """A point on the Right plane, seen edge-on, inside the lens aperture."""
        return self.cx, self.cy + 0.1 * self.span

    def front_plane(self) -> tuple[float, float]:
        return self.cx + 0.1 * self.span, self.cy

    async def dimension(self, picks: list, place: tuple[float, float], value_mm: float, tries: int = 3) -> float:
        """Dimension the entities under the canvas points in picks, placing the
        dimension at place; return the length Onshape pre-filled (mm), then set it
        to value_mm. The first pick after drawing is often dropped while Onshape
        solves the sketch, hence the pause and the retries."""
        await self.wait(1500)
        await self.key("dimension")
        await self.wait(400)
        box = self.page.locator(SEL["dimension_box"]).first
        for attempt in range(tries):
            for x, y in picks:
                await self.pick(x, y)
            await self.pick(*place, settle=500)
            try:
                await box.wait_for(state="visible", timeout=3000)
                break
            except PWTimeout:
                if attempt == tries - 1:
                    raise RuntimeError(f"no dimension box after {tries} tries (see the screenshots)")
                print(f"  no dimension box, try {attempt + 1}; picking again", flush=True)
                # Start clean, or a half-made selection pairs with the next pick.
                await self.key("escape")
                await self.key("dimension")
        drawn = parse_mm(await box.input_value())
        await box.press("Control+a")
        await self.page.keyboard.type(f"{value_mm:g} mm", delay=40)
        await self.page.keyboard.press("Enter")
        await self.wait(900)
        await self.key("escape")
        return drawn


def parse_mm(text: str) -> float:
    m = re.match(r"\s*([-+]?\d*\.?\d+)\s*(mm|cm|m|in|\"|')?", text or "")
    if not m:
        raise RuntimeError(f"can't read a length from the dimension box: {text!r}")
    value, unit = float(m.group(1)), (m.group(2) or "mm")
    return value * {"mm": 1, "cm": 10, "m": 1000, "in": 25.4, '"': 25.4, "'": 304.8}[unit]


# --- steps --------------------------------------------------------------------------

async def sign_in(ui: Ui, email: str, password: str) -> None:
    page = ui.page
    await page.goto(f"{BASE_URL}/signin", wait_until="domcontentloaded")
    field = page.locator(SEL["email"])
    await field.wait_for(state="visible", timeout=30000)
    await field.click()
    await page.keyboard.type(email, delay=70)
    await page.locator(SEL["continue"]).click()
    pw = page.locator(SEL["password"])
    await pw.wait_for(state="visible", timeout=30000)
    await pw.click()
    await page.keyboard.type(password, delay=60)
    await page.locator(SEL["signin"]).click()
    try:
        await page.wait_for_url(re.compile(r"/documents"), timeout=60000)
    except PWTimeout:
        await ui.shot("sign-in stuck")
        if await page.locator(SEL["totp"]).count():
            raise RuntimeError("the account has two-factor auth on; sign in by hand once and pass --state")
        raise RuntimeError("sign-in did not reach /documents (wrong password? reCAPTCHA? see screenshot)")
    await ui.wait(4000)
    await ui.shot("signed in")


async def signed_in(ui: Ui) -> bool:
    await ui.page.goto(f"{BASE_URL}/documents", wait_until="domcontentloaded")
    await ui.wait(5000)
    return "/signin" not in ui.page.url


async def create_document(ui: Ui, name: str) -> str:
    page = ui.page
    await page.goto(f"{BASE_URL}/documents", wait_until="domcontentloaded")
    await page.locator(SEL["create"]).click()
    await page.locator(SEL["create_document"]).click()
    box = page.locator(SEL["document_name"])
    await box.wait_for(state="visible", timeout=20000)
    await box.click(click_count=3)
    await page.keyboard.type(name, delay=40)
    await ui.shot("new document dialog")
    await page.locator(SEL["document_ok"]).click()
    await page.wait_for_url(re.compile(r"/documents/\w+/w/\w+/e/\w+"), timeout=60000)
    return page.url


async def open_part_studio(ui: Ui, url: str) -> None:
    if ui.page.url != url:
        await ui.page.goto(url, wait_until="domcontentloaded")
    await ui.page.locator(SEL["canvas"]).wait_for(state="visible", timeout=90000)
    await ui.tree("Top")
    await ui.wait(8000)                     # WebSockets never go idle; give the graphics time
    await ui.shot("part studio open")


async def new_sketch_on_top(ui: Ui) -> None:
    await ui.key("escape")
    await ui.click_tree("Top")
    await ui.key("sketch")
    await ui.wait(1200)
    await ui.centre_on_origin()


async def circle_on_origin(ui: Ui, diameter: float, label: str) -> None:
    """Drag a circle out from the origin, then set its diameter."""
    await ui.key("circle")
    r = 0.12 * ui.span
    await ui.drag(ui.cx, ui.cy, ui.cx + r, ui.cy)
    await ui.key("escape")
    a = math.radians(40)                    # off both axis lines
    edge = (ui.cx + r * math.cos(a), ui.cy - r * math.sin(a))
    await ui.dimension([edge], (ui.cx + r + 60, ui.cy - r - 40), diameter)
    await ui.shot(f"{label} sketch")


async def square_on_origin(ui: Ui, side: float, label: str) -> None:
    """A centre-point rectangle dragged out from the origin, side x side."""
    await ui.key("center_rectangle")
    h = 0.1 * ui.span
    await ui.drag(ui.cx, ui.cy, ui.cx + h, ui.cy - h)
    await ui.key("escape")
    # Top edge, picked right of centre (its midpoint is on the Right plane).
    drawn = await ui.dimension([(ui.cx + h / 2, ui.cy - h)], (ui.cx + h / 2, ui.cy - h - 45), side)
    ppm = 2 * h / drawn
    x = ui.cx + side / 2 * ppm              # the width changed about the centre
    await ui.dimension([(x, ui.cy - h / 2)], (x + 50, ui.cy - h / 2), side)
    await ui.shot(f"{label} sketch")


async def square_at(ui: Ui, side: float, x: float, y: float, label: str) -> None:
    """A side x side centre-point rectangle centred at (x, y) mm, both non-zero.
    Drawn small in that quadrant, sized, then moved by dimensioning its inner
    edges to the Right and Front planes."""
    sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
    h = 0.06 * ui.span
    c = (ui.cx + sx * 0.2 * ui.span, ui.cy - sy * 0.2 * ui.span)
    await ui.key("center_rectangle")
    await ui.drag(c[0], c[1], c[0] + h, c[1] - h)
    await ui.key("escape")
    drawn = await ui.dimension([(c[0] + h / 3, c[1] - h)], (c[0] + h / 3, c[1] - h - 45), side)   # top edge
    half = side / 2 * (2 * h / drawn)
    await ui.dimension([(c[0] + half, c[1] + 2)], (c[0] + half + 45, c[1] + 2), side)             # right edge
    ex = c[0] - sx * half                   # the edge nearer the Right plane
    d = await ui.dimension([(ex, c[1] + 0.4 * half), ui.right_plane()],
                           ((ex + ui.cx) / 2, c[1] - sy * 70), abs(x) - side / 2)
    ppm = abs(ex - ui.cx) / d               # a long baseline: better than the small square's
    c = (ui.cx + x * ppm, c[1])
    ey = c[1] + sy * half                   # the edge nearer the Front plane
    await ui.dimension([(c[0] + 0.4 * half, ey), ui.front_plane()],
                       (c[0] + sx * 80, (ey + ui.cy) / 2), abs(y) - side / 2)
    await ui.shot(f"{label} sketch")


async def circle_at(ui: Ui, diameter: float, x: float, y: float, label: str) -> None:
    """A circle centred at (x, y) mm, both non-zero, located by its centre point."""
    sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
    c = (ui.cx + sx * 0.2 * ui.span, ui.cy - sy * 0.2 * ui.span)
    r = 0.03 * ui.span
    await ui.key("circle")
    await ui.drag(c[0], c[1], c[0] + r, c[1])
    await ui.key("escape")
    a = math.radians(40)
    await ui.dimension([(c[0] + r * math.cos(a), c[1] - r * math.sin(a))],
                       (c[0] - sx * (r + 40), c[1] + sy * (r + 30)), diameter)
    d = await ui.dimension([c, ui.right_plane()], ((c[0] + ui.cx) / 2, c[1] - sy * 60), abs(x))
    ppm = abs(c[0] - ui.cx) / d
    c = (ui.cx + x * ppm, c[1])
    await ui.dimension([c, ui.front_plane()], (c[0] + sx * 60, (c[1] + ui.cy) / 2), abs(y))
    await ui.shot(f"{label} sketch")


async def extrude(ui: Ui, sketch: str, op: str, depth_mm: float | None, label: str) -> None:
    """Extrude every region of a sketch, picked from the feature list so that a
    solid above the sketch plane can't be picked instead."""
    page = ui.page
    await ui.key("escape")
    await ui.key("extrude")
    await ui.wait(800)
    await ui.click_tree(sketch)
    await ui.wait()
    if op != "New":
        await page.locator("[data-parameter-id='operationType']").get_by_text(op, exact=True).first.click()
        await ui.wait()
    if depth_mm is None:
        await page.locator("[data-parameter-id='endBound']").first.click()
        await ui.wait()
        await page.get_by_text("Through all", exact=True).first.click()
        await ui.wait()
        # Remove flips the default direction, which from the Top plane points away from
        # the part ("Selected tools and targets do not intersect"). Symmetric cuts both ways.
        await page.locator("[data-parameter-id='symmetric']").get_by_text("Symmetric", exact=True).first.click()
    else:
        depth = page.locator("[data-parameter-id='depth'] input").first
        await depth.click(click_count=3)
        await page.keyboard.type(f"{depth_mm:g} mm", delay=40)
        await page.keyboard.press("Tab")
    await ui.wait(1500)
    await ui.shot(f"{label}: extrude {op.lower()} {'through all' if depth_mm is None else f'{depth_mm:g} mm'}")
    if await page.get_by_text("do not intersect").count():
        raise RuntimeError(f"{label}: the extrude misses the part")
    await ui.accept()


async def mirror_twice(ui: Ui, feature: str, first: int) -> None:
    """Feature-mirror across Right, then the feature and its mirror across Front.
    Onshape names the results "Mirror <first>" and "Mirror <first + 1>"."""
    page = ui.page
    for plane, picks in (("Right", [feature]), ("Front", [feature, f"Mirror {first}"])):
        await ui.key("escape")
        await ui.key("search_tools")
        await ui.wait(600)
        await page.keyboard.type("Mirror", delay=60)
        await ui.wait(1000)
        await page.keyboard.press("Enter")
        await ui.wait(1600)
        await page.locator("[data-parameter-id='patternType']").first.click()
        await ui.wait()
        await page.get_by_text("Feature mirror", exact=True).first.click()
        await ui.wait(800)
        for f in picks:
            await ui.pick_into("instanceFunction", f)       # "Features to mirror"
        await page.locator("[data-parameter-id='mirrorPlane']").first.click()
        await ui.wait()
        await ui.pick_into("mirrorPlane", plane)
        await ui.wait(1200)
        await ui.shot(f"mirror {' and '.join(picks)} across {plane}")
        await ui.accept()


async def build_base(ui: Ui, p: Params) -> None:
    # 1. Plate
    await new_sketch_on_top(ui)
    await square_on_origin(ui, p.base_size, "plate")
    await ui.accept()
    await extrude(ui, "Sketch 1", "New", p.base_t, "plate")
    # 2. Collar, as a solid disc; the aperture cut turns it into a ring.
    await new_sketch_on_top(ui)
    await circle_on_origin(ui, p.aperture_d + 2 * p.collar_wall, "collar")
    await ui.accept()
    await extrude(ui, "Sketch 2", "Add", p.base_t + p.collar_h, "collar")
    # 3. Lens aperture
    await new_sketch_on_top(ui)
    await circle_on_origin(ui, p.aperture_d, "aperture")
    await ui.accept()
    await extrude(ui, "Sketch 3", "Remove", None, "aperture")
    # 4. One post, then mirror it into four.
    await new_sketch_on_top(ui)
    await square_at(ui, p.post_w, p.post_c, p.post_c, "post")
    await ui.accept()
    await extrude(ui, "Sketch 4", "Add", round(p.z_deck, 2), "post")
    await mirror_twice(ui, "Extrude 4", first=1)
    # 5. One bolt hole, then mirror it into four.
    await new_sketch_on_top(ui)
    await circle_at(ui, p.bolt_clear_d, p.bolt_xy, p.bolt_xy, "bolt hole")
    await ui.accept()
    await extrude(ui, "Sketch 5", "Remove", None, "bolt hole")
    await mirror_twice(ui, "Extrude 5", first=3)
    await ui.key("isometric")
    await ui.key("zoom_fit")
    await ui.wait(2000)
    await ui.page.mouse.move(ui.cx + 0.45 * ui.span, ui.cy + 0.45 * ui.span)   # hover off the model
    await ui.wait(600)
    await ui.shot("base finished")


async def read_volume(ui: Ui) -> float:
    """Select Part 1 and read its volume (mm^3) from the mass properties panel."""
    await ui.key("escape")
    await ui.click_tree("Part 1")
    box = await ui.page.locator(SEL["mass_properties"]).first.bounding_box()
    await ui.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    await ui.wait(4000)
    text = await ui.page.evaluate("""() => {
        for (const row of document.querySelectorAll('.os-parameter-list-item'))
            if (row.innerText.trim() === 'Volume') { const i = row.querySelector('input'); return i && i.value; }
        return null; }""")
    await ui.shot("mass properties")
    m = re.match(r"\s*([\d.]+)\s*mm", text or "")
    if not m:
        raise RuntimeError(f"can't read the volume from the mass properties panel: {text!r}")
    return float(m.group(1))


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cdp", metavar="URL",
                    help="attach to a running Chrome/Chromium's DevTools endpoint instead of launching one")
    ap.add_argument("--chrome", help="Chrome/Chromium binary to use instead of Playwright's own")
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--slow", type=int, default=0, help="extra ms after every action")
    ap.add_argument("--state", type=Path, help="reuse a saved session (Playwright storage state)")
    ap.add_argument("--save-state", type=Path, help="save the session here after signing in")
    ap.add_argument("--document-url", help="work in an existing, empty Part Studio instead of creating a document")
    ap.add_argument("--name", default=f"OT-2 lid camera mount (UI build {time.strftime('%Y-%m-%d %H:%M')})")
    ap.add_argument("--signin-only", action="store_true", help="load the sign-in page, screenshot it, stop")
    args = ap.parse_args()

    async with async_playwright() as pw:
        if args.cdp:
            browser = await pw.chromium.connect_over_cdp(args.cdp)
            context = browser.contexts[0]
            pages = [pg for pg in context.pages if not pg.url.startswith(("devtools:", "chrome:"))]
            page = pages[-1] if pages else await context.new_page()
        else:
            browser = await pw.chromium.launch(
                executable_path=args.chrome, headless=not args.headed,
                # Onshape needs WebGL. Without a GPU, SwiftShader provides it; Chrome 137+
                # no longer falls back to it on its own.
                args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
            context = await browser.new_context(viewport={"width": 1600, "height": 1000},
                                                storage_state=str(args.state) if args.state else None)
            page = await context.new_page()
        ui = Ui(page, args.slow)
        try:
            if args.signin_only:
                await ui.page.goto(f"{BASE_URL}/signin", wait_until="domcontentloaded")
                await ui.page.locator(SEL["email"]).wait_for(state="visible", timeout=30000)
                await ui.page.locator(SEL["continue"]).wait_for(state="visible")
                webgl = await ui.page.evaluate(
                    "() => !!document.createElement('canvas').getContext('webgl2')")
                await ui.shot("sign-in page, no credentials used")
                print(f"sign-in form found; WebGL2 available: {webgl}")
                return
            if await signed_in(ui):
                print("already signed in")
            else:
                email = os.environ.get("ONSHAPE_USERNAME") or os.environ.get("ONSHAPE_EMAIL")
                password = os.environ.get("ONSHAPE_PASSWORD")
                if not (email and password):
                    raise SystemExit("set ONSHAPE_USERNAME and ONSHAPE_PASSWORD, or pass --state (see the README)")
                await sign_in(ui, email, password)
                if args.save_state:
                    await context.storage_state(path=str(args.save_state))
            url = args.document_url or await create_document(ui, args.name)
            print("document:", url)
            await open_part_studio(ui, url)
            await build_base(ui, Params())
            volume = await read_volume(ui)
            print(f"done: {ui.page.url}\nvolume of Part 1: {volume:.3f} mm^3 (REST API and CadQuery: {EXPECTED_MM3})")
            if abs(volume - EXPECTED_MM3) > 0.01:
                raise SystemExit("the volume is wrong: a feature failed or was mis-picked (see the screenshots)")
        except Exception:
            await ui.shot("failed here")
            raise
        finally:
            if not args.cdp:                # an attached browser is left running
                await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
