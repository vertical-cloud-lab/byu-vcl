"""The lab's moves for the animated replay, from the event log: which tray each booking brings to its Shuttle's opening,
which MiR250 + UR12e unit drives to which dock, and when, in video time. No VTK here; lab3d.py draws the result.

    from twin.video import data as D, lab3d_sched as LS
    kin = LS.load_kin()                                   # out/twin2/video/lab3d/kin.json (written by lab3d.py export)
    clock = LS.Clock.linear(lab_h0=24 * 119, hours_per_s=2.8, seconds=60)
    plan = LS.plan(D.Replay(), kin, clock)               # every move, simulated in video time
    st = plan.state(12.5)                                 # trays, lifts, shutters, units and arms at 12.5 s

**Two clocks.** The replay's clock runs at 1.5 to 60 lab hours a video second. A Shuttle's tray change takes 8-12 s
with the tower's own timings (setup_lab.TwoLab.fetch/store, below), a unit's drive 5-15 s and its arm's work about
11 s, so at the clock's speed every move would last a few thousandths of a video second and the lab would look still.
So the moves run on a second clock, MOVE_RATE times real time (8 at a day's pace, 16 at a month's), and each starts
when the replay's clock reaches the booking that asks for it. A move keeps its own profile: the lift at 1333 mm/s,
the 2.2 s slides, the 0.7 s shutter, the MiR250 at 1.5 m/s pivoting at 60 deg/s, the arm's pick and place.

**When the moves can't keep up.** At 15-60 lab hours a second Shuttle 1 is asked for 4-14 trays a video second; drawn
at 8-16 times real time it can show one every two or three seconds. Each Shuttle and each unit, when it comes free, takes the latest
request that has reached the clock and drops the older ones still waiting; a request for the tray already at the
opening is served there, as one presentation. Plan.counts says how many were asked for and how many were drawn, and
the video says so on screen. Nothing is drawn that the event log doesn't ask for: an idle tray stays in its slot, and
a unit with nothing to do for IDLE_HOME_S of video goes back to its charger.

What each booking asks for (twin station -> lab, as twin/video/birdseye.STATION_ANCHOR places them): a station on a
tray (TRAY_OF) has its tray brought to the opening and a unit docked there at the booking's start (load) and end
(unload); a floor machine (DOCK_OF) has a unit docked at its front at both. The cloud (HPC) and outside facilities
ask for nothing.
"""
from __future__ import annotations

import bisect
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]
KIN = HERE / "out" / "twin2" / "video" / "lab3d" / "kin.json"

# ---------------------------------------------------------------------------------------- what each booking asks for
TRAY_OF = {"doser": "B", "psd": "E", "byu_sem": "D", "xrd": "D", "xrf": "M", "furnace": "F", "prep": "F",
           "hardness": "L", "nanoindent": "E", "pip": "E", "cubxl": "A", "immersion": "A", "density": "K",
           "shop": "M"}
DOCK_OF = {"atomizer": "repowder", "sieve": "sieve_cell", "utah_midi": "aconity", "edm": "wire_edm",
           "tensile": "instron_small", "tensile_hot": "instron_floor", "utah_mxlab": "ded", "byu_icpms": "fumehood"}
SHUTTLE_DOCK = {1: "vlm", 2: "vlm2"}

# ------------------------------------------------------------------------- the moves' own timings (real seconds)
LIFT_MM_S = 1333.0          # setup_lab.TwoLab.fetch/store: the extractor at |dz| / 1333 s, at least LIFT_MIN_S
LIFT_MIN_S = 0.6
SLIDE_S = 2.2               # a tray pulled onto the extractor, or pushed off it
SHUTTER_S = 0.7             # the safety shutter at the back of the bay, open or shut
DRIVE_MM_S = 1500.0         # warehouse.SPEED: the MiR250 as drawn (it does up to 2.0 m/s)
TURN_DEG_S = 60.0           # warehouse.Amr.route: MiR250s pivot on the spot
ARM_S = dict(unfold=1.0, pick=3.8, carry=1.0, place=3.8, fold=1.0)   # animate.pick/place (1.6 + 0.9 + 0.5 + 0.8 s
#                                                                       each) and warehouse.movie's 1.0 s fold
ENTRY_MM = 1500.0           # where a unit turns onto a dock's line: this far along it, at the end without the post
LANE_OFF_MM = 400.0         # the aisle's two lanes, either side of its middle (warehouse.movie's routes)

# ----------------------------------------------------------------------------------------------- the display
MOVE_RATE = 8.0             # the moves' clock: this many times real time at a day's pace (move_rate)
IDLE_HOME_S = 2.5           # video seconds a unit waits at a dock with nothing to do before it goes to charge
FLOOR_LAG_S = 2.0           # a floor job not started within this much video time of its request is dropped
ARM_X = 1.5                 # the arm's work at a dock runs this much faster than the other moves (about 1 s of video)
UNIT_WAIT_S = 2.5           # a tray at the opening waits this long for a unit, then goes back unserved


def move_rate(hours_per_s: float) -> float:
    """Real seconds of move per video second: MOVE_RATE at a day's pace (<= 2.5 lab h/s), rising to twice that at
    40 lab h/s. At 8 a tray change (8-12 s) takes 1.0-1.5 s of video, its six steps readable one by one."""
    return float(MOVE_RATE * np.clip((max(hours_per_s, 1e-6) / 2.5) ** 0.25, 1.0, 2.0))


def load_kin(path: Path = KIN) -> dict:
    return json.loads(Path(path).read_text())


def ease(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


# ================================================================================================== the clock
class Clock:
    """Video seconds <-> lab hours for one stretch of the replay, monotonic: (v, lab_h) samples."""

    def __init__(self, v: np.ndarray, lab_h: np.ndarray):
        self.v = np.asarray(v, float)
        self.h = np.asarray(lab_h, float)
        dv = np.diff(self.v)
        self.sp = np.concatenate([np.diff(self.h) / np.where(dv > 0, dv, 1e-9), [0.0]])
        self.sp[-1] = self.sp[-2] if len(self.sp) > 1 else 1.0

    @classmethod
    def linear(cls, lab_h0: float, hours_per_s: float, seconds: float):
        return cls(np.array([0.0, seconds]), np.array([lab_h0, lab_h0 + hours_per_s * seconds]))

    @classmethod
    def from_timeline(cls, tl, v0: float, v1: float, n: int = 6000):
        vs = np.linspace(v0, v1, n)
        hs = np.array([tl.lab(x)[0] for x in vs])
        hs = np.maximum.accumulate(hs)
        return cls(vs, hs)

    def lab(self, v: float) -> float:
        return float(np.interp(v, self.v, self.h))

    def video(self, lab_h: float) -> float:
        return float(np.interp(lab_h, self.h, self.v))

    def speed(self, v: float) -> float:
        i = min(max(bisect.bisect_right(self.v, v) - 1, 0), len(self.sp) - 1)
        return float(self.sp[i])

    @property
    def span(self) -> tuple:
        return float(self.v[0]), float(self.v[-1])


# =========================================================================================== requests from the log
@dataclass
class Req:
    v: float                 # video time the clock reaches it
    lab_h: float
    kind: str                # "tray" or "floor"
    where: str               # tray letter or dock key
    shuttle: int             # 0 for a floor job
    event: int               # index into the event log
    edge: str                # "load" (the booking's start) or "unload" (its end)
    campaign: str
    station: str


def requests(R, kin: dict, clock: Clock, pad_h: float = 0.0) -> list:
    """Every tray presentation and floor job the event log asks for inside the clock's span (lab time)."""
    h0, h1 = clock.h[0] - pad_h, clock.h[-1]
    trays = kin["trays"]
    out = []
    for i in range(len(R.t0)):
        st = str(R.station[i])
        if st in TRAY_OF and TRAY_OF[st] in trays:
            k = TRAY_OF[st]
            kind, where, sh = "tray", k, int(trays[k]["shuttle"])
        elif st in DOCK_OF and DOCK_OF[st] in kin["docks"]:
            kind, where, sh = "floor", DOCK_OF[st], 0
        else:
            continue
        for edge, t in (("load", float(R.t0[i])), ("unload", float(R.t1[i]))):
            if h0 <= t <= h1:
                out.append(Req(clock.video(t), t, kind, where, sh, i, edge, str(R.camp[i]), st))
    out.sort(key=lambda r: (r.v, r.lab_h))
    return out


# ================================================================================================ the tower
def fetch_profile(kin: dict, k: str, lift_z: float) -> list:
    """The tower's fetch of tray k to the opening from a lift standing at lift_z: [(real s, kind, a, b)], kinds
    'lift' (the extractor alone), 'slide' (the tray's y), 'carry' (extractor and tray), 'shutter' (0 shut, 1 open)."""
    t = kin["trays"][k]
    ys, zs = t["y"], t["z"]
    yo, zo = kin["open"]
    prof = []
    if abs(lift_z - zs) > 1.0:
        prof.append((max(LIFT_MIN_S, abs(lift_z - zs) / LIFT_MM_S), "lift", lift_z, zs))
    prof += [(SLIDE_S, "slide", ys, 0.0), (max(LIFT_MIN_S, abs(zs - zo) / LIFT_MM_S), "carry", zs, zo),
             (SHUTTER_S, "shutter", 0.0, 1.0), (SLIDE_S, "slide", 0.0, yo), (SHUTTER_S, "shutter", 1.0, 0.0)]
    return prof


def store_profile(kin: dict, k: str) -> list:
    t = kin["trays"][k]
    ys, zs = t["y"], t["z"]
    yo, zo = kin["open"]
    return [(SHUTTER_S, "shutter", 0.0, 1.0), (SLIDE_S, "slide", yo, 0.0), (SHUTTER_S, "shutter", 1.0, 0.0),
            (max(LIFT_MIN_S, abs(zs - zo) / LIFT_MM_S), "carry", zo, zs), (SLIDE_S, "slide", 0.0, ys)]


def profile_seconds(prof: list) -> float:
    return float(sum(p[0] for p in prof))


@dataclass
class TowerMove:
    v0: float
    v1: float
    tray: str
    kind: str                 # "fetch" or "store"
    prof: list
    lift0: float              # the extractor's height at the start


# ================================================================================================ the units
def _wrap(a: float) -> float:
    return (a + 180.0) % 360.0 - 180.0


def path_segments(pose0, legs, end_hd=None) -> list:
    """warehouse.Amr.route's drive: pivot to face each leg, drive it straight (backwards where the leg says so), then
    pivot to end_hd. legs: [(x, y, reverse)]. -> [(real s, (x, y, hd) from, (x, y, hd) to)]."""
    segs, (x, y, hd) = [], (float(pose0[0]), float(pose0[1]), float(pose0[2]))
    for px_, py_, rev in legs:
        dx, dy = px_ - x, py_ - y
        dist = math.hypot(dx, dy)
        if dist < 1.0:
            continue
        want = math.degrees(math.atan2(dy, dx)) + (180.0 if rev else 0.0)
        turn = _wrap(want - hd)
        if abs(turn) > 0.5:
            segs.append((abs(turn) / TURN_DEG_S, (x, y, hd), (x, y, hd + turn)))
            hd += turn
        segs.append((dist / DRIVE_MM_S, (x, y, hd), (px_, py_, hd)))
        x, y = px_, py_
    if end_hd is not None:
        turn = _wrap(end_hd - hd)
        if abs(turn) > 0.5:
            segs.append((abs(turn) / TURN_DEG_S, (x, y, hd), (x, y, hd + turn)))
    return segs


class Floor:
    """Docks, chargers and the aisle from kin.json; routes between them as warehouse.movie drives them: along the dock's
    line to its open end, out to a lane of the aisle (eastbound on the south lane, westbound on the north), along it,
    and in along the other dock's line, backing in where the floor plan says so (BACK_IN). Off a charger backwards,
    onto it forwards."""

    def __init__(self, kin: dict):
        self.docks = {k: tuple(v) for k, v in kin["docks"].items()}
        self.back_in = set(kin["back_in"])
        self.chargers = [tuple(c) for c in kin["chargers"]]
        a0, a1 = kin["aisle"]
        self.mid = (a0 + a1) / 2.0
        self._routes: dict = {}

    def entry(self, key: str) -> tuple:
        """(x, y) on the dock's line, ENTRY_MM out at its open end."""
        x, y, hd = self.docks[key]
        f = math.cos(math.radians(hd))
        s = 1.0 if key in self.back_in else -1.0           # backed into from beyond the MiR's back, else from behind
        return x + s * f * ENTRY_MM, y

    def place(self, where) -> tuple:
        """(pose, kind): kind "dock" or "charger"."""
        if isinstance(where, str):
            return self.docks[where], "dock"
        return self.chargers[int(where)], "charger"

    def route(self, frm, to) -> list:
        """Segments from place frm to place to (dock keys, or charger indices); cached."""
        key = (frm, to)
        if key in self._routes:
            return self._routes[key]
        p0, k0 = self.place(frm)
        p1, k1 = self.place(to)
        legs = []
        if frm == to:
            self._routes[key] = []
            return []
        if k0 == "dock":
            ex, ey = self.entry(frm)
            ahead = (ex - p0[0]) * math.cos(math.radians(p0[2])) > 0
            legs.append((ex, ey, not ahead))
            x_out = ex
        else:
            x_out = p0[0]
        x_in = self.entry(to)[0] if k1 == "dock" else p1[0]
        lane = self.mid - LANE_OFF_MM if x_in >= x_out else self.mid + LANE_OFF_MM
        legs.append((x_out, lane, k0 == "charger"))
        legs.append((x_in, lane, False))
        if k1 == "dock":
            legs.append((x_in, p1[1], False))
            legs.append((p1[0], p1[1], to in self.back_in))
        else:
            legs.append((p1[0], p1[1], False))
        segs = path_segments(p0, legs, end_hd=p1[2])
        self._routes[key] = segs
        return segs

    def seconds(self, frm, to) -> float:
        return 0.0 if frm == to else segs_seconds(self.route(frm, to))


def segs_end(segs: list, pose0) -> tuple:
    return tuple(segs[-1][2]) if segs else tuple(pose0)


def segs_seconds(segs: list) -> float:
    return float(sum(s[0] for s in segs))


def pose_along(segs: list, u_s: float) -> tuple:
    """The pose u_s real seconds into a route, each segment eased (the MiR stops at each pivot)."""
    t = 0.0
    for dur, a, b in segs:
        if u_s <= t + dur or (dur, a, b) == segs[-1]:
            f = ease((u_s - t) / dur) if dur > 0 else 1.0
            return tuple(a[i] + (b[i] - a[i]) * f for i in range(3))
        t += dur
    return tuple(segs[-1][2]) if segs else None


@dataclass
class UnitAct:
    v0: float
    v1: float
    kind: str                 # "drive", "work", "wait"
    where: object             # dock key or charger index at the end
    segs: list = field(default_factory=list)
    rate: float = 20.0
    job: object = None


@dataclass
class Job:
    v_post: float
    dock: str
    kind: str                 # "shuttle" or "floor"
    ready: float              # a shuttle job's tray is at the opening from here
    shuttle: int = 0
    req: object = None
    unit: int = -1
    v_start: float = -1.0
    v_done: float = -1.0
    dropped: bool = False


# ================================================================================================= the plan
# the arm's work at a dock, as fractions of it: unfold from the parked pose, three poses over the tray's front or in
# front of the machine (timelapse.Movie.work's targets), fold again
WORK_KEYS = [(0.0, "park"), (0.10, "ready"), (0.30, 0), (0.50, 1), (0.70, 2), (0.90, "ready"), (1.0, "park")]


class Plan:
    """The simulated moves of one stretch of video: tower moves per Shuttle, activities per unit, and counts."""

    def __init__(self, kin, clock, towers, units, counts, reqs):
        self.kin, self.clock, self.towers, self.units, self.counts, self.reqs = kin, clock, towers, units, counts, reqs
        self.floor = Floor(kin)
        self._tv = {s: [m.v0 for m in ms] for s, ms in towers.items()}
        self._uv = [[a.v0 for a in acts] for acts in units]

    # ------------------------------------------------------------------------------------------------ the state
    def tower_state(self, s: int, v: float) -> dict:
        """{'lift': z, 'shutter': 0..1, 'trays': {k: (y, z)} for the tray out of its slot, 'out': the tray standing in
        the opening or None, 'moving': the tray in transit or None, 'move': the TowerMove or None}."""
        kin = self.kin
        ms = self.towers.get(s, [])
        i = bisect.bisect_right(self._tv.get(s, []), v) - 1
        if i < 0:
            return dict(lift=kin["lift_home"], shutter=0.0, trays={}, out=None, moving=None, move=None)
        m = ms[i]
        yo, zo = kin["open"]
        t = kin["trays"][m.tray]
        if v >= m.v1:                                       # after the move
            if m.kind == "fetch":
                return dict(lift=zo, shutter=0.0, trays={m.tray: (yo, zo)}, out=m.tray, moving=None, move=m)
            return dict(lift=t["z"], shutter=0.0, trays={}, out=None, moving=None, move=m)
        tot = profile_seconds(m.prof)                        # within it: its profile, scaled to [v0, v1]
        u_s = (v - m.v0) / max(m.v1 - m.v0, 1e-9) * tot
        lift, shutter = m.lift0, 0.0
        ty, tz = (t["y"], t["z"]) if m.kind == "fetch" else (yo, zo)
        acc = 0.0
        for dur, kind, a, b in m.prof:
            if u_s <= acc:
                break
            val = a + (b - a) * (ease((u_s - acc) / dur) if u_s < acc + dur else 1.0)
            if kind == "lift":
                lift = val
            elif kind == "carry":
                lift = tz = val
            elif kind == "slide":
                ty = val
            elif kind == "shutter":
                shutter = val
            acc += dur
        return dict(lift=lift, shutter=shutter, trays={m.tray: (ty, tz)}, out=None, moving=m.tray, move=m)

    def unit_state(self, u: int, v: float) -> dict:
        """{'pose': (x, y, hd), 'arm': ('park',) or ('work', dock, u 0..1), 'at': where it stands or None, 'act'}."""
        acts = self.units[u]
        i = bisect.bisect_right(self._uv[u], v) - 1
        if i < 0:
            return dict(pose=tuple(self.kin["chargers"][u]), arm=("park",), at=u, moving=False, act=None)
        a = acts[i]
        if a.kind == "drive" and v < a.v1:
            return dict(pose=pose_along(a.segs, (v - a.v0) * a.rate), arm=("park",), at=None, moving=True, act=a)
        pose, _ = self.floor.place(a.where)
        if a.kind == "work" and v < a.v1:
            return dict(pose=tuple(pose), arm=("work", a.where, (v - a.v0) / max(a.v1 - a.v0, 1e-9)), at=a.where,
                        moving=False, act=a)
        return dict(pose=tuple(pose), arm=("park",), at=a.where, moving=False, act=a)

    def state(self, v: float) -> dict:
        return dict(towers={s: self.tower_state(s, v) for s in self.towers},
                    units=[self.unit_state(u, v) for u in range(len(self.units))])

    def key(self, v: float, q: float = 2.0) -> tuple:
        """A hashable summary of the drawn state, rounded to q mm (q/10 deg), so frames where nothing moves share one
        render."""
        st = self.state(v)
        out = []
        for s, ts in sorted(st["towers"].items()):
            out.append((s, round(ts["lift"] / q), round(ts["shutter"] * 50),
                        tuple(sorted((k, round(y / q), round(z / q)) for k, (y, z) in ts["trays"].items()))))
        for us in st["units"]:
            p, arm = us["pose"], us["arm"]
            out.append((round(p[0] / q), round(p[1] / q), round(p[2] * 10 / q), arm[0],
                        arm[1] if len(arm) > 1 else None, round(arm[2] * 300) if len(arm) > 2 else None))
        return tuple(out)

    def window_counts(self, v0: float, v1: float) -> dict:
        """Requests released over video [v0, v1): asked for and drawn, trays and floor jobs (cumulative sums)."""
        if not hasattr(self, "_cum"):
            vs = np.array([r.v for r in self.reqs], float)
            cols = {"tray_asked": [r.kind == "tray" for r in self.reqs],
                    "tray_drawn": [r.kind == "tray" and bool(r.drawn) for r in self.reqs],
                    "floor_asked": [r.kind != "tray" for r in self.reqs],
                    "floor_drawn": [r.kind != "tray" and bool(r.drawn) for r in self.reqs]}
            self._cum = (vs, {k: np.concatenate([[0], np.cumsum(np.array(v, int))]) for k, v in cols.items()})
        vs, cum = self._cum
        i0, i1 = np.searchsorted(vs, v0, "left"), np.searchsorted(vs, v1, "left")
        return {k: int(c[i1] - c[i0]) for k, c in cum.items()}

    def lab_counts(self, h0: float, h1: float) -> dict:
        """The same over lab hours [h0, h1)."""
        return self.window_counts(self.clock.video(h0), self.clock.video(h1) if h1 < self.clock.h[-1] else 1e18)


def plan(R, kin: dict, clock: Clock, dt: float = 1.0 / 120.0) -> Plan:
    """Simulate the tower and unit moves over the clock's span, in video time, as the module docstring says."""
    fl = Floor(kin)
    reqs = requests(R, kin, clock)
    for r in reqs:
        r.drawn = False
    shuttles = sorted({int(t["shuttle"]) for t in kin["trays"].values()})
    towers = {s: [] for s in shuttles}
    T = {s: dict(phase="idle", tray=None, until=-1e9, lift=kin["lift_home"], job=None, since=0.0) for s in shuttles}
    pending = {s: [] for s in shuttles}                    # released tray requests, oldest first
    nu = len(kin["chargers"])
    units: list = [[] for _ in range(nu)]
    U = [dict(phase="charge", where=i, until=-1e9, idle_since=-1e9, job=None, dest=None) for i in range(nu)]
    jobs: list = []
    floor_pending: list = []
    counts = dict(tray_asked=0, floor_asked=0, presentations=0, floor_visits=0)
    ri = 0
    v0, v_end = clock.span
    n = int(math.ceil((v_end - v0) / dt)) + 1

    def rate(vv):
        return move_rate(clock.speed(vv))

    def start_work(u, job, vv):
        r = rate(vv) * ARM_X
        dur = sum(ARM_S.values()) / r
        units[u].append(UnitAct(vv, vv + dur, "work", job.dock, rate=r, job=job))
        U[u].update(phase="work", until=vv + dur, job=job)
        job.v_start = vv

    def go(u, job, vv):
        st = U[u]
        job.unit = u
        st["job"] = job
        if st["where"] == job.dock:
            if job.kind == "shuttle" and vv < job.ready:
                units[u].append(UnitAct(vv, job.ready, "wait", job.dock, job=job))
                st.update(phase="wait", until=job.ready)
            else:
                start_work(u, job, vv)
            return
        segs = fl.route(st["where"], job.dock)
        r_ = rate(vv)
        dur = segs_seconds(segs) / r_
        units[u].append(UnitAct(vv, vv + dur, "drive", job.dock, segs=segs, rate=r_, job=job))
        st.update(phase="drive", until=vv + dur, dest=job.dock, where=None)

    def taken(dock, u):
        """Is the dock held by another unit: standing there, or going there?"""
        for o in range(nu):
            if o == u:
                continue
            so = U[o]
            if so["where"] == dock or so["dest"] == dock and so["phase"] == "drive" or (
                    so["job"] is not None and so["job"].dock == dock):
                return True
        return False

    for step in range(n):
        v = v0 + step * dt
        # -------------------------------------------------------------------------------- requests reach the clock
        while ri < len(reqs) and reqs[ri].v <= v:
            r = reqs[ri]
            ri += 1
            if r.kind == "tray":
                counts["tray_asked"] += 1
                pending[r.shuttle].append(r)
            else:
                counts["floor_asked"] += 1
                floor_pending.append(r)
        # -------------------------------------------------------------------------------- the towers
        for s in shuttles:
            ts = T[s]
            if ts["phase"] in ("fetch", "store") and v >= ts["until"]:
                if ts["phase"] == "fetch":
                    ts.update(phase="open", since=v, lift=kin["open"][1])
                else:
                    ts.update(phase="idle", tray=None)
            if ts["phase"] == "open":
                job = ts["job"]
                done = job is not None and job.v_done >= 0 and v >= job.v_done
                gave_up = job is not None and job.unit < 0 and v - ts["since"] > UNIT_WAIT_S
                if done or gave_up:
                    if gave_up:
                        job.dropped = True
                    same = [r for r in pending[s] if r.where == ts["tray"]]
                    if same and len(same) == len(pending[s]) and not gave_up:
                        for r in same:                    # asked for again while it stood there: served there
                            r.drawn = True
                        pending[s] = []
                        nj = Job(v, SHUTTLE_DOCK[s], "shuttle", v, shuttle=s, req=same[-1])
                        jobs.append(nj)
                        ts.update(job=nj, since=v)
                    else:
                        prof = store_profile(kin, ts["tray"])
                        dur = profile_seconds(prof) / rate(v)
                        towers[s].append(TowerMove(v, v + dur, ts["tray"], "store", prof, kin["open"][1]))
                        ts.update(phase="store", until=v + dur, job=None, lift=kin["trays"][ts["tray"]]["z"])
            if ts["phase"] == "idle" and pending[s]:
                r = pending[s][-1]                         # the latest request; the older ones are dropped
                for x in pending[s]:
                    if x.where == r.where:
                        x.drawn = True
                pending[s] = []
                prof = fetch_profile(kin, r.where, ts["lift"])
                dur = profile_seconds(prof) / rate(v)
                mv = TowerMove(v, v + dur, r.where, "fetch", prof, ts["lift"])
                mv.req = r
                towers[s].append(mv)
                ts.update(phase="fetch", tray=r.where, until=v + dur)
                counts["presentations"] += 1
                job = Job(v, SHUTTLE_DOCK[s], "shuttle", v + dur, shuttle=s, req=r)
                jobs.append(job)
                ts["job"] = job
        floor_pending = [r for r in floor_pending if v - r.v <= FLOOR_LAG_S]
        # -------------------------------------------------------------------------------- the units' own clocks
        for u in range(nu):
            st = U[u]
            if st["phase"] not in ("drive", "work", "wait") or v < st["until"]:
                continue
            if st["phase"] == "drive":
                st["where"], st["dest"] = st["dest"], None
                job = st["job"]
                if job is None:
                    st.update(phase="charge", idle_since=v)
                elif job.kind == "shuttle" and v < job.ready:
                    units[u].append(UnitAct(v, job.ready, "wait", job.dock, job=job))
                    st.update(phase="wait", until=job.ready)
                else:
                    start_work(u, job, v)
            elif st["phase"] == "wait":
                start_work(u, st["job"], v)
            else:
                st["job"].v_done = v
                st.update(phase="idle", job=None, idle_since=v)
        # -------------------------------------------------------------------------------- jobs to free units
        free = [u for u in range(nu) if U[u]["phase"] in ("idle", "charge")]
        if free:
            cands = [j for j in jobs if j.unit < 0 and not j.dropped and T[j.shuttle]["job"] is j]
            # oldest first across both kinds: a tray waiting at an opening and a machine waiting for its sample
            items = sorted(cands + list(floor_pending), key=lambda it: it.v_post if isinstance(it, Job) else it.v)
            for item in items:
                if not free:
                    break
                dock = item.dock if isinstance(item, Job) else item.where
                ok = [u for u in free if U[u]["where"] == dock or not taken(dock, u)]
                if not ok:
                    continue
                u = min(ok, key=lambda u_: (fl.seconds(U[u_]["where"], dock), u_))
                if isinstance(item, Job):
                    job = item
                else:
                    job = Job(item.v, dock, "floor", item.v, req=item)
                    jobs.append(job)
                    for x in [x for x in floor_pending if x.where == dock]:
                        x.drawn = True                     # requests at the same dock: served by this visit
                        floor_pending.remove(x)
                    counts["floor_visits"] += 1
                go(u, job, v)
                free.remove(u)
            for u in free:                                 # nothing to do for a while: back to charge
                st = U[u]
                if st["phase"] == "idle" and isinstance(st["where"], str) and v - st["idle_since"] > IDLE_HOME_S:
                    segs = fl.route(st["where"], u)
                    r_ = rate(v)
                    dur = segs_seconds(segs) / r_
                    units[u].append(UnitAct(v, v + dur, "drive", u, segs=segs, rate=r_))
                    st.update(phase="drive", until=v + dur, dest=u, where=None, job=None)
    counts["tray_drawn"] = sum(1 for r in reqs if r.kind == "tray" and r.drawn)
    counts["floor_drawn"] = sum(1 for r in reqs if r.kind == "floor" and r.drawn)
    out = Plan(kin, clock, towers, units, counts, reqs)
    out.R = R                                              # the run its requests index (lab3d_cut's tags)
    return out


def summary(p: Plan) -> dict:
    c = dict(p.counts)
    c["tower_moves"] = {s: len(ms) for s, ms in p.towers.items()}
    c["unit_drives"] = [sum(1 for a in acts if a.kind == "drive") for acts in p.units]
    c["unit_works"] = [sum(1 for a in acts if a.kind == "work") for acts in p.units]
    return c
