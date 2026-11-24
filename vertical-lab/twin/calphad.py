"""The CALPHAD layer: open databases through pycalphad, with Thermo-Calc behind the same interface.

    python3 -m twin.calphad al-dilute          # Al corner: each solute's liquidus slope m and partition coefficient
                                               #   k (mc_al, COST 507) -> data/al_dilute.json            (~2 min)
    python3 -m twin.calphad al-scheil          # Scheil runs on reference Al alloys -> data/al_scheil_ref.json
    python3 -m twin.calphad cu-design [N]      # equilibrium over N Sobol compositions of the copper space
                                               #   (mc_ni) -> data/cu_calphad.json                    (~10 min)
    python3 -m twin.calphad cu-ref             # the three reference Cu alloys, as a check against DAL's numbers

**Databases** (downloaded on first use into $TWIN_CACHE/tdb and checked by sha256; none is committed):

| key | file | covers | licence |
|---|---|---|---|
| mc_al | MatCalc mc_al v2.037 (TU Wien, Povoden-Karadeniz) | Al with Cr Cu Fe Mg Mn Ni Sc Si Ti Zn Zr | ODbL 1.0 |
| mc_ni | MatCalc mc_ni v2.036 | Cu-Ni-Al-Fe-Mn and Cr Si Nb Ti (built for Ni alloys) | ODbL 1.0 |
| cost507 | COST 507 Round II (1999), the copy bundled with pycalphad | Al with Ce, Li, Sn (and others) | "may be used freely" |

The FLAIME palette's erbium is in none of them; its Al-corner values come from the binary diagram (cited in
data/al_dilute.json) and are marked so. MatCalc's TDB syntax is converted for pycalphad by ``clean_tdb_text``, copied
from DAL's ``near-term-submissions/onr-yip/pycalphad-cu/run_calphad.py`` (MIT, same organization), which changes no
number.

**Thermo-Calc.** FLAIME and the ONR proposal both name TC-Python with TCAL and TCCU on BYU's HPC licence. That
cannot run on a CI runner. ``ThermoCalcBackend`` has the calls the twin needs (Scheil with back diffusion, equilibrium
phase fractions) so the same twin can use them where the licence is; until it runs, its outputs are the open-database
results plus the structured error the twin assigns to "TC-Python" nodes (twin/truth.py), which is what a benchmark
needs: the optimizer sees a simulator that is better than the open one and still not the truth.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.request
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CACHE = Path(os.environ.get("TWIN_CACHE", "/tmp/twin_cache")) / "tdb"
MATCALC = "https://www.matcalc.at/images/stories/Download/Database/"
TDBS = {
    "mc_al": dict(file="mc_al_v2037.tdb", url=MATCALC + "mc_al_v2037.tdb",
                  sha256="87ec595f2caae189227ed11d5598c899b436b866ccfefea91304ca57188817c4"),
    "mc_ni": dict(file="mc_ni_v2036.tdb", url=MATCALC + "mc_ni_v2036.tdb",
                  sha256="84ba813156e1f7d8bde495d74420319afec03572b981f6b56103807f305313ab"),
}
COST507_SHA256 = "6565f4d67695fbbf779d68b9eeeb83e86e44a1a3dde9bafd612d99daffb9c34d"
P0 = 101325.0
MW = dict(AL=26.9815385, CU=63.546, FE=55.845, MN=54.938044, NI=58.6934, CR=51.9961, SI=28.0855, NB=92.90637,
          TI=47.867, ZR=91.224, MG=24.305, ZN=65.38, SC=44.955908, CE=140.116, LI=6.94, SN=118.71, ER=167.259)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tdb_path(key: str) -> Path:
    if key == "cost507":
        import pycalphad
        p = Path(pycalphad.__file__).parent / "tests" / "databases" / "COST507.tdb"
        if _sha(p) != COST507_SHA256:
            print(f"warning: {p} differs from the COST 507 copy DAL checked (sha256)", file=sys.stderr)
        return p
    meta = TDBS[key]
    p = CACHE / meta["file"]
    if not p.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(meta["url"], headers={"User-Agent": "Mozilla/5.0 (twin.calphad)"})
        with urllib.request.urlopen(req, timeout=120) as r:
            p.write_bytes(r.read())
    if _sha(p) != meta["sha256"]:
        raise RuntimeError(f"{p}: sha256 mismatch (expected {meta['sha256']})")
    return p


# ------------------------------------------------------------------------------------------------- MatCalc -> pycalphad
# clean_tdb_text: copied from DAL near-term-submissions/onr-yip/pycalphad-cu/run_calphad.py (branch
# claude/onr-yip-fy27, MIT). Syntax only; no number is changed.
KEEP = {"ELEMENT", "SPECIES", "FUNCTION", "TYPE_DEFINITION", "PHASE", "CONSTITUENT", "PARAMETER",
        "TEMP_LIM", "DEFINE_SYSTEM_DEFAULT", "DEFAULT_COMMAND"}
ABBREV = {"PARA": "PARAMETER", "PARAM": "PARAMETER", "FUNC": "FUNCTION", "FUNCT": "FUNCTION",
          "CONST": "CONSTITUENT", "TYPE_DEF": "TYPE_DEFINITION", "ELEM": "ELEMENT", "SPEC": "SPECIES"}
PARAM_TYPES = {"G", "L", "TC", "BMAGN"}
PARAM_RE = re.compile(r"^PARAMETER\s+(\w+)\(\s*([^,;:()]+?)\s*,\s*([^;()]+?)\s*;\s*(\d+)\s*\)\s")


def clean_tdb_text(raw: str, elements=None) -> str:
    keep_el = None if elements is None else {e.upper() for e in elements} | {"VA", "*"}
    txt = raw.replace("\r", "").encode("ascii", "ignore").decode("ascii")
    lines = [l.split("$", 1)[0] for l in txt.split("\n")]
    cmds = []
    for c in " ".join(lines).split("!"):
        cmds.extend(re.split(r"\s(?=PARAMETER\s+\w+\()", c))
    order_disorder, used = {}, set()
    for c in cmds:
        t = c.split()
        if len(t) == 4 and t[0].upper() == "ATTACH_CONTRIBUTION" and t[3].upper() == "ORDER_DISORDER":
            order_disorder[t[1].upper()] = t[2].upper()
        if len(t) > 2 and t[0].upper() == "PHASE":
            used.update(t[2])
    free = [ch for ch in "QXZJKUWY1234567" if ch not in used]
    od_char, out = {}, []
    for ordered, disordered in order_disorder.items():
        od_char[ordered] = free.pop(0)
        out.append(f"TYPE_DEFINITION {od_char[ordered]} GES A_P_D {ordered} DIS_PART {disordered} !")
    for c in cmds:
        c = re.sub(r"\s+", " ", c).strip()
        if not c:
            continue
        kw = ABBREV.get(c.split(" ", 1)[0].upper(), c.split(" ", 1)[0].upper())
        if kw not in KEEP:
            continue
        c = kw + c[len(c.split(" ", 1)[0]):]
        if kw in ("PHASE", "CONSTITUENT"):
            c = c.split(">", 1)[0].strip()
        if kw == "PHASE":
            t = c.split()
            if t[1].upper() in od_char:
                t[2] += od_char[t[1].upper()]
                c = " ".join(t)
        if kw == "PARAMETER":
            m = PARAM_RE.match(c)
            if not m:
                toks = set(re.findall(r"[A-Z][A-Z]?", c.split(")", 1)[0].split("(", 1)[-1].upper()))
                if keep_el is not None and not toks <= keep_el:
                    continue
                raise ValueError("malformed PARAMETER in the requested subsystem: " + c[:120])
            if m.group(1).upper() not in PARAM_TYPES:
                continue
            if keep_el is not None:
                species = {s.strip().rstrip("%").upper() for sub in m.group(3).split(":") for s in sub.split(",")}
                if not species <= keep_el:
                    continue
        c = re.sub(r"REF:\s*(\S+)", r"REF_\1", c)
        out.append(c + " !")
    return "\n".join(out) + "\n"


_DB: dict = {}


def keep_phases_only(tdb: str, phases) -> str:
    """Drop the PHASE, CONSTITUENT and PARAMETER commands of phases not in `phases` (mc_ni's SIGMA parameters in
    Fe-Cr do not parse, and the copper calculations never use SIGMA)."""
    keep = {p.upper() for p in phases}
    for c in tdb.split("\n"):                   # an ordered phase and its disordered part go together
        t = c.split()
        if len(t) >= 6 and t[0] == "TYPE_DEFINITION" and "DIS_PART" in t:
            o, d = t[t.index("A_P_D") + 1].upper(), t[t.index("DIS_PART") + 1].upper()
            if o in keep or d in keep:
                keep |= {o, d}
    out = []
    for c in tdb.split("\n"):
        t = c.split()
        if t and t[0] in ("PHASE", "CONSTITUENT") and t[1].upper() not in keep:
            continue
        if t and t[0] == "PARAMETER":
            m = re.match(r"PARAMETER\s+\w+\(\s*([^,]+?)\s*,", c)
            if m and m.group(1).upper() not in keep:
                continue
        out.append(c)
    return "\n".join(out)


def load_db(key: str, elements, phases=None):
    from pycalphad import Database
    els = tuple(sorted(e.upper() for e in elements))
    tag = (key, els, tuple(sorted(phases)) if phases else None)
    if tag not in _DB:
        if key == "cost507":
            _DB[tag] = Database(str(tdb_path(key)))
        else:
            txt = clean_tdb_text(tdb_path(key).read_text(encoding="latin-1"), els)
            if phases:
                txt = keep_phases_only(txt, phases)
            _DB[tag] = Database.from_string(txt, fmt="tdb")
    return _DB[tag]


def wt_to_x(wt: dict) -> dict:
    n = {k.upper(): w / MW[k.upper()] for k, w in wt.items() if w > 0}
    s = sum(n.values())
    return {k: v / s for k, v in n.items()}


def equilibrium(db, wt: dict, phases, T, balance: str):
    """pycalphad equilibrium at temperatures T (K) for a composition in wt% (balance element included)."""
    from pycalphad import equilibrium as eq, variables as v
    from pycalphad.core.utils import filter_phases, unpack_species
    x = wt_to_x(wt)
    comps = sorted(x) + ["VA"]
    ph = filter_phases(db, unpack_species(db, comps), [p for p in phases if p in db.phases])
    conds = {v.T: np.atleast_1d(np.asarray(T, float)), v.P: P0, v.N: 1.0}
    conds.update({v.X(e): x[e] for e in x if e != balance.upper()})
    return eq(db, comps, ph, conds)


def phase_table(res) -> list[list[tuple[str, float, dict]]]:
    """Per temperature: [(phase, molar amount, {element: mole fraction})]."""
    ph = res.Phase.values.reshape(-1, res.Phase.shape[-1])
    npv = res.NP.values.reshape(-1, res.NP.shape[-1])
    X = res.X.values.reshape(-1, res.X.shape[-2], res.X.shape[-1])
    els = [str(c) for c in res.component.values]
    out = []
    for i in range(ph.shape[0]):
        out.append([(str(p), float(npv[i][j]), {e: float(X[i][j][k]) for k, e in enumerate(els)})
                    for j, p in enumerate(ph[i]) if p != "" and np.isfinite(npv[i][j])])
    return out


def _x_to_wt(xd: dict) -> dict:
    m = {e: xd[e] * MW[e] for e in xd if e in MW}
    s = sum(m.values())
    return {e: 100.0 * v / s for e, v in m.items()}


# ------------------------------------------------------------------------------------------- the Al corner, solute by solute
AL_TM = 933.47           # K, pure Al (SGTE)
# solute -> (database, probe wt%). The probe sits inside the alpha-Al two-phase field.
AL_SOLUTES = {"CR": ("mc_al", 0.2), "CU": ("mc_al", 1.0), "FE": ("mc_al", 0.2), "MG": ("mc_al", 1.0),
              "MN": ("mc_al", 0.5), "NI": ("mc_al", 0.5), "SC": ("mc_al", 0.2), "SI": ("mc_al", 1.0),
              "TI": ("mc_al", 0.1), "ZN": ("mc_al", 2.0), "ZR": ("mc_al", 0.1),
              "CE": ("cost507", 0.5), "LI": ("cost507", 0.5), "SN": ("cost507", 0.5)}


def al_dilute_one(el: str) -> dict:
    """The metastable alpha-Al liquidus slope m (K per wt%) and partition coefficient k for one solute, from the
    LIQUID + FCC_A1 equilibrium of the binary at a dilute probe composition (only those two phases, as in the
    growth-restriction literature)."""
    key, w = AL_SOLUTES[el]
    db = load_db(key, ["AL", el])
    T = np.arange(AL_TM - 40.0, AL_TM + 40.0, 0.1)
    t0 = time.time()
    res = equilibrium(db, {"AL": 100.0 - w, el: w}, ["LIQUID", "FCC_A1"], T, "AL")
    tab = phase_table(res)
    fl = np.array([sum(a for p, a, _ in pt if p == "LIQUID") if pt else np.nan for pt in tab])
    two = [i for i, f in enumerate(fl) if 1e-6 < f < 1 - 1e-6]
    if not two:
        return dict(element=el, db=key, error="no two-phase field found")
    i = two[len(two) // 2]
    liq = next(xd for p, a, xd in tab[i] if p == "LIQUID")
    sol = next(xd for p, a, xd in tab[i] if p == "FCC_A1")
    wl, ws = _x_to_wt(liq)[el], _x_to_wt(sol)[el]
    Ti = float(T[i])
    return dict(element=el, db=key, probe_wt=w, T_K=Ti, w_liquid=wl, w_solid=ws, k=ws / wl,
                m_K_per_wt=(Ti - AL_TM) / wl, T_liquidus_K=float(T[max(two)]), T_solidus_K=float(T[min(two)]),
                seconds=round(time.time() - t0, 2))


# Binary invariants at the Al corner from the assessed diagrams (ASM Handbook Vol. 3 / Murray & McAlister, as
# compiled in Mondolfo, "Aluminum Alloys: Structure and Properties", 1976), used to end the dilute Scheil path where
# the liquid reaches a eutectic, and erbium's slope and k, which no open database here covers. wt%, degC.
AL_INVARIANTS = {
    "SI": dict(kind="eutectic", w=12.6, T_C=577.0, phase="Si"),
    "CU": dict(kind="eutectic", w=33.2, T_C=548.0, phase="Al2Cu"),
    "MG": dict(kind="eutectic", w=35.0, T_C=450.0, phase="Al3Mg2"),
    "ZN": dict(kind="eutectic", w=94.9, T_C=382.0, phase="(Zn)"),
    "FE": dict(kind="eutectic", w=1.8, T_C=655.0, phase="Al13Fe4"),
    "MN": dict(kind="eutectic", w=1.9, T_C=658.0, phase="Al6Mn"),
    "NI": dict(kind="eutectic", w=6.1, T_C=640.0, phase="Al3Ni"),
    "CE": dict(kind="eutectic", w=10.0, T_C=640.0, phase="Al11Ce3"),
    "SC": dict(kind="eutectic", w=0.55, T_C=655.0, phase="Al3Sc"),
    "ER": dict(kind="eutectic", w=6.0, T_C=655.0, phase="Al3Er"),
    "LI": dict(kind="eutectic", w=9.9, T_C=600.0, phase="AlLi"),
    "SN": dict(kind="eutectic", w=99.5, T_C=228.0, phase="(Sn)"),
    "ZR": dict(kind="peritectic", w=0.11, T_C=660.8, phase="Al3Zr"),
    "TI": dict(kind="peritectic", w=0.15, T_C=665.0, phase="Al3Ti"),
    "CR": dict(kind="peritectic", w=0.41, T_C=661.0, phase="Al7Cr"),
}
ER_FALLBACK = dict(element="ER", db="binary diagram (assumed)", k=0.02, m_K_per_wt=-0.9,
                   note="no open database covers Al-Er; slope from the Al-Al3Er eutectic (about 6 wt% Er, "
                        "655 degC) and a near-zero solubility, both approximate")


def al_dilute_table(write=True) -> dict:
    rows = {}
    for el in AL_SOLUTES:
        try:
            rows[el] = al_dilute_one(el)
        except Exception as e:                       # keep going; the table says what failed
            rows[el] = dict(element=el, error=repr(e)[:300])
        print(el, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in rows[el].items()}, flush=True)
    rows["ER"] = ER_FALLBACK
    out = dict(T_m_K=AL_TM, solutes=rows, invariants=AL_INVARIANTS,
               method="LIQUID + FCC_A1 binary equilibrium at a dilute probe composition (pycalphad "
                      + __import__("pycalphad").__version__ + "); m = (T - Tm)/w_liquid, k = w_solid/w_liquid")
    if write:
        (DATA / "al_dilute.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


# ------------------------------------------------------------------------------------------- Scheil on reference Al alloys
AL_REFERENCE = {   # nominal wt%, balance Al
    "AlSi10Mg": {"SI": 10.0, "MG": 0.35},
    "Al-1Zr": {"ZR": 1.0},
    "Scalmalloy (Al-4.6Mg-0.7Sc-0.3Zr)": {"MG": 4.6, "SC": 0.7, "ZR": 0.3},
    "Al-Mn-Cr-Zr (Al-3.6Mn-0.5Cr-0.9Zr)": {"MN": 3.6, "CR": 0.5, "ZR": 0.9},
    "6061": {"MG": 1.0, "SI": 0.6, "CU": 0.28, "CR": 0.2},
    "7075": {"ZN": 5.6, "MG": 2.5, "CU": 1.6, "CR": 0.23},
    "2024": {"CU": 4.4, "MG": 1.5, "MN": 0.6},
}
AL_PHASES = ["LIQUID", "FCC_A1", "SI_DIAMOND_A4", "THETA_AL2CU", "S_PHASE", "MG2SI_B", "BETA_AL3MG2", "AL3ZR",
             "AL3SC", "AL3TI_H", "AL6MN", "AL13FE4", "AL3NI", "AL4CR", "AL11CR2", "AL13CR2", "AL12MN",
             "LC14_ZN2MG", "MGALZN_PHI", "MGZN", "HCP_ZN", "Q_PHASE_H", "ALFESI_T6", "AL8FEMNSI2", "G_AL12MG17"]


def al_scheil(name: str, wt: dict, step=2.0) -> dict:
    from pycalphad import variables as v
    from scheil import simulate_scheil_solidification
    els = ["AL"] + list(wt)
    db = load_db("mc_al", els)
    comp = dict(wt)
    comp["AL"] = 100.0 - sum(wt.values())
    x = wt_to_x(comp)
    from pycalphad.core.utils import filter_phases, unpack_species
    comps = sorted(x) + ["VA"]
    ph = filter_phases(db, unpack_species(db, comps), [p for p in AL_PHASES if p in db.phases])
    t0 = time.time()
    res = simulate_scheil_solidification(db, comps, ph, {v.X(e): x[e] for e in x if e != "AL"}, AL_TM + 150,
                                         step_temperature=step)
    T = np.array(res.temperatures) - 273.15
    fl = np.array(res.fraction_liquid)
    fs = 1 - fl
    first = float(T[np.argmax(fl < 0.9999)])
    t99 = float(T[np.argmax(fl <= 0.01)]) if (fl <= 0.01).any() else float("nan")
    # Kou's index |dT/d(fs^1/2)| near fs^1/2 = 0.87-0.94 (Kou, Acta Mater. 88, 2015)
    r = np.sqrt(np.clip(fs, 0, 1))
    sel = (r >= 0.87) & (r <= 0.94)
    csi = float(abs(np.polyfit(r[sel], T[sel], 1)[0])) if sel.sum() >= 2 else float("nan")
    return dict(alloy=name, wt=wt, first_solid_C=first, T_99pct_solid_C=t99, range_C=first - t99,
                kou_index_K=csi, end_C=float(T[-1]), converged=bool(res.converged),
                curve=dict(T_C=[round(t, 2) for t in T[::2]], fs=[round(f, 4) for f in fs[::2]]),
                seconds=round(time.time() - t0, 1))


def al_scheil_reference(write=True) -> dict:
    out = {}
    for name, wt in AL_REFERENCE.items():
        try:
            out[name] = al_scheil(name, wt)
            r = out[name]
            print(f"{name}: {r['first_solid_C']:.1f} -> {r['T_99pct_solid_C']:.1f} C, Kou {r['kou_index_K']:.0f} K, "
                  f"{r['seconds']} s", flush=True)
        except Exception as e:
            out[name] = dict(alloy=name, wt=wt, error=repr(e)[:300])
            print(name, "failed", repr(e)[:200], flush=True)
        if write:
            (DATA / "al_scheil_ref.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


# ------------------------------------------------------------------------------------------- the copper space (mc_ni)
CU_ELEMENTS = ["NI", "AL", "FE", "MN", "CR", "SI", "NB", "TI"]
CU_PHASES = ["LIQUID", "FCC_A1", "BCC_A2", "NIAL", "GAMMA_PRIME", "HCP_A3"]     # as DAL run_calphad.py (mc_ni)
CU_T_K = np.arange(1800.0, 899.0, -10.0)          # 1527 -> 627 degC
CU_REPORT_C = (1000, 900, 800, 700)


def cu_one(wt_solutes: dict) -> dict:
    """Equilibrium of one Cu alloy over 1527-627 degC: liquidus, solidus, and the phase amounts at 1000, 900, 800 and
    700 degC, grouped as the literature does (alpha fcc, beta Cu-rich bcc, kappa = NiAl-type B2 or Fe-rich bcc,
    gamma' Ni3Al)."""
    wt = {k.upper(): float(v) for k, v in wt_solutes.items() if v > 1e-4}
    wt["CU"] = 100.0 - sum(wt.values())
    els = sorted(wt)
    db = load_db("mc_ni", els, CU_PHASES)
    t0 = time.time()
    res = equilibrium(db, wt, CU_PHASES, CU_T_K, "CU")
    tab = phase_table(res)
    fl = np.array([sum(a for p, a, _ in pt if p == "LIQUID") if pt else np.nan for pt in tab])
    T = CU_T_K - 273.15

    def cross(level):            # first temperature (from the top) where the liquid fraction falls below level
        ok = np.where(np.nan_to_num(fl, nan=1.0) < level)[0]
        if len(ok) == 0 or ok[0] == 0:
            return float("nan")
        j = ok[0]
        f0, f1 = fl[j - 1], fl[j]
        return float(T[j - 1] + (T[j] - T[j - 1]) * (f0 - level) / (f0 - f1 + 1e-12))

    liq, sol = cross(1 - 1e-4), cross(1e-4)

    def groups(pt):
        g = dict(liquid=0.0, alpha=0.0, beta=0.0, kappa=0.0, gamma_prime=0.0, other=0.0)
        for p, a, xd in pt:
            if p == "LIQUID":
                g["liquid"] += a
            elif p == "FCC_A1":
                g["alpha" if xd.get("CU", 0) > 0.5 else "other"] += a
            elif p in ("BCC_A2", "BCC_B2"):
                g["beta" if xd.get("CU", 0) > 0.5 else "kappa"] += a
            elif p == "NIAL":
                g["kappa"] += a
            elif p == "GAMMA_PRIME":
                g["gamma_prime"] += a
            else:
                g["other"] += a
        return {k: round(v, 5) for k, v in g.items()}

    at = {}
    for tc in CU_REPORT_C:
        j = int(np.argmin(abs(T - tc)))
        at[str(tc)] = groups(tab[j]) if tab[j] else None
    # the temperature below which no Cu-rich bcc (beta) is left at equilibrium (the NAB 'beta solvus')
    beta = np.array([groups(pt)["beta"] if pt else np.nan for pt in tab])
    has = np.where(np.nan_to_num(beta) > 1e-4)[0]
    beta_lo = float(T[has[-1]]) if len(has) else float("nan")
    return dict(wt={k: round(v, 4) for k, v in wt.items()}, liquidus_C=liq, solidus_C=sol, phases=at,
                beta_lowest_C=beta_lo, seconds=round(time.time() - t0, 2))


def cu_design(n: int = 384, seed: int = 303, workers: int = 3, write=True) -> dict:
    """Equilibrium over a Sobol design of the copper space (twin.spaces.CU), plus the reference alloys. The twin's Cu
    thermodynamics is an emulator fitted to these points (twin/thermo.py)."""
    from concurrent.futures import ProcessPoolExecutor
    from twin import spaces
    pts = spaces.CU.sample(n, seed=seed, kind="sobol")
    comps = [{e.upper(): p[e] for e in spaces.CU.elements} for p in pts]
    comps += [{"NI": 30.0, "FE": 0.6, "MN": 0.6}, {"NI": 10.0, "FE": 1.4, "MN": 0.8},
              {"AL": 9.2, "NI": 4.5, "FE": 4.0, "MN": 1.2}]
    out, t0 = [], time.time()
    path = DATA / "cu_calphad.json"
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(_cu_safe, comps, chunksize=4)):
            out.append(r)
            if write and (i % 24 == 23 or i == len(comps) - 1):
                path.write_text(json.dumps(dict(database="mc_ni v2.036", phases=CU_PHASES, points=out),
                                           indent=0) + "\n")
                print(f"{i + 1}/{len(comps)} in {time.time() - t0:.0f} s", flush=True)
    return dict(points=out)


def _cu_safe(c):
    try:
        return cu_one(c)
    except Exception as e:
        return dict(wt=c, error=repr(e)[:200])


# ------------------------------------------------------------------------------------------- Thermo-Calc, where licensed
class ThermoCalcBackend:
    """TC-Python with TCAL (Al) or TCCU (Cu): the calls the twin would make on BYU's HPC. Not runnable here (no
    licence on a CI runner); kept so the interface is fixed. Usage there:

        tc = ThermoCalcBackend("TCAL9")          # or the licensed version, e.g. TCAL10 / TCCU7
        tc.scheil({"Al": 89.65, "Si": 10, "Mg": 0.35})
    """

    def __init__(self, database: str):
        self.database = database

    def available(self) -> bool:
        try:
            import tc_python  # noqa: F401
            return True
        except Exception:
            return False

    def scheil(self, wt: dict, back_diffusion=True) -> dict:
        from tc_python import TCPython, CompositionUnit, ScheilOptions, ScheilCalculationType  # type: ignore
        bal = max(wt, key=wt.get)
        with TCPython() as start:
            sys_ = (start.select_database_and_elements(self.database, list(wt)).get_system())
            calc = sys_.with_scheil_calculation().set_composition_unit(CompositionUnit.MASS_PERCENT)
            for el, w in wt.items():
                if el != bal:
                    calc = calc.set_composition(el, w)
            if back_diffusion:
                calc = calc.with_options(ScheilOptions().set_calculation_type(
                    ScheilCalculationType.scheil_back_diffusion()))
            r = calc.calculate()
            T, fs = r.get_values_of(ScheilCalculationType, "T", "NS")  # pragma: no cover - licence only
            return dict(T_K=list(T), fs=list(fs))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "al-dilute":
        al_dilute_table()
    elif cmd == "al-scheil":
        al_scheil_reference()
    elif cmd == "cu-design":
        cu_design(int(sys.argv[2]) if len(sys.argv) > 2 else 384)
    elif cmd == "cu-ref":
        for c in ({"NI": 30.0, "FE": 0.6, "MN": 0.6}, {"NI": 10.0, "FE": 1.4, "MN": 0.8},
                  {"AL": 9.2, "NI": 4.5, "FE": 4.0, "MN": 1.2}):
            r = cu_one(c)
            print(r["wt"], f"liq {r['liquidus_C']:.1f} sol {r['solidus_C']:.1f}", r["phases"]["900"],
                  r["beta_lowest_C"], r["seconds"], "s")
    else:
        print(__doc__)
