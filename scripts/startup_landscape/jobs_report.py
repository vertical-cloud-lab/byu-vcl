"""Merge the live and archived job postings into data/job_postings.jsonl and
write docs/startup-landscape/job-postings/ (one page per company plus a
cross-company README). Run through ``python scripts/startup_landscape/jobs.py build``.
"""
import glob
import json
import os
import re
import statistics
from collections import Counter, defaultdict

import analyze
from jobs import DOCS, RAW

OUT = os.path.join(DOCS, "job-postings")
FUNCTIONS = analyze.FUNCTIONS
TODAY = "2026-10-10"

# --- what a description asks for ------------------------------------------------------

SKILLS = {  # label: regex over the description, case-insensitive
    "Python": r"\bpython\b", "C/C++": r"\bc\+\+|\bc/c\+\+", "Rust": r"\brust\b", "TypeScript/React": r"typescript|\breact\b",
    "PyTorch": r"pytorch", "JAX": r"\bjax\b", "LLMs": r"\bllms?\b|large language model", "RL": r"reinforcement learning|\brl\b",
    "GNNs": r"graph neural|\bgnns?\b", "diffusion/generative": r"diffusion model|generative model",
    "Bayesian opt./active learning": r"bayesian optimi[sz]ation|active learning|design of experiments|\bdoe\b",
    "CUDA/GPU": r"\bcuda\b|\bgpus?\b", "distributed training": r"distributed training|multi-node|data parallel",
    "Kubernetes/cloud": r"kubernetes|\baws\b|\bgcp\b|\bazure\b", "SQL/databases": r"\bsql\b|postgres|database",
    "DFT": r"\bdft\b|density functional", "molecular dynamics": r"molecular dynamics|\blammps\b",
    "ML potentials": r"interatomic potential|machine[- ]learn(?:ed|ing) (?:force field|potential)|\bmlips?\b",
    "cheminformatics": r"cheminformatic|\brdkit\b", "pymatgen/ASE": r"pymatgen|\base\b",
    "XRD": r"\bxrd\b|x-ray diffraction", "electron microscopy": r"\bsem\b|\btem\b|electron microscop",
    "spectroscopy": r"\bxps\b|raman|ftir|uv-?vis|\bnmr\b|spectroscop", "chromatography/MS": r"hplc|lc-?ms|gc-?ms|chromatograph|mass spec",
    "electrochemistry": r"electrochem|\beis\b|potentiostat|battery|batteries|cell assembly",
    "thin films/vacuum": r"thin[- ]film|sputter|\bpvd\b|\bcvd\b|\bald\b|vacuum|deposition",
    "synthesis": r"synthes", "powders/ceramics": r"powder|ceramic|calcin|sinter|furnace|ball mill",
    "cleanroom/glovebox": r"cleanroom|clean room|glove ?box",
    "robotics": r"robot", "PLC/controls": r"\bplcs?\b|controls engineer|control systems|labview",
    "ROS": r"\bros2?\b", "CAD/mechanical design": r"solidworks|\bcad\b|onshape|fusion 360|mechanical design",
    "electronics/PCB": r"\bpcbs?\b|circuit|electronics", "liquid handling": r"liquid handl|opentrons|hamilton|tecan|pipett",
    "LIMS/ELN": r"\blims\b|\beln\b|electronic lab notebook", "machine vision": r"computer vision|machine vision",
    "EHS/safety": r"\behs\b|osha|chemical hygiene|safety", "GMP/quality": r"\bgmp\b|iso 9001|quality system",
    "customer-facing": r"customer|client", "publications": r"publication|peer-reviewed|first-author",
}
SKILLS = {k: re.compile(v, re.I) for k, v in SKILLS.items()}

KEEP = re.compile(r"(?i)^(about the (role|position|job|team|opportunity)|the (role|position|opportunity|job)|role (overview|summary)|"
                  r"position (overview|summary)|overview|job (description|summary|overview)|summary|what (you'?ll|you will|you'd) (do|work on|be doing)|"
                  r"(key |core |main |your )?responsibilit|your (mission|tasks|role|impact|profile)|in this role|you will|day[- ]to[- ]day|"
                  r"(minimum |basic |required |preferred |desired |key |additional )?qualifications|requirements|"
                  r"(nice|good|great) to have|bonus|what (we'?re|we are) looking for|who you are|about you|you (have|bring|are|might)|"
                  r"(required |preferred |desired |key )?(skills|experience|education)|must[- ]haves?|ideal candidate|"
                  r"(compensation|salary|pay)|what (success|you'?ll) (looks|need)|the work|the team|impact|we'?d love)")
DROP = re.compile(r"(?i)^(about (us|the company|lila|periodic|cusp|medra|orbital|chemify|citrine|dunia|tetsuwan|aionics)|"
                  r"who we are|why (join|work|us|lila|periodic|cusp|medra|orbital|chemify|citrine|dunia)|"
                  r"(our )?benefits|perks|what we offer|we offer|(our )?(values|culture|mission)$|equal (employment )?opportunit|"
                  r"\beeo\b|diversity|privacy|how to apply|application process|(our )?interview|hiring process|"
                  r"work authori|visa|e-verify|recruitment fraud|beware)")
BOILER = re.compile(r"(?i)(is an equal (employment )?opportunity employer|we are an equal opportunity|equal employment opportunity|"
                    r"applicant privacy|privacy notice|e-verify|reasonable accommodation|recruitment scam|"
                    r"we do not accept unsolicited|by submitting your application)")


def sections(text):
    """Split a description into (heading, body) pairs on short heading-like lines."""
    out, head, buf = [], "", []
    for line in (text or "").splitlines():
        s = line.strip()
        bare = s.rstrip(":").strip("*# ").strip()
        is_head = (0 < len(bare) <= 70 and not s.startswith("- ") and not bare.endswith((".", ","))
                   and (s.endswith(":") or KEEP.match(bare) or DROP.match(bare)) and len(bare.split()) <= 9)
        if is_head:
            if buf or head:
                out.append((head, "\n".join(buf).strip()))
            head, buf = bare, []
        else:
            buf.append(s)
    out.append((head, "\n".join(buf).strip()))
    return [(h, b) for h, b in out if b]


def role_text(text, limit=3000):
    """The role-specific part of a description: responsibilities, requirements and
    pay, without the company boilerplate. Falls back to the whole text."""
    secs = sections(text)
    kept = []
    for i, (h, b) in enumerate(secs):
        if h and DROP.match(h):
            continue
        if not h and i == 0 and len(secs) > 1 and any(KEEP.match(x) for x, _ in secs[1:] if x):
            continue  # opening "about the company" paragraph
        m = BOILER.search(b)
        if m:
            b = b[:m.start()].rsplit("\n", 1)[0].strip()
        if b:
            kept.append(f"**{h}**\n{b}" if h else b)
    body = "\n\n".join(kept) or (text or "")
    return body if len(body) <= limit else body[:limit].rsplit("\n", 1)[0] + "\n\n*(truncated: full text in `data/job_postings.jsonl`)*"


def trim(body, limit=3000):
    return body if len(body) <= limit else body[:limit].rsplit("\n", 1)[0] + \
        "\n\n*(truncated: full text in `data/job_postings.jsonl`)*"


DEGREE = [("PhD", r"\bph\.?\s?d\b|doctora"), ("MS", r"\bmaster'?s?\b|\bm\.?\s?sc?\b\.?|\bms\b"),
          ("BS", r"\bbachelor'?s?\b|\bb\.?\s?sc?\b\.?|\bbs\b|\bba/bs\b|undergraduate degree")]


def degrees(text):
    return [d for d, rx in DEGREE if re.search(rx, text or "", re.I)]


YEARS = re.compile(r"(?i)\b(\d{1,2})\s*\+?\s*(?:-|–|to)?\s*(?:\d{1,2}\s*)?\+?\s*years?(?:'|’)?\s+(?:of\s+)?"
                   r"(?:[\w/&,-]+\s+){0,6}?(?:experience|industry|hands-on|post-?doc|work)")


def years_min(text):
    vals = [int(m.group(1)) for m in YEARS.finditer(text or "") if 0 < int(m.group(1)) <= 25]
    return min(vals) if vals else None


SENIORITY = [("intern", r"\bintern|internship|co-?op\b|student"), ("leadership", r"\bhead of|\bchief\b|\bvp\b|vice president|\bdirector\b"),
             ("lead/principal", r"\blead\b|principal|staff\b|\bmanager\b"), ("senior", r"\bsenior\b|\bsr\.?\b|\biii\b|\bl[45]\b"),
             ("entry/associate", r"\bassociate\b|junior|\bjr\.?\b|technician|\bi\b$|graduate")]


def seniority(title):
    t = (title or "").lower()
    for s, rx in SENIORITY:
        if re.search(rx, t):
            return s
    return "mid/unspecified"


def ts_date(ts):
    ts = str(ts or "")
    if re.match(r"^\d{8}", ts):
        return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
    return ts[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", ts) else None


def quarter(d):
    return f"{d[:4]}Q{(int(d[5:7]) - 1) // 3 + 1}" if d else None


# --- merge ---------------------------------------------------------------------------------

GENERIC_TITLE = re.compile(r"(?i)^(careers?|jobs|join us|join our team|open positions|work with us)\b")


def norm_title(t):
    t = re.sub(r"\s+", " ", (t or "")).strip()
    t = re.sub(r"\s*[|–-]\s*(jobs at|careers at)?\s*[A-Z][\w .&]+$", "", t) if " | " in t else t
    return t


def merge():
    by = defaultdict(lambda: defaultdict(list))
    careers_pages = defaultdict(list)
    spans = {}
    for path in sorted(glob.glob(os.path.join(RAW, "*.json"))):
        slug = os.path.basename(path).split(".")[0]
        data = json.load(open(path, encoding="utf-8"))
        if isinstance(data, list):  # live
            for r in data:
                by[slug][str(r.get("posting_id") or r.get("url")).lower()].append(r)
            continue
        for k, v in (data.get("spans") or {}).items():
            spans[(slug, k)] = v
        for r in data["postings"]:
            pid = str(r.get("posting_id") or "").lower()
            if r.get("listing_only") and "/" in pid:
                pid = ""  # a board page fetched as if it were a posting: key its listings by title
            if r.get("generic") and not pid:
                careers_pages[slug].append(r)
                continue
            if not pid:
                pid = "title:" + norm_title(r.get("title")).lower()
            by[slug][pid].append(r)
    rows = []
    for slug, groups in by.items():
        for pid, recs in groups.items():
            live = [r for r in recs if r.get("basis") == "live"]
            pages = [r for r in recs if r.get("basis") == "wayback" and not r.get("listing_only")]
            lists = [r for r in recs if r.get("listing_only")]
            titles = [norm_title(r.get("title")) for r in live + pages + lists if r.get("title")]
            titles = [t for t in titles if t and not GENERIC_TITLE.match(t)]
            if not titles:
                continue
            title = Counter(titles).most_common(1)[0][0]
            texts = [r for r in live + pages if (r.get("text") or "").strip()]
            best = max(texts, key=lambda r: (r.get("basis") == "live", len(r["text"]))) if texts else {}
            dates = []
            for r in recs:
                for f in ("published",):
                    if ts_date(r.get(f)):
                        dates.append(ts_date(r[f]))
                if r.get("basis") == "wayback":
                    cap = re.search(r"/web/(\d{14})/", r.get("capture") or "")
                    if r.get("listing_only") and cap:
                        dates.append(ts_date(cap.group(1)))
                    else:
                        dates += [ts_date(r.get("first_seen")), ts_date(r.get("last_seen"))]
            sp = spans.get((slug, pid))
            if sp:
                dates += [ts_date(sp["first"]), ts_date(sp["last"])]
            dates = sorted(d for d in dates if d)
            if live:
                dates.append(live[0].get("seen") or TODAY)
            first = dates[0] if dates else None
            last = max(dates) if dates else None
            def pick(f):
                for r in live + pages + lists:
                    if r.get(f):
                        return r[f]
                return None
            sal = pick("salary")
            pay_text = pick("pay_text")
            sources = []
            for r in live:
                if r.get("url"):
                    sources.append(r["url"])
            caps = sorted({r["capture"] for r in pages if r.get("capture")})
            sources += caps[:1]
            if not caps and lists:
                sources.append(sorted(r["capture"] for r in lists)[0])
            text = best.get("text") or ""
            rt = role_text(text, limit=10 ** 6)  # requirements are read from the role-specific part only
            rows.append({
                "company": slug, "posting_id": pid if not pid.startswith("title:") else None, "title": title,
                "function": analyze.classify(title), "seniority": seniority(title),
                "team": pick("team"), "location": pick("location"), "employment_type": pick("employment_type"),
                "first_seen": first, "last_seen": last, "open_on_2026_10_10": bool(live),
                "basis": "+".join(sorted({"live" if live else "", "wayback" if pages or lists else ""} - {""})),
                "salary": sal, "pay_text": pay_text if not sal else None,
                "degrees_mentioned": degrees(rt), "years_min": years_min(rt),
                "skills": [k for k, rx in SKILLS.items() if rx.search(rt)],
                "has_description": bool(text.strip()), "text_source": "live" if best.get("basis") == "live" else
                (best.get("capture") if best else None),
                "sources": sources, "text": text,
            })
    rows = dedupe(rows)
    strip_boilerplate(rows)
    for r in rows:
        if GENERAL.search(r["title"]):
            r["function"] = "general-application"
    rows.sort(key=lambda r: (r["company"], r["first_seen"] or "9999", r["title"]))
    return rows, careers_pages


GENERAL = re.compile(r"(?i)don'?t see|general (interest|application|opportunit)|open application|talent (pool|community)|"
                     r"spontaneous|future opportunit|initiativbewerbung|^apply here")


def _line_key(line):
    return re.sub(r"[^a-z]+", "", line.lower())[:200]


def strip_boilerplate(rows):
    """Lines that recur in at least 40% of one company's descriptions (the company
    pitch, perks, legal text) are dropped before requirements are read, so a
    "we combine AI and robotics" pitch doesn't make every role look like a robotics role."""
    by = defaultdict(list)
    for r in rows:
        by[r["company"]].append(r)
    for rs in by.values():
        texts = [r for r in rs if r["text"]]
        freq = Counter(k for r in texts for k in {_line_key(l) for l in r["text"].splitlines() if len(l) > 25})
        common = {k for k, c in freq.items() if len(texts) >= 5 and c >= 0.4 * len(texts)}
        for r in rs:
            own = "\n".join(l for l in (r["text"] or "").splitlines() if _line_key(l) not in common or len(l) <= 25)
            rt = role_text(own, limit=10 ** 6)
            r["role_text"] = rt
            r["degrees_mentioned"], r["years_min"] = degrees(rt), years_min(rt)
            r["skills"] = [k for k, rx in SKILLS.items() if rx.search(rt)]
            r["function"] = classify(r["title"], r.get("team"))


EXTRA_RULES = [  # checked in order, before analyze.TITLE_RULES
    ("leadership", r"\bfounding .*lead(er)?\b|\bhead\b|\bchief\b|\bvp\b|vice president|\bdirector\b"),
    ("business-ops", r"partnership|ecosystem|program manager|developer relations|communications|counsel|controller|"
                     r"financ|strategy|\bsales\b|marketing|content|procurement|\boffice\b|payroll|talent|recruit|"
                     r"sourcer|\bpeople\b|\bhr\b|business"),
    ("software-eng", r"front-?end|back-?end|full[- ]?stack|tech lead|engineering manager"),
    ("lab-automation", r"automated systems|firmware|manufacturing engineer|mechatronic|instrument|process development|"
                       r"pilot plant|prototype"),
    ("ml-research", r"\bmlff\b"),
]


def classify(title, team=None):
    t = (title or "").lower()
    for func, rx in EXTRA_RULES:
        if re.search(rx, t):
            return func
    func = analyze.classify(title)
    # A generic "engineer" on a lab or hardware team (Periodic's "Atoms" team) is lab engineering.
    if func == "software-eng" and re.search(r"(?i)atoms|\blab\b|hardware|automation", team or ""):
        return "lab-automation"
    return func


def _days(a, b):
    from datetime import date
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def dedupe(rows):
    """Merge rows of one company with the same title whose date spans overlap or
    nearly touch: a board listing and the posting page it links to can carry
    different ids, and Ashby re-issues ids when a posting is edited. A title that
    reappears after a gap of more than 45 days stays separate (a re-posting)."""
    key = lambda r: (r["company"], re.sub(r"[^a-z0-9]+", " ", r["title"].lower()).strip())
    groups = defaultdict(list)
    for r in rows:
        groups[key(r)].append(r)
    out = []
    for rs in groups.values():
        rs.sort(key=lambda r: r["first_seen"] or "9999")
        cur = None
        for r in rs:
            if cur and cur["last_seen"] and r["first_seen"] and _days(cur["last_seen"], r["first_seen"]) <= 45:
                keep, other = (cur, r) if (cur["has_description"], cur["open_on_2026_10_10"]) >= \
                    (r["has_description"], r["open_on_2026_10_10"]) else (r, cur)
                merged = dict(keep)
                merged["first_seen"] = min(cur["first_seen"], r["first_seen"])
                merged["last_seen"] = max(cur["last_seen"], r["last_seen"])
                merged["open_on_2026_10_10"] = cur["open_on_2026_10_10"] or r["open_on_2026_10_10"]
                merged["basis"] = "+".join(sorted(set(cur["basis"].split("+")) | set(r["basis"].split("+"))))
                merged["sources"] = list(dict.fromkeys(keep["sources"] + other["sources"]))
                for f in ("team", "location", "salary", "pay_text", "employment_type"):
                    merged[f] = keep.get(f) or other.get(f)
                cur = merged
            else:
                if cur:
                    out.append(cur)
                cur = r
        out.append(cur)
    return out


# --- writing -------------------------------------------------------------------------------

def money(sal):
    if not sal or not sal.get("min"):
        return ""
    cur = {"USD": "$", "GBP": "£", "EUR": "€"}.get(sal.get("currency"), (sal.get("currency") or "") + " ")
    lo, hi = sal["min"], sal.get("max") or sal["min"]
    if lo >= 1000:
        return f"{cur}{lo / 1000:.0f}–{hi / 1000:.0f}K"
    return f"{cur}{lo:g}–{hi:g}/{(sal.get('interval') or '').lower().replace('1 ', '')}"


def link(url, label):
    return f"[{label}]({url})" if url else label


SPLIT_AT = 70  # companies with more described postings get one description page per function


def anchor(r):
    return re.sub(r"[^a-z0-9]+", "-", f'{r["title"]}-{r["first_seen"]}'.lower()).strip("-")


def desc_file(slug, r, split):
    return f"{slug}-{r['function']}.md" if split else ""


def descriptions(rows):
    lines = []
    for r in rows:
        src = r["sources"][0] if r["sources"] else ""
        if r["text_source"] and r["text_source"] != "live":
            src = r["text_source"]
        when = f'{r["first_seen"]} → {"open" if r["open_on_2026_10_10"] else r["last_seen"]}'
        lines += [f'<a id="{anchor(r)}"></a>', "", f'### {r["title"]} ({r["first_seen"]})', "",
                  f'{when} · {r["function"]} · {r["location"] or "location not stated"}'
                  + (f' · {money(r["salary"])}' if r["salary"] else "") + f" · {link(src, 'source')}", "",
                  "<details><summary>Description</summary>", "", trim(r.get("role_text") or r["text"]), "", "</details>", ""]
    return lines


def company_page(slug, rows, careers, meta, split=False):
    name = meta.get("company", slug)
    lines = [f"# {name}: job postings and descriptions", "",
             f"Back to [all companies](README.md) · [company profile](../companies/{slug}.md)", ""]
    n_text = sum(r["has_description"] for r in rows)
    live = sum(r["open_on_2026_10_10"] for r in rows)
    span = [r["first_seen"] for r in rows if r["first_seen"]]
    lines.append(f"**{len(rows)} postings recovered**, {n_text} with the full description; {live} still open on "
                 f"{TODAY}. First seen {min(span) if span else 'n/a'}, latest {max(span) if span else 'n/a'}. "
                 "Dates are the earliest and latest evidence of each posting: its publish date where the job board gives "
                 "one, otherwise its first and last Wayback capture, so they bound how long it was open from inside.")
    lines += ["", "| First seen | Last seen | Title | Function | Team | Location | Degree named | Min. years | Posted pay | Source |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        title = f'[{r["title"]}]({desc_file(slug, r, split)}#{anchor(r)})' if r["has_description"] else r["title"]
        src = " ".join(link(u, "live" if "web.archive.org" not in u else "Wayback") for u in r["sources"][:2])
        last = "open" if r["open_on_2026_10_10"] else (r["last_seen"] or "")
        lines.append(f'| {r["first_seen"] or ""} | {last} | {title} | {r["function"]} | {(r["team"] or "")[:40]} | '
                     f'{(r["location"] or "")[:40]} | {"/".join(r["degrees_mentioned"])} | {r["years_min"] or ""} | '
                     f'{money(r["salary"]) or (r["pay_text"] or "")[:40]} | {src} |')
    if careers:
        caps = sorted({c["capture"] for c in careers})
        lines += ["", "## Careers-page captures", "",
                  f"{len(caps)} archived captures of the company's own careers page. Their text is not reproduced "
                  "here: these pages list postings through embedded widgets that the archive did not capture, and "
                  "some feature named staff, whom this survey does not name. The captures: "
                  + ", ".join(link(c, ts_date(re.search(r"/web/(\d{14})/", c).group(1))) for c in caps) + "."]
    described = [r for r in rows if r["has_description"]]
    note = ("Role-specific sections only (responsibilities, requirements, pay): the company pitch, benefits and "
            "equal-opportunity text are dropped, and so are email addresses and phone numbers.")
    if described and split:
        funcs = [f for f in FUNCTIONS + ["general-application"] if any(r["function"] == f for r in described)]
        lines += ["", "## Descriptions", "", note + " They are split by function: "
                  + ", ".join(f"[{f}]({slug}-{f}.md)" for f in funcs) + "."]
    elif described:
        lines += ["", "## Descriptions", "", note, ""] + descriptions(described)
    return "\n".join(lines) + "\n"


def function_page(slug, func, rows, meta):
    name = meta.get("company", slug)
    head = [f"# {name}: {func} postings", "", f"Back to [{name}'s postings]({slug}.md) · [all companies](README.md)", ""]
    return "\n".join(head + descriptions(rows)) + "\n"


def sanitize_raw():
    """Careers-page captures can name ordinary staff (team photos, testimonials). Their
    text is not used, so it is dropped from the raw files before they are committed."""
    for path in glob.glob(os.path.join(RAW, "*.wayback.json")):
        data = json.load(open(path, encoding="utf-8"))
        changed = False
        for r in data.get("postings", []):
            if r.get("generic") and r.get("text") and (not r.get("posting_id") or GENERIC_TITLE.match(norm_title(r.get("title")))):
                r["text"] = ""
                changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=1, ensure_ascii=False)


def build():
    sanitize_raw()
    rows, careers = merge()
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for path in glob.glob(os.path.join(DOCS, "data", "*.json")):
        d = json.load(open(path, encoding="utf-8"))
        if isinstance(d, dict) and d.get("slug"):
            meta[d["slug"]] = d
    with open(os.path.join(DOCS, "data", "job_postings.jsonl"), "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps({k: v for k, v in r.items() if k != "role_text"}, ensure_ascii=False) + "\n")
    by_co = defaultdict(list)
    for r in rows:
        by_co[r["company"]].append(r)
    for old in glob.glob(os.path.join(OUT, "*.md")):
        if os.path.basename(old) not in ("README.md",):
            os.remove(old)
    for slug in sorted(set(by_co) | set(careers)):
        rs = by_co.get(slug, [])
        split = sum(r["has_description"] for r in rs) > SPLIT_AT
        with open(os.path.join(OUT, f"{slug}.md"), "w", encoding="utf-8") as fh:
            fh.write(company_page(slug, rs, careers.get(slug, []), meta.get(slug, {}), split))
        if split:
            for f in {r["function"] for r in rs if r["has_description"]}:
                with open(os.path.join(OUT, f"{slug}-{f}.md"), "w", encoding="utf-8") as fh:
                    fh.write(function_page(slug, f, [r for r in rs if r["has_description"] and r["function"] == f],
                                           meta.get(slug, {})))
    os.makedirs(os.path.join(DOCS, "figures"), exist_ok=True)
    timeline_figure(rows, meta, os.path.join(DOCS, "figures", "postings_timeline_by_function.png"))
    with open(os.path.join(OUT, "summary.md"), "w", encoding="utf-8") as fh:
        fh.write(summary(rows, by_co, careers, meta))
    print(len(rows), "postings;", sum(r["has_description"] for r in rows), "with descriptions")
    return rows, by_co, careers, meta


def first_roles(rs, n_days=60):
    """Titles first seen within n_days of the company's earliest posting on record."""
    dated = sorted((r for r in rs if r["first_seen"] and r["function"] != "general-application"),
                   key=lambda r: r["first_seen"])
    if not dated:
        return None, []
    t0 = dated[0]["first_seen"]
    return t0, [r for r in dated if _days(t0, r["first_seen"]) <= n_days]


def summary(rows, by_co, careers, meta):
    real = [r for r in rows if r["function"] != "general-application"]
    L = ["# Job postings: generated tables", "",
         "Generated by `python scripts/startup_landscape/jobs.py build` from `data/job_postings.jsonl`. "
         "The findings are in [README.md](README.md); each company's postings and descriptions are on its own page.", "",
         "![Job postings by first-seen date and function](../figures/postings_timeline_by_function.png)", "",
         "## Coverage", "",
         "| Company | Postings | With description | Open on 2026-10-10 | First seen | Last first-seen | Evidence |",
         "|---|---|---|---|---|---|---|"]
    for slug in sorted(by_co, key=lambda c: -len(by_co[c])):
        rs = [r for r in by_co[slug] if r["function"] != "general-application"]
        if not rs:
            continue
        fs = sorted(r["first_seen"] for r in rs if r["first_seen"])
        basis = Counter(b for r in rs for b in r["basis"].split("+"))
        name = meta.get(slug, {}).get("company", slug)
        L.append(f'| [{name}]({slug}.md) | {len(rs)} | {sum(r["has_description"] for r in rs)} | '
                 f'{sum(r["open_on_2026_10_10"] for r in rs)} | {fs[0] if fs else ""} | {fs[-1] if fs else ""} | '
                 + ", ".join(f"{k} {v}" for k, v in sorted(basis.items())) + " |")
    for slug in sorted(set(careers) - set(by_co)):
        name = meta.get(slug, {}).get("company", slug)
        L.append(f"| [{name}]({slug}.md) | careers-page captures only | | | | | wayback |")
    L += ["", f"**Total:** {len(real)} postings, {sum(r['has_description'] for r in real)} with a description.", "",
          "## The first roles each company posted", "",
          "Postings first seen within 60 days of the company's earliest posting on record. For companies whose "
          "board was archived from the start, this is the founding hiring plan; for older companies it is only "
          "where the record begins.", "",
          "| Company | Earliest posting | Roles in the first 60 days |", "|---|---|---|"]
    for slug in sorted(by_co, key=lambda c: (first_roles(by_co[c])[0] or "9999")):
        t0, rs = first_roles(by_co[slug])
        if not rs:
            continue
        name = meta.get(slug, {}).get("company", slug)
        L.append(f'| {name} | {t0} | ' + "; ".join(sorted({r["title"] for r in rs})) + " |")
    L += ["", "## What the descriptions ask for, by function", "",
          "Share of postings with a description that name each degree anywhere in the text (\"PhD or equivalent "
          "experience\" counts as naming a PhD), the median of the smallest \"N+ years\" figure in each description, "
          "and the skills most often named. Python is left out of the skills column because nearly every technical "
          "posting names it.", "",
          requirement_table(real), "",
          "## Functions over time", "",
          "Postings by the half-year they were first seen.", ""]
    halves = sorted({f'{r["first_seen"][:4]}H{1 if int(r["first_seen"][5:7]) <= 6 else 2}' for r in real if r["first_seen"]})
    L.append("| Half-year | " + " | ".join(FUNCTIONS) + " | total |")
    L.append("|---|" + "---|" * (len(FUNCTIONS) + 1))
    for h in halves:
        rs = [r for r in real if r["first_seen"] and f'{r["first_seen"][:4]}H{1 if int(r["first_seen"][5:7]) <= 6 else 2}' == h]
        L.append(f"| {h} | " + " | ".join(str(sum(r["function"] == f for r in rs)) for f in FUNCTIONS) + f" | {len(rs)} |")
    return "\n".join(L) + "\n"


def requirement_table(rows):
    lines = ["| Function | Postings with text | Name a PhD | Name a master's | Name a bachelor's | Median min. years | Most-named skills |",
             "|---|---|---|---|---|---|---|"]
    for f in FUNCTIONS:
        rs = [r for r in rows if r["function"] == f and r["has_description"]]
        if not rs:
            continue
        pct = lambda d: f'{100 * sum(d in r["degrees_mentioned"] for r in rs) / len(rs):.0f}%'
        yrs = [r["years_min"] for r in rs if r["years_min"]]
        skills = Counter(s for r in rs for s in r["skills"] if s not in ("customer-facing", "Python"))
        top = ", ".join(f"{s} ({100 * c / len(rs):.0f}%)" for s, c in skills.most_common(6))
        lines.append(f"| {f} | {len(rs)} | {pct('PhD')} | {pct('MS')} | {pct('BS')} | "
                     f"{statistics.median(yrs) if yrs else '—'} | {top} |")
    return "\n".join(lines)


# --- figure ----------------------------------------------------------------------------------

def timeline_figure(rows, meta, path):
    """One row per company, one lane per function inside it (lane position repeats
    the colour, so function is never read from colour alone), a dot per posting at
    its first-seen date, and a hairline at each equity round."""
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from datetime import date
    dated = [r for r in rows if r["first_seen"] and r["function"] in FUNCTIONS]
    cos = defaultdict(list)
    for r in dated:
        cos[r["company"]].append(r)
    order = sorted((c for c in cos if len(cos[c]) >= 3), key=lambda c: min(r["first_seen"] for r in cos[c]))
    lo = date(2019, 1, 1)
    fig, axes = plt.subplots(len(order), 1, figsize=(9, 0.62 * len(order) + 1.2), sharex=True)
    axes = [axes] if len(order) == 1 else axes
    for ax, slug in zip(axes, order):
        for i, f in enumerate(FUNCTIONS):
            pts = [date.fromisoformat(r["first_seen"]) for r in cos[slug] if r["function"] == f]
            pts = [max(p, lo) for p in pts]
            ax.scatter(pts, [len(FUNCTIONS) - i] * len(pts), s=16, color=analyze.SLOTS6[i],
                       edgecolor=analyze.SURFACE, linewidth=0.8, zorder=3)
        rounds = sorted((analyze.parse_date(fr.get("date")), fr.get("amount_usd_m"))
                        for fr in meta.get(slug, {}).get("funding", [])
                        if fr.get("type") in ("equity", "jv-capital") and analyze.parse_date(fr.get("date")))
        labels = []  # rounds within 120 days of each other share one label
        for d, amt in rounds:
            if d < lo:
                continue
            ax.axvline(d, color=analyze.INK2, linewidth=0.8, zorder=1)
            if labels and (d - labels[-1][0]).days <= 120:
                labels[-1][1].append(amt)
            else:
                labels.append((d, [amt]))
        for d, amts in labels:
            txt = "+".join(f"${a:g}M" for a in amts if a) or "round"
            ax.text(d, len(FUNCTIONS) + 0.9, " " + txt, fontsize=6, color=analyze.INK2, va="top", ha="left")
        ax.set_ylim(0.3, len(FUNCTIONS) + 1)
        ax.set_yticks([])
        ax.grid(axis="y", visible=False)
        name = meta.get(slug, {}).get("company", slug)
        ax.set_ylabel(f"{name}\n({len(cos[slug])})", rotation=0, ha="right", va="center", fontsize=7, color=analyze.INK)
        ax.spines["left"].set_visible(False)
    axes[-1].set_xlim(lo, date(2026, 12, 31))
    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=5, color=c, label=f)
               for c, f in zip(analyze.SLOTS6, FUNCTIONS)]
    fig.legend(handles=handles, loc="upper center", ncol=6, fontsize=7, bbox_to_anchor=(0.55, 1.0),
               title="Function (top lane to bottom lane in each row)", title_fontsize=7)
    fig.suptitle("Job postings by first-seen date, with equity rounds (vertical lines)", y=1.035, fontsize=9,
                 fontweight="bold")
    fig.text(0.99, 0.002, "Postings before 2019 are drawn at 2019. Sources: live job-board APIs and Wayback captures.",
             ha="right", fontsize=6, color=analyze.MUTED)
    fig.tight_layout(rect=(0, 0.01, 1, 0.97))
    fig.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(fig)
