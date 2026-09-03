#!/usr/bin/env node
/**
 * Render a Markdown document to a print-ready PDF (US Letter) using `marked`
 * for Markdown -> HTML and headless Chrome for HTML -> PDF.
 *
 * Usage:
 *   cd scripts/md-to-pdf && npm install
 *   node render.mjs <input.md> [output.pdf] [--title "Header title"]
 *
 * Chrome is located via $CHROME_PATH, else the usual Linux/macOS install paths.
 */
import { readFile, writeFile, access } from "node:fs/promises";
import { basename, resolve } from "node:path";
import { marked } from "marked";
import puppeteer from "puppeteer-core";

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
].filter(Boolean);

async function findChrome() {
  for (const candidate of CHROME_CANDIDATES) {
    try {
      await access(candidate);
      return candidate;
    } catch {
      /* try the next one */
    }
  }
  throw new Error(
    `No Chrome/Chromium found. Set CHROME_PATH. Tried:\n  ${CHROME_CANDIDATES.join("\n  ")}`,
  );
}

const CSS = `
  @page { size: Letter; margin: 0.62in 0.7in 0.7in 0.7in; }

  html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body {
    font-family: Lato, "DejaVu Sans", "Liberation Sans", Arial, "Noto Color Emoji", sans-serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #1b1b1b;
    margin: 0;
    orphans: 3;
    widows: 3;
  }

  h1, h2, h3, h4 { break-after: avoid; page-break-after: avoid; line-height: 1.25; }
  h1 {
    font-size: 17pt;
    margin: 0 0 0.5em;
    padding-bottom: 0.22em;
    border-bottom: 2px solid #2b4a6f;
    color: #14304d;
  }
  /* Treat each top-level H1 after the first as the start of a new document section. */
  h1:not(:first-of-type) { break-before: page; page-break-before: always; margin-top: 0; }
  h2 {
    font-size: 13pt;
    margin: 1.35em 0 0.45em;
    padding-top: 0.3em;
    border-top: 1px solid #c7d2de;
    color: #14304d;
  }
  h3 { font-size: 11.5pt; margin: 1.1em 0 0.35em; color: #22384d; }
  h4 { font-size: 10.5pt; margin: 0.9em 0 0.3em; }

  p { margin: 0.5em 0; }
  ul, ol { margin: 0.45em 0; padding-left: 1.35em; }
  li { margin: 0.22em 0; break-inside: avoid; page-break-inside: avoid; }
  li > ul, li > ol { margin: 0.2em 0; }

  strong { color: #101010; }
  hr { border: 0; border-top: 1px solid #d7dde5; margin: 1.1em 0; }

  a { color: #14456e; text-decoration: none; word-break: break-word; }

  blockquote {
    margin: 0.7em 0;
    padding: 0.5em 0.85em;
    border-left: 4px solid #e0a500;
    background: #fdf6e3;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  blockquote > :first-child { margin-top: 0; }
  blockquote > :last-child { margin-bottom: 0; }

  code {
    font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
    font-size: 0.88em;
    background: #f2f4f7;
    border: 1px solid #e2e6ec;
    border-radius: 3px;
    padding: 0.05em 0.28em;
  }
  pre {
    background: #f2f4f7;
    border: 1px solid #e2e6ec;
    border-radius: 4px;
    padding: 0.6em 0.8em;
    overflow-wrap: break-word;
    white-space: pre-wrap;
    break-inside: avoid;
  }
  pre code { background: none; border: 0; padding: 0; }

  table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.7em 0;
    font-size: 9pt;
  }
  thead { display: table-header-group; }
  tr { break-inside: avoid; page-break-inside: avoid; }
  th, td {
    border: 1px solid #b8c2cf;
    padding: 0.32em 0.5em;
    text-align: left;
    vertical-align: top;
  }
  th { background: #eef2f7; color: #14304d; font-weight: 700; }
  tbody tr:nth-child(even) { background: #f8fafc; }

  /* GFM task lists: render as printable boxes rather than form controls. */
  li:has(> input[type="checkbox"]) { list-style: none; margin-left: -1.15em; }
  input[type="checkbox"] {
    appearance: none;
    -webkit-appearance: none;
    box-sizing: border-box;
    display: inline-block;
    width: 0.85em;
    height: 0.85em;
    border: 1.2px solid #55606d;
    border-radius: 2px;
    margin: 0 0.5em 0 0;
    vertical-align: middle;
    position: relative;
    top: -0.05em;
  }
  input[type="checkbox"]:checked::after {
    content: "\\2713";
    position: absolute;
    top: -0.42em;
    left: 0.04em;
    font-size: 1.1em;
    line-height: 1;
    color: #14304d;
  }

  img { max-width: 100%; }
`;

/**
 * CommonMark folds soft line breaks, which collapses hand-written metadata blocks
 * ("**Facility**: ...\n**Applicable Powders**: ...") into one run-on paragraph. Give
 * each line in such a run an explicit hard break so it prints the way it was written.
 */
function hardBreakMetadataRuns(source) {
  const lines = source.split("\n");
  const isMetadata = (line) => /^\*\*[^*]+\*\*\s*:/.test(line);
  return lines
    .map((line, i) =>
      isMetadata(line) && isMetadata(lines[i + 1] ?? "") ? `${line.replace(/\s+$/, "")}  ` : line,
    )
    .join("\n");
}

function htmlEscape(text) {
  return text.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
}

async function main() {
  const args = process.argv.slice(2);
  const titleFlag = args.indexOf("--title");
  let headerTitle = null;
  if (titleFlag !== -1) {
    headerTitle = args[titleFlag + 1];
    args.splice(titleFlag, 2);
  }

  const input = args[0];
  if (!input) {
    console.error('Usage: node render.mjs <input.md> [output.pdf] [--title "Header title"]');
    process.exit(1);
  }
  const output = args[1] ?? input.replace(/\.md$/i, ".pdf");

  const source = await readFile(resolve(input), "utf8");
  // Fall back to the document's first H1 for the running header.
  headerTitle ??= (source.match(/^#\s+(.+)$/m)?.[1] ?? basename(input)).replace(/[*_`]/g, "");

  const body = marked.parse(hardBreakMetadataRuns(source), {
    gfm: true,
    breaks: false,
    mangle: false,
    headerIds: false,
  });
  const generated = new Date().toISOString().slice(0, 10);

  const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>${htmlEscape(headerTitle)}</title>
<style>${CSS}</style>
</head><body>${body}</body></html>`;

  const browser = await puppeteer.launch({
    executablePath: await findChrome(),
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--font-render-hinting=none"],
  });
  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: "load" });
    await page.emulateMediaType("print");

    const chrome = (s) =>
      `<div style="font-family:Lato,'DejaVu Sans',Arial,sans-serif;font-size:7.5pt;color:#6b7280;width:100%;padding:0 0.7in;">${s}</div>`;

    await page.pdf({
      path: resolve(output),
      format: "Letter",
      printBackground: true,
      displayHeaderFooter: true,
      headerTemplate: chrome(
        `<div style="border-bottom:0.5px solid #d7dde5;padding-bottom:2px;">${htmlEscape(headerTitle)}</div>`,
      ),
      footerTemplate: chrome(
        `<div style="border-top:0.5px solid #d7dde5;padding-top:3px;display:flex;justify-content:space-between;">` +
          `<span>${htmlEscape(basename(input))} &nbsp;·&nbsp; rendered ${generated}</span>` +
          `<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>` +
          `</div>`,
      ),
      margin: { top: "0.72in", bottom: "0.7in", left: "0.7in", right: "0.7in" },
    });
  } finally {
    await browser.close();
  }

  console.log(`Wrote ${output}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
