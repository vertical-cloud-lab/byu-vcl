#!/usr/bin/env python3
"""Render a SOP markdown file to a print-ready PDF.

Markdown -> styled HTML -> PDF via headless Chromium (no LaTeX / pandoc needed).

    pip install markdown
    python SOP/build-pdf.py SOP/sem-eds-polishing-sop.md

Writes <input>.pdf next to the input file.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CSS = """
@page { size: Letter; margin: 0.7in 0.75in; }
body {
  font-family: "DejaVu Sans", "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 10.5pt; line-height: 1.45; color: #16191d; margin: 0;
}
h1 {
  font-size: 20pt; margin: 0 0 4pt; color: #002E5D;  /* BYU navy */
  border-bottom: 3px solid #002E5D; padding-bottom: 6pt;
}
h2 {
  font-size: 13.5pt; margin: 20pt 0 6pt; color: #002E5D;
  border-bottom: 1px solid #c6ccd4; padding-bottom: 3pt;
  page-break-after: avoid; break-after: avoid;
}
h3 { font-size: 11.5pt; margin: 13pt 0 4pt; color: #24425f; page-break-after: avoid; }
p, li { orphans: 2; widows: 2; }
ul, ol { padding-left: 20pt; margin: 5pt 0; }
li { margin: 2.5pt 0; }
li > ul, li > ol { margin: 2.5pt 0; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 9pt;
       background: #f2f4f7; padding: 0.5pt 3pt; border-radius: 3px; }
a { color: #1c4f82; text-decoration: none; }
strong { color: #000; }
hr { border: none; border-top: 1px solid #dfe3e8; margin: 16pt 0; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9.5pt; }
tr { page-break-inside: avoid; break-inside: avoid; }
thead { display: table-header-group; }
th, td { border: 1px solid #cdd3da; padding: 4pt 7pt; text-align: left;
         vertical-align: top; }
th { background: #eef1f5; color: #002E5D; font-weight: 600; }
tr:nth-child(even) td { background: #fafbfc; }
blockquote {
  margin: 9pt 0; padding: 7pt 11pt; background: #fff8e6;
  border-left: 4px solid #e0a800; page-break-inside: avoid;
}
blockquote p { margin: 3pt 0; }
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    src = Path(sys.argv[1]).resolve()
    out = src.with_suffix(".pdf")

    html_body = markdown.markdown(
        src.read_text(encoding="utf-8"),
        extensions=["tables", "sane_lists", "toc", "attr_list"],
    )
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{src.stem}</title><style>{CSS}</style></head>"
        f"<body>{html_body}</body></html>"
    )

    chrome = next(
        (
            c
            for c in ("chromium", "chromium-browser", "google-chrome", "chrome")
            if shutil.which(c)
        ),
        None,
    )
    if chrome is None:
        print("No Chromium/Chrome binary found on PATH.", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(html, encoding="utf-8")
        subprocess.run(
            [
                chrome,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--no-pdf-header-footer",
                f"--print-to-pdf={out}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
        )

    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} kB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
