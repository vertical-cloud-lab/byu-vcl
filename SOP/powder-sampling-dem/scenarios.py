"""Fill a collection jar with powder labelled by when it was made, then sample it.

    python scenarios.py fill          # the shared starting bed (run this first)
    python scenarios.py open_tube     # glass tube pushed down open, emptied along a line
    python scenarios.py piston        # piston corer, extruded along a line
    python scenarios.py thief         # three-port sampling thief
    python scenarios.py spoon         # spoonula, top, middle and bottom scoops
    python scenarios.py pour          # jar poured out along a line, sampled along it

Raw trajectories go to $DEM_OUT (default /tmp/dem-out); the per-sample tallies go to
results/<scenario>.json next to this file.
"""

import json
import math
import os
import sys
import time

import numpy as np

from dem import ASLEEP, DEAD, FREE, Sim, Tool, revolve_rect, rot_x, rot_y

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("DEM_OUT", "/tmp/dem-out")
RES = os.path.join(HERE, "results")

mm = 1e-3
R_JAR = 12 * mm  # inner radius; "a few cm across"
T_WALL = 1 * mm
H_JAR = 26 * mm
N_RUN = 6000
N_SWEEP = 600
R_MIN, R_MAX = 0.425 * mm, 0.575 * mm
GROUPS = ["bottom third", "middle third", "top third", "sweepings"]
FPS_SIM = 40  # recorded frames per simulated second


def jar_tools(pose=None):
    pose = pose or (lambda t: (np.zeros(3), np.eye(3), True))
    wall = Tool("jar wall", "revolve", revolve_rect(R_JAR, R_JAR + T_WALL, -T_WALL, H_JAR), mu=0.3,
                pose=pose, color=(0.80, 0.84, 0.88), alpha=0.35)
    floor = Tool("jar floor", "revolve", revolve_rect(0.0, R_JAR + T_WALL, -T_WALL, 0.0), mu=0.3,
                 pose=pose, color=(0.80, 0.84, 0.88), alpha=0.35)
    return [wall, floor]


class Recorder:
    def __init__(self, sim, every_s=1.0 / FPS_SIM):
        self.sim = sim
        self.every = every_s
        self.frames = []
        self.next_t = 0.0
        self.captions = []

    def maybe(self, caption=""):
        if self.sim.t + 1e-12 >= self.next_t:
            self.snap(caption)
            self.next_t += self.every

    def snap(self, caption=""):
        s = self.sim
        self.frames.append(dict(t=s.t, x=s.x.astype(np.float32).copy(), mode=s.mode.copy(),
                                poses=s.tool_poses(), caption=caption))

    def save(self, name, extra=None):
        os.makedirs(OUT, exist_ok=True)
        n = max(len(f["x"]) for f in self.frames)
        X = np.full((len(self.frames), n, 3), np.nan, np.float32)
        M = np.full((len(self.frames), n), DEAD, np.int8)
        for k, f in enumerate(self.frames):
            X[k, : len(f["x"])] = f["x"]
            M[k, : len(f["mode"])] = f["mode"]
        P = len(self.sim.tools)
        TP = np.zeros((len(self.frames), P, 3))
        TR = np.zeros((len(self.frames), P, 3, 3))
        TO = np.zeros((len(self.frames), P), bool)
        for k, f in enumerate(self.frames):
            for g, (p, R, on) in enumerate(f["poses"]):
                TP[k, g], TR[k, g], TO[k, g] = p, R, on
        tools = [dict(name=t.name, kind=t.kind, poly=np.asarray(t.poly).tolist(), half=np.asarray(t.half).tolist(),
                      color=t.color, alpha=t.alpha, cut=t.cut) for t in self.sim.tools]
        np.savez_compressed(os.path.join(OUT, f"{name}.npz"), X=X, M=M, TP=TP, TR=TR, TO=TO,
                            t=np.array([f["t"] for f in self.frames]),
                            caption=np.array([f["caption"] for f in self.frames]),
                            rad=self.sim.rad.astype(np.float32), group=self.sim.group, label=self.sim.label,
                            tools=json.dumps(tools), extra=json.dumps(extra or {}))


def run_phase(sim, rec, duration, caption, hook=None, chunk=10):
    steps_per_frame = max(1, int(round(rec.every / sim.dt)))
    total = int(round(duration / sim.dt))
    done = 0
    while done < total:
        k = min(steps_per_frame, total - done)
        sim.advance(k, chunk=chunk, hook=hook)
        done += k
        rec.maybe(caption)


# ---------------------------------------------------------------------------
# Fill


def fill():
    rng = np.random.default_rng(264)
    sim = Sim()
    sim.tools = jar_tools()
    rec = Recorder(sim)
    batch_dt = 2e-3
    rate = N_RUN / 1.2
    inserted = 0

    def insert(nb, r_out, group_fn, label_fn):
        nonlocal inserted
        x = sim.x
        near = x[(sim.mode != DEAD) & (np.hypot(x[:, 0], x[:, 1]) < r_out + 2 * mm)] if len(x) else np.zeros((0, 3))
        # the pile surface, ignoring particles that are still falling
        resting = near[np.linalg.norm(sim.v[(sim.mode != DEAD) & (np.hypot(x[:, 0], x[:, 1]) < r_out + 2 * mm)],
                                      axis=1) < 0.06] if len(x) else near
        top = resting[:, 2].max() if len(resting) else 0.0
        z0 = top + 1.6 * mm
        pts, rs = [], []
        tries = 0
        while len(pts) < nb and tries < 400:
            tries += 1
            rr = r_out * math.sqrt(rng.random())
            th = 2 * math.pi * rng.random()
            p = np.array([rr * math.cos(th), rr * math.sin(th), z0 + rng.random() * 1.2 * mm])
            rad = rng.uniform(R_MIN, R_MAX)
            ok = all(np.linalg.norm(p - q) > rad + rq + 0.05 * mm for q, rq in zip(pts, rs))
            if ok and len(near):
                ok = np.all(np.linalg.norm(near - p, axis=1) > rad + R_MAX + 0.05 * mm)
            if ok:
                pts.append(p)
                rs.append(rad)
        k = len(pts)
        if k:
            v = np.zeros((k, 3))
            v[:, 2] = -0.15
            sim.add(np.array(pts), np.array(rs), group_fn(inserted, k), label_fn(inserted, k), v=v)
            inserted += k
        return k

    t0 = time.time()
    n_run_done = 0
    while n_run_done < N_RUN:
        want = min(int(round(rate * batch_dt)), N_RUN - n_run_done)
        k = insert(want, 3.5 * mm,
                   lambda i0, k: np.minimum((np.arange(i0, i0 + k) * 3) // N_RUN, 2),
                   lambda i0, k: (np.arange(i0, i0 + k) + 0.5) / N_RUN)
        n_run_done += k
        run_phase(sim, rec, batch_dt, "powder falls through the cone: first made at the bottom")
    n_sw = 0
    while n_sw < N_SWEEP:
        want = min(40, N_SWEEP - n_sw)
        k = insert(want, 7 * mm, lambda i0, k: np.full(k, 3), lambda i0, k: rng.random(k))
        n_sw += k
        run_phase(sim, rec, batch_dt, "sweepings from the plate, cone and bowl go in last")
    run_phase(sim, rec, 0.25, "settled")
    print(f"fill: {sim.n} particles, t={sim.t:.3f} s, wall {time.time() - t0:.0f} s", flush=True)
    rec.save("fill")
    np.savez_compressed(os.path.join(OUT, "bed.npz"), x=sim.x, v=sim.v, w=sim.w, rad=sim.rad, mode=sim.mode,
                        group=sim.group, label=sim.label, hj=sim.hj, hxi=sim.hxi, wp=sim.wp, wxi=sim.wxi)


def load_bed(sim):
    b = np.load(os.path.join(OUT, "bed.npz"))
    sim.x, sim.v, sim.w = b["x"].copy(), b["v"].copy() * 0, b["w"].copy() * 0
    sim.rad, sim.mode = b["rad"].copy(), b["mode"].copy()
    sim.group, sim.label = b["group"].copy(), b["label"].copy()
    sim.extf = np.zeros_like(sim.x)
    sim.hj, sim.hxi, sim.wp, sim.wxi = b["hj"].copy(), b["hxi"].copy(), b["wp"].copy(), b["wxi"].copy()


def bed_top_at_axis(sim, r=2.5 * mm):
    x = sim.x
    sel = (sim.mode != DEAD) & (np.hypot(x[:, 0], x[:, 1]) < r)
    return float(np.percentile(x[sel, 2] + sim.rad[sel], 98))


def tally(sim, idx):
    idx = np.asarray(idx, int)
    g = sim.group[idx]
    lab = sim.label[idx]
    counts = [int((g == k).sum()) for k in range(4)]
    return dict(n=int(len(idx)), counts=counts, mean_label=float(lab.mean()) if len(idx) else float("nan"))


def save_result(name, samples, notes, extra=None):
    os.makedirs(RES, exist_ok=True)
    out = dict(scenario=name, groups=GROUPS, samples=samples, notes=notes)
    if extra:
        out.update(extra)
    with open(os.path.join(RES, f"{name}.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=1))


# ---------------------------------------------------------------------------
# Smooth motion helpers


def ramp(t, t0, t1):
    """0 before t0, 1 after t1, smooth in between."""
    if t <= t0:
        return 0.0
    if t >= t1:
        return 1.0
    s = (t - t0) / (t1 - t0)
    return s * s * (3 - 2 * s)


def path(t, keys):
    """Piecewise smooth interpolation through [(t, value), ...]."""
    if t <= keys[0][0]:
        return np.asarray(keys[0][1], float)
    for (ta, a), (tb, b) in zip(keys[:-1], keys[1:]):
        if t <= tb:
            s = ramp(t, ta, tb)
            return (1 - s) * np.asarray(a, float) + s * np.asarray(b, float)
    return np.asarray(keys[-1][1], float)


# ---------------------------------------------------------------------------
# Tube corers (open tube and piston corer)

# ---------------------------------------------------------------------------
# Tube corers (open tube and piston corer)

R_BORE = 3.5 * mm
T_TUBE = 0.7 * mm
L_TUBE = 24 * mm
X_TRAY = 30 * mm  # where the core is laid out


def tray_tool():
    return Tool("tray", "box", half=[26 * mm, 8 * mm, 0.5 * mm], mu=0.5,
                pose=lambda t: (np.array([X_TRAY + 18 * mm, 0, -0.5 * mm]), np.eye(3), True),
                color=(0.55, 0.57, 0.60), alpha=1.0, cut=True)


def corer(piston_mode):
    sim = Sim()
    load_bed(sim)
    top = bed_top_at_axis(sim)
    z_clear = H_JAR + 1.5 * mm
    v_in = 30 * mm  # m/s
    t_in0 = 0.12
    z_surf = top + 1 * mm
    t_air = t_in0 + (z_clear - z_surf) / (80 * mm)  # quicker through the air
    t_in1 = t_air + (z_surf - 0.15 * mm) / v_in
    t_lift0 = t_in1 + 0.12
    t_lift1 = t_lift0 + 0.5
    t_move1 = t_lift1 + 0.4
    t_down1 = t_move1 + 0.3
    tip = [(0.0, (0, 0, z_clear)), (t_in0, (0, 0, z_clear)), (t_air, (0, 0, z_surf)), (t_in1, (0, 0, 0.15 * mm)),
           (t_lift0, (0, 0, 0.15 * mm)), (t_lift1, (0, 0, z_clear + 1 * mm)),
           (t_move1, (X_TRAY, 0, z_clear + 1 * mm)), (t_down1, (X_TRAY, 0, 3.0 * mm))]
    state = dict(t_ext0=None, t_ext1=None, piston_rel=None)
    v_ext = 8 * mm  # extrusion speed
    v_lay = 18 * mm  # tube speed along the tray while extruding

    def tip_pos(t):
        if state["t_ext0"] is None or t <= state["t_ext0"]:
            return path(t, tip)
        p = path(state["t_ext0"], tip).copy()
        p[0] += v_lay * (min(t, state["t_ext1"] + 0.3) - state["t_ext0"])
        return p

    def tube_pose(t):
        return tip_pos(t), np.eye(3), True

    def cap_pose(t):
        on = t_lift0 - 0.05 <= t and (state["t_ext0"] is None or t < state["t_ext0"])
        return tip_pos(t) + np.array([0, 0, -0.4 * mm]), np.eye(3), on

    surface = top + 0.3 * mm

    def piston_pose(t):
        # Piston corer: the piston face starts flush with the tube's end, stops at the powder
        # surface and is held there while the tube goes on down; after that it rides with the
        # tube. Open tube: no piston until the core is pushed out on the tray, standing in
        # for a thumb or stopper that could let the core out a little at a time (best case).
        if piston_mode:
            if t <= t_in1:
                z = max(tip_pos(t)[2], surface)
                return np.array([0, 0, z]), np.eye(3), True
            if state["piston_rel"] is None:
                state["piston_rel"] = surface - tip_pos(t_in1)[2]
            rel = state["piston_rel"]
        else:
            if state["piston_rel"] is None:
                return tip_pos(t) + np.array([0, 0, 30 * mm]), np.eye(3), False
            rel = state["piston_rel"]
        if state["t_ext0"] is not None and t > state["t_ext0"]:
            rel = rel - v_ext * (min(t, state["t_ext1"]) - state["t_ext0"])
        return tip_pos(t) + np.array([0, 0, rel]), np.eye(3), True

    jar = jar_tools()
    tube = Tool("tube", "revolve", revolve_rect(R_BORE, R_BORE + T_TUBE, 0.0, L_TUBE), mu=0.3,
                pose=tube_pose, color=(0.62, 0.86, 0.93), alpha=0.35)
    cap = Tool("cap", "revolve", revolve_rect(0.0, R_BORE + T_TUBE, -0.5 * mm, 0.0), mu=0.3, pose=cap_pose,
               color=(0.35, 0.35, 0.38), alpha=1.0)
    piston = Tool("piston", "revolve", revolve_rect(0.0, R_BORE - 0.12 * mm, 0.0, 18 * mm), mu=0.2,
                  pose=piston_pose, color=(0.45, 0.47, 0.50), alpha=1.0)
    sim.tools = jar + [tray_tool(), tube, cap, piston]
    rec = Recorder(sim)

    # Air trapped between the piston and the core: as the tube slides down, the gap would
    # grow, so the pressure drops and holds the core up (suction).
    P0 = 101325.0
    A = math.pi * R_BORE ** 2
    pore_len = 0.4 * top  # air in the core's pores, as an equivalent length of open tube

    def in_bore(s):
        p = tip_pos(s.t)
        rel = s.x - p
        return (s.mode == FREE) & (np.hypot(rel[:, 0], rel[:, 1]) < R_BORE) & (rel[:, 2] > -0.5 * mm) & \
            (rel[:, 2] < L_TUBE)

    def suction(s):
        s.extf[:] = 0.0
        if not piston_mode or s.t < t_in0 or (state["t_ext0"] is not None and s.t >= state["t_ext0"]):
            return
        pp, _, _ = piston_pose(s.t)
        if pp[2] - tip_pos(s.t)[2] < 1 * mm:
            return
        sel = in_bore(s)
        if sel.sum() < 10:
            return
        ztop = np.sort(s.x[sel, 2] + s.rad[sel])[-12:].mean()
        gap = pp[2] - ztop
        if gap <= 0:
            return
        dp = P0 * gap / (pore_len + gap)
        f = dp * A
        m = s.mass[sel].sum()
        f = min(f, 20.0 * m * s.g)
        s.extf[sel, 2] = f / sel.sum()

    run_phase(sim, rec, t_in0, "tube above the jar")
    txt = ("push the tube down; the piston stops at the surface" if piston_mode
           else "push the open tube straight down to the floor")
    run_phase(sim, rec, t_in1 - t_in0, txt, hook=suction)
    run_phase(sim, rec, t_lift0 - t_in1, "at the floor", hook=suction)
    sel = in_bore(sim)
    core_idx = np.where(sel)[0]
    core_top = float(np.sort(sim.x[sel, 2] + sim.rad[sel])[-12:].mean())
    recovery = core_top / top
    print(f"core: {len(core_idx)} particles, top {core_top / mm:.2f} mm vs bed {top / mm:.2f} mm "
          f"-> recovery {recovery:.2f}", flush=True)
    lift_caption = ("lift out (suction holds the core)" if piston_mode
                    else "thumb on top, lift out (assume the core stays in)")
    run_phase(sim, rec, t_lift1 - t_lift0, lift_caption, hook=suction)
    # the rest of the bed won't be touched again: let it sleep so the run is quicker
    out = np.ones(sim.n, bool)
    out[core_idx] = False
    still = out & (sim.mode == FREE) & (np.hypot(sim.x[:, 0], sim.x[:, 1]) < R_JAR + 1 * mm) & (sim.x[:, 2] < H_JAR)
    sim.v[still] = 0
    sim.w[still] = 0
    sim.mode[still] = ASLEEP
    run_phase(sim, rec, t_move1 - t_lift1, "move over the grounded tray", hook=suction)
    run_phase(sim, rec, t_down1 - t_move1, "lower to just above the tray", hook=suction)
    sel = in_bore(sim)
    tip_z = tip_pos(sim.t)[2]
    core_top = float(np.sort(sim.x[sel, 2] + sim.rad[sel])[-12:].mean())
    if not piston_mode:
        state["piston_rel"] = core_top - tip_z + 0.4 * mm
    else:
        pp, _, _ = piston_pose(sim.t)
        state["piston_rel"] = pp[2] - tip_z
    state["t_ext0"] = sim.t
    ext_len = state["piston_rel"] + 0.3 * mm
    state["t_ext1"] = sim.t + ext_len / v_ext
    run_phase(sim, rec, state["t_ext1"] - sim.t + 0.3, "push the core out while moving along the tray")
    run_phase(sim, rec, 0.3, "laid out: the bottom of the jar comes out first")
    on_tray = np.where((sim.mode == FREE) & (sim.x[:, 0] > X_TRAY - 8 * mm) & (sim.x[:, 2] < 8 * mm))[0]
    xs = sim.x[on_tray, 0]
    order = on_tray[np.argsort(xs)]
    thirds = np.array_split(order, 3)
    names = ["first third laid (bottom)", "second third (middle)", "last third laid (top)"]
    samples = [dict(name=nm, **tally(sim, th)) for nm, th in zip(names, thirds)]
    name = "piston" if piston_mode else "open_tube"
    extra = dict(core_particles=int(len(core_idx)), core_recovery=recovery, bed_depth_axis_mm=top / mm,
                 core_top_mm=core_top / mm, line_x_mm=[float(xs.min() / mm), float(xs.max() / mm)],
                 core_tally=tally(sim, core_idx))
    rec.save(name, extra=dict(samples=[th.tolist() for th in thirds], core=core_idx.tolist(), **extra))
    notes = ("Core laid out along the tray, then split into thirds by particle count along the line. "
             "Recovery = core height in the tube at the floor / bed depth at the axis.")
    save_result(name, samples, notes, extra=extra)


# ---------------------------------------------------------------------------
# Thief

R_THIEF = 2.5 * mm
R_THIEF_CORE = 1.2 * mm
PORT_H = 2.6 * mm
NOSE = 3.0 * mm
L_THIEF = 26 * mm


def thief():
    sim = Sim()
    load_bed(sim)
    top = bed_top_at_axis(sim)
    tip_floor = 0.2 * mm
    ports = [tip_floor + NOSE + 0.6 * mm + k * (top - tip_floor - NOSE - 0.6 * mm - PORT_H) / 2 for k in range(3)]
    z_clear = H_JAR + 1 * mm
    t_in0, v_in = 0.1, 30 * mm
    z_surf = top + 1 * mm
    t_air = t_in0 + (z_clear - z_surf) / (80 * mm)  # quicker through the air
    t_in1 = t_air + (z_surf - tip_floor) / v_in
    t_open = t_in1 + 0.1
    t_close = t_open + 0.45
    t_out1 = t_close + 0.1 + (H_JAR + 2 * mm) / (40 * mm)
    keys = [(0, (0, 0, z_clear)), (t_in0, (0, 0, z_clear)), (t_air, (0, 0, z_surf)), (t_in1, (0, 0, tip_floor)),
            (t_close + 0.1, (0, 0, tip_floor)),
            (t_out1, (0, 0, z_clear + 3 * mm))]

    def pose(t):
        return path(t, keys), np.eye(3), True

    def port_sleeve_pose(t):
        return path(t, keys), np.eye(3), not (t_open <= t < t_close)

    col = (0.62, 0.64, 0.68)
    nose = Tool("thief nose", "revolve", [(0, 0), (R_THIEF, NOSE), (R_THIEF, NOSE + 0.3 * mm), (0, NOSE + 0.3 * mm)],
                mu=0.3, pose=pose, color=col)
    core = Tool("thief core", "revolve", revolve_rect(0, R_THIEF_CORE, NOSE, L_THIEF), mu=0.3, pose=pose, color=col)
    edges = [NOSE + 0.3 * mm]
    for zp in ports:
        edges += [zp - tip_floor, zp - tip_floor + PORT_H]
    edges.append(L_THIEF)
    rings = []
    for k in range(len(edges) - 1):
        is_port = k % 2 == 1
        rings.append(Tool(f"sleeve {k}", "revolve", revolve_rect(R_THIEF_CORE, R_THIEF, edges[k], edges[k + 1]), mu=0.3,
                          pose=port_sleeve_pose if is_port else pose, color=(0.50, 0.53, 0.58) if is_port else col))
    sim.tools = jar_tools() + [nose, core] + rings
    rec = Recorder(sim)
    run_phase(sim, rec, t_in0, "thief above the jar, ports closed")
    run_phase(sim, rec, t_in1 - t_in0, "push the closed thief to the floor")
    run_phase(sim, rec, t_open - t_in1, "at the floor")
    run_phase(sim, rec, t_close - t_open, "open the three ports: powder runs in")
    samples, captured = [], []
    rel = sim.x - path(sim.t, keys)
    r = np.hypot(rel[:, 0], rel[:, 1])
    names = ["bottom port", "middle port", "top port"]
    for nm, zp in zip(names, ports):
        z0 = zp - tip_floor
        sel = np.where((sim.mode == FREE) & (r < R_THIEF + 0.1 * mm) & (rel[:, 2] > z0 - 0.2 * mm) &
                       (rel[:, 2] < z0 + PORT_H + 0.2 * mm))[0]
        samples.append(dict(name=nm, **tally(sim, sel)))
        captured.append(sel)
    cap_rel = {int(i): (sim.x[i] - path(sim.t, keys)).tolist() for c in captured for i in c}
    for c in captured:
        sim.mode[c] = DEAD  # they ride out inside the thief (drawn that way in the animation)
    rest = sim.mode == FREE
    sim.v[rest] = 0
    sim.w[rest] = 0
    sim.mode[rest] = ASLEEP  # not scored any more; frozen so pulling the thief out costs nothing
    run_phase(sim, rec, t_out1 - sim.t + 0.2, "close the ports and pull the thief out")
    extra = dict(bed_depth_axis_mm=top / mm, ports_mm=[p / mm for p in ports])
    rec.save("thief", extra=dict(captured=[c.tolist() for c in captured], capture_t=t_close, cap_rel=cap_rel,
                                 keys=[(k[0], list(k[1])) for k in keys], **extra))
    save_result("thief", samples, "Particles inside each port when it closed.", extra=extra)


# ---------------------------------------------------------------------------
# Spoonula


def spoon():
    sim = Sim()
    load_bed(sim)
    top = bed_top_at_axis(sim)
    # A flat blade with low side lips and a back lip. Local x runs along the spoon (+x is the
    # front edge), local z is up out of the bowl.
    a, b, c = 4.5 * mm, 2.6 * mm, 0.2 * mm
    lip = 0.9 * mm
    z_air = H_JAR + 4 * mm
    targets = [top * 5 / 6, top / 2, top / 6]  # middle of each third at the axis, as an operator would aim
    angles = [math.radians(v) for v in (40, 52, 62)]  # steeper for deeper scoops, to stay inside the jar
    nose_keys, ang_keys, scoop_t = [], [], []
    t = 0.3
    for k, (zk, angk) in enumerate(zip(targets, angles)):
        n_end = np.array([1.5 * mm, 0, zk])
        l_dig = (top + 1 * mm - zk) / math.sin(angk)
        n_start = n_end - l_dig * np.array([math.cos(angk), 0, -math.sin(angk)])
        n_air = np.array([n_start[0], 0, z_air + 3 * mm])
        if k:
            nose_keys.append((t - 0.2, n_air))
            ang_keys.append((t - 0.2, angk))
        else:
            nose_keys.append((0.0, n_air))
            ang_keys.append((0.0, angk))
        nose_keys.append((t, n_start))
        ang_keys.append((t, angk))
        t_dig = t + 0.3
        t_lev = t_dig + 0.25
        t_lift = t_lev + 0.3
        t_away = t_lift + 0.2
        n_lev = n_end + np.array([3 * mm, 0, 0])
        n_up = np.array([n_lev[0], 0, z_air])
        n_away = n_up + np.array([26 * mm, 0, 0])
        nose_keys += [(t_dig, n_end), (t_lev, n_lev), (t_lift, n_up), (t_away, n_away)]
        ang_keys += [(t_dig, angk), (t_lev, 0.0), (t_lift, 0.0), (t_away, 0.0)]
        scoop_t.append(dict(t0=t, dig=t_dig, lev=t_lev, lift=t_lift, away=t_away, z=zk))
        t = t_away + 0.4  # the hole slumps while the spoon goes back over the jar

    def blade_pose(t):
        nose = path(t, nose_keys)
        ang = float(path(t, [(tk, [v]) for tk, v in ang_keys])[0])
        R = rot_y(ang)
        return nose - R @ np.array([a, 0, 0]), R

    def part_pose(offset):
        def f(t):
            p, R = blade_pose(t)
            return p + R @ np.asarray(offset), R, True
        return f

    col = (0.72, 0.74, 0.78)
    parts = [Tool("spoon blade", "box", half=[a, b, c], mu=0.4, pose=part_pose([0, 0, 0]), color=col),
             Tool("spoon lip L", "box", half=[a, 0.15 * mm, lip / 2], mu=0.4, pose=part_pose([0, b, lip / 2 + c]),
                  color=col),
             Tool("spoon lip R", "box", half=[a, 0.15 * mm, lip / 2], mu=0.4, pose=part_pose([0, -b, lip / 2 + c]),
                  color=col),
             Tool("spoon back", "box", half=[0.15 * mm, b, lip / 2], mu=0.4, pose=part_pose([-a, 0, lip / 2 + c]),
                  color=col),
             Tool("spoon handle", "box", half=[7 * mm, 0.6 * mm, 0.2 * mm], mu=0.4,
                  pose=part_pose([-a - 7 * mm, 0, lip + c]), color=col)]
    sim.tools = jar_tools() + parts
    rec = Recorder(sim)
    samples, removed = [], []
    names = ["scoop 1 (top)", "scoop 2 (middle)", "scoop 3 (bottom)"]
    run_phase(sim, rec, scoop_t[0]["t0"], "spoonula over the jar")
    for k, s in enumerate(scoop_t):
        if sim.t < s["t0"] - 1e-9:
            run_phase(sim, rec, s["t0"] - sim.t, "the hole slumps in; back over the jar")
        run_phase(sim, rec, s["dig"] - sim.t, f"scoop {k + 1}: dig in at an angle")
        run_phase(sim, rec, s["lev"] - sim.t, f"scoop {k + 1}: level the spoon")
        run_phase(sim, rec, s["lift"] - sim.t, f"scoop {k + 1}: lift out")
        p, R = blade_pose(sim.t)
        loc = (sim.x - p) @ R
        sel = np.where((sim.mode == FREE) & (np.abs(loc[:, 0]) < a + 0.3 * mm) & (np.abs(loc[:, 1]) < b + 0.3 * mm)
                       & (loc[:, 2] > 0) & (loc[:, 2] < 6 * mm))[0]
        samples.append(dict(name=names[k], **tally(sim, sel)))
        removed.append(sel)
        run_phase(sim, rec, s["away"] - sim.t, f"scoop {k + 1}: to a stub")
        sim.mode[sel] = DEAD
    run_phase(sim, rec, 0.3, "after three scoops")
    extra = dict(bed_depth_axis_mm=top / mm, blade_z_mm=[s["z"] / mm for s in scoop_t])
    rec.save("spoon", extra=dict(removed=[r.tolist() for r in removed], **extra))
    save_result("spoon", samples, "Particles on the spoon when it cleared the jar.", extra=extra)


# ---------------------------------------------------------------------------
# Scrape off whole layers (idealised)


def peel():
    """Scrape the whole surface down a thin layer at a time; swab the centre at three depths.

    Idealised: powder above the scraping level just disappears, so this is the best case for
    scraping off layers, not a model of a particular tool.
    """
    sim = Sim()
    load_bed(sim)
    top = bed_top_at_axis(sim)
    sim.tools = jar_tools()
    rec = Recorder(sim)
    v_cut = 12 * mm
    targets = [top * 5 / 6, top / 2, top / 6]
    names = ["top sample", "middle sample", "bottom sample"]
    state = dict(z0=top + 1 * mm, t0=0.0, zt=top + 1 * mm)

    def z_cut(t):
        return max(state["zt"], state["z0"] - v_cut * (t - state["t0"]))

    def scrape(s):
        above = (s.mode == FREE) & (s.x[:, 2] > z_cut(s.t))
        s.mode[above] = DEAD

    run_phase(sim, rec, 0.1, "scrape the whole surface down, a thin layer at a time")
    samples, taken = [], []
    for k, zt in enumerate(targets):
        state.update(z0=z_cut(sim.t), t0=sim.t, zt=zt)
        run_phase(sim, rec, (state["z0"] - zt) / v_cut, f"scrape down to the {names[k].split()[0]} third", hook=scrape)
        run_phase(sim, rec, 0.12, f"swab the middle of the fresh surface ({names[k]})", hook=scrape)
        r = np.hypot(sim.x[:, 0], sim.x[:, 1])
        near = (sim.mode == FREE) & (r < 3 * mm)
        ztop = (sim.x[near, 2] + sim.rad[near]).max()
        sel = np.where(near & (sim.x[:, 2] + sim.rad > ztop - 1.1 * mm))[0]
        samples.append(dict(name=names[k], **tally(sim, sel)))
        taken.append(sel)
        sim.mode[sel] = DEAD
    run_phase(sim, rec, 0.1, "three swabs taken")
    extra = dict(bed_depth_axis_mm=top / mm, cut_mm=[t / mm for t in targets])
    rec.save("peel", extra=dict(taken=[t.tolist() for t in taken], **extra))
    save_result("peel", samples, "Idealised: powder above the scraping level is removed; the sample is the top "
                "particle layer within 3 mm of the axis.", extra=extra)


# ---------------------------------------------------------------------------
# Pour along a line


def pour():
    sim = Sim()
    load_bed(sim)
    lip_z = 10 * mm  # rim height above the plate when pouring starts
    drop = lip_z - H_JAR
    sim.x[:, 2] += drop
    lip0 = np.array([0.0, -(R_JAR + T_WALL), lip_z])
    origin0 = np.array([0.0, 0.0, drop])
    v_line = 20 * mm
    t0, t1 = 0.15, 2.75
    phi_max = math.radians(150)

    def phi(t):
        # tilt quickly to where the powder is about to move, then slowly
        return phi_max * (0.35 * ramp(t, t0, t0 + 0.6) + 0.65 * ramp(t, t0, t1))

    def jar_pose(t):
        R = rot_x(phi(t))
        lip = lip0 + np.array([v_line * max(0.0, t - t0), 0, 0])
        return lip + R @ (origin0 - lip0), R, True

    jar = jar_tools(jar_pose)
    for tl in jar:
        tl.cut = False
    # a tray on a stand, its back edge just under the rim the jar pours over
    y_back = lip0[1] + 0.3 * mm
    plate = Tool("plate", "box", half=[70 * mm, 20 * mm, 12 * mm], mu=0.5,
                 pose=lambda t: (np.array([45 * mm, y_back - 20 * mm, -12 * mm]), np.eye(3), True),
                 color=(0.55, 0.57, 0.60), cut=False)
    sim.tools = jar + [plate]
    rec = Recorder(sim)
    run_phase(sim, rec, t0, "jar at the back edge of a grounded tray")
    run_phase(sim, rec, t1 - t0, "tilt slowly while moving along: the top comes out first")
    run_phase(sim, rec, 0.4, "let it settle")
    on_plate = np.where((sim.mode == FREE) & (sim.x[:, 2] > -0.5 * mm) & (sim.x[:, 2] < 6 * mm) &
                        (sim.x[:, 1] < y_back))[0]
    xs = sim.x[on_plate, 0]
    order = on_plate[np.argsort(xs)]
    bins = np.array_split(order, 9)
    thirds = np.array_split(order, 3)
    names = ["first third poured (top)", "second third (middle)", "last third poured (bottom)"]
    samples = [dict(name=nm, **tally(sim, th)) for nm, th in zip(names, thirds)]
    along = [dict(x_mm=[float(sim.x[bn, 0].min() / mm), float(sim.x[bn, 0].max() / mm)], **tally(sim, bn)) for bn in bins]
    lost = int((sim.mode == FREE).sum() - len(on_plate))
    extra = dict(along_line=along, not_on_plate=lost, line_x_mm=[float(xs.min() / mm), float(xs.max() / mm)])
    rec.save("pour", extra=dict(thirds=[th.tolist() for th in thirds], bins=[bn.tolist() for bn in bins], **extra))
    save_result("pour", samples, "Line split into thirds by particle count along x; also 9 bins.", extra=extra)


if __name__ == "__main__":
    what = sys.argv[1]
    t0 = time.time()
    {"fill": fill, "open_tube": lambda: corer(False), "piston": lambda: corer(True), "thief": thief, "spoon": spoon,
     "peel": peel, "pour": pour}[what]()
    print(f"{what} done in {time.time() - t0:.0f} s", flush=True)
