"""Render the markdown sources to Word and PDF copies for co-author review.

The markdown files are the source of truth. This script only makes copies that
people can read and annotate without a markdown viewer:

    python tools/build_review_copies.py            # from the democratizing-sdl folder

Needs pandoc (the pypandoc_binary wheel bundles it), python-docx and Pillow, and
LibreOffice (`soffice`) for the PDFs; without soffice it writes the .docx only.

Outputs go to sign-off/review-copies/:

- manuscript-v3.docx / .pdf      clean text, as it would be submitted
- manuscript-v3-for-review.docx  the same, with line numbers and every
                                 SIGN-OFF anchor shown inline as [[ID]], so each
                                 co-author can find the sentences they confirm
- esi.docx / .pdf, response-to-decision-letter.docx / .pdf, cover-letter.docx / .pdf
- ../summary-of-changes.docx / .pdf and ../per-author-checklist.docx / .pdf

Figures are downscaled to 1600 px on the long side for these copies only; the
submission uses the full-resolution files in figures/.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # democratizing-sdl/
OUT = HERE / "sign-off" / "review-copies"
MAX_PX = 1600

SOURCES = [
    # (source, output stem, output dir, line numbers + visible anchors?)
    ("manuscript-v3.md", "manuscript-v3", OUT, False),
    ("manuscript-v3.md", "manuscript-v3-for-review", OUT, True),
    ("esi/supplementary-information.md", "esi", OUT, False),
    ("response-to-decision-letter.md", "response-to-decision-letter", OUT, False),
    ("cover-letter.md", "cover-letter", OUT, False),
    ("sign-off/summary-of-changes.md", "summary-of-changes", HERE / "sign-off", False),
    ("sign-off/per-author-checklist.md", "per-author-checklist", HERE / "sign-off", False),
]

FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
COMMENT = re.compile(r"<!--(.*?)-->", re.S)
SIGNOFF_ID = re.compile(r"\b(?:ALL|SGB|SL|BP|LDP|TV|TB|JEH|NP|OM|P7)-\d+\b")
SUP = re.compile(r"<sup>(.*?)</sup>")
SUB = re.compile(r"<sub>(.*?)</sub>")
FIG = re.compile(r"!\[(Figure \d+)?\]\(([^)]+)\)")
REL_LINK = re.compile(r"(?<!!)\[([^\]]*)\]\((?!https?://|#|mailto:|/)([^)\s]+)\)")


def shrink(src: Path, dst_dir: Path) -> Path:
    from PIL import Image

    dst = dst_dir / src.name
    if dst.exists():
        return dst
    im = Image.open(src)
    im.thumbnail((MAX_PX, MAX_PX))
    if im.mode == "RGBA" and src.suffix.lower() in {".jpg", ".jpeg"}:
        im = im.convert("RGB")
    im.save(dst, quality=88) if src.suffix.lower() in {".jpg", ".jpeg"} else im.save(dst)
    return dst


def preprocess(text: str, src: Path, imgdir: Path, review: bool) -> str:
    text = FRONT_MATTER.sub("", text)

    def comment(m: re.Match) -> str:
        if not review:
            return ""
        ids = sorted(set(SIGNOFF_ID.findall(m.group(1))), key=lambda s: (s.split("-")[0], int(s.split("-")[1])))
        return f" **[[{', '.join(ids)}]]** " if ids else ""

    text = COMMENT.sub(comment, text)
    text = SUP.sub(lambda m: "^" + m.group(1).replace(" ", "\\ ") + "^", text)
    text = SUB.sub(lambda m: "~" + m.group(1).replace(" ", "\\ ") + "~", text)

    def fig(m: re.Match) -> str:
        path = (src.parent / m.group(2)).resolve()
        if not path.exists():
            return m.group(0)
        return f"![]({shrink(path, imgdir)})"

    # Links to other files in this folder (not images): point readers at the GitHub copy.
    base = "https://github.com/vertical-cloud-lab/byu-vcl/{kind}/claude/issue-188-20260828-1557/docs/manuscripts/democratizing-sdl/"
    rel = src.parent.relative_to(HERE).as_posix()

    def link(m: re.Match) -> str:
        target = m.group(2)
        anchor = ""
        if "#" in target:
            target, anchor = target.split("#", 1)
            anchor = "#" + anchor
        if not target:
            return m.group(0)
        path = Path(os.path.normpath(Path(rel) / target)) if rel != "." else Path(os.path.normpath(target))
        kind = "tree" if target.endswith("/") else "blob"
        return f"[{m.group(1)}]({base.format(kind=kind)}{path.as_posix()}{'/' if target.endswith('/') else ''}{anchor})"

    text = REL_LINK.sub(link, text)
    text = FIG.sub(fig, text)
    return text


def style_docx(path: Path, line_numbers: bool) -> None:
    from docx import Document
    from docx.enum.text import WD_LINE_SPACING
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt

    doc = Document(str(path))
    for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
        if name in [s.name for s in doc.styles]:
            st = doc.styles[name]
            st.font.name = "Calibri"
            st.font.size = Pt(10.5)
            st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            st.paragraph_format.space_after = Pt(5)
    for name, size in (("Title", 17), ("Heading 1", 15), ("Heading 2", 13), ("Heading 3", 11.5)):
        if name in [s.name for s in doc.styles]:
            doc.styles[name].font.size = Pt(size)
    for sec in doc.sections:
        sec.left_margin = sec.right_margin = Cm(2.0)
        sec.top_margin = sec.bottom_margin = Cm(1.8)
        if line_numbers:
            ln = OxmlElement("w:lnNumType")
            ln.set(qn("w:countBy"), "1")
            ln.set(qn("w:restart"), "continuous")
            ln.set(qn("w:distance"), "283")
            sec._sectPr.append(ln)
    # Tables: small font, borders, so the many-column tables fit the page.
    for tbl in doc.tables:
        tbl.style = doc.styles["Table"] if "Table" in [s.name for s in doc.styles] else tbl.style
        tblPr = tbl._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "4")
            el.set(qn("w:color"), "999999")
            borders.append(el)
        tblPr.append(borders)
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.space_after = Pt(0)
                # Every run, including those inside hyperlinks, which p.runs skips.
                for r in cell._tc.iter(qn("w:r")):
                    rpr = r.find(qn("w:rPr"))
                    if rpr is None:
                        rpr = OxmlElement("w:rPr")
                        r.insert(0, rpr)
                    for tag in ("w:sz", "w:szCs"):
                        el = rpr.find(qn(tag))
                        if el is None:
                            el = OxmlElement(tag)
                            rpr.append(el)
                        el.set(qn("w:val"), "17")  # half-points: 8.5 pt
    # Figures: cap width at the text width.
    for shape in doc.inline_shapes:
        max_w = Cm(17.0)
        if shape.width > max_w:
            ratio = max_w / shape.width
            shape.width = int(shape.width * ratio)
            shape.height = int(shape.height * ratio)
    doc.save(str(path))


def main() -> int:
    import pypandoc

    OUT.mkdir(parents=True, exist_ok=True)
    soffice = shutil.which("soffice")
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        imgdir = tmpd / "img"
        imgdir.mkdir()
        for rel, stem, outdir, review in SOURCES:
            src = HERE / rel
            if not src.exists():
                print(f"skip {rel} (missing)")
                continue
            md = preprocess(src.read_text(), src, imgdir, review)
            md_path = tmpd / f"{stem}.md"
            md_path.write_text(md)
            docx = outdir / f"{stem}.docx"
            pypandoc.convert_file(
                str(md_path), "docx", outputfile=str(docx),
                format="markdown+pipe_tables+superscript+subscript+gfm_auto_identifiers-implicit_figures",
                extra_args=[f"--resource-path={src.parent}", "--wrap=none"],
            )
            style_docx(docx, line_numbers=review)
            print(f"wrote {docx.relative_to(HERE)}")
            if soffice and not review:
                subprocess.run(
                    [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(docx)],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300,
                )
                print(f"wrote {(outdir / (stem + '.pdf')).relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
