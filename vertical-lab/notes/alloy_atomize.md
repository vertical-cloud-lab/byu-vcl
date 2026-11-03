## The alloy route, chapter 2: atomize (`alloy_atomize.py`)

The MiR250 brings the two charged 5N Al cups from the VLM to the rePowder. The UR10e opens the lid, loads the cups
round the sealing rod and shuts the lid. The machine, cut open at the furnace axis, washes, melts and atomizes the
charge. The arm then takes the powder container off onto the MiR.

| | |
|---|---|
| Clip | [GIF](../out/alloy_atomize.gif), [MP4](../out/mp4/alloy_atomize.mp4), [still](../out/alloy_atomize_still.png), sub-steps in [`alloy_atomize.json`](../out/alloy_atomize.json) |
| Starts | MiR250 at the VLM's opening (`animate.AMR_XY`), the two Al cups in the first two pockets of `charge.carrier()` at `animate.BUFFER_LOCAL` on the cabinet: where chapter 1 ends |
| Ends | MiR250 at world (−3487, −2230), yaw 0: square to the container's axis, 41 mm off the view port's flange, the hand-off chapter 3 (sieve, print) starts from. The container stands in a cradle at MiR-local (280, 10), seat z = 933 mm; the arm is parked. While the arm works the MiR stands 220 mm further out (y = −2450), because at y = −2230 the lid knob and the container's handle fall inside the UR10e's unreachable cylinder over its base; it drives onto the hand-off spot at the end |
| Scene | `line.py`'s layout as `alloy_workflow.py` builds it, the rePowder loaded part by part from `repowder/model.py` (the merged copy `animate.Lab` adds is hidden) |
| Ported | `Pool`, `Powder`, `Particles`, `stream`, `film`, `shake`, the heat colours, the argon volumes, `load_machine`/`set_cut`: #124's rePowder training animations (`atomizer-training/viz3d/steps.py` and `scene.py`, branch `claude/issue-124-20261003-0335`) |

**What the clip says, and where it comes from**

| On screen | Value | Source |
|---|---|---|
| Charge | 2 cups, 78.3 g, Al-10Si (Si powder at 74 % of each cavity) | `out/alloy_charge.json` (charge.py: #222's cup and plug, tapped Si 1.10 g/cm³) |
| Two cups a run | 80–100 g, the 100 g/run basis of the #161 purchase model | #222 README, "Rods around the piston" |
| Loading order | rod fitted and seated first, then the metal round it | GU500 manual pp. 15, 47–51, via #222 |
| Getting past the rod's adapter | straight down misses by 1.35 mm; tipped in, −0.09 mm (−2.1 to +0.5) | #222 README, `loading_margin()` |
| Gas wash | 3 cycles, pump to 4 × 10⁻¹ mbar, back-fill with 5N Ar, O₂ under 50 ppm | Ge et al. 2025; Ukabhai et al. 2025; GU500 pp. 18, 36, via #222 |
| Vent | Ø1/16 in through the plug: the air under it leaves on pump-down | #104, #222 |
| Coil | 10 kW, 7 kHz | GU500 p. 18, via #222 |
| Thermocouple | Type N in the crucible wall, to 1300 °C; the metal lags the reading | GU500 pp. 18, 36, via #222 |
| Pour | 200 mbar Ar over-pressure on the furnace; the melt's own head is ~7 mbar | Ge et al. 2025, via #222; #222's 2γ/r working |
| Nozzle | 0.7 mm for Al alloys, 0.5 mm standard; ours not identified | AMAZEMET training (#124 step 2a.2); #222 |
| Ultrasound | 40 kHz | #124 (the training's scan: one wide peak a little over 40 kHz) |

**Assumed, not measured**
- **The 750 °C hold.** Al-10Si is liquid above about 595 °C. The training holds 4047 (Al-12Si) at about 800 °C; 750 is
  a choice.
- **The pool's level** (8 mm above the floor cone's rim) is the 78 g charge's liquid volume in #222's scaled crucible,
  close to #222's 28–31 mm over the pour hole for two slugs.
- **How much powder shows** in the container: 78 g is a few millimetres deep in a Ø130 container, so the heap is
  drawn low.
- **The furnace/chamber gauges** (+150 mbar during the melt, +350/+150 at the pour) are the training's style of
  reading with #222's 200 mbar difference. They are not a recipe.
- **The cradle and the cup carrier on the MiR** are this model's; chapter 1 owns the carrier.
- **The arm opens the lid by its knob** and swings it 110° (the training animation's angle). Nobody has checked
  that a UR10e can do this on the real hood, nor whether the lid's latch needs releasing first.

**Open questions the clip raises**
- **Can a robot load the cups at all?** The 3/4 in cup only goes past the rod's adapter tipped, and #222 calls that
  too close to call (−0.09 mm). In the clip the arm lets go once the cup is past the adapter, and the cup slides
  down to the floor cone; the 2F-85's fingers still brush the adapter. Options:
  - a slimmer gripper;
  - a 5/8 in cup, which goes straight in (+1.83 mm);
  - ask AMAZEMET whether the adapter can be pinned on after loading.
- **The cups stand 70° apart** (110° and 180°) so that one sits on the cut plane and the cutaway shows its powder,
  plug and vent. #222's four places are 75° apart; at 70° the cups are 0.9 mm apart.
- **The vent can misbehave.** #222's README warns that a Ø1/16 in hole can draw powder out during pump-down
  and wick liquid Al under the 200 mbar over-pressure.
- **Taking the container off under argon** assumes the container's own valve closes and the flange clamp opens
  with the chamber still at over-pressure. The training vents the chamber first; check the order with AMAZEMET.
- **The MiR parks 260 mm off the view port** so the arm has room to reach the lid knob: closer, the knob falls
  inside the UR10e's unreachable cylinder over its base. Check the floor space in front of the real rePowder.

**Re-rendering only the ending.** `ATOMIZE_TAIL=52` counts the frames of the first 52 sub-steps without drawing them, so a changed ending renders in a minute. The ending was spliced onto the first render's MP4 at frame 1267 that way (ffmpeg trim + concat). The GIF is still the first render's: re-encoding the spliced GIF came out at 10–16 MB, so it ends just before the final 7 s re-drive. The MP4 and the JSON have the re-drive.
