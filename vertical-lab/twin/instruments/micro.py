"""The latent microstructure every microscopy/diffraction/spectroscopy simulator reads: what is physically in a powder
lot or a part, derived from the truth's own state (composition, thermo, process, pores, grains), never from a
measurement.

``phase_model(sample, campaign, kind)`` returns a dict with

* ``phases``: list of phase dicts (name, structure key into ``STRUCTURES``, wt and vol fraction, composition (mass
  fractions), lattice parameters (A), crystallite size (nm), microstrain, morphology, mean Z (for BSE contrast),
  density (g/cm3), note).
* ``matrix``: the FCC solid solution: solute in solution (wt%), its lattice parameter from Vegard coefficients.
* ``pores`` (parts): per type (lof, keyhole, gas) volume fraction, lognormal size (median, gsd, um), shape (aspect,
  irregularity), number per mm3; ``cracks``: density (mm/mm2), length and opening distributions, orientation.
* ``grains`` (parts): equivalent diameter, equiaxed fraction, columnar aspect ratio, <100> fiber spread, baseline KAM.
* ``powder`` (lots): the size populations of the sieved cut, per atomizer run, satellites, irregular share.

Sources for the numbers (also in notes/twin_instruments_micro.md):

* Vegard coefficients for Al solid solutions: King, J. Mater. Sci. 1 (1966) 79 (size factors), and the lattice-
  parameter compilations in Hatch (ed.), *Aluminum: Properties and Physical Metallurgy*, ASM 1984, ch. 1 (Mg +0.0045,
  Cu -0.0051, Si -0.0017, Zn -0.0007, Li -0.0010, Mn -0.0090 A per at.%); LPBF AlSi10Mg's contracted lattice
  (a = 4.045-4.047 A) in Li et al., Acta Mater. 105 (2016) 25 and Marola et al., Mater. Des. 2018. Cr, Fe, Ni, Ti,
  Zr, Sc, Er, Ce, Sn: sign and order of magnitude from King's size factors, values assumed.
* Cu solid solutions: Cu-Ni follows Vegard between 3.6149 and 3.5240 A (Pearson's Handbook); Al +0.0022, Mn +0.0029,
  Fe +0.0009 A per at.% (Pearson; Massalski); Cr, Si, Nb, Ti assumed from King's size factors.
* Phase lattice parameters: Pearson's Crystal Data / ICSD standard values (cited per structure in ``STRUCTURES``).
* NAB phases: Hasan, Lorimer & Ridley, J. Phys. IV 1982 and Culpan & Rose, J. Mater. Sci. 13 (1978) 1647 (kappa_II
  Fe3Al DO3, kappa_III NiAl B2, kappa_IV Fe-rich BCC, retained beta' martensite).
* LPBF pore populations: lack-of-fusion 50-300 um irregular, keyhole 20-100 um spherical, gas 5-40 um spherical
  (Cunningham et al., Science 363 (2019) 849; Snell et al., JOM 72 (2020) 101); hot cracks along columnar grain
  boundaries parallel to the build direction (Martin et al., Nature 549 (2017) 365).
"""
from __future__ import annotations

import json
import math
import os
import zlib
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CALIB_PATH = HERE / "calib_micro.json"

# ------------------------------------------------------------------------------------------------ atomic data
# Z and standard atomic weight (IUPAC 2021)
ATOM = {"Li": (3, 6.94), "C": (6, 12.011), "O": (8, 15.999), "Mg": (12, 24.305), "Al": (13, 26.982),
        "Si": (14, 28.085), "Sc": (21, 44.956), "Ti": (22, 47.867), "Cr": (24, 51.996), "Mn": (25, 54.938),
        "Fe": (26, 55.845), "Ni": (28, 58.693), "Cu": (29, 63.546), "Zn": (30, 65.38), "Zr": (40, 91.224),
        "Nb": (41, 92.906), "Sn": (50, 118.71), "Ce": (58, 140.116), "Er": (68, 167.259)}
AL_ELEMENTS = ["Mn", "Cr", "Zr", "Mg", "Si", "Cu", "Ti", "Fe", "Ni", "Ce", "Sc", "Li", "Er", "Zn", "Sn"]
CU_ELEMENTS = ["Ni", "Al", "Fe", "Mn", "Cr", "Si", "Nb", "Ti"]
NA = 6.02214076e23


def Z(el):
    return ATOM[el][0]


def M(el):
    return ATOM[el][1]


def base_of(campaign: str) -> str:
    return "Al" if campaign == "flaime_al" else "Cu"


def kind_of(sample: dict) -> str:
    return "part" if ("porosity" in sample or "grain_um" in sample) else "powder"


def wt_to_at(wt: dict) -> dict:
    """wt% (or mass fractions) -> atomic fractions (sum 1)."""
    n = {e: w / M(e) for e, w in wt.items() if w > 0}
    s = sum(n.values()) or 1.0
    return {e: v / s for e, v in n.items()}


def at_to_wt(at: dict) -> dict:
    m = {e: x * M(e) for e, x in at.items() if x > 0}
    s = sum(m.values()) or 1.0
    return {e: v / s for e, v in m.items()}


def stoich_wt(formula: dict) -> dict:
    """{'Al': 2, 'Cu': 1} -> mass fractions."""
    return at_to_wt({e: float(n) for e, n in formula.items()})


def mean_Z(massfrac: dict) -> float:
    """Mass-fraction-weighted mean Z (the quantity BSE contrast follows; Castaing's rule)."""
    s = sum(massfrac.values()) or 1.0
    return sum(w * Z(e) for e, w in massfrac.items()) / s


def bse_eta(massfrac: dict, kv: float = 15.0) -> float:
    """Backscatter coefficient of a compound: mass-weighted sum of the elemental coefficients from Reuter's fit,
    eta = -0.0254 + 0.016 Z - 1.86e-4 Z^2 + 8.3e-7 Z^3 (Reuter 1972, in Goldstein et al., SEM and X-ray
    Microanalysis, 4th ed., 2018, ch. 2)."""
    s = sum(massfrac.values()) or 1.0
    eta = 0.0
    for e, w in massfrac.items():
        z = Z(e)
        eta += w / s * (-0.0254 + 0.016 * z - 1.86e-4 * z * z + 8.3e-7 * z ** 3)
    return eta


# ------------------------------------------------------------------------------------------------ crystal structures
def _fcc(t):
    return [tuple(np.mod(np.add(t, s), 1.0)) for s in ((0, 0, 0), (0, .5, .5), (.5, 0, .5), (.5, .5, 0))]


def _bcc(t):
    return [tuple(np.mod(np.add(t, s), 1.0)) for s in ((0, 0, 0), (.5, .5, .5))]


def _sites(site, positions):
    return [(site, p) for p in positions]


def _build_structures():
    """Every phase the simulators know. 'atoms': (site, (x, y, z)) in the conventional cell, where site is a key of
    the phase's ``sites`` (each site's occupancy by element is set from the phase composition). 'wilson': a
    complex cell (>= 28 atoms) whose positions we do not carry: reflections at the true lattice's d-spacings with
    the centring's absences, intensities drawn once (seeded by name) from Wilson statistics, <|F|^2> = sum f_j^2
    (assumed; Wilson, Acta Cryst. 2, 1949)."""
    S = {}
    # FCC solid solution (A1, Fm-3m): Al 4.0496 A (Pearson), Cu 3.6149 A
    S["fcc"] = dict(kind="atoms", system="cubic", sg="Fm-3m", a=4.0496, sites={"M": {"Al": 1}},
                    atoms=_sites("M", _fcc((0, 0, 0))), B=0.80, src="A1 Cu-type")
    # diamond Si, Fd-3m, a 5.4309 A
    S["Si"] = dict(kind="atoms", system="cubic", sg="Fd-3m", a=5.4309, sites={"Si": {"Si": 1}},
                   atoms=_sites("Si", _fcc((0, 0, 0)) + _fcc((.25, .25, .25))), B=0.46, src="ICSD 51688")
    # L1_2 Al3X (Pm-3m): Al3Sc 4.103, Al3Zr (metastable L1_2) 4.08, Al3Er 4.215, Al3Li (delta') 4.01 A
    for nm, x, a in (("Al3Sc", "Sc", 4.103), ("Al3Zr_L12", "Zr", 4.080), ("Al3Er", "Er", 4.215),
                     ("Al3Li", "Li", 4.010), ("Al3(Sc,Zr)", "Sc", 4.095)):
        S[nm] = dict(kind="atoms", system="cubic", sg="Pm-3m", a=a,
                     sites={"X": ({"Sc": .7, "Zr": .3} if nm == "Al3(Sc,Zr)" else {x: 1}), "Al": {"Al": 1}},
                     atoms=[("X", (0, 0, 0)), ("Al", (0, .5, .5)), ("Al", (.5, 0, .5)), ("Al", (.5, .5, 0))],
                     B=0.6, src="L1_2 (Cu3Au type); Pearson's Crystal Data")
    # D0_23 Al3Zr (I4/mmm) a 4.013 c 17.32 A, Zr 4e z=0.1196, Al 4e z=0.3753, 4c, 4d (Pearson; Srinivasan 1991)
    i = lambda p: [p, tuple(np.mod(np.add(p, (.5, .5, .5)), 1))]
    at = []
    for z in (0.1196, -0.1196):
        at += _sites("Zr", i((0, 0, z % 1)))
    for z in (0.3753, -0.3753):
        at += _sites("Al", i((0, 0, z % 1)))
    for p in ((0, .5, 0), (.5, 0, 0), (0, .5, .25), (.5, 0, .25)):
        at += _sites("Al", i(p))
    S["Al3Zr_D023"] = dict(kind="atoms", system="tetragonal", sg="I4/mmm", a=4.013, c=17.32,
                           sites={"Zr": {"Zr": 1}, "Al": {"Al": 1}}, atoms=at, B=0.6, src="D0_23; Pearson")
    # D0_22 Al3Ti (I4/mmm) a 3.851 c 8.608 A: Ti 2a, Al 2b, 4d
    at = _sites("Ti", i((0, 0, 0))) + _sites("Al", i((0, 0, .5))) + _sites("Al", i((0, .5, .25))) \
        + _sites("Al", i((.5, 0, .25)))
    S["Al3Ti"] = dict(kind="atoms", system="tetragonal", sg="I4/mmm", a=3.851, c=8.608,
                      sites={"Ti": {"Ti": 1}, "Al": {"Al": 1}}, atoms=at, B=0.6, src="D0_22; Pearson")
    # Mg2Si antifluorite (Fm-3m) a 6.351 A
    S["Mg2Si"] = dict(kind="atoms", system="cubic", sg="Fm-3m", a=6.351, sites={"Si": {"Si": 1}, "Mg": {"Mg": 1}},
                      atoms=_sites("Si", _fcc((0, 0, 0))) + _sites("Mg", _fcc((.25, .25, .25)) + _fcc((.75, .75, .75))),
                      B=0.7, src="C1 (CaF2 type); Pearson")
    # theta Al2Cu (I4/mcm, C16) a 6.067 c 4.877 A: Cu 4a (0,0,1/4); Al 8h (x, x+1/2, 0), x = 0.1581
    x = 0.1581
    at = []
    for p in ((0, 0, .25), (0, 0, .75)):
        at += _sites("Cu", i(p))
    for p in ((x, x + .5, 0), (-x, -x + .5, 0), (-x + .5, x, 0), (x + .5, -x, 0)):
        at += _sites("Al", i(tuple(np.mod(p, 1))))
    S["Al2Cu"] = dict(kind="atoms", system="tetragonal", sg="I4/mcm", a=6.067, c=4.877,
                      sites={"Cu": {"Cu": 1}, "Al": {"Al": 1}}, atoms=at, B=0.7, src="C16; Meetsma et al. 1989")
    # eta MgZn2 (C14, P6_3/mmc) a 5.221 c 8.567 A: Mg 4f z 0.062; Zn 2a; Zn 6h x 0.830
    z, x = 0.062, 0.830
    at = _sites("Mg", [(1 / 3, 2 / 3, z), (2 / 3, 1 / 3, z + .5), (2 / 3, 1 / 3, -z % 1), (1 / 3, 2 / 3, (-z + .5) % 1)])
    at += _sites("Zn", [(0, 0, 0), (0, 0, .5)])
    at += _sites("Zn", [tuple(np.mod(p, 1)) for p in ((x, 2 * x, .25), (-2 * x, -x, .25), (x, -x, .25),
                                                       (-x, -2 * x, .75), (2 * x, x, .75), (-x, x, .75))])
    S["MgZn2"] = dict(kind="atoms", system="hexagonal", sg="P6_3/mmc", a=5.221, c=8.567,
                      sites={"Mg": {"Mg": 1}, "Zn": {"Zn": 1}}, atoms=at, B=0.8, src="C14 Laves; Komura & Tokunaga 1980")
    # AlLi (B32, NaTl type, Fd-3m) a 6.37 A
    S["AlLi"] = dict(kind="atoms", system="cubic", sg="Fd-3m", a=6.37, sites={"Al": {"Al": 1}, "Li": {"Li": 1}},
                     atoms=_sites("Al", _fcc((0, 0, 0)) + _fcc((.25, .25, .25)))
                     + _sites("Li", _fcc((.5, .5, .5)) + _fcc((.75, .75, .75))), B=1.0, src="B32; Pearson")
    # beta-Sn (I4_1/amd) a 5.832 c 3.182 A
    S["Sn"] = dict(kind="atoms", system="tetragonal", sg="I4_1/amd", a=5.832, c=3.182, sites={"Sn": {"Sn": 1}},
                   atoms=_sites("Sn", [(0, 0, 0), (0, .5, .25), (.5, .5, .5), (.5, 0, .75)]), B=1.5, src="A5")
    # complex aluminides: true cells, Wilson intensities
    S["Al6(Mn,Fe)"] = dict(kind="wilson", system="orthorhombic", sg="Cmcm", centring="C", a=6.498, b=7.552,
                           c=8.870, formula={"Al": 6, "Mn": 1}, Zf=4, B=0.7, src="oC28; Kontio et al. 1980")
    S["Al13Fe4"] = dict(kind="wilson", system="monoclinic", sg="C2/m", centring="C", a=15.49, b=8.08, c=12.48,
                        beta=107.7, formula={"Al": 13, "Fe": 4}, Zf=6, B=0.7, src="mC102; Grin et al. 1994")
    S["Al45Cr7"] = dict(kind="wilson", system="monoclinic", sg="C2/m", centring="C", a=25.196, b=7.574, c=10.949,
                        beta=128.7, formula={"Al": 45, "Cr": 7}, Zf=2, B=0.7, src="mC104; Cooper 1960")
    S["Al11Ce3"] = dict(kind="wilson", system="orthorhombic", sg="Immm", centring="I", a=4.395, b=10.092, c=13.015,
                        formula={"Al": 11, "Ce": 3}, Zf=2, B=0.8, src="oI28 (La3Al11 type); Gomes de Mesquita 1967")
    S["Al3Ni"] = dict(kind="wilson", system="orthorhombic", sg="Pnma", centring="P", a=6.598, b=7.352, c=4.802,
                      formula={"Al": 3, "Ni": 1}, Zf=4, B=0.7, src="oP16 (Fe3C type)")
    S["Al3Mg2"] = dict(kind="wilson", system="cubic", sg="Fd-3m", centring="F", a=28.24, formula={"Al": 3, "Mg": 2},
                       Zf=232, B=1.0, src="cF1168; Samson 1965")
    # copper side
    # beta' martensite in NAB: modelled on its ordered parent beta1 (DO3 Cu3Al, a 5.84 A) with martensitic broadening
    # (assumed: the real 9R/3R cells split these reflections; Culpan & Rose 1978)
    do3 = lambda a, A, B: dict(kind="atoms", system="cubic", sg="Fm-3m", a=a,
                               atoms=_sites("A1", _fcc((0, 0, 0))) + _sites("B", _fcc((.5, .5, .5)))
                               + _sites("B", _fcc((.25, .25, .25)) + _fcc((.75, .75, .75))))
    S["beta'"] = dict(do3(5.84, "Al", "Cu"), sites={"A1": {"Al": 1}, "B": {"Cu": .92, "Ni": .04, "Fe": .04}}, B=0.9,
                      src="DO3 parent (beta1 Cu3Al) of the 9R martensite; assumed")
    S["kappa_II"] = dict(do3(5.75, "Al", "Fe"), sites={"A1": {"Al": 1}, "B": {"Fe": .75, "Cu": .1, "Ni": .1, "Mn": .05}},
                         B=0.6, src="DO3 Fe3Al-based (Fe,Cu,Ni)3Al; Hasan et al. 1982")
    S["kappa_III"] = dict(kind="atoms", system="cubic", sg="Pm-3m", a=2.887,
                          sites={"Ni": {"Ni": .8, "Fe": .1, "Cu": .1}, "Al": {"Al": 1}},
                          atoms=[("Ni", (0, 0, 0)), ("Al", (.5, .5, .5))], B=0.6, src="B2 NiAl; Hasan et al. 1982")
    S["kappa_IV"] = dict(kind="atoms", system="cubic", sg="Im-3m", a=2.870, sites={"M": {"Fe": .85, "Al": .1, "Cu": .05}},
                         atoms=_sites("M", _bcc((0, 0, 0))), B=0.5, src="A2 Fe-rich; Culpan & Rose 1978")
    S["Cr"] = dict(kind="atoms", system="cubic", sg="Im-3m", a=2.884, sites={"M": {"Cr": 1}},
                   atoms=_sites("M", _bcc((0, 0, 0))), B=0.3, src="A2")
    S["Fe_bcc"] = dict(kind="atoms", system="cubic", sg="Im-3m", a=2.866, sites={"M": {"Fe": .95, "Ni": .05}},
                       atoms=_sites("M", _bcc((0, 0, 0))), B=0.35, src="A2")
    S["Ni2Si"] = dict(kind="wilson", system="orthorhombic", sg="Pnma", centring="P", a=7.06, b=4.99, c=3.72,
                      formula={"Ni": 2, "Si": 1}, Zf=4, B=0.5, src="delta-Ni2Si oP12")
    S["Ni3Nb"] = dict(kind="wilson", system="orthorhombic", sg="Pmmn", centring="P", a=5.116, b=4.259, c=4.565,
                      formula={"Ni": 3, "Nb": 1}, Zf=2, B=0.5, src="delta-Ni3Nb oP8")
    S["Ni3Ti"] = dict(kind="wilson", system="hexagonal", sg="P6_3/mmc", centring="P", a=5.101, c=8.307,
                      formula={"Ni": 3, "Ti": 1}, Zf=4, B=0.5, src="eta-Ni3Ti hP16 (D0_24)")
    for k, v in S.items():
        v.setdefault("b", v.get("a"))
        v.setdefault("c", v.get("a"))
        v.setdefault("beta", 90.0)
        v["name"] = k
    return S


STRUCTURES = _build_structures()
CRYSTAL = {"fcc": "FCC", "Si": "diamond", "beta'": "BCC-derived (DO3)", "kappa_II": "BCC-derived (DO3)",
           "kappa_III": "B2", "kappa_IV": "BCC", "Cr": "BCC", "Fe_bcc": "BCC"}


def structure_formula(st: dict, comp: dict | None = None) -> dict:
    """Atoms per conventional cell, by element (for density and mass absorption)."""
    if st["kind"] == "wilson":
        return {e: n * st["Zf"] for e, n in st["formula"].items()}
    out = {}
    for site, _ in st["atoms"]:
        occ = st["sites"][site]
        for e, x in occ.items():
            out[e] = out.get(e, 0.0) + x
    return out


def cell_volume(st, a=None, b=None, c=None):
    a = a or st["a"]
    b = b or st["b"] if st["system"] not in ("cubic",) else a
    c = c or st["c"] if st["system"] not in ("cubic",) else a
    if st["system"] == "cubic":
        b = c = a
    if st["system"] == "tetragonal":
        b = a
    if st["system"] == "hexagonal":
        return a * a * c * math.sqrt(3) / 2
    if st["system"] == "monoclinic":
        return a * b * c * math.sin(math.radians(st["beta"]))
    return a * b * c


def structure_density(st, a=None, c=None) -> float:
    f = structure_formula(st)
    mass = sum(n * M(e) for e, n in f.items()) / NA
    return mass / (cell_volume(st, a=a, c=c) * 1e-24)


# ------------------------------------------------------------------------------------------------ Vegard coefficients
# A per at.% solute in solution. Al: Hatch 1984 / King 1966 (Mg, Cu, Si, Zn, Li, Mn), others assumed from size
# factors. Cu: Pearson's Handbook (Ni, Al, Mn, Fe), others assumed.
A0 = {"Al": 4.0496, "Cu": 3.6149}
VEGARD = {
    "Al": {"Mg": +0.0045, "Cu": -0.0051, "Si": -0.0017, "Zn": -0.0007, "Li": -0.0010, "Mn": -0.0090,
           "Cr": -0.0060, "Fe": -0.0050, "Ni": -0.0030, "Ti": -0.0006, "Zr": +0.0020, "Sc": +0.0035,
           "Er": +0.0060, "Ce": +0.0080, "Sn": +0.0030},
    "Cu": {"Ni": -0.00091, "Al": +0.0022, "Mn": +0.0029, "Fe": +0.0009, "Cr": +0.0012, "Si": -0.0006,
           "Nb": +0.0040, "Ti": +0.0035},
}
VEGARD_SOURCED = {"Al": {"Mg", "Cu", "Si", "Zn", "Li", "Mn"}, "Cu": {"Ni", "Al", "Mn", "Fe"}}


def vegard_a(base: str, ss_wt: dict) -> float:
    """Lattice parameter of the FCC solid solution with ``ss_wt`` (wt% of each solute in the matrix)."""
    wt = dict(ss_wt)
    wt[base] = max(100.0 - sum(ss_wt.values()), 1.0)
    at = wt_to_at(wt)
    return A0[base] + sum(VEGARD[base].get(e, 0.0) * 100.0 * x for e, x in at.items() if e != base)


# ------------------------------------------------------------------------------------------------ Al phase model
# The eutectic second phase each solute forms (thermo.AL_EUT_PHASE_X); Mg pairs with Si or Zn when present
AL_EUT = {"Si": "Si", "Cu": "Al2Cu", "Mg": "Al3Mg2", "Zn": None, "Fe": "Al13Fe4", "Mn": "Al6(Mn,Fe)",
          "Ni": "Al3Ni", "Ce": "Al11Ce3", "Sc": "Al3Sc", "Er": "Al3Er", "Li": "AlLi", "Sn": "Sn"}
AL_PRIM = {"Zr": "Al3Zr_L12", "Sc": "Al3Sc", "Ti": "Al3Ti", "Cr": "Al45Cr7", "Mn": "Al6(Mn,Fe)",
           "Fe": "Al13Fe4", "Er": "Al3Er"}
PHASE_COMP = {
    "Si": {"Si": 1}, "Al2Cu": {"Al": 2, "Cu": 1}, "Al3Mg2": {"Al": 3, "Mg": 2}, "Al13Fe4": {"Al": 13, "Fe": 4},
    "Al6(Mn,Fe)": {"Al": 6, "Mn": 1}, "Al3Ni": {"Al": 3, "Ni": 1}, "Al11Ce3": {"Al": 11, "Ce": 3},
    "Al3Sc": {"Al": 3, "Sc": 1}, "Al3Er": {"Al": 3, "Er": 1}, "AlLi": {"Al": 1, "Li": 1}, "Sn": {"Sn": 1},
    "Al3Zr_L12": {"Al": 3, "Zr": 1}, "Al3Zr_D023": {"Al": 3, "Zr": 1}, "Al3Ti": {"Al": 3, "Ti": 1},
    "Al45Cr7": {"Al": 45, "Cr": 7}, "Mg2Si": {"Mg": 2, "Si": 1}, "MgZn2": {"Mg": 1, "Zn": 2},
    "Al3Li": {"Al": 3, "Li": 1}, "Al3(Sc,Zr)": {"Al": 3, "Sc": 0.7, "Zr": 0.3},
    "beta'": {"Cu": 3.0, "Al": 1.0}, "kappa_II": {"Fe": 2.4, "Cu": .3, "Ni": .3, "Al": 1.0},
    "kappa_III": {"Ni": .8, "Fe": .1, "Cu": .1, "Al": 1.0}, "kappa_IV": {"Fe": .85, "Al": .1, "Cu": .05},
    "Cr": {"Cr": 1}, "Fe_bcc": {"Fe": .95, "Ni": .05}, "Ni2Si": {"Ni": 2, "Si": 1}, "Ni3Nb": {"Ni": 3, "Nb": 1},
    "Ni3Ti": {"Ni": 3, "Ti": 1},
}
# solute an atomized droplet (~1e4-1e5 K/s) keeps in solution, wt% (assumed: between equilibrium solubility and
# LPBF's truth_al.RETAIN, by log cooling rate)
AL_EQ_SOL = dict(Mn=0.6, Cr=0.3, Zr=0.15, Sc=0.2, Fe=0.04, Ni=0.04, Ti=0.3, Er=0.05, Ce=0.01, Si=1.2, Mg=4.0,
                 Cu=2.0, Zn=6.0, Li=1.5, Sn=0.05)
ENTRAIN = 0.10   # share of an undissolved primary intermetallic carried into the powder (assumed)


def droplet_cooling(base: str, d_um: float, superheat_K: float = 150.0) -> float:
    """Newtonian cooling of a droplet in argon, dT/dt = 6 h dT / (rho c d), h = Nu k_Ar / d with Nu = 2 + 0.6
    Re^0.5 Pr^0.33 ~ 4 (assumed relative velocity 5 m/s); K/s."""
    rho_c = 2.4e6 if base == "Al" else 3.9e6
    d = max(d_um, 5.0) * 1e-6
    h = 4.0 * 0.03 / d
    T = (660 if base == "Al" else 1080) + superheat_K
    return 6 * h * (T - 25.0) / (rho_c * d)


def _retain_frac(cool):
    """0 at 1e2 K/s (equilibrium-like), 1 at LPBF's 1e6 K/s (log-linear, assumed)."""
    return float(np.clip((math.log10(max(cool, 1.0)) - 2.0) / 4.0, 0.0, 1.0))


def _lot_runs(sample):
    runs = [r for r in sample.get("runs", []) if not r.get("failed")]
    if not runs and "d50_um" in sample:
        runs = [sample]
    return runs


def powder_population(sample: dict, campaign: str) -> dict:
    """The sieved cut as the SEM sees it: per good atomizer run (weight, d50, gsd, cut), satellites, irregulars."""
    al = campaign == "flaime_al"
    cut = (20.0, 63.0) if al else (45.0, 150.0)
    runs = _lot_runs(sample)
    comps = []
    if runs:
        w = np.array([max(r.get("usable_frac", 0.9) * r.get("cut_frac", 0.3), 1e-6) for r in runs])
        w = w / w.sum()
        for wi, r in zip(w, runs):
            sh = r.get("true_superheat_K", 150.0)
            # cold melts tear into ligaments that freeze before they spheroidize (assumed logistic in superheat)
            irr = 0.03 + 0.5 / (1 + math.exp((sh - 40.0) / 15.0))
            comps.append(dict(w=float(wi), d50=float(r["d50_um"]), gsd=float(r.get("gsd", 1.6)),
                              superheat=float(sh), irregular=float(irr)))
    else:  # a gas-atomized lot: finer, rounder (Valimet / Ames; d50 35 / 60 um, gsd 1.8, from campaign.py)
        comps.append(dict(w=1.0, d50=35.0 if al else 60.0, gsd=1.8, superheat=300.0, irregular=0.02))
    sat = sample.get("satellite_frac", 0.07)
    if sat is None or not np.isfinite(sat):
        sat = 0.07
    return dict(cut=cut, components=comps, satellite_frac=float(sat), sieve_leak=0.04)


def _add(phases, name, wt_frac, **kw):
    if wt_frac <= 1e-6:
        return
    for p in phases:
        if p["name"] == name and p.get("role") == kw.get("role"):
            p["wt"] += wt_frac
            return
    phases.append(dict(name=name, wt=wt_frac, **kw))


def _al_model(sample, kind):
    from twin import thermo as T
    from twin.truth_al import L12, RETAIN
    comp = dict(sample["composition"])
    runs = _lot_runs(sample) if kind == "powder" else []
    extra = {}
    if kind == "powder":
        for r in runs:   # entrained coarse intermetallic from a melt set below the true liquidus
            for el, x in (r.get("undissolved") or {}).items():
                extra[el] = extra.get(el, 0.0) + ENTRAIN * x / max(len(runs), 1)
    th = _al_thermo(tuple(sorted((k, round(v, 4)) for k, v in comp.items())))
    if kind == "part" and "thermo" in sample:
        th = sample["thermo"]
    phases = []
    left = {e: comp.get(e, 0.0) for e in AL_ELEMENTS}                       # wt% not yet placed
    if kind == "part":
        cool = sample.get("melt_pool", {}).get("cool", 1e6)
        retain = dict(RETAIN)
        d_cell = sample.get("cell_um", 0.4)
    else:
        pop = powder_population(sample, "flaime_al")
        d50 = sum(c["w"] * c["d50"] for c in pop["components"])
        cool = droplet_cooling("Al", d50)
        f = _retain_frac(cool)
        retain = {e: AL_EQ_SOL[e] + f * (RETAIN[e] - AL_EQ_SOL[e]) for e in RETAIN}
        d_cell = 43.0 * max(cool, 1e2) ** -0.324                           # um, same law as truth_al
    # 1. primary intermetallics above the invariant: LPBF keeps 70 % of the excess in solution (truth_al.strength);
    #    a droplet keeps less (assumed: 70 % x retain fraction)
    keep = 0.7 if kind == "part" else 0.7 * _retain_frac(cool)
    for el, p in T.AL_PRIMARY.items():
        c = comp.get(el, 0.0)
        if c > p[0]:
            into = (1 - keep) * (c - p[0])
            ph = AL_PRIM[el]
            if el in ("Sc", "Zr") and comp.get("Sc", 0) > 0.05 and comp.get("Zr", 0) > 0.05:
                ph = "Al3(Sc,Zr)"
            x = stoich_wt(PHASE_COMP[ph])
            mass = into / 100.0 / x[el]
            _add(phases, ph, mass, role="primary", size_um=1.0 if kind == "part" else 2.0, morph="cuboid")
            left[el] -= into
    # entrained, undissolved coarse particles (powder only): D0_23 Al3Zr, D0_22 Al3Ti, Al3Sc, Al45Cr7
    for el, x_wt in extra.items():
        ph = {"Zr": "Al3Zr_D023", "Ti": "Al3Ti", "Sc": "Al3Sc", "Cr": "Al45Cr7", "Er": "Al3Er"}.get(el)
        if ph:
            x = stoich_wt(PHASE_COMP[ph])
            _add(phases, ph, x_wt / 100.0 / x[el], role="undissolved", size_um=8.0, morph="faceted")
    # 2. the matrix keeps what this cooling rate retains in solution (LPBF: truth_al.RETAIN; droplets: less)
    ss = {e: min(max(left.get(e, 0.0), 0.0), retain.get(e, 0.0)) for e in AL_ELEMENTS}
    # 3. eutectic / cell-boundary network from the rest, at most the truth's Scheil share (eutectic_by) times the
    #    weight truth_al.strength gives it (LPBF suppresses the sluggish formers' eutectic); in a droplet all of it.
    #    Whatever exceeds both goes to the element's network phase anyway (mass balance).
    eut = dict(th.get("eutectic_by", {}))
    pair_mg_si = comp.get("Mg", 0) > 0.05 and comp.get("Si", 0) > 0.3
    for e in AL_ELEMENTS:
        rest = max(left.get(e, 0.0), 0.0) - ss[e]
        if rest <= 1e-4:
            continue
        name = AL_EUT.get(e)
        if e == "Mg" and pair_mg_si:
            name = "Mg2Si"
        if e == "Mg" and comp.get("Zn", 0) > 1.0:
            name = "MgZn2"
        if e == "Zn":
            name = "MgZn2" if comp.get("Mg", 0) > 0.3 else None
        if name is None:
            ss[e] += rest                       # Zn without Mg: stays in solution (Al-Zn solubility is large)
            continue
        x = stoich_wt(PHASE_COMP[name])
        mass = rest / 100.0 / x[e]
        for e2, xe in x.items():                # a binary phase cannot take more of its partner than is left
            if e2 not in ("Al", e):
                mass = min(mass, max(left.get(e2, 0.0) - (ss[e2] if e2 != "Si" else 0.0), 0.0) / 100.0 / xe)
        if mass <= 1e-6:
            ss[e] += rest
            continue
        _add(phases, name, mass, role="eutectic", size_um=0.08 if kind == "part" else 0.3 * d_cell, morph="network")
        for e2, xe in x.items():
            if e2 != "Al":
                left[e2] -= mass * 100.0 * xe
        ss[e] += max(left[e] - ss[e], 0.0) if False else 0.0
    for e in AL_ELEMENTS:
        ss[e] = max(min(ss[e], left.get(e, 0.0)), 0.0)
    # 4. parts are characterized after the family's standard heat treatment (as truth_al.strength): L1_2 and age
    #    precipitates come out of the solution
    if kind == "part":
        for e in L12:
            if ss.get(e, 0) > 0:
                f = 0.8 * ss[e]                          # wt% of the element precipitated
                name = {"Sc": "Al3Sc", "Zr": "Al3Zr_L12", "Er": "Al3Er"}[e]
                x = stoich_wt(PHASE_COMP[name])
                _add(phases, name, f / 100.0 / x[e], role="precipitate", size_um=0.008, morph="spheroid")
                ss[e] -= f
        mg_si = 0.6 * min(ss["Mg"], ss["Si"] * 1.73)
        if mg_si > 0.01:
            x = stoich_wt(PHASE_COMP["Mg2Si"])
            m = mg_si / 100.0 / x["Mg"]
            _add(phases, "Mg2Si", m, role="precipitate", size_um=0.03, morph="needle")
            ss["Mg"] -= m * 100 * x["Mg"]
            ss["Si"] = max(ss["Si"] - m * 100 * x["Si"], 0)
        if ss["Cu"] > 0.05:
            x = stoich_wt(PHASE_COMP["Al2Cu"])
            m = 0.6 * ss["Cu"] / 100.0 / x["Cu"]
            _add(phases, "Al2Cu", m, role="precipitate", size_um=0.04, morph="plate")
            ss["Cu"] *= 0.4
        mz = 0.6 * min(ss["Zn"] / 2.7, ss["Mg"]) if ss["Zn"] > 0.05 else 0.0
        if mz > 0.01:
            x = stoich_wt(PHASE_COMP["MgZn2"])
            m = mz * 3.7 / 100.0
            _add(phases, "MgZn2", m, role="precipitate", size_um=0.01, morph="spheroid")
            ss["Mg"] = max(ss["Mg"] - m * 100 * x["Mg"], 0)
            ss["Zn"] = max(ss["Zn"] - m * 100 * x["Zn"], 0)
        if ss["Li"] > 0.1:
            x = stoich_wt(PHASE_COMP["Al3Li"])
            m = 0.7 * ss["Li"] / 100.0 / x["Li"]
            _add(phases, "Al3Li", m, role="precipitate", size_um=0.02, morph="spheroid")
            ss["Li"] *= 0.3
    w_ip = sum(p["wt"] for p in phases)
    w_m = max(1.0 - w_ip, 1e-3)
    ss = {e: v / w_m for e, v in ss.items() if v > 1e-4}            # wt% in the matrix itself
    a = vegard_a("Al", ss)
    mat_comp = dict(ss)
    mat_comp["Al"] = 100.0 - sum(ss.values())
    # crystallite size and microstrain of the matrix
    if kind == "part":
        cryst = float(np.clip(1000 * d_cell * 0.45, 60, 400))              # nm: cells bounded by the network
        strain = 1.2e-3 if eut else 0.8e-3                                  # as-built residual + network (assumed)
        strain *= 0.6                                                       # after the standard heat treatment
    else:
        cryst = float(np.clip(1000 * d_cell * 0.5, 150, 1500))
        strain = 3e-4
    matrix = dict(name="fcc", role="matrix", wt=max(1.0 - w_ip, 0.0), size_um=None, morph="matrix",
                  comp_wt=mat_comp, a=a, cryst_nm=cryst, strain=strain)
    return _finish("Al", comp, th, [matrix] + phases, ss, kind, extra=extra, cool=cool)


@lru_cache(maxsize=20000)
def _al_thermo(key):
    from twin import thermo as T
    return T.AlSolidification("truth").run(dict(key))


@lru_cache(maxsize=20000)
def _cu_thermo(key):
    from twin import thermo as T
    return T.CuThermo("truth").run(dict(key))


def _cu_model(sample, kind):
    from twin.truth_cu import _retain
    comp = dict(sample["composition"])
    th = sample.get("thermo") or _cu_thermo(tuple(sorted((k, round(v, 4)) for k, v in comp.items() if k != "Cu")))
    ni, al, fe = comp.get("Ni", 0.0), comp.get("Al", 0.0), comp.get("Fe", 0.0)
    phases = []
    left = {e: comp.get(e, 0.0) for e in CU_ELEMENTS}
    if kind == "part":
        beta_p = float(sample.get("beta_prime", 0.0))
        kappa = th["kappa_700"] * (0.5 + sample.get("temper", 0.35))
        cool = sample.get("cooling_K_s", 1e4)
        temper = sample.get("temper", 0.35)
    else:
        pop = powder_population(sample, "onr_cu")
        d50 = sum(c["w"] * c["d50"] for c in pop["components"])
        cool = droplet_cooling("Cu", d50)
        beta_p = th["beta_900"] * _retain(cool)
        kappa = 0.1 * th["kappa_700"]                      # little time for kappa in a droplet (assumed)
        temper = 0.0
    kappa = float(np.clip(kappa, 0, 0.4))
    # kappa split: Fe-rich (rosette kappa_II + fine kappa_IV) vs Ni-rich lamellar kappa_III, by Fe:Ni (assumed)
    if kappa > 0 and al > 0.5:
        fe_share = fe / max(fe + ni, 1e-6)
        for nm, w, sz in (("kappa_II", 0.65 * fe_share, 2.0), ("kappa_IV", 0.35 * fe_share, 0.05),
                          ("kappa_III", 1 - fe_share, 0.5)):
            m = kappa * w
            x = stoich_wt(PHASE_COMP[nm])
            for e2, xe in x.items():             # at most 85 % of what is left of each of its formers
                if e2 in ("Fe", "Ni", "Al"):
                    m = min(m, 0.85 * max(left[e2], 0.0) / 100.0 / xe)
            if m > 1e-4:
                _add(phases, nm, m, role="precipitate", size_um=sz, morph="rosette" if nm == "kappa_II"
                     else ("lamellar" if nm == "kappa_III" else "spheroid"))
                for e2, xe in x.items():
                    if e2 in left:
                        left[e2] -= m * 100 * xe
    if beta_p > 1e-4:
        # beta' is Al-rich: holds ~12 wt% Al (Cu3Al-like) and the alloy's share of Ni, Fe
        _add(phases, "beta'", beta_p, role="martensite", size_um=0.15, morph="lath",
             comp_override={"Cu": 100 - 12.4 - 0.5 * ni - 0.5 * fe, "Al": 12.4, "Ni": 0.5 * ni, "Fe": 0.5 * fe})
        left["Al"] -= beta_p * 12.4
        left["Ni"] -= beta_p * 0.5 * max(left["Ni"], 0.0)
        left["Fe"] -= beta_p * 0.5 * max(left["Fe"], 0.0)
    # silicides, Ni-Nb, Ni-Ti, Cr, Fe-rich in the Cu-Ni family (solubility limits assumed; DED's partial retention)
    sol = dict(Si=0.05 + (0.3 if kind == "powder" else 0.0), Nb=0.1, Ti=0.15 + 0.01 * ni, Cr=0.15,
               Fe=2.3 + 0.3 * al)
    prec = 0.7 if kind == "part" else 0.3
    for el, ph in (("Si", "Ni2Si"), ("Nb", "Ni3Nb"), ("Ti", "Ni3Ti"), ("Cr", "Cr"), ("Fe", "Fe_bcc")):
        c = max(left.get(el, 0.0), 0.0)
        if el == "Fe" and al > 3:
            continue
        if c > sol[el]:
            if ph in ("Ni2Si", "Ni3Nb", "Ni3Ti") and ni < 1.0:
                ph = {"Ni2Si": None, "Ni3Nb": "Cr", "Ni3Ti": None}[ph]
                if ph is None:
                    continue
            amt = prec * (c - sol[el])
            x = stoich_wt(PHASE_COMP[ph])
            key = el if el in x else max(x, key=x.get)
            m = amt / 100.0 / x[key]
            _add(phases, ph, m, role="precipitate", size_um=0.2, morph="spheroid")
            for e2, xe in x.items():
                if e2 in left:
                    left[e2] -= m * 100 * xe
    ss = {e: max(v, 0.0) for e, v in left.items() if v > 1e-4}
    w_ip = sum(p["wt"] for p in phases)
    w_m = max(1.0 - w_ip, 1e-3)
    ss_m = {e: v / w_m for e, v in ss.items()}                   # wt% in the alpha matrix itself
    a = vegard_a("Cu", ss_m)
    mat_comp = dict(ss_m)
    mat_comp["Cu"] = 100.0 - sum(ss_m.values())
    if kind == "part":
        cryst = float(np.clip(250 + 400 * temper - 200 * beta_p, 60, 600))
        strain = 6e-4 + 1.5e-3 * beta_p
    else:
        cryst = 500.0
        strain = 3e-4 + 1e-3 * beta_p
    matrix = dict(name="fcc", role="matrix", wt=w_m, size_um=None, morph="matrix", comp_wt=mat_comp, a=a,
                  cryst_nm=cryst, strain=strain)
    return _finish("Cu", comp, th, [matrix] + phases, ss_m, kind, cool=cool, beta_p=beta_p, kappa=kappa)


def _finish(base, comp, th, phases, ss, kind, extra=None, cool=None, beta_p=0.0, kappa=0.0):
    out = []
    for p in phases:
        st = STRUCTURES[p["name"]]
        if "comp_wt" in p:
            cw = {e: v / 100.0 for e, v in p["comp_wt"].items() if v > 0}
        elif "comp_override" in p:
            cw = {e: v / 100.0 for e, v in p.pop("comp_override").items() if v > 0}
        else:
            cw = stoich_wt(PHASE_COMP[p["name"]])
        p["comp"] = cw
        p.setdefault("a", st["a"])
        p.setdefault("c", st["c"])
        p.setdefault("b", st["b"])
        if p["role"] != "matrix":
            sz = p.get("size_um") or 0.5
            p.setdefault("cryst_nm", float(np.clip(sz * 1000 * 0.6, 4, 800)))
            p.setdefault("strain", 2.0e-3 if p["name"] == "beta'" else 5e-4)
        p["Z_mean"] = mean_Z(cw)
        p["eta"] = bse_eta(cw)
        p["density"] = _phase_density(p["name"], cw, p["a"])
        p["structure"] = p["name"]
        p["crystal"] = CRYSTAL.get(p["name"], STRUCTURES[p["name"]]["sg"])
        out.append(p)
    vol = np.array([p["wt"] / p["density"] for p in out])
    vol = vol / vol.sum()
    for p, v in zip(out, vol):
        p["vol"] = float(v)
    wsum = sum(p["wt"] for p in out)
    for p in out:
        p["wt"] = p["wt"] / wsum
    return dict(base=base, kind=kind, composition=dict(comp), thermo=th, phases=out,
                matrix=dict(ss_wt=dict(ss), a_A=out[0]["a"]), extra=extra or {}, cooling_K_s=cool,
                beta_prime=float(beta_p), kappa=float(kappa))


def _phase_density(name, cw, a):
    st = STRUCTURES[name]
    if name == "fcc":
        at = wt_to_at(cw)
        m = 4 * sum(x * M(e) for e, x in at.items()) / NA
        return m / ((a * 1e-8) ** 3)
    return structure_density(st)


# ------------------------------------------------------------------------------------------------ defects and grains
def pore_model(sample: dict, campaign: str) -> dict:
    """Pore populations by type: volume fraction, lognormal size (equivalent sphere diameter), shape, number
    density. LoF median scales with the hatch/layer gap the melt pool left (assumed), keyhole with melt-pool depth."""
    al = campaign == "flaime_al"
    pores = dict(sample.get("pores") or {})
    if not pores:
        pores = dict(lof=0.5 * sample.get("porosity", 0.0), keyhole=0.1 * sample.get("porosity", 0.0),
                     gas=0.4 * sample.get("porosity", 0.0))
    mp = sample.get("melt_pool") or {}
    if al:
        lof_d = float(np.clip(70.0 * (1 + 0.8 * max(mp.get("lof", 0.5) - 0.5, 0.0)), 50, 300))
        kh_d = float(np.clip(0.35 * mp.get("D_um", 100.0), 20, 100))
        gas_d = 12.0
    else:
        lof_d = float(np.clip(110.0 * (1 + 0.8 * max(1.3 - sample.get("energy_ratio", 1.5), 0.0)), 50, 300))
        kh_d, gas_d = 60.0, 18.0
    spec = dict(lof=(lof_d, 1.55, 2.6, 0.55), keyhole=(kh_d, 1.35, 1.1, 0.05), gas=(gas_d, 1.45, 1.05, 0.02))
    out = {}
    for t, (d, g, asp, irr) in spec.items():
        f = float(max(pores.get(t, 0.0), 0.0))
        s = math.log(g)
        mean_v = math.pi / 6 * d ** 3 * math.exp(4.5 * s * s) * (asp if t == "lof" else 1.0) ** 0  # um3
        n_v = f / (mean_v * 1e-9) if f > 0 else 0.0                                              # per mm3
        out[t] = dict(vol_frac=f, d_med_um=d, gsd=g, aspect=asp, irregularity=irr, n_per_mm3=n_v)
    crack = float(sample.get("crack_density", 0.0))
    # hot cracks: lengths of a few columnar grain lengths, openings 1-3 um (Martin 2017); along the build direction
    L = 60.0 + 4.0 * float(sample.get("grain_um", 10.0))
    cracks = dict(density_mm_mm2=crack, len_med_um=float(np.clip(L, 40, 400)), len_gsd=1.6, open_um=1.5,
                  orientation="build", tortuosity=0.25)
    return dict(pores=out, cracks=cracks, porosity=float(sample.get("porosity", sum(v["vol_frac"] for v in out.values()))))


def grain_model(sample: dict, campaign: str) -> dict:
    """Grain size and morphology of a part: equiaxed share (Al: the truth's nucleant-driven ``equiaxed``; Cu: from
    tempering by later passes and Fe-rich nucleation, assumed), columnar aspect ratio, <100> fiber spread."""
    al = campaign == "flaime_al"
    d = float(sample.get("grain_um", 10.0))
    if al:
        eq = float(np.clip(sample.get("equiaxed", 0.0), 0.0, 1.0))
        aspect = 4.0
        spread = 14.0                     # deg, <100> fiber spread of columnar grains (assumed; MRD 3-6)
        kam = 0.55 if sample.get("strength", {}).get("parts", {}).get("age", 0) > 0 else 0.7
    else:
        comp = sample.get("composition", {})
        temper = float(sample.get("temper", 0.35))
        eq = float(np.clip(0.08 + 0.55 * temper + 0.12 * min(comp.get("Fe", 0.0), 4.0) / 4.0, 0, 0.95))
        aspect = 5.0
        spread = 18.0
        kam = 0.45 + 1.2 * float(sample.get("beta_prime", 0.0))
    return dict(d_um=d, equiaxed_frac=eq, aspect=aspect, fiber_spread_deg=spread, kam_deg=kam,
                build_dir="z")


def phase_model(sample: dict, campaign: str, kind: str | None = None) -> dict:
    """The whole latent microstructure of a lot (kind 'powder') or part ('part')."""
    kind = kind or kind_of(sample)
    key = _key(sample, campaign, kind)
    if key is not None and key in _PM_CACHE:
        return _PM_CACHE[key]
    pm = _al_model(sample, kind) if campaign == "flaime_al" else _cu_model(sample, kind)
    if kind == "part":
        pm.update(pore_model(sample, campaign))
        pm["grains"] = grain_model(sample, campaign)
    else:
        pm["powder"] = powder_population(sample, campaign)
        pm["oxygen_ppm"] = sample.get("oxygen_ppm")
    if key is not None:
        if len(_PM_CACHE) > 4000:
            _PM_CACHE.clear()
        _PM_CACHE[key] = pm
    return pm


_PM_CACHE: dict = {}


def _key(sample, campaign, kind):
    try:
        c = tuple(sorted((k, round(float(v), 5)) for k, v in sample["composition"].items()))
        extra = []
        for k in ("porosity", "grain_um", "equiaxed", "beta_prime", "cell_um", "temper", "crack_density",
                  "satellite_frac", "oxygen_ppm", "cooling_K_s", "d50_um", "energy_ratio"):
            v = sample.get(k)
            if isinstance(v, (int, float)):
                extra.append((k, round(float(v), 6)))
        runs = tuple((round(r.get("d50_um", 0), 4), round(r.get("true_superheat_K", 0), 3), bool(r.get("failed")),
                      tuple(sorted((r.get("undissolved") or {}).items())))
                     for r in sample.get("runs", []))
        pores = tuple(sorted((k, round(v, 7)) for k, v in (sample.get("pores") or {}).items()))
        return (campaign, kind, c, tuple(extra), runs, pores)
    except Exception:
        return None


# ------------------------------------------------------------------------------------------------ calibration store
_CAL = None


def calib(instrument: str) -> dict:
    """The fitted error parameters for an instrument's fast mode (twin/instruments/calib_micro.json)."""
    global _CAL
    if _CAL is None:
        try:
            _CAL = json.loads(CALIB_PATH.read_text())
        except Exception:
            _CAL = {}
    return _CAL.get(instrument, {})


def calib_reload():
    global _CAL
    _CAL = None


def calib_write(instrument: str, params: dict):
    """Merge one instrument's parameters into calib_micro.json (file-locked: several calibrations may run)."""
    import fcntl
    lock = CALIB_PATH.with_suffix(".lock")
    with open(lock, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            cur = json.loads(CALIB_PATH.read_text()) if CALIB_PATH.exists() else {}
        except Exception:
            cur = {}
        cur[instrument] = params
        tmp = CALIB_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(cur, indent=1, sort_keys=True))
        os.replace(tmp, CALIB_PATH)
        fcntl.flock(lf, fcntl.LOCK_UN)
    calib_reload()


def seed_of(name: str) -> int:
    return zlib.crc32(name.encode()) & 0x7FFFFFFF


# ------------------------------------------------------------------------------------------------ sample builders
AL_PROC = dict(superheat_K=150, pour_mbar=200, amplitude=0.8, P_W=300, v_mm_s=1000, h_um=110, t_um=30, T0_C=150)
CU_PROC = dict(superheat_K=120, pour_mbar=220, amplitude=0.8, P_W=600, v_mm_min=600, feed_g_min=6)
GALLERY = {"flaime_al": {"AlSi10Mg": {"Si": 10.0, "Mg": 0.35}, "Scalmalloy": {"Mg": 4.6, "Sc": 0.7, "Zr": 0.3},
                         "7075": {"Zn": 5.6, "Mg": 2.5, "Cu": 1.6, "Cr": 0.23}},
           "onr_cu": {"70-30 Cu-Ni": {"Ni": 30.0, "Fe": 0.6, "Mn": 0.6},
                      "NAB": {"Al": 9.2, "Ni": 4.5, "Fe": 4.0, "Mn": 1.2}}}


def make_samples(campaign: str, design: dict, proc: dict | None = None, seed: int = 0, mode: str = "blown_large",
                 n_runs: int = 2, set_TL_offset: float = 0.0, truth=None):
    """A lot (with its atomizer runs) and a part made from it through the truth, as the campaign builds them (and
    as truth_al.reference_table / truth_cu.reference_table do). Returns (lot, part)."""
    al = campaign == "flaime_al"
    rng = np.random.default_rng(seed)
    if truth is None:
        truth = _truth(campaign)
    base = "Al" if al else "Cu"
    proc = dict(proc or (AL_PROC if al else CU_PROC))
    comp = {e: float(v) for e, v in design.items() if e in ATOM and e != base and v > 0}
    comp[base] = 100.0 - sum(comp.values())
    th = truth.thermo(comp)
    TL = (th["T_liquidus_C"] if al else th["liquidus_C"]) + set_TL_offset
    runs = []
    for _ in range(n_runs * 3):
        r = truth.atomize(comp, proc, TL, rng)
        runs.append(r)
        if sum(not x["failed"] for x in runs) >= n_runs:
            break
    good = [r for r in runs if not r["failed"]] or [dict(runs[-1], failed=False, usable_frac=0.5)]
    w = np.array([r["usable_frac"] * r["cut_frac"] + 1e-9 for r in good])
    w = w / w.sum()
    tc = {e: float(sum(wi * r["composition"].get(e, 0.0) for wi, r in zip(w, good)))
          for e in set().union(*[r["composition"] for r in good])}
    lot = dict(composition=tc, oxygen_ppm=float(sum(wi * r["oxygen_ppm"] for wi, r in zip(w, good))),
               satellite_frac=float(sum(wi * r["satellite_frac"] for wi, r in zip(w, good))),
               carbon_ppm=float(sum(wi * r.get("carbon_ppm", 0.0) for wi, r in zip(w, good))), runs=runs,
               campaign=campaign, design={e: v for e, v in comp.items() if e != base})
    if al:
        part = truth.build(lot, proc, rng)
    else:
        part = truth.deposit(lot, proc, mode, rng)
    part = dict(part, campaign=campaign, design=dict(lot["design"]), reuse=0)
    part["strength"] = truth.strength(part)
    if not al:
        part["corrosion"] = truth.corrosion(part)
    return lot, part


_TRUTHS = {}


def _truth(campaign):
    if campaign not in _TRUTHS:
        if campaign == "flaime_al":
            from twin.truth_al import AlTruth
            _TRUTHS[campaign] = AlTruth(0)
        else:
            from twin.truth_cu import CuTruth
            _TRUTHS[campaign] = CuTruth(0)
    return _TRUTHS[campaign]


def gallery_samples() -> dict:
    """{campaign: {alloy: (lot, part)}} for the figures and tests (AlSi10Mg, Scalmalloy, uninoculated 7075;
    70-30 Cu-Ni, NAB)."""
    out = {}
    for camp, alloys in GALLERY.items():
        out[camp] = {nm: make_samples(camp, d, seed=i) for i, (nm, d) in enumerate(alloys.items())}
    return out


def random_samples(campaign: str, n: int, seed: int = 0) -> list:
    """Representative (lot, part) pairs across the campaign's space and process window, for calibration: random
    feasible designs from twin.spaces, process settings from the design, a third of the atomizer melts set cold."""
    from twin.spaces import SPACES, REFERENCE
    sp = SPACES[campaign]
    designs = sp.sample(n, seed=seed)
    refs = list(REFERENCE[campaign].values()) + list(GALLERY[campaign].values())
    rng = np.random.default_rng(seed + 17)
    out = []
    for i, d in enumerate(designs):
        if i < len(refs):
            comp = dict(refs[i])
            proc = dict(AL_PROC if campaign == "flaime_al" else CU_PROC)
            for v in sp.process:
                if rng.random() < 0.5:
                    proc[v.name] = d[v.name]
        else:
            comp = {e: d[e] for e in sp.elements if d[e] > 0}
            proc = {v.name: d[v.name] for v in sp.process}
        off = -60.0 if rng.random() < 0.25 else 0.0
        mode = ["preplaced", "blown_small", "blown_large"][i % 3]
        try:
            out.append(make_samples(campaign, comp, proc, seed=seed * 1000 + i, mode=mode, set_TL_offset=off))
        except Exception:
            continue
    return out
