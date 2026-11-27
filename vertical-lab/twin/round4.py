"""Round 4 of the twin: building the lab while running real experiments, every route at its maximum throughput.

Round 3 asked what the finished vertical lab does in a year. Round 4 counts from the day the funding arrives, when
nothing of the cell has been ordered yet, and runs the campaigns on every route at once:

* **Build-out.** Each in-house station is ordered on day 0 and arrives after its procurement lead time (a draw around
  a stand-in median, ``BUILD``); it is installed once it and the room are there, commissioned, and then ramps up:
  slower jobs, more failed jobs and more breakdowns until it is through a learning curve. Until the two mobile
  manipulators and the Kardex are in and integrated (the cell), in-house stations are run by people on the day shift.
* **The learning curve** is fitted to the lab's own atomizer history (DAL PR 286, ``atomizer-runs/runs.csv`` at
  8320f13: ten runs, Oct 2 to Nov 13 2026; ``LEARN``): the chance that a job fails falls as P0 exp(-n / N_L) with the
  jobs done, the job takes F0 times as long at first, and a fifth of the first jobs end in an equipment fault.
* **Routes.** Every step of an action names a role (round 3's station keys: ``utah_midi`` is "an LPBF build",
  ``edm`` "a wire-EDM job"), and a router books it on whichever station of that role returns the result first, with the
  redos a ramping station would need counted (``Facility4.pick``): the in-house station once it is online, the BYU core
  facilities and the partners from day 0 (Utah's Aconity MIDI and MX-Lab, 3D Powder Tech, the Mines X2, outside
  testing, the Provo EDM service, Plastometrex's PIP service, NSL, Valimet). Policies still decide what to do; the
  router decides where.
* **Standing slots, filled late.** The partners' sessions are booked ahead as standing slots (Utah MIDI 3 builds a
  week, MX-Lab a session every three weeks, Mines every five, Valimet monthly). What goes into a slot is decided as
  late as possible: an action is admitted to a slot only once the slot starts within its shipping time plus a day
  (``Station.late_h``), so the policy has every result back by then that it could have.
* **Site offsets and provenance.** Each fabrication route has its own process offset (the same nominal laser power
  delivers a different effective power) and each testing route its own measurement offset (``OFFSETS``). The lab
  records the nominal settings unless someone has been on site to record the process in full (``opts['provenance']``),
  which costs a visit and leaves a quarter of the offset unknown.
* **Three plans** (``PLANS``): ``wait`` (build the cell, then start the campaigns in it, as round 3's vertical lab);
  ``parallel`` (start on day 0 on the existing atomizer and every partner route, move work in house as stations come
  online; the data from the partners warm-start the models); ``external`` (never build: BYU's own equipment and the
  partners only).

Everything is simulated, and the lead times, the partners' slots, fees and offsets are stand-ins (marked in the
tables) until the BOM's and the partners' own figures are available.
"""
from __future__ import annotations

import heapq
import itertools
import math

import numpy as np

from twin import campaign as C
from twin import facility as fac
from twin import supply

H, WEEK = 24.0, 168.0

# ------------------------------------------------------------------------------------------------- learning curve
# Fitted to DAL PR 286's atomizer-runs/runs.csv @ 8320f13 (the lab's own runs, AMAZEMET's two training runs left out):
# Oct 2, 6, 8, 21 no usable powder; Oct 22 "more powder than Oct 21, still below target" (counted as half); Oct 27
# about 91 % usable; Oct 28 about 3 %; Nov 5 the induction generator tripped mid-pour; Nov 10 about 75 %; Nov 13
# barely any, the hot shot burned the cup's seals and cracked its glass. With a mature run failing 10 % of the time,
# the chance of a learning failure on a station's (n+1)-th job is P0 exp(-n / N_L): maximum likelihood P0 = 1.0,
# N_L = 12.9 jobs (the profile likelihood is flat from about 5 to beyond 50 jobs). 10 runs in 43 days is 1.6 a week
# against the 5 a week of DAL #256's plan: a job takes F0 = 3 times as long at first. 2 of the 10 runs ended in an
# equipment fault (Q0 = 0.2), each down for days (MTTR median 72 h, assumed).
LEARN = dict(P0=1.0, N_L=12.9, F0=3.0, Q0=0.2, MTTR_H=72.0, P_MATURE=0.10, N_ATOMIZER_DAY0=10,
             source="DAL PR 286 atomizer-runs/runs.csv @ 8320f13 (10 runs, 2026-10-02 to 2026-11-13); fit in "
                    "twin/round4.py fit_learning()")
# instruments with the vendor's validated methods (SEM, XRD, ICP-MS, tensile frames ...) are assumed to start at a
# third of the process stations' failure chance, on the same curve
P0_INSTRUMENT = 0.3
PROCESS = {"utah_midi", "utah_mxlab", "edm", "shop", "doser", "sieve", "atomizer"}

ATOMIZER_RUNS = [  # (date, outcome as counted: 1 usable, 0.5 partial, 0 none, equipment fault)
    ("2026-10-02", 0.0, False), ("2026-10-06", 0.0, False), ("2026-10-08", 0.0, False), ("2026-10-21", 0.0, False),
    ("2026-10-22", 0.5, False), ("2026-10-27", 1.0, False), ("2026-10-28", 0.0, False), ("2026-11-05", 0.0, True),
    ("2026-11-10", 1.0, False), ("2026-11-13", 0.0, True)]


def fit_learning(p_mature=LEARN["P_MATURE"]):
    """Maximum-likelihood (P0, N_L) for the atomizer's runs, and the profile likelihood over N_L."""
    from scipy.optimize import minimize
    y = np.array([o for _, o, _ in ATOMIZER_RUNS])
    n = np.arange(len(y))

    def nll(p0, nl):
        ps = np.clip((1 - p_mature) * (1 - p0 * np.exp(-n / nl)), 1e-9, 1 - 1e-9)
        return float(-np.sum(y * np.log(ps) + (1 - y) * np.log(1 - ps)))

    prof = {}
    for nl in (3, 5, 8, 10, 12.9, 15, 20, 30, 50):
        r = min((minimize(lambda a: nll(1 / (1 + math.exp(-a[0])), nl), [x], method="Nelder-Mead")
                 for x in np.linspace(-2, 6, 9)), key=lambda r: r.fun)
        prof[nl] = (round(1 / (1 + math.exp(-r.x[0])), 3), round(r.fun, 3))
    return prof


# ------------------------------------------------------------------------------------------------- build-out
# Item keys are twin/econ.py's (_vertical()). (lead weeks, install weeks, commissioning weeks, source). No vendor has
# given a lead or installation time for any of these stations (PR 331's quote drafts ask; "nothing has been sent to
# any vendor"; PR 318: "There are no costs (#331 is where quotes go)"), so every lead here is a stand-in until the
# BOM's figures are available. Each includes BYU's purchase order, "ten days to two weeks PLUS shipping" (DAL PR 266
# lead-times.md L24-L27). A seed draws each around its median (lognormal, sigma 0.25).
PO_W = 2
BUILD = {
    # the room: the atomizer arrived Jun 11 2026 and was installed Sep 28, held up by the room's renovation
    # (electrical and chilled water by Jul 7; DAL #142, DAL #159): about 16 weeks
    "services": (16, 0, 2, "the atomizer room's renovation, Jun 11 to Sep 28 2026 (DAL #142, #159): 16 weeks"),
    "hoods": (PO_W + 8, 1, 0, "assumed"), "glovebox": (PO_W + 10, 1, 1, "assumed"),
    "shuttle": (PO_W + 12, 2, 2, "Kardex QuickShip 4-6 weeks for standard sizes, custom longer (PR 331 "
                                 "build_our_own_vlm.md L76): 12 weeks for two 9 m Shuttles, assumed"),
    "units": (PO_W + 12, 1, 4, "MiR250 + UR12e x2: assumed"),
    "couplings": (PO_W + 6, 1, 1, "CombiTac docks: assumed"), "ups": (PO_W + 4, 0, 0, "assumed"),
    "cameras": (PO_W + 2, 0, 0, "assumed"),
    "midi": (PO_W + 16, 2, 6, "Aconity's lead not found; comparable LPBF machines 12-16 weeks (Xact Metal 12, DAL "
                              "#133; AO Metal A30 12-16, DAL PR 245 lpbf-options.md L62): the top of that; "
                              "commissioning with Aconity's acceptance test and parameter qualification, assumed"),
    "mxlab": (PO_W + 24, 2, 6, "InssTek's lead not found (installation and training included, DAL PR 245 "
                               "ded-options.md L198): assumed, made in Korea"),
    "edm": (PO_W + 16, 2, 3, "assumed"),
    "instron": (PO_W + 14, 2, 2, "assumed"), "chamber": (PO_W + 14, 0, 1, "assumed"),
    "zwick": (PO_W + 8, 1, 1, "assumed"), "machining": (PO_W + 20, 2, 4, "PR 373's cell: assumed"),
    "icpms": (PO_W + 12, 1, 3, "assumed"), "sieve_cell": (PO_W + 10, 1, 2, "assumed"),
    "furnaces": (PO_W + 6, 0, 1, "assumed"), "sem": (PO_W + 8, 1, 1, "assumed"), "eds": (PO_W + 8, 0, 1, "assumed"),
    "ebsd": (PO_W + 14, 1, 2, "assumed"), "xrd": (PO_W + 8, 1, 1, "assumed"),
    "xrf": (PO_W + 10, 1, 4, "set-up 3-4 weeks (BYU's WDXRF, VCL PR 95 c-4972202625), applied here"),
    "mastersizer": (PO_W + 8, 1, 1, "assumed"), "hardness": (PO_W + 6, 0, 1, "assumed"),
    "nanoindenter": (PO_W + 14, 1, 2, "assumed"), "pip": (PO_W + 10, 0, 1, "assumed"),
    "vhx": (PO_W + 4, 0, 1, "assumed"), "polish": (PO_W + 6, 1, 1, "assumed (BYU already has an MX400 and PX500, "
                                                                     "ONR YIP field 10 L22)"),
    "carvera": (PO_W + 1, 0, 0, "assumed"), "doser": (PO_W + 14, 1, 3, "multi-doser carousel: assumed"),
    "floor_unit": (PO_W + 12, 1, 2, "assumed"), "cubxl": (0, 0, 0, "DAL's own CubXL is used from day 0"),
}
LEAD_SIGMA = 0.25
ROOM = ("services", "hoods", "glovebox")          # installation in the new room waits for its fit-out
CELL = ("units", "shuttle", "couplings")          # the robots run the stations round the clock once these are in
CELL_INTEGRATION_W = 8.0                          # programming and testing every station's transfers, assumed
# the twin's in-house stations and the econ items each needs (twin/econ.py's ``stations`` maps)
STATION_ITEMS = {
    "utah_midi@vcl": ("midi",), "utah_mxlab@vcl": ("mxlab",), "edm@vcl": ("edm",), "byu_sem@vcl": ("sem", "eds"),
    "byu_icpms@vcl": ("icpms",), "density@vcl": ("vhx",), "tensile@vcl": ("zwick", "instron"),
    "tensile_hot@vcl": ("instron", "chamber"), "sieve@vcl": ("sieve_cell",), "psd@vcl": ("mastersizer",),
    "doser@vcl": ("doser",), "shop@vcl": ("machining",), "xrd@vcl": ("xrd",), "xrf@vcl": ("xrf",),
    "prep@vcl": ("polish",), "hardness@vcl": ("hardness",), "nanoindent@vcl": ("nanoindenter",), "pip@vcl": ("pip",),
    "furnace@vcl": ("furnaces",),
}
DEPOSIT = (0.30, 100_000.0)                       # 30 % on order for items of $100k or more, the rest on delivery


def build_schedule(seed: int, plan: str) -> dict:
    """When each item arrives, is installed and commissioned (hours from funding), the payments, and when each
    in-house station and the cell come online. ``plan='external'`` builds nothing."""
    from twin import econ as E
    items = {it.key: it for it in E.items("vertical_lab")}
    rng = np.random.default_rng(60_000 + seed)
    out = dict(items={}, payments=[], stations={}, cell_h=None, start_h=0.0)
    if plan == "external":
        return out
    t_arr = {}
    for k in sorted(BUILD):
        lead_w, inst_w, com_w, src = BUILD[k]
        t_arr[k] = lead_w * WEEK * math.exp(rng.normal(0, LEAD_SIGMA)) if lead_w > 0 else 0.0
    room_h = max(t_arr[k] + BUILD[k][1] * WEEK + BUILD[k][2] * WEEK for k in ROOM)
    for k in sorted(BUILD):
        if k not in items:
            continue
        lead_w, inst_w, com_w, src = BUILD[k]
        it = items[k]
        if k == "cubxl" or it.kind == "owned":
            continue
        inst0 = t_arr[k] if k in ROOM else max(t_arr[k], room_h)
        inst1 = inst0 + inst_w * WEEK
        com1 = inst1 + com_w * WEEK
        out["items"][k] = dict(name=it.name, capex=it.capex, order_h=0.0, arrive_h=t_arr[k], install_h=inst0,
                               commission_h=inst1, online_h=com1, source=src)
        dep = DEPOSIT[0] if it.capex >= DEPOSIT[1] else 0.0
        if dep:
            out["payments"].append((0.0, it.capex * dep, k))
        out["payments"].append((t_arr[k], it.capex * (1 - dep), k))
    for st, its in STATION_ITEMS.items():
        out["stations"][st] = max(out["items"][k]["online_h"] for k in its if k in out["items"])
    cell = max(out["items"][k]["online_h"] for k in CELL) + CELL_INTEGRATION_W * WEEK
    out["cell_h"] = cell
    out["full_h"] = max([cell] + list(out["stations"].values()))
    out["start_h"] = out["full_h"] if plan == "wait" else 0.0
    out["payments"].sort()
    return out


# ------------------------------------------------------------------------------------------------- partner routes
# Standing slots (round 4): the partner's session is reserved ahead, so no booking lead at decision time, only the
# shipping lead (``ship_h``); what goes in is decided at most ``late_h`` before the slot starts.
STANDING = {
    # Utah's Aconity MIDI core facility: "$120/hr, self-run or assisted" (FLAIME genesis proposal L1003-L1004); the ONR
    # budget's $800 a build is unconfirmed. Its one real job: powder dropped off Apr 16, printing started Apr 23 (capstone
    # students first), parts done Apr 27 (DAL #138). Edison's estimate: about 8 builds a month. DAL #256: two-day
    # sessions, Tue-Wed. Round 4 holds a standing reservation of two builds a week (8 a month), Tue and Wed, parts 4
    # days after the start (the Apr 23-27 job); rounds 2-3 assumed 3 a week, which no source supports
    "utah_midi": dict(hours="24/7", starts=(8.0, 13.0), sat_starts=None, weekdays=(1, 2), attended_h=None,
                      per_period=(2, 7), booking_days=0.0, turnaround_days=4.0, ship_h=24.0, late_h=48.0,
                      source="FLAIME genesis L1003-L1004 ($120/h); ONR budget ($800 a build, unconfirmed); DAL #138 "
                             "(Apr 16 drop-off, Apr 23 start, Apr 27 parts); Edison: ~8 builds a month; DAL #256 "
                             "(Tue-Wed); standing reservation of 2 a week, round 4"),
    # Utah's InssTek MX-Lab (Fang group): about twelve half-day sessions a year (DAL PR 117), Tuesdays (DAL #256)
    "utah_mxlab": dict(hours="24/7", starts=(8.0,), sat_starts=None, weekdays=(1,), attended_h=None,
                       per_period=(1, 30), booking_days=0.0, turnaround_days=1.0, ship_h=24.0, late_h=48.0,
                       source="ONR YIP technical proposal L1265 ('about twelve half-day sessions a year', an "
                              "allowance until Fang sets a rate); DAL #256 (Tuesdays); rounds 2-3 had one per 21 days"),
    # Mines' FormAlloy X2: 3-7 sessions a year (DAL PR 117), 2 kg hoppers; "$155 per machine hour and $165 per labor
    # hour", about $795 a session or $1,204 with F&A (ONR YIP field 10, facilities page L35); powder shipped to Golden.
    # Round 4 takes the top of the range, 7 a year; "results in weeks" (turnaround never answered): 10 days as before
    "mines_x2": dict(hours="24/7", starts=(8.0,), sat_starts=None, weekdays=(2,), attended_h=None,
                     per_period=(1, 52), booking_days=0.0, turnaround_days=10.0, ship_h=5 * 24.0, late_h=6 * 24.0,
                     fee_usd=1204.0,
                     source="DAL PR 117 (3 machine h + 2 labour h a session, 3-7 sessions a year); ONR YIP field 10 "
                            "L35 ($155/machine h, $165/labour h; $1,204 a session with F&A); 7 a year; 10-day "
                            "turnaround and 5-day shipping assumed"),
    # Valimet's gas atomization: >= 50 kg, about $8k a run (FLAIME DAG); a monthly standing slot; the melt stock ships
    # two weeks ahead
    "valimet": dict(hours="24/7", starts=(8.0,), sat_starts=None, weekdays=(0,), attended_h=None,
                    per_period=(1, 28), booking_days=0.0, turnaround_days=21.0, ship_h=14 * 24.0, late_h=15 * 24.0,
                    source="FLAIME DAG (~$8k a run of >= 50 kg); monthly slot, 21-day turnaround as rounds 2-3"),
}
# partner routes that rounds 1-3 did not have (stand-ins)
EXTRA = [
    # 3D Powder Tech sells a small LPBF printer ("base pricing is $40,000") and has printed samples only toward a sale,
    # and its trial prints were poor (DAL #133). No printing service or rate exists: this route is hypothetical, a paid
    # sample service at one build a week, kept because the request names it; its offset is the largest of the printers
    fac.Station("lpbf_3dpt", "3D Powder Tech LPBF prints (hypothetical service)", 1, "24/7", fee_usd=1500.0,
                external=True, booking_days=0.0, turnaround_days=5.0, starts=(8.0,), weekdays=(3,),
                per_period=(1, 7), mtbf_h=800, mttr_h=72,
                source="DAL #133 (a printer vendor, $40k base; samples only toward a sale; poor trial prints): the "
                       "service, its fee, slot and turnaround are assumed (stand-ins)"),
    # no outside tensile or corrosion laboratory is named anywhere in DAL or byu-vcl: a stand-in at bofn-clocked's
    # price ($200 a bar outside, DAL PR 297 MODEL.md L45-L55)
    fac.Station("tensile_ext", "Outside testing laboratory (tensile, 3 bars; hypothetical)", 4, "day", fee_usd=600.0,
                external=True, booking_days=2.0, turnaround_days=8.0,
                source="no outside lab named (DAL, byu-vcl); $200 a bar as DAL PR 297 (bofn-clocked); about 10 days "
                       "with shipping, assumed"),
]
EXTRA_SHIP = {"lpbf_3dpt": (72.0, 96.0)}          # (ship_h, late_h) for the extra standing-slot routes
ROLE_EXTRA = {"utah_midi": ["lpbf_3dpt"], "tensile": ["tensile_ext"]}

# Site offsets (stand-ins; DAL #283 covers them at the method level). Fabrication: the effective laser power differs
# from the nominal one by a factor (1 + delta), delta ~ N(0, sigma) per site and seed. Testing: the reported yield
# and tensile strength read (1 + beta) of the truth. The lab's own stations are the reference (0).
OFFSETS = {
    "utah_midi": ("P_W", 0.05, "Utah's MIDI: same machine model, its own optics and calibration"),
    "lpbf_3dpt": ("P_W", 0.10, "3D Powder Tech: a different machine and gas flow"),
    "utah_mxlab": ("P_W", 0.05, "Utah's MX-Lab: same machine model"),
    "mines_x2": ("P_W", 0.10, "Mines' FormAlloy X2: a different machine, larger melt pool"),
    "tensile": ("ys", 0.02, "BYU's Instron frames"),
    "tensile_ext": ("ys", 0.04, "an outside laboratory's frames, grips and extensometry"),
}
# a visit to record the process in full: (usd, the share of the offset left unknown afterwards)
PROVENANCE = dict(usd={"utah_midi": 1500.0, "utah_mxlab": 1500.0, "lpbf_3dpt": 4000.0, "mines_x2": 4000.0,
                       "tensile_ext": 2500.0, "tensile": 500.0},
                  residual=0.25,
                  source="a person on site for the first job, recording settings, calibrations, gas, powder "
                         "handling and the build log: travel and two to three days, assumed")

PLANS = ("wait", "parallel", "external")

# Stages a promising alloy moves through after discovery (round 4; the same rule in every plan, for every policy). An
# alloy enters when its measured utility reaches the second target's level (T2), one at a time per campaign:
#   A. production-representative powder: a gas-atomized lot (Valimet for aluminium, >= 50 kg; Ames for copper, 25 kg,
#      as rounds 1-3), because the next two stages need kilograms the ultrasonic atomizer makes a few hundred grams
#      at a time, and not as a production atomizer would;
#   B. a distributed validation network: the gas lot made into parts and tested at every fabrication site of the plan
#      at once (aluminium: the in-house MIDI, Utah's MIDI, 3D Powder Tech; copper: the in-house MX-Lab, Utah's MX-Lab,
#      Mines' X2), each with its own process offset; it moves on when the first two sites have reported, and passes if
#      their mean true utility is at or above the state of the art (T1);
#   C. a full part in an application-specific performance test at an outside laboratory (aluminium: a printed
#      heat-exchanger or bracket in thermal-mechanical cycling, 6 weeks; copper: a DED repair on a seawater pump or
#      valve part, 60 days in flowing seawater).
# Money for the stages is a scale-up line of its own (FLAIME's DAG budgets six gas-atomization runs), so discovery's
# money is the same in every plan. Durations and fees of stage C are assumed.
STAGES = dict(
    gas={"flaime_al": ("valimet", 50.0), "onr_cu": ("ames", 25.0)},
    sites={"flaime_al": ("utah_midi@vcl", "utah_midi", "lpbf_3dpt"),
           "onr_cu": ("utah_mxlab@vcl", "utah_mxlab", "mines_x2")},
    site_h={"utah_midi@vcl": 8.0, "utah_midi": 8.0, "lpbf_3dpt": 8.0, "utah_mxlab@vcl": 8.0, "utah_mxlab": 4.0,
            "mines_x2": 5.0},
    app={"flaime_al": (42.0, 15_000.0, "a printed heat-exchanger or bracket, thermal-mechanical cycling"),
         "onr_cu": (60.0, 20_000.0, "a DED repair on a seawater pump or valve part, 60 days in flowing seawater")},
)


class Resource4(fac.Resource):
    """A station of round 4: available from ``online_h``, and with a learning state (jobs done, curve)."""

    def __init__(self, st, rng, horizon_h, online_h=0.0, curve=None, n0=0):
        super().__init__(st, rng, horizon_h)
        self.online_h = online_h
        self.curve = curve                        # (P0, N_L, F0, Q0) or None for a mature station
        self.n = n0
        self.n0 = n0
        self.redos = 0
        self.faults = 0
        if online_h > 0:
            self.down = [(a, b) for a, b in self.down if b > online_h]

    def find(self, t, dur, campaign, changeover_h=0.0, empty=False):
        return super().find(max(t, self.online_h), dur, campaign, changeover_h, empty)

    def p_fail(self):
        if not self.curve:
            return 0.0
        return self.curve[0] * math.exp(-self.n / self.curve[1])

    def factor(self):
        if not self.curve:
            return 1.0
        return 1.0 + (self.curve[2] - 1.0) * math.exp(-self.n / self.curve[1])

    def q_fault(self):
        if not self.curve:
            return 0.0
        return self.curve[3] * math.exp(-self.n / self.curve[1])


class Facility4(fac.Facility):
    """Round 4's facility: BYU's own equipment and core facilities and the partners from day 0, the in-house stations
    from their build-out dates, a router over each role's stations."""

    def __init__(self, plan: str, seed: int, horizon_h: float, opts: dict | None = None):
        assert plan in PLANS, plan
        self.kind = "r4_" + plan
        self.plan = plan
        self.physical = True
        self.opts = dict(opts or {})
        self.sched = self.schedule(seed, plan)
        self.start_h = self.sched["start_h"]
        self.cell_h = self.sched.get("cell_h")
        rng = np.random.default_rng(30_000 + seed)
        base = fac.facility("proposed", physical=True)
        stations = dict(base)
        drop = set(self.opts.get("drop_routes") or ())
        if plan in ("parallel", "external"):
            for k, over in STANDING.items():
                for f_, x in over.items():
                    if f_ not in ("ship_h", "late_h", "source"):
                        setattr(stations[k], f_, x)
                stations[k].source = over["source"]
            for s in EXTRA:
                stations[s.key] = fac.Station(**s.__dict__)
        if plan in ("wait", "parallel"):
            for s in fac.VERTICAL:
                stations[s.key + "@vcl"] = fac.Station(**dict(s.__dict__, key=s.key + "@vcl"))
            pv = fac.PHYSICAL["vertical_lab"]
            fv = fac.Station(**dict(stations["furnace"].__dict__, key="furnace@vcl",
                                    name="Two Nabertherm furnaces x 4 positions (in house, robots load)"))
            for f_, x in pv["furnace"].items():
                setattr(fv, f_, x)
            stations["furnace@vcl"] = fv
            stations["robot"] = fac.Station(**pv["robot"].__dict__)
        self.ship = {k: (v["ship_h"], v["late_h"]) for k, v in STANDING.items()} if plan != "wait" else {}
        self.ship.update(EXTRA_SHIP if plan != "wait" else {})
        self.res = {}
        n_atom0 = int(self.opts.get("atomizer_n0", LEARN["N_ATOMIZER_DAY0"]))
        learn = self.opts.get("learn", True)
        for k, s in stations.items():
            online = self.sched["stations"].get(k, 0.0)
            curve, n0 = None, 0
            if learn and (k.endswith("@vcl") or k == "atomizer"):
                role = k.split("@")[0]
                p0 = LEARN["P0"] if role in PROCESS else P0_INSTRUMENT
                curve = (p0, LEARN["N_L"], LEARN["F0"] if role in PROCESS else 1.0 + (LEARN["F0"] - 1.0) / 3.0,
                         LEARN["Q0"] if role in PROCESS else LEARN["Q0"] / 3.0)
                n0 = n_atom0 if k == "atomizer" else 0
            self.res[k] = Resource4(s, rng, horizon_h, online, curve, n0)
        # the routes: each role's stations (a plan uses the ones it has); 'wait' is round 3's vertical lab: in house,
        # plus the outside services round 3's vertical lab kept (Mines, NSL, Valimet, Ames)
        self.routes = {}
        for k in list(self.res):
            role = k.split("@")[0]
            if k in ("robot", "operator"):
                continue
            self.routes.setdefault(role, [])
            if "@" in k or k not in ROLE_EXTRA.get(role, []):
                self.routes[role].append(k)
        for role, extra in ROLE_EXTRA.items():
            for k in extra:
                if k in self.res:
                    self.routes.setdefault(role, []).append(k)
                    self.routes.setdefault(k, [k])
        for role in list(self.routes):
            ks = [k for k in self.routes[role] if k not in drop]
            if plan == "wait":
                vcl = [k for k in ks if k.endswith("@vcl")]
                if vcl:
                    ks = vcl
            self.routes[role] = ks
        self.rng = np.random.default_rng(40_000 + seed)
        self.orng = np.random.default_rng(50_000 + seed)
        self.helper_misses = 0
        self.now = 0.0
        # site offsets: the truth's, and the lab's estimate (0 unless someone recorded the process on site)
        mult = float(self.opts.get("offset_mult", 1.0))
        self.offset = {k: float(self.orng.normal(0, sd * mult)) for k, (_, sd, _) in OFFSETS.items()}
        self.offset_known = {k: None for k in OFFSETS}       # time a provenance visit was made
        self.offset_est = {k: 0.0 for k in OFFSETS}
        prov = self.opts.get("provenance") or ()
        self.prov_sites = set(OFFSETS) if prov == "all" else set(prov)
        self.prov_log = []
        self.route_log = []                                # (t, campaign, role, station, what)

    def schedule(self, seed, plan) -> dict:
        """The build-out (round 4's ``build_schedule``; round 5 overrides it with the facility window and used
        equipment)."""
        return build_schedule(seed, plan)

    # ------------------------------------------------------------------------------------------ availability
    def online(self, k, t) -> bool:
        r = self.res.get(k)
        return r is not None and r.online_h <= t + 1e-9

    def cands(self, role, t=None, slack_h=0.0):
        ks = self.routes.get(role)
        if ks is None:
            ks = [role] if role in self.res else []
        if t is None:
            return ks
        return [k for k in ks if self.res[k].online_h <= t + slack_h]

    def robots_on(self, t) -> bool:
        return self.cell_h is not None and t >= self.cell_h and "robot" in self.res

    # ------------------------------------------------------------------------------------------ the router
    def expected_result(self, k, t, hours, campaign, what):
        r = self.res[k]
        st = r.st
        h = self.adjust(k, hours, what, campaign) * r.factor()
        t0 = t + self.ship.get(k, (0.0, 0.0))[0]
        if st.external and st.booking_days:
            t0 += st.booking_days * H
        s, d, _ = r.find(t0, max(h, 0.01), campaign)
        p = min(r.p_fail(), 0.9)
        end = s + d + p / (1 - p) * d
        back = st.turnaround_days * H + self.ship.get(k, (0.0, 0.0))[0] * (0.5 if st.external else 0.0)
        return end + back, s

    def pick(self, role, t, hours, campaign, what):
        """The station of a role that returns the result first (ties: the cheaper); a concrete key is itself."""
        ks = self.cands(role, t, 0.0)
        if not ks:
            ks = self.cands(role)            # nothing of this role is online yet: the earliest that will be
        if len(ks) == 1:
            return ks[0]
        best, bk = None, None
        for k in ks:
            res, _ = self.expected_result(k, t, hours, campaign, what)
            key = (round(res, 3), self.res[k].st.fee_usd)
            if best is None or key < best:
                best, bk = key, k
        return bk

    def primary(self, role, t):
        """The station of a role an estimate prices by: in house once online, else the first of its routes."""
        ks = self.cands(role, t, 0.0) or self.cands(role)
        for k in ks:
            if k.endswith("@vcl"):
                return k
        return ks[0] if ks else role

    # ------------------------------------------------------------------------------------------ booking
    def helpers(self, station: str, dur: float, t: float = 0.0) -> list:
        from twin import econ as E
        if station in fac.NO_HELPER or station not in self.res:
            return []
        role = station.split("@")[0]
        st = self.res[station].st
        if station.endswith("@vcl") and self.robots_on(t):
            return [("robot", fac.ROBOT_H[0])]
        if st.external and station not in ("utah_midi", "utah_mxlab"):
            a = E.HANDS_ON.get(role, (0.5, 0.0, ""))[0]
            return [("operator", a)] if a > 0 else []
        a, b, _ = E.HANDS_ON.get(role, (0.25, 1.0, ""))
        h = min(a + b * dur, 8.0)
        if st.attended_h is not None:
            h = min(h, max(st.attended_h, a))
        if role == "atomizer":
            h = min(st.attended_h or 1.0, dur)
        return [("operator", h)] if h > 0 else []

    def run_step_joint(self, station: str, ready: float, dur: float, campaign: str, what: str, changeover_h=0.0,
                       tag=None):
        r = self.res[station]
        st = r.st
        t0 = ready + self.ship.get(station, (0.0, 0.0))[0]
        if st.external and st.booking_days:
            t0 = ready + st.booking_days * H * math.exp(self.rng.normal(0, 0.35))
        hl = self.helpers(station, dur, t0)
        t = t0
        found = []
        s = d = i = None
        for _ in range(400):
            s, d, i = r.find(t, dur, campaign, changeover_h)
            hl = self.helpers(station, dur, s)
            found, ok = [], True
            for hk, hh in hl:
                hr = self.res[hk]
                s2, d2, i2 = hr.find(s, hh, campaign)
                if s2 > s + 1e-6:
                    t, ok = s2, False
                    break
                found.append((hr, s2, d2, i2))
            if ok:
                break
        else:
            self.helper_misses += 1
            found = []
        handle = r.commit(s, d, i, campaign, what, tag)
        for hr, s2, d2, i2 in found:
            hr.commit(s2, d2, i2, campaign, what, dict(tag or {}, helper_for=station))
        lag = st.turnaround_days * H * math.exp(self.rng.normal(0, 0.4)) if st.turnaround_days else 0.0
        if station in self.ship and st.external:
            lag += 0.5 * self.ship[station][0]               # the parts come back
        cost = st.fee_usd + st.rate_usd_h * dur
        return s, s + d, s + d + lag, cost, handle

    def queue_wait(self, station: str, ready: float, dur: float, campaign: str) -> float:
        r = self.res[station]
        st = r.st
        t = ready + self.ship.get(station, (0.0, 0.0))[0]
        if st.external and st.booking_days:
            t += st.booking_days * H
        s1, _, _ = r.find(t, dur, campaign)
        s0, _, _ = r.find(t, dur, campaign, empty=True)
        return s1 - s0

    def job_done(self, station: str, t_end: float, campaign: str, what: str) -> tuple:
        """A job on a learning station ends: did it work (False: it must be redone), and is the station down after
        it (an equipment fault)? The atomizer's failures are the run's own (Campaign4.charge_plan), so it is never
        redone here."""
        r = self.res[station]
        if not r.curve:
            return True, t_end
        p, q = r.p_fail(), r.q_fault()
        r.n += 1
        ok = True
        if station != "atomizer" and self.rng.random() < p:
            ok = False
            r.redos += 1
        t_next = t_end
        if self.rng.random() < q:
            dd = LEARN["MTTR_H"] * math.exp(self.rng.normal(0, 0.5))
            r.down.append((t_end, t_end + dd))
            r.faults += 1
            t_next = t_end + dd
            if station != "atomizer":
                ok = False
        return ok, t_next

    # ------------------------------------------------------------------------------------------ reports
    def monthly(self, horizon_h: float, month_h: float = 30.4 * 24.0) -> dict:
        """Per station: busy unit-hours and jobs per month, and utilization against the unit-hours its calendar
        offered while it was online."""
        n_m = int(math.ceil(horizon_h / month_h))
        out = {}
        for k, r in self.res.items():
            busy = np.zeros(n_m)
            jobs = np.zeros(n_m)
            for j in r.jobs:
                a, b = j[0], j[1]
                if a >= horizon_h:
                    continue
                m0 = int(a // month_h)
                jobs[min(m0, n_m - 1)] += 1
                bb = min(b, horizon_h)
                for m in range(m0, min(int(bb // month_h), n_m - 1) + 1):
                    busy[m] += max(0.0, min(bb, (m + 1) * month_h) - max(a, m * month_h))
            avail = np.zeros(n_m)
            for m in range(n_m):
                a, b = m * month_h, min((m + 1) * month_h, horizon_h)
                a = max(a, r.online_h)
                if b > a:
                    avail[m] = _cal_hours(r.st.hours, a, b) * r.st.units
            if busy.sum() <= 0 and r.online_h >= horizon_h:
                continue
            out[k] = dict(busy=[round(x, 2) for x in busy], jobs=[int(x) for x in jobs],
                          avail=[round(x, 1) for x in avail], online_h=round(r.online_h, 1),
                          external=bool(r.st.external), units=r.st.units, hours=r.st.hours,
                          redos=r.redos, faults=r.faults, n_jobs=r.n - r.n0)
        return out


def _cal_hours(cal, a, b):
    if cal == "24/7":
        return b - a
    per_week = 54.0 if cal == "day6" else 45.0
    return (b - a) / WEEK * per_week


class Campaign4(C.Campaign):
    """A campaign on round 4's facility: each step goes to the station of its role that returns the result first."""

    start_h = 0.0

    def __init__(self, spec, policy, market, facility, horizon_h):
        self._vertical_flag = False
        super().__init__(spec, policy, market, facility, horizon_h)
        self._last_route = []
        self.prov_usd = 0.0

    @property
    def vertical(self):
        """For the policies: the in-house DED station is online (1 kg deposits in house, no NSL certificate)."""
        f = self.fac
        return f.online("utah_mxlab@vcl", getattr(self, "now_h", 0.0)) if isinstance(f, Facility4) else \
            self._vertical_flag

    @vertical.setter
    def vertical(self, v):
        self._vertical_flag = v

    # ---------------------------------------------------------------------------------------- routing
    def _route(self, steps, ready_h, what, changeover=False, tag=None, handles=None):
        t, usd = ready_h, 0.0
        tag = dict(tag or {}, what=what)
        res_t = t
        self._last_route = []
        F = self.fac
        for role, hours in steps:
            if role.startswith("="):                  # a named station, not routed (the validation network's sites)
                role = st = role[1:]
            else:
                st = F.pick(role, t, hours, self.key, what)
            hours = F.adjust(st, hours, what, self.key)
            if hours <= 0 and role not in ("nsl",):
                continue
            R = F.res[st]
            cal = R.st
            for attempt in range(4):
                h_all = max(hours * R.factor(), 0.01)
                chunk = 8.0 if (cal.hours != "24/7" and cal.attended_h is None) else h_all
                left, first = h_all, True
                e = t
                while left > 1e-9:
                    h = min(left, chunk)
                    s, e, r, c, hd = F.run_step_joint(st, t, h, self.key, what,
                                                      C.CHANGEOVER_H if (changeover and role == "atomizer") else 0.0,
                                                      dict(tag, route=st, attempt=attempt))
                    if handles is not None:
                        handles.append((st, hd))
                    usd += self.market.service_price(c if first else c - cal.fee_usd, s / H)
                    first = False
                    left -= h
                    t, res_t = e, r
                ok, t_next = F.job_done(st, e, self.key, what)
                if ok:
                    break
                t = max(t_next, res_t)
            F.route_log.append((round(ready_h, 2), self.key, role, st, what))
            self._last_route.append((role, st))
        return max(res_t, t), usd

    def _route_of(self, role):
        for r, st in self._last_route:
            if r == role:
                return st
        return None

    GATE = {"blend_ded": ([("doser", 0.5)], "utah_mxlab", 3.0), "print": ([], "utah_midi", 5.0),
            "promote": ([], "utah_midi", 8.0), "test": ([], "edm", 0.75), "section": ([], "prep", 1.5),
            "preplaced": ([], "utah_mxlab", 4.0), "small_ded": ([], "utah_mxlab", 4.0),
            "tensile": ([("shop", 1.0)], "tensile", 0.6), "screen": ([], "cubxl", 1.2),
            "immersion": ([], "immersion", 720.0)}

    def gate(self, a):
        k = a.get("kind")
        if k == "large_ded":
            if self.fac.online("utah_mxlab@vcl", self.now_h):
                return [], "utah_mxlab@vcl", 8.0
            return [], "mines_x2", 5.0
        if k in ("powder", "pip"):
            return super().gate(a)
        return self.GATE.get(k)

    def gate_ok(self, a, now_h) -> bool:
        """Round 3's admission rule over every route of the gating role: some station of it takes the action within
        GATE_W of when the part gets there; a standing slot only once it starts within its shipping time plus a day
        (decided as late as possible)."""
        self.now_h = now_h
        g = self.gate(a)
        if g is None:
            return True
        pre, role, h = g
        F = self.fac
        t = now_h
        for s_, hh in pre:
            k = F.pick(s_, t, hh, self.key, a.get("kind", ""))
            R = F.res[k]
            cal = R.st
            chunk = 8.0 if (cal.hours != "24/7" and cal.attended_h is None) else max(hh, 0.01)
            left = max(hh * R.factor(), 0.01)
            while left > 1e-9:
                s0, d0, _ = R.find(t, min(left, chunk), self.key)
                t, left = s0 + d0, left - min(left, chunk)
        for k in F.cands(role, now_h, self.GATE_W):
            R = F.res[k]
            hh = h * R.factor()
            if F.queue_wait(k, t, hh, self.key) > self.GATE_W:
                continue
            if k in F.ship:
                s, _, _ = R.find(t + F.ship[k][0], hh, self.key)
                if s - now_h > F.ship[k][1] + self.GATE_W:
                    continue
            return True
        return False

    # standing slots a campaign holds, and the action that fills one (its estimate is the slot's money)
    SLOT_ROLES = {"flaime_al": {"utah_midi": "print"}, "onr_cu": {"utah_mxlab": "small_ded", "mines_x2": "large_ded"}}

    def reserve(self, now_h) -> float:
        """Money kept for the campaign's standing slots of the coming week that are not yet filled: a lab with two
        builds a week reserved at Utah keeps their money for them, so that cheaper work decided in the meantime does
        not spend it before the slot's content is decided (as late as possible)."""
        F = self.fac
        tot = 0.0
        for role, kind in self.SLOT_ROLES.get(self.key, {}).items():
            for k in F.cands(role, now_h, 0.0):
                if k not in F.ship:
                    continue
                R = F.res[k]
                n, days = R.st.per_period or (1, 7)
                per_week = n * 7.0 / days
                booked = sum(1 for s in R.period_starts if now_h <= s <= now_h + WEEK)
                free = max(0.0, per_week - booked)
                if free > 0:
                    fee = R.st.fee_usd
                    tot += free * (fee + (215.0 if kind == "print" else 140.0 if kind == "small_ded" else 210.0))
        return tot

    KANBAN_WEEKS = 2.0

    def first_step_capacity(self, now_h) -> float:
        """Jobs a week the routes of a lot's first fabrication step can take now (aluminium: LPBF builds; copper:
        small DED deposits and blend screens): a partner's standing slots, or an in-house station's hours over the
        job's (ramp-up slowed) hours, round the clock once the robots run it, two starts a day before."""
        F = self.fac
        role, h = ("utah_midi", 5.0) if self.key == "flaime_al" else ("utah_mxlab", 4.0)
        cap = 0.0
        for k in F.cands(role, now_h, 0.0):
            R = F.res[k]
            if k in F.ship or R.st.per_period:
                n, d = R.st.per_period or (1, 7)
                cap += n * 7.0 / d
            else:
                cap += (168.0 / (h * R.factor())) if F.robots_on(now_h) else 12.0 / R.factor()
        return cap

    KANBAN_FRESH_D = 14.0

    def waiting_lots(self, now_h) -> int:
        """Lots in the making, and lots made in the last two weeks that have not had their first build (aluminium)
        or deposit (copper). An older lot the policy has not built from is one it chose not to (poor powder, a better
        design since), and does not hold up new designs."""
        used = {B["lot"] for B in self.builds.values()} | {D.get("lot") for D in self.deposits.values()}
        used |= {pt.get("lot") for pt in self._part_truth.values()}
        n = sum(1 for i, L in self.lots.items() if i not in used and L["remaining_g"] >= 30.0 and
                L.get("t", 0.0) >= now_h - self.KANBAN_FRESH_D * H)
        # powders started in the last two weeks (one waiting months for an out-of-stock metal holds nothing up)
        return n + sum(1 for p in self.pending.values() if p["kind"] == "powder" and
                       p["t"] >= now_h - self.KANBAN_FRESH_D * H)

    def submit3(self, a: dict, now_h: float) -> str:
        """Round 3's admission, with two round-4 rules for every policy: (1) the standing slots' reserve: an action
        that does not fill a slot may use the spending plan's room only beyond what the coming week's unfilled slots
        need; (2) a WIP limit before the bottleneck: a new design starts only while the lots waiting for their first
        build or deposit are fewer than KANBAN_WEEKS of those routes' capacity (at least 3), so that a policy blind
        to partner capacity cannot spend the money on powders nobody can print."""
        k = a.get("kind")
        if k == "powder" and not a.get("into"):
            lim = max(3.0, self.KANBAN_WEEKS * self.first_step_capacity(now_h))
            if self.waiting_lots(now_h) >= lim:
                self.status_log["kanban"] = self.status_log.get("kanban", 0) + 1
                self.status_log["capacity"] = self.status_log.get("capacity", 0) + 1
                return "capacity"
        g = self.gate(a) if k != "stop" else None
        slot = g is not None and g[1] in self.SLOT_ROLES.get(self.key, {})
        if k != "stop" and not slot:
            self.now_h = now_h
            est = self.estimate(a)
            if est > 50.0 and est <= self.budget_left and self.spent + est <= self.plan(now_h) and \
                    self.spent + est + self.reserve(now_h) > self.plan(now_h):
                self.status_log["plan_reserve"] = self.status_log.get("plan_reserve", 0) + 1
                self.status_log["plan"] = self.status_log.get("plan", 0) + 1
                return "plan"
        return super().submit3(a, now_h)

    def load(self, station: str, t_h: float, window_h: float = 72.0) -> float:
        ks = self.fac.cands(station, t_h, 0.0) if isinstance(self.fac, Facility4) else [station]
        if not ks:
            return 1.0
        return min(C.Campaign.load(self, k, t_h, window_h) for k in ks)

    def charge_plan(self, a) -> tuple:
        cm3, kg, run_h, extra, p_add = super().charge_plan(a)
        R = self.fac.res.get("atomizer")
        if isinstance(R, Resource4) and R.curve:
            p_add = 1.0 - (1.0 - p_add) * (1.0 - R.p_fail())
        return cm3, kg, run_h, extra, p_add

    def estimate(self, action) -> float:
        """Round 3's estimate, priced at each role's primary station now (in house once online)."""
        k = action["kind"]
        A = C.ACTIONS[self.key]
        if "usd" in A.get(k, {}):
            return A[k]["usd"]
        t = getattr(self, "now_h", 0.0)
        F = self.fac

        def fee(role):
            return F.res[F.primary(role, t)].st.fee_usd

        def rate(role):
            return F.res[F.primary(role, t)].st.rate_usd_h
        feed = self._feed_cost(action) if k == "powder" else 0.0
        if k == "gas_atomize":
            st = "valimet" if self.key == "flaime_al" else "ames"
            return F.res[st].st.fee_usd + self._gas_feed(action)
        if k == "section":
            return 30.0 + fee("prep") + rate("byu_sem") * 1.0 + fee("xrd") + rate("xrd") * 0.75
        if k == "pip":
            return 10.0 + fee("pip") + fee("prep")
        if k == "blend_ded":
            return 25.0 + fee("utah_mxlab") + 0.3 * 300.0 + 40.0
        if self.key == "flaime_al":
            if k == "powder":
                n = action.get("runs", 1)
                f = int(action.get("crucible_cm3") or self.spec.crucible_cm3) / 225.0
                return n * (20 * f + 6.3 + 120 + 37.5 * (1.0 + 0.6 * (f - 1))) + 15 + (35 if action.get("icp") else 0) \
                    + 40 + feed
            if k == "print":
                return fee("utah_midi") + 80 + 90 + 45
            if k == "test":
                return fee("edm") + 120 + (60 if action.get("hot") else 0) + fee("tensile")
            if k == "promote":
                return fee("utah_midi") * 1.5 + 80 + 90 + fee("edm") + 120 + 120
        else:
            if k == "powder":
                n = action.get("runs", 1)
                f = int(action.get("crucible_cm3") or self.spec.crucible_cm3) / 225.0
                return n * (60 * f + 14.4 + 350 + 120 + 75 * (1.0 + 0.6 * (f - 1))) + 15 + 40 + feed
            if k == "nsl":
                return F.res["nsl"].st.fee_usd
            if k in ("preplaced", "small_ded"):
                return fee("utah_mxlab") + 40 + (60 if k == "small_ded" else 30) + 40
            if k == "large_ded":
                if F.online("utah_mxlab@vcl", t):
                    return F.res["utah_mxlab@vcl"].st.fee_usd + 80 + 60
                return F.res["mines_x2"].st.fee_usd + 150 + 60
            if k == "tensile":
                return 120 + fee("tensile")
            if k == "screen":
                return 35
            if k == "immersion":
                return 30 + 140
        return 0.0

    # ---------------------------------------------------------------------------------------- site offsets
    def _visit(self, station, t_h):
        """Provenance: someone goes on site with the first job there and records the process in full."""
        F = self.fac
        if station not in F.prov_sites or F.offset_known.get(station) is not None:
            return
        F.offset_known[station] = t_h
        sd = OFFSETS[station][1] * float(F.opts.get("offset_mult", 1.0))
        F.offset_est[station] = F.offset[station] + float(F.orng.normal(0, PROVENANCE["residual"] * sd))
        usd = PROVENANCE["usd"].get(station, 2500.0)
        self.charge(t_h, usd, f"provenance visit {station}")
        self.prov_usd += usd
        F.prov_log.append((round(t_h, 2), self.key, station, usd))

    def _proc_offset(self, station, params, t_h):
        """(params the part is built with, params the lab records) at a fabrication station."""
        F = self.fac
        if station not in OFFSETS or OFFSETS[station][0] != "P_W":
            return params, params
        self._visit(station, t_h)
        d, dh = F.offset[station], F.offset_est[station]
        eff = [dict(p, P_W=p["P_W"] * (1 + d)) if isinstance(p, dict) and "P_W" in p else p for p in params]
        rec = [dict(p, P_W=p["P_W"] * (1 + d) / (1 + dh)) if isinstance(p, dict) and "P_W" in p else p
               for p in params]
        return eff, rec

    def _meas_offset(self, station, m, t_h):
        F = self.fac
        if station not in OFFSETS or OFFSETS[station][0] != "ys":
            return m
        self._visit(station, t_h)
        f = (1 + F.offset[station]) / (1 + F.offset_est[station])
        return dict(m, ys_MPa=m["ys_MPa"] * f, uts_MPa=m["uts_MPa"] * f)

    # ---------------------------------------------------------------------------------------- actions with routes
    def _do_print(self, a, now_h):
        L = self._lot(a["lot"])
        need = self.PRINT_FILL_G
        if L["remaining_g"] < need:
            return False
        L["remaining_g"] -= need
        params = a["params"][:9]
        st0 = self.fac.pick("utah_midi", now_h, 5.0, self.key, "print")
        ready = self._materials({"build_plate": 1.0, "argon": 1.0 if st0.endswith("@vcl") else 0.0}, now_h)
        bid = next(self.ids)
        tag = dict(design=L["design"], node="print", lot=a["lot"], sample=f"B{bid}")
        t_r, usd = self._route([("utah_midi", 5.0), ("density", 0.5), ("byu_sem", 1.0)], ready, "print", tag=tag)
        self.charge(now_h, usd, "print")
        st = self._route_of("utah_midi")
        eff, rec = self._proc_offset(st, params, now_h)
        lt = self._lot_truth[a["lot"]]
        lot = dict(lt, composition=lt["composition"])
        parts, meas = [], []
        for p, pr in zip(eff, rec):
            part = self.truth.build(lot, p, self.rng)
            part["reuse"] = lt.get("reuse", 0.0)
            parts.append(part)
            meas.append(dict(self._soundness(part, L["design"]), params=pr))
        back, stt = self._return_powder(a["lot"], need, self.PRINT_FUSED_G, eff[0])
        self._part_truth[bid] = dict(parts=parts, lot=a["lot"], bars_at=int(a.get("bars_at", 0)), route=st)
        self._emit(t_r, dict(type="build", id=bid, lot=a["lot"], design=L["design"], measured=meas,
                             bars_at=int(a.get("bars_at", 0)), returned_g=back, returned_state=stt))
        return True

    def _ded(self, a, now_h, mode, grams, steps, substrates):
        L = self._lot(a["lot"])
        if L["remaining_g"] < grams:
            return False
        L["remaining_g"] -= grams
        ready = self._materials({"ded_substrate": substrates} if substrates else {}, now_h)
        node = {"preplaced": "ded_small", "blown_small": "ded_small", "blown_large": "ded_large"}[mode]
        dep = next(self.ids)
        t_r, usd = self._route(steps, ready, mode, tag=dict(design=L["design"], node=node, lot=a["lot"],
                                                            sample=f"D{dep}"))
        self.charge(now_h, usd, mode)
        st = self._last_route[0][1] if self._last_route else steps[0][0]
        lot = self._lot_truth[a["lot"]]
        params = a["params"] if isinstance(a["params"], list) else [a["params"]]
        params = params[:(4 if mode != "blown_large" else 1)]
        eff, rec = self._proc_offset(st.split("@")[0] if not st.endswith("@vcl") else st, params, now_h)
        did = L["design"]
        nab = {"Al": 9.2, "Ni": 4.5, "Fe": 4.0, "Mn": 1.2}
        parts, meas = [], []
        for p, pr in zip(eff, rec):
            part = self.truth.deposit(lot, p, mode, self.rng, substrate=nab if mode != "blown_small" else None)
            part["reuse"] = lot.get("reuse", 0.0)
            parts.append(part)
            m = dict(self._soundness(part, did), dilution=part["dilution"] * math.exp(self.rng.normal(0, 0.1)),
                     params=pr)
            if mode != "preplaced":
                m.update(beta_prime=float(np.clip(part["beta_prime"] + self.rng.normal(0, 0.03), 0, 1)),
                         catchment=part["catchment"] * math.exp(self.rng.normal(0, 0.05)),
                         grain_um=part["grain_um"] * math.exp(self.rng.normal(0, 0.1)))
            if part["fusion_ok"] is not None:
                m["fusion_ok"] = part["fusion_ok"] if self.rng.random() > 0.05 else (not part["fusion_ok"])
            meas.append(m)
        catch = float(np.mean([pp["catchment"] for pp in parts])) if parts else 0.6
        back, stt = self._return_powder(a["lot"], grams, None, eff[0], mode="ded", catchment=catch) \
            if mode != "preplaced" else (0.0, None)
        self._part_truth[dep] = dict(parts=parts, lot=a["lot"], mode=mode, route=st)
        self._emit(t_r, dict(type="deposit", id=dep, lot=a["lot"], design=did, mode=mode, measured=meas,
                             returned_g=back, returned_state=stt))
        return True

    def _do_large_ded(self, a, now_h):
        L = self._lot(a["lot"])
        F = self.fac
        if F.online("utah_mxlab@vcl", now_h) and L["remaining_g"] >= 1000.0:
            return self._ded(a, now_h, "blown_large", 1000.0, [("utah_mxlab@vcl", 8.0), ("byu_sem", 1.0)], 1.0)
        if "mines_x2" in F.cands("mines_x2") and L.get("nsl") and L["remaining_g"] >= 2000.0:
            return self._ded(a, now_h, "blown_large", 2000.0, [("mines_x2", 5.0), ("byu_sem", 2.0)], 1.0)
        return False

    def _do_test(self, a, now_h):
        B = self.builds.get(a["build"])
        if B is None or B.get("tested"):
            return False
        B["tested"] = True
        steps = [("edm", 0.75), ("furnace", 3.0), ("shop", 1.0), ("tensile", 0.6)]
        if a.get("hot"):
            steps.append(("tensile_hot", 1.5))
        t_r, usd = self._route(steps, now_h, "test", tag=dict(design=B["design"], node="test", sample=f"B{a['build']}"))
        self.charge(now_h, usd + 120.0, "test (3 specimens machined)")
        st = self._route_of("tensile")
        pt = self._part_truth[a["build"]]
        part = pt["parts"][pt["bars_at"]]
        s = self.truth.strength(part)
        hot = self.truth.strength(part, 250.0) if a.get("hot") else None
        smp = self._psample(part, B["design"], hot=bool(a.get("hot")))
        m = self._meas_offset(st, self._m("tensile", smp), now_h)
        meas = dict(ys_MPa=m["ys_MPa"], uts_MPa=m["uts_MPa"], el_pct=m["el_pct"], n_bars=m.get("n_bars", 3))
        if hot:
            mh = self._m("tensile_hot", smp)
            meas["hot_ys_MPa"] = mh["ys_MPa"]
        u, det = self._al_score(part, s, hot)
        det.update(route_fab=pt.get("route"), route_test=st, meas_ys=meas["ys_MPa"], meas_el=meas["el_pct"])
        self._emit(t_r, dict(type="test", build=a["build"], design=B["design"], measured=meas,
                             params=B["measured"][pt["bars_at"]]["params"], score=(u, det)))
        return True

    def _do_tensile(self, a, now_h):
        D, part = self._dep(a["deposit"])
        if D["mode"] == "preplaced" or "tensile" in D:
            return False
        D["tensile"] = "pending"
        t_r, usd = self._route([("shop", 1.0), ("tensile", 0.6)], now_h, "tensile",
                               tag=dict(design=D["design"], node="tensile", sample=f"D{a['deposit']}"))
        self.charge(now_h, usd + 120.0, "tensile (3 specimens machined)")
        st = self._route_of("tensile")
        m = self._meas_offset(st, self._m("tensile", self._psample(part, D["design"])), now_h)
        meas = dict(ys_MPa=m["ys_MPa"], el_pct=m["el_pct"], uts_MPa=m["uts_MPa"], n_bars=m.get("n_bars", 3))
        self._part_truth[a["deposit"]]["route_test"] = st
        self._emit(t_r, dict(type="cu_test", what="tensile", deposit=a["deposit"], design=D["design"],
                             measured=meas))
        return True

    def _cu_check(self, dep_id):
        sc = super()._cu_check(dep_id)
        if sc:
            pt = self._part_truth.get(dep_id, {})
            sc[1].update(route_fab=pt.get("route"), route_test=pt.get("route_test"))
        return sc

    def view(self, now_h):
        v = super().view(now_h)
        v["large_g"] = 1000.0 if self.vertical else 2000.0
        return v


_T = {}


def _targets():
    if not _T:
        from twin import bench2 as B2
        _T.update(B2.targets())
    return _T


class Twin4(C.Twin):
    """Both campaigns on round 4's facility, from the day the funding arrives."""

    def __init__(self, specs: dict, policies: dict, plan="parallel", seed=0, horizon_days=730,
                 scenario="historical", opts=None):
        self.h = horizon_days * H
        self.horizon_days = horizon_days
        supply.load_private()
        self.market = supply.Market(scenario, seed, int(horizon_days) + 400)
        self.mode = "async"
        self.plan = plan
        self.fac4 = Facility4(plan, seed, self.h + 2000 * H, opts)
        self.campaigns = {}
        for k, sp in specs.items():
            c = Campaign4(sp, policies[k], self.market, self.fac4, self.h)
            c.async_ = True
            c.start_h = self.fac4.start_h
            self.campaigns[k] = c
        self.facilities = {k: c.fac for k, c in self.campaigns.items()}
        self.seq = itertools.count()
        self.trace = None
        self._iters = {k: 0 for k in self.campaigns}
        self.stages = bool((opts or {}).get("stages", True))

    def run_async(self, verbose=False):
        """Round 3's event loop; a campaign is not asked before the plan's start (the cell's completion for
        ``wait``)."""
        q, ends = [], []
        F = self.fac4
        for r in F.res.values():
            r.on_commit = lambda e, _ends=ends: heapq.heappush(_ends, e)
        dirty = {k: True for k in self.campaigns}
        last = {k: -1e9 for k in self.campaigns}
        tot_b = sum(c.spec.budget_usd for c in self.campaigns.values())
        self._money_share = {k: c.spec.budget_usd / tot_b for k, c in self.campaigns.items()}
        keys = list(self.campaigns)
        g, step = 0.0, 0
        start = F.start_h
        import os as _os
        import time as _time
        _verb = bool(_os.environ.get("TWIN4_VERBOSE"))
        _t0 = _time.time()
        while g <= self.h + 1e-9:
            F.now = g
            if _verb and step % (24 * 15) == 0:
                print(f"  day {g / 24:.0f}: {_time.time() - _t0:.1f} s", flush=True)
            while q and q[0][0] <= g + 1e-9:
                tr, _, k, p = heapq.heappop(q)
                c = self.campaigns[k]
                if c.release3(tr, p):
                    dirty[k] = True
                for tr2, pay in c.events_out:
                    heapq.heappush(q, (tr2, next(self.seq), k, pay))
                c.events_out = []
            freed = False
            while ends and ends[0] <= g + 1e-9:
                heapq.heappop(ends)
                freed = True
            if g + 1e-9 < start:
                g += self.DT_H
                step += 1
                continue
            if step % 24 == 0 and self.stages:
                self._stage_tick(g)
            order = keys if step % 2 == 0 else keys[::-1]
            if len(keys) == 2:
                order = sorted(order, key=lambda k: self._atom_share(k, g) - self._money_share[k])
            for k in order:
                c = self.campaigns[k]
                if not (dirty[k] or freed or g - last[k] >= 24.0) or c.budget_left <= 0:
                    continue
                dirty[k], last[k] = False, g
                v = c.view(g)
                acts = c.policy.propose(v, self.N_ASK) or []
                blocked = False
                for a in acts:
                    if blocked and a.get("kind") != "stop" and c.estimate(a) > 50.0:
                        st = "plan"
                        c.status_log["plan_wait"] = c.status_log.get("plan_wait", 0) + 1
                    else:
                        st = c.submit3(a, g)
                        blocked = blocked or st == "plan"
                    ok = st == "ok"
                    cb = getattr(c.policy, "admitted" if ok else "rejected", None)
                    if cb is not None:
                        cb(a) if ok else cb(a, st)
                for tr2, pay in c.events_out:
                    heapq.heappush(q, (tr2, next(self.seq), k, pay))
                c.events_out = []
            g += self.DT_H
            step += 1
        return self.summary()

    # ------------------------------------------------------------------------------------------ stages
    def _stage_tick(self, g):
        """Once a day: start, advance or finish each campaign's alloy in the stages (``STAGES``)."""
        from twin.opt.policies2 import Base2
        T = _targets()
        for k, c in self.campaigns.items():
            if not hasattr(c, "stage"):
                c.stage, c.stage_done, c.stage_tried, c.scale_usd = None, [], set(), 0.0
            stg = c.stage
            if stg is None:
                try:
                    rows = Base2.observed(c.policy, c.view(g))
                except Exception:
                    rows = []
                cand = [(u, d) for d, u in rows if u >= T["T2"][k] and d not in c.stage_tried]
                if not cand:
                    continue
                u, did = max(cand)
                c.stage_tried.add(did)
                gst, kg = STAGES["gas"][k]
                t_r, usd = c._route([(gst, 8.0)], g, "stage gas", tag=dict(design=did, node="stage_gas"))
                feed = c._gas_feed(dict(design=c.designs[did]["design"]))
                c.scale_usd += usd + feed
                c.stage = dict(design=did, u_meas=u, t0=g, step="gas", t_next=t_r, t_gas=None, sites={})
                continue
            if g < stg["t_next"]:
                continue
            if stg["step"] == "gas":
                stg["t_gas"] = g
                ends, us = [], []
                lot = self._gas_lot(c, stg["design"])
                for site in STAGES["sites"][k]:
                    if site not in c.fac.res or site not in c.fac.cands(site.split("@")[0]) or \
                            c.fac.res[site].online_h > g + 30 * H:
                        continue
                    t_s, u_s, usd = self._stage_site(c, site, stg["design"], lot, g)
                    c.scale_usd += usd
                    ends.append(t_s)
                    us.append(u_s)
                    stg["sites"][site] = dict(t=round(t_s / H, 2), u=round(u_s, 4))
                # the network moves on when the first two sites have reported (one, if the plan has only one): the
                # slowest partner's next session does not hold the alloy up; its result still comes in
                order = sorted(range(len(ends)), key=lambda i: ends[i])[:min(2, len(ends))]
                stg["u_network"] = float(np.mean([us[i] for i in order])) if order else 0.0
                stg["u_network_all"] = float(np.mean(us)) if us else 0.0
                stg["step"], stg["t_next"] = "network", (max(ends[i] for i in order) if order else g)
                continue
            if stg["step"] == "network":
                if stg["u_network"] < T["T1"][k]:
                    c.stage_done.append(dict(stg, result="failed network", t_end=g))
                    c.stage = None
                    continue
                dd, fee, what = STAGES["app"][k]
                role = "utah_midi" if k == "flaime_al" else "utah_mxlab"
                t_f, usd = c._route([(role, 8.0)], g, "stage full part", tag=dict(design=stg["design"],
                                                                                   node="stage_part"))
                c.scale_usd += usd + fee
                stg["t_part"] = t_f
                stg["step"], stg["t_next"] = "app", t_f + dd * H * math.exp(self.fac4.rng.normal(0, 0.2))
                continue
            if stg["step"] == "app":
                u_true = max((d["u"] for d in c.demonstrated if d["design"] == stg["design"]), default=0.0)
                c.stage_done.append(dict(stg, result="validated", t_end=g, u_true=u_true))
                c.stage = None

    def _gas_lot(self, c, did):
        """A gas-atomized lot's truth (as Campaign._do_gas_atomize): volatile losses, finer and rounder powder."""
        comp = dict(c.designs[did]["composition"])
        al = c.key == "flaime_al"
        for el, f in (("Mg", 0.03), ("Zn", 0.05), ("Li", 0.08), ("Mn", 0.02)):
            if comp.get(el, 0) > 0:
                comp[el] *= 1 - f
        bal = c.space.balance
        comp[bal] = 100.0 - sum(v for kk, v in comp.items() if kk != bal)
        return dict(composition=comp, oxygen_ppm=900.0 if al else 300.0, satellite_frac=0.03, carbon_ppm=20.0,
                    runs=[], reuse=0.0)

    def _stage_site(self, c, site, did, lot, g):
        """One site of the validation network: the gas lot made into a part at the site's settings (the alloy's best
        so far) with the site's process offset, then tested on the plan's routes. Returns (result time, true
        utility, money)."""
        al = c.key == "flaime_al"
        F = c.fac
        if al:
            prm = None
            for t in sorted(c.tests, key=lambda t: t["t"]):
                if t["design"] == did and t.get("params"):
                    prm = t["params"]
            prm = dict(prm or {"P_W": 250.0, "v_mm_s": 900.0, "h_um": 100.0, "t_um": 30.0, "T0_C": 100.0})
            steps = [("=" + site, STAGES["site_h"][site]), ("edm", 1.0), ("furnace", 3.0), ("shop", 1.5),
                     ("tensile", 0.6)]
        else:
            prm = None
            for D in c.deposits.values():
                if D["design"] == did and D["mode"] == "blown_large":
                    prm = D["measured"][0].get("params")
            prm = dict(prm or {"P_W": 600.0, "v_mm_min": 600.0, "feed_g_min": 6.0})
            steps = [("=" + site, STAGES["site_h"][site]), ("byu_sem", 1.0), ("shop", 1.0), ("tensile", 0.6),
                     ("immersion", 720.0)]
        t_r, usd = c._route(steps, g, "stage network", tag=dict(design=did, node="stage_network", site=site))
        off = F.offset.get(site, 0.0)
        p_eff = dict(prm, P_W=prm["P_W"] * (1 + off))
        if al:
            part = c.truth.build(lot, p_eff, c.rng)
            u, _ = c._al_score(part, c.truth.strength(part))
        else:
            part = c.truth.deposit(lot, p_eff, "blown_large", c.rng,
                                   substrate={"Al": 9.2, "Ni": 4.5, "Fe": 4.0, "Mn": 1.2})
            u = self._cu_u_true(c, part)
        return t_r, float(u), usd

    @staticmethod
    def _cu_u_true(c, part):
        s, cr = c.truth.strength(part), c.truth.corrosion(part)
        ref = c._cu_ref_rate()
        ni = part["composition"].get("Ni", 0.0)
        feas = part["rel_density"] >= 0.99 and part["crack_free"]
        d = [C._desir(s["ys_MPa"], 100, 400), C._desir(s["el_pct"], 5, 35),
             C._desir(3.0 * ref - cr["rate_um_yr"], 0, 2.5 * ref), C._desir(30 - ni, 0, 30)]
        return float(np.prod(d) ** 0.25) * (1.0 if feas else 0.0)

    def report(self) -> dict:
        """What round 4 adds to a run's record: the build-out, capital payments, monthly use of every station,
        route choices and provenance visits."""
        F = self.fac4
        sch = F.sched
        routes = {}
        for t, camp, role, st, what in F.route_log:
            d = routes.setdefault(camp, {}).setdefault(role, {})
            d[st] = d.get(st, 0) + 1
        return dict(plan=self.plan, start_h=F.start_h, cell_h=F.cell_h, full_h=sch.get("full_h"),
                    build={k: {kk: (round(vv, 1) if isinstance(vv, float) else vv) for kk, vv in v.items()
                               if kk != "name"} for k, v in sch["items"].items()},
                    station_online={k: round(v, 1) for k, v in sch["stations"].items()},
                    payments=[(round(t, 1), round(u, 2), k) for t, u, k in sch["payments"]],
                    monthly=F.monthly(self.h), routes=routes,
                    offsets={k: round(v, 4) for k, v in F.offset.items()},
                    offset_est={k: round(v, 4) for k, v in F.offset_est.items()},
                    provenance=F.prov_log, helper_misses=F.helper_misses,
                    stages={k: dict(done=[{kk: (round(vv / H, 2) if kk in ("t0", "t_next", "t_gas", "t_part", "t_end")
                                                and isinstance(vv, float) else vv) for kk, vv in d.items()}
                                          for d in getattr(c, "stage_done", [])],
                                    open=(None if getattr(c, "stage", None) is None else
                                          {kk: (round(vv / H, 2) if isinstance(vv, float) and kk.startswith("t")
                                                else vv) for kk, vv in c.stage.items()}),
                                    usd=round(getattr(c, "scale_usd", 0.0), 2))
                            for k, c in self.campaigns.items()})
