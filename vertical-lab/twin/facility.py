"""The shared facility: stations in the lab, outside services, their calendars, rates, turnaround and breakdowns.

Two facility scenarios, both shared by the two campaigns:

* ``proposed``: what the two proposals say they will use. BYU: the AMAZEMET rePOWDER (3 starts a weekday and 1 on
  Saturday, FLAIME's "up to 3 compositions/day M-F and 1 on Saturday"), the powder doser and press, a sieve shaker,
  the CubXL corrosion screen and its immersion vials, a furnace and Instron frames; the BYU Microscopy Center
  ($45/h) and ICP-MS facility ($35/sample) (ONR budget); the machine shop ($40 a tensile specimen) and a Provo wire
  EDM service ("turnaround times are not guaranteed", FLAIME Appendix 2). Outside: the University of Utah's Aconity
  MIDI core facility ($800 a build, ONR budget; $120/h, FLAIME), its InssTek MX-Lab (Fang group; about twelve
  half-day sessions a year), the Colorado School of Mines' FormAlloy X2 (2 kg hoppers, 3 machine h + 2 labour h a
  session; 3-7 sessions a year), NSL Analytical (O, C and composition of every lot sent to Mines), Valimet's gas
  atomization (FLAIME: about $8k a run of >= 50 kg) and Ames (ONR: one run a year). BYU's HPC runs the CALPHAD,
  AM-module and heat-flow nodes.
* ``vertical_lab``: PR 318's lab. The same atomizer (its crucible still needs a person on the day shift), and in
  house, round the clock, with the two MiR250 + UR12e units: the Aconity MIDI, an MX-Lab, the wire EDM, the furnaces,
  the Instron 68FM-100 and the zwickiLine, the SEM, the ICP-MS station, the CubXL. Step times are the finale's
  (``timelapse.STEPS``, notes/timelapse.md). The Mines X2 stays outside (2 kg builds and repair coupons on thick
  plate need more laser than an MX-Lab).

Bookings are made when an action is bought, so a later booking may fill an earlier gap; the atomizer's changeover is
charged when a booking switches campaign from the previous booking made, an approximation of the previous run in time.

Rates for outside services that the proposals keep private (Mines) or don't give (Utah MX-Lab, Valimet, Ames) are
assumed and marked so; breakdown rates are assumed (upkeep.py's own are for the vertical lab and are mostly assumed
too).
"""
from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, field

import numpy as np

H_DAY, H_WEEK = 24.0, 168.0


@dataclass
class Station:
    key: str
    name: str
    units: int = 1
    hours: str = "24/7"              # '24/7', 'day' (Mon-Fri 08-17), 'day6' (Mon-Sat 08-17)
    attended_h: float | None = None  # hours at the start of a job that must fall in the calendar (None: all of it)
    starts: tuple | None = None      # allowed start hours of day (slot-based machines)
    sat_starts: tuple | None = None
    mtbf_h: float | None = None
    mttr_h: float = 24.0
    rate_usd_h: float = 0.0
    fee_usd: float = 0.0             # per job
    external: bool = False
    booking_days: float = 0.0        # median lead before an outside session can start
    turnaround_days: float = 0.0     # median lag from the end of the work to the result
    per_period: tuple | None = None  # (jobs, days): an outside facility's cap
    source: str = ""
    weekdays: tuple | None = None    # weekdays a job may start (0 = Monday); None: any the calendar allows
    campaign_weekdays: dict | None = None   # per-campaign weekdays (DAL #256: copper runs on Fridays)
    adjust: dict | None = None       # {what or what@campaign: (scale, add_h)} on a booking's hours (DAL #256's times)


def _st(*a, **k):
    return Station(*a, **k)


PROPOSED = [
    _st("hpc", "BYU HPC (CALPHAD, AM Module, heat flow)", 50, source="FLAIME App. 2: ~28,000 cores"),
    _st("atomizer", "AMAZEMET rePOWDER ultrasonic atomizer", 1, "day6", attended_h=1.0, starts=(8.0, 10.5, 13.0),
        sat_starts=(9.0,), mtbf_h=400, mttr_h=36, fee_usd=0.0,
        source="FLAIME App. 2: <= 3 compositions/day M-F and 1 on Saturday; timelapse.py: 2.5 h a run"),
    _st("shop", "BYU Prototyping Lab (cups and plugs; tensile specimens)", 2, "day", fee_usd=0.0,
        source="FLAIME App. 2; ONR budget: $40 per tensile specimen"),
    _st("doser", "Powder doser + vacuum press (charge cups)", 1, "day",
        source="DAL PR 117: the doser weighs to 0.1 mg; chapter 1 of PR 318"),
    _st("sieve", "Sieve shaker (Retsch AS 200)", 1, "day"),
    _st("psd", "Powder size and flow (sieve analysis, Hall funnel)", 1, "day"),
    _st("byu_sem", "BYU Microscopy Center (SEM, EDS, EBSD)", 2, "day", rate_usd_h=45.0, turnaround_days=1.0,
        source="ONR budget: 100 h x $45/h"),
    _st("byu_icpms", "BYU ICP-MS (Agilent 8900)", 5, "day", fee_usd=35.0, turnaround_days=10.0,
        source="ONR budget: 40 samples x $35; FLAIME: ICP-MS every 10th composition"),
    _st("density", "Density (Archimedes) and optical crack check", 1, "day"),
    _st("edm", "Wire EDM, Provo service", 1, "day", fee_usd=150.0, external=True, turnaround_days=7.0,
        source="FLAIME App. 2 ('turnaround times are not guaranteed'); fee assumed"),
    _st("furnace", "Heat-treatment furnace", 2, "24/7", attended_h=0.25),
    _st("tensile", "Instron frames (BYU)", 1, "day", source="FLAIME App. 3: 1 kip and 110 kip frames"),
    _st("tensile_hot", "Instron with furnace (elevated temperature)", 1, "day"),
    _st("utah_midi", "Univ. of Utah Aconity MIDI core facility", 1, "day", fee_usd=800.0, external=True,
        booking_days=7.0, turnaround_days=2.0, per_period=(3, 7), mtbf_h=600, mttr_h=72,
        source="ONR budget: $800 a build (purchase order); FLAIME: $120/h"),
    _st("utah_mxlab", "Univ. of Utah InssTek MX-Lab (half-day sessions)", 1, "day", fee_usd=300.0, external=True,
        booking_days=10.0, turnaround_days=1.0, per_period=(1, 21),
        source="DAL PR 117 README: about twelve half-day sessions a year; fee assumed"),
    _st("mines_x2", "Colorado School of Mines FormAlloy X2", 1, "day", fee_usd=600.0, external=True,
        booking_days=21.0, turnaround_days=10.0, per_period=(1, 35),
        source="DAL PR 117: 3 machine h + 2 labour h a session, 3-7 sessions a year; rates private, fee assumed"),
    _st("nsl", "NSL Analytical (O, C, composition)", 10, "day", fee_usd=150.0, external=True, turnaround_days=10.0,
        source="DAL PR 117: every lot sent to Mines; ONR README guesses $2,000 for about 20 lots"),
    _st("cubxl", "CubXL corrosion screen (OCP, LPR, EIS, CP)", 1, "24/7", attended_h=0.25,
        source="DAL PR 117 Task 2; 67 min a spot with EIS (timelapse.py)"),
    _st("immersion", "30-day immersion vials on the gantry deck", 24, "24/7"),
    # round 2: the characterization a conventional lab books at core facilities (BYU) or sends out
    _st("xrd", "BYU XRD lab (powder diffractometer, core facility)", 1, "day", rate_usd_h=30.0, turnaround_days=1.0,
        source="assumed core-facility rate; XRD prep and scan about 0.75 h"),
    _st("xrf", "XRF (core facility)", 1, "day", rate_usd_h=30.0, turnaround_days=1.0, source="assumed"),
    _st("prep", "Metallography (section, mount, polish; by hand)", 2, "day", source="DAL SOPs (PR 258); manual"),
    _st("hardness", "Micro-Vickers (by hand)", 1, "day"),
    _st("nanoindent", "Nanoindenter (core facility)", 1, "day", rate_usd_h=50.0, turnaround_days=2.0,
        source="assumed core-facility rate"),
    _st("pip", "Plastometrex PIP testing service (outside)", 1, "day", fee_usd=250.0, external=True,
        booking_days=5.0, turnaround_days=7.0, source="Plastometrex offers PIP testing as a service; fee assumed"),
    _st("valimet", "Valimet gas atomization (>= 50 kg)", 1, "day", fee_usd=8000.0, external=True,
        booking_days=30.0, turnaround_days=21.0, per_period=(1, 30),
        source="FLAIME DAG: ~$8k a run; 6 scale-up runs"),
    _st("ames", "Ames National Laboratory gas atomization", 1, "day", fee_usd=5000.0, external=True,
        booking_days=45.0, turnaround_days=30.0, per_period=(1, 300),
        source="DAL PR 117: one run a year as a purchased service; fee assumed"),
]

# PR 318's lab: in-house replacements, round the clock (the robots), times from timelapse.STEPS
VERTICAL = [
    _st("utah_midi", "Aconity MIDI (in house, PR 318)", 1, "24/7", fee_usd=150.0, mtbf_h=500, mttr_h=48,
        source="timelapse.STEPS print 5 h; plate, argon and powder change as the fee (assumed)"),
    _st("utah_mxlab", "InssTek MX-Lab (in house, PR 318 floor)", 1, "24/7", fee_usd=120.0, mtbf_h=500, mttr_h=48,
        source="bottleneck.py: an MX-Lab plate of 8 blocks, 8 h"),
    _st("edm", "Wire EDM (in house)", 1, "24/7", fee_usd=25.0, source="timelapse.STEPS edm 0.75 h"),
    _st("byu_sem", "SEM TM4000 + EDS, tray D (in house)", 1, "24/7", source="timelapse.STEPS sem 0.5 h"),
    _st("byu_icpms", "ICP-MS station (in house, PR 318 round 14)", 1, "day", fee_usd=15.0, turnaround_days=1.0,
        source="icpms.py; consumables assumed"),
    _st("density", "Density and crack check (in house)", 1, "24/7"),
    _st("tensile", "zwickiLine Z5.0 TN + Instron 68FM-100 (in house)", 2, "24/7"),
    _st("tensile_hot", "Instron 68FM-100 with 3119-608 chamber", 1, "24/7"),
    _st("sieve", "Sieve cell with wash (in house)", 1, "24/7"),
    _st("psd", "Mastersizer + XRF (in house)", 1, "24/7"),
    _st("doser", "Doser + vacuum press, tray B (in house)", 1, "24/7"),
    _st("shop", "Machining cell (PR 373) and shop", 2, "24/7"),
    # round 2: the trays' characterization, in house and round the clock (PR 318 chapters 4, 6 and 7)
    _st("xrd", "Rigaku MiniFlex with its prep station, tray D (in house)", 1, "24/7", fee_usd=2.0,
        source="chapter 4: back-loaded zero-background holder; 0.75 h prep and scan"),
    _st("xrf", "Bruker S2 PUMA, tray F (in house)", 1, "24/7", fee_usd=2.0, source="chapter 4"),
    _st("prep", "Sectioning, MX400 hot mounting, PX500 polishing (in house)", 1, "24/7", fee_usd=8.0,
        source="chapter 6; pre-loaded discs changed by the arm; consumables assumed"),
    _st("hardness", "Mitutoyo HM-220 micro-Vickers, tray L (in house)", 1, "24/7", source="chapter 7"),
    _st("nanoindent", "KLA iMicro, tray E (in house)", 1, "24/7", source="chapter 7"),
    _st("pip", "Plastometrex PLX-Benchtop, tray E (in house)", 1, "24/7", fee_usd=5.0, source="chapter 7"),
]


# DAL #256's schedule for DAL's own lab (al-campaign-schedule/README.md and tasks.csv at DAL 6ff7717, the plan in
# DAL #256's comment 7123300072): the proposed facility's stations on #256's calendar and step times. Every #256 time
# is an estimate ("Nothing in the chain has been timed end to end"); times #256 does not give keep the twin's own and
# are listed in out/twin2/trace/README.md. The optimizer's Friday batches are not modelled: policies propose whenever
# a slot frees.
DAL256 = {
    # one run a day Mon-Thu at 08:00 (Thursday is #256's flex slot), copper on Fridays ("so the ~1 h clean that follows
    # each one doesn't eat into an Al week"); a run is 2.5-3.5 h (start-up, loading, three washes, melt, pour), then
    # ~1 h to cool to 400 C and vent and 1-2 h to collect, weigh, clean and rebuild: the twin's 2.5 h run + 3.0 h
    # (3.0 + 1 + 1.5), + 4.0 h for copper (the ~1 h full clean). The BN coat (15 min + overnight dry) fits the
    # one-run-a-day cadence and is not booked.
    "atomizer": dict(hours="day", starts=(8.0,), sat_starts=None, attended_h=None, weekdays=(0, 1, 2, 3),
                     campaign_weekdays={"onr_cu": (4,)}, adjust={"atomize": (1.0, 3.0), "atomize@onr_cu": (1.0, 4.0)},
                     source="DAL #256 (al-campaign-schedule/README.md L76-L101 @ 6ff7717): runs Mon-Thu, Cu Fridays; "
                            "2.5-3.5 h run, ~1 h cool, 1-2 h turnaround, ~1 h full clean after Cu"),
    # cups and plugs are machined "ahead, in bulk", off the critical path; dose, pack, press the plug and clean with
    # IPA, 1-1.5 h the day before
    "shop": dict(adjust={"charge": (0.0, 0.0)}, source="DAL #256 README L97: cups and plugs ahead, in bulk"),
    "doser": dict(adjust={"charge": (1.0, 0.25)}, source="DAL #256 README L96: 1-1.5 h the day before"),
    # sieve two splits within 48 h of the run (1-1.5 h); flowability and Hausner ratio within a week (0.5-1 h)
    "sieve": dict(adjust={"powder QC": (1.0, 0.5)}, source="DAL #256 README L103: 1-1.5 h within 48 h"),
    "psd": dict(adjust={"powder QC": (1.0, 0.5)}, source="DAL #256 README L104: flowability, Hausner, 0.5-1 h"),
    # one SEM session a week, Thursday, for all of the week's powders (4-5 h for 3-4 runs; stubs Tuesday): 1.25 h a
    # lot; sections and deposits keep the twin's times but wait for Thursday too
    "byu_sem": dict(weekdays=(3,), adjust={"powder QC": (1.0, 0.75)},
                    source="DAL #256 README L46-L48, L105: one Thursday session, 4-5 h, 2-3 h a run with stubs"),
    # one polishing batch a week (Wednesday, PX500), with hardness and density on everything printed that week
    "prep": dict(weekdays=(2,), source="DAL #256 README L50-L53, L82; tasks.csv L24: one batch a week, Wednesday"),
    "hardness": dict(weekdays=(2,), source="DAL #256 README L52-L53, L82: Wednesday"),
    "density": dict(weekdays=(2,), source="DAL #256 README L52-L53, L82: Wednesday"),
    # tensile or corrosion on Thursdays, daytime only
    "tensile": dict(weekdays=(3,), source="DAL #256 README L83: tensile or corrosion, Thursday daytime"),
    "tensile_hot": dict(weekdays=(3,), source="DAL #256 README L339 excludes hot tests by Feb 28; Thursday if run"),
    "cubxl": dict(hours="day", attended_h=None, weekdays=(3,),
                  source="DAL #256 README L58-L60, L83: corrosion daytime only (EZstat-Pro on the CubXL), Thursday"),
    # Utah: an LPBF session is two days (Tue-Wed) on alternate weeks, each composition its own build; parts come back
    # for removal, heat treatment and prep about a week after each session. DED sessions are one day (Tuesday).
    "utah_midi": dict(weekdays=(1, 2), per_period=(3, 14), turnaround_days=7.0,
                      source="DAL #256 tasks.csv L10-L14, L18-L22; README L81: 2-day sessions on alternate weeks, "
                             "parts back about a week after"),
    "utah_mxlab": dict(weekdays=(1,), source="DAL #256 tasks.csv L15-L17: one-day DED sessions, Tuesday"),
}


def facility(kind: str = "proposed") -> dict:
    st = {s.key: Station(**s.__dict__) for s in PROPOSED}
    if kind == "vertical_lab":
        for s in VERTICAL:
            st[s.key] = Station(**s.__dict__)
    elif kind == "dal256":
        for k, over in DAL256.items():
            for f, x in over.items():
                setattr(st[k], f, x)
    elif kind != "proposed":
        raise ValueError(kind)
    # private rates the lab holds (e.g. a partner's posted external rates kept out of public text), git-ignored:
    # data/private/rates.json = {"mines_x2": {"fee_usd": ...}, ...}
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parent / "data" / "private" / "rates.json"
    if p.exists():
        for k, v in json.loads(p.read_text()).items():
            if k in st:
                for f, x in v.items():
                    setattr(st[k], f, x)
    return st


# ------------------------------------------------------------------------------------------------------- calendars
def in_hours(cal: str, t: float) -> bool:
    if cal == "24/7":
        return True
    day = int(t // H_DAY)
    dow = day % 7                                        # day 0 is a Monday
    hod = t - day * H_DAY
    if dow < 5 or (cal == "day6" and dow == 5):
        return 8.0 <= hod < 17.0
    return False


def next_open(cal: str, t: float) -> float:
    if cal == "24/7":
        return t
    for _ in range(24 * 14 * 4):
        if in_hours(cal, t):
            return t
        t = math.floor(t * 4 + 1) / 4.0
    return t


class Line:
    """One unit's bookings: sorted, non-overlapping intervals (a later booking may use an earlier gap)."""

    def __init__(self):
        self.s, self.e = [], []

    def fits(self, t, d):
        i = bisect.bisect_right(self.e, t)
        return i >= len(self.s) or self.s[i] >= t + d - 1e-9

    def next_try(self, t, d):
        """Where to try next if a booking of d at t does not fit: the end of the interval in the way."""
        i = bisect.bisect_right(self.e, t)
        if i < len(self.s) and self.s[i] < t + d - 1e-9:
            return self.e[i]
        return t

    def add(self, a, b):
        i = bisect.bisect_left(self.s, a)
        self.s.insert(i, a)
        self.e.insert(i, b)


class Resource:
    def __init__(self, st: Station, rng: np.random.Generator, horizon_h: float):
        self.st = st
        self.lines = [Line() for _ in range(st.units)]
        self.jobs: list = []                     # (start, end, campaign, what)
        self.last_campaign = None
        self.busy_h = 0.0
        self.down = []                           # breakdowns: (start, end)
        if st.mtbf_h:
            t = rng.exponential(st.mtbf_h * 2.0)   # calendar hours, at about 50 % utilization
            while t < horizon_h:
                d = st.mttr_h * math.exp(rng.normal(0, 0.5))
                self.down.append((t, t + d))
                t += d + rng.exponential(st.mtbf_h * 2.0)
        self.period_starts: list = []

    def _down_at(self, t, d):
        for a, b in self.down:
            if a < t + d and b > t:
                return b
        return None

    def _day_ok(self, campaign, dow) -> bool:
        st = self.st
        wd = (st.campaign_weekdays or {}).get(campaign, st.weekdays)
        return wd is None or dow in wd

    def _slot(self, t, campaign=None):
        """The next allowed start for slot-based machines (the atomizer), on the station's weekdays."""
        st = self.st
        if not st.starts:
            t2 = next_open(st.hours, t)
            if st.weekdays is None and not st.campaign_weekdays:
                return t2
            for _ in range(60):
                day = int(t2 // H_DAY)
                if self._day_ok(campaign, day % 7):
                    return t2
                t2 = next_open(st.hours, (day + 1) * H_DAY)
            return t2
        day = int(t // H_DAY)
        for k in range(60):
            dd = day + k
            dow = dd % 7
            if not self._day_ok(campaign, dow):
                continue
            starts = st.starts if dow < 5 else (st.sat_starts if (dow == 5 and st.hours == "day6") else ())
            for s in starts or ():
                ts = dd * H_DAY + s
                if ts >= t - 1e-9:
                    return ts
        return t

    def book(self, t, dur, campaign: str, what: str, changeover_h: float = 0.0, tag=None) -> tuple[float, float]:
        """Earliest booking of `dur` hours at or after t. Returns (start, end)."""
        st = self.st
        att = dur if st.attended_h is None else min(st.attended_h, dur)
        if st.external and st.booking_days:
            t = max(t, t + 0.0)
        for _ in range(20000):
            t = self._slot(t, campaign)
            if st.hours != "24/7" and not in_hours(st.hours, t + att - 1e-6):
                t = next_open(st.hours, math.floor(t / H_DAY + 1) * H_DAY)
                continue
            if st.per_period:
                n, days = st.per_period
                win = [s for s in self.period_starts if t - days * H_DAY < s <= t + days * H_DAY]
                if len(win) >= n:
                    t = min(win) + days * H_DAY + 0.01
                    continue
            extra = changeover_h if (self.last_campaign and self.last_campaign != campaign) else 0.0
            d = dur + extra
            b = self._down_at(t, d)
            if b is not None:
                t = b
                continue
            for ln in self.lines:
                if ln.fits(t, d):
                    ln.add(t, t + d)
                    self.jobs.append((t, t + d, campaign, what, tag))
                    self.busy_h += d
                    if st.per_period:
                        self.period_starts.append(t)
                    self.last_campaign = campaign
                    return t, t + d
            t = max(min(ln.next_try(t, d) for ln in self.lines), t + 1e-3)
        raise RuntimeError(f"could not book {st.key}")


class Facility:
    def __init__(self, kind: str, seed: int, horizon_h: float):
        rng = np.random.default_rng(30_000 + seed)
        self.kind = kind
        self.res = {k: Resource(s, rng, horizon_h) for k, s in facility(kind).items()}
        self.rng = np.random.default_rng(40_000 + seed)

    def run_step(self, station: str, ready: float, dur: float, campaign: str, what: str, changeover_h=0.0, tag=None):
        """Book a step; returns (start, end, result_time, cost). ``tag`` (design, node, ...) goes into the job record
        so the event log can say which experiment a booking served."""
        r = self.res[station]
        st = r.st
        t0 = ready
        if st.external and st.booking_days:
            t0 = ready + st.booking_days * H_DAY * math.exp(self.rng.normal(0, 0.35))
        s, e = r.book(t0, dur, campaign, what, changeover_h, tag)
        lag = st.turnaround_days * H_DAY * math.exp(self.rng.normal(0, 0.4)) if st.turnaround_days else 0.0
        cost = st.fee_usd + st.rate_usd_h * dur
        return s, e, e + lag, cost

    def adjust(self, station: str, hours: float, what: str, campaign: str) -> float:
        """A booking's hours on this facility's schedule (DAL #256's step times on ``dal256``; unchanged elsewhere)."""
        a = self.res[station].st.adjust
        if not a:
            return hours
        for key in (f"{what}@{campaign}", what):
            if key in a:
                scale, add = a[key]
                return hours * scale + add if hours * scale > 0 else 0.0
        return hours

    def utilization(self, t_end: float) -> dict:
        return {k: round(r.busy_h / max(t_end, 1.0) / r.st.units, 4) for k, r in self.res.items() if r.busy_h > 0}
