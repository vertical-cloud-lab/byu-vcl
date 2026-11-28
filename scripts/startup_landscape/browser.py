#!/usr/bin/env python3
"""Headed-browser and LinkedIn passes for the startup survey (the 2026-11-28 refresh).

The browser is the repo's Onshape rig: headed Chrome on a virtual display (:99), DevTools on
127.0.0.1:9222, and its traffic sent out through a lab Pi over an SSH SOCKS tunnel
(127.0.0.1:1080), so sites see the BYU network rather than a datacenter. Fetch the rig
pinned, as CLAUDE.md describes, then:

    /tmp/onshape-rig/record/rig.sh start
    python scripts/startup_landscape/browser.py linkedin-page  periodic-labs:periodic-labs ...
    python scripts/startup_landscape/browser.py linkedin-jobs  /tmp/li/jobs_byid.json
    SL_SOCKS=127.0.0.1:1080 python scripts/startup_landscape/browser.py linkedin-wayback
    python scripts/startup_landscape/browser.py render URL ...      # client-side pages, no proxy
    python scripts/startup_landscape/browser.py export              # -> data/linkedin_*.json
    /tmp/onshape-rig/record/rig.sh stop

Rules the LinkedIn passes keep:
- Logged out. No account, no form input; the mouse only moves, scrolls and clicks.
- Human pace: 25-50 s between companies, several seconds between clicks.
- Stop at the first sign-in wall or checkpoint for good, for the whole run. Never clear
  cookies, change profile or change exit address to get past one.
- Company-level data only. Page text is kept in /tmp, never committed, with the
  "Employees at ..." card (ordinary staff names) cut out first.
"""
import asyncio
import json
import os
import random
import re
import sys
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(ROOT, "docs", "startup-landscape", "data")
WORK = os.environ.get("SL_BROWSER_WORK", "/tmp/li")
CDP = "http://127.0.0.1:9222"

# LinkedIn company slugs, read from each company's own website footer where it links one.
LINKEDIN = {
    "periodic-labs": ["periodic-labs"], "lila-sciences": ["lila-sciences"], "radical-ai": ["radicalai"],
    "medra": ["medra-ai"], "tetsuwan-scientific": ["tetsuwan-scientific", "tetsuwan"],
    "citrine-informatics": ["citrine-informatics"], "kebotix": ["kebotix"], "mitra-chem": ["mitrachem"],
    "aionics": ["aionics"], "mattiq": ["mattiq"], "emerald-cloud-lab": ["emerald-cloud-lab", "emeraldcloudlab"],
    "orbital-materials": ["orbitalindustries"], "cuspai": ["cusp-ai"], "chemify": ["chemify-limited"],
    "materials-nexus": ["materials-nexus", "materialsnexus"], "entalpic": ["entalpic"], "altrove": ["altrove-ai"],
    "dunia-innovations": ["dunia-innovations"], "atinary": ["atinary"],
    "telescope-innovations": ["telescope-innovations-corp", "telescope-innovations"],
    "intrepid-labs": ["intrepid-labs-ai"], "dp-technology": ["dptechnology"], "deep-principle": ["deep-principle"],
    "matlantis": ["matlantis"], "polymerize": ["polymerize-io"],
}


class Wall(Exception):
    """LinkedIn served its sign-in wall or a checkpoint: the run stops."""


# --- mouse --------------------------------------------------------------------------------

async def wiggle(page, n=None):
    for _ in range(n or random.randint(2, 4)):
        await page.mouse.move(random.randint(150, 1700), random.randint(120, 950), steps=random.randint(15, 45))
        await page.wait_for_timeout(random.randint(250, 900))


async def click_el(page, el):
    """Move the pointer onto an element along a path and click it."""
    box = await el.bounding_box()
    if not box:
        return False
    x = box["x"] + box["width"] * random.uniform(0.35, 0.65)
    y = box["y"] + box["height"] * random.uniform(0.35, 0.65)
    await page.mouse.move(x, y, steps=random.randint(20, 45))
    await page.wait_for_timeout(random.randint(150, 450))
    await page.mouse.click(x, y, delay=random.randint(40, 120))
    return True


async def scroll(page, times=None):
    for _ in range(times or random.randint(3, 6)):
        await page.mouse.wheel(0, random.randint(280, 650))
        await page.wait_for_timeout(random.randint(600, 1600))


def check_wall(url, title):
    if re.search(r"authwall|checkpoint|/login|signup|uas/", url) or \
            re.search(r"(?i)security verification|sign up \||log in or sign up", title or ""):
        raise Wall(f"{url} | {title}")


async def dismiss_modal(page):
    for sel in ["button.modal__dismiss", "button[aria-label='Dismiss']",
                "button.contextual-sign-in-modal__modal-dismiss"]:
        el = await page.query_selector(sel)
        if el and await el.is_visible():
            await click_el(page, el)
            await page.wait_for_timeout(random.randint(500, 1200))
            return True
    return False


async def idle(page, lo=22, hi=45):
    t_end = time.time() + random.uniform(lo, hi)
    while time.time() < t_end:
        await wiggle(page, 1)
        await page.wait_for_timeout(random.randint(2500, 6000))


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


# --- LinkedIn company page (logged out) -------------------------------------------------------

def strip_names(txt):
    return re.sub(r"Employees at [^\n]*\n(?:.*\n){0,40}?(?=See all employees|Updates|Similar pages|Browse jobs)",
                  "Employees at [names removed]\n", txt)


def _field(txt, label):
    m = re.search(rf"\n{re.escape(label)}\n\s*([^\n]+)", txt)
    return m.group(1).strip() if m else None


async def company_page(page, slug, cands):
    out = os.path.join(WORK, "out", "company")
    os.makedirs(out, exist_ok=True)
    for cand in cands:
        resp = await page.goto(f"https://www.linkedin.com/company/{cand}/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(random.randint(3000, 5500))
        title = await page.title()
        check_wall(page.url, title)
        if (resp and resp.status == 404) or re.search(r"(?i)page not found", title):
            await page.wait_for_timeout(random.randint(6000, 12000))
            continue
        await wiggle(page)
        await dismiss_modal(page)
        await scroll(page)
        txt = await page.evaluate("document.body.innerText")
        href = await page.evaluate("""() => { const a = [...document.querySelectorAll('a[href*="f_C="]')];
                                              return a.length ? a[0].href : null }""")
        fc = re.search(r"f_C=(\d+)", href or "")
        rec = {"slug": slug, "linkedin": cand, "url": page.url, "date": time.strftime("%Y-%m-%d", time.gmtime()),
               "members": (re.search(r"View all ([\d,]+) employees", txt) or [None, None])[1],
               "followers": (re.search(r"([\d,.]+K?)\s+followers", txt) or [None, None])[1],
               "size": _field(txt, "Company size"), "f_C": fc.group(1) if fc else None, "how": "live"}
        json.dump(rec, open(os.path.join(out, f"{slug}.json"), "w"), indent=1)
        open(os.path.join(WORK, f"company-{slug}.txt"), "w").write(strip_names(txt))
        return rec
    return None


# --- LinkedIn public job search (logged out) ------------------------------------------------------

CARD_JS = """() => [...document.querySelectorAll('ul.jobs-search__results-list > li')].map(li => {
  const q = s => li.querySelector(s); const t = s => (q(s) && q(s).innerText.trim()) || null;
  const a = q('a.base-card__full-link') || q('a');
  return {title: t('.base-search-card__title'), company: t('.base-search-card__subtitle'),
          location: t('.job-search-card__location'), posted: q('time') && q('time').getAttribute('datetime'),
          posted_text: t('time'), salary: t('.job-search-card__salary-info'), benefits: t('.job-posting-benefits__text'),
          url: a && a.href && a.href.split('?')[0]};
})"""

DETAIL_JS = """() => { const q = s => document.querySelector(s); const t = s => (q(s) && q(s).innerText.trim()) || null;
  return {posted_ago: t('.posted-time-ago__text'), applicants: t('.num-applicants__caption'),
          salary_detail: t('.salary.compensation__salary') || t('.compensation__salary'),
          criteria: [...document.querySelectorAll('li.description__job-criteria-item')].map(li => li.innerText.trim().replace(/\\n+/g, ': ')),
          text: t('.show-more-less-html__markup') || t('.description__text')}; }"""


async def company_filter(page, names):
    """Without a company ID: open the Company filter and tick the company, by mouse."""
    btn = None
    for b in await page.query_selector_all("button"):
        if re.match(r"^Company\b", (await b.inner_text()).strip()) and await b.is_visible():
            btn = b
            break
    if not btn:
        return None
    await click_el(page, btn)
    await page.wait_for_timeout(random.randint(900, 1600))
    labels = await page.query_selector_all("div.filter-values-container label, label[for^='f_C']")
    for lab in labels:
        t = (await lab.inner_text()).strip()
        if norm(re.sub(r"\(\d[\d,]*\)\s*$", "", t)) in names and await lab.is_visible():
            await click_el(page, lab)
            await page.wait_for_timeout(random.randint(500, 1100))
            for b in await page.query_selector_all("button"):
                if (await b.inner_text()).strip() == "Done" and await b.is_visible():
                    await click_el(page, b)
                    break
            await page.wait_for_timeout(random.randint(3500, 6000))
            check_wall(page.url, await page.title())
            return True
    return [(await lab.inner_text()).strip() for lab in labels][:12]


async def company_jobs(page, slug, name, aliases, fcid, detail_cap):
    names = {norm(name), *map(norm, aliases)}
    url = (f"https://www.linkedin.com/jobs/search?f_C={fcid}&geoId=92000000&location=Worldwide" if fcid else
           f"https://www.linkedin.com/jobs/search?keywords={urllib.parse.quote(chr(34) + name + chr(34))}"
           "&location=Worldwide&geoId=92000000")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(random.randint(3500, 6000))
    check_wall(page.url, await page.title())
    await wiggle(page)
    await dismiss_modal(page)
    filt = "by-id" if fcid else await company_filter(page, names)
    header = await page.evaluate("(document.querySelector('h1')||{}).innerText || null")
    for _ in range(8):  # scroll the list; press "See more jobs" while it is offered
        await page.mouse.move(random.randint(250, 600), random.randint(400, 900), steps=random.randint(10, 25))
        for _ in range(random.randint(3, 5)):
            await page.mouse.wheel(0, random.randint(500, 900))
            await page.wait_for_timeout(random.randint(500, 1100))
        more = await page.query_selector("button.infinite-scroller__show-more-button")
        if more and await more.is_visible():
            await click_el(page, more)
            await page.wait_for_timeout(random.randint(2000, 3500))
        else:
            n0 = await page.evaluate("document.querySelectorAll('ul.jobs-search__results-list > li').length")
            await page.wait_for_timeout(1500)
            if n0 == await page.evaluate("document.querySelectorAll('ul.jobs-search__results-list > li').length"):
                break
    cards = await page.evaluate(CARD_JS)
    mine = [c for c in cards if norm(c.get("company")) in names]
    for c in mine[:detail_cap]:  # click into the posting; read the detail pane
        link = await page.query_selector(f'a.base-card__full-link[href^="{c["url"]}"]')
        if not link:
            continue
        await link.scroll_into_view_if_needed()
        await click_el(page, link)
        await page.wait_for_timeout(random.randint(3000, 5000))
        check_wall(page.url, await page.title())
        more = await page.query_selector("button.show-more-less-html__button--more")
        if more and await more.is_visible():
            await click_el(page, more)
        c.update(await page.evaluate(DETAIL_JS))
        if "/jobs/view/" in page.url:
            await page.go_back(wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(6000, 14000))
    return {"slug": slug, "query": name, "search_url": page.url.split("&position")[0], "company_filter": filt,
            "f_C": fcid, "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "header": header,
            "cards_total": len(cards), "cards": mine}


async def run_linkedin(kind, items, detail=None):
    from playwright.async_api import async_playwright
    out = os.path.join(WORK, "out", "jobs_id" if kind == "jobs" else "company")
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP)
        page = browser.contexts[0].pages[0]
        for item in items:
            slug = item[0]
            if os.path.exists(os.path.join(out, f"{slug}.json")):
                continue
            try:
                if kind == "jobs":
                    name, aliases, fcid = item[1], item[2], (item[3] if len(item) > 3 else None)
                    rec = await company_jobs(page, slug, name, aliases, fcid, (detail or {}).get(slug, 0))
                    json.dump(rec, open(os.path.join(out, f"{slug}.json"), "w"), indent=1, ensure_ascii=False)
                else:
                    rec = await company_page(page, slug, item[1])
                print(json.dumps({"slug": slug, "ok": bool(rec)}), flush=True)
            except Wall as wall:
                print("STOP at sign-in wall:", str(wall)[:200], flush=True)
                return 3
            await idle(page)
    return 0


# --- Wayback captures of LinkedIn company pages (archive.org only) ----------------------------------

def parse_capture(body):
    import html
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body)))
    g = lambda rx: (re.search(rx, t) or [None, None])[1]  # noqa: E731
    fc = re.search(r"f_C=(\d+)", body) or re.search(r"urn:li:(?:organization|company|fsd_company):(\d+)", body)
    return {"members": g(r"View all ([\d,]+) employees"), "size": g(r"Company size\s+([\d,]+(?:-[\d,]+)?\+? employees)"),
            "followers": g(r"([\d,.]+K?) followers"), "f_C": fc.group(1) if fc else None}


def linkedin_wayback(per_company=10, since="2019"):
    """Distinct captures (collapsed by digest): the newest half of `per_company`, plus older ones spread
    over time. Requests go through fetch.get: cached, 6 s apart, via $SL_SOCKS."""
    sys.path.insert(0, HERE)
    import fetch
    fetch.MIN_INTERVAL["web.archive.org"] = 6.0
    out_path = os.path.join(WORK, "wayback_linkedin.json")
    out = json.load(open(out_path)) if os.path.exists(out_path) else {}
    for slug, cands in LINKEDIN.items():
        if slug in out:
            continue
        for li in cands:
            rows = fetch.cdx(f"linkedin.com/company/{li}", frm=since, filters=("statuscode:200",), collapse="digest")
            if not rows:
                continue
            if len(rows) > per_company:
                older = rows[:-per_company // 2]
                step = max(1, len(older) // (per_company - per_company // 2))
                rows = older[::step][: per_company - per_company // 2] + rows[-(per_company // 2):]
            caps = []
            for r in rows:
                body = fetch.get(f"https://web.archive.org/web/{r['timestamp']}id_/{r['original']}", timeout=120)
                caps.append({"timestamp": r["timestamp"],
                             "url": f"https://web.archive.org/web/{r['timestamp']}/{r['original']}", **parse_capture(body)})
            out[slug] = {"linkedin": li, "captures": caps}
            break
        json.dump(out, open(out_path, "w"), indent=1)


# --- client-side pages (no proxy: these sites don't need the Pi's address) -------------------------

async def render(urls, outdir, wait_ms=4000):
    from playwright.async_api import async_playwright
    os.makedirs(outdir, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=False,
                                    args=["--no-first-run", "--window-size=1600,1000"],
                                    env={**os.environ, "DISPLAY": ":99"})
        page = await b.new_page(viewport={"width": 1600, "height": 1000})
        res = []
        for u in urls:
            try:
                r = await page.goto(u, wait_until="load", timeout=60000)
            except Exception as err:  # noqa: BLE001
                res.append({"url": u, "error": repr(err)[:200]})
                continue
            await page.mouse.move(random.randint(200, 1400), random.randint(150, 800), steps=25)
            for _ in range(4):
                await page.mouse.wheel(0, random.randint(400, 800))
                await page.wait_for_timeout(700)
            await page.wait_for_timeout(wait_ms)
            res.append({"url": u, "final": page.url, "status": r.status if r else None, "title": await page.title(),
                        "text": await page.evaluate("document.body.innerText")})
        await b.close()
    json.dump(res, open(os.path.join(outdir, "result.json"), "w"), indent=1, ensure_ascii=False)


# --- export to data/ ------------------------------------------------------------------------------------

def _date(ts):
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"


def export(date):
    """data/linkedin_company_pages.json and data/linkedin_jobs.json from the work directory."""
    wb = {}
    for name in ("li_wayback.json", "li_series.json", "wayback_linkedin.json"):
        for d in (WORK, "/tmp/wb"):
            path = os.path.join(d, name)
            if os.path.exists(path):
                for slug, rec in json.load(open(path)).items():
                    wb.setdefault(slug, {"linkedin": rec.get("linkedin"), "captures": {}})
                    wb[slug]["linkedin"] = wb[slug]["linkedin"] or rec.get("linkedin")
                    for c in rec.get("captures") or []:
                        if c.get("timestamp") and not c.get("error"):
                            wb[slug]["captures"][c["timestamp"]] = c
    live = {}
    cdir = os.path.join(WORK, "out", "company")
    for name in os.listdir(cdir) if os.path.isdir(cdir) else []:
        rec = json.load(open(os.path.join(cdir, name)))
        live[rec["slug"]] = rec
    pages = {"refreshed": date, "how": (
        "LinkedIn company pages. 'wayback': captures of the page in the Wayback Machine, read from archive.org. "
        "'live': the page as LinkedIn served it logged out to headed Chrome on a lab Pi's network, before its "
        "sign-in wall stopped the pass. members = 'View all N employees' (people listing the company, alumni "
        "who never updated included); size = the company's self-reported band."), "companies": {}}
    for slug in sorted(set(wb) | set(live)):
        obs, fcid = [], None
        for ts, c in sorted(wb.get(slug, {}).get("captures", {}).items()):
            fcid = fcid or c.get("f_C")
            if c.get("members") or c.get("size"):
                obs.append({"date": _date(ts), "members": int(c["members"].replace(",", "")) if c.get("members") else None,
                            "size": c.get("size"), "followers": c.get("followers"), "source": c["url"], "how": "wayback"})
        if slug in live:
            r = live[slug]
            fcid = fcid or r.get("f_C")
            obs.append({"date": r.get("date") or date, "members": int(r["members"].replace(",", "")) if r.get("members") else None,
                        "size": r.get("size"), "followers": r.get("followers"),
                        "source": f"https://www.linkedin.com/company/{r['linkedin']}/", "how": "live"})
        pages["companies"][slug] = {"linkedin": (wb.get(slug) or {}).get("linkedin") or (live.get(slug) or {}).get("linkedin"),
                                    "company_id": fcid, "observations": obs}
    with open(os.path.join(DATA, "linkedin_company_pages.json"), "w", encoding="utf-8") as fh:
        json.dump(pages, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    jobs = {"refreshed": date, "how": (
        "LinkedIn's public job search, logged out, driven by mouse in headed Chrome on a lab Pi's network: "
        "by company ID (f_C, read from archived company pages) where known, else by name with the Company "
        "filter. Cards are the company's own postings; for companies with no job board of their own, each "
        "card was clicked and its detail pane read."), "companies": {}}
    for sub in ("jobs", "jobs_id"):  # the by-ID pass overrides the by-name one
        jdir = os.path.join(WORK, "out", sub)
        for name in sorted(os.listdir(jdir)) if os.path.isdir(jdir) else []:
            rec = json.load(open(os.path.join(jdir, name)))
            if sub == "jobs" and rec["slug"] in jobs["companies"]:
                continue
            rec.pop("company_filter", None) if isinstance(rec.get("company_filter"), list) else None
            jobs["companies"][rec["slug"]] = rec
    with open(os.path.join(DATA, "linkedin_jobs.json"), "w", encoding="utf-8") as fh:
        json.dump(jobs, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(len(pages["companies"]), "companies' LinkedIn pages;", len(jobs["companies"]), "job searches")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "linkedin-page":
        items = [(a.split(":")[0], a.split(":")[1].split(",")) for a in sys.argv[2:]] or list(LINKEDIN.items())
        return asyncio.run(run_linkedin("page", items))
    if cmd == "linkedin-jobs":
        cfg = json.load(open(sys.argv[2]))
        return asyncio.run(run_linkedin("jobs", cfg["items"], cfg.get("detail")))
    if cmd == "linkedin-wayback":
        return linkedin_wayback()
    if cmd == "render":
        return asyncio.run(render(sys.argv[2:], os.path.join(WORK, "render")))
    if cmd == "export":
        return export(sys.argv[2] if len(sys.argv) > 2 else time.strftime("%Y-%m-%d"))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
