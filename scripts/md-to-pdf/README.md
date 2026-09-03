# `md-to-pdf` — render a repo Markdown doc to a print-ready PDF

Used to produce the printable copy of the powder-disposal SOP
(`edison/powder-disposal-sop/powder-disposal-sop.pdf`). Works on any Markdown file in the
repo, so regenerate rather than hand-editing the PDF whenever the source `.md` changes.

`marked` handles Markdown → HTML (GFM: tables, task lists, autolinks); headless Chrome
handles HTML → PDF, which is why tables, checkboxes and emoji all print correctly.

## Usage

```bash
cd scripts/md-to-pdf
npm install                     # once; needs Chrome/Chromium on PATH or $CHROME_PATH

cd ../..                        # back to the repo root, so relative paths resolve
node scripts/md-to-pdf/render.mjs edison/powder-disposal-sop/powder-disposal-sop.md
```

The output path defaults to the input with a `.pdf` extension; pass a second argument to
override it, and `--title "..."` to override the running header (defaults to the document's
first `# ` heading).

## Output conventions

- US Letter, 0.7" margins, running header with the document title, footer with the source
  filename, render date and `Page N of M`.
- Each `#` heading after the first starts a new page (so a provenance/caveats preamble
  becomes a cover page).
- Table headers repeat across page breaks; rows and list items avoid splitting.
- `- [ ]` / `- [x]` task lists print as real checkboxes.

## Requirements

Node 18+, and Google Chrome or Chromium. The script looks at `$CHROME_PATH` first, then
`/usr/bin/google-chrome`, `/usr/bin/chromium`, `/usr/bin/chromium-browser`, and the macOS
`Google Chrome.app` path.
