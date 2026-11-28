"""A discrete-event simulation of the machining cell's day: the lathe, the arm, the baths, the dryer, the gauge (#367).

Sterling, on PR #373 (2026-11-22): "seems like you could benefit from running simulations" and "it seems like the
suggestion is to have a stand-alone robot arm rather than use one of the existing mobile manipulators".

``machining.capacity()`` adds up busy hours. This runs the cell part by part (SimPy), with the times of
``machining.py`` made variable and the stoppages that sums can't show: the lathe blocked when nothing takes its parts
away, a jam waiting for a person, the basket waiting for the dryer, the arm away serving the rest of the lab.

    python3 machining_sim.py          # every scenario, 5 seeds x 20 working days -> out/machining_sim.json, .png

Scenarios (``SCENARIOS``):

- **pedestal**: the PR's design: a UR10e on a pedestal, always at the cell; three baskets.
- **mobile, stays**: no fixed arm. The lathe drops its parts on an accumulator (16 pairs). When a basket's worth is
  there, the cell calls one of the lab's MiR250 + UR10e units; it comes when the fleet frees one, docks, and stays
  until every part it found is cleaned, dried, weighed, gauged and racked (it waits out the baths and the dryer).
  Three baskets, as the pedestal.
- **mobile + hoist**: as above, but a small hoist (a cleaning line's lift-and-shuttle) carries the baskets from the
  load stand through wash, rinse and dryer to the unload stand. The unit only handles parts: in from the accumulator,
  out to the scale, the gauge and the rack. Six baskets, so a visit has a batch to do; it comes when four baskets'
  worth of parts wait (16 pairs) with an empty basket to take them, or three dried baskets wait.
- **mobile + hoist, lathe overnight**: the same, with the lathe running round the clock into a 48-pair accumulator
  and the unit working the day shift. (An unattended lathe with an alcohol mist is a fire-safety question first.)

The fleet is modelled only as a response time: a call waits an exponentially distributed time (mean ``fleet_wait_min``)
before a unit is free, then travels and docks (``dock_s``, re-localising on the cell's fiducials). PR #332's
bottleneck study has three MiR250 + UR10e units carrying about 3.8 h per fully tested alloy, about 38 unit-hours a day
at ten a day, or half of three units' 72; the hours this cell would add are reported against that.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

import machining as MC

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

DAY = 24 * 3600.0
SHIFT = (7 * 3600.0, 15 * 3600.0)      # the day shift, 07:00-15:00: people in, the IPA process attended
WEEK_DAYS = 5                           # Monday to Friday
DAYS = 28                               # four weeks of calendar time (20 working days)
SEEDS = 5
PAIRS_PER_BAR = MC.bar_per_pair()["pairs_per_bar"]

BASE = dict(
    al_share=0.5,
    demand_per_day=MC.DEMAND,           # pairs a calendar day; the cell must make them in its working hours
    lathe_cv=0.04,                      # spread of the lathe's cycle (log-normal), est.
    bar_change_s=90.0,                  # the bar feeder pushes the remnant out and loads the next bar, est.
    magazine_bars=10,                   # bars the feeder's magazine holds at Ø20 (not found; est.)
    jam_p={"Al": 0.004, "Cu": 0.002},   # chance a part ends in a chip wrap or a lost part that stops the lathe, est.
    jam_fix_s=600.0,                    # a person clears it once there (est.)
    arm=dict(MC.ARM),                   # s: load_part 16, unload_part 32 (scale, gauge, rack), basket_moves 48, lid 15
    arm_cv=0.10,
    misgrip_p=0.002,                    # a part the arm drops or misses: a retry from the camera, 60 s, est.
    wash_s=MC.CLEAN["wash_min"] * 60.0,
    rinse_s=MC.CLEAN["rinse_min"] * 60.0,
    dry_s=(8 * 60.0, 14 * 60.0),        # the dryer's cycle, uniform (the PR's 10 min estimate, give or take)
    parts_per_basket=2 * MC.CLEAN["pairs_per_basket"],
    baskets=3,                          # one loading, one in the baths, one in the dryer
    reject_p=0.01,                      # parts the gauge or the scale rejects (set aside, made again), est.
    acc_pairs=None,                     # the accumulator's capacity in pairs (None: the upender, 1 part)
    mobile=False, hoist=False, lathe_24h=False,
    call_pairs=4,                       # a mobile unit is called at this many pairs waiting (and a basket free)
    call_dried=1,                       # ... or this many dried baskets waiting to be unloaded
    fleet_wait_min=15.0,                # mean wait for a free unit
    dock_s=150.0,                       # drive in from the aisle, dock, re-localise on the fiducials, est.
    leave_s=60.0,                       # undock and leave
)

SCENARIOS = {
    "pedestal": dict(),
    "mobile, stays": dict(mobile=True, acc_pairs=24, call_pairs=8, baskets=3),
    "mobile + hoist": dict(mobile=True, hoist=True, acc_pairs=32, call_pairs=16, baskets=6, call_dried=3),
    "mobile + hoist, lathe overnight": dict(mobile=True, hoist=True, acc_pairs=64, call_pairs=16, baskets=6,
                                            call_dried=3, lathe_24h=True),
}


def working(t: float, s: dict) -> bool:
    d = int(t // DAY)
    return (d % 7) < WEEK_DAYS and SHIFT[0] <= t % DAY < SHIFT[1]


def next_shift(t: float) -> float:
    """The next moment the shift is on (t itself if it is)."""
    d = int(t // DAY)
    while True:
        if (d % 7) < WEEK_DAYS:
            a, b = d * DAY + SHIFT[0], d * DAY + SHIFT[1]
            if t < b:
                return max(t, a)
        d += 1


def shift_overlap(t0: float, t1: float) -> float:
    """Seconds of [t0, t1] that fall in the shift."""
    tot, d = 0.0, int(t0 // DAY)
    while d * DAY < t1:
        if (d % 7) < WEEK_DAYS:
            a, b = d * DAY + SHIFT[0], d * DAY + SHIFT[1]
            tot += max(0.0, min(b, t1) - max(a, t0))
        d += 1
    return tot


def simulate(sc: dict, seed: int, days: int = DAYS) -> dict:
    import simpy
    s = dict(BASE, **sc)
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    horizon = days * DAY
    st = dict(made_parts=0, racked_pairs=0, rejected=0, jams=0, misgrips=0, lathe_busy=0.0, lathe_blocked=0.0,
              lathe_starved=0.0, arm_busy=0.0, visits=0, unit_at_cell=0.0, lead=[], acc_max=0, dryer_busy=0.0,
              basket_wait_dryer=0.0, call_wait=[])
    acc_cap = 2 * (s["acc_pairs"] or 0.5)                            # parts
    acc = simpy.Store(env, capacity=int(acc_cap))
    arm = simpy.PriorityResource(env, capacity=1)
    wash, rinse, dryer = (simpy.Resource(env, 1) for _ in range(3))
    baskets = simpy.Store(env, capacity=s["baskets"])
    for k in range(s["baskets"]):
        baskets.put([])
    dried = simpy.Store(env)                                          # baskets waiting to be unloaded
    state = dict(docked=not s["mobile"], present=env.event(), called=False, racked_parts=0, pending_tasks=0,
                 pending=[0, 0, 0], in_chain=0, loading=False, unloading=False)
    if not s["mobile"]:
        state["present"].succeed()

    def lognorm(mean, cv):
        sig = math.sqrt(math.log(1 + cv * cv))
        return float(mean * rng.lognormal(-sig * sig / 2, sig))

    cyc = {m: (sum(t for _, t, _ in MC.cycle(m)["cup"]), sum(t for _, t, _ in MC.cycle(m)["plug"]))
           for m in ("Al", "Cu")}

    def person_needed(t_need):
        """Wait for a person (the shift), then for the fix."""
        yield env.timeout(next_shift(env.now) - env.now)
        yield env.timeout(t_need)

    # ---------------------------------------------------------------------------------------------------- lathe
    def lathe():
        bars_left, pairs_on_bar, k = s["magazine_bars"], 0, 0
        while True:
            if not s["lathe_24h"] and not working(env.now, s):
                t0 = env.now
                yield env.timeout(next_shift(env.now) - env.now)
                st["lathe_starved"] += env.now - t0
                continue
            metal = "Al" if int(env.now // DAY) % 2 == 0 else "Cu"     # Al and Cu on alternate days (the notes)
            if pairs_on_bar >= PAIRS_PER_BAR:
                if bars_left <= 0:                                    # a person refills the magazine
                    t0 = env.now
                    yield from person_needed(300.0)
                    st["lathe_starved"] += env.now - t0
                    bars_left = s["magazine_bars"]
                yield env.timeout(s["bar_change_s"])
                st["lathe_busy"] += s["bar_change_s"]
                bars_left -= 1
                pairs_on_bar = 0
            for j, base in enumerate(cyc[metal]):
                dt = lognorm(base, s["lathe_cv"])
                yield env.timeout(dt)
                st["lathe_busy"] += dt
                if rng.random() < s["jam_p"][metal]:
                    st["jams"] += 1
                    t0 = env.now
                    yield from person_needed(s["jam_fix_s"])
                    st["lathe_starved"] += env.now - t0
                t0 = env.now
                yield acc.put(dict(born=env.now, metal=metal, kind="cup" if j == 0 else "plug"))
                st["lathe_blocked"] += (env.now - t0) if s["lathe_24h"] else shift_overlap(t0, env.now)
                st["made_parts"] += 1
                st["acc_max"] = max(st["acc_max"], len(acc.items))
            pairs_on_bar += 1
            k += 1

    # ---------------------------------------------------------------------------------------------------- the arm
    def arm_task(seconds, prio):
        """Hold the arm for `seconds` once the arm is at the cell (priority: lower first)."""
        state["pending_tasks"] += 1
        state["pending"][prio] += 1
        while True:
            while not state["docked"]:
                yield state["present"]
            req = arm.request(priority=prio)
            yield req
            if state["docked"]:
                break
            arm.release(req)                                          # it left while we queued: wait for the next
        dt = lognorm(seconds, s["arm_cv"])
        if rng.random() < s["misgrip_p"]:
            st["misgrips"] += 1
            dt += 60.0
        yield env.timeout(dt)
        st["arm_busy"] += dt
        arm.release(req)
        state["pending_tasks"] -= 1
        state["pending"][prio] -= 1

    def basket_move():
        if not s["hoist"]:
            yield from arm_task(s["arm"]["basket_moves"] / 6.0, 1)
        else:
            yield env.timeout(25.0)                                   # the hoist's lift and shuttle, est.

    def loader():
        """Parts from the accumulator through the blow-off into the basket on the load stand."""
        while True:
            b = yield baskets.get()
            state["loading"] = True
            while len(b) < s["parts_per_basket"]:
                part = yield acc.get()
                yield from arm_task(s["arm"]["load_part"], 2)
                b.append(part)
            state["loading"] = False
            state["in_chain"] += 1
            env.process(chain(b))

    def chain(b):
        """Wash, rinse, dry (the IPA steps attended: they start only on the shift), then wait to be unloaded."""
        yield env.timeout(next_shift(env.now) - env.now)
        for res, dur in ((wash, s["wash_s"]), (rinse, s["rinse_s"])):
            with res.request() as r:
                yield r
                yield from basket_move()
                yield env.timeout(dur)
        t0 = env.now
        with dryer.request() as r:
            yield r
            st["basket_wait_dryer"] += env.now - t0
            yield from basket_move()
            dt = float(rng.uniform(*s["dry_s"]))
            yield env.timeout(dt)
            st["dryer_busy"] += dt
            yield from basket_move()
        yield dried.put(b)

    def unloader():
        """Each dried part to the scale, the gauge and the rack; the lid on each full cassette; the basket back."""
        while True:
            b = yield dried.get()
            state["unloading"] = True
            for part in b:
                yield from arm_task(s["arm"]["unload_part"], 0)
                if rng.random() < s["reject_p"]:
                    st["rejected"] += 1
                    continue
                state["racked_parts"] += 1
                if part["kind"] == "plug":
                    st["racked_pairs"] += 1
                    st["lead"].append((env.now - part["born"]) / 3600.0)
                if state["racked_parts"] % 8 == 0:
                    yield from arm_task(s["arm"]["lid"], 0)
            state["unloading"] = False
            yield from basket_move()
            state["in_chain"] -= 1
            yield baskets.put([])

    # ---------------------------------------------------------------------------------------------------- the fleet
    def fleet():
        """Call a unit when enough waits; it docks, works while there is work, and leaves."""
        while True:
            yield env.timeout(30.0)
            waiting_pairs = len(acc.items) / 2
            room = len(baskets.items) > 0 or state["loading"]          # an empty basket to load into
            dried_waiting = len(dried.items) + int(state["unloading"])
            need = (state["pending"][1] > 0                               # a basket stuck for want of a move
                    or dried_waiting >= s["call_dried"]
                    or (waiting_pairs >= s["call_pairs"] and room)
                    or (len(acc.items) >= acc_cap - 1 and room))
            if not need or (s["lathe_24h"] and not working(env.now, s)):
                continue
            t_call = env.now
            yield env.timeout(float(rng.exponential(s["fleet_wait_min"] * 60.0)))
            yield env.timeout(next_shift(env.now) - env.now)          # the units work the shift here too
            yield env.timeout(s["dock_s"])
            arrive = env.now
            st["visits"] += 1
            state["docked"] = True
            state["present"].succeed()
            idle = 0.0
            while True:
                yield env.timeout(15.0)
                busy = state["pending_tasks"] > 0 or len(dried.items) > 0 or (len(acc.items) > 0 and
                                                                              state["loading"])
                if not s["hoist"]:
                    busy = busy or state["in_chain"] > 0                 # it waits out the baths and the dryer
                idle = 0.0 if busy else idle + 15.0
                if idle >= 60.0 or not working(env.now, s):
                    break
            state["docked"] = False
            state["present"] = env.event()
            st["unit_at_cell"] += env.now - arrive + s["dock_s"] + s["leave_s"]
            st["call_wait"].append((arrive - next_shift(t_call)) / 60.0)   # a night's call counts from 07:00
            yield env.timeout(s["leave_s"])

    env.process(lathe())
    env.process(loader())
    env.process(unloader())
    if s["mobile"]:
        env.process(fleet())
    env.run(until=horizon)
    work_days = sum(1 for d in range(days) if d % 7 < WEEK_DAYS)
    lead = np.array(st["lead"]) if st["lead"] else np.array([np.nan])
    return dict(pairs_per_working_day=st["racked_pairs"] / work_days,
                pairs_per_calendar_day=st["racked_pairs"] / days,
                lathe_util_shift=st["lathe_busy"] / (work_days * (SHIFT[1] - SHIFT[0])),
                lathe_blocked_h_per_day=st["lathe_blocked"] / 3600.0 / work_days,
                arm_busy_h_per_day=st["arm_busy"] / 3600.0 / work_days,
                unit_at_cell_h_per_day=st["unit_at_cell"] / 3600.0 / work_days,
                visits_per_day=st["visits"] / work_days, jams=st["jams"], misgrips=st["misgrips"],
                rejected=st["rejected"], acc_max_pairs=st["acc_max"] / 2,
                lead_h_median=float(np.nanmedian(lead)), lead_h_p90=float(np.nanpercentile(lead, 90)),
                dryer_h_per_day=st["dryer_busy"] / 3600.0 / work_days,
                call_to_arrival_min=float(np.mean(st["call_wait"])) if st["call_wait"] else 0.0)


# ---------------------------------------------------------------------------------------------------- drying
# A lumped check of the dryer's 10 min (the cell's limit, above). Under vacuum the IPA boils off at the temperature where
# its vapour pressure meets the chamber's (the condenser at -10 C holds it near 7 mbar: about -2 C for IPA); the heat to
# do it comes first from the part's own heat (it cools from 45 C), then from the pot's 45 C walls, by radiation and by
# conduction through the basket's few contacts, both poor in a vacuum. Constants: IPA 0.786 g/mL, 756 J/g; Al 0.90,
# Cu 0.385 J/g K; Antoine for IPA (log10 mmHg = 8.00308 - 1505.52 / (T_C + 211.6)).
DRY = dict(T_wall=318.15, p_ch_mbar=7.0, emissivity=0.10, area_m2=0.0061, pump_down_s=180.0,
           contact_w_per_k=(0.01, 0.05), bore_ml=6.0, film_ml=0.2)
PART_G = {"Al": 32.08 + 3.17, "Cu": 106.27 + 10.48}       # a cup and its plug (notes/machining.md)
CP = {"Al": 0.90, "Cu": 0.385}


def ipa_t_eq(p_mbar: float) -> float:
    """K at which IPA's vapour pressure is p_mbar."""
    mmhg = p_mbar * 0.750062
    return 1505.52 / (8.00308 - math.log10(mmhg)) - 211.6 + 273.15


def drying() -> dict:
    """Minutes to dry a basket (heat-limited, per pair, the basket's four pairs in parallel): bores full of IPA, or
    drained to a film, for Al and Cu, at the poor and the good end of the contact conductance."""
    d = DRY
    T_eq = ipa_t_eq(d["p_ch_mbar"])
    out = {"T_eq_C": round(T_eq - 273.15, 1)}
    for metal in ("Al", "Cu"):
        C = PART_G[metal] * CP[metal]
        sens = C * (d["T_wall"] - T_eq)                    # J the part gives up cooling to T_eq
        rad = 5.67e-8 * d["emissivity"] * d["area_m2"] * (d["T_wall"] ** 4 - T_eq ** 4)
        for case, ml in (("bore full", d["bore_ml"] + d["film_ml"]), ("drained", d["film_ml"])):
            latent = ml * 0.786 * 756.0
            rest = max(0.0, latent - sens)
            mins = []
            for g in d["contact_w_per_k"]:
                q = rad + g * (d["T_wall"] - T_eq)
                mins.append(round((d["pump_down_s"] + rest / q) / 60.0, 1))
            out[f"{metal}, {case}"] = dict(ipa_g=round(ml * 0.786, 2), latent_J=round(latent), part_heat_J=round(sens),
                                           minutes_poor_good_contact=mins)
    return out


def run(scenarios=None, seeds: int = SEEDS) -> dict:
    out = {}
    for name, sc in (scenarios or SCENARIOS).items():
        rs = [simulate(sc, seed) for seed in range(seeds)]
        out[name] = {k: dict(mean=round(float(np.mean([r[k] for r in rs])), 3),
                             lo=round(float(np.min([r[k] for r in rs])), 3),
                             hi=round(float(np.max([r[k] for r in rs])), 3)) for k in rs[0]}
        o = out[name]
        print(f"{name:34s} {o['pairs_per_calendar_day']['mean']:6.1f} pairs/day  lathe blocked "
              f"{o['lathe_blocked_h_per_day']['mean']:4.1f} h  arm {o['arm_busy_h_per_day']['mean']:4.2f} h  unit at cell "
              f"{o['unit_at_cell_h_per_day']['mean']:4.2f} h in {o['visits_per_day']['mean']:4.1f} visits  lead "
              f"{o['lead_h_median']['mean']:5.1f} h", flush=True)
    return out


def sensitivity(seeds: int = 3) -> dict:
    """The mobile options against the fleet's response time, and the pedestal at a doubled demand."""
    out = {}
    for w in (5.0, 15.0, 30.0, 60.0):
        for name in ("mobile, stays", "mobile + hoist"):
            sc = dict(SCENARIOS[name], fleet_wait_min=w)
            rs = [simulate(sc, seed) for seed in range(seeds)]
            out[f"{name}, wait {w:.0f} min"] = {k: round(float(np.mean([r[k] for r in rs])), 3) for k in
                                                ("pairs_per_calendar_day", "unit_at_cell_h_per_day", "visits_per_day",
                                                 "lathe_blocked_h_per_day", "lead_h_median")}
    return out


def plot(res: dict, path=OUT / "machining_sim.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = list(res)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    col = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
    panels = [("pairs_per_calendar_day", "Pairs a calendar day", MC.DEMAND, "demand"),
              ("unit_at_cell_h_per_day", "Arm hours a working day: the pedestal's busy hours;\nthe mobile unit's "
                                         "hours at the cell, docking included", None, None),
              ("lead_h_median", "Median hours from parting off to the rack", None, None)]
    for ax, (k, title, ref, lab) in zip(axes, panels):
        vals = [res[n][k]["mean"] if k != "unit_at_cell_h_per_day" or "mobile" in n else
                res[n]["arm_busy_h_per_day"]["mean"] for n in names]
        lo = [res[n][k]["lo"] if k != "unit_at_cell_h_per_day" or "mobile" in n else
              res[n]["arm_busy_h_per_day"]["lo"] for n in names]
        hi = [res[n][k]["hi"] if k != "unit_at_cell_h_per_day" or "mobile" in n else
              res[n]["arm_busy_h_per_day"]["hi"] for n in names]
        y = np.arange(len(names))
        ax.barh(y, vals, color=col[:len(names)], height=0.6,
                xerr=[np.array(vals) - np.array(lo), np.array(hi) - np.array(vals)], ecolor="#555555", capsize=3)
        for yi, v in zip(y, vals):
            ax.text(v, yi, f"  {v:.1f}", va="center", fontsize=9)
        if ref:
            ax.axvline(ref, color="#333333", lw=1, ls="--")
            ax.text(ref, len(names) - 0.4, f" {lab} {ref:.0f}", fontsize=8, va="bottom")
        ax.set_yticks(y)
        ax.set_yticklabels(names if ax is axes[0] else [""] * len(names), fontsize=9)
        ax.set_title(title, fontsize=10)
        ax.invert_yaxis()
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.margins(x=0.25)
    fig.suptitle(f"The machining cell simulated: {SEEDS} seeds x {DAYS} days (day shift, Mon-Fri); bars: range "
                 f"over seeds", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def main(argv):
    res = run()
    sens = sensitivity()
    dry = drying()
    print("drying:", json.dumps(dry))
    for m in (6.0, 20.0, 40.0):                         # the pedestal against the dryer's time
        rs = [simulate(dict(dry_s=(0.8 * m * 60, 1.2 * m * 60)), seed) for seed in range(3)]
        sens[f"pedestal, dryer {m:.0f} min"] = {k: round(float(np.mean([r[k] for r in rs])), 3) for k in
                                                ("pairs_per_calendar_day", "lathe_blocked_h_per_day", "lead_h_median")}
    for k, v in sens.items():
        print(f"  {k:40s} {v}")
    OUT.mkdir(exist_ok=True)
    (OUT / "machining_sim.json").write_text(json.dumps(dict(
        note="machining_sim.py: SimPy, part by part; times from machining.py, stoppages est. (BASE)",
        base={k: v for k, v in BASE.items() if k != "arm"} | {"arm_s": BASE["arm"]}, shift=SHIFT,
        week_days=WEEK_DAYS, days=DAYS, seeds=SEEDS, scenarios=res, fleet_wait_sensitivity=sens, drying_check=dry,
        drying_constants=DRY), indent=1))
    print(plot(res))


if __name__ == "__main__":
    main(sys.argv[1:])
