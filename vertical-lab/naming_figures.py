"""Figures for naming.py: the floor and the trays with their names, and label mock-ups (out/naming/).

    python3 naming.py figures
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle            # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "naming"
INK, INK2, MUTED, FILL, EDGE, ACCENT = "#1f2328", "#4b5563", "#8a8f98", "#eef0f3", "#9aa1ab", "#2f5d8a"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def _plan():
    return json.loads((HERE / "out" / "tray_plan.json").read_text())


OFFSET = {"sieve_cell": (-700, 1650), "glovebox": (0, -1650), "packaging": (0, -1150), "instron_small": (0, -1700),
          "fumehood": (-450, -1650), "ded": (750, -1650), "charger0": (-1050, -2500), "charger1": (1050, -2500),
          "instron_floor": (-900, -1650)}


def floor(rows: list[dict], path: Path) -> None:
    """The floor in plan view: every floor machine's footprint with its call name."""
    import naming as N
    plan = _plan()
    by_key = {r.get("key"): r for r in rows if r["kind"] == "station"}
    fig, ax = plt.subplots(figsize=(16, 10.5), dpi=110)
    x0, x1, y0, y1 = plan["floor"]["aisle_mm"]
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#f6f7f9", ec="none", zorder=0))
    ax.text(x0 + 150, (y0 + y1) / 2, "aisle: the MiR250s' turning lane", color=MUTED, fontsize=9, va="center")
    for key, (a, b, c, d) in plan["floor"]["machines"].items():
        st = by_key.get(key)
        shuttle = key in ("vlm", "vlm2")
        ax.add_patch(Rectangle((a, c), b - a, d - c, fc="#e3e9f0" if shuttle else FILL,
                               ec=ACCENT if shuttle else EDGE, lw=1.2, zorder=1))
        if st is None:                                  # the chargers
            name, what = ("charger-1" if key == "charger0" else "charger-2"), "MiR charger"
        else:
            name, what = st["name"], N.STATIONS[key][2]
        what = what if len(what) < 34 else what[:32].rsplit(" ", 1)[0] + " ..."
        cx, cy = (a + b) / 2, (c + d) / 2
        big = 13 if (b - a) > 1500 else 10.5
        off = OFFSET.get(key)
        if off is None and (b - a) >= 1100:
            ax.text(cx, cy + 60, name, ha="center", va="bottom", fontsize=big, weight="bold", color=INK, zorder=3)
            ax.text(cx, cy - 40, what, ha="center", va="top", fontsize=7.2, color=INK2, zorder=3)
            continue
        dx, dy = off if off else (0, -(d - c) / 2 - 650)
        tx, ty = cx + dx, cy + dy
        ax.annotate("", xy=(cx, cy), xytext=(tx, ty), arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7),
                    zorder=2)
        ax.text(tx, ty + 40, name, ha="center", va="bottom", fontsize=10.5, weight="bold", color=INK, zorder=3,
                bbox=dict(fc="white", ec="none", pad=0.5))
        ax.text(tx, ty - 30, what, ha="center", va="top", fontsize=7.0, color=INK2, zorder=3,
                bbox=dict(fc="white", ec="none", pad=0.3))
    # the two robots, parked on their chargers' approach in the aisle
    for i, nm in enumerate(("elsie", "freddy")):
        a, b, c, d = plan["floor"]["machines"][f"charger{i}"]
        ax.add_patch(FancyBboxPatch(((a + b) / 2 - 290, d + 150), 580, 900, boxstyle="round,pad=0,rounding_size=60",
                                    fc="white", ec=INK, lw=1.2, zorder=2))
        ax.text((a + b) / 2, d + 600, nm, ha="center", va="center", fontsize=10, weight="bold", rotation=90, zorder=3)
    ax.text(-6500, -12350, "Not on the set-up floor yet: aston (the ICP-MS station, planned past the wire EDM, "
            "notes/icpms.md)\nand blodgett (the atomizer's BN coating station, atom_bn_station.py).", fontsize=8.5,
            color=INK2, va="top")
    ax.text(-11600, 2050, "Equipment names on the floor (plan view). Bold: the call name. Below it: what it is.",
            fontsize=12, color=INK, weight="bold")
    ax.text(-11600, 1700, "Shuttles are named for the peaks over Provo, robots for robots of history, printers for "
            "printers and laser pioneers, every other station for someone whose own work is its job.",
            fontsize=9.5, color=INK2)
    ax.set_xlim(-12000, 12200)
    ax.set_ylim(-12900, 2300)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot([-11500, -9500], [-12700, -12700], color=INK, lw=2)
    ax.text(-10500, -12620, "2 m", ha="center", va="bottom", fontsize=9, color=INK)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def trays(rows: list[dict], path: Path) -> None:
    """Every tray in plan view, in its Shuttle's slot order, each item labelled with its name."""
    import naming as N
    plan = _plan()
    names = {}
    for t, d in plan["trays"].items():
        names[t], twins = [], {}
        for it in d["items"]:
            lab = it["item"]
            if it["kind"] in ("lines",) or lab.endswith("post"):
                continue
            if it["kind"] == "ups":
                nm = "ups"
            elif it["kind"] == "monitor":
                nm = "air"
            elif it["kind"] == "plate":
                nm = "plate"
            elif it["kind"] == "cam":
                nm = f"cam{lab.split()[0].split('_')[1][1:]}"
            else:
                hit = next(((k, s) for txt, k, s in N.TRAY_ITEMS if txt in lab), (None, None))
                key, suf = hit
                if key == "tray":
                    nm = f"tray-{t.lower()}-{suf}"
                elif suf == "#":
                    twins[key] = twins.get(key, 0) + 1
                    nm = f"{N.STATIONS[key][0]}-{twins[key]}"
                else:
                    nm = N.STATIONS[key][0] + (f"-{suf}" if suf else "")
            names[t].append((nm, it["box_mm"], it["kind"]))
    sh = {1: [], 2: []}
    for t, d in plan["trays"].items():
        sh[d["shuttle"]].append((d["slot"], t, d))
    order = {1: ["R1", "R2", "R3", "R4", "R5", "F0", "F1", "F2"], 2: ["2R1", "2R2", "2R3", "2R4", "2R5", "2R6", "2F0",
                                                                       "2F0b", "2F1", "2F2"]}
    nrow = max(len(v) for v in sh.values())
    fig, axs = plt.subplots(nrow, 2, figsize=(17, 2.15 * nrow), dpi=100)
    for col, s in enumerate((1, 2)):
        items = sorted(sh[s], key=lambda e: order[s].index(e[0]) if e[0] in order[s] else 99)
        for row in range(nrow):
            ax = axs[row, col]
            ax.axis("off")
            if row >= len(items):
                continue
            slot, t, d = items[row]
            ax.add_patch(Rectangle((-1225, -432), 2450, 864, fc="#fafbfc", ec=EDGE, lw=1))
            for nm, (bx0, bx1, by0, by1, _z0, _z1), kind in names[t]:
                small = kind in ("ups", "monitor", "plate", "cam")
                ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, fc="white" if small else FILL,
                                       ec=MUTED if small else EDGE, lw=0.6 if small else 0.9))
                if kind == "monitor":                    # it sits on the UPS: say so beside it, not over it
                    ax.text(bx1 + 15, (by0 + by1) / 2, nm, ha="left", va="center", fontsize=5.5, color=INK2)
                    continue
                w, h = bx1 - bx0, by1 - by0
                fs, text, rot = (6.0 if small else 9.5), nm, 0
                MM_PER_CHAR_PT = 5.4                      # about 0.6 em a character: a panel is ~4 in for 2520 mm
                if len(text) * MM_PER_CHAR_PT * fs > 0.92 * w:
                    if h > 1.6 * w:                       # tall and narrow: along its length
                        rot = 90
                        fs = min(fs, 0.92 * h / (len(text) * MM_PER_CHAR_PT))
                    elif "-" in text and not small:
                        text = text.replace("-", "-\n", 1)
                        fs = min(fs, 0.92 * w / (max(len(x) for x in text.split("\n")) * MM_PER_CHAR_PT))
                    else:
                        fs = 0.92 * w / (len(text) * MM_PER_CHAR_PT)
                ax.text((bx0 + bx1) / 2, (by0 + by1) / 2, text, ha="center", va="center", fontsize=max(fs, 4.5),
                        weight="normal" if small else "bold", color=INK2 if small else INK, rotation=rot,
                        linespacing=0.95)
            shname = N.STATIONS["vlm" if s == 1 else "vlm2"][0]
            ax.text(-1225, 470, f"tray {t} · “{N.NATO[t]}”", fontsize=10.5, weight="bold", color=INK,
                    va="bottom")
            role = d["role"].replace(", second rack", " (rack 2)").replace(", second store", " (store 2)")
            ax.text(-1225 + 1000, 478, role, fontsize=7.4, color=INK2, va="bottom", ha="left")
            ax.text(1225, 470, f"{shname} {slot}", fontsize=9, color=ACCENT, va="bottom", ha="right",
                    weight="bold")
            ax.set_xlim(-1260, 1260)
            ax.set_ylim(-470, 640)
            ax.set_aspect("equal")
    axs[0, 0].set_title("Shuttle 1: timp", fontsize=13, weight="bold", color=ACCENT, loc="left", pad=16)
    axs[0, 1].set_title("Shuttle 2: nebo", fontsize=13, weight="bold", color=ACCENT, loc="left", pad=16)
    fig.suptitle("The trays and what is on them, named (plan view, front of the tray down). Each tray's own services "
                 "take its name: on tray D, cam0 is tray-d-cam0, ups is tray-d-ups, air (the AirGradient on the UPS) "
                 "is tray-d-air.", fontsize=10.5, x=0.02, ha="left", y=0.997)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ labels
def _qr(text: str, px: int):
    import qrcode
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=1, box_size=10)
    q.add_data(text)
    q.make(fit=True)
    return q.make_image(fill_color="black", back_color="white").convert("RGB").resize((px, px), 0)


def _label(w_mm, h_mm, lines, qr=None, dpi=300, pad_mm=2.5, rule=None):
    from PIL import Image, ImageDraw, ImageFont
    s = dpi / 25.4
    W, H = int(w_mm * s), int(h_mm * s)
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, W - 3, H - 3), radius=int(1.5 * s), outline=(150, 150, 150), width=3)
    qx = W
    if qr:
        q = _qr(qr, int(H - 2 * pad_mm * s))
        qx = W - q.size[0] - int(pad_mm * s)
        im.paste(q, (qx, int(pad_mm * s)))
    y = pad_mm * s
    for text, size_mm, bold, mono, colour in lines:
        f = ImageFont.truetype(FONT_M if mono else (FONT_B if bold else FONT), int(size_mm * s))
        while d.textlength(text, font=f) > qx - 2 * pad_mm * s and f.size > 8:
            f = ImageFont.truetype(f.path, f.size - 2)
        d.text((pad_mm * s, y), text, font=f, fill=colour)
        y += size_mm * s * 1.22
    if rule:
        d.line((pad_mm * s, rule * s, qx - pad_mm * s, rule * s), fill=(200, 200, 200), width=2)
    return im


def labels(rows: list[dict], path: Path) -> None:
    """Four kinds of label, at print size (300 dpi), on one sheet."""
    from PIL import Image, ImageDraw, ImageFont
    import naming as N
    r = {x["name"]: x for x in rows}
    ink, ink2 = (31, 35, 40), (75, 85, 99)
    say = {}
    tts = OUT / "tts_check.json"
    if tts.exists():
        for row in json.loads(tts.read_text()).get("rows", []):
            if row.get("fix") and row["fix"].get("say"):
                say[row["name"]] = row["fix"]["say"]
    st = r["lonsdale"]
    plate = _label(100, 38, [("Lonsdale", 11, True, False, ink),
                             ("XRD · Rigaku MiniFlex", 3.6, False, False, ink2),
                             (f"{st['asset']} · timp · tray D (Delta)", 3.4, False, True, ink2),
                             ("Kathleen Lonsdale, X-ray crystallographer", 3.0, False, False, ink2)],
                   qr=f"{st['asset']} lonsdale")
    bk = r["baekeland"]
    plate2 = _label(100, 38, [("Baekeland", 11, True, False, ink),
                              ("mounting press · LECO MX400", 3.6, False, False, ink2),
                              (f"{bk['asset']} · timp · tray F (Foxtrot)", 3.4, False, True, ink2),
                              (f"say “{say.get('baekeland', 'BAKE-land')}” · Leo Baekeland, Bakelite",
                               3.0, False, False, ink2)], qr=f"{bk['asset']} baekeland")
    tr = r["tray-d"]
    tray = _label(70, 30, [("D", 13, True, False, ink), ("DELTA · timp R1", 4.0, True, False, ink2),
                           (tr["asset"], 3.2, False, True, ink2)], qr=f"{tr['asset']} tray-d")
    rb = r["elsie"]
    robot = _label(100, 38, [("Elsie", 11, True, False, ink), ("MiR250 + UR12e, unit 1", 3.6, False, False, ink2),
                             (f"{rb['asset']} · elsie-base · elsie-arm", 3.4, False, True, ink2),
                             ("after Grey Walter's Elsie (1949)", 3.0, False, False, ink2)],
                   qr=f"{rb['asset']} elsie")
    tags = [_label(62, 12, [(n, 4.6, True, True, ink), (r[n]["asset"], 2.6, False, True, ink2)], qr=None, pad_mm=1.5)
            for n in ("tray-d-cam0", "tray-d-ups", "lonsdale-pc", "timp-bay-front")]
    gap = 50
    W = max(plate.width + robot.width, tray.width + plate2.width) + 3 * gap
    H = 150 + plate.height + plate2.height + sum(t.height for t in tags[:2]) + 6 * gap + 90
    sheet = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(FONT_B, 40)
    d.text((gap, 30), "Label mock-ups at print size (300 dpi): station and robot plates 100 x 38 mm,\n"
           "a tray end 70 x 30 mm, tags on 12 mm tape", font=f, fill=ink, spacing=8)
    y = 150
    sheet.paste(plate, (gap, y))
    sheet.paste(robot, (2 * gap + plate.width, y))
    y += plate.height + gap
    sheet.paste(plate2, (gap, y))
    sheet.paste(tray, (2 * gap + plate2.width, y))
    y += plate2.height + gap
    x = gap
    for i, t in enumerate(tags):
        sheet.paste(t, (x, y))
        x += t.width + gap
        if i == 1:
            x, y = gap, y + t.height + gap
    f2 = ImageFont.truetype(FONT, 30)
    d.text((gap, H - 100), f"The QR code holds the asset number and the name ('{st['asset']} lonsdale'): a phone "
           "shows it as text,\nand the arm's wrist camera can read it to confirm where it is.", font=f2, fill=ink2,
           spacing=6)
    sheet.save(path, optimize=True)


def all_figures(rows, res) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    floor(rows, OUT / "floor_names.png")
    trays(rows, OUT / "tray_names.png")
    labels(rows, OUT / "labels.png")
    print("figures:", ", ".join(p.name for p in sorted(OUT.glob("*.png"))))
