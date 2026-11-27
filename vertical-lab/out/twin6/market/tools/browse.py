"""Read public listing pages through the lab Pi's tunnel, at a person's pace.

Attaches to the headed Chrome that rig.sh started (Xvfb :99, DevTools on 127.0.0.1:9222, traffic out through the
CubXL Pi's SOCKS tunnel). Every page: a pause of several seconds first, mouse moves along eased Bezier curves with
jitter, wheel scrolls in uneven steps, and a check for a challenge or block page. A challenged or blocked page is
recorded (visits.jsonl, blocked=...) and left alone: nothing is clicked, solved or retried around it.
Never logs in, bids, buys or messages anyone.
"""
from __future__ import annotations

import json
import math
import random
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

RAW = Path("/tmp/market/raw")
SHOTS = Path("/tmp/market/shots")
CDP = "http://127.0.0.1:9222"
W, H = 1920, 1080
POS = [W / 2, H / 2]

BLOCKS = [
    ("ebay_interruption", r"Pardon Our Interruption"),
    ("cloudflare", r"Just a moment\.\.\.|Checking your browser|Verify you are human|Performing security verification|"
                   r"needs to review the security of your connection"),
    ("captcha", r"\bcaptcha\b|I'm not a robot|press (?:&|and) hold|Press & Hold|confirm you are (?:a )?human"),
    ("access_denied", r"Access Denied|You don't have permission to access|Request blocked|403 Forbidden|"
                      r"Sorry, you have been blocked|has been blocked|Error 1020"),
    ("incapsula", r"Incapsula incident|Request unsuccessful"),
    ("robot", r"Are you a robot|Robot or human|unusual traffic|automated (?:access|queries|requests)|bot detected"),
]


def pause(a: float, b: float) -> None:
    time.sleep(random.uniform(a, b))


def _bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def move(page, to=None) -> None:
    """One eased, slightly curved mouse path with jitter, like a hand on a trackpad."""
    x0, y0 = POS
    x1, y1 = to or (random.uniform(80, W - 80), random.uniform(140, H - 100))
    d = math.hypot(x1 - x0, y1 - y0)
    if d < 2:
        return
    nx, ny = -(y1 - y0) / d, (x1 - x0) / d
    bend = random.uniform(-0.25, 0.25) * d
    c1 = (x0 + (x1 - x0) * 0.3 + nx * bend, y0 + (y1 - y0) * 0.3 + ny * bend)
    c2 = (x0 + (x1 - x0) * 0.7 + nx * bend * 0.6, y0 + (y1 - y0) * 0.7 + ny * bend * 0.6)
    n = max(12, min(60, int(d / random.uniform(18, 32))))
    for i in range(1, n + 1):
        t = i / n
        t = t * t * (3 - 2 * t)
        x, y = _bez((x0, y0), c1, c2, (x1, y1), t)
        if i < n:
            x += random.gauss(0, 0.8)
            y += random.gauss(0, 0.8)
        page.mouse.move(x, y)
        time.sleep(random.uniform(0.006, 0.022))
    POS[0], POS[1] = x1, y1
    if random.random() < 0.3:
        pause(0.2, 0.9)


def scroll(page, steps=(2, 5)) -> None:
    for _ in range(random.randint(*steps)):
        page.mouse.wheel(0, random.choice([1, 1, 1, 0.6]) * random.uniform(260, 620))
        pause(0.35, 1.3)
        if random.random() < 0.5:
            move(page)
    if random.random() < 0.4:
        page.mouse.wheel(0, -random.uniform(150, 400))
        pause(0.3, 0.8)


def check_block(page) -> str | None:
    try:
        title = page.title() or ""
    except Exception:
        title = ""
    for name, pat in BLOCKS:
        if re.search(pat, title, re.I):
            return name
    try:
        txt = page.evaluate("() => (document.body && document.body.innerText || '').slice(0, 4000)")
        frames = page.evaluate("() => Array.from(document.querySelectorAll('iframe')).map(f => f.src || '')"
                               ".filter(s => /captcha|challenges[.]cloudflare|hcaptcha|px-cloud|perimeterx|datadome/i.test(s))"
                               ".slice(0, 3)")
    except Exception:
        return None
    for name, pat in BLOCKS:
        if len(txt) < 2500 and re.search(pat, txt, re.I):
            return name
    if frames and len(txt) < 700:
        return "challenge_iframe"
    return None


def log_visit(rec: dict) -> None:
    rec["t_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(RAW / "visits.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")


def visit(page, url: str, *, gap=(5.0, 11.0), scrolls=(2, 5), wait_ms=(1800, 3800), label="") -> dict:
    pause(*gap)
    move(page)
    status, err = None, None
    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        status = resp.status if resp else None
    except Exception as e:
        err = str(e)[:300]
    page.wait_for_timeout(random.randint(*wait_ms))
    blocked = check_block(page)
    if not blocked and not err:
        move(page)
        scroll(page, scrolls)
        move(page)
        blocked = check_block(page)
    rec = dict(url=url, final_url=page.url, status=status, title=(page.title() or "")[:200], blocked=blocked,
               error=err, label=label)
    log_visit(rec)
    return rec


CARDS_JS = r"""
(sel) => {
  const norm = h => (h || '').split('#')[0].split('?')[0].replace(/\/$/, '');
  const anchors = Array.from(document.querySelectorAll(sel)).filter(a => a.href);
  const seen = new Set(); const out = [];
  for (const a of anchors) {
    const key = norm(a.href);
    if (seen.has(key)) continue;
    // the card is the largest ancestor that links to this item only
    let card = a, el = a;
    for (let i = 0; i < 12; i++) {
      el = el.parentElement; if (!el || el === document.body) break;
      const keys = new Set(Array.from(el.querySelectorAll(sel)).map(x => norm(x.href)));
      if (keys.size > 1) break;
      if ((el.innerText || '').length > 3000) break;
      card = el;
    }
    const text = (card.innerText || '').replace(/[ \t]+/g, ' ').replace(/\n\s*\n+/g, '\n').slice(0, 1200);
    let title = '';
    const cands = [a.getAttribute('title'), a.innerText, ...(Array.from(card.querySelectorAll('h1,h2,h3,h4,[class*=title],[class*=Title],[class*=name]')).map(h => h.innerText))];
    for (const c of cands) { const t = (c || '').trim(); if (t.length > title.length && t.length < 300) title = t; }
    seen.add(key);
    out.push({href: a.href, title: title.replace(/\s+/g, ' ').slice(0, 260), text});
  }
  return out;
}
"""


def cards(page, sel: str) -> list[dict]:
    try:
        return page.evaluate(CARDS_JS, sel)
    except Exception:
        return []


def shot(page, name: str, full=False) -> str:
    p = SHOTS / name
    page.screenshot(path=str(p), full_page=full)
    return str(p)


def connect():
    pw = sync_playwright().start()
    br = pw.chromium.connect_over_cdp(CDP)
    ctx = br.contexts[0]
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.set_viewport_size({"width": W, "height": H - 80}) if False else None
    return pw, br, ctx, page
