#!/usr/bin/env python3
"""Screen-record onshape_ui.py building the lid-mount base, and put it on YouTube.

Attaches to the Chrome that rig.sh started, signs in off camera, then records the whole
virtual display with ffmpeg while onshape_ui.py's own steps run unchanged. Two things are
drawn over the page for the viewer (overlay.js), both invisible to Onshape:

  * a pointer, click ripples and key badges. Playwright moves the mouse through DevTools,
    so the X cursor never moves and a raw recording would show no pointer at all;
  * a caption naming the current step. The first caption of each feature becomes a
    chapter in the YouTube description.

    ./rig.sh start
    python record_ui_build.py --folder-url 'https://cad.onshape.com/documents?nodeId=...&resourceType=folder'
    python record_ui_build.py --folder-url ... --upload --privacy unlisted

The login is typed before ffmpeg starts, so it is never on screen. Uploading uses the
upload-only YouTube token (YOUTUBE_UPLOAD_TOKEN_PICKLE_B64) through youtube/yt_service.py.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ONSHAPE = HERE.parent
REPO = ONSHAPE.parents[2]
sys.path.insert(0, str(ONSHAPE))
import onshape_ui as ou  # noqa: E402

BANNER = "Claude (AI agent) driving Onshape's web UI · mouse and keyboard only, no API · real time"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Feature label (as onshape_ui passes it) -> chapter title.
CHAPTERS = {
    "plate": "Plate, 112 × 112 × 6 mm",
    "collar": "Light collar, Ø52 mm",
    "aperture": "Lens aperture, Ø46 mm through",
    "post": "Posts: one drawn, three mirrored",
    "bolt hole": "Bolt holes: one drawn, three mirrored",
}


class Session:
    """The recording: ffmpeg on the display, the caption on the page, and a timeline."""

    def __init__(self, page, display: str, size: str, fps: int, out: Path):
        self.page, self.display, self.size, self.fps, self.out = page, display, size, fps, out
        self.raw = out / "raw.mkv"
        self.events: list[dict] = []
        self.caption_text = ""
        self.label = ""
        self.proc = None
        self.t0 = 0.0

    def t(self) -> float:
        return round(time.monotonic() - self.t0, 2)

    def start(self) -> None:
        self.proc = subprocess.Popen(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-f", "x11grab", "-draw_mouse", "0", "-framerate", str(self.fps),
             "-video_size", self.size, "-i", self.display,
             "-c:v", "libx264", "-preset", "ultrafast", "-crf", "16", "-pix_fmt", "yuv420p", str(self.raw)],
            stdin=subprocess.PIPE)
        self.t0 = time.monotonic()

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.stdin.write(b"q")
            self.proc.stdin.flush()
            self.proc.wait(timeout=120)

    async def show(self) -> None:
        try:
            await self.page.evaluate("([b, c]) => window.__rec && (__rec.banner(b), __rec.caption(c))",
                                     [BANNER, self.caption_text])
        except Exception:                   # mid-navigation; the next load event puts it back
            pass

    async def caption(self, text: str, chapter: str | None = None) -> None:
        self.caption_text = text
        self.events.append({"t": self.t(), "caption": text, **({"chapter": chapter} if chapter else {})})
        print(f"[{self.t():7.1f}s] {text}", flush=True)
        await self.show()


def captioned(rec: Session) -> None:
    """Wrap onshape_ui's step functions so each one captions itself first. build_base
    calls them through the module, so replacing the module attributes is enough."""

    def wrap(name, describe):
        fn = getattr(ou, name)

        async def inner(ui, *a, **kw):
            label = kw.get("label", a[-1] if a and isinstance(a[-1], str) else None)
            if name in ("square_on_origin", "circle_on_origin", "square_at", "circle_at") and label:
                rec.label = label
            first = rec.label and rec.label not in {e.get("chapter") for e in rec.events}
            await rec.caption(describe(*a, **kw), chapter=rec.label if first else None)
            return await fn(ui, *a, **kw)
        setattr(ou, name, inner)

    title = lambda s: s[:1].upper() + s[1:]  # noqa: E731
    wrap("new_sketch_on_top", lambda: "New sketch on the Top plane, viewed square and zoomed to fit")
    wrap("square_on_origin", lambda side, label:
         f"{title(label)}: drag a centre-point rectangle from the origin, type {side:g} mm for each side")
    wrap("circle_on_origin", lambda d, label:
         f"{title(label)}: drag a circle from the origin, dimension it Ø{d:g} mm")
    wrap("square_at", lambda side, x, y, label:
         f"{title(label)}: a {side:g} mm square, placed {x - side / 2:g} mm off the Right and Front planes")
    wrap("circle_at", lambda d, x, y, label:
         f"{title(label)}: Ø{d:g} mm circle, centre dimensioned to ({x:g}, {y:g}) mm")
    wrap("extrude", lambda sketch, op, depth, label:
         f"{title(label)}: extrude {sketch}, "
         + ("new part" if op == "New" else op.lower())
         + (f", {depth:g} mm" if depth is not None else ", through all, symmetric"))
    wrap("mirror_twice", lambda feature, first:
         f"{title(rec.label)}: mirror {feature} across the Right plane, then both across Front")


async def create_document_in(ui: ou.Ui, rec: Session, folder_url: str | None, name: str) -> str:
    """onshape_ui.create_document, but in a folder rather than the account's top level."""
    page = ui.page
    await rec.caption("Create a document in vcl-shared › OT-2 Overhead Camera", chapter="document")
    await ui.wait(1500)
    await page.locator(ou.SEL["create"]).click()
    await ui.wait(700)
    await page.locator(ou.SEL["create_document"]).click()
    box = page.locator(ou.SEL["document_name"])
    await box.wait_for(state="visible", timeout=20000)
    await box.click(click_count=3)
    await page.keyboard.type(name, delay=40)
    await ui.wait(800)
    await page.locator(ou.SEL["document_ok"]).click()
    await page.wait_for_url(re.compile(r"/documents/\w+/w/\w+/e/\w+"), timeout=60000)
    return page.url


async def orbit(ui: ou.Ui, px: float = 320, seconds: float = 5.0) -> None:
    """Right-drag across the canvas: Onshape rotates the view, nothing else."""
    m, steps = ui.page.mouse, 60
    x0, y0 = ui.cx + 0.25 * ui.span, ui.cy + 0.30 * ui.span
    await m.move(x0, y0)
    await ui.wait(300)
    await m.down(button="right")
    for i in range(1, steps + 1):
        await m.move(x0 - px * i / steps, y0 - 0.15 * px * i / steps)
        await ui.page.wait_for_timeout(int(1000 * seconds / steps))
    await m.up(button="right")
    await ui.wait(600)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def finish(rec: Session, title_lines: list[str], hold_s: float = 4.0) -> tuple[Path, float]:
    """Prepend a title card and encode for upload. Returns the file and the card's length."""
    out = rec.out
    w, h = rec.size.split("x")
    draw = []
    for i, (text, size, font, colour, y) in enumerate(zip(
            title_lines, (54, 32, 32, 26), (FONT_BOLD, FONT, FONT, FONT),
            ("white", "0xe0e0e0", "0xe0e0e0", "0xffcc80"), ("h/2-150", "h/2-40", "h/2+10", "h/2+110"))):
        f = out / f"title{i}.txt"
        f.write_text(text)
        draw.append(f"drawtext=fontfile={font}:textfile={f}:fontsize={size}:fontcolor={colour}:x=(w-text_w)/2:y={y}")
    card = out / "title.mkv"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
         "-i", f"color=c=0x1d1f24:s={w}x{h}:r={rec.fps}:d={hold_s}", "-vf", ",".join(draw),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(card)])
    final = out / "onshape_ui_build.mp4"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(card), "-i", str(rec.raw),
         "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(rec.fps),
         "-movflags", "+faststart", str(final)])
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-sseof", "-2", "-i", str(final),
         "-frames:v", "1", str(out / "poster.png")])
    return final, hold_s


def chapters(events: list[dict], offset: float, min_s: float = 10.0) -> list[tuple[float, str]]:
    """YouTube chapters: the first at 0:00, each at least 10 s long, at least three."""
    names = dict(CHAPTERS, document="New document in vcl-shared › OT-2 Overhead Camera",
                 check="Check: volume from Onshape's mass properties")
    marks = [(0.0 if not i else e["t"] + offset, names.get(e["chapter"], e["chapter"]))
             for i, e in enumerate(x for x in events if "chapter" in x)]
    kept: list[tuple[float, str]] = []
    for t, name in marks:
        if kept and t - kept[-1][0] < min_s:
            continue
        kept.append((t, name))
    return kept


def stamp(t: float) -> str:
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cdp", default="http://127.0.0.1:9222")
    ap.add_argument("--display", default=os.environ.get("DISP", ":99"))
    ap.add_argument("--size", default=os.environ.get("SIZE", "1920x1080"))
    ap.add_argument("--fps", type=int, default=15)
    ap.add_argument("--out", type=Path, default=Path("/tmp/onshape-rec/out"))
    ap.add_argument("--folder-url", help="Onshape folder to create the document in (open it and copy the URL)")
    ap.add_argument("--name", default=f"OT-2 lid camera mount (UI build, screen-recorded, {time.strftime('%Y-%m-%d')})")
    ap.add_argument("--upload", action="store_true", help="upload with youtube/yt_service.py")
    ap.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    ap.add_argument("--pr", default="https://github.com/vertical-cloud-lab/byu-vcl/pull/234")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    ou.SHOTS = args.out / "screenshots"

    async with async_playwright() as pw:
        browser = await pw.chromium.connect_over_cdp(args.cdp)
        context = browser.contexts[0]
        pages = [pg for pg in context.pages if not pg.url.startswith(("devtools:", "chrome:"))]
        page = pages[-1] if pages else await context.new_page()
        ui = ou.Ui(page)

        # Off camera: sign in, then open the folder with the overlay in place.
        if not await ou.signed_in(ui):
            await ou.sign_in(ui, os.environ.get("ONSHAPE_USERNAME") or os.environ["ONSHAPE_EMAIL"],
                             os.environ["ONSHAPE_PASSWORD"])
        overlay = (HERE / "overlay.js").read_text()
        await context.add_init_script(overlay)
        await page.goto(args.folder_url or f"{ou.BASE_URL}/documents", wait_until="domcontentloaded")
        await ui.wait(6000)
        await page.evaluate(overlay)
        await page.mouse.move(960, 600)

        rec = Session(page, args.display, args.size, args.fps, args.out)
        page.on("load", lambda _: asyncio.ensure_future(rec.show()))   # a full page load drops the caption
        captioned(rec)
        result: dict = {"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        rec.start()
        try:
            url = await create_document_in(ui, rec, args.folder_url, args.name)
            result["document"] = url
            await rec.caption("The new document opens on an empty Part Studio")
            await ou.open_part_studio(ui, url)
            await ou.build_base(ui, ou.Params())
            await rec.caption("All 14 features built. Right-drag to turn the view")
            await orbit(ui)
            await ui.key("isometric")
            await ui.wait(1500)
            await rec.caption("Check: select Part 1 and open Onshape's mass properties", chapter="check")
            volume = await ou.read_volume(ui)
            result["volume_mm3"] = volume
            # Onshape's figure varies by a few hundredths between runs; the smallest
            # feature, one bolt hole, is 95 mm^3.
            result["volume_ok"] = abs(volume - ou.EXPECTED_MM3) < 1
            await rec.caption(f"Volume {volume:,.3f} mm³: " + (
                f"the CadQuery model's {ou.EXPECTED_MM3:,.3f}, to Onshape's numerical tolerance" if result["volume_ok"]
                else f"expected {ou.EXPECTED_MM3:,.3f}, so a feature went wrong"))
            await ui.wait(9000)
            if not result["volume_ok"]:
                raise RuntimeError(f"volume {volume} mm^3, expected {ou.EXPECTED_MM3}: not uploading")
        except Exception as exc:
            result["error"] = repr(exc)
            await ui.shot("failed here")
            raise
        finally:
            result["recorded_s"] = rec.t()
            rec.stop()
            result["events"] = rec.events
            (args.out / "run.json").write_text(json.dumps(result, indent=1, ensure_ascii=False))

    date = time.strftime("%Y-%m-%d")
    final, offset = finish(rec, [
        "OT-2 lid camera mount: the base, built in Onshape",
        "by Claude, an AI agent, through the web UI",
        "mouse drags, clicks and typed dimensions; no API calls",
        f"BYU Vertical Cloud Lab · recorded {date} · real time, no cuts",
    ])
    marks = chapters(rec.events, offset)
    minutes = result["recorded_s"] / 60
    description = "\n".join([
        "Claude, an AI agent, builds the base of a camera mount for an Opentrons OT-2 liquid handler "
        "in Onshape by driving the web app the way a person would: mouse drags to sketch, clicks "
        "to pick edges and planes, typed dimensions and keyboard shortcuts. No Onshape API calls. "
        f"Real time, no cuts (about {minutes:.0f} minutes).",
        "",
        f"The part has 14 features: a 112 mm plate, a light collar, a 46 mm lens aperture, four "
        f"99.66 mm posts and four M4 bolt holes. Onshape's mass properties give "
        f"{result['volume_mm3']:,.3f} mm³; the CadQuery model it was specified from is "
        f"{ou.EXPECTED_MM3:,.3f} mm³, the same to within Onshape's numerical tolerance.",
        "",
        "The browser ran headed on a virtual display. Playwright's input does not move the system "
        "cursor, so the pointer, the key badges and the captions are drawn over the page for "
        "the recording.",
        "",
        "Chapters",
        *[f"{stamp(t)} {name}" for t, name in marks],
        "",
        f"Code and notes: {args.pr}",
    ])
    meta = {"title": "Claude (AI agent) builds a part in Onshape with mouse and keyboard: OT-2 camera mount",
            "description": description, "file": str(final), "chapters": marks, **result}
    (args.out / "upload.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    print(description)

    if args.upload:
        sys.path.insert(0, str(REPO / "youtube"))
        from yt_service import upload_video
        video_id = upload_video(str(final), meta["title"], description, privacy=args.privacy,
                                tags=["Onshape", "CAD", "AI agent", "Claude", "Playwright",
                                      "browser automation", "Opentrons", "OT-2", "lab automation"])
        meta["video_id"] = video_id
        (args.out / "upload.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
        print(f"https://www.youtube.com/watch?v={video_id}")


if __name__ == "__main__":
    asyncio.run(main())
