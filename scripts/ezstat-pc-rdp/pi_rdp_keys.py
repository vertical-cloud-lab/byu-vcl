"""Send keystrokes to the EZstat Pro PC through a running Remote Desktop session (#231).

Runs on the CubXL Pi, inside the session directory that pi_rdp_look.sh made. It
injects key events into that session's Xvfb display with the XTEST extension, and
xfreerdp3 forwards them to the PC as scancodes. Keyboard only: it never sends a
mouse event. python-xlib (pure Python) is imported from wheels copied into
DIR/whl, so nothing is installed on the Pi.

    python3 -I pi_rdp_keys.py DIR < SCRIPT

SCRIPT has one action per line:

    key super+r          a key combination: modifiers, then an X keysym name
    type dir /b          type the rest of the line literally (ASCII only)
    sleep 1.5            wait, in seconds

Every key pressed is released again, even on an error.
"""

import glob
import os
import sys
import time

DIR = sys.argv[1]
sys.path[:0] = sorted(glob.glob(os.path.join(DIR, "whl", "*.whl")))

from Xlib import X, XK, display  # noqa: E402
from Xlib.ext import xtest  # noqa: E402

GAP_S = 0.03
MODIFIERS = {"ctrl": "Control_L", "shift": "Shift_L", "alt": "Alt_L", "super": "Super_L"}


def read(name):
    with open(os.path.join(DIR, name)) as f:
        return f.read().strip()


os.environ["DISPLAY"] = read("display")
os.environ["XAUTHORITY"] = read("xauth")
d = display.Display()
if not d.query_extension("XTEST").present:
    sys.exit("XTEST extension missing on the display")
held = []


def press(keycode):
    xtest.fake_input(d, X.KeyPress, keycode)
    d.sync()
    held.append(keycode)
    time.sleep(GAP_S)


def release(keycode):
    xtest.fake_input(d, X.KeyRelease, keycode)
    d.sync()
    held.remove(keycode)
    time.sleep(GAP_S)


def keycode_of(keysym_name):
    keysym = XK.string_to_keysym(keysym_name)
    keycode = d.keysym_to_keycode(keysym) if keysym else 0
    if not keycode:
        raise ValueError(f"no key for {keysym_name!r}")
    return keycode


def combo(spec):
    *mods, last = spec.split("+")
    codes = [keycode_of(MODIFIERS[m]) for m in mods] + [keycode_of(last)]
    for c in codes:
        press(c)
    for c in reversed(codes):
        release(c)


def char_key(keysym):
    """(keycode, needs_shift) for a keysym, on the main keyboard block if possible.

    Xvfb's evdev keymap also puts "(" and ")" on keycodes 187 and 188, unshifted,
    and Display.keysym_to_keycode() returns those, but FreeRDP has no scancode for
    them, so nothing reaches Windows. The lowest keycode is the main-block key.
    """
    info = d.display.info
    hits = [(keycode, index) for keycode in range(info.min_keycode, info.max_keycode + 1)
            for index in (0, 1) if d.keycode_to_keysym(keycode, index) == keysym]
    if not hits:
        raise ValueError(f"no key for keysym {keysym:#x}")
    keycode, index = min(hits)
    return keycode, index == 1


def type_text(text):
    shift = keycode_of("Shift_L")
    for ch in text:
        if not " " <= ch <= "~":
            raise ValueError(f"refusing to type non-ASCII character {ch!r}")
        keycode, shifted = char_key(ord(ch))  # ASCII keysyms equal their code points
        if shifted:
            press(shift)
        press(keycode)
        release(keycode)
        if shifted:
            release(shift)


try:
    for line in sys.stdin.read().splitlines():
        action, _, arg = line.partition(" ")
        if action == "key":
            combo(arg.strip())
        elif action == "type":
            type_text(arg)
        elif action == "sleep":
            time.sleep(float(arg))
        elif action.strip():
            raise ValueError(f"unknown action {action!r}")
    print("keys sent")
finally:
    for keycode in reversed(list(held)):
        release(keycode)
    d.close()
