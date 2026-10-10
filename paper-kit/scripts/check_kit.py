"""make check: the figure and data conventions, and what is left to fill.

    python scripts/check_kit.py               # conventions; placeholders listed
    python scripts/check_kit.py --submission  # also fails on any placeholder left

Checks that every figure script is named figN_slug.py and has its PDF, 600 dpi
PNG and caption stub in figures/out/ (and nothing there lacks a script), that
every PNG is 85 or 175 mm wide, and that every file in data/ has a README
stating units, n and provenance.  Then lists the \\fillme{}, \\todo{} and
other placeholders still in the manuscript.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))
import vcl_style as vs  # noqa: E402

PLACEHOLDER = re.compile(r"\\fillme\{|\\todo(?:\[[^\]]*\])?\{|\\figplaceholder|\\tabplaceholder"
                         r"|\\dummy\{|XXXXXXX|\[TOOL|\[PURPOSE|\[FUNDER|\[GRANT")


def figure_problems() -> list[str]:
    out = []
    scripts = sorted((KIT / "figures").glob("*.py"))
    slugs = set()
    for s in scripts:
        if not vs.FIG_NAME.match(s.stem):
            out.append(f"figures/{s.name}: name figure scripts figN_slug.py")
            continue
        slugs.add(s.stem)
        for ext in (".pdf", ".png", ".caption.tex", ".caption.md"):
            if not (vs.OUT / f"{s.stem}{ext}").exists():
                out.append(f"figures/out/{s.stem}{ext} missing: run make figures")
        png = vs.OUT / f"{s.stem}.png"
        if png.exists():
            from PIL import Image
            with Image.open(png) as im:
                dpi = im.info.get("dpi", (0, 0))[0]
                w_mm = im.width / (dpi or 1) * 25.4
            if round(dpi) != vs.DPI_PNG:
                out.append(f"figures/out/{png.name}: {dpi:.0f} dpi, not {vs.DPI_PNG}")
            elif not any(abs(w_mm - w) < 0.5 for w in vs.WIDTHS_MM.values()):
                out.append(f"figures/out/{png.name}: {w_mm:.1f} mm wide, not 85 or 175 mm")
    if vs.OUT.exists():
        for f in sorted(vs.OUT.iterdir()):
            stem = f.name.split(".")[0]
            if f.is_file() and stem not in slugs:
                out.append(f"figures/out/{f.name}: no figures/{stem}.py makes it (stale?)")
    return out


def data_problems() -> list[str]:
    out = []
    for f in sorted(vs.DATA.iterdir()):
        if f.is_dir() or f.name.endswith(".md") or f.name.startswith("."):
            continue
        out += [f"data/{f.name}: {p}" for p in vs.readme_problems(vs.readme_for(f))]
    return out


def placeholders() -> list[str]:
    out = []
    for tex in sorted((KIT / "manuscript").rglob("*.tex")):
        if "vendor" in tex.parts or tex.name.endswith("-diff.tex"):
            continue
        for i, line in enumerate(tex.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("%"):
                continue
            if PLACEHOLDER.search(line):
                out.append(f"{tex.relative_to(KIT)}:{i}: {line.strip()[:90]}")
    for cap in sorted(vs.OUT.glob("*.caption.tex")) if vs.OUT.exists() else []:
        if "\\fillme" in cap.read_text(encoding="utf-8"):
            out.append(f"{cap.relative_to(KIT)}: the finding is still a placeholder")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--submission", action="store_true",
                    help="fail if any placeholder is left in the manuscript")
    args = ap.parse_args()
    problems = figure_problems() + data_problems()
    for p in problems:
        print("FAIL", p)
    left = placeholders()
    if left:
        print(f"\n{len(left)} placeholder lines left to fill (main-*.tex for journals you are not "
              "targeting can be deleted):")
        for p in left:
            print("  ", p)
    if not problems:
        print("\nfigures and data: OK")
    return 1 if problems or (args.submission and left) else 0


if __name__ == "__main__":
    sys.exit(main())
