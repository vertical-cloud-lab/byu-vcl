"""The two search spaces, as the proposals define them, plus the process settings each campaign tunes.

**FLAIME (aluminium, LPBF).** DAL ``consolidation-2``: ``genesis-mission-proposal/flaime-genesis-proposal.tex``
(Activity 1: "Al + Mn, Cr, Zr, Mg, Si, Cu, Ti, Fe, Ni, Ce, Sc, Li, Er, Zn, Sn") with the per-element bounds of
``figures/dag-thumbnails/periodic-table/alloy_element_bounds.csv`` ("Recommended upper bound"), Al >= 85 wt%, and the
joint caps that file recommends: Mg + Zn + Li <= 10, Cu + Mg <= 5, Sc + Zr <= 1.5 (conservative), and an activity
floor of 0.05 wt% for an element that is on. FLAIME's subsystems run from ternary to 9-component (k = 2..8 alloying
elements), which is how ``sample`` draws: pick k, pick which elements, then their amounts.

**ONR YIP (copper, blown-powder DED).** DAL PR 117 ``onr-yip-technical-proposal-cu-ded.tex``, Table "tab:space":
Ni 0-30, Al 0-9.5, Fe 0-4.5, Mn 0-4, Cr 0-0.7, Si 0-0.5, Nb 0-0.8, Ti 0-0.5 wt%, Cu the balance at >= 65 %, with its
rules: Cr and Nb only where Al <= 3; Si above 0.1 only with Nb (and only where Al <= 3); above 7 % Al, Ni >= Fe; below
1.5 % Al, Fe <= 2.3. The calculated-liquidus cap (<= 1250 degC) is a black-box constraint: the CALPHAD node predicts
it and the atomizer enforces it (twin/truth.py).

Process settings (both from the proposals' text; ranges from the machines' published limits, cited in
notes/twin.md): the atomizer's melt superheat, pour pressure and plate amplitude ("the search's atomizer settings are
now melt temperature, pour pressures and plate amplitude", DAL PR 117 README); LPBF power, speed, hatch, layer and
plate temperature on an Aconity MIDI (200-1000 W fibre laser); DED power, travel speed and powder feed rate on an
InssTek MX-Lab (500 W) or a FormAlloy X2.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Var:
    name: str
    lo: float
    hi: float
    unit: str = ""
    log: bool = False
    note: str = ""

    def from_unit(self, u):
        u = np.clip(u, 0.0, 1.0)
        if self.log:
            return math.exp(math.log(self.lo) + u * (math.log(self.hi) - math.log(self.lo)))
        return self.lo + u * (self.hi - self.lo)

    def to_unit(self, x):
        if self.log:
            return (math.log(x) - math.log(self.lo)) / (math.log(self.hi) - math.log(self.lo))
        return (x - self.lo) / (self.hi - self.lo)


@dataclass
class Space:
    """A composition (wt%, `balance` element as the remainder) plus process settings."""
    key: str
    balance: str
    bounds: dict                       # element -> (lo, hi) wt%
    min_balance: float
    process: list = field(default_factory=list)
    k_range: tuple = (1, 8)            # alloying elements switched on
    floor: float = 0.05                # wt%, an element that is on is at least this
    rules: list = field(default_factory=list)       # (text, fn(comp) -> bool)
    source: str = ""

    @property
    def elements(self) -> list:
        return list(self.bounds)

    @property
    def dim(self) -> int:
        return len(self.bounds) + len(self.process)

    def names(self) -> list:
        return self.elements + [v.name for v in self.process]

    # ------------------------------------------------------------------ encoding for optimizers: a vector in [0, 1]^d
    def encode(self, design: dict) -> np.ndarray:
        u = [design.get(e, 0.0) / self.bounds[e][1] for e in self.elements]
        u += [v.to_unit(design[v.name]) for v in self.process]
        return np.clip(np.array(u, float), 0, 1)

    def decode(self, u) -> dict:
        u = np.clip(np.asarray(u, float), 0, 1)
        d = {e: float(u[i] * self.bounds[e][1]) for i, e in enumerate(self.elements)}
        for j, v in enumerate(self.process):
            d[v.name] = float(v.from_unit(u[len(self.elements) + j]))
        return self.repair(d)

    def composition(self, design: dict) -> dict:
        c = {e: float(design.get(e, 0.0)) for e in self.elements if design.get(e, 0.0) > 0}
        c[self.balance] = 100.0 - sum(c.values())
        return c

    def check(self, design: dict) -> list:
        """The rules a design breaks (empty: feasible)."""
        bad = []
        for e, (lo, hi) in self.bounds.items():
            w = design.get(e, 0.0)
            if w < -1e-9 or w > hi + 1e-9:
                bad.append(f"{e} outside {lo}-{hi}")
            if 0 < w < self.floor - 1e-9:
                bad.append(f"{e} below the {self.floor} wt% activity floor")
        if 100.0 - sum(design.get(e, 0.0) for e in self.elements) < self.min_balance - 1e-9:
            bad.append(f"{self.balance} below {self.min_balance}")
        for text, fn in self.rules:
            if not fn(design):
                bad.append(text)
        return bad

    def repair(self, d: dict) -> dict:
        """Project onto the rules: zero sub-floor amounts, enforce conditional rules, scale solutes to fit the caps."""
        d = dict(d)
        for e in self.elements:
            lo, hi = self.bounds[e]
            w = min(max(d.get(e, 0.0), 0.0), hi)
            d[e] = 0.0 if w < self.floor else w
        d = self._fix(d)
        tot = sum(d[e] for e in self.elements)
        cap = 100.0 - self.min_balance
        if tot > cap:
            s = cap / tot
            for e in self.elements:
                d[e] = d[e] * s if d[e] * s >= self.floor else 0.0
        return d

    def _fix(self, d):
        return d

    def sample(self, n: int, seed: int = 0, kind: str = "random") -> list:
        """Feasible designs. Each: k alloying elements switched on (k uniform in k_range), amounts uniform between
        the floor and the bound, process settings uniform (or log-uniform), then repaired and re-drawn until it
        breaks no rule. kind='sobol' uses a scrambled Sobol sequence for the amounts and process settings."""
        rng = np.random.default_rng(seed)
        sob = None
        if kind == "sobol":
            from scipy.stats import qmc
            sob = qmc.Sobol(self.dim, scramble=True, seed=seed)
        out, tries = [], 0
        while len(out) < n and tries < 200 * n:
            tries += 1
            u = sob.random(1)[0] if sob is not None else rng.random(self.dim)
            k = int(rng.integers(self.k_range[0], min(self.k_range[1], len(self.elements)) + 1))
            on = set(rng.choice(self.elements, size=k, replace=False))
            d = {}
            for i, e in enumerate(self.elements):
                lo, hi = self.bounds[e]
                d[e] = (self.floor + u[i] * (hi - self.floor)) if e in on else 0.0
            for j, v in enumerate(self.process):
                d[v.name] = float(v.from_unit(u[len(self.elements) + j]))
            d = self.repair(d)
            if not self.check(d):
                out.append(d)
        return out


# ------------------------------------------------------------------------------------------------------------ FLAIME (Al)
AL_BOUNDS = {"Mn": (0, 5.0), "Cr": (0, 3.0), "Zr": (0, 1.0), "Mg": (0, 5.0), "Si": (0, 12.0), "Cu": (0, 4.0),
             "Ti": (0, 0.5), "Fe": (0, 0.5), "Ni": (0, 0.5), "Ce": (0, 6.0), "Sc": (0, 0.8), "Li": (0, 2.0),
             "Er": (0, 0.5), "Zn": (0, 8.0), "Sn": (0, 0.1)}


class AlSpace(Space):
    def _fix(self, d):
        for group, cap in ((("Mg", "Zn", "Li"), 10.0), (("Cu", "Mg"), 5.0), (("Sc", "Zr"), 1.5)):
            tot = sum(d[e] for e in group)
            if tot > cap:
                for e in group:
                    d[e] *= cap / tot
        return d


ATOMIZER = [
    Var("superheat_K", 50.0, 250.0, "K", note="melt temperature above the liquidus at the pour"),
    Var("pour_mbar", 100.0, 400.0, "mbar", note="argon over-pressure that drives the melt through the nozzle "
                                                  "(the lab's runs used 200 mbar; notes/alloy_atomize.md)"),
    Var("amplitude", 0.3, 1.0, "of max", note="sonotrode amplitude, as a share of the generator's maximum"),
]
LPBF = [
    Var("P_W", 100.0, 400.0, "W", note="laser power on the Aconity MIDI (200-1000 W source; Al runs 150-400 W)"),
    Var("v_mm_s", 200.0, 2000.0, "mm/s", log=True),
    Var("h_um", 60.0, 160.0, "um", note="hatch spacing"),
    Var("t_um", 20.0, 60.0, "um", note="layer thickness"),
    Var("T0_C", 25.0, 200.0, "degC", note="build plate temperature"),
]
DED = [
    Var("P_W", 200.0, 1000.0, "W", note="the MX-Lab's source is 500 W; the X2 reaches higher (DAL PR 117)"),
    Var("v_mm_min", 200.0, 1500.0, "mm/min", log=True, note="travel speed"),
    Var("feed_g_min", 2.0, 12.0, "g/min", note="powder feed rate"),
]

AL = AlSpace(
    key="flaime_al", balance="Al", bounds=AL_BOUNDS, min_balance=85.0, process=ATOMIZER + LPBF, k_range=(2, 8),
    rules=[("Mg + Zn + Li <= 10", lambda d: d["Mg"] + d["Zn"] + d["Li"] <= 10.0 + 1e-9),
           ("Cu + Mg <= 5", lambda d: d["Cu"] + d["Mg"] <= 5.0 + 1e-9),
           ("Sc + Zr <= 1.5", lambda d: d["Sc"] + d["Zr"] <= 1.5 + 1e-9)],
    source="DAL consolidation-2: flaime-genesis-proposal.tex; alloy_element_bounds.csv (recommended upper bounds)")


# ---------------------------------------------------------------------------------------------------------- ONR YIP (Cu)
CU_BOUNDS = {"Ni": (0, 30.0), "Al": (0, 9.5), "Fe": (0, 4.5), "Mn": (0, 4.0), "Cr": (0, 0.7), "Si": (0, 0.5),
             "Nb": (0, 0.8), "Ti": (0, 0.5)}


class CuSpace(Space):
    def _fix(self, d):
        if d["Al"] > 3.0:                       # Cr, Nb (and so Si) only in the Cu-Ni family
            d["Cr"] = d["Nb"] = d["Si"] = 0.0
        if d["Si"] > 0.1 and d["Nb"] <= 0.0:
            d["Si"] = 0.1 if d["Si"] >= self.floor else 0.0
        if d["Al"] > 7.0 and d["Ni"] < d["Fe"]:
            d["Ni"] = d["Fe"]
        if d["Al"] < 1.5 and d["Fe"] > 2.3:
            d["Fe"] = 2.3
        return d


CU = CuSpace(
    key="onr_cu", balance="Cu", bounds=CU_BOUNDS, min_balance=65.0, process=ATOMIZER + DED, k_range=(1, 6),
    rules=[("Cr and Nb only where Al <= 3", lambda d: d["Al"] <= 3.0 or (d["Cr"] == 0 and d["Nb"] == 0)),
           ("Si only where Al <= 3", lambda d: d["Al"] <= 3.0 or d["Si"] == 0),
           ("Si above 0.1 only with Nb", lambda d: d["Si"] <= 0.1 + 1e-9 or d["Nb"] > 0),
           ("above 7 % Al, Ni >= Fe", lambda d: d["Al"] <= 7.0 or d["Ni"] >= d["Fe"] - 1e-9),
           ("below 1.5 % Al, Fe <= 2.3", lambda d: d["Al"] >= 1.5 or d["Fe"] <= 2.3 + 1e-9)],
    source="DAL PR 117: onr-yip-technical-proposal-cu-ded.tex, Table tab:space and the rules after it")

SPACES = {"flaime_al": AL, "onr_cu": CU}

# Reference alloys each campaign starts from or compares against (nominal wt%, balance the base element).
REFERENCE = {
    "flaime_al": {
        "AlSi10Mg": {"Si": 10.0, "Mg": 0.35},
        "Al-Mn-Cr-Zr": {"Mn": 3.6, "Cr": 0.5, "Zr": 0.9},
        "Al-Zr": {"Zr": 1.0},
        "Scalmalloy": {"Mg": 4.6, "Sc": 0.7, "Zr": 0.3},
    },
    "onr_cu": {
        "C71500 70-30 Cu-Ni": {"Ni": 30.0, "Fe": 0.6, "Mn": 0.6},
        "C70600 90-10 Cu-Ni": {"Ni": 10.0, "Fe": 1.4, "Mn": 0.8},
        "C95800 NAB": {"Al": 9.2, "Ni": 4.5, "Fe": 4.0, "Mn": 1.2},
    },
}
