"""Shared chart style: reference palette from the dataviz skill (light mode), thin marks, recessive axes."""
import matplotlib as mpl
SURFACE = "#fcfcfb"; INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#8a8985"; GRID = "#e6e5e1"
OPEN = "#2a78d6"     # slot 1, blue: open-source origin
CLOSED = "#eb6834"   # slot 2, orange: closed source
THIRD = "#1baf7a"    # slot 3, aqua
def style():
    mpl.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False, "font.size": 10.5,
        "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "legend.frameon": False, "figure.dpi": 110, "savefig.dpi": 160, "savefig.bbox": "tight"})
