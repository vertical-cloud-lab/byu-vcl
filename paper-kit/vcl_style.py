"""House figure style for Vertical Cloud Lab papers and talks.

    import vcl_style as vs

    vs.use("paper")                         # or vs.use("slide")
    df = vs.read_csv("salt_doses.csv")      # from data/ only, and only with a README
    fig, ax = vs.figure("single", height_mm=60)
    ...
    vs.save(fig)                            # figures/out/<script name>.pdf and .png
    vs.caption(what=..., n=..., error_bars=..., data="salt_doses.csv")

Two presets.

``paper``
    A figure is drawn at the size it is printed and is never scaled: 85 mm
    wide for one column, 175 mm for two.  No text is smaller than 7 pt and
    every line is 0.6 pt (thicker for emphasis is allowed, thinner is not).
    Colours come from the Okabe-Ito palette.  There are no titles, because
    the caption carries the message, and axis labels read "Quantity (unit)".
    save() writes a vector PDF and a 600 dpi PNG, and refuses a figure that
    breaks these rules, so a figure that builds is one that meets them.

``slide``
    The look of the powder-doser optimization slides (vertical-cloud-lab/
    powder-doser, docs/optimization/slides/slide_style.py on branch
    claude/opt-results-slides-20261005).  Every slide is drawn on a
    13.333 x 7.5 in canvas, the size of a 16:9 PowerPoint slide, so a
    matplotlib point is a PowerPoint point when the PNG fills the slide.  The
    smallest text anywhere is 24 pt.  The message sits at the same spot, top
    left, on every slide; graphs have no titles, horizontal two-line y labels
    above the axis, no grid, and faded same-colour callout lines (no
    arrowheads) instead of legends.  The slide helpers keep the powder-doser
    names, so ``import vcl_style as ss; ss.use("slide")`` stands in for
    ``import slide_style as ss``.

Set VCL_STRICT_DATA=1 (``make figures`` does) and a figure script that opens a
data file from anywhere but data/ stops with an error.
"""
from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from cycler import cycler  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.text import Text  # noqa: E402
from matplotlib.transforms import ScaledTranslation  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parent        # the paper folder
DATA = ROOT / "data"                          # the only place figures read from
OUT = ROOT / "figures" / "out"                # the only place figures write to

PRESET: str | None = None                     # set by use()

# --------------------------------------------------------------------------- #
# paper
# --------------------------------------------------------------------------- #
MM = 1 / 25.4                                 # inches per millimetre
WIDTHS_MM = {"single": 85.0, "double": 175.0}
MAX_HEIGHT_MM = 225.0                         # leaves room for a caption on every target's page
MIN_TEXT_PT = 7.0
LINE_PT = 0.6
DPI_PNG = 600

# Okabe and Ito, "Color Universal Design" (2008), https://jfly.uni-koeln.de/color/
OKABE_ITO = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "reddish_purple": "#CC79A7",
}
# Strongest on white first; yellow last, as it is faint on white.
CYCLE = [OKABE_ITO[k] for k in ("blue", "orange", "bluish_green", "vermillion",
                                 "reddish_purple", "sky_blue", "black", "yellow")]
CONTEXT = "#8c8c8c"                           # grey for context marks, not a series

# A figure's file name: fig1_slug, fig2b_slug, figS1_slug (supplementary)
FIG_NAME = re.compile(r"^fig(S?\d+[a-z]?)_[a-z0-9]+(?:_[a-z0-9]+)*$")
UNIT_LABEL = re.compile(r"\s\(.+\)\s*$")     # "Quantity (unit)"

# --------------------------------------------------------------------------- #
# slide (powder-doser)
# --------------------------------------------------------------------------- #
FIG_IN = (13.3334, 7.5)    # 1920 x 1080 at 144 dpi (13.3333 rounds down to 1919)
DPI_SCREEN = 144           # 1920 x 1080
DPI_PRINT = 300            # 4000 x 2250, for the stills

INK = "#0b0b0b"
INK2 = "#52514e"
GREY = "#83827d"           # de-emphasised marks and labels
LEADER = "#8d8c88"
FAINT = "#c9c7c1"          # earlier steps, pushed back
GHOST = "#e4e2dc"
BLUE = "#2a78d6"           # the optimizer's results
BLUE_LIGHT = "#cde2fb"
ORANGE = "#eb6834"         # hand tuning
ORANGE_LIGHT = "#fbd9c9"

FS = 24                    # floor for every piece of text on a slide
FS_TITLE = 32
TITLE_XY = (0.045, 0.935)

# Sizes the shared helpers (style_axes, ylabel_top, callout) use, per preset.
_GEOM = {
    "paper": dict(spine_out=3.0, tick_pad=2.0, label_y=1.04, callout_lw=LINE_PT,
                  callout_alpha=0.6, shrink=(2, 2)),
    "slide": dict(spine_out=14.0, tick_pad=6.0, label_y=1.045, callout_lw=1.8,
                  callout_alpha=0.45, shrink=(6, 7)),
}


def _first_font(names):
    have = {f.name for f in font_manager.fontManager.ttflist}
    return next((n for n in names if n in have), "DejaVu Sans")


def _paper_rc(text_pt: float) -> dict:
    lw = LINE_PT
    return {
        # Arial or Helvetica where installed; Liberation Sans and Arimo have
        # Arial's metrics.  pdf.fonttype 42 embeds TrueType, so text stays text.
        "font.family": "sans-serif",
        "font.sans-serif": [_first_font(["Arial", "Helvetica", "Liberation Sans", "Arimo",
                                         "DejaVu Sans"])],
        "mathtext.default": "regular",
        "font.size": text_pt,
        "axes.labelsize": text_pt + 1,
        "axes.titlesize": text_pt + 1,
        "figure.titlesize": text_pt + 1,
        "xtick.labelsize": text_pt,
        "ytick.labelsize": text_pt,
        "legend.fontsize": text_pt,
        "legend.title_fontsize": text_pt,
        "axes.linewidth": lw,
        "grid.linewidth": lw,
        "lines.linewidth": lw,
        "lines.markersize": 3.0,
        "lines.markeredgewidth": lw,
        "patch.linewidth": lw,
        "hatch.linewidth": lw,
        "boxplot.boxprops.linewidth": lw,
        "boxplot.whiskerprops.linewidth": lw,
        "boxplot.capprops.linewidth": lw,
        "boxplot.medianprops.linewidth": lw,
        "boxplot.flierprops.linewidth": lw,
        "errorbar.capsize": 1.5,
        "xtick.major.width": lw,
        "ytick.major.width": lw,
        "xtick.minor.width": lw,
        "ytick.minor.width": lw,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "xtick.minor.size": 1.5,
        "ytick.minor.size": 1.5,
        "xtick.major.pad": 2.0,
        "ytick.major.pad": 2.0,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "axes.labelpad": 2.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "axes.prop_cycle": cycler(color=CYCLE),
        "axes.edgecolor": "black",
        "axes.labelcolor": "black",
        "text.color": "black",
        "xtick.color": "black",
        "ytick.color": "black",
        "legend.frameon": False,
        "legend.handlelength": 1.5,
        "legend.borderaxespad": 0.3,
        "image.cmap": "viridis",              # perceptually uniform and colourblind-safe
        "figure.dpi": 150,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.dpi": DPI_PNG,
        "savefig.bbox": "standard",           # never "tight": it changes the printed size
        "figure.constrained_layout.use": True,
        "figure.constrained_layout.h_pad": 2 / 72,
        "figure.constrained_layout.w_pad": 2 / 72,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }


_SLIDE_RC = {
    "font.family": ["Lato", "DejaVu Sans"],
    "font.size": FS,
    "axes.labelsize": FS,
    "xtick.labelsize": FS,
    "ytick.labelsize": FS,
    "axes.edgecolor": INK2,
    "axes.labelcolor": INK,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "xtick.labelcolor": INK,
    "ytick.labelcolor": INK,
    "axes.linewidth": 1.4,
    "xtick.major.width": 1.4,
    "ytick.major.width": 1.4,
    "xtick.major.size": 7,
    "ytick.major.size": 7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "lines.solid_capstyle": "round",
    "pdf.fonttype": 42,
}


def use(preset: str = "paper", *, text_pt: float = MIN_TEXT_PT) -> None:
    """Switch every later figure to a preset: "paper" or "slide".

    text_pt raises the paper text size for a journal that asks for more than
    7 pt (labels are always 1 pt larger than tick labels).
    """
    global PRESET
    plt.rcdefaults()
    if preset == "paper":
        if text_pt < MIN_TEXT_PT:
            raise ValueError(f"text_pt {text_pt} is under the {MIN_TEXT_PT:g} pt floor")
        plt.rcParams.update(_paper_rc(text_pt))
    elif preset == "slide":
        for f in font_manager.findSystemFonts():
            if "Lato" in f:
                font_manager.fontManager.addfont(f)
        plt.rcParams.update(_SLIDE_RC)
    else:
        raise ValueError(f"unknown preset {preset!r}: use 'paper' or 'slide'")
    PRESET = preset
    if os.environ.get("VCL_STRICT_DATA"):
        _guard_data_reads()


def _need(preset: str) -> None:
    if PRESET != preset:
        raise RuntimeError(f"call vcl_style.use({preset!r}) first (current preset: {PRESET})")


# --------------------------------------------------------------------------- #
# data/: the only input
# --------------------------------------------------------------------------- #
README_FIELD = re.compile(r"(?im)^\s*(?:[-*]\s*\*\*|#+\s*)(units|n|provenance)\b")
_DATA_SUFFIXES = {".csv", ".tsv", ".txt", ".dat", ".json", ".jsonl", ".xlsx", ".xls",
                  ".parquet", ".feather", ".npy", ".npz", ".h5", ".hdf5", ".mat", ".pkl",
                  ".pickle"}
_guard_on = False


def readme_for(path: Path) -> Path:
    """data/foo.csv is described by data/foo.README.md."""
    return path.with_name(path.stem + ".README.md")


def readme_problems(readme: Path) -> list[str]:
    """The fields a data README must state that it does not."""
    if not readme.exists():
        return [f"no {readme.name}"]
    text = readme.read_text(encoding="utf-8")
    found = {m.lower() for m in README_FIELD.findall(text)}
    missing = [f"{readme.name} does not state {f}" for f in ("units", "n", "provenance")
               if f not in found]
    return missing + ([f"{readme.name} still has FILL lines"] if "FILL" in text else [])


def data_path(name: str) -> Path:
    """The path of data/<name>, after checking it is inside data/ and has a
    README that states units, n and provenance."""
    p = (DATA / name).resolve()
    if DATA.resolve() not in p.parents:
        raise ValueError(f"{name}: figures read only from data/")
    if not p.exists():
        raise FileNotFoundError(f"data/{name} does not exist")
    problems = readme_problems(readme_for(p))
    if problems:
        raise FileNotFoundError(
            f"data/{name}: " + "; ".join(problems)
            + " (see data/README.md for what a data README states)")
    return p


def read_csv(name: str, **kwargs):
    """pandas.read_csv on data/<name>, which must have its README."""
    import pandas as pd
    return pd.read_csv(data_path(name), **kwargs)


def _guard_data_reads() -> None:
    """Refuse, for the rest of this process, to open a data file for reading
    from anywhere but data/ (fonts, styles and code are not data files)."""
    global _guard_on
    if _guard_on:
        return
    data = str(DATA.resolve())
    allowed = (data, str(Path(sys.prefix).resolve()), str(Path(sys.base_prefix).resolve()))

    def hook(event, args):
        if event != "open" or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        mode = args[1] if len(args) > 1 and isinstance(args[1], str) else "r"
        if any(c in mode for c in "wax+"):
            return
        path = os.path.abspath(os.fsdecode(args[0]))
        if Path(path).suffix.lower() in _DATA_SUFFIXES and not path.startswith(allowed):
            raise PermissionError(f"{path}: figure scripts read data only from {data}")

    sys.addaudithook(hook)
    _guard_on = True


# --------------------------------------------------------------------------- #
# paper figures
# --------------------------------------------------------------------------- #
def figure(width="single", height_mm: float | None = None, nrows: int = 1, ncols: int = 1,
           **subplots_kw):
    """A figure at its printed size, with its axes.

    width is "single" (85 mm), "double" (175 mm) or a number of millimetres
    (save() accepts only the two); height_mm defaults to 0.7 of the width for
    one column and 0.4 for two.
    """
    _need("paper")
    w = WIDTHS_MM[width] if isinstance(width, str) else float(width)
    h = height_mm if height_mm is not None else w * (0.7 if w < 120 else 0.4)
    return plt.subplots(nrows, ncols, figsize=(w * MM, h * MM), **subplots_kw)


def qty(name: str, unit: str | None = None) -> str:
    """An axis label in the house form: qty("Time", "s") -> "Time (s)"."""
    return f"{name} ({unit})" if unit else name


def panel_label(ax, letter: str, dx_pt: float = 24.0, dy_pt: float = 3.0, fmt: str = "{}"):
    """A bold panel letter above the axes' top-left corner, dx_pt to the left
    of the y axis (enough to clear tick labels and the y label).  fmt="({})"
    gives "(a)" for journals that want parentheses."""
    tr = ax.transAxes + ScaledTranslation(-dx_pt / 72, dy_pt / 72, ax.figure.dpi_scale_trans)
    return ax.text(0, 1, fmt.format(letter), transform=tr, ha="left", va="bottom",
                   fontweight="bold", fontsize=plt.rcParams["axes.labelsize"])


def check(fig) -> tuple[list[str], list[str]]:
    """(errors, warnings) for a paper figure: errors break the house rules;
    warnings are things to look at (an axis label without a unit)."""
    errors, warns = [], []
    w_mm, h_mm = (fig.get_size_inches() / MM).tolist()
    if not any(abs(w_mm - v) < 0.5 for v in WIDTHS_MM.values()):
        errors.append(f"figure is {w_mm:.1f} mm wide: make it 85 mm (one column) or "
                      "175 mm (two), and draw it at that size")
    if h_mm > MAX_HEIGHT_MM:
        errors.append(f"figure is {h_mm:.0f} mm tall: keep it under {MAX_HEIGHT_MM:.0f} mm")
    if getattr(fig, "_suptitle", None) is not None and fig._suptitle.get_text().strip():
        errors.append(f"figure title {fig._suptitle.get_text()!r}: the caption carries the message")
    fig.canvas.draw()                         # tick labels exist only after a draw
    for ax in fig.axes:
        for loc in ("left", "center", "right"):
            if ax.get_title(loc=loc).strip():
                errors.append(f"axes title {ax.get_title(loc=loc)!r}: no titles in a paper figure")
        for which, lab in (("x", ax.get_xlabel()), ("y", ax.get_ylabel())):
            if lab.strip() and not UNIT_LABEL.search(lab):
                warns.append(f"{which} label {lab!r} has no unit: write 'Quantity (unit)'; "
                             "a dimensionless quantity takes (%) or (1)")
        for spine in ax.spines.values():
            if spine.get_visible() and 0 < spine.get_linewidth() < LINE_PT - 1e-6:
                errors.append(f"axis line {spine.get_linewidth():g} pt: lines are at least {LINE_PT} pt")
        for axis in (ax.xaxis, ax.yaxis):
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                mew = tick.tick1line.get_markeredgewidth()
                if tick.tick1line.get_visible() and 0 < mew < LINE_PT - 1e-6:
                    errors.append(f"tick width {mew:g} pt: lines are at least {LINE_PT} pt")
                    break
    seen = set()
    for t in fig.findobj(Text):
        s = t.get_text().strip()
        if t.get_visible() and s and t.get_fontsize() < MIN_TEXT_PT - 1e-6 and s not in seen:
            seen.add(s)
            errors.append(f"text {s!r} is {t.get_fontsize():g} pt: the minimum is {MIN_TEXT_PT:g} pt")
    for ln in fig.findobj(Line2D):
        drawn = ln.get_visible() and ln.get_linestyle() not in ("None", "none", "", " ")
        if drawn and 0 < ln.get_linewidth() < LINE_PT - 1e-6:
            errors.append(f"line {ln.get_label()!r} is {ln.get_linewidth():g} pt: lines are at "
                          f"least {LINE_PT} pt")
    for coll in fig.findobj(LineCollection):
        lws = np.atleast_1d(coll.get_linewidths())
        if coll.get_visible() and np.any((lws > 0) & (lws < LINE_PT - 1e-6)):
            errors.append(f"line collection {coll.get_label()!r} has lines under {LINE_PT} pt")
    return sorted(set(errors), key=errors.index), warns


def _script_slug() -> str:
    main = sys.modules.get("__main__")
    return Path(getattr(main, "__file__", "") or sys.argv[0]).stem


def save(fig, path=None, dpi=None, *, strict: bool = True):
    """paper: check the figure, then write figures/out/<slug>.pdf (vector) and
    <slug>.png (600 dpi); the slug defaults to the script's name (figN_slug).
    With strict=False rule breaks are reported instead of raised.

    slide: as in powder-doser, write a PNG to path at dpi (default 144)."""
    if PRESET == "slide":
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=dpi or DPI_SCREEN)
        return path
    _need("paper")
    slug = str(path) if path is not None else _script_slug()
    if not FIG_NAME.match(slug):
        raise ValueError(f"{slug!r}: name figures figN_slug (fig1_dose_error, figS2_setup)")
    errors, warns = check(fig)
    for w in warns:
        warnings.warn(f"{slug}: {w}", stacklevel=2)
    if errors:
        msg = f"{slug} breaks the paper rules:\n  - " + "\n  - ".join(errors)
        if strict:
            raise ValueError(msg)
        warnings.warn(msg, stacklevel=2)
    OUT.mkdir(parents=True, exist_ok=True)
    # No creation date in the PDF, so an unchanged figure rebuilds byte for byte.
    fig.savefig(OUT / f"{slug}.pdf", metadata={"CreationDate": None})
    fig.savefig(OUT / f"{slug}.png", dpi=DPI_PNG)
    plt.close(fig)
    return OUT / f"{slug}.pdf"


# --------------------------------------------------------------------------- #
# caption stubs
# --------------------------------------------------------------------------- #
_TEX_SPECIAL = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
                "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
                "^": r"\textasciicircum{}", "−": "$-$", "±": r"$\pm$",
                "µ": r"\textmu{}", "×": r"$\times$", "≤": r"$\leq$",
                "≥": r"$\geq$"}


def tex_escape(s: str) -> str:
    return "".join(_TEX_SPECIAL.get(c, c) for c in s)


def n_text(n) -> str:
    """n = 42, or {"hand-tuned": 4, "optimizer": 14} -> "n = 4 (hand-tuned), 14 (optimizer)"."""
    if isinstance(n, dict):
        return "n = " + ", ".join(f"{v} ({k})" for k, v in n.items())
    return f"n = {n}"


def caption(what: str, *, n, error_bars: str, data, message: str | None = None,
            slug: str | None = None):
    """Write the caption stub next to the figure: figures/out/<slug>.caption.tex
    (for \\figcaption{<slug>} in the manuscript) and <slug>.caption.md.

    what        what is plotted, as a sentence
    n           the number of independent samples behind each mark: an int,
                or {group: n}; computed from the data, never typed in
    error_bars  what the error bars are ("mean ± one standard deviation"), or
                why there are none ("none: each point is a single dose")
    data        the data/ file or files the figure reads
    message     the one-sentence finding; a fill-me placeholder until known
    """
    slug = slug or _script_slug()
    files = [data] if isinstance(data, str) else list(data)
    what, eb = what.strip().rstrip("."), error_bars.strip().rstrip(".")
    if eb.lower().startswith("none"):
        body = f"{what}. {n_text(n)}. No error bars{eb[4:]}."
    else:
        body = f"{what}. {n_text(n)}. Error bars: {eb}."
    tex_msg = tex_escape(message) if message else r"\fillme{One-sentence finding.}"
    md_msg = message or "**[One-sentence finding.]**"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.caption.tex").write_text(
        f"% Caption stub for {slug}, written by figures/{slug}.py: edit the words there,\n"
        f"% not here, as make figures overwrites this file.\n"
        + "".join(f"% data: data/{f}\n" for f in files)
        + f"{tex_msg} {tex_escape(body)}\n", encoding="utf-8")
    (OUT / f"{slug}.caption.md").write_text(
        f"**{slug}.** {md_msg} {body}\n\nData: " + ", ".join(f"`data/{f}`" for f in files) + "\n",
        encoding="utf-8")


# --------------------------------------------------------------------------- #
# helpers for both presets (the powder-doser look)
# --------------------------------------------------------------------------- #
def _geom():
    return _GEOM[PRESET or "paper"]


def style_axes(ax, xlim, ylim, xticks, yticks, xfmt=None, yfmt=None):
    """Left and bottom axis lines only, pushed out from the data and ending at
    the outermost ticks; ticks at round values only."""
    g = _geom()
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    if xfmt:
        ax.set_xticklabels([xfmt(v) for v in xticks])
    if yfmt:
        ax.set_yticklabels([yfmt(v) for v in yticks])
    for side in ("left", "bottom"):
        ax.spines[side].set_position(("outward", g["spine_out"]))
    ax.spines["left"].set_bounds(yticks[0], yticks[-1])
    ax.spines["bottom"].set_bounds(xticks[0], xticks[-1])
    ax.tick_params(pad=g["tick_pad"])


def ylabel_top(ax, text, x=-0.0, y=None):
    """Horizontal y label above the axis, left aligned with it."""
    ax.text(x, _geom()["label_y"] if y is None else y, text, transform=ax.transAxes,
            ha="left", va="bottom", fontsize=plt.rcParams["axes.labelsize"],
            color=plt.rcParams["axes.labelcolor"], linespacing=1.2)


def xlabel(ax, text, pad=None):
    ax.set_xlabel(text, fontsize=plt.rcParams["axes.labelsize"],
                  color=plt.rcParams["axes.labelcolor"],
                  labelpad=pad if pad is not None else (14 if PRESET == "slide" else 2),
                  loc="left")


def callout(ax, text, xy, xytext, color, ha="left", va="center", alpha=None, fs=None,
            weight="normal", zorder=6, lw=None, coords="data"):
    """Text in the series colour, joined to its mark by a faded line with no
    arrowhead (instead of a legend)."""
    g = _geom()
    a, b = g["shrink"]
    return ax.annotate(text, xy=xy, xytext=xytext, textcoords=coords,
                       fontsize=fs or plt.rcParams["font.size"], color=color, ha=ha, va=va,
                       fontweight=weight, zorder=zorder,
                       arrowprops=dict(arrowstyle="-", color=color,
                                       alpha=g["callout_alpha"] if alpha is None else alpha,
                                       lw=g["callout_lw"] if lw is None else lw,
                                       shrinkA=a, shrinkB=b))


# --------------------------------------------------------------------------- #
# slides (from powder-doser slide_style.py, unchanged in behaviour)
# --------------------------------------------------------------------------- #
def slide(message: str | None = None):
    """A blank 16:9 slide with the message, if any, at the fixed spot."""
    _need("slide")
    fig = plt.figure(figsize=FIG_IN)
    if message:
        fig.text(*TITLE_XY, message, fontsize=FS_TITLE, color=INK, ha="left", va="top",
                 linespacing=1.15)
    return fig


def to_image(fig, dpi=DPI_SCREEN) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, format="png")
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def _crossfade(frames, holds, fade_s, fps, fades=None):
    """fades: the cross-fade into each frame (s); default fade_s for all."""
    seq = []
    for i, (im, hold) in enumerate(zip(frames, holds)):
        f = fade_s if fades is None else fades[i]
        if i > 0 and f > 0:
            prev = frames[i - 1]
            n = max(1, round(f * fps))
            for k in range(1, n + 1):
                seq.append(Image.blend(prev, im, k / (n + 1)))
        seq += [im] * max(1, round(hold * fps))
    return seq


def write_gif(frames, holds, path: Path, fade_s=0.25, fps=12, width=1280, fades=None):
    """Build GIF: each step held for its time, short cross-fades between.
    Identical consecutive frames are merged so the file stays small."""
    seq = _crossfade(frames, holds, fade_s, fps, fades)
    if width and seq[0].width != width:
        h = round(seq[0].height * width / seq[0].width)
        seq = [im.resize((width, h), Image.LANCZOS) for im in seq]
    merged, durs = [], []
    for im in seq:
        if merged and np.array_equal(np.asarray(merged[-1]), np.asarray(im)):
            durs[-1] += 1000 / fps
        else:
            merged.append(im)
            durs.append(1000 / fps)
    pal = [im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
           for im in merged]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=[round(d) for d in durs],
                loop=0, optimize=True, disposal=2)


def write_mp4(frames, holds, path: Path, fade_s=0.25, fps=30, fades=None):
    """Same build as an H.264 MP4 at the frames' size (1920 x 1080)."""
    seq = _crossfade(frames, holds, fade_s, fps, fades)
    w, h = seq[0].size
    ff = subprocess.Popen(
        [shutil.which("ffmpeg"), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
         "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-movflags", "+faststart", str(path)], stdin=subprocess.PIPE)
    for im in seq:
        ff.stdin.write(im.tobytes())
    ff.stdin.close()
    assert ff.wait() == 0
