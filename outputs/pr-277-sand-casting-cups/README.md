# Sand-casting the larger charge cups: Edison literature check

Asked on [PR #277](https://github.com/vertical-cloud-lab/byu-vcl/pull/277) on 2026-10-30: what would
sand casting the larger cups do to oxygen, purity and the quality of the metal? The atomizer and alloy
work has since moved to vertical-cloud-lab/digital-alloy-lab#179.

Two Edison `LITERATURE_HIGH` tasks, submitted 22:19 UTC and both `success`:

| Task | Answer | References | Full trajectory |
|---|---|---|---|
| Oxygen, hydrogen and purity | [`literature_oxygen_purity_answer.md`](literature_oxygen_purity_answer.md) | [refs](literature_oxygen_purity_references.md) | [`literature_oxygen_purity_task.json`](literature_oxygen_purity_task.json) |
| Metal quality after casting, alternatives | [`literature_cast_quality_answer.md`](literature_cast_quality_answer.md) | [refs](literature_cast_quality_references.md) | [`literature_cast_quality_task.json`](literature_cast_quality_task.json) |

`submit.py` holds the query text (also in `queries.json`), and `fetch.py` waits for the tasks and saves everything here.

## What it says

- **Oxide.** Wrought bar from a DC caster with in-line degassing and filtering is about 0.01 mm²/kg by
  PoDFA. Industrial Al-Mg-Si melts with 25-50 % scrap were 0.34-3.13 mm²/kg before flux refining
  (30-300 times more) and 0.05-1.11 after it
  ([Kovačec and Zupanič 2025](https://doi.org/10.5545/sv-jme.2025.1371)). A hand pour folds the oxide skin into the
  metal. In one model, a 1.5 m fall makes about 1,000 bifilms/mm³, and a 0.3 m pour does about as much
  damage as six minutes of rotary degassing
  ([Jarfors and Bogdanoff 2026](https://doi.org/10.21203/rs.3.rs-10838912/v1), a preprint). No source gives bulk oxygen in
  ppm for either route.
- **Hydrogen.** Solid bar is near the solid solubility, 0.03-0.05 mL/100 g (inferred, not measured on
  our bar). An undegassed air or gas-furnace melt carries 0.30-0.45 mL/100 g, and argon degassing brings
  it to 0.10-0.15. Green sand is 3-4 % water, which reacts with the metal and adds more. In mass terms
  this is under 0.5 ppm. The risk is porosity, and gas bubbling out of a 150-250 g melt on its way to a
  sub-mm nozzle. Nobody has measured that for a sand-cast charge.
- **Purity.** Fe from bare steel tools dissolves in the melt and can't be degassed, fluxed or filtered
  out (6063 allows 0.35 wt %). Mg oxidises off when melting in air. One recycled "6063-like" batch had
  0.24 wt % Mg against a 0.45 minimum. Sand grains and burnt binder end up in the skin, and flux leaves
  Na, K, Ca, Cl and F. Every melt becomes its own lot and needs its own analysis.
- **Castability.** 6063 is one of the worst alloys to sand cast: poor fluidity, hot tearing and
  shrinkage porosity. A356 and 4047 cast well, but a cup made of either changes the composition spread.
  A356 alone is about 7 % Si, above the top of the planned spread (3.4-4.3 % Si at 30 wt % powder).
- **Walls and fit.** Green sand needs walls of 3-5 mm. A 1.5-3 mm cast wall is high-risk and likely to
  leak through its porosity. Even impregnated die castings leak through narrow pore channels
  ([Réger et al. 2024](https://doi.org/10.1088/1757-899x/1313/1/012007)). Green sand holds about ±0.4 mm. Permanent moulds hold ±0.1-0.2 mm. The press
  fit needs about ±0.005 mm, so the bore and plug seat must be machined whichever way the cup is made.
- **Recommendation.** Use larger-diameter 6063 bar, or 6063 tube with plugs at both ends. If casting
  anyway: use sorted 6063 or certified pure Al only, rotary argon degassing, a ceramic foam filter,
  bottom gating at no more than 0.5 m/s, dry no-bake sand (or better, a coated graphite or steel
  permanent mould), BN-coated tools and a dedicated crucible, and machine off every mould-contact
  surface.

## Check of Edison's press-fit stress

The cast-quality answer puts the hoop stress from the plug at about 35 MPa, using
σ ≈ (δ/2r)·E·(r/t). That formula gives about 350 MPa for its own inputs, and it doesn't apply here
anyway. A thick-wall (Lamé) calculation for a solid Al plug in an Al cup (E = 70 GPa, ν = 0.33), at the
bore:

| Cup | Wall | Interference | Contact pressure | Hoop stress | von Mises |
|---|---|---|---|---|---|
| Thin-wall, 5/8 in bore | 1.59 mm | 13 µm (.0005 in) | 8.6 MPa | 47 MPa | 52 MPa |
| Thin-wall, 5/8 in bore | 1.59 mm | 20 µm (.0008 in) | 13.7 MPa | 76 MPa | 84 MPa |
| As-made, 1/2 in bore | 3.17 mm | 13 µm (.0005 in) | 19.4 MPa | 51 MPa | 63 MPa |
| As-made, 1/2 in bore | 3.17 mm | 20 µm (.0008 in) | 31.1 MPa | 81 MPa | 100 MPa |

Edison estimates the yield strength of as-cast 6063 at 50-90 MPa. It gives no source for that, and says
direct data are scarce. If it's right, a cast cup is at or past yield at the planned interference, even
with the as-made wall. Its verdict (the thin cast wall is impractical for the press fit) is right, but
for this reason, not because of its 35 MPa figure.

## Where the evidence is thin

Edison found no measurements of sand-cast feedstock in a vacuum-induction or ultrasonic atomizer. It
also found no bulk ppm O for 6063 bar or for sand castings, no Fe pickup rate from steel tools, no Mg
loss per melt for 6xxx, and no feedstock cleanliness spec for ultrasonic atomizers. A few numbers in
the answers have no citation (Fe saturation of 1.8-2.5 wt %, 1-5 vol % porosity, the as-cast 6063
strengths). The closing summary of the oxygen answer ("10-100x oxide, 2-4x hydrogen") also doesn't
match its own tables. The figures above come from the tables.
