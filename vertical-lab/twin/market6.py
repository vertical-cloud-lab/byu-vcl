"""Round 6's used-equipment market: what the listings say about each station, in the twin's units.

    python3 -m twin.market6            # out/twin6/market/{listings.csv,new.csv} -> summary.csv, summary.json
    from twin import market6; m = market6.load()      # station key -> dict, the columns of summary.csv

Round 5 (``twin/round5.py``) bought a station used when ``USED_OK`` named it, with one set of stand-ins for every
station (``USED``: ships 2 weeks after the purchase order, 45 % of the new price, 1 in 4 faulty, 6 weeks and 15 % of
the new price to put right, a week more commissioning). This module replaces those with each station's own figures,
read from ``out/twin6/market/listings.csv`` (issue #424: LabX, Machinio, Machineseeker, Exapro, GovDeals, AllSurplus,
Public Surplus, DOTmed, Federal Equipment and Marshall Scientific, read through the lab Pi on 2026-11-27; eBay,
BidSpotter, EquipNet and Surplus Record blocked or challenged the browser and are not in it).

What is measured and what is assumed:

* **Measured** (from the listings): how many listings fit each station's role and where they are, the asking prices
  (median and quartiles, in USD at the ECB's 17 Nov 2026 rates), the mix of conditions (as-is, used, tested,
  refurbished, warranty), stated availability and delivery terms.
* **Assumed** (constants below, each marked): what freight and rigging cost by shipping class and distance
  (``FREIGHT``), how long handling, transit and rigging take (``LEAD``), the chance a unit of each condition arrives
  faulty or needs refurbishment (``P_FAULT``), and how long and how much the refurbishment takes (``REFURB``), where
  the listings don't give a refurbished-against-as-is price difference.

Units are the twin's: weeks, fractions of the twin's new price (``twin/econ.py``), probabilities. ``lead_w`` is, as in
round 5, the time from BYU's purchase order (``round4.PO_W`` = 2 weeks, not included) to the unit on site.
"""
from __future__ import annotations

import csv
import json
import math
import statistics as stats
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "out" / "twin6" / "market"

# ------------------------------------------------------------------------------------------------- assumptions
# Freight and rigging, USD, by the station's shipping class (stations.py's ``wt``) and where the unit is: North
# America (scaled by distance from Provo, UT where the listing gives it) or overseas (export crating, ocean or air,
# customs broker, inland delivery). Anchors: LTL at $0.22-0.42 a pound (Red Stag Fulfillment, 2025,
# https://redstagfulfillment.com/what-is-average-cost-per-pound-ltl-shipping/), a cross-country pallet $350-600
# (https://www.wearewarp.com/how-much-does-ltl-shipping-cost), freight, rigging and set-up at 5-20 % over a CNC
# machine's price (https://encycam.com/articles/how-much-does-a-cnc-machine-cost-a-practical-2025-price-guide-for-cnc-programmers/).
# Air-ride, white-glove delivery for sensitive instruments is quote-only; the multipliers on LTL are ours.
FREIGHT = {  # class: (North America, overseas, what it covers)
    "parcel": (150, 600, "parcel or a small pallet"),
    "bench": (500, 2_500, "LTL pallet with liftgate; air freight and broker from overseas"),
    "bench_sens": (2_500, 6_000, "air-ride, white-glove, inside delivery (vacuum instruments, X-ray sources)"),
    "bench_heavy": (900, 3_500, "LTL pallet with liftgate, 100-300 kg"),
    "floor": (2_500, 8_000, "crated, LTL or air-ride, riggers into the lab"),
    "floor_sens": (5_000, 12_000, "air-ride, white-glove, riggers into the lab, chiller and gas fittings"),
    "floor_heavy": (6_000, 14_000, "1-2 t frame: riggers out, air-ride, riggers in"),
    "machine": (9_000, 22_000, "2-5 t machine: riggers out, flatbed or air-ride, riggers in; overseas a container"),
    "machine_light": (1_000, 3_500, "a crated robot or AMR, 100-300 kg"),
    "vlm": (45_000, 70_000, "a 9 m VLM taken down, trucked in pieces and re-erected by certified fitters"),
}
FREIGHT_SRC = "estimates anchored on LTL rates and machine-moving guides (see the comment above FREIGHT)"

# Lead, weeks after the purchase order: the seller's handling, transit and rigging, by seller kind and region.
LEAD = {
    "handling": {"dealer": 1.0, "refurbisher": 2.0, "auction": 2.0, "broker": 1.5},
    "transit": {"NA": 1.0, "overseas": 6.0},           # LTL or air-ride across the US; ocean, customs and inland
    "rigging": {"parcel": 0.0, "bench": 0.0, "bench_sens": 0.5, "bench_heavy": 0.0, "floor": 0.5, "floor_sens": 0.5,
                "floor_heavy": 1.0, "machine": 1.0, "machine_light": 0.0, "vlm": 2.0},
}
LEAD_SRC = ("assumed: a week for a dealer to crate and release, two for a refurbisher or an auction's close and "
            "removal window; a week across the US, six from overseas (ocean, customs, inland); riggers booked a week "
            "ahead for machines")
# Commissioning a used unit beyond what a new one needs: the maker's or a service engineer's check, calibration,
# software licence transfer. Weeks.
EXTRA_COM = {"parcel": 0.0, "bench": 0.5, "bench_sens": 1.5, "bench_heavy": 0.5, "floor": 1.0, "floor_sens": 2.0,
             "floor_heavy": 1.5, "machine": 2.0, "machine_light": 1.0, "vlm": 2.0}
EXTRA_COM_LPBF_DED = 6.0      # an LPBF or DED machine's recommissioning and requalification by the maker, assumed
EXTRA_COM_SRC = ("assumed: half a week for a bench tool, 1.5-2 for vacuum and X-ray instruments and machines (a "
                 "service engineer's visit, calibration, licence transfer), 6 for LPBF and DED (the maker's "
                 "recommissioning and parameter requalification)")
# The chance a unit arrives faulty or needs refurbishment, by the listing's condition. Stand-ins: no failure-rate
# data for used lab equipment was found. The listings' mix of conditions is measured; these are not.
P_FAULT = {"refurbished_warranty": 0.05, "warranty": 0.10, "refurbished": 0.10, "new_surplus": 0.10, "tested": 0.20,
           "used": 0.30, "as_is_tested": 0.35, "as_is": 0.50}
P_FAULT_SRC = ("assumed per condition (1 in 20 refurbished with a warranty, 1 in 10 refurbished or warranted, 1 in 5 "
               "tested, 3 in 10 'used' with nothing said, 1 in 2 as-is); weighted by each station's listings")
# Refurbishment if it is faulty: weeks, and cost as a fraction of the new price, by class. Replaced by the listings'
# own refurbished-against-as-is difference where both have at least two priced listings.
REFURB = {"parcel": (2.0, 0.10), "bench": (3.0, 0.10), "bench_sens": (6.0, 0.15), "bench_heavy": (3.0, 0.10),
          "floor": (4.0, 0.10), "floor_sens": (8.0, 0.15), "floor_heavy": (6.0, 0.10), "machine": (6.0, 0.10),
          "machine_light": (4.0, 0.10), "vlm": (6.0, 0.10)}
REFURB_SIGMA = 0.4
REFURB_SRC = ("assumed by class: 3 weeks and 10 % of new for bench tools, 6-8 weeks and 15 % for vacuum and X-ray "
              "instruments (a source, a pump, a detector), 6 weeks and 10 % for machines")
# A real used market: at least MARKET_MIN listings that fit the role, at least MARKET_NA_MIN of them in North
# America, and at least one with a price.
MARKET_MIN, MARKET_NA_MIN = 5, 2
PO_W = 2.0                    # BYU's purchase order, round4.PO_W: before the lead, used or new
LFL_REQUIRED = {"shuttle", "midi", "mxlab", "repowder", "pip", "couplings", "doser:press", "units:mir", "units:arm", "units:gripper",
                "floor_unit:mir", "floor_unit:arm", "floor_unit:gripper", "machining:robot_arm"}
# ^ stations and components whose integration depends on the model (tray geometry, an open LPBF or DED machine, the
#   robots' programs and tooling): priced and judged on like-for-like listings only. Elsewhere another maker's
#   instrument that does the job counts.
INSTRUMENTS = {"sem", "eds", "ebsd", "xrd", "xrf", "mastersizer", "nanoindenter", "icpms", "vhx", "hardness"}
# ^ measuring instruments: the same maker's generation first (an older or manual one measures, but not always as the
#   automated lab needs), then any maker's in North America. Generic tools (furnaces, hoods, gloveboxes, prep, frames,
#   sieve shakers, the EDM and lathe) are priced on what can be trucked in first.
LFL_MIN = 3                   # priced like-for-like listings (the twin's model or its maker's line) needed to price on
                              # those alone; otherwise every listing that fits the role is used
LEAD_SIGMA_MIN = 0.25         # round 4's new-item spread, the floor for a used one


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _q(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def read_csv(p):
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh))


def seller_kind(r):
    s = (r.get("seller_type") or "").lower()
    if "auction" in s or "bid" in (r.get("price_kind") or ""):
        return "auction"
    if "refurbisher" in s or r.get("condition", "").startswith("refurbished"):
        return "refurbisher"
    if "broker" in s:
        return "broker"
    return "dealer"


def freight(wt, region, dist_km):
    na, ov, _ = FREIGHT[wt]
    if region == "overseas":
        return ov
    if dist_km:
        scale = 0.7 if dist_km < 1000 else 1.0 if dist_km < 2500 else 1.25
        return round(na * scale)
    return na


def lead_of(r, wt):
    reg = "overseas" if r.get("region") == "overseas" else "NA"
    return LEAD["handling"][seller_kind(r)] + LEAD["transit"][reg] + LEAD["rigging"][wt]


PLAUSIBLE = (0.02, 1.5)        # a price under 2 % or over 150 % of new is a part, a placeholder or a bundle: listed,
                              # but not in the price statistics


def in_stats(r, new_usd) -> bool:
    """Whether a listing's price counts: an asking, sold or starting price (not a running auction's current bid), not
    for parts, and plausible against the new price."""
    p = _f(r.get("price_usd"))
    if not p or r.get("price_kind") not in ("asking", "sold", "starting bid") or r.get("condition") == "parts":
        return False
    if new_usd and not (PLAUSIBLE[0] * new_usd <= p <= PLAUSIBLE[1] * new_usd):
        return False
    return True


def summarize(listings, new):
    """Per station (and per component where the station is several machines)."""
    by = defaultdict(list)
    for r in listings:
        if r.get("keep", "1") in ("0", "false", "False"):
            continue
        by[(r["station"], r.get("component") or "")].append(r)
    out = {}
    for n in new:
        key, comp = n["station"], n.get("component") or ""
        wt = n["wt"]
        new_usd = _f(n["new_usd_each"])
        rows = [r for r in by.get((key, comp), []) if r["condition"] != "parts"]
        if n.get("pool"):                       # a component that shares its listings with another station's
            for pk in n["pool"].split("+"):
                ps, pc = (pk.split(":") + [""])[:2]
                rows += [r for r in by.get((ps, pc), []) if r["condition"] != "parts"]
        na = [r for r in rows if r.get("region") in ("US", "CA")]
        priced = [r for r in rows if in_stats(r, new_usd)]
        bids = [r for r in rows if _f(r.get("price_usd")) and r.get("price_kind") == "current bid"]
        px = [_f(r["price_usd"]) for r in priced]
        pxf = [_f(r["price_usd"]) for r in priced if r["match"] in ("exact", "family")]
        med = _q(px, 0.5)
        lfl = [r for r in priced if r["match"] in ("exact", "family")]
        lfl_only = key in LFL_REQUIRED or f"{key}:{comp}" in LFL_REQUIRED
        lfl_na = [r for r in lfl if r.get("region") in ("US", "CA")]
        any_na = [r for r in priced if r.get("region") in ("US", "CA")]
        if lfl_only:
            chain = (("like-for-like in North America", lfl_na), ("like-for-like", lfl))
        elif key in INSTRUMENTS:
            chain = (("like-for-like in North America", lfl_na), ("like-for-like", lfl), ("North America", any_na))
        else:
            chain = (("like-for-like in North America", lfl_na), ("North America", any_na), ("like-for-like", lfl))
        price_basis, basis_rows = "", []
        pool = lfl if lfl_only else priced
        if pool:
            price_basis, basis_rows = ("like-for-like" if lfl_only else "all that fit"), pool
            for name, cand in chain:
                if len(cand) >= LFL_MIN:
                    price_basis, basis_rows = name, cand
                    break
            price_basis = f"{price_basis} ({len(basis_rows)} priced)"
        med_basis = _q([_f(r["price_usd"]) for r in basis_rows], 0.5) if basis_rows else None
        cond = Counter(r["condition"] for r in rows)
        nfit = len(rows)
        base = [r for r in rows if r["match"] in ("exact", "family")] if lfl_only else rows
        base_na = [r for r in base if r.get("region") in ("US", "CA")]
        buy = base_na if len(base_na) >= MARKET_NA_MIN else base   # where the lab would buy: at home if it can
        pf = (sum(P_FAULT.get(r["condition"], 0.3) for r in buy) / len(buy)) if buy else None
        # best: the lowest-risk listing where it would buy, at no more than 1.5 x the median price (or any, if unpriced)
        best = [r for r in buy if not med or not _f(r.get("price_usd")) or _f(r["price_usd"]) <= 1.5 * med]
        pf_best = min((P_FAULT.get(r["condition"], 0.3) for r in best), default=None)
        leads = [lead_of(r, wt) for r in buy]
        ships = [LEAD["handling"][seller_kind(r)] + LEAD["transit"]["overseas" if r.get("region") == "overseas" else "NA"]
                 for r in buy]
        lead_w = _q(leads, 0.5) if leads else None
        lead_sigma = None
        if leads:
            ll = [math.log(x) for x in leads if x > 0]
            lead_sigma = max(LEAD_SIGMA_MIN, stats.pstdev(ll)) if len(ll) >= 3 else LEAD_SIGMA_MIN
        rw, rf = REFURB[wt]
        rf_src = "class"
        ref_p = [_f(r["price_usd"]) for r in priced if r["condition"].startswith("refurbished") or r["condition"] == "warranty"]
        asis_p = [_f(r["price_usd"]) for r in priced if r["condition"] in ("as_is", "as_is_tested", "used")]
        if len(ref_p) >= 2 and len(asis_p) >= 2 and new_usd:
            d = (_q(ref_p, 0.5) - _q(asis_p, 0.5)) / new_usd
            if 0 < d < 0.6:
                rf, rf_src = round(d, 3), f"listings: refurbished median - as-is/used median ({len(ref_p)} vs {len(asis_p)})"
        extra = EXTRA_COM[wt] + (EXTRA_COM_LPBF_DED - EXTRA_COM[wt] if key in ("midi", "mxlab") else 0.0)
        market = ("yes" if nfit >= MARKET_MIN and len(na) >= MARKET_NA_MIN and priced else
                  "thin" if nfit >= 1 else "none")
        lrows = [r for r in rows if r["match"] in ("exact", "family")]
        lna = [r for r in lrows if r.get("region") in ("US", "CA")]
        market_lfl = ("yes" if len(lrows) >= MARKET_MIN and len(lna) >= MARKET_NA_MIN and lfl else
                      "thin" if lrows else "none")
        if lfl_only:
            market = market_lfl
        if n.get("used_market") == "no":
            market = "n/a (new only)"
        if med_basis:
            if buy is base_na and base_na:
                fr = freight(wt, "NA", _q([_f(r.get("dist_km")) for r in base_na if _f(r.get("dist_km"))], 0.5))
            else:
                regs = Counter("overseas" if r.get("region") == "overseas" else "NA" for r in basis_rows)
                fr = freight(wt, regs.most_common(1)[0][0], None)
            dmed = med_basis + fr
        else:
            fr, dmed = None, None
        tl, ti, tc = _f(n.get("twin_lead_w")), _f(n.get("twin_install_w")) or 0.0, _f(n.get("twin_com_w")) or 0.0
        otw = (PO_W + lead_w + (pf or 0) * rw + ti + tc + extra) if lead_w is not None else None
        otw_new = (tl + ti + tc) if tl else None
        rec = dict(
            lab=n.get("lab", ""), station=key, component=comp, item=n["item"], qty=int(n["qty"]), wt=wt,
            new_usd_each=new_usd,
            new_source=n.get("new_source", ""), new_lead_w_vendor=_f(n.get("vendor_lead_w")),
            new_lead_text=n.get("vendor_lead_text", ""), twin_lead_w=_f(n.get("twin_lead_w")),
            n_listings=nfit, n_north_america=len(na), n_priced=len(priced), n_current_bids=len(bids),
            n_exact=sum(r["match"] == "exact" for r in rows), n_family=sum(r["match"] == "family" for r in rows),
            n_substitute=sum(r["match"] == "sub" for r in rows),
            median_used_usd=round(med) if med else None, median_basis_usd=round(med_basis) if med_basis else None,
            bought_from=("North America" if buy is base_na and base_na else "anywhere") if buy else "",
            median_exact_family_usd=round(_q(pxf, 0.5)) if pxf else None, n_priced_exact_family=len(pxf),
            p25_used_usd=round(_q(px, 0.25)) if px else None,
            p75_used_usd=round(_q(px, 0.75)) if px else None, min_used_usd=round(min(px)) if px else None,
            max_used_usd=round(max(px)) if px else None,
            median_bid_usd=round(_q([_f(r["price_usd"]) for r in bids], 0.5)) if bids else None,
            discount_vs_new=round(1 - med_basis / new_usd, 3) if (med_basis and new_usd) else None,
            discount_vs_new_all=round(1 - med / new_usd, 3) if (med and new_usd) else None,
            freight_rigging_usd=fr, median_delivered_usd=round(dmed) if dmed else None,
            priced_on_like_for_like_only=lfl_only,
            price_frac=round(dmed / new_usd, 3) if (dmed and new_usd) else None, price_basis=price_basis,
            market_like_for_like=market_lfl if n.get("used_market") != "no" else "n/a (new only)",
            lead_w=round(lead_w, 2) if lead_w is not None else None,
            lead_sigma=round(lead_sigma, 3) if lead_sigma is not None else None,
            p_fault=round(pf, 3) if pf is not None else None, p_fault_best=pf_best,
            refurb_w=rw, refurb_sigma=REFURB_SIGMA, refurb_frac=rf, refurb_source=rf_src, extra_com_w=extra,
            ship_w=round(_q(ships, 0.5), 2) if ships else None, rigging_w=LEAD["rigging"][wt],
            refurb_expected_w=round((pf or 0) * rw, 2) if pf is not None else None, checkout_w=extra,
            order_to_working_used_w=round(otw, 1) if otw is not None else None,
            order_to_working_new_w=round(otw_new, 1) if otw_new is not None else None,
            share_as_is=round((cond["as_is"] + cond["as_is_tested"]) / nfit, 3) if nfit else None,
            share_used=round(cond["used"] / nfit, 3) if nfit else None,
            share_tested=round(cond["tested"] / nfit, 3) if nfit else None,
            share_refurb_or_warranty=round((cond["refurbished"] + cond["refurbished_warranty"] + cond["warranty"])
                                           / nfit, 3) if nfit else None,
            share_new_surplus=round(cond["new_surplus"] / nfit, 3) if nfit else None,
            market=market, note=n.get("note", ""))
        out[(key, comp)] = rec
    return out


def station_rows(comp_rows, new):
    """One row per station key: components combined. A component with a real used market is bought used at its
    delivered median; the rest new. Leads and risks are those of the used components, weighted by new price."""
    by = defaultdict(list)
    for (k, c), r in comp_rows.items():
        by[k].append(r)
    res = {}
    for k, rs in by.items():
        if len(rs) == 1 and not rs[0]["component"]:
            r = dict(rs[0])
            r["used_ok"] = r["market"] == "yes" and r["price_frac"] is not None and r["price_frac"] < 1.0
            res[k] = r
            continue
        tot_new = sum(r["new_usd_each"] for r in rs)
        used = [r for r in rs if r["market"] == "yes" and r["price_frac"] is not None and r["price_frac"] < 1.0]
        paid = sum((r["median_delivered_usd"] if r in used else r["new_usd_each"]) for r in rs)
        wsum = sum(r["new_usd_each"] for r in used) or 1.0
        avg = lambda f: (round(sum(r[f] * r["new_usd_each"] for r in used if r[f] is not None) / wsum, 3)
                         if used else None)
        slow_new = [r for r in rs if r not in used and (r.get("twin_lead_w") or 0) > 0 and r["component"] != "install"]
        new_parts_lead = max(((r.get("twin_lead_w") or 0) - PO_W for r in slow_new), default=None)
        used_lead = max((r["lead_w"] for r in used if r["lead_w"] is not None), default=None)
        r0 = dict(lab=rs[0].get("lab", ""), station=k, component="(station)", item=" + ".join(r["component"] for r in rs),
                  twin_lead_w=rs[0].get("twin_lead_w"),
                  qty=rs[0]["qty"], wt=rs[0]["wt"], new_usd_each=tot_new, new_source="sum of the components",
                  n_listings=sum(r["n_listings"] for r in rs), n_north_america=sum(r["n_north_america"] for r in rs),
                  n_priced=sum(r["n_priced"] for r in rs), price_frac=round(paid / tot_new, 3) if used else None,
                  discount_vs_new=round(1 - paid / tot_new, 3) if used else None,
                  lead_w=used_lead,
                  new_parts_lead_w=new_parts_lead,
                  lead_w_with_new_parts=(max(used_lead, new_parts_lead) if (used_lead is not None and
                                         new_parts_lead is not None) else used_lead),
                  lead_sigma=max((r["lead_sigma"] for r in used if r["lead_sigma"] is not None), default=None),
                  p_fault=round(1 - math.prod(1 - (r["p_fault"] or 0) for r in used), 3) if used else None,
                  refurb_w=max((r["refurb_w"] for r in used), default=None), refurb_sigma=REFURB_SIGMA,
                  refurb_frac=avg("refurb_frac"), extra_com_w=max((r["extra_com_w"] for r in used), default=None),
                  market=("yes (" + ", ".join(r["component"] for r in used) + ")") if used else
                  ("thin" if any(r["n_listings"] for r in rs) else "none"),
                  used_ok=bool(used), share_of_new_bought_used=round(wsum / tot_new, 3) if used else 0.0,
                  order_to_working_used_w=max((r["order_to_working_used_w"] for r in used
                                               if r.get("order_to_working_used_w") is not None), default=None),
                  order_to_working_new_w=rs[0].get("order_to_working_new_w"),
                  note=("components: " + "; ".join(f"{r['component']} {r['market']}" for r in rs) +
                        ("; the parts bought new still set the station's lead" if used and slow_new else "")))
        res[k] = r0
    return res


COLS = ["lab", "station", "component", "item", "qty", "new_usd_each", "new_lead_w_vendor", "new_lead_text", "twin_lead_w",
        "market", "market_like_for_like", "used_ok", "n_listings", "n_north_america", "n_priced", "n_current_bids", "n_exact", "n_family",
        "n_substitute", "median_used_usd", "median_exact_family_usd", "n_priced_exact_family", "price_basis", "median_basis_usd", "bought_from", "p25_used_usd", "p75_used_usd", "min_used_usd", "max_used_usd",
        "median_bid_usd", "discount_vs_new", "discount_vs_new_all", "freight_rigging_usd", "median_delivered_usd", "price_frac", "lead_w",
        "lead_sigma", "new_parts_lead_w", "lead_w_with_new_parts", "ship_w", "rigging_w", "refurb_expected_w", "checkout_w", "p_fault", "p_fault_best", "refurb_w", "refurb_sigma", "refurb_frac", "refurb_source",
        "extra_com_w", "order_to_working_used_w", "order_to_working_new_w", "share_as_is", "share_used", "share_tested", "share_refurb_or_warranty", "share_new_surplus",
        "share_of_new_bought_used", "wt", "new_source", "note"]


def build(out=OUT):
    listings = read_csv(out / "listings.csv")
    new = read_csv(out / "new.csv")
    comp = summarize(listings, new)
    st = station_rows(comp, new)
    rows = []
    for (k, c), r in sorted(comp.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        if c:
            rows.append(r)
    for k, r in sorted(st.items()):
        rows.append(r)
    rows.sort(key=lambda r: (r["station"], r["component"] not in ("", "(station)"), r["component"]))
    with open(out / "summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in COLS})
    meta = dict(source="out/twin6/market/listings.csv and new.csv; twin/market6.py", freight=FREIGHT,
                freight_source=FREIGHT_SRC, lead=LEAD, lead_source=LEAD_SRC, extra_com=EXTRA_COM,
                extra_com_lpbf_ded=EXTRA_COM_LPBF_DED, extra_com_source=EXTRA_COM_SRC, p_fault=P_FAULT,
                p_fault_source=P_FAULT_SRC, refurb=REFURB, refurb_sigma=REFURB_SIGMA, refurb_source=REFURB_SRC,
                market_rule=f">= {MARKET_MIN} listings that fit, >= {MARKET_NA_MIN} in North America, >= 1 priced",
                plausible_price=dict(low=PLAUSIBLE[0], high=PLAUSIBLE[1], of="the twin's new price"),
                stations={k: v for k, v in st.items()},
                components={f"{k}:{c}": v for (k, c), v in comp.items() if c})
    (out / "summary.json").write_text(json.dumps(meta, indent=1, default=str) + "\n")
    return st


def load(out=OUT) -> dict:
    """summary.csv's station rows (one per twin key), numbers as floats, for round 6."""
    res = {}
    for r in read_csv(out / "summary.csv"):
        if r["component"] not in ("", "(station)"):
            continue
        d = {}
        for k, v in r.items():
            f = _f(v)
            d[k] = f if (f is not None and k not in ("station", "component", "item", "market", "note", "wt")) else v
        d["used_ok"] = r.get("used_ok") in ("True", "true", "1")
        res[r["station"]] = d
    return res


ROUND5_USED = dict(lead_w=2.0, lead_sigma=0.35, price_frac=0.45, p_fault=0.25, refurb_w=6.0, refurb_sigma=0.4,
                   refurb_frac=0.15, extra_com_w=1.0)     # round5.USED's stand-ins, the fallback for a missing value


def used_params(key: str, m: dict | None = None) -> dict:
    """Round 5's ``USED`` for one station, from the market: ``ok`` (buy used at all: a real used market at a saving)
    and the eight values round 5 reads. For a station bought partly used, ``lead_w`` is the later of its used parts'
    lead and its new parts' lead. A value the market doesn't give falls back to round 5's stand-in, named in
    ``fallback``."""
    m = m if m is not None else load()
    r = m.get(key)
    out, fb = {}, []
    for k, v in ROUND5_USED.items():
        x = r.get(k) if r else None
        if k == "lead_w" and r and isinstance(r.get("lead_w_with_new_parts"), float):
            x = r["lead_w_with_new_parts"]          # a station bought partly used waits for its new parts too
        if isinstance(x, float) and not math.isnan(x):
            out[k] = x
        else:
            out[k] = v
            fb.append(k)
    out["ok"] = bool(r and r.get("used_ok"))
    out["fallback"] = fb
    out["market"] = r.get("market") if r else "none"
    return out


if __name__ == "__main__":
    st = build()
    for k, r in sorted(st.items()):
        print(f"{k:13s} {str(r.get('market')):28s} n={r.get('n_listings'):>3} priced={r.get('n_priced'):>3} "
              f"price_frac={r.get('price_frac')} lead_w={r.get('lead_w')} p_fault={r.get('p_fault')}")
