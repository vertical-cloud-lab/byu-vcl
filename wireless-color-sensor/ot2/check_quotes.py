#!/usr/bin/env python3
"""Second check for accuracy-sources-2026-10-02.md: find every quotation again in its source.

    python3 check_quotes.py accuracy-sources-quotes-2026-10-02.json --dir <folder>

<folder> holds the sources, downloaded from the URLs in the JSON under the file names it
gives (PDFs, or saved HTML pages). Each PDF is converted with `pdftotext -layout` and with
plain `pdftotext` (poppler-utils); HTML is reduced to its text. A quotation passes if it
appears in either text with only whitespace, line-break hyphens, quote marks and ligatures
normalised. "OK~" means it matched only with every hyphen ignored, which is how some PDFs
break a hyphenated word across lines. Exit status 1 if any quotation is missing.
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import unicodedata


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("‑", "-"), ("­", "")):
        s = s.replace(a, b)
    s = re.sub(r"-\s*\n\s*", "-", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def texts(path):
    if path.lower().endswith(".pdf"):
        out = []
        for flags in (["-layout"], []):
            r = subprocess.run(["pdftotext", *flags, path, "-"], capture_output=True, text=True)
            out.append(r.stdout)
        return [norm(t) for t in out]
    src = open(path, encoding="utf-8", errors="replace").read()
    src = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", src)
    return [norm(html.unescape(re.sub(r"(?s)<[^>]+>", "\n", src)))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("quotes")
    ap.add_argument("--dir", required=True)
    a = ap.parse_args()
    spec = json.load(open(a.quotes))
    cache, missing = {}, 0
    for q in spec["quotes"]:
        src = spec["sources"][q["source"]]
        path = os.path.join(a.dir, src["file"])
        if path not in cache:
            cache[path] = texts(path) if os.path.exists(path) else None
        if cache[path] is None:
            print(f"NOFILE {q['id']}: {src['file']} (download from {src['url']})")
            missing += 1
            continue
        n = norm(q["quote"])
        if any(n in t for t in cache[path]):
            tag = "OK  "
        elif any(n.replace("-", "") in t.replace("-", "") for t in cache[path]):
            tag = "OK~ "
        else:
            tag = "MISS"
            missing += 1
        print(f"{tag} {q['id']} [{q['source']}, {q['where']}]: {q['quote'][:80]!r}")
    print(f"{len(spec['quotes']) - missing}/{len(spec['quotes'])} found")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
