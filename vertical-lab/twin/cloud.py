"""Utilization of the vertical lab's instruments, the outside work its idle hours could take, and what that costs the
campaigns in time.

    python3 -m twin.cloud events [n_seeds]       # make event logs from the twin (out/twin2/econ/events/*.json)
    python3 -m twin.cloud validate [n_seeds]     # book outside jobs into the twin and re-run (2 workers)

* ``utilization(events)``: each station's busy hours over its available hours (its calendar, times its units;
  the atomizer by its start slots), by campaign, and the idle hours left.
* ``CATALOGUE``: typical outside jobs (an SEM/EDS session, an EBSD map, an XRD scan, a PSD measurement, a PIP
  test, a tensile test, a hardness map, a corrosion screen, an ICP-MS sample, an atomization run of a user's
  feedstock, an LPBF build, a DED session, a heat treatment, an XRF sample), each with its station hours and the
  external rates user facilities charge (sources per entry).
* ``fill(util, cap)``: the jobs that fit in each station's idle hours up to a utilization cap, jobs and revenue a year.
* ``kingman_wq`` / ``slowdown(...)``: the campaigns' added waiting from the outside load, by Kingman's G/G/1
  approximation (Kingman 1961) in its multi-server form (Hopp & Spearman's VUT equation with Sakasegawa's term), and
  the relative change in a campaign's cycle time.
* ``validate(...)``: the same outside load booked into the twin's facility before the campaigns run
  (``Twin(..., external=callable)`` when the twin has the hook; otherwise the same callable is run on each
  ``Facility`` as it is built), and the campaigns re-run to measure the slowdown directly.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

from twin import econ as E

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "out" / "twin2" / "econ"
H_YEAR = 8760.0

# ------------------------------------------------------------------------------------------------------- catalogue
# rate: what an outside academic user pays (USD per job); industry: what a company pays. h: station hours a job.
# 'cv': coefficient of variation of the job's duration (assumed).
U_EMSAL = "https://www.nanofab.utah.edu/documents/2025/12/emsal-rates-1-1-2026.pdf/"
U_BYU_EM = "https://microscopy.byu.edu/services"
U_UW = "https://www.moles.washington.edu/facilities/molecular-analysis-facility/rates"
U_CLEMSON = "https://media.clemson.edu/finance/controller/rates/2627/Electron_Microscope_FY2627.pdf"
U_CORNELL = ("https://www.ccmr.cornell.edu/sites/default/files/2026-06/FY27%20Cornell%20facility%20fees.pdf and "
             "https://www.ccmr.cornell.edu/sites/default/files/2026-06/FY27%20External%20Industry%20or%20for-profit%20fees.pdf")
U_NUANCE = "https://nuance.northwestern.edu/documents/rates/2027-rates/nuance-user-rates-fy27-keck-ii-nu.pdf (and -fp.pdf)"
U_UMASS = "https://www.umass.edu/ials/core-facility-rates"
U_UTAH_ICP = "https://earth.utah.edu/research_facilities/earth-core-facility/icp-ms.php"
U_WMU = "https://wmich.edu/construction-research/priceoverview/tensionpricing"
U_CMU_EOS = "https://engineering.cmu.edu/mfi/facilities/equipment-details/eos-m-290.html"
U_CMU_LMD = "https://engineering.cmu.edu/next/facilities/equipment-details/trumpf-trulaser-cell-3000.html"
U_UAA = "https://uaa.alaska.edu/academics/college-of-engineering/facilities/aic-lab/aic-pricing.cshtml"

CATALOGUE = [
    dict(key="sem_eds", name="SEM/EDS session", station="byu_sem", h=1.0, cv=0.5, rate=85.0, industry=175.0,
         src="off-campus academic: Utah EMSAL FEG SEM $69.30/h (" + U_EMSAL + "), BYU EM non-BYU users $105/h (" +
             U_BYU_EM + "); industry: Clemson SU9000 $175/h (" + U_CLEMSON + "), Utah $90, UW $200 + $50 EDS (" +
             U_UW + ")"),
    dict(key="ebsd", name="EBSD map", station="byu_sem", h=2.0, cv=0.5, rate=165.0, industry=600.0,
         src="Clemson EBSD $82.50/h external non-profit, $600 a sample industry (" + U_CLEMSON + ")"),
    dict(key="xrd", name="Powder XRD scan", station="xrd", h=0.75, cv=0.3, rate=0.75 * 65.0, industry=0.75 * 190.0,
         src="per hour: Utah D8 $64.68 off-campus, $84 industry (" + U_EMSAL + "); Cornell D8 $193 industry (" +
             U_CORNELL + "); UW $64 / $200 (" + U_UW + "); 0.75 h a scan (the twin)"),
    dict(key="psd", name="Laser-diffraction PSD (dry)", station="psd", h=0.5, cv=0.3, rate=0.5 * 49.0,
         industry=0.5 * 113.0, src="NUANCE Mastersizer 3000 $49/h (universities and non-profits), $113/h for-profit (" +
                                   U_NUANCE + "); 0.5 h a sample assumed"),
    dict(key="xrf", name="XRF sample", station="xrf", h=0.5, cv=0.3, rate=0.5 * 63.14, industry=0.5 * 82.0,
         src="Utah micro-XRF $63.14/h off-campus, $82/h industry (" + U_EMSAL + ")"),
    dict(key="pip", name="PIP test (stress-strain curve by indentation)", station="pip", h=0.5, cv=0.3, rate=250.0,
         industry=400.0, src="assumed: the twin's PIP service fee, $250 (twin/facility.py); no published rate found"),
    dict(key="tensile", name="Tensile test, 3 sub-size bars", station="tensile", h=0.6, cv=0.3, rate=3 * 64.0,
         industry=3 * 96.0, src="Western Michigan, ASTM E8 metals $64 a test (" + U_WMU + "); industry 1.5x assumed"),
    dict(key="tensile_hot", name="Elevated-temperature tensile test", station="tensile_hot", h=1.5, cv=0.3,
         rate=2 * 3 * 64.0, industry=2 * 3 * 96.0, src="assumed: twice a room-temperature test"),
    dict(key="hardness", name="Micro-Vickers hardness map", station="hardness", h=0.5, cv=0.3,
         rate=1.54 * (6.0 + 6.45 * 0.5), industry=15.5 + 20.5 * 0.5,
         src="Cornell microhardness $6 + $6.45/h internal, $15.50 + $20.50/h industry (" + U_CORNELL + "); "
             "external academic as Utah's 1.54x internal"),
    dict(key="nano", name="Nanoindentation map", station="nanoindent", h=1.0, cv=0.4, rate=77.0, industry=134.0,
         src="Utah Hysitron $77/h off-campus, $100 industry (" + U_EMSAL + "); UMass $168 industry (" + U_UMASS +
             ")"),
    dict(key="corrosion", name="Corrosion screen (OCP, LPR, EIS, CP)", station="cubxl", h=1.2, cv=0.2,
         rate=1.2 * 50.0, industry=1.2 * 250.0,
         src="Univ. of Alaska Anchorage corrosion lab $50/h for sponsored research, $250/h external (" + U_UAA + ")"),
    dict(key="icpms", name="ICP-MS sample", station="byu_icpms", h=0.1, cv=0.3, rate=90.0, industry=153.0,
         src="midpoints: UMass $37 other academic, $122 external (" + U_UMASS + "); Utah Earth Core 25-45 elements "
             "$142 other academic, $184 commercial (" + U_UTAH_ICP + "); BYU's internal $35 (notes/twin.md)"),
    dict(key="atomize", name="Ultrasonic atomization of a user's feedstock (a run and a full clean)",
         station="atomizer", h=5.5, cv=0.2, rate=1500.0, industry=2500.0,
         src="DAL's prelim benchmark charges $1,500 an atomization (notes/twin.md); industry assumed; 2.5 h a run "
             "plus a full material change, 2-4 h (AMAZEMET, twin/campaign.py)"),
    dict(key="lpbf", name="LPBF build on the MIDI (user powder)", station="utah_midi", h=8.0, cv=0.5,
         rate=8 * 150.0, industry=8 * 320.0,
         src="per hour: Utah's MIDI $120 (FLAIME, twin/facility.py), CMU EOS M290 $230 internal, $320 corporate (" +
             U_CMU_EOS + "); 8 h a build"),
    dict(key="ded", name="DED session (half a day)", station="utah_mxlab", h=4.0, cv=0.3, rate=4 * 128.0,
         industry=4 * 251.0, src="CMU TruLaser Cell 3000 LMD $128/h internal, $251/h corporate (" + U_CMU_LMD + ")"),
    dict(key="heat", name="Heat treatment (a furnace run)", station="furnace", h=4.0, cv=0.3,
         rate=1.54 * (6.0 + 3.24 * 4), industry=13.0 + 8.10 * 4,
         src="Cornell furnaces $6 + $3.24/h internal, $13 + $8.10/h industry (" + U_CORNELL + ")"),
    dict(key="edm", name="Wire-EDM cutting (a plate of specimens)", station="edm", h=1.0, cv=0.5, rate=150.0,
         industry=250.0, src="assumed: the twin's Provo EDM fee, $150 a job (twin/facility.py)"),
]
CAT = {c["key"]: c for c in CATALOGUE}
BY_STATION: dict = {}
for _c in CATALOGUE:
    BY_STATION.setdefault(_c["station"], []).append(_c)


def station_job(station: str, rng=None):
    """One outside job at a station: equal shares of the station's catalogue entries by hours."""
    jobs = BY_STATION.get(station, [])
    if not jobs:
        return None
    if rng is None or len(jobs) == 1:
        return jobs[0]
    return jobs[int(rng.integers(len(jobs)))]


def mean_job(station: str) -> dict:
    jobs = BY_STATION.get(station, [])
    if not jobs:
        return {}
    w = np.ones(len(jobs)) / len(jobs)              # equal shares of hours
    h = float(sum(wi * j["h"] for wi, j in zip(w, jobs)))
    rate_h = float(sum(wi * j["rate"] / j["h"] for wi, j in zip(w, jobs)))
    ind_h = float(sum(wi * j["industry"] / j["h"] for wi, j in zip(w, jobs)))
    m2 = float(sum(wi * (j["h"] ** 2) * (1 + j["cv"] ** 2) for wi, j in zip(w, jobs)))
    return dict(h=h, rate_per_h=rate_h, industry_per_h=ind_h, cs2=m2 / h ** 2 - 1.0, names=[j["name"] for j in jobs])


# ------------------------------------------------------------------------------------------------------- event logs
def _horizon(ev: dict) -> float:
    m = ev.get("meta", {})
    return float(m.get("horizon_h") or 24.0 * float(m.get("horizon_days") or 365.0))


def load_events(path) -> dict:
    return json.loads(Path(path).read_text())


def events_from_twin(tw, meta: dict | None = None) -> dict:
    """The event-log schema (out/twin2/events/<run>.json) from a Twin after run()."""
    fac = next(iter(tw.facilities.values()))
    stations, events = {}, []
    for k, r in fac.res.items():
        s = r.st
        stations[k] = dict(name=s.name, units=s.units, hours=s.hours, external=s.external)
        for j in r.jobs:
            tag = j[4] if len(j) > 4 and isinstance(j[4], dict) else {}
            events.append(dict(t0_h=round(j[0], 4), t1_h=round(j[1], 4), station=k, campaign=j[2], what=j[3],
                               design=tag.get("design"), node=tag.get("node")))
    events.sort(key=lambda e: e["t0_h"])
    results, curves = [], {}
    for k, c in tw.campaigns.items():
        best = 0.0
        cur = []
        for d in sorted(c.demonstrated, key=lambda d: d["t_h"]):
            best = max(best, d["u"])
            results.append(dict(t_h=round(d["t_h"], 3), campaign=k, type="demonstrated", design=d.get("design"),
                                u_true=round(d["u"], 4), best_true=round(best, 4), spent=round(d["spent"], 2)))
            cur.append([round(d["t_h"] / 24.0, 3), round(d["spent"], 2), round(best, 4)])
        curves[k] = cur
    return dict(meta=dict(meta or {}, horizon_h=tw.h, facility=fac.kind), stations=stations, events=events,
                results=results, curves=curves)


def utilization(ev: dict, horizon_h: float | None = None) -> dict:
    """{station: dict(units, hours, available_h, busy_h, by_campaign, util, idle_h, jobs)}; in-house stations only
    (the outside facilities' calendars are theirs)."""
    hz = float(horizon_h or _horizon(ev))
    hrs = E.station_hours_from_events(ev, hz)
    out = {}
    for k, s in ev["stations"].items():
        if s.get("external") or k == "hpc":
            continue
        A = E.available_hours(s.get("hours", "24/7"), int(s.get("units", 1)), hz, k)
        by = {c: d[k][0] for c, d in hrs.items() if k in d}
        jobs = {c: d[k][1] for c, d in hrs.items() if k in d}
        B = sum(by.values())
        out[k] = dict(name=s.get("name", k), units=s.get("units", 1), hours=s.get("hours"), available_h=A, busy_h=B,
                      by_campaign=by, jobs=jobs, util=B / A if A else 0.0, idle_h=max(A - B, 0.0))
    return out


def mean_utilization(evs: list) -> dict:
    """Station utilization averaged over several runs' event logs."""
    us = [utilization(e) for e in evs]
    keys = sorted(set().union(*[u.keys() for u in us]))
    out = {}
    for k in keys:
        rows = [u[k] for u in us if k in u]
        camps = sorted(set().union(*[r["by_campaign"].keys() for r in rows]))
        out[k] = dict(name=rows[0]["name"], units=rows[0]["units"], hours=rows[0]["hours"],
                      available_h=float(np.mean([r["available_h"] for r in rows])),
                      jobs={c: float(np.mean([r["jobs"].get(c, 0) for r in rows])) for c in camps},
                      busy_h=float(np.mean([r["busy_h"] for r in rows])),
                      by_campaign={c: float(np.mean([r["by_campaign"].get(c, 0.0) for r in rows])) for c in camps},
                      util=float(np.mean([r["util"] for r in rows])),
                      idle_h=float(np.mean([r["idle_h"] for r in rows])))
    return out


# ------------------------------------------------------------------------------------------------------- capacity
# what an outside job costs the lab besides station time (all assumed): a technician's hands for reception, mounting in
# the robot's holders, data and invoicing; a unit's time to carry it (a MiR trip, the arm's picks and places);
# consumables as a share of the price
HANDLING_H = (0.25, "assumed: reception, mounting, data and invoicing, a technician's quarter hour a job")
ROBOT_H = {"default": 0.15, "byu_icpms": 0.02, "psd": 0.1, "utah_midi": 0.5, "utah_mxlab": 0.5, "atomizer": 0.3,
           "src": "assumed: a MiR trip and the arm's picks and places, 9 minutes a job; ICP-MS samples go in racks"}
PERSON_JOB_H = {"atomizer": 1.0}       # the crucible needs a person (upkeep.py); extra to HANDLING_H
CONSUMABLES_FRAC = (0.10, "assumed: consumables 10 % of the price")
ROBOT_UNITS, ROBOT_AVAIL = 2, 0.9      # two MiR250 + UR12e units, 90 % available (assumed)
DEMAND_H_WEEK = (10.0, "assumed: 10 h a week of outside bookings per instrument, about a quarter of a busy core-"
                       "facility instrument's week; the sensitivity table runs 5-40")


def fill(util: dict, cap: float = 0.6, price: str = "rate", demand_h_week: float | None = None,
         robot_limit: bool = True, campaign_robot_h: float | None = None) -> dict:
    """Outside jobs that fit in each station's idle hours up to `cap` utilization (and, if given, up to
    `demand_h_week` hours a week of outside demand per station), limited by the two units' hours: jobs, revenue,
    and the lab's own costs of them (handling labour, robot hours, consumables), a year. ``price``: 'rate' for
    academic users, 'industry' for companies."""
    from twin import econ as E2
    rows = {}
    for k, u in util.items():
        mj = mean_job(k)
        if not mj:
            continue
        room = max(cap * u["available_h"] - u["busy_h"], 0.0)
        if demand_h_week is not None:
            room = min(room, demand_h_week * u["available_h"] / (E2.CAL.get(u["hours"], 168.0) * max(u["units"], 1)))
        rows[k] = dict(ext_h=room, job_h=mj["h"], usd_per_h=mj["rate_per_h"] if price == "rate" else mj["industry_per_h"],
                       jobs_named=mj["names"], util_before=u["util"], available_h=u["available_h"], busy_h=u["busy_h"])
    # the units: every outside job needs a trip
    if campaign_robot_h is None:
        n_c = sum(sum(u.get("jobs", {}).values()) if isinstance(u.get("jobs"), dict) else 0 for u in util.values())
        campaign_robot_h = n_c * ROBOT_H["default"]
    robot_avail = ROBOT_UNITS * H_YEAR * ROBOT_AVAIL - campaign_robot_h
    need = sum(r["ext_h"] / r["job_h"] * ROBOT_H.get(k, ROBOT_H["default"]) for k, r in rows.items())
    scale = min(1.0, robot_avail / need) if (robot_limit and need > 0) else 1.0
    out = {}
    lab_rate = E2.hourly("technician")
    for k, r in rows.items():
        ext_h = r["ext_h"] * scale
        jobs = ext_h / r["job_h"]
        rev = ext_h * r["usd_per_h"]
        hand_h = jobs * (HANDLING_H[0] + PERSON_JOB_H.get(k, 0.0))
        cost = hand_h * lab_rate + rev * CONSUMABLES_FRAC[0]
        out[k] = dict(ext_h=ext_h, jobs=jobs, revenue=rev, handling_h=hand_h, cost=cost, net=rev - cost,
                      robot_h=jobs * ROBOT_H.get(k, ROBOT_H["default"]), util_before=r["util_before"],
                      util_after=(r["busy_h"] + ext_h) / r["available_h"] if r["available_h"] else 0.0,
                      job_h=r["job_h"], usd_per_h=r["usd_per_h"], jobs_named=r["jobs_named"])
    out["_robots"] = dict(scale=scale, need_h=need, available_h=robot_avail, campaign_h=campaign_robot_h,
                          limited=scale < 1.0)
    return out


def stations_of(fill_out: dict) -> dict:
    return {k: v for k, v in fill_out.items() if not k.startswith("_")}


def capex_recovery(fill_out: dict, facility: str = "vertical_lab", discount: float = 0.0) -> dict:
    """Outside revenue against the stations' annual fixed costs (depreciation; and all fixed costs)."""
    st_fixed, ov = E.station_fixed(facility, discount)
    fill_out = stations_of(fill_out)
    rev = sum(v["revenue"] for v in fill_out.values())
    net = sum(v["net"] for v in fill_out.values())
    dep = sum(v["capex"] for v in st_fixed.values()) + ov["capex"]
    fixed = sum(v["capex"] + v["service"] + v["utilities"] for v in st_fixed.values()) + \
        sum(ov[k] for k in ("capex", "service", "utilities", "labour"))
    per_station = {}
    for k, v in fill_out.items():
        F = st_fixed.get(k)
        if F:
            per_station[k] = dict(revenue=v["revenue"], depreciation=F["capex"],
                                  share_of_depreciation=v["revenue"] / F["capex"] if F["capex"] else None)
    return dict(revenue=rev, net=net, depreciation=dep, fixed=fixed,
                share_of_depreciation=rev / dep if dep else None, net_share_of_depreciation=net / dep if dep else None,
                share_of_fixed=rev / fixed if fixed else None, net_share_of_fixed=net / fixed if fixed else None,
                capex=E.capex(facility), jobs=sum(v["jobs"] for v in fill_out.values()), per_station=per_station)


# ------------------------------------------------------------------------------------------------------- queueing
def kingman_wq(rho: float, ca2: float, cs2: float, ts: float, m: int = 1) -> float:
    """Mean wait in queue (hours of the station's own clock). m = 1: Kingman (1961), W = rho/(1-rho) (ca2+cs2)/2 ts.
    m > 1: the VUT form with Sakasegawa's exponent, W = rho^(sqrt(2(m+1))-1)/(m(1-rho)) (ca2+cs2)/2 ts."""
    if rho <= 0:
        return 0.0
    if rho >= 0.999:
        return float("inf")
    v = (ca2 + cs2) / 2.0
    if m <= 1:
        return rho / (1.0 - rho) * v * ts
    return rho ** (math.sqrt(2.0 * (m + 1)) - 1.0) / (m * (1.0 - rho)) * v * ts


def _cv2(x) -> float:
    x = np.asarray(x, float)
    if len(x) < 3 or x.mean() <= 0:
        return 1.0
    return float(x.var() / x.mean() ** 2)


def station_stats(ev: dict, campaign: str | None = None) -> dict:
    """Per station, the campaigns' job durations and inter-start gaps: mean service ts, cs2, ca2, rate."""
    hz = _horizon(ev)
    by = {}
    for e in ev["events"]:
        if e["campaign"] == "external" or (campaign and e["campaign"] != campaign):
            continue
        if e["t0_h"] >= hz:
            continue
        by.setdefault(e["station"], []).append((e["t0_h"], e["t1_h"] - e["t0_h"]))
    out = {}
    for s, xs in by.items():
        xs.sort()
        d = [x[1] for x in xs]
        gaps = np.diff([x[0] for x in xs])
        out[s] = dict(n=len(xs), ts=float(np.mean(d)), cs2=_cv2(d), ca2=_cv2(gaps) if len(gaps) > 2 else 1.0,
                      lam=len(xs) / hz)
    return out


def cycle_days(ev: dict, campaign: str) -> float:
    """A campaign's typical cycle: the median time from a design's first booking to its demonstration (days), from
    the event log's design tags; without tags, the first demonstration's day."""
    first = {}
    for e in ev["events"]:
        if e["campaign"] == campaign and e.get("design") is not None:
            first[e["design"]] = min(first.get(e["design"], 1e18), e["t0_h"])
    res = [r for r in ev.get("results", []) if r["campaign"] == campaign and r.get("type") == "demonstrated"]
    cyc = [(r["t_h"] - first[r["design"]]) / 24.0 for r in res if r.get("design") in first]
    if cyc:
        return float(np.median(cyc))
    if res:
        return float(min(r["t_h"] for r in res)) / 24.0
    return float("nan")


def visits_per_experiment(ev: dict, campaign: str) -> dict:
    """Bookings per demonstrated alloy at each station (all of a campaign's bookings over its demonstrations)."""
    n_dem = sum(1 for r in ev.get("results", []) if r["campaign"] == campaign and r.get("type") == "demonstrated")
    st = station_stats(ev, campaign)
    return {s: v["n"] / max(n_dem, 1) for s, v in st.items()}


def slowdown(ev: dict, campaign: str, levels=(0.3, 0.5, 0.6, 0.7, 0.8, 0.9), cs2_ext: float | None = None) -> dict:
    """Kingman's estimate of the campaign's cycle time as every in-house station with catalogue jobs is filled with
    outside work up to each utilization level: 1 + sum_s visits_s * (W_s(rho_s) - W_s(rho0_s)) / cycle, waits in
    calendar time (a day-shift station's hours stretched to the week)."""
    util = utilization(ev)
    st_all = station_stats(ev)
    vis = visits_per_experiment(ev, campaign)
    C0 = cycle_days(ev, campaign)
    out = dict(levels=list(levels), factor=[], added_days=[], cycle_days=C0, by_station={})
    for lv in levels:
        add = 0.0
        for s, v in vis.items():
            if s not in util or s not in st_all:
                continue
            u0 = util[s]
            m = int(u0["units"])
            rho0 = min(u0["util"], 0.98)
            rho1 = max(rho0, lv) if BY_STATION.get(s) else rho0      # outside jobs only where the catalogue has some
            a = st_all[s]
            mj = mean_job(s)
            lam_c = a["lam"]
            if mj and rho1 > rho0:
                ext_h = (rho1 - rho0) * u0["available_h"]
                lam_e = ext_h / mj["h"] / _horizon(ev)
                lt = lam_c + lam_e
                ca2 = (lam_c * a["ca2"] + lam_e * 1.0) / lt
                p_c, p_e = lam_c / lt, lam_e / lt
                es = p_c * a["ts"] + p_e * mj["h"]
                es2 = p_c * a["ts"] ** 2 * (1 + a["cs2"]) + p_e * mj["h"] ** 2 * (1 + (cs2_ext if cs2_ext is not None
                                                                                       else mj["cs2"]))
                cs2 = es2 / es ** 2 - 1.0
                ts = es
            else:
                ca2, cs2, ts = a["ca2"], a["cs2"], a["ts"]
            cal = 168.0 / E.CAL.get(u0["hours"], 168.0)            # station hours -> calendar hours
            w0 = kingman_wq(rho0, a["ca2"], a["cs2"], a["ts"], m) * cal
            w1 = kingman_wq(rho1, ca2, cs2, ts, m) * cal
            d = v * (w1 - w0) / 24.0
            add += d
            out["by_station"].setdefault(s, []).append(round(d, 3))
        out["added_days"].append(add)
        out["factor"].append(1.0 + add / C0 if C0 and np.isfinite(C0) else float("nan"))
    return out


# ------------------------------------------------------------------------------------------------------- the twin
def external_callable(ext_h: dict, horizon_h: float, seed: int = 0):
    """A callable for Twin(external=...): books outside jobs at each station, Poisson arrivals over the horizon,
    ext_h[station] hours a year of them, each job drawn from the station's catalogue entries."""
    def book(fac):
        rng = np.random.default_rng(70_000 + seed)
        n_booked = 0
        for s in sorted(ext_h):
            h = ext_h[s]
            if h <= 0 or s not in fac.res or not BY_STATION.get(s):
                continue
            mj = mean_job(s)
            n = int(rng.poisson(h * horizon_h / H_YEAR / mj["h"]))
            ts = np.sort(rng.uniform(0.0, horizon_h, n))
            for t in ts:
                j = station_job(s, rng)
                d = max(j["h"] * math.exp(rng.normal(0.0, j["cv"]) - j["cv"] ** 2 / 2), 0.05)
                try:
                    fac.res[s].book(float(t), d, "external", "user job " + j["key"],
                                    changeover_h=j.get("changeover_h", 0.0))
                    n_booked += 1
                except RuntimeError:
                    pass
        fac.n_external = n_booked
    return book


def simulate(cfg: dict, external=None) -> tuple[dict, dict]:
    """One twin run like bench.run_one, returning (run row, event log). ``external``: a callable(fac) run on each
    Facility before the campaigns start (through Twin's own hook if it has one)."""
    import inspect
    from twin import bench as B, campaign as C, policies as P
    from twin import facility as FAC
    wip = cfg.get("wip") or (B.WIP["flaime_al"], B.WIP["onr_cu"])
    horizon = cfg.get("horizon_days", B.HORIZON_DAYS)
    specs = {"flaime_al": C.Spec("flaime_al", B.BUDGET["flaime_al"], wip[0], cfg["seed"], cfg.get("kappa", 1.0)),
             "onr_cu": C.Spec("onr_cu", B.BUDGET["onr_cu"], wip[1], cfg["seed"], 1.0)}
    pols = {k: P.POLICIES[cfg["policy"]](k, cfg["seed"]) for k in specs}
    kw = dict(scenario=cfg.get("scenario", "historical"), facility=cfg["facility"], seed=cfg["seed"],
              horizon_days=horizon, isolated=cfg.get("isolated", False))
    t0 = time.time()
    hooked = "external" in inspect.signature(C.Twin.__init__).parameters
    orig = FAC.Facility
    if external is not None and hooked:
        tw = C.Twin(specs, pols, external=external, **kw)
    elif external is not None:
        class _Fx(orig):
            def __init__(self, *a, **k):
                super().__init__(*a, **k)
                external(self)
        C.fac.Facility = _Fx
        try:
            tw = C.Twin(specs, pols, **kw)
        finally:
            C.fac.Facility = orig
    else:
        tw = C.Twin(specs, pols, **kw)
    out = tw.run()
    row = dict(cfg=dict(cfg, horizon_days=horizon), seconds=round(time.time() - t0, 2), campaigns={},
               hook="twin" if hooked else "patched")
    for k in specs:
        o = out[k]
        row["campaigns"][k] = dict(spent=round(o["spent"], 2), best=o["best"],
                                   curve=[(round(a, 3), round(b, 2), round(u, 4)) for a, b, u in o["curve"]],
                                   n_demonstrated=o["n_demonstrated"], n_discoveries=o["n_discoveries"],
                                   n_designs=o["n_designs"], n_lots=o["n_lots"], n_builds=o["n_builds"],
                                   n_sims=o["n_sims"], spend_by=o["spend_by"])
    row["utilization"] = out["utilization"]["shared"]
    ev = events_from_twin(tw, meta=dict(cfg=cfg))
    return row, ev


def _sim_worker(args):
    cfg, ext_h = args
    ext = external_callable(ext_h, cfg.get("horizon_days", 365) * 24.0, cfg["seed"]) if ext_h else None
    row, ev = simulate(cfg, ext)
    return row, ev


def make_events(seeds=4, facility="vertical_lab", policy="cost_aware", workers=2, save=True) -> list:
    """Event logs of `seeds` twin-years (round-1 settings) into out/twin2/econ/events/."""
    from concurrent.futures import ProcessPoolExecutor
    cfgs = [dict(facility=facility, scenario="historical", policy=policy, seed=s, kappa=1.0, isolated=False)
            for s in range(seeds)]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(_sim_worker, [(c, None) for c in cfgs]))
    if save:
        d = OUT / "events"
        d.mkdir(parents=True, exist_ok=True)
        for row, ev in res:
            c = row["cfg"]
            (d / f"{c['facility']}_{c['policy']}_s{c['seed']}.json").write_text(json.dumps(ev))
            with open(d / "runs.jsonl", "a") as f:
                f.write(json.dumps(row) + "\n")
    return res


def validate(seeds=4, levels=(0.0, 0.25, 0.5, 0.7, 0.85), facility="vertical_lab", policy="cost_aware", workers=2,
             baseline_events=None) -> dict:
    """Book outside jobs to bring every in-house station with catalogue jobs to each utilization level, re-run the
    campaigns (``seeds`` twin-years a level), and compare time to target and the year's best with the empty lab."""
    from concurrent.futures import ProcessPoolExecutor
    from twin import bench as B
    cfgs = [dict(facility=facility, scenario="historical", policy=policy, seed=s, kappa=1.0, isolated=False)
            for s in range(seeds)]
    if baseline_events is None:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            base = list(ex.map(_sim_worker, [(c, None) for c in cfgs]))
        baseline_events = [ev for _, ev in base]
        base_rows = [r for r, _ in base]
        d = OUT / "events_validate"
        d.mkdir(parents=True, exist_ok=True)
        for (row, ev) in base:
            (d / f"{facility}_{policy}_s{row['cfg']['seed']}.json").write_text(json.dumps(ev))
    else:
        base_rows = None
    U = mean_utilization(baseline_events)
    tasks, meta = [], []
    for lv in levels:
        ext_h = {k: max(lv * u["available_h"] - u["busy_h"], 0.0) for k, u in U.items() if BY_STATION.get(k)} \
            if lv > 0 else {}
        for c in cfgs:
            tasks.append((c, ext_h))
            meta.append(lv)
    if base_rows is not None:
        todo = [(t, m) for t, m in zip(tasks, meta) if m > 0]
    else:
        todo = list(zip(tasks, meta))
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(_sim_worker, [t for t, _ in todo]))
    rows_by = {lv: [] for lv in levels}
    evs_by = {lv: [] for lv in levels}
    if base_rows is not None:
        rows_by[0.0] = base_rows
        evs_by[0.0] = baseline_events
    for (t, lv), (row, ev) in zip(todo, res):
        rows_by[lv].append(row)
        evs_by[lv].append(ev)
    out = dict(seeds=seeds, levels=list(levels), facility=facility, policy=policy, runs=len(res) + (len(base_rows or [])),
               campaigns={}, util={}, hook=(res[0][0].get("hook") if res else None))
    for lv in levels:
        Ul = mean_utilization(evs_by[lv])
        out["util"][str(lv)] = {k: round(v["util"], 4) for k, v in Ul.items()}
    from twin import accel as AC
    for camp in ("flaime_al", "onr_cu"):
        tgt = B.TARGET[camp]
        d = dict(target=tgt, days_km=[], days_all=[], best_mean=[], n_dem_mean=[], hit_frac=[], cycle_days=[],
                 kingman=[], kingman_cycle_days=[])
        for lv in levels:
            days, ok, best, ndem = [], [], [], []
            for r in rows_by[lv]:
                c = r["campaigns"][camp]
                x, hit = AC.time_to_target(c["curve"], tgt, "days", r["cfg"].get("horizon_days", 365))
                days.append(x)
                ok.append(hit)
                best.append(c["best"])
                ndem.append(c["n_demonstrated"])
            d["days_all"].append([round(float(x), 2) if h else None for x, h in zip(days, ok)])
            d["days_km"].append(AC.km_median(days, ok))
            d["best_mean"].append(float(np.mean(best)))
            d["n_dem_mean"].append(float(np.mean(ndem)))
            d["hit_frac"].append(float(np.mean(ok)))
            cyc = [cycle_days(ev, camp) for ev in evs_by[lv]]
            d["cycle_days"].append(float(np.nanmedian(cyc)) if np.isfinite(cyc).any() else None)
            ks = [slowdown(ev, camp, levels=[lv])["factor"][0] for ev in baseline_events]
            d["kingman"].append(float(np.nanmean(ks)) if lv > 0 else 1.0)
        b0 = d["days_km"][0]
        d["slowdown_days"] = [(x / b0 if (np.isfinite(x) and b0) else None) for x in d["days_km"]]
        c0 = d["cycle_days"][0]
        d["slowdown_cycle"] = [(x / c0 if (x is not None and c0) else None) for x in d["cycle_days"]]
        d["throughput_ratio"] = [x / d["n_dem_mean"][0] if d["n_dem_mean"][0] else None for x in d["n_dem_mean"]]
        out["campaigns"][camp] = d
    return out


# ------------------------------------------------------------------------------------------------------- round 2
def _sim2_worker(args):
    """One bench2 run (the benchmark's own construction, twin.bench2.run_one) with outside jobs booked first through
    Twin(external=...); its files go to `outdir`, never to the benchmark's out/twin2."""
    cfg, ext_h, outdir = args
    from twin import bench2 as B2, campaign as C
    d = Path(outdir)
    d.mkdir(parents=True, exist_ok=True)
    B2.OUT, B2.EVENTS, B2.RUNS = d, d / "events", d / "runs"
    ext = external_callable(ext_h, float(cfg.get("days", 365)) * 24.0, cfg["seed"]) if ext_h else None
    orig = C.Twin.__init__
    if ext is not None:
        def init(self, *a, **k):
            k["external"] = ext
            orig(self, *a, **k)
        C.Twin.__init__ = init
    try:
        row = B2.run_one(dict(cfg, events=True))
    finally:
        C.Twin.__init__ = orig
    ev = json.loads((B2.EVENTS / f"{B2.run_id(cfg)}.json").read_text())
    row.pop("events_file", None)
    row["hook"] = "twin"
    return row, ev


def validate2(policies=("bofn", "heuristic"), seeds=4, levels=(0.0, 0.5, 0.7, 0.85), facility="vertical_lab",
              workers=2, scratch="/tmp/econ_val") -> dict:
    """The slowdown validation on the round-2 benchmark (twin.bench2): for each policy, `seeds` twin-years with the
    lab empty, then with outside jobs bringing every station with catalogue jobs to each level; time to T1 (the
    state of the art, bench2.targets()) on the new-alloy curves, cycle time, throughput, and Kingman's estimate on
    the empty lab's logs."""
    from concurrent.futures import ProcessPoolExecutor
    from twin import accel as AC, bench2 as B2
    T1 = B2.targets()["T1"]
    base_cfg = lambda pol, s: dict(policy=pol, seed=s, facility=facility, stock="stocked", days=365,
                                   years_budget=1.0, crucible=225, reuse=True, scenario="historical")
    tasks = [(base_cfg(p, s), None, f"{scratch}/{p}_0_s{s}") for p in policies for s in range(seeds)]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        base = list(ex.map(_sim2_worker, tasks))
    by = {(t[0]["policy"], 0.0): [] for t in tasks}
    for t, r in zip(tasks, base):
        by[(t[0]["policy"], 0.0)].append(r)
    d = OUT / "events_validate"
    d.mkdir(parents=True, exist_ok=True)
    for (row, ev) in base:
        c = row["cfg"]
        (d / f"{c['facility']}_{c['policy']}_s{c['seed']}.json").write_text(json.dumps(ev))
    tasks2 = []
    for p in policies:
        U = mean_utilization([ev for _, ev in by[(p, 0.0)]])
        for lv in levels:
            if lv <= 0:
                continue
            ext_h = {k: max(lv * u["available_h"] - u["busy_h"], 0.0) for k, u in U.items() if BY_STATION.get(k)}
            for s in range(seeds):
                tasks2.append((base_cfg(p, s), ext_h, f"{scratch}/{p}_{lv:g}_s{s}", lv))
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(_sim2_worker, [t[:3] for t in tasks2]))
    for t, r in zip(tasks2, res):
        by.setdefault((t[0]["policy"], t[3]), []).append(r)
    out = dict(seeds=seeds, levels=list(levels), facility=facility, runs=len(base) + len(res), hook="twin",
               engine="twin.bench2 (benchmark snapshot)", targets=T1, policies={})
    for p in policies:
        P = dict(campaigns={}, util={})
        for lv in levels:
            Ul = mean_utilization([ev for _, ev in by[(p, lv)]])
            P["util"][str(lv)] = {k: round(v["util"], 4) for k, v in Ul.items()}
        for camp in ("flaime_al", "onr_cu"):
            dd = dict(target=T1[camp], days_km=[], days_all=[], best_mean=[], n_dem_mean=[], hit_frac=[],
                      cycle_days=[], kingman=[])
            for lv in levels:
                rows = by[(p, lv)]
                days, ok = [], []
                for row, _ in rows:
                    c = row["campaigns"][camp]
                    x, h = AC.time_to_target(c.get("curve_new") or c["curve"], T1[camp], "days", 365.0)
                    days.append(x)
                    ok.append(h)
                dd["days_all"].append([round(float(x), 2) if h else None for x, h in zip(days, ok)])
                dd["days_km"].append(AC.km_median(days, ok))
                dd["best_mean"].append(float(np.mean([r["campaigns"][camp].get("best_new", r["campaigns"][camp]["best"])
                                                      for r, _ in rows])))
                dd["n_dem_mean"].append(float(np.mean([r["campaigns"][camp]["n_demonstrated"] for r, _ in rows])))
                dd["hit_frac"].append(float(np.mean(ok)))
                cyc = [cycle_days(ev, camp) for _, ev in rows]
                dd["cycle_days"].append(float(np.nanmedian(cyc)) if np.isfinite(cyc).any() else None)
                ks = [slowdown(ev, camp, levels=[lv])["factor"][0] for _, ev in by[(p, 0.0)]]
                dd["kingman"].append(float(np.nanmean(ks)) if lv > 0 else 1.0)
            b0, c0, n0 = dd["days_km"][0], dd["cycle_days"][0], dd["n_dem_mean"][0]
            dd["slowdown_days"] = [(x / b0 if (np.isfinite(x) and b0 and np.isfinite(b0)) else None) for x in dd["days_km"]]
            dd["slowdown_cycle"] = [(x / c0 if (x is not None and c0) else None) for x in dd["cycle_days"]]
            dd["throughput_ratio"] = [x / n0 if n0 else None for x in dd["n_dem_mean"]]
            P["campaigns"][camp] = dd
        out["policies"][p] = P
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "events"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    if cmd == "events":
        res = make_events(n)
        print(f"{len(res)} event logs in {OUT / 'events'}")
    elif cmd == "validate2":
        pols = tuple(sys.argv[3].split(",")) if len(sys.argv) > 3 else ("bofn", "heuristic")
        v = validate2(pols, n)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "validate.json").write_text(json.dumps(v, indent=1, default=float))
        print(json.dumps({p: {k: dict(cycle=d["slowdown_cycle"], days=d["slowdown_days"], kingman=d["kingman"])
                              for k, d in P["campaigns"].items()} for p, P in v["policies"].items()}))
    elif cmd == "validate":
        v = validate(n)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "validate.json").write_text(json.dumps(v, indent=1))
        print(json.dumps({k: dict(days=v["campaigns"][k]["slowdown_days"], cycle=v["campaigns"][k]["slowdown_cycle"],
                                  kingman=v["campaigns"][k]["kingman"]) for k in v["campaigns"]}))
