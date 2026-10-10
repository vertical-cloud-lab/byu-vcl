#!/usr/bin/env python3
"""Draw.io outline diagrams for the rePowder tutorials, with a highlight variant per step and PowerPoint-style builds.

Every tutorial opens on an outline of its major steps, built up step by step in sync with the narration: first the step
boxes alone, then each step's detail panel appearing in turn. The same outline comes back as a section divider with the
current step in full colour and a bold border, and the other steps dimmed. The words and numbers follow
../../sop.md (checked 2026-10-03); edit them in SPECS below.

    python make_diagrams.py                 # write the .drawio files from SPECS, then export every PNG
    python make_diagrams.py --export-only   # keep the .drawio files as they are (edited in diagrams.net), re-export
    python make_diagrams.py --no-export     # only write the .drawio files
    python make_diagrams.py 02-during       # just one diagram (and its variants)

The variants are made from the .drawio files on disk, by cell id: s<k>_... belongs to step (or tutorial lane) k, and
a<k> is the arrow after step k. Highlights: <name>_step<k>.png (<name>_tutorial<k>.png for the overview's lanes).
Builds: <name>_build0.png has every step box, arrow and title but no details; <name>_build<k>.png adds the details of
steps 1..k (s<k>_panel, or the overview captions s<k>_c<j>), so the last build is the whole diagram. Keep those ids
when editing in diagrams.net and the variants follow.
Needs draw.io desktop (`drawio` on PATH, or DRAWIO=/path/to/draw.io), Pillow, and xvfb-run when there is no display.
"""
import argparse, base64, html, os, re, shutil, signal, subprocess, sys, tempfile, time, urllib.parse, zlib
import xml.etree.ElementTree as ET
from PIL import Image, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 720                      # page = PNG size; the tutorials are 1280x720
SCALE = 2                             # export at 2x, then downsample with Pillow for smooth text
INK, ARROW = "#1F2937", "#4B5563"     # text and arrows wear neutral ink; colour carries the tutorial
THEMES = {                            # main fill (white bold text >= 4.3:1), dark stroke, light tint (ink >= 13:1)
    "before": dict(main="#00897B", dark="#00574B", tint="#E0F2F1"),   # teal
    "during": dict(main="#C2410C", dark="#7C2D12", tint="#FCEDE4"),   # burnt orange
    "after":  dict(main="#6D28D9", dark="#4C1D95", tint="#EFE9FC"),   # violet
}
DIM_SHAPE, DIM_TEXT, DIM_TITLE = 30, 45, 80   # opacity (%) of what is not highlighted: shapes, text, step names
NB = "\u00a0"                         # no-break space


def nb(s):
    """Keep a phrase on one line, not breaking it at a space or at a hyphen."""
    return '<span style="white-space:nowrap">' + s.replace(" ", NB) + "</span>"


def b(s):
    """A key number: bold and never broken, not even at its dash or hyphen."""
    return '<b style="white-space:nowrap">' + nb(s) + "</b>"


SPECS = {
    "00-overview": dict(
        kind="overview", title="Overview · One rePowder run, start to finish",
        lanes=[
            dict(theme="before", label="Tutorial 1 · Before a run", phases=[
                ("Utilities on", ["chilled water · compressed air " + b("~4 bar"),
                                  "argon 5N at " + b("8 bar") + " · vacuum pump oil"]),
                ("Prepare the machine", ["furnace: crucible, nut, insulation, thermocouple,",
                                         "sealing rod + lever, charge",
                                         "chamber: splash disc, container, catch bowl",
                                         "stack into the door, scan; " + nb("door bolted")]),
            ]),
            dict(theme="during", label="Tutorial 2 · During a run", phases=[
                ("Gas wash", ["furnace ×5, then chamber", "again at " + b("250 °C") + " and " + b("500 °C"),
                              "O₂ " + b("≤ 100 ppm") + ", best " + b("40–50")]),
                ("Melt", ["overshoot to drop the charge", "then " + b("780–800 °C"), "hold " + b("2 min") + ", no longer"]),
                ("Pour", ["vibration on", "→ draining pressure", "→ sealing rod up", "→ turbo as needed"]),
                ("End of pour", ["turbo, rod down,", "melting pressure,", "generator stop,", "ultrasonics stop"]),
            ]),
            dict(theme="after", label="Tutorial 3 · After a run", phases=[
                ("Cool down", ["open at " + b("≤ 400 °C") + ", vent first", "utilities off at " + b("~100 °C")]),
                ("Collect powder", ["close the container valve, sieve", "bag with a " + b("6-character") + " ID"]),
                ("Clean", ["by what runs next:", "same alloy, or alloy change"]),
            ]),
        ]),
    "01-before": dict(
        kind="steps", theme="before", title="Tutorial 1 · Before a run",
        steps=[
            ("Utilities", ["chilled water: facility valve " + nb("barely open"),
                           "compressed air " + b("~4 bar") + " (" + b("8 bar") + " supply)",
                           "argon 5N, " + nb("regulator at ") + b("8 bar"),
                           "vacuum pump oil between min and max"]),
            ("Furnace", ["lid open, " + nb("rod lever up"),
                         "nozzle " + b("0.5 / 0.7 mm") + ", white side up",
                         "crucible " + nb("just tight") + "; nut from below, " + nb("snug, never forced"),
                         "insulation, then thermocouple",
                         "sealing rod in, " + nb("lever down") + ", then the charge: " + b("≤ 20 mm") + ", "
                         + b("250–300 g"),
                         "lid latched, no hissing"]),
            ("Chamber", ["splash disc in the " + nb("container's flange"),
                         "container: flange " + nb("finger-tight") + " " + nb("(a 2nd person helps)"),
                         "catch bowl " + nb("through the door"),
                         "covers over " + nb("the openings")]),
            ("Ultrasonic stack", ["transducer → booster → sonotrode → plate",
                                  "torque " + b("65 / 60 / 50 N·m"),
                                  "scan: one wide peak, " + nb("a little over ") + b("40 kHz"),
                                  "wet test; transducer cover on",
                                  "door shut with " + nb("all ") + b("3") + nb(" bolts")]),
        ]),
    "02-during": dict(
        kind="steps", theme="during", title="Tutorial 2 · During a run",
        steps=[
            ("Gas wash", ["pressure control off before pumping",
                          "furnace " + b("×5") + " cycles, " + nb("then chamber"),
                          "again at " + b("250 °C") + " " + nb("and ") + b("500 °C"),
                          "O₂ read under gas: " + b("≤ 100 ppm") + ", best " + b("40–50")]),
            ("Heat & melt", ["melting pressure, pressure control on",
                             "setpoint " + b("850–1000 °C") + " drops the charge",
                             "at the melting cues: " + b("780–800 °C"),
                             "wait " + b("2 min") + ", no longer"]),
            ("Pour", ["transducer cooling on, rescan",
                      "amplitude " + b("~90"),
                      "vibration on<br>→ draining pressure<br>→ sealing rod up<br>→ turbo as needed",
                      "operator at the window, " + b("2–3 min")]),
            ("End of pour", ["turbo to clear " + nb("the nozzle"),
                             "sealing rod down",
                             "melting pressure",
                             "generator stop",
                             "ultrasonics stop",
                             "all " + b("within seconds")]),
        ]),
    "03-after": dict(
        kind="steps", theme="after", title="Tutorial 3 · After a run",
        steps=[
            ("Shutdown sequence", ["rod down, " + nb("melting pressure"),
                                   "generator and ultrasonics stopped",
                                   "setpoint " + b("250 °C") + " for " + nb("next time"),
                                   "transducer cooling off",
                                   "run log written " + nb("while fresh")]),
            ("Cool down & open", ["furnace " + b("≤ 400 °C"),
                                  "pressure control off, " + nb("vent first"),
                                  "respirator, gloves, coat; " + nb("then the ") + b("3") + nb(" clamps"),
                                  "utilities off at " + b("~100 °C")]),
            ("Collect powder", ["brush powder into " + nb("the container"),
                                "close the container valve, remove it",
                                "pour onto paper, " + nb("pick out chunks") + ", sieve",
                                "bag, " + b("6-character") + " ID label, photo"]),
            ("Clean & maintain", ["same alloy next: brush, light clean",
                                  "alloy change: vacuum, wipe all, " + b("~1 h"),
                                  "plates: one alloy " + nb("each, logged"),
                                  "slag and nozzle checked once cool",
                                  "HEPA filter every " + b("~2 months")]),
        ]),
}

# ---------------------------------------------------------------- text measurement (Helvetica = Liberation Sans here)
FONT_DIRS = ["/usr/share/fonts/truetype/liberation", "/usr/share/fonts/liberation", "/usr/share/fonts/truetype",
             os.path.expanduser("~/Library/Fonts"), "/Library/Fonts"]
_FONTS = {}


def _font(bold, size):
    key = (bold, size)
    if key not in _FONTS:
        name = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
        path = next((os.path.join(d, name) for d in FONT_DIRS if os.path.exists(os.path.join(d, name))), None)
        _FONTS[key] = ImageFont.truetype(path, size) if path else None
    return _FONTS[key]


def _runs(markup):
    """(bold, text) runs of one line of label markup; other tags are ignored."""
    return [(m.group(1) is not None, html.unescape(m.group(1) if m.group(1) is not None else m.group(2)))
            for m in re.finditer(r"<b[^>]*>(.*?)</b>|([^<]+)", re.sub(r"<(?!/?b\b)[^>]+>", "", markup))]


def text_width(markup, size):
    """Width in px of one line of markup; estimated if Liberation Sans is not installed."""
    total = 0.0
    for bold, run in _runs(markup):
        f = _font(bold, size)
        total += f.getlength(run) if f else len(run) * size * (0.58 if bold else 0.53)
    return total


def wrapped_lines(markup, size, width):
    """Lines the browser needs for markup in a column `width` px wide (wraps at spaces, <br> forces a break)."""
    lines = 0
    for seg in re.split(r"<br\s*/?>", markup):
        words, cur = [], []
        for bold, run in _runs(seg):
            for i, piece in enumerate(run.split(" ")):
                if i:
                    words.append(cur); cur = []
                cur.append((bold, piece))
        words.append(cur)
        space, x, n = text_width(" ", size), 0.0, 1
        for wd in words:
            ww = sum(text_width(f"<b>{t}</b>" if bo else t, size) for bo, t in wd)
            if x and x + space + ww > width:
                n += 1; x = ww
            else:
                x += (space if x else 0) + ww
        lines += n
    return lines


# ---------------------------------------------------------------- draw.io document
def style_str(d):
    return "".join(f"{k};" if v is None else f"{k}={v};" for k, v in d.items())


def style_dict(s):
    d = {}
    for tok in filter(None, (s or "").split(";")):
        k, eq, v = tok.partition("=")
        d[k] = v if eq else None
    return d


class Doc:
    def __init__(self, name):
        self.mxfile = ET.Element("mxfile", host="make_diagrams.py", type="device")
        dia = ET.SubElement(self.mxfile, "diagram", id=re.sub(r"\W", "", name)[:20] or "d", name=name)
        self.model = ET.SubElement(dia, "mxGraphModel", dx=str(W), dy=str(H), grid="0", gridSize="10", guides="1",
                                   tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1",
                                   pageWidth=str(W), pageHeight=str(H), background="#FFFFFF", math="0", shadow="0")
        self.root = ET.SubElement(self.model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        # a locked background layer with a full-page white rectangle, so the export is exactly the 16:9 page
        ET.SubElement(self.root, "mxCell", id="bg_layer", value="Background (locked)", style="locked=1;", parent="0")
        self.vertex("bg", "", dict(rounded=0, html=1, fillColor="#FFFFFF", strokeColor="none"), 0, 0, W, H,
                    parent="bg_layer")
        ET.SubElement(self.root, "mxCell", id="1", value="Outline", parent="0")

    def vertex(self, id_, value, style, x, y, w, h, parent="1"):
        c = ET.SubElement(self.root, "mxCell", id=id_, value=value, style=style_str(style), vertex="1", parent=parent)
        ET.SubElement(c, "mxGeometry", x=f"{x:g}", y=f"{y:g}", width=f"{w:g}", height=f"{h:g}", **{"as": "geometry"})

    def edge(self, id_, src, tgt, style, parent="1"):
        c = ET.SubElement(self.root, "mxCell", id=id_, value="", style=style_str(style), edge="1", parent=parent,
                          source=src, target=tgt)
        ET.SubElement(c, "mxGeometry", relative="1", **{"as": "geometry"})

    def write(self, path):
        ET.indent(self.mxfile, space="  ")
        ET.ElementTree(self.mxfile).write(path, encoding="utf-8", xml_declaration=False)


def title_cell(doc, text, size, y, h):
    doc.vertex("title", html.escape(text), dict(text=None, html=1, whiteSpace="wrap", align="center",
                                                verticalAlign="middle", fontSize=size, fontStyle=1, fontColor=INK,
                                                strokeColor="none", fillColor="none"), 40, y, W - 80, h)


def arrow_style():
    return dict(edgeStyle="none", html=1, endArrow="block", endFill=1, endSize=5, strokeWidth=4, strokeColor=ARROW,
                exitX=1, exitY=0.5, exitDx=0, exitDy=0, entryX=0, entryY=0.5, entryDx=0, entryDy=0)


# ---- step outlines (tutorials 1-3): four columns, a filled step box with its detail panel under it.
# One geometry for all three, so cutting from one tutorial's outline to the next does not jump.
S_MARGIN, S_GAP = 30, 38
S_COL = (W - 2 * S_MARGIN - 3 * S_GAP) / 4
S_TITLE_Y, S_TITLE_H, S_TITLE_PX = 22, 60, 42
S_BOX_H, S_BOX_PAD, S_PANEL_GAP = 104, 6, 16
S_TEXT_PX, S_LINE, S_ITEM_GAP = 22, 1.2, 12
S_PAD_X, S_PAD_Y, S_INDENT = 10, 14, 22


def panel_height(items):
    width = S_COL - 2 * S_PAD_X - 4 - S_INDENT          # draw.io adds 2 px spacing each side; then the list indent
    lines = sum(wrapped_lines(it, S_TEXT_PX, width) for it in items)
    return lines * S_TEXT_PX * S_LINE + (len(items) - 1) * S_ITEM_GAP + 2 * S_PAD_Y + 12


def step_specs():
    return [s for s in SPECS.values() if s["kind"] == "steps"]


def step_geometry():
    ph = max(panel_height(items) for s in step_specs() for _, items in s["steps"])
    top, bottom = S_TITLE_Y + S_TITLE_H + 20, H - 20
    y0 = top + max(0, (bottom - top - (S_BOX_H + S_PANEL_GAP + ph)) / 2)
    return y0, ph


def name_size(names, start=28, smallest=22):
    """Largest step-name size (px) at which every name fits on one line of its box."""
    room = S_COL - 2 * S_BOX_PAD - 4 - 10
    for size in range(start, smallest - 1, -1):
        if all(text_width(f"<b>{n}</b>", size) <= room for n in names):
            return size
    return smallest


def build_steps(name, spec):
    t = THEMES[spec["theme"]]
    doc = Doc(spec["title"])
    title_cell(doc, spec["title"], S_TITLE_PX, S_TITLE_Y, S_TITLE_H)
    y0, ph = step_geometry()
    size = name_size([n for n, _ in spec["steps"]])
    for k, (step, items) in enumerate(spec["steps"], 1):
        x = S_MARGIN + (k - 1) * (S_COL + S_GAP)
        label = f'<span style="font-size:20px;font-weight:normal">Step {k}</span><br>{html.escape(step)}'
        doc.vertex(f"s{k}_box", label, dict(rounded=1, arcSize=10, whiteSpace="wrap", html=1, fontSize=size,
                                            fontStyle=1, fillColor=t["main"], strokeColor=t["dark"], strokeWidth=2,
                                            fontColor="#FFFFFF", spacing=S_BOX_PAD), x, y0, S_COL, S_BOX_H)
        lis = "".join(f'<li style="margin-bottom:{S_ITEM_GAP if i < len(items) - 1 else 0}px">{it}</li>'
                      for i, it in enumerate(items))
        doc.vertex(f"s{k}_panel", f'<ul style="margin:0;padding-left:{S_INDENT}px">{lis}</ul>',
                   dict(rounded=1, arcSize=5, whiteSpace="wrap", html=1, fontSize=S_TEXT_PX, align="left",
                        verticalAlign="top", spacingLeft=S_PAD_X, spacingRight=S_PAD_X, spacingTop=S_PAD_Y,
                        fillColor=t["tint"], strokeColor=t["main"], strokeWidth=1, fontColor=INK),
                   x, y0 + S_BOX_H + S_PANEL_GAP, S_COL, ph)
    for k in range(1, len(spec["steps"])):
        doc.edge(f"a{k}", f"s{k}_box", f"s{k + 1}_box", arrow_style())
    return doc


# ---- overview (tutorial 0): one swimlane per tutorial, one numbered box per phase, key numbers under each box
O_MARGIN, O_TITLE_Y, O_TITLE_H, O_TOP, O_LANE_GAP, O_FOOT = 24, 12, 52, 72, 12, 14
O_HEAD, O_IN_X, O_IN_TOP, O_BOX_H, O_GAP = 38, 18, 12, 50, 44
O_CAP_PX, O_CAP_LINE, O_CAP_GAP, O_BOTTOM = 20, 1.2, 6, 10


def build_overview(name, spec):
    doc = Doc(spec["title"])
    title_cell(doc, spec["title"], 36, O_TITLE_Y, O_TITLE_H)
    lane_w = W - 2 * O_MARGIN
    heights = [O_HEAD + O_IN_TOP + O_BOX_H + O_CAP_GAP + O_BOTTOM
               + max(len(c) for _, c in lane["phases"]) * O_CAP_PX * O_CAP_LINE for lane in spec["lanes"]]
    spare = H - O_FOOT - O_TOP - sum(heights) - O_LANE_GAP * (len(heights) - 1)
    if spare < 0:
        print(f"  ! {name}: lanes are {-spare:.0f} px too tall for the page", file=sys.stderr)
    heights = [h + spare / len(heights) for h in heights]          # share the spare height between the lanes
    y, n = O_TOP, 0
    for li, (lane, lh) in enumerate(zip(spec["lanes"], heights), 1):
        t, lid = THEMES[lane["theme"]], f"s{li}_lane"
        doc.vertex(lid, html.escape(lane["label"]),
                   {"swimlane": None, "startSize": O_HEAD, "horizontal": 1, "rounded": 1, "arcSize": 8, "html": 1,
                    "whiteSpace": "wrap", "fontSize": 22, "fontStyle": 1, "fontColor": "#FFFFFF", "align": "left",
                    "spacingLeft": 14, "fillColor": t["main"], "swimlaneFillColor": t["tint"],
                    "strokeColor": t["main"], "strokeWidth": 2, "collapsible": 0, "swimlaneLine": 0},
                   O_MARGIN, y, lane_w, lh)
        m = len(lane["phases"])
        bw = (lane_w - 2 * O_IN_X - (m - 1) * O_GAP) / m
        cap_y = O_HEAD + O_IN_TOP + O_BOX_H + O_CAP_GAP
        for j, (phase, cap) in enumerate(lane["phases"], 1):
            n += 1
            bx = O_IN_X + (j - 1) * (bw + O_GAP)
            doc.vertex(f"s{li}_b{j}", f"{n} · {html.escape(phase)}",
                       dict(rounded=1, arcSize=14, whiteSpace="wrap", html=1, fontSize=24, fontStyle=1,
                            fillColor="#FFFFFF", strokeColor=t["main"], strokeWidth=3, fontColor=INK),
                       bx, O_HEAD + O_IN_TOP, bw, O_BOX_H, parent=lid)
            doc.vertex(f"s{li}_c{j}", "<br>".join(cap),
                       dict(text=None, html=1, whiteSpace="wrap", align="center", verticalAlign="top",
                            fontSize=O_CAP_PX, fontColor=INK, strokeColor="none", fillColor="none", spacing=0),
                       bx, cap_y, bw, lh - cap_y - O_BOTTOM, parent=lid)
            for line in cap:                                          # the explicit lines must fit the box width
                if text_width(line, O_CAP_PX) > bw - 6:
                    print(f"  ! {name}: caption line too wide ({text_width(line, O_CAP_PX):.0f} > {bw - 6:.0f} px):"
                          f" {line}", file=sys.stderr)
        for j in range(1, m):
            doc.edge(f"s{li}_a{j}", f"s{li}_b{j}", f"s{li}_b{j + 1}", arrow_style(), parent=lid)
        y += lh + O_LANE_GAP
    return doc


# ---------------------------------------------------------------- highlight variants (work on any .drawio, by id)
def read_model(path):
    tree = ET.parse(path)
    for dia in tree.getroot().iter("diagram"):
        if dia.find("mxGraphModel") is None and (dia.text or "").strip():    # a compressed save from diagrams.net
            raw = zlib.decompress(base64.b64decode(dia.text.strip()), -15).decode("utf-8")
            dia.text = None
            dia.append(ET.fromstring(urllib.parse.unquote(raw)))
    return tree


def groups(tree):
    return sorted({int(m.group(1)) for c in tree.iter("mxCell") for m in [re.match(r"s(\d+)_", c.get("id", ""))] if m})


def highlight(tree, k):
    """Step (or lane) k keeps its colour and gets a bold border; everything else numbered is dimmed."""
    for c in tree.iter("mxCell"):
        cid = c.get("id", "")
        m = re.match(r"s(\d+)_(\w+)", cid)
        st = style_dict(c.get("style"))
        if m and int(m.group(1)) == k:
            part = m.group(2)
            if part in ("box", "lane"):
                st.update(strokeWidth="7" if part == "box" else "6", shadow="1")
            elif part == "panel" or re.fullmatch(r"b\d+", part):
                st["strokeWidth"] = "4"
            else:
                continue
        elif m or re.fullmatch(r"a\d+", cid):
            st.update(opacity=str(DIM_SHAPE), textOpacity=str(DIM_TEXT))
            if m and m.group(2) in ("box", "lane") and st.get("fontColor", "").upper() == "#FFFFFF":
                # white names would vanish on a dimmed fill: write them in the step's dark shade instead
                st.update(fontColor=st.get("strokeColor") or INK, textOpacity=str(DIM_TITLE))
        else:
            continue
        c.set("style", style_str(st))
    return tree


# ---------------------------------------------------------------- builds (work on any .drawio, by id)
DETAIL = re.compile(r"s(\d+)_(panel|c\d+)$")     # what a build reveals: a step's panel, or an overview lane's captions


def cell_ref(el):
    """(id, parent, source, target) of a cell, bare <mxCell> or wrapped in the <object>/<UserObject> that diagrams.net
    uses for cells carrying custom data."""
    inner = el if el.tag == "mxCell" else el.find("mxCell")
    get = (lambda key: inner.get(key)) if inner is not None else (lambda key: None)
    return el.get("id", ""), get("parent"), get("source"), get("target")


def build_stage(tree, k):
    """Stage k of a PowerPoint-style build: the whole diagram minus the details of the steps (lanes) after k. Stage 0
    is the step boxes, arrows and title alone; the last stage is the full diagram."""
    for root in tree.iter("root"):
        cells = list(root)
        refs = [cell_ref(el) for el in cells]
        drop = {cid for cid, *_ in refs if (m := DETAIL.match(cid)) and int(m.group(1)) > k}
        grew = bool(drop)
        while grew:                     # anything hanging off a dropped cell (children, connected edges) goes too
            grew = False
            for cid, parent, src, tgt in refs:
                if cid not in drop and drop & {parent, src, tgt}:
                    drop.add(cid); grew = True
        for el, (cid, *_) in zip(cells, refs):
            if cid in drop:
                root.remove(el)
    return tree


# ---------------------------------------------------------------- export
def drawio_cmd():
    exe = os.environ.get("DRAWIO") or shutil.which("drawio") or shutil.which("draw.io")
    if not exe:
        sys.exit("draw.io desktop not found: install it (see README.md) or set DRAWIO=/path/to/drawio")
    cmd = [exe, "--no-sandbox", "--disable-gpu"]
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY") and shutil.which("xvfb-run"):
        cmd = ["xvfb-run", "-a"] + cmd
    return cmd


STALL = 60                            # s without a new PNG before a draw.io launch counts as hung


def run_drawio(src, out, log):
    """One draw.io launch exporting every .drawio in `src` to `out`. On a busy machine draw.io (31.x) sometimes fails a
    page capture (UnknownVizError, an unhandled promise rejection) and then waits forever, so the launch is stopped, with
    its X server and helpers, on that error or once no new PNG has appeared for STALL seconds. The caller retries."""
    start = os.path.getsize(log) if os.path.exists(log) else 0
    with open(log, "a") as f:
        p = subprocess.Popen(drawio_cmd() + ["-x", "-f", "png", "-s", str(SCALE), "-b", "0", "-o", out, src],
                             stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
        seen, last = -1, time.time()
        while p.poll() is None:
            time.sleep(1)
            n = len(os.listdir(out))
            if n != seen:
                seen, last = n, time.time()
            with open(log, errors="replace") as g:
                g.seek(start)
                failed = "UnhandledPromiseRejection" in g.read()
            if failed or time.time() - last > STALL:
                os.killpg(p.pid, signal.SIGKILL); p.wait()
                print(f"  ! draw.io {'failed a page capture' if failed else 'stalled'} with {n} PNGs exported;"
                      " restarting it for the rest", file=sys.stderr)


def png_ok(path):
    try:
        with Image.open(path) as im:
            im.load()
        return True
    except (OSError, SyntaxError):
        return False


def export_all(jobs):
    """jobs: (drawio_path, png_path) pairs. One draw.io launch exports the whole batch (a hung launch is restarted for
    whatever it had not exported yet); Pillow makes each PNG exactly 1280x720."""
    with tempfile.TemporaryDirectory() as tmp:
        out, log = os.path.join(tmp, "out"), os.path.join(tmp, "drawio.log")
        os.makedirs(out)
        todo = list(range(len(jobs)))
        for attempt in range(6):
            src = os.path.join(tmp, f"src{attempt}")
            os.makedirs(src)
            for i in todo:
                shutil.copy(jobs[i][0], os.path.join(src, f"{i:03d}.drawio"))
            run_drawio(src, out, log)
            todo = [i for i in todo if not png_ok(os.path.join(out, f"{i:03d}.png"))]
            if not todo:
                break
        for i, (_, png) in enumerate(jobs):
            raw = os.path.join(out, f"{i:03d}.png")
            if i in todo:
                sys.exit(f"export failed for {png}:\n{open(log, errors='replace').read()[-3000:]}")
            im = Image.open(raw).convert("RGB")
            w, h = im.size
            if abs(w - SCALE * W) > 4 or abs(h - SCALE * H) > 4:      # something sticks out of the page
                print(f"  ! {os.path.basename(png)}: export was {w}x{h}, expected ~{SCALE * W}x{SCALE * H};"
                      " keep every shape inside the page", file=sys.stderr)
            left, top = (w - SCALE * W) // 2, (h - SCALE * H) // 2       # the export adds a pixel of border
            if left >= 0 and top >= 0:
                im = im.crop((left, top, left + SCALE * W, top + SCALE * H))
            im.resize((W, H), Image.LANCZOS).save(png, optimize=True)
            print(f"  {os.path.basename(png)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("names", nargs="*", help=f"diagrams to make (default all: {', '.join(SPECS)})")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--export-only", action="store_true", help="re-export PNGs from the .drawio files as they are")
    g.add_argument("--no-export", action="store_true", help="write the .drawio files only")
    a = ap.parse_args()
    names = a.names or list(SPECS)
    for name in names:
        if name not in SPECS:
            sys.exit(f"unknown diagram {name!r}; choose from {', '.join(SPECS)}")
    if not a.export_only:
        for name in names:
            spec = SPECS[name]
            (build_overview if spec["kind"] == "overview" else build_steps)(name, spec).write(
                os.path.join(HERE, f"{name}.drawio"))
            print(f"  {name}.drawio")
    if a.no_export:
        return
    with tempfile.TemporaryDirectory() as tmp:
        jobs = []
        for name in names:
            path = os.path.join(HERE, f"{name}.drawio")
            jobs.append((path, os.path.join(HERE, f"{name}.png")))
            tree = read_model(path)
            kind = "tutorial" if any(c.get("id", "").endswith("_lane") for c in tree.iter("mxCell")) else "step"
            for k in groups(tree):
                var = os.path.join(tmp, f"{name}_{kind}{k}.drawio")
                highlight(read_model(path), k).write(var, encoding="utf-8")
                jobs.append((var, os.path.join(HERE, f"{name}_{kind}{k}.png")))
            for k in [0] + groups(tree):         # build stages; the last one is the full diagram again
                var = os.path.join(tmp, f"{name}_build{k}.drawio")
                build_stage(read_model(path), k).write(var, encoding="utf-8")
                jobs.append((var, os.path.join(HERE, f"{name}_build{k}.png")))
        export_all(jobs)


if __name__ == "__main__":
    main()
