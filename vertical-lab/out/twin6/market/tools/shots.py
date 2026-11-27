"""Crop chosen screenshots to the listing (title, photo, price, condition), leaving out seller contact panels.

    python3 shots.py <out dir>        # writes <out dir>/shots/*.jpg
"""
import sys
from pathlib import Path
from PIL import Image

S = "/tmp/market/shots"
PICK = [  # (source file, crop box (left, top, right, bottom), output name, what it shows)
    (f"{S}/detail/labx_690003580.jpg", (260, 140, 1645, 860), "icpms_agilent7850_refurbished_labx.jpg",
     "the twin's own ICP-MS model, refurbished with a 90-day warranty, $100,000 (Texas); refurbished 7800 and 7900 alongside"),
    (f"{S}/detail/machineseeker_360035035.jpg", (380, 110, 1525, 835), "edm_robocut_c400ic_2024_machineseeker.jpg",
     "the twin's own wire EDM model, a 2024 FANUC ROBOCUT a-C400iC, EUR 89,000 FCA (Slovakia)"),
    (f"{S}/detail/dotmed_424702650.jpg", (230, 290, 1310, 860), "icpms_agilent7850_asis_dotmed.jpg",
     "an Agilent 7850 sold as-is by a US dealer, $90,000 (New Hampshire)"),
    (f"{S}/test_ebay.png", (370, 30, 1570, 670), "blocked_ebay.jpg",
     "eBay's answer to the first request through the lab Pi: an HTTP 403 block page; eBay was left alone"),
    (f"{S}/newlead_haas.png", (60, 0, 1080, 600), "new_haas_st10_lead.jpg",
     "Haas's ST-10 page on 27 Nov 2026: $64,995, 16 available, one week, built to order"),
]


def main(out):
    o = Path(out) / "shots"
    o.mkdir(parents=True, exist_ok=True)
    rows = []
    for src, box, name, what in PICK:
        im = Image.open(src).convert("RGB")
        w, h = im.size
        box = (max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3]))
        im.crop(box).save(o / name, quality=72, optimize=True)
        rows.append((name, what))
    with open(o / "README.md", "w") as fh:
        fh.write("# Representative listings\n\nScreenshots taken by the survey's browsers on 27 Nov 2026, cropped to "
                 "the listing (seller contact panels left out).\n\n")
        for name, what in rows:
            fh.write(f"- [`{name}`]({name}): {what}\n")
    # listings.csv: the shot column names a committed screenshot, or is empty (the rest stayed in /tmp)
    lp = Path(out) / "listings.csv"
    if lp.exists():
        import csv
        src2name = {src: name for src, _, name, _ in PICK}
        with open(lp, newline="") as fh:
            L = list(csv.DictReader(fh))
        for r in L:
            r["shot"] = ("shots/" + src2name[r["shot"]]) if r.get("shot") in src2name else ""
        with open(lp, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(L[0].keys()))
            w.writeheader()
            w.writerows(L)
    print(len(rows), "shots")


if __name__ == "__main__":
    main(sys.argv[1])
