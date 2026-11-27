"""The alloys the experiments chapter follows, and what the twin's own models say about them (twin/video/exp_data.py).

    python -m twin.video.exp_data            # the two alloys and every number the chapter shows -> facts.json
    python -m twin.video.exp_data scheil     # the open-database Scheil run (pycalphad + scheil) -> scheil_open.json

**Which alloys.** One per campaign, read from the committed event logs of the runs the video replays
(``data.replay3b_parts()``: out/twin3b/like3b.json's median seeds): the design whose tensile (Al) or immersion (Cu)
result took that run's best-so-far past the target the run is the median seed for. In round 3b's replay that is
aluminium design 299 of seed 0 (day 96, the halfway target) and copper design 74 of seed 5 (day 221, the best
existing alloy). ``Alloy(campaign, seed, design, events)`` follows any other design of any other run (round 5's
continuous seed, for instance).

**Where every curve and map comes from.** The event logs hold a design's composition, its bookings and its true
utility, but no raw data and no process settings: the campaign's instruments run in their fast mode, which returns
numbers only. So the chapter makes the alloy again through the twin's own truth (``twin/truth_al.py``,
``twin/truth_cu.py``, with the run's seed, so it is the same hidden alloy) and measures it with the twin's own
instrument simulators at full fidelity (``twin/instruments``), which return the raw data a real instrument would:
micrographs, spectra, orientation maps, load records. Nothing here changes the engine; everything is seeded and
repeats. What that means for the numbers on screen:

* they are this alloy's, from the same models the benchmark runs, but **not the replayed run's own draws**; the
  true yield strength and elongation of the part made here are close to the log's (the same truth; other settings);
* the atomizer and laser settings are stated example settings (``AL_PROC``, ``CU_PROC`` of twin/instruments/micro.py
  and a 3 x 3 power x speed grid for the nine cubes), not the settings the campaign's policy chose.

``scheil_twin`` is the twin's dilute Scheil model (twin/thermo.py ``AlSolidification``) with the curve kept, which
``run()`` does not return; ``twin/tests/test_video_experiments.py`` checks it gives ``run()``'s numbers exactly.
``scheil_open`` is an independent calculation with pycalphad and scheil on MatCalc's open aluminium database, for the
elements that database has. ``melt_pool`` is the twin's stand-in for Thermo-Calc's AM Module: Rosenthal's moving
point source (twin/physics.py), with the field and a point's thermal history kept.
"""
from __future__ import annotations

import json
import math
import sys
import types
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import data as D

OUT = D.OUT3B / "video" / "experiments"          # the chapter's own files (its records are committed)
SCHEIL_JSON = OUT / "scheil_open.json"
FACTS_JSON = OUT / "facts.json"
CAMP_WORD = {"flaime_al": "aluminium", "onr_cu": "copper"}
SEED_SAMPLE = 0                                  # the lot's atomizer runs and the parts made from it
GRID_P = (150.0, 250.0, 350.0)                   # W: the nine cubes' laser powers ...
GRID_V = (600.0, 1000.0, 1700.0)                 # ... and scan speeds, mm/s (example settings, stated on screen)
BARS_AT = 4                                      # the cube the tensile blanks are printed beside: the middle setting
RNG = {"yield": 11, "psd": 12, "sem_powder": 13, "eds": 14, "density": 15, "sem_section": 16, "ebsd": 17,
       "vickers": 18, "pip": 19, "tensile": 20, "corrosion_screen": 21, "immersion": 22, "interim": 23, "cubes": 24,
       "sim_tc": 25, "sim_am": 26, "xrd_part": 27}


def _twin():
    sys.path.insert(0, str(D.HERE))
    import twin  # noqa: F401  (applies the numerical pin before numpy-heavy modules load)


# ------------------------------------------------------------------------------------------------ which alloys
@lru_cache(maxsize=8)
def _events(path: str) -> dict:
    return D._load_json(Path(path))


def follow() -> dict:
    """{campaign: {run, seed, design, day, target, events, composition, u_true, ys, el}}: the design that took each
    replayed run's best-so-far past the target that run is the median seed for (nothing typed in)."""
    out = {}
    for part in D.replay3b_parts():
        ev = _events(str(part["events"]))
        camp = part["campaign"]
        dem = [r for r in ev["results"] if r["campaign"] == camp and r["type"] == "demonstrated"
               and abs(r["u_true"] - r["best_true"]) < 1e-12 and r["u_true"] > 0]
        row = min(dem, key=lambda r: abs(r["t_h"] / D.HPD - float(part["day"])))
        comp = ev["designs"][camp][str(row["design"])]
        out[camp] = dict(run=ev["meta"]["run_id"], seed=int(part["seed"]), design=int(row["design"]),
                         day=row["t_h"] / D.HPD, target=part["target"], events=str(part["events"]),
                         composition=dict(comp), u_true=row["u_true"], ys=row["ys"], el=row["el"],
                         policy=ev["meta"]["cfg"]["policy"], hit=int(part["hit"]), of=int(part["of"]))
    return out


# ------------------------------------------------------------------------------------------------ one alloy
class Alloy:
    """One design of one run, made again through the twin's truth and measured at full fidelity. Everything is
    computed on first use and kept."""

    def __init__(self, campaign: str, seed: int, design: int, events: str, meta: dict | None = None):
        _twin()
        self.campaign, self.seed, self.design_id, self.events = campaign, int(seed), int(design), str(events)
        self.al = campaign == "flaime_al"
        self.base = "Al" if self.al else "Cu"
        self.meta = dict(meta or {})
        ev = _events(self.events)
        comp = dict(ev["designs"][campaign][str(design)])
        self.comp = {e: float(v) for e, v in comp.items()}                       # wt%, with the balance element
        self.design = {e: v for e, v in self.comp.items() if e != self.base}    # the additions only
        self._c: dict = {}

    # ---------------------------------------------------------------- the run it comes from
    def run_designs(self) -> dict:
        """Every design of this campaign in the run's log: {id: composition}, and which were made into powder
        (``made``), printed or deposited (``built``) and demonstrated (``shown``: id -> true utility)."""
        if "run_designs" not in self._c:
            ev = _events(self.events)
            c = self.campaign
            made = {r["design"] for r in ev["results"] if r["campaign"] == c and r["type"] == "lot"}
            built = {r["design"] for r in ev["results"] if r["campaign"] == c and r["type"] in ("build", "deposit")}
            shown = {r["design"]: r["u_true"] for r in ev["results"] if r["campaign"] == c
                     and r["type"] == "demonstrated"}
            self._c["run_designs"] = dict(designs={int(k): v for k, v in ev["designs"][c].items()}, made=made,
                                          built=built, shown=shown)
        return self._c["run_designs"]

    @property
    def space(self):
        from twin.spaces import SPACES
        return SPACES[self.campaign]

    @property
    def truth(self):
        if "truth" not in self._c:
            if self.al:
                from twin.truth_al import AlTruth
                self._c["truth"] = AlTruth(self.seed)
            else:
                from twin.truth_cu import CuTruth
                self._c["truth"] = CuTruth(self.seed)
        return self._c["truth"]

    @property
    def proc(self) -> dict:
        """The example settings: the instrument gallery's own (micro.AL_PROC / CU_PROC)."""
        from twin.instruments import micro
        return dict(micro.AL_PROC if self.al else micro.CU_PROC)

    # ---------------------------------------------------------------- the lot and the parts
    def _make(self):
        if "lot" in self._c:
            return
        from twin.instruments import micro
        lot, part = micro.make_samples(self.campaign, self.design, proc=self.proc, seed=SEED_SAMPLE, truth=self.truth)
        good = [r for r in lot["runs"] if not r["failed"]]
        w = np.array([max(r["usable_frac"] * r["cut_frac"], 1e-9) for r in good])
        w = w / w.sum()
        smp = dict(lot, campaign=self.campaign, design=dict(self.comp))          # as Campaign._lsample
        for k in ("d50_um", "cut_frac", "fines_frac", "gsd", "true_superheat_K"):
            smp[k] = float(sum(wi * r[k] for wi, r in zip(w, good)))
        self._c["lot"] = smp
        self._c["part0"] = dict(part, design=dict(self.comp))

    @property
    def lot(self) -> dict:
        self._make()
        return self._c["lot"]

    def _shim(self, fidelity="full", seed=0):
        """A stand-in for the Campaign whose methods measure a part (``_psample``, ``_soundness``, ``_interim``), so
        the chapter reports a part exactly as the campaign does, from the engine's own code."""
        from twin.campaign import Campaign
        sh = types.SimpleNamespace(key=self.campaign, truth=self.truth, fidelity=fidelity,
                                   rng=np.random.default_rng(seed), designs={0: dict(composition=dict(self.comp))},
                                   IMM_DAYS=Campaign.IMM_DAYS)
        sh._psample = lambda part, did, hot=False: Campaign._psample(sh, part, did, hot)
        sh._m = lambda name, sample, **kw: Campaign._m(sh, name, sample, **kw)
        sh._soundness = lambda part, did: Campaign._soundness(sh, part, did)
        sh._interim = lambda smp, meas: Campaign._interim(sh, smp, meas)
        return sh

    def cubes(self) -> list:
        """Aluminium: nine cubes of one build at GRID_P x GRID_V, each as the campaign reports a fresh part
        (Archimedes density and the section's image analysis, the lower of the two; cracks). Row-major, P outer."""
        if "cubes" not in self._c:
            assert self.al
            sh = self._shim("full", RNG["cubes"])
            lot = self.lot
            out = []
            for P in GRID_P:
                for v in GRID_V:
                    proc = dict(self.proc, P_W=P, v_mm_s=v)
                    part = self.truth.build(lot, proc, sh.rng)
                    part["reuse"] = 0.0
                    m = sh._soundness(part, 0)
                    mp = part["melt_pool"]
                    out.append(dict(P_W=P, v_mm_s=v, part=part, measured=m, true_density=part["rel_density"],
                                    kh=mp["kh"], lof=mp["lof"], W_um=mp["W_um"], D_um=mp["D_um"],
                                    cool_K_s=mp["cool"]))
            self._c["cubes"] = out
        return self._c["cubes"]

    @property
    def best(self) -> int:
        """The cube that is sectioned and whose setting the tensile blanks are printed at. In the campaign a build
        is up to nine density cubes at different settings and blanks at ONE of them, chosen before printing
        (twin/campaign.py ``bars_at``); here that is the middle setting of the grid."""
        return BARS_AT

    @property
    def densest(self) -> int:
        cs = self.cubes()
        return max(range(len(cs)), key=lambda i: cs[i]["measured"]["rel_density"])

    @property
    def part(self) -> dict:
        """The part the bars come from, as the instruments see it (Campaign._psample): aluminium, the cube at the
        setting the blanks are printed at (``best``); copper, the larger deposit."""
        if "part" not in self._c:
            sh = self._shim()
            if self.al:
                p = self.cubes()[self.best]["part"]
            else:
                self._make()
                p = {k: v for k, v in self._c["part0"].items() if k not in ("strength", "corrosion")}
            self._c["part"] = sh._psample(p, 0)
        return self._c["part"]

    # ---------------------------------------------------------------- the instruments, full fidelity
    def measure(self, name: str, **kw) -> dict:
        """One instrument's measurement with its raw data (``twin.instruments.measure(..., fidelity='full')``), on
        the lot (powder instruments) or on the part."""
        key = ("m", name, tuple(sorted(kw.items())))
        if key not in self._c:
            from twin import instruments as INS
            smp = self.lot if name in ("yield", "psd", "sem_powder", "eds", "xrd_powder", "xrf") else self.part
            self._c[key] = INS.measure(name, smp, self.campaign, np.random.default_rng(RNG[name]), "full", **kw)
        return self._c[key]

    def immersion(self) -> dict:
        """Copper: the 30-day immersion's record and the interim readings the campaign takes on the way
        (Campaign._interim, days 1, 3, 7 and 14)."""
        if "imm" not in self._c:
            final = self.measure("immersion")
            sh = self._shim("full", RNG["interim"])
            self._c["imm"] = dict(final=final, interim=sh._interim(self.part, final))
        return self._c["imm"]

    # ---------------------------------------------------------------- CALPHAD: what the nodes report
    def sims(self) -> dict:
        """What each simulation node of the twin reports for this alloy: ``open`` (the open-database node, the one
        every round 3b run used), ``tc`` (the Thermo-Calc stand-in), and for aluminium ``am`` (the AM Module
        stand-in at the best cube's settings); ``truth`` is the hidden thermodynamics."""
        if "sims" not in self._c:
            t = self.truth
            out = dict(open=t.sim_open(self.comp), tc=t.sim_tc(self.comp, np.random.default_rng(RNG["sim_tc"])),
                       truth=t.thermo(self.comp))
            if self.al:
                c = self.cubes()[self.best]
                out["am"] = t.sim_am(self.lot["composition"], dict(self.proc, P_W=c["P_W"], v_mm_s=c["v_mm_s"]),
                                     np.random.default_rng(RNG["sim_am"]))
            self._c["sims"] = out
        return self._c["sims"]

    def scheil(self) -> dict:
        """Aluminium: the twin's dilute Scheil curves, as the open-database node (``open``) and as the hidden truth
        (``truth``) see this alloy."""
        if "scheil" not in self._c:
            assert self.al
            self._c["scheil"] = dict(open=scheil_twin("open", self.comp), truth=scheil_twin("truth", self.comp))
        return self._c["scheil"]

    def melt_pool(self) -> dict:
        """Aluminium: the melt pool of the best cube's settings (see melt_pool())."""
        if "mp" not in self._c:
            assert self.al
            c = self.cubes()[self.best]
            self._c["mp"] = melt_pool(self.truth, self.lot["composition"],
                                      dict(self.proc, P_W=c["P_W"], v_mm_s=c["v_mm_s"]))
        return self._c["mp"]


@lru_cache(maxsize=4)
def alloy(campaign: str) -> Alloy:
    f = follow()[campaign]
    return Alloy(campaign, f["seed"], f["design"], f["events"], f)


# ------------------------------------------------------------------------------------------------ Scheil (the twin's)
def scheil_twin(kind: str, wt: dict) -> dict:
    """twin.thermo.AlSolidification(kind).run(wt), with the curve it reads its numbers from kept: T (degC) against
    fraction solid for the fcc matrix's solidification, the fraction solid at which each solute's eutectic starts,
    and the primary intermetallics above the matrix's liquidus. The same arithmetic, line for line; the test compares
    its numbers with run()'s."""
    _twin()
    from twin import thermo as TH
    sol = TH.AlSolidification(kind)
    fs = sol.FS
    T = np.full_like(fs, TH.AL_TM_C)
    used, eut_on, share_by, Q = {}, {}, {}, 0.0
    for el, c in wt.items():
        if el == "Al" or c <= 0 or el not in sol.params:
            continue
        k, m, _ = sol.params[el]
        used[el] = c
        c_eff = c
        prim = TH.AL_PRIMARY.get(el)
        if kind == "truth" and prim and c > prim[0] and prim[0] < TH.AL_EUTECTIC.get(el, (1e9,))[0]:
            c_eff = prim[0]
        if kind == "truth" and el == "Sc" and c > TH.AL_EUTECTIC["Sc"][0]:
            c_eff = TH.AL_EUTECTIC["Sc"][0]
        cl = c_eff * np.power(np.maximum(1 - fs, 1e-6), k - 1.0)
        cap = TH.AL_EUTECTIC.get(el)
        if cap and k < 1:
            hit = cl >= cap[0]
            if hit.any():
                f_on = float(fs[np.argmax(hit)])
                eut_on[el] = f_on
                share_by[el] = (1.0 - f_on) * cap[0] / TH.AL_EUT_PHASE_X.get(el, 1.0) / 100.0
            cl = np.minimum(cl, cap[0])
        T += m * cl
        Q += m * c_eff * (k - 1.0)
    floors = [TH.AL_EUTECTIC[e][1] for e in used if e in TH.AL_EUTECTIC]
    if floors:
        T = np.maximum(T, min(floors) - 10.0 * (len(floors) - 1))
    primary = {}
    if kind == "truth":
        for el, c in used.items():
            p = TH.AL_PRIMARY.get(el)
            if p and c > p[0]:
                primary[el] = dict(phase=p[4], T_C=p[1] + p[2] * (c - p[0]) ** p[3], excess_wt=c - p[0])
    i98 = int(np.searchsorted(fs, 0.98))
    r = np.sqrt(fs)
    sel = (r >= 0.87) & (r <= 0.94)
    slope, icpt = np.polyfit(r[sel], T[sel], 1)
    run = sol.run(dict(wt))
    eut_phase = {"Si": "Si", "Cu": "Al2Cu", "Mg": "Al3Mg2", "Zn": "Zn", "Fe": "Al13Fe4", "Mn": "Al6Mn", "Ni": "Al3Ni",
                 "Ce": "Al11Ce3", "Sc": "Al3Sc", "Er": "Al3Er", "Li": "AlLi", "Sn": "Sn"}
    return dict(kind=kind, fs=fs, T_C=T, T_alpha_liquidus_C=float(T[0]), T_98_C=float(T[min(i98, len(T) - 1)]),
                kou_index_K=float(abs(slope)), kou_fit=(float(slope), float(icpt)), kou_window=(0.87 ** 2, 0.94 ** 2),
                Q_K=float(Q), eutectic_on={e: dict(fs=f, phase=eut_phase.get(e, e), share=share_by[e])
                                            for e, f in eut_on.items()},
                primary=primary, elements=sorted(used), missing=sorted(e for e in wt if e != "Al" and wt[e] > 0
                                                                       and e not in sol.params), run=run)


# ------------------------------------------------------------------------------------------------ Scheil (open CALPHAD)
OPEN_DB = "mc_al"                               # MatCalc mc_al v2.037 (TU Wien, ODbL 1.0): twin/calphad.py TDBS
OPEN_HAS = ("Cr", "Cu", "Fe", "Mg", "Mn", "Ni", "Sc", "Si", "Ti", "Zn", "Zr")


def scheil_open_compute(wt: dict, step: float = 1.0) -> dict:
    """A Scheil-Gulliver solidification of the alloy with pycalphad and scheil on MatCalc's open aluminium database,
    for the elements that database has (the others are left out and named). Minutes on one core; its result is
    committed (scheil_open.json), so the chapter rebuilds without it."""
    _twin()
    import time
    import pycalphad
    import scheil
    from pycalphad import variables as v
    from pycalphad.core.utils import filter_phases, unpack_species
    from scheil import simulate_scheil_solidification
    from twin import calphad as CP
    keep = {e.upper(): float(c) for e, c in wt.items() if e in OPEN_HAS and c > 0}
    left = {e: float(c) for e, c in wt.items() if e != "Al" and c > 0 and e not in OPEN_HAS}
    db = CP.load_db(OPEN_DB, ["AL"] + list(keep))
    comp = dict(keep)
    comp["AL"] = 100.0 - sum(keep.values())
    x = CP.wt_to_x(comp)
    comps = sorted(x) + ["VA"]
    phases = filter_phases(db, unpack_species(db, comps), [p for p in CP.AL_PHASES if p in db.phases])
    t0 = time.time()
    res = simulate_scheil_solidification(db, comps, phases, {v.X(e): x[e] for e in x if e != "AL"},
                                         CP.AL_TM + 200.0, step_temperature=step)
    T = np.array(res.temperatures) - 273.15
    fl = np.array(res.fraction_liquid)
    cum = {ph: np.array(a) for ph, a in res.cum_phase_amounts.items() if np.max(a) > 1e-6}
    first = {ph: float(T[int(np.argmax(a > 1e-6))]) for ph, a in cum.items()}
    return dict(database="MatCalc mc_al v2.037 (TU Wien; ODbL 1.0)", sha256=CP.TDBS[OPEN_DB]["sha256"],
                tools=f"pycalphad {pycalphad.__version__}, scheil {scheil.__version__}",
                wt={e.capitalize(): c for e, c in keep.items()}, left_out=left, step_K=step,
                converged=bool(res.converged), seconds=round(time.time() - t0, 1),
                T_C=[round(float(t), 3) for t in T], fraction_solid=[round(float(1 - f), 6) for f in fl],
                phases={ph: [round(float(a), 6) for a in arr] for ph, arr in cum.items()},
                first_appears_C={ph: round(t, 2) for ph, t in first.items()})


def scheil_open(campaign: str = "flaime_al") -> dict | None:
    """The committed open-database Scheil run for the alloy followed, or None if it was made for another design."""
    if not SCHEIL_JSON.exists():
        return None
    d = json.loads(SCHEIL_JSON.read_text())
    a = alloy(campaign)
    if d.get("design") != a.design_id or d.get("run") != a.meta.get("run"):
        return None
    d["T_C"], d["fraction_solid"] = np.array(d["T_C"]), np.array(d["fraction_solid"])
    d["phases"] = {k: np.array(v) for k, v in d["phases"].items()}
    return d


# ------------------------------------------------------------------------------------------------ the melt pool
def rosenthal_T(xi, y, z, q, v, a, T0):
    """Rosenthal's thick-plate moving point source in the frame moving with it (source at the origin, travelling
    towards +xi): T = T0 + q / R exp(-v (R + xi) / (2 a)), q = A P / (2 pi k). Arrays broadcast."""
    R = np.sqrt(np.asarray(xi) ** 2 + np.asarray(y) ** 2 + np.asarray(z) ** 2)
    R = np.maximum(R, 1e-9)
    return T0 + q / R * np.exp(-v * (R + xi) / (2 * a))


def melt_pool(truth, comp: dict, proc: dict, probe_um: float | None = None) -> dict:
    """The twin's melt pool for an aluminium composition at LPBF settings (truth_al.AlTruth.melt_pool: Rosenthal's
    point source with the alloy's conductivity, density, liquidus and absorptivity), with what the twin's model
    does not keep: the temperature field on the surface and on the centre plane, and the thermal history of a point
    two layers under the track. ``twin`` holds the numbers the twin takes (width, depth, cooling rate, the lack-of-
    fusion and keyhole indices, the energy density)."""
    k, rho, cp, Tm, Tb, A = truth.props(comp)
    mp = truth.melt_pool(comp, proc)
    P, v = float(proc["P_W"]), float(proc["v_mm_s"]) * 1e-3
    T0 = float(proc["T0_C"]) + 273.15
    a = k / (rho * cp)
    q = A * P / (2 * math.pi * k)
    half = mp["W_um"] * 0.5e-6
    span = max(8 * half, 400e-6)
    xi = np.linspace(-2.6 * span, 0.5 * span, 520)
    yy = np.linspace(-0.62 * span, 0.62 * span, 208)
    zz = np.linspace(0.0, 0.62 * span, 104)
    top = rosenthal_T(xi[None, :], yy[:, None], 0.0, q, v, a, T0) - 273.15            # surface, degC
    side = rosenthal_T(xi[None, :], 0.0, zz[:, None], q, v, a, T0) - 273.15           # centre plane, degC
    zp = (2.0 * float(proc["t_um"]) if probe_um is None else probe_um) * 1e-6             # two layers down
    t = np.linspace(-0.25e-3, 1.75e-3, 1200)                                           # s; the laser passes at t = 0
    hist = rosenthal_T(-v * t, 0.0, zp, q, v, a, T0) - 273.15
    cooling = np.gradient(hist, t)
    after = np.argmax(hist)
    below = np.nonzero(hist[after:] <= Tm - 273.15)[0]
    i_liq = after + int(below[0]) if len(below) else None
    return dict(xi_um=xi * 1e6, y_um=yy * 1e6, z_um=zz * 1e6, top_C=top, side_C=side, liquidus_C=Tm - 273.15,
                boil_C=Tb - 273.15, T0_C=T0 - 273.15, t_ms=t * 1e3, hist_C=hist, probe_um=zp * 1e6,
                hist_peak_C=float(hist.max()), i_liquidus=i_liq,
                hist_cool_K_s=None if i_liq is None else float(-cooling[i_liq]),
                twin=dict(W_um=mp["W_um"], D_um=mp["D_um"], cool_K_s=mp["cool"], kh=mp["kh"], lof=mp["lof"],
                          Ev_J_mm3=mp["Ev"]),
                props=dict(k_W_mK=k, rho_kg_m3=rho, cp_J_kgK=cp, absorptivity=A), proc=dict(proc))


# ------------------------------------------------------------------------------------------------ the numbers
def _r(v, n=3):
    return None if v is None else round(float(v), n)


def facts() -> dict:
    """Every number the chapter shows or speaks, by path (written to facts.json; the narration's ``nums`` point
    here, and the test compares them)."""
    f = follow()
    al, cu = alloy("flaime_al"), alloy("onr_cu")
    out = {"follow": {c: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items() if k != "events"}
                      for c, d in f.items()}}
    for a in (al, cu):
        rd = a.run_designs()
        out.setdefault("run", {})[a.campaign] = dict(designs=len(rd["designs"]), made=len(rd["made"]),
                                                     built=len(rd["built"]), demonstrated=len(rd["shown"]),
                                                     elements=len(a.space.bounds), in_design=len(a.design))
    # aluminium
    s, sc, mp = al.sims(), al.scheil(), al.melt_pool()
    cubes = al.cubes()
    b = cubes[al.best]
    ten, ps, sp, eb, sx = (al.measure(n) for n in ("tensile", "psd", "sem_powder", "ebsd", "sem_section"))
    yl = al.measure("yield")
    op = scheil_open()
    out["al"] = dict(
        open=dict(liquidus_C=_r(s["open"]["liquidus_C"], 1), kou_K=_r(s["open"]["kou_K"], 1),
                  range_K=_r(s["open"]["freezing_range_K"], 1), Q_K=_r(s["open"]["Q_K"], 1),
                  missing=sc["open"]["missing"]),
        truth=dict(liquidus_C=_r(s["truth"]["T_liquidus_C"], 1), alpha_liquidus_C=_r(s["truth"]["T_alpha_liquidus_C"], 1),
                   kou_K=_r(s["truth"]["kou_index_K"], 1), range_K=_r(s["truth"]["freezing_range_K"], 1),
                   Q_K=_r(s["truth"]["Q_K"], 1),
                   primary={e: dict(phase=p["phase"], T_C=_r(p["T_C"], 1)) for e, p in s["truth"]["primary"].items()}),
        scheil_open=None if op is None else dict(
            first_solid_C=_r(float(op["T_C"][int(np.argmax(op["fraction_solid"] > 1e-4))]), 1),
            end_C=_r(float(op["T_C"][-1]), 1), phases=sorted(op["phases"]), left_out=op["left_out"],
            converged=op["converged"], seconds=op["seconds"]),
        am=dict(P_W=b["P_W"], v_mm_s=b["v_mm_s"], h_um=al.proc["h_um"], t_um=al.proc["t_um"], T0_C=al.proc["T0_C"],
                W_um=_r(mp["twin"]["W_um"], 0), D_um=_r(mp["twin"]["D_um"], 0), kh=_r(mp["twin"]["kh"], 2),
                lof=_r(mp["twin"]["lof"], 2), cool_K_s=_r(mp["twin"]["cool_K_s"], 0),
                cool_MK_s=_r(mp["twin"]["cool_K_s"] / 1e6, 1), probe_um=_r(mp["probe_um"], 0),
                probe_peak_C=_r(mp["hist_peak_C"], 0), liquidus_C=_r(mp["liquidus_C"], 0),
                node=dict(W_um=_r(s["am"]["width_um"], 0), D_um=_r(s["am"]["depth_um"], 0),
                          lof=_r(s["am"]["lof_index"], 2), kh=_r(s["am"]["keyhole_index"], 2),
                          cool_K_s=_r(s["am"]["cooling_K_s"], 0))),
        powder=dict(runs=len(al.lot["runs"]), failed=sum(r["failed"] for r in al.lot["runs"]),
                    superheat_K=al.proc["superheat_K"], pour_mbar=al.proc["pour_mbar"],
                    d10_um=_r(ps["d10_um"], 0), d50_um=_r(ps["d50_um"], 0), d90_um=_r(ps["d90_um"], 0),
                    cut_frac_pct=_r(100 * ps["cut_frac"], 0), cut=list(ps["raw"]["cut"]),
                    charge_g=_r(yl["charge_g"], 0), collected_g=_r(yl["collected_g"], 0), cut_g=_r(yl["cut_g"], 0),
                    yield_pct=_r(100 * yl["yield_frac"], 0), cut_yield_pct=_r(100 * yl["cut_yield_frac"], 0),
                    sphericity=_r(sp["sphericity"], 2), satellite_pct=_r(100 * sp["satellite_frac"], 1),
                    particles=int(sp["n_particles"]), oxygen_ppm=_r(al.lot["oxygen_ppm"], 0)),
        cubes=[dict(P_W=c["P_W"], v_mm_s=c["v_mm_s"], density_pct=_r(100 * c["measured"]["rel_density"], 2),
                    true_pct=_r(100 * c["true_density"], 2), crack=_r(c["measured"]["crack_density"], 3),
                    kh=_r(c["kh"], 2), lof=_r(c["lof"], 2)) for c in cubes],
        best=dict(index=al.best, P_W=b["P_W"], v_mm_s=b["v_mm_s"],
                  density_pct=_r(100 * b["measured"]["rel_density"], 2), crack=_r(b["measured"]["crack_density"], 3),
                  true_pct=_r(100 * b["true_density"], 2), true_crack=_r(b["part"]["crack_density"], 3)),
        densest=dict(index=al.densest, P_W=cubes[al.densest]["P_W"], v_mm_s=cubes[al.densest]["v_mm_s"],
                     density_pct=_r(100 * cubes[al.densest]["measured"]["rel_density"], 2)),
        gates=dict(density_pct=99.5, crack=0.05),
        section=dict(porosity_pct=_r(100 * sx["porosity"], 2), cracks=int(sx["n_cracks"]), pores=int(sx["n_pores"]),
                     crack_density=_r(sx["crack_density"], 3), pore_dmax_um=_r(sx["pore_dmax_um"], 0)),
        ebsd=dict(grain_um=_r(eb["grain_um"], 1), equiaxed_pct=_r(100 * eb["equiaxed_frac"], 0),
                  texture_mrd=_r(eb["texture_mrd"], 1), indexed_pct=_r(100 * eb["indexed_frac"], 0),
                  step_um=_r(eb["raw"]["step_um"], 2)),
        tensile=dict(ys_MPa=_r(ten["ys_MPa"], 0), uts_MPa=_r(ten["uts_MPa"], 0), el_pct=_r(ten["el_pct"], 1),
                     E_GPa=_r(ten["E_GPa"], 0), bars=int(ten["n_bars"]),
                     truth_ys=_r(al.part["strength"]["ys_MPa"], 0), truth_el=_r(al.part["strength"]["el_pct"], 1)))
    # copper
    scr, imm = cu.measure("corrosion_screen"), cu.immersion()
    cs = cu.sims()
    tc = cu.measure("tensile")
    out["cu"] = dict(
        open=dict(liquidus_C=_r(cs["open"]["liquidus_C"], 0), range_K=_r(cs["open"]["freezing_range_K"], 0),
                  beta_900=_r(cs["open"]["beta_900"], 3), kappa_700_pct=_r(100 * cs["open"]["kappa_700"], 1)),
        proc=cu.proc,
        part=dict(density_pct=_r(100 * cu.part["rel_density"], 2), beta_prime=_r(cu.part["beta_prime"], 3),
                  ys_MPa=_r(tc["ys_MPa"], 0), el_pct=_r(tc["el_pct"], 1)),
        screen=dict(ocp_mV=_r(scr["ocp_mV"], 0), rp_kohm_cm2=_r(scr["rp_ohm_cm2"] / 1000, 1),
                    icorr_uA_cm2=_r(scr["icorr_uA_cm2"], 1), early_um_yr=_r(scr["early_rate_um_yr"], 0),
                    Eb_mV=_r(scr["Eb_mV"], 0), minutes=60),
        immersion=dict(days=30, rate30_um_yr=_r(imm["final"]["rate30_um_yr"], 1),
                       mass_loss_mg=_r(imm["final"]["raw"]["mass_loss_mg"], 1),
                       attack_um=_r(imm["final"]["attack_um"], 1),
                       interim={str(d): dict(mass_mg=_r(m["mass_change_mg"], 2), rate_um_yr=_r(m["rate_um_yr"], 1))
                                for d, m in imm["interim"].items()},
                       true_rate_um_yr=_r(cu.part["corrosion"]["rate_um_yr"], 1)))
    # what round 3b's runs bought from the simulation nodes
    out["sim_kinds"] = sim_kinds()
    return out


def sim_kinds() -> dict:
    """How often each simulation node ran in round 3b's committed event logs, and how many hot tensile tests were
    booked (kept in facts.json: reading all 436 logs takes a minute). Every call is the open-database node; no run
    bought the Thermo-Calc or AM-Module nodes."""
    if FACTS_JSON.exists():
        have = json.loads(FACTS_JSON.read_text()).get("sim_kinds")
        if have and "hot_tests" in have:
            return have
    n, kinds, hot = 0, {}, 0
    for p in sorted(D.EVENTS_DIR.glob("*.json*")):
        ev = D._load_json(p)
        n += 1
        for e in ev["events"]:
            if e["station"] == "hpc":
                kinds[e["what"]] = kinds.get(e["what"], 0) + 1
            elif e["station"] == "tensile_hot":
                hot += 1
    return dict(logs=n, calls=kinds, hot_tests=hot)


_FACTS: dict = {}


def load_facts() -> dict:
    """facts(), from the committed facts.json when it is for the alloys followed (a segment needs a few numbers, not
    every instrument run); computed and written otherwise."""
    if not _FACTS:
        if FACTS_JSON.exists():
            d = json.loads(FACTS_JSON.read_text())
            f = follow()
            if all(d.get("follow", {}).get(c, {}).get("design") == f[c]["design"]
                   and d["follow"][c].get("run") == f[c]["run"] for c in f):
                _FACTS.update(d)
        if not _FACTS:
            _FACTS.update(json.loads(json.dumps(write_facts(), default=str)))
    return _FACTS


def write_facts() -> dict:
    f = facts()
    OUT.mkdir(parents=True, exist_ok=True)
    FACTS_JSON.write_text(json.dumps(f, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o)) + "\n")
    return f


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "facts"
    if cmd == "scheil":
        a = alloy("flaime_al")
        r = scheil_open_compute(a.comp, float(sys.argv[2]) if len(sys.argv) > 2 else 1.0)
        r.update(design=a.design_id, run=a.meta.get("run"), composition=a.comp)
        OUT.mkdir(parents=True, exist_ok=True)
        SCHEIL_JSON.write_text(json.dumps(r) + "\n")
        print(f"{SCHEIL_JSON}: {len(r['T_C'])} steps, {r['seconds']} s, converged {r['converged']}, phases "
              f"{r['first_appears_C']}, left out {r['left_out']}")
    else:
        f = write_facts()
        print(json.dumps(f, indent=1)[:6000])
