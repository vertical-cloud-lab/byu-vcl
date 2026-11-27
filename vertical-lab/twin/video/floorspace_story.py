"""The floor-space segment's choreography, as pure functions of time: where every instrument, machine, wall, person,
robot, tray and the camera is at t (s from the segment's start). No VTK here, so the overlay and the 3-D render read
the same story (twin/video/floorspace3d.py renders it, twin/video/floorspace_cut.py draws over it).

The segment, in four phases (PH, s):

* conv   the conventional lab (floorspace.conventional): people walk between stations carrying sample boxes;
* flat   the same plan automated: four MiR250 + UR12e units drive in and take the routes people walked, docking
         targets, fixed arms and sample racks come up at the stations, most of the people leave;
* vert   the two Shuttles come down north of the building, every benchtop instrument flies to its tray (the tray plan),
         the walls and benches go, the floor machines move to the vertical layout around one MiR aisle, the camera
         closes in on the smaller floor, and the lab works: trays presented, two units docking;
* plans  (2-D, floorspace_cut.py) the three footprints side by side.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import floorspace as FS

HERE = Path(__file__).resolve().parents[2]
PH = dict(conv=0.0, flat=31.0, vert=51.0, plans=83.0, end=138.5)
T3D_END = PH["plans"] + 2.6            # the 3-D renders run into the cross-fade
WALK = 1150.0                          # mm/s, a person
DRIVE = 900.0                          # mm/s, a MiR250 among people (the spec sheet allows 2000)
STRIDE = 1016.0                        # people.Person.STRIDE
WALL_H = 1200.0                        # the walls are cut at 1.2 m, as an architect's model, so the rooms show
SLOT = {"R1": (1030.0, 300.0), "R2": (1030.0, 1050.0), "R3": (1030.0, 1800.0), "R4": (1030.0, 2700.0),
        "R5": (1030.0, 3425.0), "F0": (-1030.0, 300.0), "F1": (-1030.0, 1950.0), "F2": (-1030.0, 2675.0),
        "2R1": (1030.0, 300.0), "2R2": (1030.0, 1150.0), "2R3": (1030.0, 1875.0), "2R4": (1030.0, 2625.0),
        "2R5": (1030.0, 3250.0), "2R6": (1030.0, 3400.0), "2F0": (-1030.0, 300.0), "2F0b": (-1030.0, 525.0),
        "2F1": (-1030.0, 1950.0), "2F2": (-1030.0, 2675.0), "open": (-1030.0, 854.0)}
SHUTTLE_X = {1: 0.0, 2: 3630.0}
VLM_DOCK_Y = -1932.0                   # a MiR250 docked at a Shuttle's opening (the 3-D lab's dock)


def ease(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def win(t: float, t0: float, t1: float) -> float:
    return ease((t - t0) / max(t1 - t0, 1e-9))


def ang(f: str) -> float:
    return FS.FACING[f]


def wrap(a: float) -> float:
    return (a + 180.0) % 360.0 - 180.0


# ============================================================================================ paths
@dataclass
class Leg:
    kind: str                     # walk | dwell
    t0: float
    t1: float
    pts: np.ndarray | None = None  # walk: (n, 2) polyline
    s0: float = 0.0               # walk: distance walked before this leg (the gait's phase)
    at: tuple | None = None       # dwell: (x, y, heading deg (math convention: 0 = +x))
    target: tuple | None = None   # dwell: the point worked on (x, y, z)
    station: str | None = None


def _plen(pts: np.ndarray) -> float:
    return float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1))) if len(pts) > 1 else 0.0


def _along(pts: np.ndarray, s: float) -> tuple[np.ndarray, float]:
    """The point at distance s along a polyline, and the heading there (deg, 0 = +x), blended over 250 mm at corners."""
    seg = np.diff(pts, axis=0)
    L = np.linalg.norm(seg, axis=1)
    cum = np.r_[0.0, np.cumsum(L)]
    s = min(max(s, 0.0), cum[-1])
    i = int(min(np.searchsorted(cum, s, side="right") - 1, len(L) - 1))
    while i > 0 and L[i] < 1e-6:
        i -= 1
    f = (s - cum[i]) / max(L[i], 1e-9)
    p = pts[i] + seg[i] * f
    h = math.degrees(math.atan2(seg[i][1], seg[i][0])) if L[i] > 1e-6 else 0.0
    blend = 250.0
    if i + 1 < len(L) and cum[i + 1] - s < blend and L[i + 1] > 1e-6:
        h2 = math.degrees(math.atan2(seg[i + 1][1], seg[i + 1][0]))
        w = 0.5 * (1 - (cum[i + 1] - s) / blend)
        h = h + wrap(h2 - h) * w
    elif i > 0 and s - cum[i] < blend and L[i - 1] > 1e-6:
        h0 = math.degrees(math.atan2(seg[i - 1][1], seg[i - 1][0]))
        w = 0.5 * (1 - (s - cum[i]) / blend)
        h = h + wrap(h0 - h) * w
    return p, h


class Agent:
    """A person or a robot on a schedule of legs: walk/drive along polylines at a constant speed, dwell at stations."""

    def __init__(self, name: str, kind: str, speed: float, t_in: float = 0.0, t_out: float = 1e9,
                 fade: float = 0.8):
        self.name, self.kind, self.speed = name, kind, speed
        self.legs: list[Leg] = []
        self.t_in, self.t_out, self.fade = t_in, t_out, fade
        self.walked = 0.0

    def walk(self, t0: float, pts) -> float:
        pts = np.asarray(pts, float)
        keep = [pts[0]]
        for p in pts[1:]:
            if np.linalg.norm(p - keep[-1]) > 1.0:
                keep.append(p)
        pts = np.array(keep)
        L = _plen(pts)
        t1 = t0 + L / self.speed
        self.legs.append(Leg("walk", t0, t1, pts=pts, s0=self.walked))
        self.walked += L
        return t1

    def dwell(self, t0: float, t1: float, at, target=None, station=None) -> float:
        self.legs.append(Leg("dwell", t0, t1, at=tuple(at), target=target, station=station))
        return t1

    def state(self, t: float) -> dict:
        """{x, y, hd (deg, 0 = +x), moving (0-1), s (distance walked), target, station, alpha}"""
        legs = self.legs
        if not legs:
            return dict(alpha=0.0)
        if t <= legs[0].t0:
            lg = legs[0]
        else:
            lg = legs[-1]
            for l_ in legs:
                if l_.t0 <= t < l_.t1:
                    lg = l_
                    break
        a = 1.0
        if self.fade > 0:
            a = min(1.0, max(0.0, (t - self.t_in) / self.fade + (1.0 if self.t_in <= PH["conv"] else 0.0)))
            a = min(a, max(0.0, (self.t_out - t) / self.fade))
        if lg.kind == "walk":
            s = (min(max(t, lg.t0), lg.t1) - lg.t0) * self.speed
            p, h = _along(lg.pts, s)
            mv = 1.0 if lg.t0 <= t <= lg.t1 else 0.0
            return dict(x=float(p[0]), y=float(p[1]), hd=h, moving=mv, s=lg.s0 + s, target=None, station=None,
                        alpha=a, u=0.0)
        x, y, h = lg.at
        u = (t - lg.t0) / max(lg.t1 - lg.t0, 1e-9)
        return dict(x=x, y=y, hd=h, moving=0.0, s=lg.s0 if hasattr(lg, "s0") else 0.0, target=lg.target,
                    station=lg.station, alpha=a, u=min(max(u, 0.0), 1.0), t_in_dwell=t - lg.t0,
                    t_left=lg.t1 - t)


# ============================================================================================ the story
class Story:
    def __init__(self):
        self.inv, (self.conv, self.flat, self.vert) = FS.build_all()
        self.tp = json.loads((HERE / "out" / "tray_plan.json").read_text())
        self._rooms = {r["name"]: r for r in self.conv.rooms}
        self.cor = next(a for a in self.conv.aisles if a["kind"] == "corridor")["rect"]
        self.cor_y = (self.cor[1] + self.cor[3]) / 2
        self._items()
        self._machines()
        self._people()
        self._robots()
        self._trays()
        self._cameras()

    # ---------------------------------------------------------------------------------------- benchtop items
    def tray_of(self, it) -> tuple:
        """(shuttle, slot y, slot z) of an item's tray at home."""
        tr = self.tp["trays"][it.tray]
        y, z = SLOT[tr["slot"]]
        return tr["shuttle"], y, z

    def _items(self):
        """Each benchtop item's flight: from its bench (conventional place) to its tray (home slot), staggered, the
        storage racks last."""
        keys = [k for k, it in self.inv.items() if it.tray is not None]
        # order: by distance to the Shuttles, nearest first, so the flights spread from the north
        keys.sort(key=lambda k: (self.inv[k].group in ("jars", "store"), -self.conv.places[k].y))
        t0, t1 = PH["vert"] + 3.6, PH["vert"] + 10.4
        dur = 2.6
        self.fly = {}
        n = len(keys)
        for i, k in enumerate(keys):
            s = t0 + (t1 - t0) * i / max(1, n - 1)
            self.fly[k] = (s, s + dur)
        self.fly_end = t1 + dur

    def item_local(self, k) -> tuple:
        """An item's anchor in its tray's frame: (cx, cy, z0), the centre of its footprint at its base (tray plan)."""
        b = self.inv[k].box
        return ((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, b[4])

    def item_pose(self, k, t, local=None) -> tuple:
        """(x, y, z, theta deg, where) of an item's anchor: on its bench, in flight, or in its tray (where = 'tray')."""
        it = self.inv[k]
        p = self.conv.places[k]
        cx, cy, z0 = local or self.item_local(k)
        bench = (p.x, p.y, p.z, ang(p.facing) - ang("S"))
        sh, ys, zs = self.tray_of(it)
        tray = (SHUTTLE_X[sh] + cx, ys + cy, zs + z0, 0.0)
        a, b = self.fly[k]
        if t <= a:
            return (*bench, "bench")
        if t >= b:
            return (*tray, "tray")
        u = ease((t - a) / (b - a))
        d = math.hypot(tray[0] - bench[0], tray[1] - bench[1])
        lift = 1600.0 + 0.12 * d
        x = bench[0] + (tray[0] - bench[0]) * u
        y = bench[1] + (tray[1] - bench[1]) * u
        z = bench[2] + (tray[2] - bench[2]) * u + lift * math.sin(math.pi * u)
        th = bench[3] + wrap(tray[3] - bench[3]) * u
        return (x, y, z, th, "flight")

    # ---------------------------------------------------------------------------------------- floor machines
    def _machines(self):
        keys = [k for k, it in self.inv.items() if it.tray is None]
        keys.sort(key=lambda k: self.vert.places[k].x)
        t0, t1 = PH["vert"] + 14.6, PH["vert"] + 17.2
        self.move = {}
        for i, k in enumerate(keys):
            s = t0 + (t1 - t0) * i / max(1, len(keys) - 1)
            self.move[k] = (s, s + 3.4)
        self.move_end = t1 + 3.4

    def machine_pose(self, k, t) -> tuple:
        """(x, y, theta deg) of a floor machine's plan centre and its front's facing."""
        a, b = self.move[k]
        p0, p1 = self.conv.places[k], self.vert.places[k]
        A_ = (p0.x, p0.y, ang(p0.facing))
        B_ = (p1.x, p1.y, ang(p1.facing))
        u = win(t, a, b)
        return (A_[0] + (B_[0] - A_[0]) * u, A_[1] + (B_[1] - A_[1]) * u, A_[2] + wrap(B_[2] - A_[2]) * u)

    # ---------------------------------------------------------------------------------------- what comes and goes
    def vlm_dz(self, t) -> tuple[float, float]:
        """(dz, alpha) of the Shuttles: hidden until they come down north of the building."""
        a, b = PH["vert"] + 0.4, PH["vert"] + 3.6
        if t < a:
            return 11000.0, 0.0
        return 11000.0 * (1 - win(t, a, b)), 1.0

    def sink(self, t) -> float:
        """0 -> 1: the conventional lab's walls, benches and shelves going down into the floor."""
        return win(t, PH["vert"] + 12.4, PH["vert"] + 14.6)

    def grow(self, t) -> float:
        """0 -> 1: the vertical lab's floor spreading from the Shuttles."""
        return win(t, PH["vert"] + 15.2, PH["vert"] + 20.4)

    def pop(self, t, i=0, n=1, phase="flat") -> float:
        """0 -> 1: the automation's pieces coming up in the flat lab (i of n, staggered), and going with the benches."""
        if phase == "flat":
            a = PH["flat"] + 1.5 + 4.0 * i / max(1, n)
            return win(t, a, a + 0.9) * (1 - self.sink(t))
        a = PH["vert"] + 19.6 + 1.6 * i / max(1, n)
        return win(t, a, a + 0.8)

    # ---------------------------------------------------------------------------------------- people
    def access(self, key: str, lay=None) -> tuple:
        """Where a person or robot stands to work at a station in the conventional plan: in its zone's aisle, in front of
        it, facing it. -> (x, y, heading to the station (deg), the point worked on (x, y, z), zone)."""
        lay = lay or self.conv
        p = lay.places[key]
        r = self._rooms[p.zone]
        it = self.inv[key]
        x = min(max(p.x, r["rect"][0] + 500.0), r["rect"][2] - 500.0)
        y = r["aisle_y"]
        hd = 90.0 if p.y > y else -90.0
        z = (p.z + 150.0) if p.on == "bench" else 1000.0
        rr = p.rect(it)
        ty = rr[1] if p.y > y else rr[3]
        if p.on == "bench":
            b = next(b for b in lay.benches if key in b["keys"])
            ty = b["rect"][1] + 150 if p.y > y else b["rect"][3] - 150
        return (x, y, hd, (p.x, ty, z), p.zone)

    def route(self, a, b, lane=0.0) -> np.ndarray:
        """A walk between two stations' access points in the conventional plan: along a zone's aisle to its entry,
        through it, along the corridor (in a lane, so people pass), in through the other zone's entry."""
        xa, ya, _, _, za = self.access(a)
        xb, yb, _, _, zb = self.access(b)
        if za == zb:
            return np.array([(xa, ya), (xb, yb)])
        ra, rb = self._rooms[za], self._rooms[zb]
        ea, eb = ra["entry"][0], rb["entry"][0]
        yc = self.cor_y + lane
        return np.array([(xa, ya), (ea, ya), (ea, yc), (eb, yc), (eb, yb), (xb, yb)])

    def _tour(self, ag: Agent, stations: list, t0: float, t_end: float, dwell=(4.0, 6.0), lane=0.0, start=None,
              rng=None):
        """Walk a loop of stations from t0 until t_end, dwelling at each; start: a point to walk from first."""
        rng = rng or np.random.default_rng(len(ag.name))
        t = t0
        cur = None
        i = 0
        if start is not None:
            x, y, hd, tgt, _ = self.access(stations[0])
            first = self.access(stations[0])
            ent = self._rooms[first[4]]["entry"][0]
            t = ag.walk(t, [start, (ent, self.cor_y + lane), (ent, y), (x, y)])
            cur = stations[0]
            t = ag.dwell(t, t + float(rng.uniform(*dwell)), (x, y, hd), tgt, cur)
            i = 1
        while t < t_end:
            nxt = stations[i % len(stations)]
            i += 1
            if cur is None:
                x, y, hd, tgt, _ = self.access(nxt)
                t = ag.dwell(t, t + float(rng.uniform(*dwell)), (x, y, hd), tgt, nxt)
                cur = nxt
                continue
            if nxt == cur:
                continue
            t = ag.walk(t, self.route(cur, nxt, lane))
            x, y, hd, tgt, _ = self.access(nxt)
            t = ag.dwell(t, t + float(rng.uniform(*dwell)), (x, y, hd), tgt, nxt)
            cur = nxt
        return t

    def _exit(self, ag: Agent, t0: float, side: int, lane=0.0) -> float:
        """From wherever its schedule has it at t0 (cut there), out of the corridor's west (-1) or east (+1) end."""
        st = ag.state(t0)
        ag.legs = [l_ for l_ in ag.legs if l_.t0 < t0]
        if ag.legs:
            ag.legs[-1].t1 = t0
            if ag.legs[-1].kind == "walk":
                s = (t0 - ag.legs[-1].t0) * ag.speed
                p, _ = _along(ag.legs[-1].pts, s)
                pts = [q for q in ag.legs[-1].pts]
                cum = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(ag.legs[-1].pts, axis=0), axis=1))]
                ag.legs[-1].pts = np.array([q for q, c in zip(pts, cum) if c < s] + [p])
        x, y = st["x"], st["y"]
        z = self._zone_at(x, y)
        if side == 0:                                   # the nearer end
            side = -1 if x - self.conv.envelope[0] < self.conv.envelope[2] - x else 1
        ex = self.conv.envelope[0] - 2500.0 if side < 0 else self.conv.envelope[2] + 2500.0
        yc = self.cor_y + lane
        if z is None:
            pts = [(x, y), (x, yc), (ex, yc)]
        else:
            r = self._rooms[z]
            pts = [(x, y), (x, r["aisle_y"]), (r["entry"][0], r["aisle_y"]), (r["entry"][0], yc), (ex, yc)]
        t1 = ag.walk(t0, pts)
        ag.t_out = t1 - 0.4
        return t1

    def _zone_at(self, x, y):
        for r in self.conv.rooms:
            x0, y0, x1, y1 = r["rect"]
            if x0 <= x <= x1 and y0 <= y <= y1:
                return r["name"]
        return None

    def _people(self):
        """Six people in the conventional lab, each on a loop that follows the samples. Four leave as the robots come
        in; two stay at the powder room's and the AM bay's machines until the walls go. One works the glovebox and the
        atomizer in the vertical lab."""
        P = {
            "p1": (["repowder", "aconity", "wire_edm", "F1", "instron_floor"], -500.0),
            "p2": (["D1", "D0", "M0", "B1"], 500.0),
            "p3": (["C0", "packaging", "G0", "H1"], -250.0),
            "p4": (["L0", "F0", "K1", "E1"], 250.0),
            "p5": (["glovebox", "B1", "sieve_cell", "repowder", "I0"], -650.0),
            "p6": (["eos_m400", "ded", "meltio_cell", "aconity"], 650.0),
        }
        self.people = {}
        offs = {"p1": 0.0, "p2": 1.5, "p3": 3.0, "p4": 0.7, "p5": 2.2, "p6": 1.1}
        for nm, (st, lane) in P.items():
            ag = Agent(nm, "person", WALK, t_in=-1.0)
            self._tour(ag, st, PH["conv"] - offs[nm], PH["vert"] + 16.0, lane=lane,
                       rng=np.random.default_rng(int(nm[1:]) * 7))
            self.people[nm] = ag
        # the robots take over: four leave by the corridor's ends
        for nm, side, tt in (("p1", 0, PH["flat"] + 3.0), ("p2", 0, PH["flat"] + 4.0), ("p3", 0, PH["flat"] + 5.0),
                             ("p4", 0, PH["flat"] + 6.0)):
            ag = self.people[nm]
            ag.speed = 1350.0
            self._exit(ag, tt, side, self.people_lane(nm))
            ag.t_out = min(ag.t_out, tt + 12.0)            # out of sight by then, fading on the way
        for nm in ("p5", "p6"):
            ag = self.people[nm]
            ag.t_out = PH["vert"] + 13.8
        # the vertical lab's person: at the glovebox's ports, then the atomizer
        ag = Agent("p7", "person", WALK, t_in=PH["vert"] + 20.5)
        g = self.vert.places["glovebox"]
        rp = self.vert.places["repowder"]
        ya = -2150.0
        t = ag.dwell(PH["vert"] + 20.0, PH["vert"] + 27.0, (g.x + 900.0, ya, 90.0), (g.x + 250.0, g.y - 900.0, 1100.0),
                     "glovebox")
        t = ag.walk(t, [(g.x + 900.0, ya), (rp.x - 700.0, ya)])
        t = ag.dwell(t, PH["end"], (rp.x - 700.0, ya, 90.0), (rp.x - 500.0, -1700.0, 1150.0), "repowder")
        self.people["p7"] = ag

    def people_lane(self, nm):
        return {"p1": -500.0, "p2": 500.0, "p3": -250.0, "p4": 250.0}.get(nm, 0.0)

    # ---------------------------------------------------------------------------------------- robots
    def _robots(self):
        """Four MiR250 + UR12e units drive in from the corridor's east end and run the people's loops; at the change
        two leave and two drive to the vertical lab's aisle, where they shuttle between the Shuttles' openings and the
        floor machines."""
        x1 = self.conv.envelope[2]
        R = {
            "r1": (["repowder", "aconity", "wire_edm", "F1", "instron_floor"], -300.0, 0.0),
            "r2": (["D1", "D0", "M0", "B1"], 300.0, 1.4),
            "r3": (["C0", "packaging", "G0", "H1"], -300.0, 2.8),
            "r4": (["L0", "F0", "K1", "E1"], 300.0, 4.2),
        }
        self.robots = {}
        for nm, (st, lane, dt) in R.items():
            ag = Agent(nm, "robot", DRIVE, t_in=PH["flat"] + 0.8 + dt, fade=0.01)
            t0 = PH["flat"] + 0.8 + dt
            start = (x1 + 2500.0, self.cor_y + lane)
            self._tour(ag, st, t0, PH["vert"] + 12.0, dwell=(5.0, 7.0), lane=lane, start=start,
                       rng=np.random.default_rng(int(nm[1:]) * 11))
            self.robots[nm] = ag
        # at the change (walls going), every loop is cut: the two units nearest the Shuttles drive to their openings
        # (they become r1 and r2), the other two leave by the nearer end of the corridor
        tc = PH["vert"] + 12.4
        ya = (FS.ASSUME["dock_zone"] * -1 - 1562.0 + (-1562.0 - FS.ASSUME["dock_zone"] - FS.ASSUME["mir_aisle"])) / 2
        self.aisle_y = ya
        near = sorted(self.robots, key=lambda n: -self.robots[n].state(tc)["y"])
        keep = sorted(near[:2], key=lambda n: self.robots[n].state(tc)["x"])
        leave = near[2:]
        ren = {keep[0]: "r1", keep[1]: "r2"}
        for i, nm in enumerate(leave):
            ren[nm] = f"r{3 + i}"
        self.robots = {ren[n]: ag for n, ag in self.robots.items()}
        for n, ag in self.robots.items():
            ag.name = n
        for nm in ("r3", "r4"):
            ag = self.robots[nm]
            ag.speed = 1500.0
            self._exit(ag, tc, 0, 0.0)
            ag.t_out = min(ag.t_out, tc + 4.5)
        for nm, xs in (("r1", SHUTTLE_X[1]), ("r2", SHUTTLE_X[2])):
            ag = self.robots[nm]
            st = ag.state(tc)
            ag.legs = [l_ for l_ in ag.legs if l_.t0 < tc]
            if ag.legs:
                ag.legs[-1].t1 = tc
                if ag.legs[-1].kind == "walk":
                    s = (tc - ag.legs[-1].t0) * ag.speed
                    p, _ = _along(ag.legs[-1].pts, s)
                    cum = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(ag.legs[-1].pts, axis=0), axis=1))]
                    ag.legs[-1].pts = np.array([q for q, c in zip(ag.legs[-1].pts, cum) if c < s] + [p])
            # wait for the walls to go down, then drive straight up to the aisle (faster: the floor is clear) and dock
            # at the opening
            t = ag.dwell(tc, PH["vert"] + 14.8, (st["x"], st["y"], st["hd"]))
            ag.speed = 1500.0
            t = ag.walk(t, [(st["x"], st["y"]), (st["x"], ya), (xs + (1400.0 if nm == "r1" else -1400.0), ya),
                            (xs, VLM_DOCK_Y)])
            t = ag.dwell(t, max(t, self.move_end + 0.5), (xs, VLM_DOCK_Y, 0.0), (xs, -1300.0, 900.0),
                         "vlm1" if nm == "r1" else "vlm2")
            ag.speed = DRIVE
            self._vloop(ag, nm, t)

    def vdock(self, key) -> tuple:
        """A MiR250's dock pose in the vertical lab: (x, y, heading)."""
        if key in ("vlm1", "vlm2"):
            return (SHUTTLE_X[1 if key == "vlm1" else 2], VLM_DOCK_Y, 0.0)
        d = next(d for d in self.vert.docks if d["station"] == key)
        return (d["x"], d["y"], 0.0 if d["y"] > self.aisle_y else 180.0)

    def _vloop(self, ag: Agent, nm: str, t: float):
        home = "vlm1" if nm == "r1" else "vlm2"
        stops = (["repowder", home, "instron_floor", home, "sieve_cell", home] if nm == "r1" else
                 ["aconity", home, "wire_edm", home, "ded", home])
        x, y, h = self.vdock(home)
        t = ag.dwell(t, t + (6.5 if nm == "r1" else 4.0), (x, y, h), (x, -1300.0, 900.0), home)
        cur = home
        ya = self.aisle_y + (350.0 if nm == "r1" else -350.0)
        for k in stops * 3:
            if t > PH["end"]:
                break
            x0, y0, _ = self.vdock(cur)
            x1, y1, h1 = self.vdock(k)
            sx = 1.0 if x1 > x0 else -1.0
            pts = [(x0, y0), (x0 + sx * 700.0, ya), (x1 - sx * 700.0, ya), (x1, y1)]
            if abs(x1 - x0) < 1600.0:
                pts = [(x0, y0), ((x0 + x1) / 2, ya), (x1, y1)]
            t = ag.walk(t, pts)
            tgt = (x1, -1300.0 if y1 > self.aisle_y else -6000.0, 950.0)
            t = ag.dwell(t, t + (5.5 if k in ("vlm1", "vlm2") else 4.5), (x1, y1, h1), tgt, k)
            cur = k

    # ---------------------------------------------------------------------------------------- trays at the openings
    def _trays(self):
        """Tray presentations in the vertical lab, timed to the units' stops at the openings."""
        self.present = []
        for nm, k in (("r1", "D"), ("r2", "L")):
            ag = self.robots[nm]
            for lg in ag.legs:
                if (lg.kind == "dwell" and lg.station in ("vlm1", "vlm2") and lg.t0 > PH["vert"] + 18.0
                        and lg.t1 - lg.t0 > 3.0):
                    self.present.append((k, lg.t0, lg.t1))

    def tray_state(self, t) -> dict:
        """Per Shuttle: {lift, shutter, trays: {k: (y, z)}, out}, as lab3d.Lab3D.apply takes it."""
        out = {}
        for s in (1, 2):
            out[s] = dict(lift=SLOT["open"][1], shutter=0.0, trays={}, out=None)
        for k, a, b in self.present:
            tr = self.tp["trays"][k]
            s = tr["shuttle"]
            ys, zs = SLOT[tr["slot"]]
            yo, zo = SLOT["open"]
            lift_t = abs(zs - zo) / 1333.0
            seq = [("lift", 0.0, zs, max(0.6, abs(zs - zo) / 1333.0)), ("pull", ys, 0.0, 1.6),
                   ("lift_up", zs, zo, max(0.6, lift_t)), ("shut", 0.0, 1.0, 0.6), ("push", 0.0, yo, 1.6),
                   ("shut", 1.0, 0.0, 0.5)]
            total = sum(d for *_, d in seq)
            t_start = a - total + 1.2           # the tray reaches the opening a moment after the unit docks
            t_back = b - 0.2
            st = out[s]
            if t < t_start or t > t_back + total:
                continue
            # forward, then held, then the reverse
            if t <= t_start + total:
                tau = t - t_start
                y, z, lift, shut = ys, zs, zo, 0.0
                for nm_, v0, v1, d in seq:
                    u = win(tau, 0.0, d)
                    if nm_ == "lift":
                        lift = zo + (zs - zo) * u
                    elif nm_ == "pull":
                        y = ys + (0.0 - ys) * u
                    elif nm_ == "lift_up":
                        z = zs + (zo - zs) * u
                        lift = z
                    elif nm_ == "shut":
                        shut = v0 + (v1 - v0) * u
                    elif nm_ == "push":
                        y = 0.0 + (yo - 0.0) * u
                    tau -= d
                    if tau < 0:
                        break
                st.update(lift=lift, shutter=shut, out=k if y == yo else None)
                st["trays"][k] = (y, z)
            elif t <= t_back:
                st.update(lift=zo, shutter=0.0, out=k)
                st["trays"][k] = (yo, zo)
            else:
                tau = t - t_back
                rev = [("shut", 0.0, 1.0, 0.5), ("pull_in", yo, 0.0, 1.6), ("shut", 1.0, 0.0, 0.6),
                       ("lift_dn", zo, zs, max(0.6, lift_t)), ("push_back", 0.0, ys, 1.6)]
                y, z, lift, shut = yo, zo, zo, 0.0
                for nm_, v0, v1, d in rev:
                    u = win(tau, 0.0, d)
                    if nm_ == "shut":
                        shut = v0 + (v1 - v0) * u
                    elif nm_ == "pull_in":
                        y = yo + (0.0 - yo) * u
                    elif nm_ == "lift_dn":
                        z = zo + (zs - zo) * u
                        lift = z
                    elif nm_ == "push_back":
                        y = 0.0 + (ys - 0.0) * u
                    tau -= d
                    if tau < 0:
                        break
                st.update(lift=lift, shutter=shut, out=None)
                st["trays"][k] = (y, z)
        return out

    # ---------------------------------------------------------------------------------------- the camera
    def _cameras(self):
        """Keyframes (t, position, focal point, view angle), each fitted to what it must show (fit())."""
        cx0, cy0, cx1, cy1 = self.conv.envelope
        vx0, vy0, vx1, vy1 = self.vert.envelope
        conv_pts = [(cx0, cy0, 0), (cx1, cy0, 0), (cx0, cy1, 0), (cx1, cy1, 0), (cx0, cy1, WALL_H),
                    (cx1, cy1, WALL_H)]
        both = conv_pts + [(-1500.0, 1600.0, 9200.0), (5100.0, 1600.0, 9200.0), (-1500.0, -1600.0, 9200.0)]
        vert_pts = [(vx0, vy0, 0), (vx1, vy0, 0), (vx0, vy1, 0), (vx1, vy1, 0), (-1500.0, 1600.0, 9200.0),
                    (5100.0, 1600.0, 9200.0)]
        vboth = vert_pts + [(cx0, cy0, 0), (cx1, cy0, 0)]          # the old footprint too, as the floor shrinks
        K = []
        K.append((PH["conv"], fit(conv_pts, az=-78.0, el=46.0, va=30.0, margin=(0.03, 0.16, 0.03, 0.10))))
        K.append((PH["conv"] + 15.0, fit(conv_pts, az=-98.0, el=40.0, va=30.0, margin=(0.03, 0.16, 0.03, 0.10))))
        K.append((PH["flat"], fit(conv_pts, az=-86.0, el=50.0, va=30.0, margin=(0.03, 0.16, 0.03, 0.10))))
        K.append((PH["flat"] + 13.0, fit(conv_pts, az=-74.0, el=44.0, va=30.0, margin=(0.03, 0.16, 0.03, 0.10))))
        K.append((PH["vert"], fit(both, az=-82.0, el=36.0, va=30.0, margin=(0.03, 0.12, 0.03, 0.10))))
        K.append((PH["vert"] + 12.0, fit(both, az=-92.0, el=38.0, va=30.0, margin=(0.03, 0.12, 0.03, 0.10))))
        K.append((PH["vert"] + 18.5, fit(vboth, az=-90.0, el=42.0, va=30.0, margin=(0.03, 0.12, 0.03, 0.10))))
        K.append((PH["vert"] + 24.0, fit(vert_pts, az=-98.0, el=38.0, va=30.0, margin=(0.04, 0.12, 0.04, 0.10))))
        K.append((PH["vert"] + 28.5, fit(vert_pts, az=-84.0, el=44.0, va=30.0, margin=(0.04, 0.12, 0.04, 0.10))))
        top = top_view(self.vert.envelope)
        K.append((PH["plans"] - 0.6, top))
        K.append((T3D_END + 1.0, top))
        self.keys = K

    def camera(self, t) -> dict:
        K = self.keys
        if t <= K[0][0]:
            return K[0][1]
        for (ta, ca), (tb, cb) in zip(K[:-1], K[1:]):
            if ta <= t <= tb:
                u = ease((t - ta) / max(tb - ta, 1e-9))
                return blend(ca, cb, u)
        return K[-1][1]


# ============================================================================================ cameras (numpy)
ASPECT = 16 / 9


def look(pos, foc, up=(0, 0, 1)) -> np.ndarray:
    pos, foc, up = (np.asarray(v, float) for v in (pos, foc, up))
    f = foc - pos
    f /= np.linalg.norm(f)
    s = np.cross(f, up)
    if np.linalg.norm(s) < 1e-9:
        s = np.cross(f, (0, 1, 0))
    s /= np.linalg.norm(s)
    u = np.cross(s, f)
    M = np.eye(4)
    M[0, :3], M[1, :3], M[2, :3] = s, u, -f
    M[:3, 3] = -M[:3, :3] @ pos
    return M


def project(cam: dict, pts, size=(1920, 1080)) -> np.ndarray:
    """World points -> pixels (x, y) and depth, as VTK's perspective camera with this view angle (vertical)."""
    P = np.atleast_2d(np.asarray(pts, float))
    V = look(cam["pos"], cam["foc"], cam.get("up", (0, 0, 1)))
    h = np.c_[P, np.ones(len(P))] @ V.T
    f = 1.0 / math.tan(math.radians(cam["va"]) / 2)
    z = -h[:, 2]
    x = f / ASPECT * h[:, 0] / np.maximum(z, 1e-6)
    y = f * h[:, 1] / np.maximum(z, 1e-6)
    return np.c_[(x + 1) / 2 * size[0], (1 - (y + 1) / 2) * size[1], z]


def fit(pts, az, el, va=30.0, margin=(0.04, 0.12, 0.04, 0.05), foc=None) -> dict:
    """A camera looking from azimuth az, elevation el (deg) at pts, as close as it can be with every point inside the
    frame less the margins (left, top, right, bottom, as fractions of the frame), the points' box centred in what the
    margins leave."""
    P = np.asarray(pts, float)
    c = (P.min(0) + P.max(0)) / 2 if foc is None else np.asarray(foc, float)
    c = np.array([c[0], c[1], 0.0])
    d = np.array([math.cos(math.radians(el)) * math.cos(math.radians(az)),
                  math.cos(math.radians(el)) * math.sin(math.radians(az)), math.sin(math.radians(el))])
    W_, H_ = 1920.0, 1080.0
    fx0, fy0, fx1, fy1 = margin[0] * W_, margin[1] * H_, (1 - margin[2]) * W_, (1 - margin[3]) * H_

    def ok(cam):
        q = project(cam, P)
        return (q[:, 2].min() > 0 and q[:, 0].min() >= fx0 and q[:, 0].max() <= fx1 and q[:, 1].min() >= fy0
                and q[:, 1].max() <= fy1)

    dist = 50000.0
    for _ in range(8):
        lo, hi = 1000.0, 600000.0
        for _ in range(50):
            mid = (lo + hi) / 2
            if ok(dict(pos=c + d * mid, foc=c, up=(0, 0, 1), va=va)):
                hi = mid
            else:
                lo = mid
        dist = hi
        cam = dict(pos=c + d * dist, foc=c, up=(0, 0, 1), va=va)
        q = project(cam, P)
        ox = (q[:, 0].min() + q[:, 0].max()) / 2 - (fx0 + fx1) / 2
        oy = (q[:, 1].min() + q[:, 1].max()) / 2 - (fy0 + fy1) / 2
        if abs(ox) < 2 and abs(oy) < 2:
            break
        V = look(cam["pos"], cam["foc"])
        right, up = V[0, :3], V[1, :3]
        s_px = 2 * dist * math.tan(math.radians(va) / 2) / H_
        c = c + right * ox * s_px * 0.9 - up * oy * s_px * 0.9
    return dict(pos=tuple(c + d * dist), foc=tuple(c), up=(0.0, 0.0, 1.0), va=va)


def top_view(env, va=14.0, frac=0.86, offset_y=0.0) -> dict:
    """Straight down on an envelope, long lens (near orthographic), the envelope's width a fraction of the frame."""
    x0, y0, x1, y1 = env
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0), (y1 - y0)
    half_w = w / 2 / frac
    half_h = max(half_w / ASPECT, h / 2 / frac)
    dist = half_h / math.tan(math.radians(va) / 2)
    return dict(pos=(cx, cy + offset_y, dist), foc=(cx, cy + offset_y, 0.0), up=(0.0, 1.0, 0.0), va=va)


def blend(a: dict, b: dict, u: float) -> dict:
    """Between two cameras: the focal point and the distance linearly, the direction by slerp, the angle linearly."""
    fa, fb = np.asarray(a["foc"], float), np.asarray(b["foc"], float)
    da, db = np.asarray(a["pos"], float) - fa, np.asarray(b["pos"], float) - fb
    la, lb = np.linalg.norm(da), np.linalg.norm(db)
    na, nb = da / la, db / lb
    dot = float(np.clip(na @ nb, -1, 1))
    om = math.acos(dot)
    if om < 1e-6:
        n = na
    else:
        n = (math.sin((1 - u) * om) * na + math.sin(u * om) * nb) / math.sin(om)
    foc = fa + (fb - fa) * u
    L = la * (lb / la) ** u
    ua, ub = np.asarray(a.get("up", (0, 0, 1)), float), np.asarray(b.get("up", (0, 0, 1)), float)
    up = ua + (ub - ua) * u
    if np.linalg.norm(up) < 1e-6:
        up = ub
    up = up / np.linalg.norm(up)
    return dict(pos=tuple(foc + n * L), foc=tuple(foc), up=tuple(up), va=a["va"] + (b["va"] - a["va"]) * u)


if __name__ == "__main__":
    st = Story()
    for t in (0, 10, 31, 40, 51, 55, 60, 65, 70, 75, 80, 84):
        c = st.camera(t)
        print(t, [round(v) for v in c["pos"]], round(c["va"], 1))
    print("flights end", round(st.fly_end, 1), "moves end", round(st.move_end, 1))
    for nm, ag in {**st.people, **st.robots}.items():
        print(nm, len(ag.legs), round(ag.legs[0].t0, 1), round(ag.legs[-1].t1, 1), "out", round(ag.t_out, 1))
    print("presentations", [(k, round(a, 1), round(b, 1)) for k, a, b in st.present])
