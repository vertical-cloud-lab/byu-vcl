"""The one-servo version of the miniature doser (doser_cad.tilt_meshes): the module turns about PR 176's own hinge on one
of PR 176's MG996R-size servos, outlet up while the gantry moves and outlet down to dispense. Draws the three poses side
on, at one scale, beside a view of the whole tool, and an animation of the tilt.

Needs what module_views.py needs (its docstring has the checkout and install commands), then:
    POWDER_DOSER=/tmp/powder-doser/cad/text-to-cad xvfb-run -a -s "-screen 0 1920x1080x24" python tilt_views.py
Writes tilt_views.png and tilt_motion.gif next to this file.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from module_views import D, HERE, INK, MUTED, font, panel, render, scale_bar

SIDE = np.array([-1.0, 0.0, 0.0])                       # along the hinge, from the -x arm's side
ISO = np.array([1.05, -1.20, 0.70])                     # front right, above: the servo's side
ACCENT = (235, 104, 52)
POSES = ((D.TILT_PARK, "Park, for moves", ["outlet 10° up: the capillary slopes", "back into the tube"]),
         (D.TILT_LEVEL, "Level", ["PR 176's rest pose", "the flight's pockets hold the powder"]),
         (D.TILT_DISPENSE, "Dispense", ["the fixed module's 35°, outlet down", "the tip drops 28 mm, 9 mm nearer"]))


def to_px(p, focus, h, w, scale):
    """A doser-frame point to pixels in a SIDE render: screen right is -y, screen up is +z."""
    k = (h / 2) / scale
    return w / 2 - (p[1] - focus[1]) * k, h / 2 - (p[2] - focus[2]) * k


def angle_marks(img, deg, focus, scale):
    """The hinge, a level line through it, and the auger's axis at `deg`, with the angle between them."""
    w, h = img.size
    d = ImageDraw.Draw(img)
    k = (h / 2) / scale
    hx, hy = to_px(D.HINGE, focus, h, w, scale)
    reach = 56.0 * k                                    # 56 mm: past the capillary's tip (48 mm from the hinge)
    for x in np.arange(0.0, reach, 12.0):              # level, dashed
        d.line((hx + x, hy, hx + min(x + 7.0, reach), hy), fill=MUTED, width=2)
    t = np.radians(deg)
    d.line((hx, hy, hx + reach * np.cos(t), hy + reach * np.sin(t)), fill=ACCENT, width=3)
    r = 0.62 * reach
    box = (hx - r, hy - r, hx + r, hy + r)
    if abs(deg) > 0.5:
        d.arc(box, start=min(0.0, deg), end=max(0.0, deg), fill=ACCENT, width=3)
    lab = f"{deg:+.0f}°".replace("-", "−") if deg else "0°"
    lx, ly = hx + (r + 10) * np.cos(t / 2), hy + (r + 10) * np.sin(t / 2) + (22 if deg >= 0 else -22)
    f = font(24, bold=True)
    d.rounded_rectangle(d.textbbox((lx, ly), lab, font=f, anchor="lm"), 4, fill=(255, 255, 255))
    d.text((lx, ly), lab, font=f, fill=ACCENT, anchor="lm")
    d.ellipse((hx - 5, hy - 5, hx + 5, hy + 5), outline=INK, width=2)
    f = font(17)
    d.rounded_rectangle(d.textbbox((hx - 12, hy - 12), "hinge", font=f, anchor="rb"), 3, fill=(255, 255, 255))
    d.text((hx - 12, hy - 12), "hinge", font=f, fill=INK, anchor="rb")


def views(w=480, h=600):
    focus, scale = np.array([0.0, 59.0, 40.0]), 92.0      # side panels: one focus and scale, so the poses compare
    panels = []
    for deg, title, lines in POSES:
        im = render(D.tilt_meshes(deg), w, h, scale, focus=focus, view=SIDE)
        angle_marks(im, deg, focus, scale)
        panels.append(panel(im, f"{title} ({deg:+.0f}°)".replace("+0°", "0°").replace("-", "−"), lines))
        scale_bar(im, scale, h, mm=20)
    tool = D.tilt_meshes(D.TILT_DISPENSE)
    p = np.vstack([m.points for m in tool.values()])
    s = p.max(axis=0) - p.min(axis=0)
    lvl = np.vstack([m.points for m in D.tilt_meshes(D.TILT_LEVEL).values()])
    sl = lvl.max(axis=0) - lvl.min(axis=0)
    iso = panel(render(tool, w, h, 105.0, view=ISO), "One servo, one hinge",
                [f"{sl[0]:.0f} × {sl[1]:.0f} × {sl[2]:.0f} mm at level, with its bracket",
                 "MG996R-size servo on the hinge axis"])
    scale_bar(iso, 105.0, h, mm=50)
    sheet = Image.new("RGB", (4 * w + 5 * 12, h + 2 * 12), (232, 234, 238))
    for i, im in enumerate([iso] + panels):
        sheet.paste(im, (12 + i * (w + 12), 12))
    sheet.save(HERE / "tilt_views.png", optimize=True)
    print("tilt_views.png", sheet.size, "tool at level", sl.round(1), "at 35 deg", s.round(1))


def motion(w=480, h=400):
    """Park, down to dispense, hold, and back up, in a fixed camera."""
    a, b = D.TILT_PARK, D.TILT_DISPENSE
    ease = lambda n: a + (b - a) * (1 - np.cos(np.linspace(0.0, np.pi, n))) / 2
    seq = [a] * 6 + list(ease(16)) + [b] * 8 + list(ease(16)[::-1]) + [a] * 2
    p = np.vstack([m.points for m in D.tilt_meshes(D.TILT_LEVEL).values()])
    c = (p.min(axis=0) + p.max(axis=0)) / 2 + np.array([0.0, 0.0, 8.0])
    frames = []
    for deg in seq:
        im = render(D.tilt_meshes(deg), w, h, 82.0, focus=c, view=ISO)
        d = ImageDraw.Draw(im)
        d.text((12, 10), "Miniature doser, one-servo tilt", font=font(18, bold=True), fill=INK)
        state = "park, for moves" if deg <= a + 0.1 else "dispense" if deg >= b - 0.1 else "tilting"
        d.text((12, 36), f"{deg:+.0f}°  {state}".replace("-", "−"), font=font(17), fill=MUTED)
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=128))
    frames[0].save(HERE / "tilt_motion.gif", save_all=True, append_images=frames[1:], duration=100, loop=0,
                   optimize=True)
    print("tilt_motion.gif", len(frames), "frames", (HERE / "tilt_motion.gif").stat().st_size, "bytes")


if __name__ == "__main__":
    views()
    motion()
