"""Everything the video reads, through one adapter: the event log of the replayed run, the benchmark summary, the
economics summary and the two function networks.

Every key read from another stream's file is named in ``KEYS`` (or in the small ``_find``/``_get`` lists next to it), so
a late schema change is a one-line fix here and nothing else moves. Missing inputs fall back to placeholders that
carry ``placeholder=True``; every segment that shows a number from one prints a PLACEHOLDER tag on the frame.

Inputs (vertical-lab/out/twin2/):
  events/<run_id>.json     the replayed run: meta, stations, events, designs, results, curves (twin.campaign.event_log)
  bench2_summary.json      curves per facility, policy and seed (the lead's benchmark)
  econ/econ_summary.json   acceleration factor, cost ratios with and without capex, cost per experiment, utilization,
                           outside capacity (the economics stream)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]          # vertical-lab/
# TWIN_VIDEO_ROUND=3: round 3's results (out/twin3: runs/*.jsonl, econ/econ_summary.json, events/) and its own cut in
# out/twin3/video. Round 2's cuts build exactly as before without it. OUT2 stays what both rounds share: the oracle's
# targets, the instruments' pictures, the lab's stills and kin.json.
ROUND = int(os.environ.get("TWIN_VIDEO_ROUND", "2"))
OUT2 = HERE / "out" / "twin2"
OUT3 = HERE / "out" / "twin3"
RES = OUT3 if ROUND == 3 else OUT2
VID = RES / "video"
EVENTS_DIR = RES / "events"
CAMPAIGNS = ("flaime_al", "onr_cu")
HPD = 24.0
HELPERS = ("robot", "operator")                     # round 3 books a step's robot or person as well as its station

# ---------------------------------------------------------------------------------------------------- the keys read
KEYS = dict(
    # event log (twin.campaign.Twin.event_log)
    meta="meta", stations="stations", events="events", designs="designs", results="results", curves="curves",
    t0="t0_h", t1="t1_h", station="station", campaign="campaign", what="what", design="design", node="node",
    st_name="name", st_units="units", st_hours="hours", st_external="external",
    r_t="t_h", r_type="type", r_design="design", r_u="u_true", r_best="best_true", r_spent="spent",
    r_demo="demonstrated", horizon="horizon_days", facility="facility", policy="policy", run_id="run_id",
    # bench2_summary.json
    b_target="target", b_groups="groups", b_curves="curves", b_runs="runs", b_cfg="cfg", b_campaigns="campaigns",
    b_curve="curve", b_n="n",
    # econ_summary.json (each looked up under several names; see econ())
)
FACILITY_LABEL = {"vertical_lab": "automated lab (PR 318)", "proposed": "conventional (partners, core facilities)",
                  "conventional": "conventional (partners, core facilities)"}
VERTICAL, CONVENTIONAL = "vertical_lab", "proposed"     # the two facility keys of twin.facility; see facility_keys()
POLICY_LABEL = {"cost_aware": "cost-aware network surrogate", "tiered": "tiered CALPHAD screening",
                "random": "random, full chain", "cost_aware_tc": "cost-aware, Thermo-Calc",
                "tiered_tc": "tiered, Thermo-Calc", "cost_aware_scaleup": "cost-aware with scale-up",
                "bofn": "BOFN", "pkgfn": "pKGFN", "bofn_blend": "BOFN, blend screening for Cu",
                "gpbo": "GP-BO", "sobol": "Sobol sampling", "heuristic": "heuristic",
                "bofn3": "BOFN, time-aware", "bofn3_usd": "BOFN, per dollar", "pkgfn3": "pKGFN, time-aware"}
TARGET_FALLBACK = {"flaime_al": 0.6, "onr_cu": 0.45}    # twin.bench.TARGET, read live in target() when importable


def facility_keys(keys) -> tuple:
    """(automated, conventional) among a run's facility names: the lead may rename 'proposed' to 'conventional'."""
    ks = list(keys)
    auto = next((k for k in ks if "vertical" in k or "auto" in k), VERTICAL)
    conv = next((k for k in ks if k != auto and ("proposed" in k or "conv" in k or "baseline" in k)), CONVENTIONAL)
    return auto, conv


# ------------------------------------------------------------------------------------------------------- networks
# Until twin/opt/network.py exists (the lead's, about 06:30), the networks as the brief gives them. A node: key, title,
# what it measures, kind (input, sim, lab, out = an outside facility in the conventional lab, output) and the event
# nodes/whats that light it.
NETWORKS = {
    "flaime_al": dict(
        nodes=[
            dict(key="composition", title="Composition", meas="Al + 15 elements, wt%", kind="input", ev=()),
            dict(key="calphad", title="CALPHAD", meas="open databases, Thermo-Calc, AM module", kind="sim",
                 ev=("calphad", "sim_open", "sim_tc", "sim_am", "sim")),
            dict(key="powder", title="Charge + atomize", meas="yield, PSD, SEM/EDS, XRD, XRF", kind="lab",
                 ev=("powder", "charge", "atomize", "powder QC", "gas_atomize")),
            dict(key="print", title="LPBF build", meas="density, cracks", kind="lab", ev=("print",)),
            dict(key="section", title="Section", meas="SEM porosity and cracks, EBSD grains and texture, Vickers",
                 kind="lab", ev=("section",)),
            dict(key="pip", title="PIP", meas="yield, UTS, uniform elongation", kind="lab", ev=("pip",)),
            dict(key="test", title="Heat treat + EDM + tensile", meas="YS, UTS, elongation; 250 C", kind="lab",
                 ev=("test", "promote")),
            dict(key="utility", title="Utility", meas="YS, elongation, mineral burden, gates", kind="output", ev=()),
        ],
        edges=[("composition", "calphad"), ("calphad", "powder"), ("powder", "print"), ("print", "section"),
               ("section", "pip"), ("pip", "test"), ("test", "utility"), ("composition", "utility")]),
    "onr_cu": dict(
        nodes=[
            dict(key="composition", title="Composition", meas="Cu + 8 elements, wt%", kind="input", ev=()),
            dict(key="calphad", title="CALPHAD / heat flow", meas="phases, freezing range, melt pool", kind="sim",
                 ev=("calphad", "sim_open", "sim_tc", "sim_heat", "sim")),
            dict(key="powder", title="Atomize", meas="yield, PSD, SEM/EDS, XRD", kind="lab",
                 ev=("powder", "charge", "atomize", "powder QC", "nsl", "gas_atomize")),
            dict(key="ded_small", title="DED blocks", meas="density, cracks, dilution", kind="lab",
                 ev=("ded_small", "preplaced", "blown_small", "blend_ded")),
            dict(key="section", title="Section", meas="SEM, EBSD beta', XRD beta', Vickers", kind="lab",
                 ev=("section",)),
            dict(key="pip", title="PIP", meas="yield, UTS, uniform elongation", kind="lab", ev=("pip",)),
            dict(key="screen", title="Corrosion screen", meas="OCP, LPR, EIS, CP", kind="lab", ev=("screen",)),
            dict(key="tensile", title="DED bars + tensile", meas="YS, UTS, elongation", kind="lab",
                 ev=("tensile", "ded_large", "blown_large")),
            dict(key="immersion", title="30-day immersion + ICP-MS", meas="seawater corrosion rate, ions",
                 kind="lab", ev=("immersion",)),
            dict(key="utility", title="Utility", meas="YS, elongation, seawater rate, Ni", kind="output", ev=()),
        ],
        edges=[("composition", "calphad"), ("calphad", "powder"), ("powder", "ded_small"), ("ded_small", "section"),
               ("section", "pip"), ("pip", "screen"), ("screen", "tensile"), ("tensile", "immersion"),
               ("immersion", "utility"), ("composition", "utility")]),
}


def network(campaign: str) -> dict:
    """The campaign's function network: the lead's twin/opt/network.py when it imports and has nodes, else NETWORKS.
    Its nodes are adapted to {key, title, meas, kind, ev}; anything missing keeps the brief's value."""
    base = NETWORKS[campaign]
    try:
        sys.path.insert(0, str(HERE))
        from twin.opt import network as N            # noqa: F401  (the lead's module, when it lands)
        spec = None
        for name in ("NETWORKS", "NETS", "networks"):
            v = getattr(N, name, None)
            if isinstance(v, dict) and campaign in v:
                spec = v[campaign]
                break
        if spec is None and hasattr(N, "network"):
            spec = N.network(campaign)
        if not spec:
            return base
        nodes = spec.get("nodes") if isinstance(spec, dict) else getattr(spec, "nodes", None)
        edges = spec.get("edges") if isinstance(spec, dict) else getattr(spec, "edges", None)
        if not nodes:
            return base
        known = {n["key"]: n for n in base["nodes"]}
        out = []
        for n in (nodes.values() if isinstance(nodes, dict) else nodes):
            if isinstance(n, str):
                n = {"key": n}
            elif not isinstance(n, dict):
                n = {k: getattr(n, k) for k in ("key", "name", "title", "label", "outputs", "kind") if hasattr(n, k)}
            key = n.get("key") or n.get("name")
            k0 = known.get(key, {})
            meas = n.get("meas") or n.get("outputs") or k0.get("meas", "")
            if isinstance(meas, (list, tuple)):
                meas = ", ".join(str(m) for m in meas)
            out.append(dict(key=key, title=n.get("title") or n.get("label") or k0.get("title") or key, meas=meas,
                            kind=n.get("kind") or k0.get("kind", "lab"),
                            ev=tuple(n.get("ev") or n.get("events") or k0.get("ev") or (key,))))
        ed = [tuple(e[:2]) for e in (edges or [])] or [(a["key"], b["key"]) for a, b in zip(out[:-1], out[1:])]
        return dict(nodes=out, edges=ed, source="twin/opt/network.py")
    except Exception:                                   # noqa: BLE001  (not there yet, or mid-edit)
        return base


def node_of(campaign: str, ev_node, what) -> str | None:
    """The network node an event lights: its own node tag, else its 'what'."""
    for n in network(campaign)["nodes"]:
        if ev_node is not None and (ev_node == n["key"] or ev_node in n["ev"]):
            return n["key"]
    for n in network(campaign)["nodes"]:
        if what is not None and what in n["ev"]:
            return n["key"]
    return None


# ------------------------------------------------------------------------------------------------------ event log
REPLAY_RUNS = [os.environ.get("TWIN_VIDEO_RUN", "vertical_lab_bofn_blend_s0"),   # the lead's replay (06:01 plan)
               "vertical_lab_bofn_s0", "vertical_lab_cost_aware_s0"]
# round 3's replay: time-aware BOFN, seed 0, the only seed whose event log round 3 committed. For aluminium it is the
# median seed of the 12 (its halfway target on day 96, the Kaplan-Meier median itself; the first target on day 96
# against a median of 83). For copper it is one of the 4 seeds of 12 that never reach the first target (the median
# seed gets there on day 221): the replay says so (compose.seed_badge, narration3.json seed1). A re-run of seed 5
# (near the median in both campaigns) did not reproduce its committed row on this runner, so its log is not used.
REPLAY_RUN3 = os.environ.get("TWIN_VIDEO_RUN", "r3_vertical_lab_bofn3_s0")


def _meta_of(p: Path) -> dict:
    try:
        m = json.loads(Path(p).read_text()).get(KEYS["meta"], {})
    except Exception:                                   # noqa: BLE001
        return {}
    cfg = m.get("cfg") if isinstance(m.get("cfg"), dict) else {}
    return dict(cfg, **{k: v for k, v in m.items() if k != "cfg"})


def _newest_events() -> Path | None:
    """The run to replay: $TWIN_VIDEO_EVENTS, else events/<REPLAY_RUN>.json, else the newest automated-lab log, else
    the lead's sample."""
    env = os.environ.get("TWIN_VIDEO_EVENTS")
    if env:
        return Path(env)
    if ROUND == 3:
        return EVENTS_DIR / f"{REPLAY_RUN3}.json"
    if not EVENTS_DIR.exists():
        return None
    if not os.environ.get("TWIN_VIDEO_RUN"):          # the lead may swap in another seed: the newest of the pattern
        seeds = sorted(EVENTS_DIR.glob("vertical_lab_bofn_blend_s*.json"), key=lambda p: (p.stat().st_mtime, p.name))
        if seeds:
            return seeds[-1]
    for run in REPLAY_RUNS:
        if (EVENTS_DIR / f"{run}.json").exists():
            return EVENTS_DIR / f"{run}.json"
    files = sorted(EVENTS_DIR.glob("*.json"), key=lambda p: (p.stat().st_mtime, p.name))
    pick = [p for p in files if p.stem != "sample"] or files
    for p in reversed(pick):
        if "vertical" in str(_meta_of(p).get(KEYS["facility"], "vertical")):
            return p
    return pick[-1] if pick else None


def make_placeholder_events(facility: str = "vertical_lab", seed: int = 0, policy: str = "cost_aware") -> Path:
    """A real one-year run of the twin as it is now (seconds), written to out/twin2/video/placeholder_<facility>.json,
    standing in until the lead's event log exists."""
    VID.mkdir(parents=True, exist_ok=True)
    dst = VID / f"placeholder_{facility}.json"
    if dst.exists():
        return dst
    code = (
        "import json,sys; sys.path.insert(0,'.');"
        "from twin import campaign as C, policies as P, bench as B;"
        f"sp={{k: C.Spec(k, B.BUDGET[k], B.WIP[k], {seed}, 1.0) for k in ('flaime_al','onr_cu')}};"
        f"po={{k: P.POLICIES['{policy}'](k, {seed}) for k in sp}};"
        f"tw=C.Twin(sp, po, scenario='historical', facility='{facility}', seed={seed}, horizon_days=365, "
        "isolated=False); tw.run();"
        f"log=tw.event_log(meta=dict(run_id='placeholder_{facility}', facility='{facility}', policy='{policy}', "
        f"seed={seed}, scenario='historical', placeholder=True));"
        f"json.dump(log, open(r'{dst}', 'w'))")
    subprocess.run([sys.executable, "-c", code], cwd=HERE, check=True, timeout=900)
    return dst


class Replay:
    """The event log, indexed for per-frame questions: what runs at t, which nodes are lit, the best so far, money."""

    def __init__(self, path: Path | None = None):
        path = path or _newest_events()
        self.placeholder = False
        if path is None or not Path(path).exists():
            path = make_placeholder_events("vertical_lab")
            self.placeholder = True
        self.path = Path(path)
        js = json.loads(self.path.read_text())
        K = KEYS
        m0 = js.get(K["meta"], {})
        cfg = m0.get("cfg") if isinstance(m0.get("cfg"), dict) else {}
        self.meta = dict(cfg, **{k: v for k, v in m0.items() if k != "cfg"})     # meta.cfg.policy -> meta.policy
        self.placeholder = self.placeholder or bool(self.meta.get("placeholder")) or self.path.stem == "sample"
        self.horizon_days = float(self.meta.get(K["horizon"], 365))
        self.horizon_h = self.horizon_days * HPD
        self.stations = js.get(K["stations"], {})
        self.designs = {c: {str(k): v for k, v in d.items()} for c, d in js.get(K["designs"], {}).items()}
        evs = js.get(K["events"], [])
        if ROUND == 3:                                  # a step's robot and person are booked beside its station:
            self.helper_h = {h: sum(e[K["t1"]] - e[K["t0"]] for e in evs if e.get(K["station"]) == h)
                             for h in HELPERS}          # their hours kept, their bookings not drawn as stations
            evs = [e for e in evs if e.get(K["station"]) not in HELPERS]
            self.stations = {k: v for k, v in self.stations.items() if k not in HELPERS}
        self.ev = evs
        self.t0 = np.array([e[K["t0"]] for e in evs], float)
        self.t1 = np.array([max(e[K["t1"]], e[K["t0"]] + 1e-3) for e in evs], float)
        self.camp = np.array([e.get(K["campaign"]) or "" for e in evs])
        self.station = np.array([e.get(K["station"]) or "" for e in evs])
        self.what = [e.get(K["what"]) for e in evs]
        self.design = [None if e.get(K["design"]) is None else str(e.get(K["design"])) for e in evs]
        self.node = np.array([node_of(c, e.get(K["node"]), e.get(K["what"])) or "" for c, e in zip(self.camp, evs)])
        self.results = sorted(js.get(K["results"], []), key=lambda r: r.get(K["r_t"], 0.0))
        self.curves = {c: np.array(v, float).reshape(-1, 3) for c, v in js.get(K["curves"], {}).items()}
        for c in CAMPAIGNS:
            self.curves.setdefault(c, np.zeros((0, 3)))
        self.facility = self.meta.get(K["facility"], VERTICAL)
        self.policy = str(self.meta.get(K["policy"], "cost_aware")).split(" ")[0]     # "cost_aware (round 1, ...)"
        self.seed = self.meta.get("seed")
        self.spend = {}
        if ROUND == 3:
            # round 3 scores new alloys only (the reference alloys the lab also makes don't count toward a target),
            # so the replay's best-so-far is the committed run's own curve_new, and its money the run's weekly ledger
            self.curves_all = dict(self.curves)
            row = run_row(self.facility, self.policy, self.seed)
            self.row = row
            for c in CAMPAIGNS:
                cc = (row or {}).get("campaigns", {}).get(c) or {}
                self.curves[c] = np.array(cc.get("curve_new") or [], float).reshape(-1, 3)
                if cc.get("spend_curve"):
                    self.spend[c] = np.array(cc["spend_curve"], float).reshape(-1, 2)
        # counters: alloys made (a lot of powder came back), printed or deposited, tested (a demonstrated result)
        self._made = {c: sorted(r[K["r_t"]] for r in self.results if r.get(K["campaign"]) == c
                                and r.get(K["r_type"]) == "lot") for c in CAMPAIGNS}
        self._built = {c: sorted(r[K["r_t"]] for r in self.results if r.get(K["campaign"]) == c
                                 and r.get(K["r_type"]) in ("build", "deposit")) for c in CAMPAIGNS}
        self._tested = {c: sorted(r[K["r_t"]] for r in self.results if r.get(K["campaign"]) == c
                                  and r.get(K["r_type"]) == K["r_demo"]) for c in CAMPAIGNS}
        self._sims = {c: sorted(r[K["r_t"]] for r in self.results if r.get(K["campaign"]) == c
                                and r.get(K["r_type"]) == "sim") for c in CAMPAIGNS}
        self._span = {c: {} for c in CAMPAIGNS}           # design -> (first booking starts, last booking ends)
        for i in range(len(evs)):
            c, d = self.camp[i], self.design[i]
            if d is not None and c in self._span:
                a, b = self._span[c].get(d, (self.t0[i], self.t1[i]))
                self._span[c][d] = (min(a, self.t0[i]), max(b, self.t1[i]))
        self._designs_t = {}
        for c in CAMPAIGNS:
            first = {}
            for i in range(len(evs)):
                if self.camp[i] == c and self.design[i] is not None:
                    first.setdefault(self.design[i], self.t0[i])
            self._designs_t[c] = sorted(first.values())

    # -------------------------------------------------------------------------------------------- per-frame queries
    def active(self, t_h: float, span_h: float = 0.0, campaign: str | None = None) -> np.ndarray:
        """Indices of events running at any moment of [t_h - span_h, t_h]."""
        m = (self.t0 <= t_h) & (self.t1 > t_h - span_h)
        if campaign:
            m &= self.camp == campaign
        return np.nonzero(m)[0]

    def lit(self, t_h: float, span_h: float = 0.0) -> dict:
        """{(campaign, node): number of its events running over [t_h - span_h, t_h]}."""
        out: dict = {}
        for i in self.active(t_h, span_h):
            k = (self.camp[i], self.node[i])
            if k[1]:
                out[k] = out.get(k, 0) + 1
        return out

    def busy_stations(self, t_h: float, span_h: float = 0.0) -> dict:
        """{station: (campaigns running there, the share of [t_h - span_h, t_h] it was busy)}."""
        out: dict = {}
        idx = self.active(t_h, span_h)
        for i in idx:
            st = self.station[i]
            camps, occ = out.get(st, (set(), 0.0))
            camps.add(self.camp[i])
            if span_h > 0:
                a, b = max(self.t0[i], t_h - span_h), min(self.t1[i], t_h)
                occ += max(0.0, b - a) / span_h
            else:
                occ = 1.0
            out[st] = (camps, occ)
        units = {k: max(1, int(v.get(KEYS["st_units"], 1) or 1)) for k, v in self.stations.items()}
        return {k: (c, min(1.0, o / units.get(k, 1))) for k, (c, o) in out.items()}

    def wip(self, t_h: float, campaign: str) -> int:
        """Designs in progress at t_h: their first booking has started and their last has not ended."""
        return sum(1 for a, b in self._span[campaign].values() if a <= t_h < b)

    def in_progress(self, t_h: float, campaign: str, n: int = 6) -> list:
        """Designs in progress at t_h (see wip), the most recently busy first: [(design id, composition, node)]."""
        live = [d for d, (a, b) in self._span[campaign].items() if a <= t_h < b and d in self.designs.get(campaign, {})]
        if not live:
            return []
        m = (self.t0 <= t_h) & (self.camp == campaign)
        last: dict = {}
        for i in np.nonzero(m)[0]:
            d = self.design[i]
            if d in live and self.t0[i] >= last.get(d, (-1.0, ""))[0]:
                last[d] = (self.t0[i], self.node[i])
        live.sort(key=lambda d: -last.get(d, (0.0, ""))[0])
        return [(d, self.designs[campaign][d], last.get(d, (0.0, ""))[1]) for d in live[:n]]

    def in_flight(self, t_h: float, campaign: str, span_h: float = 0.0, n: int = 9) -> list:
        """Designs with work running over [t_h - span_h, t_h], latest start first: [(design id, composition, node)]."""
        idx = self.active(t_h, span_h, campaign)
        idx = sorted(idx, key=lambda i: -self.t0[i])
        seen, out = set(), []
        for i in idx:
            d = self.design[i]
            if d is None or d in seen or d not in self.designs.get(campaign, {}):
                continue
            seen.add(d)
            out.append((d, self.designs[campaign][d], self.node[i]))
            if len(out) >= n:
                break
        return out

    def steps_now(self, t_h: float, span_h: float = 0.0) -> list:
        """(campaign, what, station, design) of the events running, most recent start first."""
        idx = sorted(self.active(t_h, span_h), key=lambda i: -self.t0[i])
        return [(self.camp[i], self.what[i], self.station[i], self.design[i]) for i in idx]

    def best_at(self, campaign: str, t_h: float) -> float:
        c = self.curves[campaign]
        if not len(c):
            return 0.0
        m = c[:, 0] * HPD <= t_h
        return float(c[m, 2].max()) if m.any() else 0.0

    def spent_at(self, campaign: str, t_h: float) -> float:
        """Money spent by t_h: linear between the run's own (day, spent) points, from 0 at day 0."""
        if campaign in self.spend:                      # round 3: the run's ledger at 7-day steps
            sc = self.spend[campaign]
            return float(np.interp(t_h / HPD, sc[:, 0], sc[:, 1]))
        c = self.curves[campaign]
        if not len(c):
            return 0.0
        d = np.concatenate([[0.0], c[:, 0]])
        s = np.concatenate([[0.0], c[:, 1]])
        return float(np.interp(t_h / HPD, d, s))

    def curve_upto(self, campaign: str, t_h: float, x: str = "days") -> np.ndarray:
        """The best-so-far step curve up to t_h as (x, best) points, x in days or dollars."""
        c = self.curves[campaign]
        m = c[:, 0] * HPD <= t_h
        cc = c[m]
        col = 0 if x == "days" else 1
        return np.stack([cc[:, col], cc[:, 2]], 1) if len(cc) else np.zeros((0, 2))

    def counts(self, campaign: str, t_h: float) -> dict:
        import bisect
        return dict(designed=bisect.bisect_right(self._designs_t[campaign], t_h),
                    sims=bisect.bisect_right(self._sims[campaign], t_h),
                    made=bisect.bisect_right(self._made[campaign], t_h),
                    built=bisect.bisect_right(self._built[campaign], t_h),
                    tested=bisect.bisect_right(self._tested[campaign], t_h))

    def first_event(self, campaign: str, whats=None, nodes=None, after_h: float = 0.0):
        """The first event of a campaign with one of the whats (or nodes) starting at or after after_h."""
        for i in np.argsort(self.t0, kind="stable"):
            if self.t0[i] < after_h or self.camp[i] != campaign:
                continue
            if (whats and self.what[i] in whats) or (nodes and self.node[i] in nodes):
                return int(i)
        return None


# ------------------------------------------------------------------------------------------ round 3's runs
RUNS3 = {"main": "main.jsonl", "conventional": "conventional.jsonl", "main_more": "main_more.jsonl",
         "cu_money": "cu_money.jsonl", "cu_hidden": "cu_hidden.jsonl", "cu_hidden_net": "cu_hidden_net.jsonl",
         "cu_proxy": "cu_proxy.jsonl", "cu_ablation": "cu_ablation.jsonl"}
_ROWS: dict = {}


def rows3(exp: str = "main") -> list:
    """Round 3's committed runs of one experiment (out/twin3/runs/<exp>.jsonl), one dict a run."""
    if exp not in _ROWS:
        p = OUT3 / "runs" / RUNS3.get(exp, f"{exp}.jsonl")
        _ROWS[exp] = [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()] if p.exists() else []
    return _ROWS[exp]


def run_row(facility: str, policy: str, seed) -> dict | None:
    """The committed run a round-3 event log belongs to: main for the vertical lab, conventional for the other."""
    exp = "main" if "vertical" in str(facility) else "conventional"
    for r in rows3(exp):
        c = r["cfg"]
        if c["policy"] == policy and c["seed"] == seed and c["facility"] == facility:
            return r
    return None


def targets2() -> dict:
    """The halfway target (T2): halfway from the best existing alloy's score to the best the twin's search found
    (bench2_summary.json targets.T2, twin.bench2.targets(); the same in rounds 2 and 3)."""
    t = ((_read(OUT2 / "bench2_summary.json") or {}).get("targets") or {}).get("T2") or {}
    return {c: float(t[c]) for c in CAMPAIGNS if c in t}


def hit_day(curve, tv: float):
    """The first day a best-so-far curve [(day, spent, best), ...] reaches tv, else None (twin.bench2.hit)."""
    for row in curve:
        if row[2] >= tv:
            return float(row[0])
    return None


def km_median(times: list, horizon: float):
    """Kaplan-Meier median of first-hit days, a run that never gets there censored at the horizon (twin.bench3
    .km_median, the rule round 3's tables use for every arm): for 12 runs, the 6th to get there; None when fewer than
    half do."""
    ev = sorted((t if t is not None else horizon + 1e-6, t is not None) for t in times)
    n, sv = len(ev), 1.0
    for i, (t, hit) in enumerate(ev):
        if hit:
            sv *= 1.0 - 1.0 / (n - i)
            if sv <= 0.5:
                return t
    return None


def arm3(exp: str, facility: str, policy: str, campaign: str, **cfg) -> dict:
    """One arm of round 3 from its committed runs: per-seed days to both targets, the counts that got there, the
    Kaplan-Meier medians, the final best new alloy (mean, SE) and the horizon. cfg filters the runs' own cfg."""
    rs = [r for r in rows3(exp) if r["cfg"]["policy"] == policy and r["cfg"]["facility"] == facility
          and all(r["cfg"].get(k) == v for k, v in cfg.items())]
    rs.sort(key=lambda r: r["cfg"]["seed"])
    T = {"T1": target()[campaign], "T2": targets2()[campaign]}
    hz = float(rs[0]["cfg"].get("days", 365)) if rs else 365.0
    out = dict(n=len(rs), seeds=[r["cfg"]["seed"] for r in rs], horizon=hz)
    best = [r["campaigns"][campaign]["best_new"] for r in rs]
    out["best"] = best
    out["best_mean"] = float(np.mean(best)) if best else None
    out["best_se"] = float(np.std(best, ddof=1) / np.sqrt(len(best))) if len(best) > 1 else 0.0
    for tn, tv in T.items():
        d = [hit_day(r["campaigns"][campaign]["curve_new"], tv) for r in rs]
        out[tn] = dict(target=tv, days=d, hits=sum(x is not None for x in d), median=km_median(d, hz),
                       hits_365=sum(x is not None and x <= 365.0 for x in d))
    return out


# --------------------------------------------------------------------------------------------- bench summary
def target() -> dict:
    """The state-of-the-art utility each campaign is scored against: bench2_summary.json targets.T1 (the oracle's best
    reference alloy), else econ_summary.json targets.values, else twin.bench.TARGET."""
    js = _read(OUT2 / "bench2_summary.json")
    t = (js or {}).get("targets") if isinstance(js, dict) else None
    if isinstance(t, dict):
        t1 = t.get(TARGET_KEY) if isinstance(t.get(TARGET_KEY), dict) else t
        if all(isinstance(t1.get(c), (int, float)) for c in CAMPAIGNS):
            return {c: float(t1[c]) for c in CAMPAIGNS}
    e = _read(OUT2 / "econ" / "econ_summary.json")
    v = ((e or {}).get("targets") or {}).get("values") if isinstance(e, dict) else None
    if isinstance(v, dict) and all(c in v for c in CAMPAIGNS):
        return {c: float(v[c]) for c in CAMPAIGNS}
    try:
        sys.path.insert(0, str(HERE))
        from twin import bench as B
        return {c: float(B.TARGET[c]) for c in CAMPAIGNS}
    except Exception:                                   # noqa: BLE001
        return dict(TARGET_FALLBACK)


TARGET_KEY = "T1"                                       # bench2_summary.json targets.T1: state of the art


def target_refs() -> dict:
    """{campaign: the reference alloy that sets the target} from out/twin2/oracle.json ('sota'), when present."""
    o = _read(OUT2 / "oracle.json") or {}
    return {c: (o.get(c) or {}).get("sota") for c in CAMPAIGNS}


def _read(p: Path):
    try:
        return json.loads(Path(p).read_text())
    except Exception:                                   # noqa: BLE001
        return None


def _is_curve(x) -> bool:
    return isinstance(x, list) and (not x or (isinstance(x[0], (list, tuple)) and len(x[0]) == 3))


HEADLINE_GROUP = dict(scenario="historical")            # bench rows kept: the historical market, default settings
V1_RUNS = [HERE / "out" / "twin" / "runs" / "main.jsonl", HERE / "out" / "twin" / "runs" / "facility.jsonl"]


def bench(extra_runs: list | None = None) -> dict:
    """Per-seed best-so-far curves {(facility, policy): {campaign: [array (days, spent, best), ...]}}.

    From out/twin2/bench2_summary.json: experiments.<exp>.<group>.{facility, policy, campaigns.<c>.curves}; a (facility,
    policy) found in several experiments keeps the first. Pairs it lacks (the conventional lab, until bench2 runs it)
    come from the round-1 runs the economics stream also uses as its reference (out/twin/runs/main.jsonl and
    facility.jsonl, historical market, default kappa and WIP). placeholder=True when neither exists."""
    js = _read(OUT2 / "bench2_summary.json")
    groups: dict = {}
    source: dict = {}

    def add(fac, pol, camp, curve, src):
        if fac is None or pol is None or camp not in CAMPAIGNS or not _is_curve(curve):
            return
        groups.setdefault((fac, pol), {}).setdefault(camp, []).append(np.array(curve, float).reshape(-1, 3))
        source[(fac, pol)] = src

    if ROUND == 3:
        # round 3: each run's best new alloy so far (curve_new) from the committed runs: the vertical lab's 12
        # one-year runs per policy (main) and the conventional lab's 12 three-year runs (conventional)
        for exp in ("main", "conventional"):
            for r in sorted(rows3(exp), key=lambda r: r["cfg"]["seed"]):
                c = r["cfg"]
                for camp in CAMPAIGNS:
                    add(c["facility"], c["policy"], camp, r["campaigns"][camp]["curve_new"],
                        f"out/twin3/runs/{exp}.jsonl")
        return dict(groups=groups, placeholder=not groups, target=target(), source=source)

    if isinstance(js, dict):
        exps = js.get("experiments") if isinstance(js.get("experiments"), dict) else {"": js}
        prefer = ["main", "conventional"]               # the lead's final experiments; dev only while they are missing
        names = [e for e in prefer if e in exps] or [e for e in ("dev",) if e in exps] or list(exps)
        for ename in names:
            exp = exps[ename]
            if not isinstance(exp, dict):
                continue
            for gk, g in exp.items():
                if not isinstance(g, dict):
                    continue
                cfg = g.get("cfg") if isinstance(g.get("cfg"), dict) else {}
                fac, pol = g.get("facility") or cfg.get("facility"), g.get("policy") or cfg.get("policy")
                if fac is None or pol is None:          # 'proposed_tiered', 'vertical_lab_bofn_blend'
                    for f in ("vertical_lab", "proposed", "conventional"):
                        if str(gk).startswith(f + "_"):
                            fac, pol = fac or f, pol or str(gk)[len(f) + 1:]
                if any(cfg.get(k) not in (None, v) for k, v in HEADLINE_GROUP.items()):
                    continue
                if (fac, pol) in groups and source.get((fac, pol)) != f"bench2_summary.json:{ename}":
                    continue
                camps = g.get("campaigns") if isinstance(g.get("campaigns"), dict) else g
                for camp in CAMPAIGNS:
                    cc = camps.get(camp)
                    for c in (cc.get("curves") or []) if isinstance(cc, dict) else []:
                        add(fac, pol, camp, c, f"bench2_summary.json:{ename}")
    b2_conv = any(("proposed" in str(f) or "conv" in str(f)) for f, _ in groups)
    if not b2_conv and groups:                          # no conventional runs in bench2 yet: the round-1 runs for
        b2 = (groups, source)                           # both labs (what econ_summary.json used), bench2's other
        groups, source = {}, {}                         # policies after them
    else:
        b2 = None
    have = set(groups)
    for p in V1_RUNS if not b2_conv else []:            # the conventional reference the economics stream uses
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            try:
                r = json.loads(line)
            except Exception:                           # noqa: BLE001
                continue
            c = r.get("cfg", {})
            if c.get("scenario") != "historical" or float(c.get("kappa", 1.0)) != 1.0 or c.get("isolated") \
                    or c.get("wip") or (c.get("facility"), c.get("policy")) in have:
                continue
            for camp in CAMPAIGNS:
                add(c.get("facility"), c.get("policy"), camp, (r.get("campaigns", {}).get(camp) or {}).get("curve"),
                    f"out/twin/runs/{p.name} (round 1)")
    if b2 is not None:
        for k, v in b2[0].items():
            if k not in groups:
                groups[k], source[k] = v, b2[1][k]
    placeholder = not groups
    if placeholder:                                     # the replayed run and one twin-year of each facility
        logs = list(extra_runs or [])
        for f in sorted(VID.glob("placeholder_*.json")):
            try:
                logs.append(Replay(f))
            except Exception:                           # noqa: BLE001
                pass
        seen = set()
        for log in logs:
            if log is None or (log.facility, str(log.path)) in seen:
                continue
            seen.add((log.facility, str(log.path)))
            for camp in CAMPAIGNS:
                add(log.facility, log.policy, camp, log.curves[camp].tolist(), "placeholder run")
    return dict(groups=groups, placeholder=placeholder, target=target(), source=source)


def mean_curve(curves: list, grid: np.ndarray, col: int = 0) -> tuple:
    """Mean and standard error of best-so-far step curves on a grid of days (col 0) or dollars (col 1)."""
    if not curves:
        return np.zeros_like(grid), np.zeros_like(grid)
    Y = []
    for c in curves:
        y = np.zeros(len(grid))
        for row in c:
            y[grid >= row[col]] = np.maximum(y[grid >= row[col]], row[2])
        Y.append(y)
    Y = np.array(Y)
    se = Y.std(0, ddof=1) / np.sqrt(len(Y)) if len(Y) > 1 else np.zeros(len(grid))
    return Y.mean(0), se


def first_hit(curves: list, tgt: float, col: int = 0) -> tuple:
    """(median over seeds of the day (col 0) or dollars (col 1) at which a curve first reaches tgt, hit fraction)."""
    hits = []
    for c in curves:
        h = [row[col] for row in c if row[2] >= tgt]
        hits.append(h[0] if h else np.nan)
    hits = np.array(hits, float)
    return (float(np.nanmedian(hits)) if np.isfinite(hits).any() else None,
            float(np.isfinite(hits).mean()) if len(hits) else 0.0)


# ---------------------------------------------------------------------------------------------- econ summary
# econ_summary.json (the economics stream). The comparison the headline quotes, and the cost basis the takeaway's Y
# uses; both are one-line choices.
HEADLINE_COMPARISON = os.environ.get("TWIN_VIDEO_COMPARISON", "")      # "" = choose by the replayed policy
COST_BASES = [  # canonical cost bases (see canon_basis) and their labels on screen, in the order the results list them
    ("cash", "the campaigns' own spending"),
    ("op_alone", "operating cost, no capex"),
    ("full_alone", "full cost, capex included"),
    ("op_shared", "operating cost, lab shared with outside users"),
    ("full_shared", "full cost, lab shared with outside users"),
]
TAKEAWAY_BASIS = os.environ.get("TWIN_VIDEO_BASIS", "auto")   # "auto": the first basis on which it is cheaper
BASIS_WORDS = {
    "op_alone": "of the conventional lab's operating cost (no capex)",
    "full_alone": "of the conventional lab's full cost (capex included)",
    "op_shared": "of the conventional lab's operating cost, but only with the lab shared with outside users",
    "full_shared": "of the conventional lab's full cost, but only with the lab shared with outside users",
    "cash": "of the conventional lab's spending on the campaigns alone",
}


# round 3: BOFN and pKGFN were not run in the conventional lab, so the comparison the explainer draws is the one the
# economics summary leads with (the vertical lab with pKGFN against the conventional lab run by the heuristic)
COMPARISON3 = "vertical lab + pkgfn3 vs conventional + heuristic"


def canon_basis(name: str) -> str:
    """econ_summary.json's cost basis names, old and new, to one set: cash, op_alone, op_shared, full_alone,
    full_shared ('operating, alone', 'full, shared', 'full at 60% utilization', ...)."""
    n = str(name).lower()
    if "cash" in n:
        return "cash"
    shared = "shared" in n or "60%" in n or "utiliz" in n
    if "full" in n:
        return "full_shared" if shared else "full_alone"
    if "operat" in n:
        return "op_shared" if shared else "op_alone"
    return n


def comparison_pair(name: str) -> tuple:
    """(automated lab's policy, conventional lab's policy) from 'vertical lab + A vs conventional + B' or
    'B on the partners -> A in the vertical lab'."""
    n = str(name)
    m = re.match(r"\s*vertical lab \+ (\S+) vs conventional \+ (\S+)", n)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"\s*(\S+) on the partners -> (\S+) in the vertical lab", n)
    if m:
        return m.group(2), m.group(1)
    return None, None


def choose_comparison(names: list, policy: str) -> str | None:
    """The comparison the headline quotes: $TWIN_VIDEO_COMPARISON if set, else the automated lab running the replayed
    policy (or its base: bofn for bofn_blend) against the conventional lab running the same, else against any."""
    if HEADLINE_COMPARISON in names:
        return HEADLINE_COMPARISON
    base = str(policy).split("_blend")[0]
    pairs = {n: comparison_pair(n) for n in names}
    for want_a in (policy, base):
        for want_b in (policy, base, "cost_aware", "tiered", None):
            for n, (a, b) in pairs.items():
                if a == want_a and (want_b is None or b == want_b):
                    return n
    return names[0] if names else None


def pick_basis(costs: dict) -> tuple:
    """(basis, ratio, words) the takeaway quotes. 'auto' takes the first of op_alone, full_alone, op_shared,
    full_shared on which the automated lab is cheaper (ratio < 1), so a saving that needs outside users says so; if
    none, the operating cost, worded as the higher cost it is. $TWIN_VIDEO_BASIS forces one."""
    def r(k):
        c = costs.get(k) or {}
        return c.get("ratio") if c.get("ratio") is not None else c.get("ratio_bound")
    if TAKEAWAY_BASIS != "auto" and r(TAKEAWAY_BASIS) is not None:
        return TAKEAWAY_BASIS, r(TAKEAWAY_BASIS), BASIS_WORDS.get(TAKEAWAY_BASIS, TAKEAWAY_BASIS)
    for k in ("op_alone", "full_alone", "op_shared", "full_shared"):
        if r(k) is not None and r(k) < 1.0:
            return k, r(k), BASIS_WORDS[k]
    if r("op_alone") is not None:
        return "op_alone", r("op_alone"), "of the conventional lab's operating cost: the automated lab costs more"
    return None, None, "cost: pending"


CPE_CASES = [  # (case in cost_per_experiment.cases.<campaign>, label)
    ("conventional, no capex", "conventional, no capex"),
    ("conventional, with capex", "conventional, with capex"),
    ("vertical lab, campaigns only, no capex", "automated, no capex"),
    ("vertical lab, campaigns only, with capex", "automated, with capex"),
    ("vertical lab, 60% utilized, with capex", "automated at 60% use, with capex"),
]
CPE_PARTS = ["capex", "service", "utilities", "labour", "consumables", "outside_fees"]


def _num(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    if v in ("inf", "Infinity"):
        return float("inf")
    return None


def econ(policy: str | None = None) -> dict:
    """The economics stream's numbers, normalised:
    comparison (name), comparisons (all names), accel {campaign: {af, lo, hi, bounded, af_bound, median_ref,
    median_new, hit_ref, hit_new, n_ref, n_new, ref, new}}, cost {campaign: {basis: {ratio, lo, hi, median_ref,
    median_new}}}, per_experiment {campaign: [(label, {part: $}, total, n)]}, utilization {station: share} (and
    util_by_campaign), outside {jobs, revenue, net, net_x_depreciation, net_x_fixed, cap, demand_h_week, dl_*},
    headlines [str], targets {campaign: utility}, target_src; placeholder=True when the file is missing."""
    js = _read(RES / "econ" / "econ_summary.json")
    out = dict(placeholder=not isinstance(js, dict), raw=js, accel={}, cost={}, per_experiment={}, utilization={},
               util_by_campaign={}, outside={}, headlines=[], comparisons=[], comparison=None)
    if not isinstance(js, dict):
        return out
    acc = js.get("acceleration") or {}
    out["comparisons"] = list(acc)
    if policy is None:
        try:
            policy = Replay().policy
        except Exception:                               # noqa: BLE001
            policy = "cost_aware"
    cmp_ = choose_comparison(list(acc), policy)
    if ROUND == 3 and COMPARISON3 in acc:               # round 3's economics were run for pKGFN, not the replayed BOFN
        cmp_ = COMPARISON3
    out["comparison"] = cmp_
    for camp in CAMPAIGNS:
        c = ((acc.get(cmp_) or {}).get(camp) or {}).get("compare") or {}
        dd = c.get("days") or {}
        if dd:
            out["accel"][camp] = dict(af=_num(dd.get("af")), lo=_num(dd.get("lo")), hi=_num(dd.get("hi")),
                                      bounded=bool(dd.get("bounded")), af_bound=_num(dd.get("af_bound")),
                                      bound_kind=dd.get("bound_kind"), median_ref=_num(dd.get("median_ref")),
                                      median_new=_num(dd.get("median_new")), hit_ref=_num(dd.get("hit_ref")),
                                      hit_new=_num(dd.get("hit_new")), n_ref=dd.get("n_ref"), n_new=dd.get("n_new"),
                                      ref=c.get("ref"), new=c.get("new"))
        cc = c.get("cost") or {}
        out["cost"][camp] = {canon_basis(k): dict(ratio=_num(v.get("ratio")), lo=_num(v.get("lo")),
                                                  hi=_num(v.get("hi")),
                                     bounded=bool(v.get("bounded")), ratio_bound=_num(v.get("ratio_bound")),
                                     median_ref=_num(v.get("median_ref")), median_new=_num(v.get("median_new")))
                             for k, v in cc.items() if isinstance(v, dict)}
        cases = ((js.get("cost_per_experiment") or {}).get("cases") or {}).get(camp) or {}
        rows = []
        for key, lab in CPE_CASES:
            v = cases.get(key)
            if isinstance(v, dict):
                rows.append((lab, {k: float(v.get("per", {}).get(k, 0.0)) for k in CPE_PARTS},
                             float(v.get("per_total", 0.0)), v.get("n")))
        out["per_experiment"][camp] = rows
    out["cpe_unit"] = (js.get("cost_per_experiment") or {}).get("unit", "experiment")
    st = (js.get("utilization") or {}).get("stations") or {}
    out["utilization"] = {k: float(v.get("util", 0.0)) for k, v in st.items() if isinstance(v, dict)}
    out["util_by_campaign"] = {k: v.get("by_campaign") for k, v in st.items() if isinstance(v, dict)}
    out["util_capex_weighted"] = _num((js.get("utilization") or {}).get("capex_weighted_mean"))
    ow = js.get("outside_work") or {}
    cap, dl = ow.get("capacity") or {}, ow.get("demand_limited") or {}
    out["outside"] = dict(jobs=_num(cap.get("jobs")), revenue=_num(cap.get("revenue")), net=_num(cap.get("net")),
                          net_x_depreciation=_num(cap.get("net_share_of_depreciation")),
                          net_x_fixed=_num(cap.get("net_share_of_fixed")), cap=_num(ow.get("cap")),
                          demand_h_week=_num(ow.get("demand_h_week")), dl_jobs=_num(dl.get("jobs")),
                          dl_revenue=_num(dl.get("revenue")), dl_net=_num(dl.get("net")),
                          dl_net_x_depreciation=_num(dl.get("net_share_of_depreciation")),
                          dl_net_x_fixed=_num(dl.get("net_share_of_fixed")),
                          stations={k: v for k, v in (cap.get("stations") or {}).items() if isinstance(v, dict)})
    out["headlines"] = [h for h in (js.get("headline") or []) if isinstance(h, str)]
    t = js.get("targets") or {}
    out["targets"] = t.get("values") or {}
    out["target_src"] = t.get("src", "")
    fac = js.get("facilities") or {}
    out["capex"] = {k: _num(v.get("capex")) for k, v in fac.items() if isinstance(v, dict)}
    return out


def headline(replay: Replay | None = None) -> dict:
    """X (times faster) and Y (share of the cost) per campaign. From econ_summary.json's chosen comparison when it
    has one (X = median days to the target, reference over new; Y per cost basis), else from the benchmark curves.
    Each value says where it came from."""
    E = econ(replay.policy if replay is not None else None)
    Bn = bench([replay] if replay is not None else None)
    tgt = Bn["target"]
    facs = {f for f, _ in Bn["groups"]}
    auto, conv = facility_keys(facs)
    pol = replay.policy if replay is not None else "cost_aware"
    out = dict(target=tgt, auto=auto, conv=conv, policy=pol, placeholder=Bn["placeholder"] and E["placeholder"],
               comparison=E.get("comparison"), basis=TAKEAWAY_BASIS)
    for camp in CAMPAIGNS:
        a = Bn["groups"].get((auto, pol), {}).get(camp, [])
        c = Bn["groups"].get((conv, pol), {}).get(camp, [])
        da, ha = first_hit(a, tgt[camp], 0)
        dc, hc = first_hit(c, tgt[camp], 0)
        sa, _ = first_hit(a, tgt[camp], 1)
        sc, _ = first_hit(c, tgt[camp], 1)
        row = dict(days_auto=da, days_conv=dc, usd_auto=sa, usd_conv=sc, hit_auto=ha, hit_conv=hc,
                   n_auto=len(a), n_conv=len(c),
                   accel=(dc / da) if (da and dc) else None, cost_ratio=(sa / sc) if (sa and sc) else None,
                   cost_ratio_capex=None, source="bench curves" if not Bn["placeholder"] else "placeholder runs")
        A = E["accel"].get(camp)
        if A:
            af = A["af"]
            row.update(accel=af if (af is not None and af != float("inf")) else A.get("af_bound"),
                       accel_at_least=bool(A.get("bounded") and A.get("bound_kind") == "lower"),
                       accel_lo=A["lo"], accel_hi=A["hi"], days_conv=A["median_ref"] if A["median_ref"] != float(
                           "inf") else None, days_auto=A["median_new"], hit_auto=A["hit_new"], hit_conv=A["hit_ref"],
                       n_auto=A["n_new"] or row["n_auto"], n_conv=A["n_ref"] or row["n_conv"], ref=A["ref"],
                       new=A["new"], accel_source="econ_summary.json", source="econ_summary.json")
        C = E["cost"].get(camp) or {}
        if C:
            row["costs"] = {k: C.get(k) for k, _ in COST_BASES if C.get(k)}
            op, full = C.get("op_alone") or {}, C.get("full_alone") or {}
            bk, yv, words = pick_basis(C)
            basis = C.get(bk) or {}
            row.update(cost_ratio=op.get("ratio") if op.get("ratio") is not None else op.get("ratio_bound"),
                       cost_ratio_capex=full.get("ratio") if full.get("ratio") is not None else full.get(
                           "ratio_bound"),
                       y=yv, y_basis=bk, y_words=words, y_shared=bk == "full at 60% utilization",
                       y_lo=basis.get("lo"), y_hi=basis.get("hi"),
                       usd_auto=(C.get("cash") or {}).get("median_new") or row["usd_auto"],
                       usd_conv=(C.get("cash") or {}).get("median_ref") or row["usd_conv"],
                       cost_ratio_source="econ_summary.json")
        out[camp] = row
    return out
