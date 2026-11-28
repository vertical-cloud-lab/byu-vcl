#!/usr/bin/env python3
"""Read a MakerWorld model's license and print profiles from MakerWorld's public design API, and
table each profile's grams, cost and time against the toy drive's limits.

    python makerworld_profiles.py 1366309 > rexagon.json      # the Articulated Rexagon

MakerWorld's model pages sit behind a Cloudflare challenge, from the runner and from the lab's
Pis alike, but ``/api/v1/design-service/design/<id>`` answers without one. It gives only the
designer's own numbers for the printer each profile was made for. The model files themselves
need a signed-in Bambu account ("Please log in to download models"), so this script doesn't
fetch them, and nothing here slices them.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.request

API = "https://makerworld.com/api/v1/design-service/design/{}"
LIMITS = {"grams": 250, "usd": 4.00, "hours": 8}


def hms(seconds: int) -> str:
    h, rem = divmod(int(seconds), 3600)
    return f"{h} h {rem // 60:02d} min"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("design_id", type=int)
    ap.add_argument("--usd-per-kg", type=float, default=18.99)
    args = ap.parse_args()
    req = urllib.request.Request(API.format(args.design_id),
                                 headers={"user-agent": "Mozilla/5.0", "accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    profiles = []
    for inst in d["instances"]:
        info = inst["extention"]["modelInfo"]
        grams, seconds = float(inst["weight"]), int(inst["prediction"])
        usd = round(grams * args.usd_per_kg / 1000, 2)
        profiles.append({
            "instance_id": inst["id"], "title": inst["title"], "by": inst["instanceCreator"]["name"],
            "made_for": info["compatibility"]["devProductName"],
            "nozzle_mm": info["compatibility"]["nozzleDiameter"],
            "also_compatible": [c["devProductName"] for c in info.get("otherCompatibility") or []],
            "settings": info.get("projectSettings"),
            "needs_ams": inst["needAms"],
            "filaments": [{"type": f["type"], "colour": f["color"], "g": float(f["usedG"])}
                          for f in inst["instanceFilaments"]],
            "plates": len(info.get("plates") or []),
            "filament_g": grams, "cost_usd": usd, "usd_per_kg": args.usd_per_kg,
            "prediction_s": seconds, "print_time": hms(seconds),
            "over_limits": [k for k, ok in (("grams", grams <= LIMITS["grams"]), ("usd", usd <= LIMITS["usd"]),
                                            ("hours", seconds <= LIMITS["hours"] * 3600)) if not ok],
            "makerworld_prints": inst["printCount"], "makerworld_downloads": inst["downloadCount"],
        })
    out = {
        "read_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": API.format(args.design_id),
        "design_id": d["id"], "title": d["title"],
        "model_url": f"https://makerworld.com/en/models/{d['id']}-{d['slug']}",
        "designer": d["designCreator"]["name"],
        "designer_url": f"https://makerworld.com/en/@{d['designCreator']['handle']}",
        "license": d["license"], "license_text": (d.get("licenseDescriptionInfo") or {}).get("content"),
        "makerworld_exclusive": d.get("isExclusive"),
        "published_utc": d["createTime"],
        "counts": {k: d[k] for k in ("printCount", "downloadCount", "likeCount", "collectionCount")},
        "model_files": [f["modelName"] for f in d["designExtension"].get("model_files", [])],
        "profiles": profiles,
    }
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
