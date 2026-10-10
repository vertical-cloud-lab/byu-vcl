#!/usr/bin/env python3
"""Scrape the full call-for-abstracts text of every TMS 2027 symposium from
ProgramMaster (the same content TMS renders into the per-symposium flyer PDFs:
title, sponsorship, organizers + affiliations, full scope, abstract deadline).

tms.org hosts the flyer PDFs behind Cloudflare, but ProgramMaster serves the
identical source text without restriction.

Writes:
  edison-trajectories/tms-symposium-top10/bundle/tms2027-symposia-full-text.md
  edison-trajectories/tms-symposium-top10/bundle/tms2027-symposia.json

Usage:
    python scripts/edison/scrape_tms2027_symposia.py
"""
from __future__ import annotations

import html
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
BUNDLE = HERE / "edison-trajectories" / "tms-symposium-top10" / "bundle"

PORTAL = (
    "https://www.programmaster.org/PM/PM.nsf/Home"
    "?OpenForm&ParentUNID=A79798B673220E9885258B13005BB1F5"
)
BASE = "https://www.programmaster.org"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_tags(fragment: str) -> list[str]:
    text = re.sub(r"<script.*?</script>", " ", fragment, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = html.unescape(text)
    return [ln.strip() for ln in text.split("\n") if ln.strip()]


def parse_symposium(page: str) -> dict:
    lines = strip_tags(page)

    def section(start_label: str, end_labels: tuple[str, ...]) -> list[str]:
        try:
            i = lines.index(start_label)
        except ValueError:
            return []
        out = []
        for ln in lines[i + 1 :]:
            if ln in end_labels:
                break
            out.append(ln)
        return out

    title = section("Symposium", ("Sponsorship",))
    sponsorship = section("Sponsorship", ("Organizer(s)",))
    organizer_lines = section("Organizer(s)", ("Scope",))
    organizers = []
    pending_name = None
    for ln in organizer_lines:
        if ln == ",":
            continue
        if pending_name is None:
            pending_name = ln
        else:
            organizers.append({"name": pending_name, "affiliation": ln})
            pending_name = None
    if pending_name:
        organizers.append({"name": pending_name, "affiliation": ""})
    scope = section(
        "Scope", ("Abstracts Due", "Proceedings Plan", "IF YOU WOULD LIKE TO SUBMIT AN ABSTRACT . . .")
    )
    due = section("Abstracts Due", ("Proceedings Plan", "IF YOU WOULD LIKE TO SUBMIT AN ABSTRACT . . ."))
    proceedings = section("Proceedings Plan", ("IF YOU WOULD LIKE TO SUBMIT AN ABSTRACT . . .",))
    return {
        "title": " ".join(title),
        "sponsorship": sponsorship,
        "organizers": organizers,
        "scope": "\n".join(scope),
        "abstracts_due": " ".join(due),
        "proceedings": " ".join(proceedings),
    }


def main() -> None:
    BUNDLE.mkdir(parents=True, exist_ok=True)
    portal = fetch(PORTAL)
    links = re.findall(r'href="(/PM/PM\.nsf/UpcomingSymposia/[^"]+)"', portal)
    # de-dup, preserve order
    seen, urls = set(), []
    for u in links:
        if u not in seen:
            seen.add(u)
            urls.append(BASE + html.unescape(u))
    print(f"found {len(urls)} symposium pages")

    symposia = []
    for n, url in enumerate(urls, 1):
        for attempt in range(3):
            try:
                page = fetch(url)
                break
            except Exception as exc:  # noqa: BLE001
                print(f"  retry {attempt + 1} for {url}: {exc}")
                time.sleep(5)
        else:
            print(f"  FAILED: {url}")
            continue
        info = parse_symposium(page)
        info["url"] = url
        symposia.append(info)
        print(f"[{n}/{len(urls)}] {info['title'][:70]}")
        time.sleep(0.5)

    (BUNDLE / "tms2027-symposia.json").write_text(json.dumps(symposia, indent=2))

    md = [
        "# TMS 2027 Annual Meeting & Exhibition — full symposium call-for-abstracts text",
        "",
        "Source: ProgramMaster (www.programmaster.org/TMS2027), scraped 2026-07-10.",
        "This is the same content TMS renders into each symposium's flyer PDF:",
        "title, sponsorship, organizers with affiliations, full scope, and deadline.",
        f"Total symposia: {len(symposia)}",
        "",
    ]
    for i, s in enumerate(symposia, 1):
        md.append(f"---\n\n## {i}. {s['title']}\n")
        md.append("**Sponsorship:** " + "; ".join(s["sponsorship"]))
        orgs = ", ".join(f"{o['name']} ({o['affiliation']})" for o in s["organizers"])
        md.append(f"**Organizers:** {orgs}")
        if s["abstracts_due"]:
            md.append(f"**Abstracts due:** {s['abstracts_due']}")
        if s["proceedings"]:
            md.append(f"**Proceedings:** {s['proceedings']}")
        md.append("\n**Scope:**\n")
        md.append(s["scope"])
        md.append("")
    out = BUNDLE / "tms2027-symposia-full-text.md"
    out.write_text("\n".join(md))
    print("wrote", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
