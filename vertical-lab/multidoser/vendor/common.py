"""Shared plumbing for vendor files (CAD, drawings, datasheets) used by both carousels.

Files live in cad/vendor/files/<vendor>/ (git-ignored: no redistribution licence).
Each fetch_*.py records what it downloaded in manifest_<vendor>.json (committed):
page URL, file URL, sha256, size and the UTC date, so a rebuild can check it has
the same bytes. Part builders call `step_or_none()` and fall back to their
dimension-table stand-in when the file is missing; `report_missing()` lists which
parts used a stand-in, and build.py prints it.

Browsing: headed Chromium (Playwright, under Xvfb) whose traffic leaves through the
doser Pi as a SOCKS5 proxy (`pi_socks.sh` here opens it on 127.0.0.1:1080), with real
mouse moves and clicks, throttled to 400 kB/s for the Pi's Wi-Fi.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

VENDOR = Path(__file__).resolve().parent
FILES = VENDOR / "files"
PROXY = "socks5://127.0.0.1:1080"
THROTTLE_BPS = 400_000
_MISSING: set[str] = set()


# ---------------------------------------------------------------- manifest
def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def record(vendor: str, key: str, path: Path, page: str, url: str, kind: str, note: str = "") -> dict:
    """Add/replace one entry in manifest_<vendor>.json for a downloaded file."""
    mf = VENDOR / f"manifest_{vendor}.json"
    data = json.loads(mf.read_text()) if mf.exists() else []
    path = Path(path)
    ent = dict(key=key, kind=kind, file=str(path.relative_to(VENDOR)), page=page, url=url,
               sha256=sha256(path), bytes=path.stat().st_size,
               retrieved=datetime.now(timezone.utc).strftime("%Y-%m-%d"), note=note)
    data = [d for d in data if not (d["key"] == key and d["kind"] == kind)] + [ent]
    mf.write_text(json.dumps(sorted(data, key=lambda d: (d["key"], d["kind"])), indent=1) + "\n")
    return ent


def manifest_entry(key: str, kind: str = "step") -> dict | None:
    for mf in sorted(VENDOR.glob("manifest_*.json")):
        for d in json.loads(mf.read_text()):
            if d["key"] == key and d["kind"] == kind:
                return d
    return None


# ---------------------------------------------------------------- CAD loading
@lru_cache(None)
def _read_step(path: str):
    import cadquery as cq
    return cq.importers.importStep(path).val()


def step_or_none(key: str, check_hash: bool = True):
    """The vendor STEP for `key` as a cq.Shape (vendor's own frame), or None if it isn't on disk
    (or its sha256 doesn't match the manifest). The caller places it in the part's frame."""
    ent = manifest_entry(key, "step")
    if ent is None:
        _MISSING.add(key)
        return None
    p = VENDOR / ent["file"]
    if not p.exists() or (check_hash and sha256(p) != ent["sha256"]):
        _MISSING.add(key)
        return None
    return _read_step(str(p))


def report_missing() -> list[str]:
    """Vendor parts that fell back to a stand-in in this process."""
    return sorted(_MISSING)


# ---------------------------------------------------------------- browser (headed, through the Pi)
def open_browser(pw, downloads: Path | None = None):
    """Headed Chromium through the Pi's SOCKS proxy, throttled. Returns (browser, context, page)."""
    browser = pw.chromium.launch(headless=False, proxy={"server": PROXY},
                                 args=["--window-size=1366,900", "--disable-blink-features=AutomationControlled"])
    ctx = browser.new_context(viewport={"width": 1366, "height": 860}, accept_downloads=True,
                              user_agent=("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                          "Chrome/131.0.0.0 Safari/537.36"), locale="en-US", timezone_id="America/Denver")
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    cdp.send("Network.enable")
    cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 40,
                                                   "downloadThroughput": THROTTLE_BPS, "uploadThroughput": 100_000})
    return browser, ctx, page


def human_move(page, x: float, y: float, steps: int | None = None) -> None:
    """Move the real pointer along a slightly curved path (shows in recordings)."""
    steps = steps or random.randint(14, 26)
    page.mouse.move(x + random.uniform(-2, 2), y + random.uniform(-2, 2), steps=steps)


def human_click(page, locator, timeout: float = 15000) -> None:
    """Scroll the element into view, move the pointer onto it, pause, click."""
    locator.scroll_into_view_if_needed(timeout=timeout)
    box = locator.bounding_box(timeout=timeout)
    if box is None:
        raise RuntimeError("element has no box")
    x = box["x"] + box["width"] * random.uniform(0.35, 0.65)
    y = box["y"] + box["height"] * random.uniform(0.35, 0.65)
    human_move(page, x, y)
    time.sleep(random.uniform(0.25, 0.7))
    page.mouse.click(x, y)


def pause(a: float = 1.5, b: float = 4.0) -> None:
    time.sleep(random.uniform(a, b))
