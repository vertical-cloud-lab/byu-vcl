"""A full nightly pass across the facility (#366, #303): unit 3 (option C in notes/floor_cleaning.md) leaves its
charger at 01:00 and works every powder zone a robot serves, and the aisle, on floor_cleaning.py's floor plan, reach
and pass model, then goes back to charge. A top-down time-lapse.

    python3 floor_pass.py          # -> out/mp4/floor_pass.mp4, out/floor_pass.gif, out/floor_pass.json,
                                   #    out/floor_pass_still.png (the last frame) (about 3 min)
    python3 floor_pass.py plan     # the route only -> out/floor_pass.json

**What comes from the model** (floor_cleaning.py, units_pou: an arm with the wand of a station's 118EXP): where the
robot's centre can be, the floor it cleans (within the arm's 1.3 m of the robot and the hose's 7.0 m of the station),
the zones, the two stations and their zones, the stroke rate (a 0.30 m effective width at 0.15 m/s, times 1.25 for
turns and edges), the 4 min of continuity check, run-on and settle, and driving at 0.5 m/s.

**What is ours here, and assumed:**
- the route: the atomizer's station's zones (glovebox, atomizer, sieving, Shuttle 1's opening, the aisle's west half),
  then the printer line's (Shuttle 2's opening, the MIDI, the DED, the aisle's east half); the EOS is people's;
- the work spots: a greedy cover of each zone by the arm's reach from where the robot can stand, every 200 mm, in a
  nearest-neighbour order, with the drive between them on the floor the robot can stand on;
- a ground stud at each work spot (spots under 800 mm apart share one), clipped and read at each spot, 20 s a spot;
- the camera's look before the lanes and its colour check after them, 10 s each a spot;
- the model's 4 min split as 2 min at the wand's pick-up (continuity on the fixture) and 2 min at its return (20 s of
  run-on, off, 60 s settle, holster), at each of the two stations;
- two events, to show what the robot does with them (the model has no spill rate): loose powder by the sieving
  cell's door, scooped and brushed before the lanes (NFPA 484 11.5), and a visible layer at Shuttle 1's opening,
  which is a person's: unit 3 keeps 1 m away, leaves it, and messages the person (vacuum SOP 8);
- the wheel brush strip at the charger, 1 min.
Notes: notes/floor_cleaning.md.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from collections import deque
from pathlib import Path

import numpy as np

import floor_cleaning as FC

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NAME = "floor_pass"
FPS = 15
GIF_FPS = 10
SPEED_D = 20.0                  # model seconds per video second where each step is shown (the first spot, the two
#                                 powder events, the stations), with a floor per step (MIN_VS) so it can be read
SPEED_R = 150.0                 # and at the routine spots, the time-lapse proper
W_PX, H_PX = 1280, 720
ROBOT = FC.ROBOTS["units_pou"]
ARM_R = ROBOT["cleans"][1]      # 1300 mm: the wand's reach to the floor from the robot's centre (assumed)
HOSE_R = ROBOT["cleans"][2]     # 7000 mm: a 25 ft hose in a straight line (assumed)
STROKE = ROBOT["w_eff"] * ROBOT["v"] / ROBOT["k"]    # m2 a second of lanes (0.30 m x 0.15 m/s / 1.25)
DRIVE_V = 0.5                   # m/s (floor_cleaning.job_table)
BOND_S = 20.0                   # ours, assumed: clip the lead to the spot's stud, read the bond, unclip
LOOK_S = 10.0                   # ours, assumed: the camera's look before the lanes, and its colour check after
PICK_S = ROBOT["fixed_min"] * 60 / 2      # the model's 4 min, split: pick-up and continuity, then return
SCOOP_S = 60.0                  # ours, assumed: scoop and brush a small pile into the conductive bag
WHEEL_S = 60.0                  # ours, assumed: the wheel brush strip at the charger
KEEP_OUT = 1000.0               # ours, assumed: how far unit 3 keeps from a visible spill (its arm's work and its body)
CAM_R = 3000.0                  # ours, assumed: how far its camera sees a visible layer on the floor
STUD_SHARE = 800.0              # spots closer than this share a stud
L_MM, W_MM = ROBOT["L"], ROBOT["W"]
ROUTE = [("atomizer", ["glovebox", "atomizer", "sieving", "opening 1", "aisle"]),
         ("printer line", ["opening 2", "midi", "DED", "aisle"])]
ZONE_TITLES = {"glovebox": "glovebox", "atomizer": "atomizer (rePowder)", "sieving": "sieving cell",
               "opening 1": "Shuttle 1's opening", "opening 2": "Shuttle 2's opening", "midi": "Aconity MIDI",
               "DED": "DED", "aisle": "aisle", "EOS": "EOS M 400-4 (people's)"}
# the two illustrated events (ours: the model has no spill rate)
LOOSE_AT = (-1985.0, -2090.0)   # loose powder in front of the sieving cell's door (its dock)
SPILL_AT = (-150.0, -1950.0)    # a visible layer at Shuttle 1's opening, under the presented trays
MIN_VS = dict(undock=0.8, drive=0.25, turn=0.15, pickup=3.0, ret=2.4, bond=0.9, look=0.7, scoop=2.2, clean=0.7,
              check=0.7, unbond=0.5, spill=4.5, dock=2.0, wait=0.0)

# colours: the repo's (upkeep.py: SURF, INK, INK2; SLOTS[6] is unit 3's in floor_cleaning_year.png)
SURF, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
UNIT3 = "#6250d6"
FLOOR = (0.935, 0.933, 0.918)
ZONE_DIRTY = (0.905, 0.855, 0.760)     # a zone's floor not yet cleaned tonight
CLEAN = (0.780, 0.755, 0.960)          # cleaned tonight (unit 3's purple, lightened)
MACHINE = (0.42, 0.44, 0.47)
PEOPLE = (0.80, 0.80, 0.80)
SPILL = "#c62828"
BRASS = "#a8823c"
LEAD = "#3f8f3f"


# ================================================================================================ the route
def _snap(tree_pts, tree, p):
    return tree_pts[tree.query(p)[1]]


class Grid:
    """The robot-centre floor on a 100 mm lattice, for the drives between spots (8-connected search, then the path
    pulled straight where the lattice has a clear line)."""

    def __init__(self, F, cen):
        from scipy.spatial import cKDTree
        self.F = F
        self.k = 4
        self.ok = cen[::self.k, ::self.k]
        self.xc, self.yc = F.xc[::self.k], F.yc[::self.k]
        ii, jj = np.nonzero(self.ok)
        self.pts = np.c_[self.xc[jj], self.yc[ii]]
        self.ij = np.c_[ii, jj]
        self.tree = cKDTree(self.pts)

    def cell(self, p):
        return tuple(self.ij[self.tree.query(p)[1]])

    def xy(self, c):
        return np.array([self.xc[c[1]], self.yc[c[0]]])

    def clear(self, a, b) -> bool:
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
        for t in np.linspace(0, 1, n):
            i, j = int(round(a[0] + (b[0] - a[0]) * t)), int(round(a[1] + (b[1] - a[1]) * t))
            if not self.ok[i, j]:
                return False
        return True

    def path(self, p0, p1) -> np.ndarray:
        a, b = self.cell(p0), self.cell(p1)
        prev = {a: None}
        q = deque([a])
        ny, nx = self.ok.shape
        while q:
            c = q.popleft()
            if c == b:
                break
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di or dj:
                        n_ = (c[0] + di, c[1] + dj)
                        if 0 <= n_[0] < ny and 0 <= n_[1] < nx and self.ok[n_] and n_ not in prev:
                            prev[n_] = c
                            q.append(n_)
        if b not in prev:
            return np.array([p0, p1], float)
        cells = [b]
        while prev[cells[-1]] is not None:
            cells.append(prev[cells[-1]])
        cells = cells[::-1]
        out, i = [cells[0]], 0                       # string-pulling
        while i < len(cells) - 1:
            j = len(cells) - 1
            while j > i + 1 and not self.clear(cells[i], cells[j]):
                j -= 1
            out.append(cells[j])
            i = j
        pts = [np.asarray(p0, float)] + [self.xy(c) for c in out[1:-1]] + [np.asarray(p1, float)]
        return np.array(pts)


def _heading_at(ok0, ok90, F, p) -> float:
    i, j = F.ij(*p)
    if ok0[i, j]:
        return 0.0
    if ok90[i, j]:
        return 90.0
    return 0.0


def _stud_for(F, p, hd) -> np.ndarray:
    """A free floor point beside the parked robot (ours: the stud sits 150 mm off the chassis on its long side, or at
    its end, on free floor)."""
    a = math.radians(hd)
    ux, uy = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
    for off in (-(W_MM / 2 + 150) * uy, (W_MM / 2 + 150) * uy, (L_MM / 2 + 150) * ux, -(L_MM / 2 + 150) * ux):
        q = np.asarray(p) + off
        i, j = F.ij(*q)
        if 0 <= i < F.ny and 0 <= j < F.nx and F.free[i, j]:
            return q
    return np.asarray(p) + (W_MM / 2 + 150) * uy


def _lane_order(F, cells: np.ndarray, centre) -> np.ndarray:
    """The cells a spot cleans, in the order the squeegee passes them: lanes LANE_W wide along x (along the machines'
    fronts), the lanes taken from the far side in, each in the opposite direction to the last."""
    ii, jj = np.unravel_index(cells, F.free.shape)
    x, y = F.xc[jj], F.yc[ii]
    lane = np.floor((y - y.min()) / 356.0).astype(int)
    far = np.abs(y - centre[1])
    order_l = {l: -float(far[lane == l].mean()) for l in np.unique(lane)}
    lanes = sorted(order_l, key=order_l.get)
    out = []
    for k, l in enumerate(lanes):
        sel = np.nonzero(lane == l)[0]
        s = sel[np.argsort(x[sel] * (1 if k % 2 == 0 else -1), kind="stable")]
        out.append(s)
    return cells[np.concatenate(out)]


def plan() -> dict:
    from scipy.spatial import cKDTree
    F = FC.Floor(bay=True)
    R = FC.reach(F, "units_pou")
    cen, cov = R["centres"], R["covered"]
    ok0, ok90 = R["layers"]
    G = Grid(F, cen)
    near = {s: np.hypot(F.X - FC.POU[s][0], F.Y - FC.POU[s][1]) <= HOSE_R for s, _ in ROUTE}
    d_st = {s: np.hypot(F.X - FC.POU[s][0], F.Y - FC.POU[s][1]) for s, _ in ROUTE}
    aisle_of = {"atomizer": d_st["atomizer"] <= d_st["printer line"],
                "printer line": d_st["atomizer"] > d_st["printer line"]}
    cleaned = np.zeros_like(F.free)
    keep_out = np.hypot(F.X - SPILL_AT[0], F.Y - SPILL_AT[1]) <= KEEP_OUT
    body_out = np.hypot(F.X - SPILL_AT[0], F.Y - SPILL_AT[1]) <= KEEP_OUT + math.hypot(L_MM, W_MM) / 2
    events = []
    spill_found = False
    pos = np.array(_snap(G.pts, G.tree, BAY["park"][:2]))
    hd = 90.0
    start_pos = pos.copy()
    events.append(dict(kind="undock", s=10.0, p=pos.tolist(), hd=hd, detail=True,
                       text="01:00: unit 3 leaves its charger"))
    studs: list[np.ndarray] = []
    spots_out = []
    zone_stats = {}

    def drive_to(p1, hd1, why):
        nonlocal pos, hd
        pth = G.path(pos, p1)
        L = float(np.linalg.norm(np.diff(pth, axis=0), axis=1).sum())
        if L > 1.0:
            events.append(dict(kind="drive", s=L / 1000 / DRIVE_V, path=pth.tolist(), text=why))
        pos = np.asarray(p1, float)
        if abs(((hd1 - hd + 180) % 360) - 180) > 1:
            events.append(dict(kind="turn", s=4.0, p=pos.tolist(), hd0=_last_heading(), hd=hd1, text=why))
        hd = hd1

    def _last_heading():
        for e in reversed(events):
            if e["kind"] == "drive":
                d = np.diff(np.asarray(e["path"])[-2:], axis=0)[0]
                return math.degrees(math.atan2(d[1], d[0]))
            if "hd" in e:
                return e["hd"]
        return hd

    for st, zones in ROUTE:
        sx, sy = FC.POU[st]
        front = _snap(G.pts, G.tree, (sx, -2380.0 if st == "atomizer" else -2330.0))
        h_front = _heading_at(ok0, ok90, F, front)
        drive_to(front, h_front, f"To the {st}'s vacuum station")
        events.append(dict(kind="pickup", s=PICK_S, p=pos.tolist(), hd=hd, station=st, detail=True,
                           text=f"The {st}'s station: the Al-family wand out of its holster; continuity on the "
                                f"station's fixture, 0.1 ohm a joint at most (vacuum SOP 1); vacuum on"))
        for z in zones:
            target = F.zones[z]["mask"] & cov & near[st] & ~cleaned & ~keep_out
            if z == "aisle":
                target &= aisle_of[st]
            if not target.any():
                continue
            ii, jj = np.nonzero(target)
            sel = (ii % 4 == 0) & (jj % 4 == 0)
            tpts = np.c_[F.xc[jj[sel]], F.yc[ii[sel]]]
            x0, x1, y0, y1 = F.zones[z]["rect"]
            cand = cen & near[st] & F.rect(x0 - ARM_R, x1 + ARM_R, y0 - ARM_R, y1 + ARM_R) & ~body_out
            ci, cj = np.nonzero(cand)
            s2 = (ci % 8 == 0) & (cj % 8 == 0)
            cpts = np.c_[F.xc[cj[s2]], F.yc[ci[s2]]]
            lists = cKDTree(tpts).query_ball_point(cpts, ARM_R - 20.0)
            uncov = np.ones(len(tpts), bool)
            chosen = []
            while uncov.mean() > 0.002:
                gains = np.array([uncov[l].sum() if l else 0 for l in lists])
                k = int(gains.argmax())
                if gains[k] < 4:
                    break
                chosen.append(cpts[k])
                uncov[lists[k]] = False
            # the order: nearest-neighbour from where the robot is
            order, left, cur = [], list(range(len(chosen))), pos.copy()
            while left:
                k = min(left, key=lambda i: float(np.hypot(*(chosen[i] - cur))))
                order.append(chosen[k])
                cur = chosen[k]
                left.remove(k)
            zcells = np.flatnonzero(target)
            zx, zy = F.X.flat[zcells], F.Y.flat[zcells]
            done_z = np.zeros(len(zcells), bool)
            n_z = 0
            for n_s, p in enumerate(order):
                d = np.hypot(zx - p[0], zy - p[1])
                mine = (d <= ARM_R) & ~done_z
                spilled = keep_out.flat[zcells] & mine
                mine_clean = mine & ~keep_out.flat[zcells]
                if not mine_clean.any():
                    continue
                done_z |= mine
                n_z += 1
                h1 = _heading_at(ok0, ok90, F, p)
                drive_to(np.asarray(p, float), h1, f"{ZONE_TITLES[z]}: work spot {n_z}")
                stud = _stud_for(F, p, h1)
                for s_ in studs:
                    if np.hypot(*(s_ - stud)) < STUD_SHARE:
                        stud = s_
                        break
                else:
                    studs.append(stud)
                first = not any(e["kind"] == "bond" for e in events)
                scoop_here = z == "sieving" and np.hypot(p[0] - LOOSE_AT[0], p[1] - LOOSE_AT[1]) <= ARM_R - 100 \
                    and not any(e["kind"] == "scoop" for e in events)
                spill_here = not spill_found and float(np.hypot(p[0] - SPILL_AT[0], p[1] - SPILL_AT[1])) <= CAM_R
                detail = first or scoop_here or spill_here
                if detail and events[-1]["kind"] in ("drive", "turn"):
                    events[-1]["detail"] = True
                base = dict(p=pos.tolist(), hd=hd, zone=z, station=st, stud=stud.tolist(), spot=n_z, detail=detail)
                events.append(dict(base, kind="bond", s=BOND_S / 2,
                                   text=f"{ZONE_TITLES[z]}, spot {n_z}: the bonding lead on the floor stud; the "
                                        "bond read before suction (NFPA 484 11.6.3.1: after each move)"))
                events.append(dict(base, kind="look", s=LOOK_S,
                                   text=f"{ZONE_TITLES[z]}, spot {n_z}: the camera looks over the floor in reach"))
                if spill_here:
                    spill_found = True
                    events.append(dict(base, kind="spill", s=30.0, spill=list(SPILL_AT),
                                       text="A visible layer in front of Shuttle 1's opening: a person's job (vacuum "
                                            "SOP 8). Unit 3 keeps 1 m away, leaves it, and messages the person and EHS"))
                if scoop_here:
                    events.append(dict(base, kind="scoop", s=SCOOP_S, at=list(LOOSE_AT),
                                       text="Loose powder by the door: scooped and brushed into the conductive bag "
                                            "first (conductive scoop, natural bristles: NFPA 484 11.5)"))
                cells = _lane_order(F, zcells[mine_clean], p)
                area = len(cells) * FC.CELL * FC.CELL / 1e6
                events.append(dict(base, kind="clean", s=area / STROKE, cells=cells, area_m2=area,
                                   text=f"{ZONE_TITLES[z]}, spot {n_z}: squeegee lanes, 14 in at 0.15 m/s "
                                        f"({area:.1f} m2 here)"))
                events.append(dict(base, kind="check", s=LOOK_S,
                                   text=f"{ZONE_TITLES[z]}, spot {n_z}: colour check: the floor's colour must "
                                        "show through (NFPA 484 11.4.1)"))
                events.append(dict(base, kind="unbond", s=BOND_S / 2, text=f"{ZONE_TITLES[z]}, spot {n_z}: unclip, "
                                                                           "move on"))
                spots_out.append(dict(zone=z, station=st, xy=[round(float(v)) for v in p], heading=h1,
                                      area_m2=round(area, 2), stud=[round(float(v)) for v in stud]))
                cleaned.flat[cells] = True
            tot = F.area_m2(F.zones[z]["mask"] & ~F.occ)
            zs = zone_stats.setdefault(z, dict(spots=0, cleaned_m2=0.0, area_m2=round(tot, 2)))
            zs["spots"] += n_z
        # back to the station: the wand's run-on, off, settle and holster
        drive_to(front, h_front, f"Back to the {st}'s station")
        events.append(dict(kind="ret", s=PICK_S, p=pos.tolist(), hd=hd, station=st, detail=True,
                           text=f"The {st}'s station: 20 s of run-on in clean air, off, 60 s to settle, the wand in "
                                "its holster (vacuum SOP 4.1-4.3)"))
    drive_to(start_pos, 90.0, "Back to the charger")
    events.append(dict(kind="dock", s=WHEEL_S, p=pos.tolist(), hd=90.0, detail=True,
                       text="On the charger, outside every zone; the wheels over the brush strip"))
    for z, zs in zone_stats.items():
        zs["cleaned_m2"] = round(F.area_m2(cleaned & F.zones[z]["mask"]), 2)
    t = 0.0
    for e in events:
        e["t0"], e["t1"] = t, t + e["s"]
        t += e["s"]
    by = {}
    for e in events:
        by[e["kind"]] = by.get(e["kind"], 0.0) + e["s"]
    robot_zones = np.zeros_like(F.free)
    for z, zd in F.zones.items():
        if z != "EOS":
            robot_zones |= zd["mask"]
    jt = FC.job_table(F, {"units_pou": R})["units_pou"]
    summary = dict(
        total_min=round(t / 60, 1), model_night_min=jt["night_min"], by_step_min={k: round(v / 60, 1) for k, v in by.items()},
        spots=len(spots_out), studs=len(studs), cleaned_m2=round(F.area_m2(cleaned), 1),
        robot_zones_m2=round(F.area_m2(robot_zones), 1),
        cleaned_share_of_robot_zones=round(F.area_m2(cleaned & robot_zones) / F.area_m2(robot_zones), 3),
        left_for_the_person_m2=round(F.area_m2(keep_out & robot_zones & cov), 2),
        drive_m=round(sum(float(np.linalg.norm(np.diff(np.asarray(e["path"]), axis=0), axis=1).sum())
                          for e in events if e["kind"] == "drive") / 1000, 1))
    return dict(F=F, R=R, events=events, studs=studs, spots=spots_out, zones=zone_stats, summary=summary,
                cleaned=cleaned, keep_out=keep_out)


BAY = FC.BAY


# ================================================================================================ the frames
def _video_table(events):
    """Each event's video seconds: its model seconds over SPEED_D, at least MIN_VS for its kind, where the steps are
    shown; over SPEED_R, at least a frame, elsewhere."""
    vt = 0.0
    for e in events:
        e["v0"] = vt
        if e.get("detail"):
            vt += max(e["s"] / SPEED_D, MIN_VS.get(e["kind"], 0.3))
        else:
            vt += max(e["s"] / SPEED_R, 1.0 / FPS)
        e["v1"] = vt
    return vt


def _pose_on_path(path, u):
    P = np.asarray(path)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    L = seg.sum()
    s = u * L
    k = int(np.searchsorted(np.cumsum(seg), s))
    k = min(k, len(seg) - 1)
    s0 = seg[:k].sum()
    f = 0.0 if seg[k] == 0 else (s - s0) / seg[k]
    p = P[k] + (P[k + 1] - P[k]) * f
    d = P[k + 1] - P[k]
    return p, math.degrees(math.atan2(d[1], d[0]))


def render(pl: dict):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon, Rectangle
    from PIL import Image
    import scene as S

    F, events = pl["F"], pl["events"]
    total_v = _video_table(events)
    intro, outro = 2.5, 6.0
    n_frames = int(round((intro + total_v + outro) * FPS))
    # ---- the static floor
    base = np.ones((F.ny, F.nx, 3))
    base[F.free] = FLOOR
    robot_zones = np.zeros_like(F.free)
    for z, zd in F.zones.items():
        if z != "EOS":
            robot_zones |= zd["mask"]
    base[robot_zones & F.free] = ZONE_DIRTY
    base[F.zones["EOS"]["mask"] & ~robot_zones] = PEOPLE
    base[F.occ] = MACHINE
    img = base.copy()
    fig = plt.figure(figsize=(W_PX / 100, H_PX / 100), dpi=100)
    fig.patch.set_facecolor(SURF)
    ax = fig.add_axes((0.005, 0.065, 0.735, 0.81))
    ext = (FC.X_LIM[0] / 1000, FC.X_LIM[1] / 1000, FC.Y_LIM[0] / 1000, FC.Y_LIM[1] / 1000)
    im = ax.imshow(img, origin="lower", extent=ext, interpolation="nearest")
    ax.set_xlim(ext[0], ext[1])
    ax.set_ylim(ext[2], ext[3])
    ax.set_aspect("equal")
    ax.axis("off")
    for z, zd in F.zones.items():
        x0, x1, y0, y1 = zd["rect"]
        ax.add_patch(Rectangle((x0 / 1000, y0 / 1000), (x1 - x0) / 1000, (y1 - y0) / 1000, fill=False, lw=0.9,
                               ec=INK2, ls=(0, (3, 2)) if z == "aisle" else "-"))
    ex0, ex1, ey0, ey1 = F.zones["EOS"]["rect"]
    ax.add_patch(Rectangle((ex0 / 1000, ey0 / 1000), (ex1 - ex0) / 1000, (ey1 - ey0) / 1000, fill=False, lw=0,
                           hatch="////", ec="#9a9a9a"))
    labels = {"repowder": "rePowder", "sieve_cell": "sieve", "vlm": "Shuttle 1", "vlm2": "Shuttle 2",
              "aconity": "MIDI", "glovebox": "glove-\nbox", "vacuum station": "vac", "eos_m400": "EOS M 400-4",
              "meltio_cell": "Meltio cell", "ded": "DED", "wire_edm": "wire EDM", "fumehood": "fume hood",
              "instron_floor": "Instron", "packaging": "pack.", "bay charger": "3"}
    for k, lbl in labels.items():
        if k in F.rects:
            x0, x1, y0, y1 = F.rects[k]
            ax.text((x0 + x1) / 2000, (y0 + y1) / 2000, lbl, ha="center", va="center", fontsize=6.5, color="white")
    ax.text(ex0 / 1000 + 0.15, ey1 / 1000 + 0.15, "EOS zone: people's (no MiR dock)", fontsize=7, color=INK2,
            va="bottom")
    ax.text(-10.1, -3.9, "aisle", fontsize=7.5, color=INK2, va="center")
    for nm, (sx, sy) in FC.POU.items():
        ax.add_patch(Circle((sx / 1000, sy / 1000), HOSE_R / 1000, fill=False, lw=0.6, ec=UNIT3, alpha=0.18,
                            ls=(0, (2, 3))))
        ax.plot([sx / 1000], [sy / 1000], marker="s", ms=6.5, color=INK, zorder=6)
        ax.text(sx / 1000 + (-0.25 if nm == "atomizer" else 0.25), sy / 1000 + 0.95, f"the {nm}'s\nvacuum station",
                fontsize=6.5, color=INK, ha="right" if nm == "atomizer" else "left", va="bottom", zorder=12,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    studs = np.asarray(pl["studs"]) / 1000
    ax.scatter(studs[:, 0], studs[:, 1], s=7, color=BRASS, zorder=5, lw=0)
    for x_ in (-1500.0, -300.0):                            # units 1 and 2 on their chargers (warehouse.CHARGERS)
        ax.add_patch(Rectangle((x_ / 1000 - 0.29, -5.818 - 0.40), 0.58, 0.80, color="#8e8f93", zorder=5))
    ax.text(-0.9, -5.15, "units 1-2", fontsize=6.5, color=INK2, ha="center")
    # ---- the moving parts
    body = Polygon(np.zeros((4, 2)), closed=True, fc=UNIT3, ec=INK, lw=0.6, zorder=8)
    nose = Polygon(np.zeros((3, 2)), closed=True, fc="white", ec="none", zorder=9)
    ax.add_patch(body)
    ax.add_patch(nose)
    reach_c = Circle((0, 0), ARM_R / 1000, fill=False, lw=0.8, ec=UNIT3, ls=(0, (2, 2)), zorder=7, visible=False)
    ax.add_patch(reach_c)
    hose, = ax.plot([], [], color="#202020", lw=1.1, zorder=7)
    arm, = ax.plot([], [], color=UNIT3, lw=1.6, zorder=9, solid_capstyle="round")
    tool, = ax.plot([], [], marker="o", ms=4.0, color=INK, zorder=10)
    lead, = ax.plot([], [], color=LEAD, lw=1.4, zorder=9)
    stud_on, = ax.plot([], [], marker="o", ms=5.5, color=BRASS, mec=INK, mew=0.6, zorder=10)
    trail, = ax.plot([], [], color=UNIT3, lw=0.7, alpha=0.35, zorder=4)
    cam = Polygon(np.zeros((3, 2)), closed=True, fc=UNIT3, alpha=0.18, ec="none", zorder=7, visible=False)
    ax.add_patch(cam)
    spill_c = Circle((SPILL_AT[0] / 1000, SPILL_AT[1] / 1000), KEEP_OUT / 1000, fc=SPILL, alpha=0.10, ec=SPILL,
                     lw=1.0, ls=(0, (3, 2)), zorder=6, visible=False)
    ax.add_patch(spill_c)
    spill_m, = ax.plot([SPILL_AT[0] / 1000], [SPILL_AT[1] / 1000], marker="X", ms=8, color=SPILL, zorder=11,
                       visible=False)
    spill_t = ax.text(SPILL_AT[0] / 1000, SPILL_AT[1] / 1000 - 1.25, "visible spill: the person's", color=SPILL,
                      fontsize=7.5, ha="center", va="top", zorder=11, visible=False)
    loose_m, = ax.plot([LOOSE_AT[0] / 1000], [LOOSE_AT[1] / 1000], marker="o", ms=6, color="#8a6d3b", zorder=11,
                       visible=False)
    # ---- the text
    fig.text(0.012, 0.955, "Unit 3's nightly pass: every powder zone a robot serves, and the aisle", fontsize=15,
             color=INK, weight="bold", va="center")
    cap = fig.text(0.012, 0.905, "", fontsize=10.5, color=INK2, va="center")
    px = 0.755
    clock = fig.text(px, 0.80, "", fontsize=26, color=INK, weight="bold", family="DejaVu Sans Mono")
    clock2 = fig.text(px, 0.765, "", fontsize=9, color=INK2)
    fig.text(px, 0.715, "Zones", fontsize=10.5, color=INK, weight="bold")
    rows = [("glovebox", "atomizer"), ("atomizer", "atomizer"), ("sieving", "atomizer"), ("opening 1", "atomizer"),
            ("aisle", "atomizer"), ("opening 2", "printer line"), ("midi", "printer line"), ("DED", "printer line"),
            ("aisle", "printer line"), ("EOS", None)]
    row_area = {}
    for z, st in rows:
        if z == "EOS":
            continue
        a = sum(len(e["cells"]) for e in events if e["kind"] == "clean" and e["zone"] == z and e["station"] == st)
        row_area[(z, st)] = a
    row_txt, row_bar = [], []
    y = 0.675
    for z, st in rows:
        name = ZONE_TITLES[z] + ({"atomizer": " (west half)", "printer line": " (east half)"}.get(st, "")
                                 if z == "aisle" else "")
        t_ = fig.text(px, y, name, fontsize=8.2, color=INK2, va="center")
        bar_bg = fig.add_axes((px + 0.142, y - 0.008, 0.052, 0.016))
        bar_bg.set_xlim(0, 1)
        bar_bg.set_ylim(0, 1)
        bar_bg.axis("off")
        bar_bg.add_patch(Rectangle((0, 0), 1, 1, color="#e4e3df"))
        b = Rectangle((0, 0), 0, 1, color=UNIT3 if z != "EOS" else "#9a9a9a")
        bar_bg.add_patch(b)
        tt = fig.text(px + 0.199, y, "", fontsize=7.6, color=INK2, va="center")
        row_txt.append((t_, tt))
        row_bar.append(b)
        y -= 0.037
    tally = fig.text(px, 0.30, "", fontsize=8.6, color=INK, va="top", linespacing=1.45)
    msg = fig.text(px, 0.165, "", fontsize=8.0, color=SPILL, va="top", linespacing=1.35)
    fig.text(0.012, 0.008, "Floor: purple, cleaned tonight; sand, a powder zone not yet; grey hatched, the EOS's zone "
             "(people's); dark grey, machines.\nBrass dots: ground studs at the work spots (ours). Faint dashed "
             "circles: each station's hose, 7.0 m. Unit 3: the purple MiR250, white arrow forward; its arm's 1.3 m "
             "reach dashed.", fontsize=7.4, color=INK2, va="bottom", linespacing=1.3)

    # cleaning progress bookkeeping
    clean_ev = [e for e in events if e["kind"] == "clean"]
    done_cells = np.zeros(F.free.size, bool)
    revealed = {id(e): 0 for e in clean_ev}
    trail_pts: list = []
    drive_ev = [e for e in events if e["kind"] == "drive"]
    done_drives = 0
    cur_trail = None
    flat_img = img.reshape(-1, 3)
    flat_base = base.reshape(-1, 3)

    def robot_poly(p, hd):
        a = math.radians(hd)
        ux, uy = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
        c = np.asarray(p) / 1000
        L, W = L_MM / 2000, W_MM / 2000
        corners = [c + ux * L + uy * W, c - ux * L + uy * W, c - ux * L - uy * W, c + ux * L - uy * W]
        n = [c + ux * L * 0.95, c + ux * L * 0.45 + uy * W * 0.55, c + ux * L * 0.45 - uy * W * 0.55]
        return np.array(corners), np.array(n)

    def hhmm(sec):
        m = 60 + sec / 60.0
        return f"0{int(m // 60)}:{int(m % 60):02d}"

    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                             f"{W_PX}x{H_PX}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "20", "-pix_fmt", "yuv420p", "-threads", "2", "-movflags", "+faststart",
                             str(OUT / "mp4" / f"{NAME}.mp4")], stdin=subprocess.PIPE)
    gif_frames = []
    still = None
    spill_seen = False
    msgs = []
    ev_i = 0
    sc_i = next((i for i, x in enumerate(events) if x["kind"] == "scoop"), None)
    loose_win = None if sc_i is None else (events[sc_i - 1]["v0"], events[sc_i]["v0"])
    for fi in range(n_frames):
        vt = fi / FPS - intro
        if vt < 0:
            e, u = events[0], 0.0
        elif vt >= total_v:
            e, u = events[-1], 1.0
        else:
            while ev_i < len(events) - 1 and events[ev_i]["v1"] <= vt:
                ev_i += 1
            e = events[ev_i]
            u = (vt - e["v0"]) / (e["v1"] - e["v0"])
        # finish every clean event before this one (frames can step over short ones)
        for ce in clean_ev:
            if ce["v1"] <= max(vt, -1) and revealed[id(ce)] < len(ce["cells"]):
                c = ce["cells"][revealed[id(ce)]:]
                flat_img[c] = CLEAN
                done_cells[c] = True
                revealed[id(ce)] = len(ce["cells"])
        tsec = e["t0"] + (e["t1"] - e["t0"]) * u if vt >= 0 else 0.0
        kind = e["kind"]
        if kind == "drive":
            p, hd = _pose_on_path(e["path"], u)
            P_ = np.asarray(e["path"])
            seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P_, axis=0), axis=1))]
            cur_trail = np.vstack([P_[seg <= u * seg[-1]], p[None]]) / 1000
        elif kind == "turn":
            p = np.asarray(e["p"])
            d = ((e["hd"] - e["hd0"] + 180) % 360) - 180
            hd = e["hd0"] + d * u
        else:
            p, hd = np.asarray(e["p"]), e.get("hd", 90.0)
        corners, n = robot_poly(p, hd)
        body.set_xy(corners)
        nose.set_xy(n)
        working = kind in ("bond", "look", "spill", "scoop", "clean", "check", "unbond")
        reach_c.set_visible(working)
        reach_c.center = (p[0] / 1000, p[1] / 1000)
        # the hose: from the station to the robot, while the wand is out
        st_now = None
        for e2 in events[:ev_i + 1] if vt >= 0 else []:
            if e2["kind"] == "pickup":
                st_now = e2["station"]
            if e2["kind"] == "ret" and (e2 is not e or u >= 0.85):
                st_now = None
        tip = None
        if kind == "clean":
            k = int(round(u * len(e["cells"])))
            if k > revealed[id(e)]:
                c = e["cells"][revealed[id(e)]:k]
                flat_img[c] = CLEAN
                done_cells[c] = True
                revealed[id(e)] = k
            j = e["cells"][max(0, min(k, len(e["cells"]) - 1))]
            tip = np.array([F.X.flat[j], F.Y.flat[j]]) / 1000
        elif kind == "scoop":
            tip = np.asarray(e["at"]) / 1000 + 0.12 * np.array([math.cos(u * 18), math.sin(u * 18)])
        elif kind in ("look", "check", "spill"):
            tip = p / 1000 + 0.55 * np.array([math.cos(math.radians(hd + 90)), math.sin(math.radians(hd + 90))])
        if st_now is not None:
            sx, sy = FC.POU[st_now]
            pts = [(sx / 1000, sy / 1000), (p[0] / 1000, p[1] / 1000)]
            if tip is not None and kind in ("clean", "scoop"):
                pts.append(tuple(tip))
            hose.set_data([q[0] for q in pts], [q[1] for q in pts])
        else:
            hose.set_data([], [])
        if tip is not None:
            arm.set_data([p[0] / 1000, tip[0]], [p[1] / 1000, tip[1]])
            tool.set_data([tip[0]], [tip[1]])
        else:
            arm.set_data([], [])
            tool.set_data([], [])
        if kind in ("look", "check", "spill"):
            a0 = math.radians(hd + 90) if kind != "spill" else math.atan2(SPILL_AT[1] - p[1], SPILL_AT[0] - p[0])
            sweep = (u - 0.5) * 1.6 if kind != "spill" else 0.0
            a0 += sweep
            c0 = tip if tip is not None else p / 1000
            fan = [c0, c0 + 1.5 * np.array([math.cos(a0 - 0.45), math.sin(a0 - 0.45)]),
                   c0 + 1.5 * np.array([math.cos(a0 + 0.45), math.sin(a0 + 0.45)])]
            cam.set_xy(np.array(fan))
            cam.set_visible(True)
        else:
            cam.set_visible(False)
        if kind in ("bond", "look", "spill", "scoop", "clean", "check") or (kind == "unbond" and u < 0.6):
            sd = np.asarray(e["stud"]) / 1000
            lead.set_data([p[0] / 1000, sd[0]], [p[1] / 1000, sd[1]])
            stud_on.set_data([sd[0]], [sd[1]])
        else:
            lead.set_data([], [])
            stud_on.set_data([], [])
        if kind == "spill" and not spill_seen and u > 0.2:
            spill_seen = True
            msgs.append(f"{hhmm(tsec)}  Message to the person and EHS: a visible layer at Shuttle 1's opening. "
                        "Unit 3 keeps 1 m away; the patch waits for the morning.")
        spill_c.set_visible(spill_seen)
        spill_m.set_visible(spill_seen)
        spill_t.set_visible(spill_seen)
        loose_vis = loose_win is not None and loose_win[0] <= vt < loose_win[1]
        if kind == "scoop":
            loose_m.set_visible(u < 0.8)
            loose_m.set_markersize(6 * (1 - u))
        else:
            loose_m.set_visible(bool(loose_vis))
            loose_m.set_markersize(6)
        while done_drives < len(drive_ev) and drive_ev[done_drives]["v1"] <= max(vt, -1):
            trail_pts.append(np.asarray(drive_ev[done_drives]["path"]) / 1000)
            trail_pts.append(np.array([[np.nan, np.nan]]))
            done_drives += 1
        parts = trail_pts[-24:] + ([cur_trail] if kind == "drive" else [])
        if parts:
            tp = np.vstack(parts)
            trail.set_data(tp[:, 0], tp[:, 1])
        im.set_data(img)
        # text
        cap.set_text("Lights out, nobody in (01:00, assumed). Unit 3 (purple) parks, bonds to a floor stud and works "
                     "the floor in its arm's reach; time-lapse" if vt < 0 else e["text"])
        clock.set_text(hhmm(tsec) if vt >= 0 else "01:00")
        clock2.set_text("model time; time-lapse " + (f"{SPEED_D:.0f}x, short steps held" if e.get("detail") or vt < 0
                                                     else f"{SPEED_R:.0f}x"))
        for (z, st), (t_, tt), b in zip(rows, row_txt, row_bar):
            if z == "EOS":
                b.set_width(1.0)
                tt.set_text("people's")
                continue
            tot = row_area[(z, st)]
            got = sum(revealed[id(ce)] for ce in clean_ev if ce["zone"] == z and ce["station"] == st)
            b.set_width(got / tot if tot else 0)
            n_sp = len([ce for ce in clean_ev if ce["zone"] == z and ce["station"] == st])
            tt.set_text(f"{n_sp} spot{'s' if n_sp != 1 else ''}")
            t_.set_color(INK if (vt >= 0 and e.get("zone") == z and e.get("station") == st) else INK2)
        cleaned_m2 = done_cells.sum() * FC.CELL * FC.CELL / 1e6
        n_sp_done = sum(1 for x in events[:ev_i + 1] if x["kind"] == "bond") if vt >= 0 else 0
        tally.set_text(f"Cleaned tonight: {cleaned_m2:5.1f} of {pl['summary']['robot_zones_m2']:.1f} m2\n"
                       f"Work spots: {n_sp_done} of {pl['summary']['spots']}, each bonded and read\n"
                       f"Ground studs (ours): {pl['summary']['studs']}\n"
                       f"Wand: {'Al family, the ' + st_now + chr(39) + 's station' if st_now else 'in its holster'}")
        msg.set_text("\n".join(_wrap(m_, 50) for m_ in msgs[-1:]))
        if fi >= n_frames - int(outro * FPS):
            s_ = pl["summary"]
            cap.set_text(f"{hhmm(events[-1]['t1'])}: done in {s_['total_min']:.0f} min ({s_['model_night_min']:.0f} "
                         f"in floor_cleaning.py's model, without the bonding at each spot and the second station)")
            msg.set_text(_wrap("08:00, the person: the spill at Shuttle 1's opening (restrict access, scoop into a "
                               "conductive bag, the residue with the 118EXP); the liners checked and emptied at the "
                               "day shift's end; the EOS's floor.", 50))
            msg.set_color(INK)
        fig.canvas.draw()
        frame = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        proc.stdin.write(np.ascontiguousarray(frame).tobytes())
        if math.floor(math.ceil(fi * GIF_FPS / FPS) * FPS / GIF_FPS) == fi:
            gif_frames.append(Image.fromarray(frame).resize((800, 450), Image.LANCZOS))
        if fi == n_frames - 1:
            still = Image.fromarray(frame.copy())
    proc.stdin.close()
    proc.wait()
    plt.close(fig)
    still.save(OUT / f"{NAME}_still.png", optimize=True)
    S.write_gif(gif_frames, OUT / f"{NAME}.gif")
    return dict(frames=n_frames, seconds=round(n_frames / FPS, 1), gif_frames=len(gif_frames),
                gif_mb=round((OUT / f"{NAME}.gif").stat().st_size / 1e6, 2),
                mp4_mb=round((OUT / "mp4" / f"{NAME}.mp4").stat().st_size / 1e6, 2))


def _wrap(s, n):
    import textwrap
    return "\n".join(textwrap.wrap(s, n))


def write_json(pl, info=None):
    s = pl["summary"]
    ev = [dict(kind=e["kind"], t0_min=round(e["t0"] / 60, 2), t1_min=round(e["t1"] / 60, 2),
               **({"zone": e["zone"]} if "zone" in e else {}), **({"area_m2": round(e["area_m2"], 2)}
                                                                  if "area_m2" in e else {}), text=e["text"])
          for e in pl["events"]]
    out = dict(what="Unit 3's nightly pass across the lab (floor_pass.py): the route, its work spots and studs, and "
                    "its time step by step, on floor_cleaning.py's floor, reach and pass model. Ours, a model.",
               assumed=dict(bond_s_a_spot=BOND_S, look_s=LOOK_S, check_s=LOOK_S, pick_up_s=PICK_S, return_s=PICK_S,
                            scoop_s=SCOOP_S, wheel_strip_s=WHEEL_S, keep_out_mm=KEEP_OUT, stud_share_mm=STUD_SHARE,
                            loose_powder_at=LOOSE_AT, visible_spill_at=SPILL_AT,
                            route=[dict(station=s_, zones=z_) for s_, z_ in ROUTE],
                            note="the two powder events are illustrations: the model has no spill rate"),
               summary=s, zones=pl["zones"], spots=pl["spots"], studs=[[round(float(v)) for v in q] for q in pl["studs"]],
               events=ev)
    if info:
        out["render"] = info
    (OUT / f"{NAME}.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    pl = plan()
    print(json.dumps(pl["summary"], indent=1), flush=True)
    print(json.dumps(pl["zones"], indent=1), flush=True)
    if len(sys.argv) > 1 and sys.argv[1] == "plan":
        write_json(pl)
    else:
        (OUT / "mp4").mkdir(parents=True, exist_ok=True)
        info = render(pl)
        write_json(pl, info)
        print(info, flush=True)
