#!/usr/bin/env python3
"""Answer two questions from the committed runs, with every denominator named.

1. Are readings more accurate with the OT-2 rail lights on or off?
2. What would removing the green glow inside the enclosure actually buy?

Both are decided by the same quantity, so it is defined once here and used
throughout:

    counts        the AS7341's raw ADC output for one channel, 0 .. 65535.
                  Never a percentage. All eight summed is a reading's "total".

    share s_i     ch_i divided by the total of that SAME reading, x100.
                  Units: percent OF THAT ONE READING'S TOTAL COUNTS.
                  This is what "colour" means for this sensor -- it is the
                  only quantity that survives the brightness of the room.

    resolution    2 x the standard deviation of s_i over the repeat reads at
    floor         one position, in PERCENTAGE POINTS OF SHARE. A sample that
                  moves a channel's share by less than this cannot be told
                  apart from doing nothing at all.

"Accuracy" for a colour test is the resolution floor: the smallest colour
difference the instrument can resolve. Everything else is bookkeeping.

    python3 analyse_lights_and_offset.py
"""
from __future__ import annotations

import glob
import json
import os
import statistics as st
import sys

CH = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
NM = [410, 440, 470, 510, 550, 583, 620, 670]
HERE = os.path.dirname(os.path.abspath(__file__))
FULL_SCALE = 65535  # AS7341 ADC, 16 bit


def load(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


def sealed_reads(d):
    """Reads taken with the module closed on its base.

    A reseat-confirm above 800 counts means the release failed and the module
    is still on the nozzle, so it is not a sealed read at all -- that is what
    happened at the end of the lights-off run on 2026-09-10.
    """
    out = []
    for r in d.get("readings", []):
        lab = r["label"]
        if lab.startswith(("seated-baseline", "background-baseline")):
            out.append(r)
        elif lab.startswith("reseat-confirm") and r["total"] < 800:
            out.append(r)
    return out


def scan_positions(d):
    """{position label: [readings]} for the reads taken over the slot."""
    pos = {}
    for r in d.get("readings", []):
        lab = r["label"]
        if lab.startswith("pos"):
            pos.setdefault(lab.rsplit("-", 1)[0], []).append(r)
    return pos


def mean_vec(rs):
    return {c: st.mean(r["channels"][c] for r in rs) for c in CH}


def shares(vec, offset=None):
    """Channel shares, in percent of the reading's own total counts."""
    v = {c: vec[c] - (offset[c] if offset else 0.0) for c in CH}
    tot = sum(v.values())
    return {c: 100.0 * v[c] / tot for c in CH}


def rule(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def main():
    on = load("background-lightson-2026-09-10.json")
    off = load("background-lightsoff-2026-09-10.json")
    on_off = {"rail lights ON": on, "rail lights OFF": off}

    # -- 1. the sealed offset, split into what the room controls and what it does not
    rule("1. What is inside the closed box, and how much of it is the room?")
    von, voff = mean_vec(sealed_reads(on)), mean_vec(sealed_reads(off))
    print("Module closed on its base, same enclosure, four minutes apart.")
    print("Everything below is COUNTS.\n")
    print(f"  {'ch':>6} {'sealed, rails ON':>17} {'sealed, rails OFF':>18} "
          f"{'difference':>11} {'= rails, as % of the ON value':>31}")
    for c in CH:
        d = von[c] - voff[c]
        print(f"  {c:>6} {von[c]:17.1f} {voff[c]:18.1f} {d:11.1f} {100 * d / von[c]:30.1f}%")
    ton, toff = sum(von.values()), sum(voff.values())
    print(f"  {'total':>6} {ton:17.1f} {toff:18.1f} {ton - toff:11.1f} "
          f"{100 * (ton - toff) / ton:30.1f}%")

    # -- 2. the same offset across every condition on record
    rule("2. Which part of that offset is a lamp, and which part is leaked room light?")
    conds = []
    for f in sorted(glob.glob(os.path.join(HERE, "xscan-*.json"))) + \
             sorted(glob.glob(os.path.join(HERE, "background-*.json"))):
        d = json.load(open(f))
        rs = sealed_reads(d)
        if rs:
            conds.append((os.path.basename(f), len(rs), mean_vec(rs)))
    print(f"{len(conds)} sealed conditions: two rooms, rails on and off, ~24 h apart.")
    print("A self-emitting lamp inside the box does not care what the room does;")
    print("light leaking in does. So the channels that hold still are the lamp.\n")
    print(f"  {'ch':>6} {'lowest seen':>12} {'highest seen':>13} {'swing':>8} "
          f"{'swing as % of the lowest':>26}")
    lamp = {}
    for c in CH:
        lo = min(v[c] for _, _, v in conds)
        hi = max(v[c] for _, _, v in conds)
        lamp[c] = lo
        print(f"  {c:>6} {lo:12.1f} {hi:13.1f} {hi - lo:8.1f} {100 * (hi - lo) / lo:25.0f}%")
    green = lamp["ch510"] + lamp["ch550"]
    floor = sum(lamp.values())
    print(f"\n  ch510 + ch550 hold to 5%; every other channel swings 29-126%.")
    print(f"  green core (510+550) ....... {green:6.1f} counts")
    print(f"  darkest sealed total ....... {floor:6.1f} counts")
    print(f"  green core is {100 * green / floor:.0f}% of the darkest sealed reading.")
    print(f"  {100 * floor / FULL_SCALE:.2f}% of the AS7341's full scale ({FULL_SCALE}).")

    # -- 3. lights on vs off: signal, repeatability, resolution floor
    rule("3. Rail lights on or off: which gives the more accurate colour?")
    summary = {}
    for name, d in on_off.items():
        offset = mean_vec(sealed_reads(d))
        rows = []
        for lab, rs in sorted(scan_positions(d).items()):
            tots = [r["total"] for r in rs]
            mean_tot = st.mean(tots)
            spread = 100.0 * (max(tots) - min(tots)) / mean_tot
            per = [shares(r["channels"], offset) for r in rs]
            sds = {c: (st.stdev([p[c] for p in per]) if len(per) > 1 else 0.0) for c in CH}
            worst = max(sds.values())
            rows.append({"label": lab, "mean_total": mean_tot, "spread_pct": spread,
                         "floor_pts": 2 * worst,
                         "offset_pct_of_total": 100.0 * sum(offset.values()) / mean_tot,
                         "offset_pct_of_ch510": 100.0 * offset["ch510"] /
                                                 st.mean(r["channels"]["ch510"] for r in rs),
                         "shares": shares(mean_vec(rs), offset)})
        summary[name] = {"rows": rows, "offset": offset}
        print(f"\n  --- {name} ---")
        print(f"  {'position':<12} {'total counts':>13} {'read-to-read spread':>21} "
              f"{'resolution floor':>18} {'offset, % of that':>18}")
        hdr2 = "position's total"
        print(f"  {'':<12} {'(mean of 3)':>13} {'(% of that total)':>21} "
              f"{'(share pts)':>18} {hdr2:>18}")
        for r in rows:
            print(f"  {r['label']:<12} {r['mean_total']:13.0f} {r['spread_pct']:20.2f}% "
                  f"{r['floor_pts']:18.3f} {r['offset_pct_of_total']:17.1f}%")
    a, b = summary["rail lights ON"], summary["rail lights OFF"]
    ma = st.mean(r["mean_total"] for r in a["rows"])
    mb = st.mean(r["mean_total"] for r in b["rows"])
    fa = max(r["floor_pts"] for r in a["rows"])
    fb = max(r["floor_pts"] for r in b["rows"])
    print(f"\n  mean total counts ............. ON {ma:8.0f}   OFF {mb:8.0f}   "
          f"ON is {ma / mb:.1f}x brighter")
    print(f"  worst resolution floor ........ ON {fa:8.3f}   OFF {fb:8.3f}   share points")
    print(f"      -> ON resolves colour changes {fb / fa:.0f}x smaller than OFF can.")
    # Being fair to OFF: its worst position is the one whose third read stepped
    # down mid-run (the room changed). Drop it and OFF still loses, by less.
    fb2 = sorted(r["floor_pts"] for r in b["rows"])[-2]
    fa2 = sorted(r["floor_pts"] for r in a["rows"])[-2]
    print(f"  second-worst floor ............ ON {fa2:8.3f}   OFF {fb2:8.3f}   "
          f"-> still {fb2 / fa2:.0f}x, with OFF's contaminated position dropped")
    print(f"  worst read-to-read spread ..... ON {max(r['spread_pct'] for r in a['rows']):8.2f}%  "
          f"OFF {max(r['spread_pct'] for r in b['rows']):7.2f}%   of that position's own total")

    # position-to-position disagreement: systematic, a blank removes it
    def disagree(rows):
        return max(max(r["shares"][c] for r in rows) - min(r["shares"][c] for r in rows)
                   for c in CH)
    print(f"  stop-to-stop colour disagreement  ON {disagree(a['rows']):8.3f}   "
          f"OFF {disagree(b['rows']):7.3f}   share points")
    print("      (this one is fixed lamp geometry: a per-position blank divides it out)")

    # -- 4. removing the green lamp
    rule("4. If the green lamp were removed, what changes?")
    print("The lamp is ADDITIVE: counts = lamp + leak + light off the sample.")
    print("So it shifts a channel's SHARE without carrying any information.\n")
    for name, d in on_off.items():
        offset = summary[name]["offset"]
        rows = summary[name]["rows"]
        r = rows[0]
        vec = mean_vec(scan_positions(d)[r["label"]])
        raw = shares(vec)                      # nobody subtracts anything
        cor = shares(vec, offset)              # full offset removed
        lamp_only = {c: lamp[c] for c in CH}
        no_lamp = shares(vec, lamp_only)       # only the lamp removed
        print(f"  --- {name}, position {r['label']}, {r['mean_total']:.0f} counts ---")
        print(f"  {'ch':>6} {'share, raw':>11} {'share, lamp':>12} {'share, full':>12} "
              f"{'bias from':>11} {'bias from':>11}")
        print(f"  {'':>6} {'(no subtr.)':>11} {'removed':>12} {'offset gone':>12} "
              f"{'the lamp':>11} {'everything':>11}")
        for c in CH:
            print(f"  {c:>6} {raw[c]:10.2f}% {no_lamp[c]:11.2f}% {cor[c]:11.2f}% "
                  f"{raw[c] - no_lamp[c]:+10.2f} {raw[c] - cor[c]:+10.2f}")
        print(f"  units of the last two columns: PERCENTAGE POINTS OF SHARE.")
        print(f"  worst lamp bias {max(abs(raw[c] - no_lamp[c]) for c in CH):.2f} pts, "
              f"against a resolution floor of {r['floor_pts']:.3f} pts "
              f"({max(abs(raw[c] - no_lamp[c]) for c in CH) / r['floor_pts']:.0f}x)\n")

    # drift: what a stale offset costs
    rule("5. The catch: subtracting only works if the offset is current")
    hist = [(n, sum(v.values())) for n, _, v in conds]
    lo = min(t for _, t in hist)
    hi = max(t for _, t in hist)
    print("Sealed totals actually measured, in counts:")
    for n, t in hist:
        print(f"  {t:7.1f}   {n}")
    print(f"\n  swing across the day: {hi - lo:.1f} counts "
          f"({100 * (hi - lo) / hi:.1f}% of the largest)")
    green_swing = max(v["ch510"] + v["ch550"] for _, _, v in conds) - green
    print(f"  of which the green core moved {green_swing:.1f} counts "
          f"({100 * green_swing / green:.1f}% of the green core)")
    print(f"  and everything else moved {(hi - lo) - green_swing:.1f} counts")
    print("\n  -> the lamp is the STABLE part of the offset. The room leak is the part")
    print("     that moves, and removing the lamp does not touch it.")

    rule("6. Does the lamp add NOISE, or only bias?")
    bg = load("background-2026-09-10.json")
    rs = bg["readings"]
    print(f"{len(rs)} sealed reads, one unchanged condition, ~100 s apart.\n")
    print(f"  {'ch':>6} {'mean counts':>12} {'sd counts':>10} {'sd as % of':>12} "
          f"{'sqrt(mean)':>11} {'sd / sqrt(mean)':>16}")
    print(f"  {'':>6} {'':>12} {'':>10} {'that mean':>12} "
          f"{'= shot noise':>11} {'':>16}")
    for c in CH:
        v = [r["channels"][c] for r in rs]
        m, sd = st.mean(v), st.stdev(v)
        print(f"  {c:>6} {m:12.2f} {sd:10.3f} {100 * sd / m:11.2f}% "
              f"{m ** 0.5:11.2f} {sd / m ** 0.5:16.3f}")
    print("\n  Every channel's sd is 0.18-0.54 counts REGARDLESS of its level, and")
    print("  0.014-0.17 of the shot noise a photon-counting detector would show.")
    print("  So the counts are heavily integrated, the noise is a fixed ~0.2-0.5")
    print("  count floor, and the lamp -- 329 of those counts -- contributes")
    print("  essentially none of it. THE LAMP IS BIAS ONLY, NOT NOISE.")

    rule("7. What a stale offset costs, in the units that matter")
    lit = summary["rail lights ON"]
    r0 = lit["rows"][0]
    vec = mean_vec(scan_positions(on)[r0["label"]])
    fresh = lit["offset"]
    stale = mean_vec(sealed_reads(load("xscan-slot7-z129-press90-2026-09-09.json")))
    a_sh, b_sh = shares(vec, fresh), shares(vec, stale)
    err = max(abs(a_sh[c] - b_sh[c]) for c in CH)
    print(f"Yesterday's sealed vector was {sum(stale.values()):.1f} counts; "
          f"today's is {sum(fresh.values()):.1f}.")
    print(f"Subtracting yesterday's from a {r0['mean_total']:.0f}-count reading taken today")
    print(f"  costs {err:.3f} share points at worst.")
    print(f"  Resolution floor at that pose: {r0['floor_pts']:.3f} share points.")
    print(f"  -> a one-day-stale offset is {err / r0['floor_pts']:.0f}x the noise floor. "
          f"Take a fresh one every run.")

    rule("8. The yardstick: how big is a real colour signal?")
    sweep = load("xscan-slot7-sweep-2026-09-09.json")
    soff = mean_vec(sealed_reads(sweep))
    srows = []
    for lab, rr in scan_positions(sweep).items():
        srows.append((lab, shares(mean_vec(rr), soff)))
    best_c, best = None, 0.0
    for c in CH:
        vals = [sh[c] for _, sh in srows]
        med = st.median(vals)
        dev = max(abs(v - med) for v in vals)
        if dev > best:
            best_c, best = c, dev
    print("The 9-position sweep of 2026-09-09 is the only run with a sample present")
    print("and nobody at the machine throughout. Largest departure of any channel's")
    print(f"share from the median of the nine stops: {best:.2f} share points on {best_c}.")
    print("That is the biggest colour feature this rig has ever produced.\n")
    lamp_lit = max(abs(shares(vec)[c] - shares(vec, lamp)[c]) for c in CH)
    voff_pos = mean_vec(scan_positions(off)[summary["rail lights OFF"]["rows"][0]["label"]])
    lamp_unlit = max(abs(shares(voff_pos)[c] - shares(voff_pos, lamp)[c]) for c in CH)
    print(f"  {'quantity':<52} {'share points':>13}")
    print(f"  {'-' * 52} {'-' * 13}")
    print(f"  {'largest colour feature ever measured':<52} {best:13.2f}")
    print(f"  {'green-lamp bias, rails OFF, nothing subtracted':<52} {lamp_unlit:13.2f}")
    print(f"  {'green-lamp bias, rails ON,  nothing subtracted':<52} {lamp_lit:13.2f}")
    # If the lamp were physically gone, the reading would be vec - lamp and the
    # seated baseline would be fresh - lamp. Subtracting one from the other is
    # the same arithmetic either way, so the residual is identically zero --
    # computed rather than asserted.
    no_lamp_vec = {c: vec[c] - lamp[c] for c in CH}
    no_lamp_off = {c: fresh[c] - lamp[c] for c in CH}
    residual = max(abs(shares(vec, fresh)[c] - shares(no_lamp_vec, no_lamp_off)[c])
                   for c in CH)
    print(f"  {'green-lamp bias, seated baseline subtracted':<52} {residual:13.2f}")
    print(f"  {'resolution floor, rails OFF':<52} {fb:13.3f}")
    print(f"  {'resolution floor, rails ON':<52} {fa:13.3f}")

    rule("9. The error budget, all in share points")
    print("Every row is the WORST disagreement, in share points, that the named")
    print("mistake introduces. Ranked against the 2.61-point colour signal.\n")
    budget = []
    budget.append(("resolution floor, rails ON", fa))
    budget.append(("green-lamp bias, seated baseline subtracted", residual))
    budget.append(("a one-day-stale offset, rails ON", err))
    lit_rows = {r["label"]: r["shares"] for r in lit["rows"]}
    budget.append(("blank taken at the wrong X stop, rails ON",
                   max(max(abs(lit_rows[i][c] - lit_rows[j][c]) for c in CH)
                       for i in lit_rows for j in lit_rows)))
    # a person at the machine: scatter WITHIN one position, reads 1.4 s apart
    z128 = load("xscan-slot7-z128-2026-09-09.json")
    o128 = mean_vec(sealed_reads(z128))
    person = max(max(max(p[c] for p in per) - min(p[c] for p in per) for c in CH)
                 for per in ([shares(r["channels"], o128) for r in rs]
                             for rs in scan_positions(z128).values()))
    budget.append(("a person at the machine during the reading", person))
    off_off = mean_vec(sealed_reads(off))
    budget.append(("blank taken with the lights in the other state",
                   max(max(abs(shares(mean_vec(scan_positions(on)[l]), fresh)[c]
                               - shares(mean_vec(scan_positions(off)[l]), off_off)[c])
                           for c in CH) for l in scan_positions(on))))
    z120 = load("xscan-slot7-z120-2026-09-09.json")
    o120 = mean_vec(sealed_reads(z120))
    budget.append(("blank taken at a different read height (z120 vs z128)",
                   max(max(abs(shares(mean_vec(scan_positions(z120)[l]), o120)[c]
                               - shares(mean_vec(scan_positions(z128)[l]), o128)[c])
                           for c in CH) for l in scan_positions(z120))))
    for lab, val in sorted(budget, key=lambda kv: kv[1]):
        flag = "  <-- bigger than the colour signal" if val > best else ""
        print(f"  {lab:<54} {val:8.3f}{flag}")
    print(f"  {'colour signal, for comparison':<54} {best:8.3f}")

    rule("10. Answers")
    print(f"Q1  Rail lights ON or OFF?")
    print(f"    ON. {ma / mb:.1f}x the signal, and it resolves colour changes {fb / fa:.0f}x")
    print(f"    smaller: {fa:.3f} share points against {fb:.3f}.")
    print()
    print(f"Q2  Remove the green lamp?")
    print(f"    It is pure bias -- {lamp_unlit:.1f} share points unlit, {lamp_lit:.2f} lit, and")
    print(f"    0.0 once the seated baseline is subtracted, which every run already")
    print(f"    takes. It adds no measurable noise. So removing it buys accuracy only")
    print(f"    if the subtraction is NOT done; with the subtraction it buys nothing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
