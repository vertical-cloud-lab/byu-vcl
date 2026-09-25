#!/usr/bin/env python3
"""Point / click / drag / type / screenshot helper for a headed browser on an X display.

All input goes through XTEST (xdotool), so the page sees real hardware input
(event.isTrusted is true) and there is no WebDriver or DevTools attached.
The loop is: `shot`, look at the PNG, pick coordinates, act, `shot` again.

  hb.py shot NAME                 screenshot -> $HB_WORK/shots/NN-NAME.png
  hb.py move X Y                  curved, eased mouse move
  hb.py click X Y [BUTTON]        move then click (1=left, 3=right)
  hb.py dclick X Y                double click
  hb.py drag X1 Y1 X2 Y2          press at 1, curved move, release at 2 (sliders)
  hb.py type TEXT                 type with a jittered per-key delay
  hb.py key KEYS...               e.g. ctrl+l Return
  hb.py scroll N [X Y]            wheel N notches (+down / -up), optionally over X,Y
  hb.py text                      select-all + copy, print the page's visible text
  hb.py url                       print the address-bar URL
  hb.py wait SECONDS
"""
import math
import os
import random
import subprocess
import sys
import time

DISPLAY = os.environ.setdefault("DISPLAY", ":99")
SHOTS = os.path.join(os.environ.get("HB_WORK", "/tmp/hb"), "shots")


def xdo(*args):
    return subprocess.run(["xdotool", *map(str, args)], check=True,
                          capture_output=True, text=True).stdout


def clipboard():
    return subprocess.run(["xclip", "-selection", "clipboard", "-o"],
                          capture_output=True, text=True).stdout


def pos():
    out = dict(l.split("=") for l in xdo("getmouselocation", "--shell").split())
    return int(out["X"]), int(out["Y"])


def move(x, y):
    x0, y0 = pos()
    dist = math.hypot(x - x0, y - y0)
    if dist < 2:
        return
    # cubic Bezier with control points pushed off the straight line
    nx, ny = -(y - y0) / dist, (x - x0) / dist
    bend = random.uniform(-0.25, 0.25) * dist
    c1 = (x0 + (x - x0) * 0.3 + nx * bend, y0 + (y - y0) * 0.3 + ny * bend)
    c2 = (x0 + (x - x0) * 0.7 + nx * bend * 0.5, y0 + (y - y0) * 0.7 + ny * bend * 0.5)
    steps = max(12, min(60, int(dist / 12)))
    duration = random.uniform(0.25, 0.45) + dist / 2500
    for i in range(1, steps + 1):
        t = i / steps
        t = t * t * (3 - 2 * t)  # ease in/out
        bx = (1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * c1[0] + 3 * (1 - t) * t ** 2 * c2[0] + t ** 3 * x
        by = (1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * c1[1] + 3 * (1 - t) * t ** 2 * c2[1] + t ** 3 * y
        xdo("mousemove", round(bx), round(by))
        time.sleep(duration / steps)
    xdo("mousemove", x, y)


def click(x, y, button=1, n=1):
    move(x, y)
    time.sleep(random.uniform(0.08, 0.2))
    for _ in range(n):
        xdo("mousedown", button)
        time.sleep(random.uniform(0.05, 0.12))
        xdo("mouseup", button)
        time.sleep(random.uniform(0.06, 0.12))


def drag(x1, y1, x2, y2):
    move(x1, y1)
    time.sleep(random.uniform(0.1, 0.25))
    xdo("mousedown", 1)
    time.sleep(random.uniform(0.1, 0.2))
    move(x2, y2)
    time.sleep(random.uniform(0.1, 0.2))
    xdo("mouseup", 1)


def type_(text):
    for ch in text:
        xdo("type", "--delay", "0", ch)
        time.sleep(random.uniform(0.04, 0.14))


def scroll(n, x=None, y=None):
    if x is not None:
        move(x, y)
    button = 5 if n > 0 else 4
    for _ in range(abs(n)):
        xdo("click", button)
        time.sleep(random.uniform(0.05, 0.15))


def shot(name):
    os.makedirs(SHOTS, exist_ok=True)
    n = len([f for f in os.listdir(SHOTS) if f.endswith(".png")])
    path = os.path.join(SHOTS, f"{n:02d}-{name}.png")
    subprocess.run(["import", "-display", DISPLAY, "-window", "root", path], check=True)
    print(path)


def url():
    xdo("key", "ctrl+l")
    time.sleep(0.2)
    xdo("key", "ctrl+c")
    time.sleep(0.3)
    out = clipboard()
    xdo("key", "Escape")
    print(out.strip())


def text():
    # Focus must be on the page body, not the address bar or a dialog: click some
    # plain text on the page first.
    subprocess.run(["xclip", "-selection", "clipboard", "-i", "/dev/null"])
    xdo("key", "ctrl+a")
    time.sleep(0.3)
    xdo("key", "ctrl+c")
    time.sleep(0.5)
    print(clipboard())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, *a = sys.argv[1:]
    if cmd == "shot":
        shot(a[0] if a else "screen")
    elif cmd == "move":
        move(int(a[0]), int(a[1]))
    elif cmd == "click":
        click(int(a[0]), int(a[1]), int(a[2]) if len(a) > 2 else 1)
    elif cmd == "dclick":
        click(int(a[0]), int(a[1]), 1, 2)
    elif cmd == "drag":
        drag(*map(int, a[:4]))
    elif cmd == "type":
        type_(" ".join(a))
    elif cmd == "key":
        for k in a:
            xdo("key", k)
            time.sleep(0.15)
    elif cmd == "scroll":
        scroll(int(a[0]), *(map(int, a[1:3]) if len(a) >= 3 else ()))
    elif cmd == "text":
        text()
    elif cmd == "url":
        url()
    elif cmd == "wait":
        time.sleep(float(a[0]))
    else:
        sys.exit(__doc__)
