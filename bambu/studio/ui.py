#!/usr/bin/env python3
"""Tiny xdotool wrapper for driving Bambu Studio on :99 with visible, smooth pointer moves.

ui.py click X Y [X Y ...] | move X Y | dbl X Y | key KEYS... | type TEXT | typeenv VAR | scroll X Y N
typeenv reads the value from the environment and feeds it to xdotool on stdin, so it never
appears in argv, the terminal or a log.
"""
import os, subprocess, sys, time

ENV = dict(os.environ, DISPLAY=":99")

def xdo(*args, stdin=None):
    return subprocess.run(["xdotool", *map(str, args)], env=ENV, input=stdin, text=True,
                          capture_output=True).stdout

def pos():
    out = xdo("getmouselocation", "--shell")
    d = dict(l.split("=") for l in out.split())
    return int(d["X"]), int(d["Y"])

def move(x, y, dur=0.45):
    x0, y0 = pos()
    n = max(2, int(dur / 0.015))
    for i in range(1, n + 1):
        t = i / n
        t = t * t * (3 - 2 * t)  # smoothstep
        xdo("mousemove", int(x0 + (x - x0) * t), int(y0 + (y - y0) * t))
        time.sleep(dur / n)

def click(x, y, button=1, hover=0.35):
    move(x, y)
    time.sleep(hover)
    xdo("click", button)
    time.sleep(0.25)

if __name__ == "__main__":
    cmd, *a = sys.argv[1:]
    if cmd == "click":
        for i in range(0, len(a), 2):
            click(int(a[i]), int(a[i + 1]))
    elif cmd == "rclick":
        click(int(a[0]), int(a[1]), button=3)
    elif cmd == "dbl":
        move(int(a[0]), int(a[1])); time.sleep(0.3); xdo("click", "--repeat", 2, "--delay", 120, 1)
    elif cmd == "move":
        move(int(a[0]), int(a[1]))
    elif cmd == "key":
        for k in a:
            xdo("key", "--delay", 80, k); time.sleep(0.2)
    elif cmd == "type":
        xdo("type", "--delay", 70, "--file", "-", stdin=" ".join(a))
    elif cmd == "typeenv":
        val = os.environ[a[0]]
        xdo("type", "--delay", 70, "--file", "-", stdin=val)
        print(f"typed ${a[0]} ({len(val)} chars)")
    elif cmd == "scroll":
        move(int(a[0]), int(a[1]))
        n = int(a[2]); btn = 5 if n > 0 else 4
        for _ in range(abs(n)):
            xdo("click", btn); time.sleep(0.08)
