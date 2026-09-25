#!/usr/bin/env python3
"""Path B2: build the lid-mount base in Onshape through the browser.

Drives the Onshape web UI the way a person would, with Playwright. It signs in,
creates a document, draws sketches with mouse clicks and drags, types the
dimensions, and extrudes, cuts and mirrors features. A screenshot is saved after
every step to ./screenshots, so a failed run shows exactly where it stopped.

> Onshape's Terms of Use, section 4(a)(ix), forbid "any robot, spider, scraper or
> other automated means to access the Service". The REST API (onshape_api.py) is
> the sanctioned route; run this only on an account whose owner accepts that.

    ONSHAPE_EMAIL, ONSHAPE_PASSWORD   an Onshape login (email + password, no 2FA)

    python onshape_ui.py --signin-only          # load the sign-in page and stop (no login)
    python onshape_ui.py --save-state s.json    # sign in, build, keep the session
    python onshape_ui.py --state s.json         # reuse a saved session (avoids repeated logins)
    python onshape_ui.py --document-url https://cad.onshape.com/documents/...   # reuse a document
    xvfb-run -a python onshape_ui.py --headed --slow 300                         # watch it

It builds the geometry that meets the lid, as native features on the Top plane
with every dimension typed in mm:

    Sketch 1 / Extrude 1   plate: centre-point rectangle on the origin, 112 x 112, 6 deep
    Sketch 2 / Extrude 2   collar: O52 circle on the origin, 20 deep, added
    Sketch 3 / Extrude 3   lens aperture: O46 circle on the origin, cut through all
    Sketch 4 / Extrude 4   one 10 x 10 post at (47, 47), 99.66 tall, added
    Mirror 1, Mirror 2     the post across Right, then both across Front: four posts
    Sketch 5 / Extrude 5   one O4.5 bolt hole at (33, 33), cut through all
    Mirror 3, Mirror 4     the bolt hole, the same way

The deck, nut traps, tabs and fillets come in with the STEP import in onshape_api.py.

How it knows where to click. With the view square to the Top plane and zoomed to
fit a model that is symmetric about the origin, the origin sits at the centre of
the canvas. Each sketch entity is then drawn with a drag of a known number of
pixels, and when its dimension box opens, Onshape pre-fills the length it
actually drew. That gives pixels per millimetre for the current view, without
reading the WebGL canvas at all.
"""
from __future__ import annotations

import argparse
import asyncio
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

# Default shortcuts from https://cad.onshape.com/help/Content/Home/keyboard_shortcuts_and_hotkeys.htm
# (checked 2026-09). Kept in one place so a change on Onshape's side is a one-line fix.
KEYS = {
    "sketch": "Shift+S",          # new sketch; inside an open sketch Shift+S is Point instead
    "extrude": "Shift+E",
    "center_rectangle": "r",
    "circle": "c",
    "dimension": "d",
    "top_view": "Shift+5",
    "isometric": "Shift+7",
    "zoom_fit": "f",
    "search_tools": "Alt+c",      # tool search, for features with no shortcut (Mirror)
    "escape": "Escape",
}

# Selectors from Onshape's web client (2026-09); the sign-in ones were checked live.
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
    "dimension_box": ".dimension-dialog input",
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
        await self.wait(250)                # Onshape selects what the cursor hovers
        await self.page.mouse.click(x, y)
        await self.wait(250)

    async def drag(self, x0: float, y0: float, x1: float, y1: float) -> None:
        m = self.page.mouse
        await m.move(x0, y0)
        await self.wait(250)
        await m.down()
        for i in range(1, 13):              # move in steps so Onshape sees a drag
            await m.move(x0 + (x1 - x0) * i / 12, y0 + (y1 - y0) * i / 12)
            await self.page.wait_for_timeout(25)
        await m.up()
        await self.wait(350)

    async def tree(self, name: str):
        """A feature-list row (Top, Front, Right, Origin, Sketch 1, Extrude 3, ...)."""
        loc = self.page.locator(SEL["tree_item"], has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))
        await loc.first.wait_for(state="visible", timeout=20000)
        return loc.first

    async def accept(self) -> None:
        """Click the green check of the open sketch or feature dialog. Enter does
        not close a sketch, so this always clicks."""
        ok = self.page.locator(SEL["dialog_ok"])
        await ok.first.click()
        await self.wait(1200)

    async def centre_on_origin(self) -> None:
        """Square to the Top plane and zoom to fit. With a model symmetric about
        the origin, that puts the origin at the canvas centre."""
        await self.key("top_view")
        await self.key("zoom_fit")
        await self.wait(1200)
        box = await self.page.locator(SEL["canvas"]).bounding_box()
        self.cx, self.cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        self.span = min(box["width"], box["height"])

    def at(self, x_mm: float, y_mm: float, ppm: float) -> tuple[float, float]:
        return self.cx + x_mm * ppm, self.cy - y_mm * ppm

    async def dimension(self, picks: list, place: tuple[float, float], value_mm: float) -> float:
        """Dimension the picked entities, return the length Onshape pre-filled
        (mm), then set it to value_mm. A pick is (x, y) on the canvas or a
        feature-list name such as "Origin"."""
        await self.key("dimension")
        for pk in picks:
            if isinstance(pk, str):
                await (await self.tree(pk)).click()
                await self.wait()
            else:
                await self.click(*pk)
        await self.click(*place)
        box = self.page.locator(SEL["dimension_box"]).first
        await box.wait_for(state="visible", timeout=10000)
        drawn = parse_mm(await box.input_value())
        await box.fill(f"{value_mm:g} mm")
        await box.press("Enter")
        await self.wait(700)
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
    await page.locator(SEL["email"]).fill(email)
    await page.locator(SEL["continue"]).click()
    pw = page.locator(SEL["password"])
    await pw.wait_for(state="visible", timeout=30000)
    await pw.fill(password)
    await page.locator(SEL["signin"]).click()
    try:
        await page.wait_for_url(re.compile(r"/documents"), timeout=60000)
    except PWTimeout:
        await ui.shot("sign-in stuck")
        if await page.locator(SEL["totp"]).count():
            raise RuntimeError("the account has two-factor auth on; sign in by hand once and pass --state")
        raise RuntimeError("sign-in did not reach /documents (wrong password? reCAPTCHA? see screenshot)")
    await ui.shot("signed in")


async def create_document(ui: Ui, name: str) -> str:
    page = ui.page
    await page.goto(f"{BASE_URL}/documents", wait_until="domcontentloaded")
    await page.locator(SEL["create"]).click()
    await page.locator(SEL["create_document"]).click()
    await page.locator(SEL["document_name"]).fill(name)
    await ui.shot("new document dialog")
    await page.locator(SEL["document_ok"]).click()
    await page.wait_for_url(re.compile(r"/documents/\w+/w/\w+/e/\w+"), timeout=60000)
    return page.url


async def open_part_studio(ui: Ui, url: str) -> None:
    await ui.page.goto(url, wait_until="domcontentloaded")
    await ui.page.locator(SEL["canvas"]).wait_for(state="visible", timeout=90000)
    await ui.tree("Top")
    await ui.wait(8000)                     # WebSockets never go idle; give the graphics time
    await ui.shot("part studio open")


async def new_sketch_on_top(ui: Ui) -> None:
    await ui.key("escape")
    await (await ui.tree("Top")).click()
    await ui.key("sketch")
    await ui.wait(800)
    await ui.centre_on_origin()


async def circle_on_origin(ui: Ui, diameter: float, label: str) -> float:
    """Drag a circle out from the origin, then set its diameter. Returns px/mm."""
    await ui.key("circle")
    r = 0.12 * ui.span
    await ui.drag(ui.cx, ui.cy, ui.cx + r, ui.cy)
    await ui.key("escape")
    edge = (ui.cx + r * 0.7071, ui.cy - r * 0.7071)
    drawn = await ui.dimension([edge], (ui.cx + r + 60, ui.cy - r - 40), diameter)
    await ui.shot(f"{label} sketch")
    return 2 * r / drawn


async def extrude(ui: Ui, sketch: str, op: str, depth_mm: float | None, label: str) -> None:
    """Extrude every region of a sketch, picked from the feature list so that a
    solid above the sketch plane can't be picked instead."""
    page = ui.page
    await ui.key("escape")
    await ui.key("extrude")
    await (await ui.tree(sketch)).click()
    await ui.wait()
    if op != "New":
        await page.locator("[data-parameter-id='operationType']").get_by_text(op, exact=True).first.click()
    if depth_mm is None:
        await page.locator("[data-parameter-id='endBound']").get_by_text("Blind", exact=True).first.click()
        await page.get_by_text("Through all", exact=True).first.click()
    else:
        depth = page.locator("[data-parameter-id='depth'] input").first
        await depth.fill(f"{depth_mm:g} mm")
        await depth.press("Tab")
    await ui.wait()
    await ui.shot(f"{label}: extrude {op.lower()} {'through all' if depth_mm is None else f'{depth_mm:g} mm'}")
    await ui.accept()


async def mirror_twice(ui: Ui, feature: str, first: int) -> None:
    """Feature-mirror across Right, then the feature and its mirror across Front.
    Onshape names the results "Mirror <first>" and "Mirror <first + 1>"."""
    page = ui.page
    for plane, picks in (("Right", [feature]), ("Front", [feature, f"Mirror {first}"])):
        await ui.key("escape")
        await ui.key("search_tools")
        await page.keyboard.type("Mirror", delay=40)
        await ui.wait(700)
        await page.keyboard.press("Enter")
        await ui.wait(1000)
        await page.locator("[data-parameter-id='patternType']").get_by_text("Part mirror").first.click()
        await page.get_by_text("Feature mirror", exact=True).first.click()
        await ui.wait()
        for f in picks:
            await (await ui.tree(f)).click()
        await page.locator("[data-parameter-id='mirrorPlane']").click()
        await (await ui.tree(plane)).click()
        await ui.shot(f"mirror {feature} across {plane}")
        await ui.accept()


async def square_at(ui: Ui, side: float, x: float, y: float, label: str, anchored: bool) -> None:
    """A centre-point rectangle side x side with its centre at (x, y) mm. When
    anchored, it is dragged out from the origin itself."""
    await ui.key("center_rectangle")
    h = 0.1 * ui.span
    if anchored:
        c = (ui.cx, ui.cy)
    else:                                   # anywhere in the right quadrant; dimensions move it
        c = (ui.cx + 0.25 * ui.span * (1 if x > 0 else -1), ui.cy - 0.25 * ui.span * (1 if y > 0 else -1))
    await ui.drag(c[0], c[1], c[0] + h, c[1] - h)
    await ui.key("escape")
    drawn = await ui.dimension([(c[0], c[1] - h)], (c[0], c[1] - h - 40), side)       # top edge
    ppm = 2 * h / drawn
    # The width changed about the centre; the right edge is now side / 2 away.
    await ui.dimension([(c[0] + side / 2 * ppm, c[1])], (c[0] + side / 2 * ppm + 40, c[1]), side)
    if not anchored:
        # Centre point to the origin: horizontal (placed below), then vertical (placed left).
        await ui.dimension([c, "Origin"], ((c[0] + ui.cx) / 2, max(c[1], ui.cy) + 60), abs(x))
        c = (ui.cx + x * ppm, c[1])
        await ui.dimension([c, "Origin"], (min(c[0], ui.cx) - 60, (c[1] + ui.cy) / 2), abs(y))
    await ui.shot(f"{label} sketch")


async def build_base(ui: Ui, p: Params) -> None:
    # 1. Plate
    await new_sketch_on_top(ui)
    await square_at(ui, p.base_size, 0, 0, "plate", anchored=True)
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
    await square_at(ui, p.post_w, p.post_c, p.post_c, "post", anchored=False)
    await ui.accept()
    await extrude(ui, "Sketch 4", "Add", round(p.z_deck, 2), "post")
    await mirror_twice(ui, "Extrude 4", first=1)
    # 5. One bolt hole, then mirror it into four.
    await new_sketch_on_top(ui)
    await ui.key("circle")
    d = 0.1 * ui.span
    c = (ui.cx + 0.25 * ui.span, ui.cy - 0.25 * ui.span)
    await ui.drag(c[0], c[1], c[0] + d, c[1])
    await ui.key("escape")
    drawn = await ui.dimension([(c[0] + d, c[1])], (c[0] + d + 50, c[1] - 30), p.bolt_clear_d)
    ppm = 2 * d / drawn
    await ui.dimension([c, "Origin"], ((c[0] + ui.cx) / 2, ui.cy + 60), p.bolt_xy)
    c = (ui.cx + p.bolt_xy * ppm, c[1])
    await ui.dimension([c, "Origin"], (ui.cx - 60, (c[1] + ui.cy) / 2), p.bolt_xy)
    await ui.shot("bolt hole sketch")
    await ui.accept()
    await extrude(ui, "Sketch 5", "Remove", None, "bolt hole")
    await mirror_twice(ui, "Extrude 5", first=3)
    await ui.key("isometric")
    await ui.key("zoom_fit")
    await ui.wait(1500)
    await ui.shot("base finished")


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chrome", help="Chrome/Chromium binary to use instead of Playwright's own")
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--slow", type=int, default=0, help="extra ms after every action")
    ap.add_argument("--state", type=Path, help="reuse a saved session (Playwright storage state)")
    ap.add_argument("--save-state", type=Path, help="save the session here after signing in")
    ap.add_argument("--document-url", help="work in an existing Part Studio instead of creating a document")
    ap.add_argument("--name", default=f"OT-2 lid camera mount (UI build {time.strftime('%Y-%m-%d %H:%M')})")
    ap.add_argument("--signin-only", action="store_true", help="load the sign-in page, screenshot it, stop")
    args = ap.parse_args()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=args.chrome, headless=not args.headed,
            # Onshape needs WebGL. Without a GPU, SwiftShader provides it; Chrome 137+
            # no longer falls back to it on its own.
            args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        context = await browser.new_context(viewport={"width": 1600, "height": 1000},
                                            storage_state=str(args.state) if args.state else None)
        ui = Ui(await context.new_page(), args.slow)
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
            if not args.state:
                email, password = os.environ.get("ONSHAPE_EMAIL"), os.environ.get("ONSHAPE_PASSWORD")
                if not (email and password):
                    raise SystemExit("set ONSHAPE_EMAIL and ONSHAPE_PASSWORD, or pass --state (see the README)")
                await sign_in(ui, email, password)
                if args.save_state:
                    await context.storage_state(path=str(args.save_state))
            url = args.document_url or await create_document(ui, args.name)
            print("document:", url)
            await open_part_studio(ui, url)
            await build_base(ui, Params())
            print("done:", ui.page.url)
        except Exception:
            await ui.shot("failed here")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
