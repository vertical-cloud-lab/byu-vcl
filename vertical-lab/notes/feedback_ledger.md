# Every point Sterling has raised on #303 and PR #318, and where it stands

Sterling, 2026-11-07: "You probably still have a lot to do if you carefully comb through all my feedback here and do
some careful thinking, considering that this is meant to help us simulate as realistically as possible in order to
make things more seamless in an actual implementation."

This ledger is the comb-through. It covers every comment Sterling wrote on issue #303 (Oct 27 – Nov 3) and on PR #318
(Nov 3 – Nov 7). Each point is checked against this branch: the code, the notes and the committed renders, as of
round 10's start (`813e74e`). Status:

- ✅ done
- 🟡 partly done
- ❌ not done
- ↪ superseded by a later ask
- 💬 a question, answered

Round 10's outcome for each open point is in the last column.

## What is still open, and what round 10 does about it

| From | Point | Status before round 10 | Round 10's plan | Outcome (2026-11-07/08) |
|---|---|---|---|---|
| #303, Nov 3 | Three each of the OT-2, CubXL, H2D, A2L and A1 mini | ❌ Built only on the unmerged side branch `claude/issue-303-20261103-1726` (`39db74a`). The current lab has one OT-2, one CubXL, one H2D, one A1 mini and no A2L | lab stream: what adding them takes (trays, a third Shuttle, docks), as a plan for Sterling to decide | ✅ a plan, not a render: [`three_each.md`](three_each.md). 4-5 new trays and a third Shuttle either way, so the Aconity and the packaging station would move; for Sterling to decide |
| #303, Nov 3 | Scaling to 50 ft, an array of VLMs serviced by a rail | 🟡 On the same side branch: eight 15.15 m Shuttles and a UR10e on a rail. The rail was dropped on Nov 4 ("Just stick with the mobile manipulator setup"), and the array isn't in the long-form | open: a mobile-base version of the array | ❌ not started |
| #303, Oct 27 | "Design and build our own [VLM], including making sure it meets ASHRAE requirements" | ❌ never answered | vendors PR: `procurement/build_our_own_vlm.md` | ✅ #331: [`build_our_own_vlm.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/claude/issue-303-vendors-rfq/vertical-lab/procurement/build_our_own_vlm.md): buy the lift, build what sits on and around the trays |
| PR, Nov 3 19:45 | Real data in every visualization "wherever possible" | 🟡 The only measured data on screen are the c3k0n5 SEM images and the particle count from them. Every other panel is badged computed or illustrative | open: needs the lab's own measurements | 🟡 unchanged |
| PR, Nov 3 19:49 | The PCB line | 🟡 It has no reflow oven; tray H's right end was left free for one | lab stream, if cheap | ✅ a Puhui T-962A reflow oven on tray H (`e860058`) |
| PR, Nov 4 04:11 | Refit every model to footage, piece by piece | 🟡 Done so far: ten models, the rePowder (#327, first pass) and the 68FM-100 (AT6 footage, round 8). Not refitted: the nanoindenter, sieve shaker, glovebox, wire EDM, MX400 and the round-4 lab models. The VibroMet 2 is only a caption | repowder stream continues #327: clamps, fittings, door, viewport | 🟡 #327's second pass: the chamber door hinged at the back, the swing-bolt clamps, the viewport, a second held-out frame |
| PR, Nov 4 18:26 | A sideways tensile tester on a tray | 🟡 The zwickiLine Z5.0 TN fits, but at 5 kN it can't pull the route's 14.8 kN E8 bar. No horizontal frame with a published size reaches 15 kN | vendors PR asks Tinius Olsen, ADMET and ZwickRoell | 🟡 #331 drafts the question to all three makers; no answer yet |
| PR, Nov 5 00:37 | "Are there other things like that [the catch shelf], that you didn't address yet?" | 🟡 Round 9 left collisions: chapter 6 at 456 frames, chapter 4 at 19, chapter 3 at 7, chapter 7 at 1; chapter 5 and the MiR bodies weren't audited | prep stream (chapter 6) and checks stream (chapters 3, 4, 5 and 7, and the MiR bodies) | ✅ chapter 6: 456 → 0 frames, re-rendered; chapter 4: 19 → 0 of 1,028, re-rendered; chapters 3 and 7: 0 in the changed sub-steps, fixed in code, their renders older. The MiR bodies still aren't audited |
| PR, Nov 5 00:37 | "Self-inconsistency" (9:09) | 🟡 Fixed for 9:09 in round 8. Round 9 didn't re-render the set-up, services, hookups, bay-camera or finale clips, so they show round 8's coloured lids, the v2 doser and the bay without its floor | lab stream re-renders them; upkeep-model re-renders the finale | ✅ the set-up movie, services, hookups and bay-camera clips re-rendered on round 9's lab, and the finale. The set-up's first render showed tinted jars on trays N and O: fixed (`54c3bdb`) and re-rendered |
| PR, Nov 5 22:56 | The rePowder model faithful to the real machine (hinges, clamps) | 🟡 #327's first pass: the lid hinges at the back, the latch and the bolt. Chapter 2 still opens the lid about the old hinge | repowder stream continues #327; chapter 2 adopts it once #327 is merged | 🟡 as #327 stands; chapter 2 adopts it once #327 is merged |
| PR, Nov 5 22:56 | Tensile bars at several orientations through the EDM | 🟡 #328 has flat, vertical and 45° bars as figures. Chapter 5 animates flat and vertical bars; 45° isn't animated | open | 🟡 unchanged |
| PR, Nov 7 | Maintenance over the long term, in the workflows | ❌ new | upkeep-model and upkeep-clip streams | ✅ [`upkeep.md`](upkeep.md), the upkeep clip, and the finale with maintenance on screen |
| PR, Nov 7 | The doser cup raised close to the nozzle on a platform, or a funnel | ❌ new: the vessel's mouth is still 153-156 mm under the exit, as in v5 | doser stream | 💬 a block can't work in v5: the parked carriage is 12.6 mm over the HR-202i. The vial needs no funnel; the cups should have one per powder, designed and checked, not yet in chapter 1 ([`multidoser.md`](multidoser.md)) |
| PR, Nov 7 | Contacts, specs and RFQ answers for every part | ❌ new | vendors PR | ✅ #331, first and second pass: of 88 contacts, 45 verified, 27 partly, 16 unverified |

## Issue #303

| Date | Point | Status | Where |
|---|---|---|---|
| Oct 27 17:44 | An animated visualization like the org page's, in the repo's style: GIF and MP4, assembly and disassembly, real equipment models | ✅ | `animate.py`, `out/mp4/vlm_*.mp4` |
| Oct 27 18:09 | Could we design and build our own VLM to ASHRAE, given the safety risks? | ❌ never answered | round 10: vendors PR, `procurement/build_our_own_vlm.md` |
| Oct 27 18:32 | The arm should do an actual workflow, not move side to side | ✅ | every chapter since round 2 |
| Oct 27 18:32 | The latest multi-doser CAD from powder-doser | ✅ chain carousel v5 at `353dae7`, which is still PR #185's head | `carousel.py`, `multidoser/`, `notes/multidoser.md` |
| Oct 27 18:32 | The large bay opening; fine-tune against Kardex's images | ✅ 996 mm since round 7 | `vlm.py`, `notes/kardex_opening.md` |
| Oct 27 18:32 | Equipment loaded onto the trays one at a time before any workflow | ✅ | `animate.py loading`, `setup_lab.py` |
| Oct 27 18:32 | A UR10e (or UR7e or UR3e) instead of the PiPER, chosen for clearance | ✅ UR10e | `README.md` "The arm: why a UR10e", `reach.py` |
| Oct 27 18:33 | Show the clad VLM before the see-through one; upload to YouTube | ✅ | `vlm_assembly`; `out/youtube.md` |
| Oct 27 18:36 | The rePowder from DAL's best model | ✅ refined further in #327 | `repowder/model.py` |
| Nov 3 17:25 | Three OT-2s, three CubXLs, three H2Ds, three A2Ls, three A1 minis | ❌ only on the unmerged side branch `claude/issue-303-20261103-1726` | above |
| Nov 3 17:25 | Atomizer just off to the left, Aconity MIDI just off to the right, both facing inward | 🟡 left and right are kept. Since round 7 both face the aisle, where the MiR250s dock (`setup_lab.FLOOR_PLAN`), not each other | `setup_lab.py` |
| Nov 3 17:25 | Is the vial oriented correctly for the doser? | ✅ upright since round 9 | `notes/multidoser.md` |
| Nov 3 17:25 | Scaling to 50 ft with an array of VLMs on a rail | 🟡 side branch only | above |
| Nov 3 17:35 | OpenFlexure (delta and v7, reflectance) | ↪ built in rounds 3-5, then dropped at Sterling's request (Nov 5) | `openflexure.py` |
| Nov 3 17:35 | PIP with sample placement; desktop XRD opening and closing; desktop SEM with EDS and EBSD; gloveboxes; polishing; nanoindenter; furnace; small and full-size Instron; laser diffraction; wire EDM | ✅ all modelled and in the chapters | `instruments*.py`, `r8_*.py`, chapters 4-7 |
| Nov 3 17:35 | A rail as a backup, using Vention's CAD through the Pi | ↪ built (`instruments.RAIL`), then removed (Nov 4 18:26) | `notes/maintenance.md` |

## PR #318

### Nov 3 19:45: tray services, set-up, DAL's workflow, more instruments

| Point | Status | Where |
|---|---|---|
| Quick disconnects on the trays for gas, liquid and power; connect automatically in the bay | ✅ Stäubli CombiTac at each tray's back-right corner, mating sideways in each slot and in the bay | `services.py`, `notes/services.md` |
| Retractable cabling (a tether) | ↪ modelled in round 4, removed Nov 4 ("overcomplicates things") | |
| UPS as the alternative; an N₂ generator; self-contained chilled water; heat | ✅ a UPS on every tray; N₂ and the chiller beside the VLM; about 7 kW of heat worked out | `notes/services.md` |
| The whole lab set up from scratch: arms installed, every tray loaded | ✅ re-rendered each round. Round 9's version wasn't rendered | `setup_lab.py`; round 10: lab stream |
| Go through DAL for every workflow step | ✅ 17 steps mapped | `notes/dal_workflow.md` |
| Sieving the powder: an automated module, or the arm | ✅ a sieving cell with a tipper, plus the wash module (round 9) | `alloy_print.py`, `sieve_station.py` |
| A VHX with the LIBS module | ✅ VHX-7000 + EA-300, refitted | `instruments_char.py`, `notes/refine_vhx.md` |
| Desktop XRF | ✅ Bruker S2 PUMA | |
| A sixth OpenFlexure, in an array on a sub-tray | ↪ done, then dropped (Nov 5) | |
| Rail low on a pedestal versus a mobile manipulator; a warehouse version | ✅ studied (`out/rail_vs_amr.json`). Mobile base only since Nov 4 | `warehouse.py` |
| Find the real-VLM video | ✅ ck8QJhVqPiY, the long-form's opening | `out/footage/` |
| Upload the videos | ✅ | `out/youtube.md` |
| Plate out of the MIDI → wire EDM → tensile tester | ✅ chapter 5 | `alloy_workflow.py` |
| An automated packaging station with labels and fixturing | ✅ | `instruments_lab.py` (packaging) |
| The stream cameras: on the modules or the trays? An overhead one at the bay; several per tray | ✅ on the trays, plus one over the bay with its own sequence | `services.py`, `notes/services.md` |
| Cabling: tidy wired power | ✅ | `vlm_cabling` |
| The CubXL set up for corrosion, per DAL | ✅ DAL PR #180's deck | `cubxl_rig.py`, `notes/cubxl_corrosion.md` |
| Each machine shown at work inside, the rest faded, with real data such as SEM images | 🟡 cutaways throughout; the real data are only the c3k0n5 SEM images and the particle count | `data_panels.py` |
| Could a HIP fit on the VLM? | 💬 no: 1300 mm tall and 1100 kg | `README.md` |
| A freestanding DED machine | ✅ InssTek MX-Lab | |
| Stacked PRs for sub-agents | ✅ #320, #321, #327, #328 | |

### Nov 3 19:49: fabrication

| Point | Status | Where |
|---|---|---|
| Desktop LPBF on the VLM | ✅ SnowX SnowPod (tray I) | `fab_metal.py` |
| Any DED on a tray? | 💬 none fits at 727.5 mm. At 996 mm the MX-Lab fits by height, but its load per area is 2.3× the tray's rating | `notes/kardex_opening.md` |
| Resin printers | ✅ Form 4 ×2, Form Wash, Form Cure (tray G) | `fab_resin.py` |
| Automatic pick-and-place (open source) and a PCB stencil printer | 🟡 Opulo LumenPnP and DDM Novastar (tray H); no reflow oven yet | `fab_pcb.py` |

### Nov 3 21:08 – 21:16: charge cups, no disassembly, render style

| Point | Status | Where |
|---|---|---|
| Charge cups (Al and Cu), with the plugs going in, instead of a vial; the full alloy workflow | ✅ chapter 1 onwards | `alloy_charge.py`, `charge.py` |
| No need to take the equipment off at the end | ✅ | |
| Too much sheen | ✅ | `scene.py` |
| Furnace door swings the wrong way; OpenFlexure legs don't follow the stage; PIP platen distorted; grey bar through the disc | ✅ all four | round-4 fixes |

### Nov 4 04:04 – 04:34: bigger bay, refits, round 5, maintenance access

| Point | Status | Where |
|---|---|---|
| Does Kardex have a larger bay? | 💬 Kardex publishes only 727.5 mm. Sterling found Modula's Bay M (895 mm) and XL (1,295 mm); the model uses a used unit's 996 mm | `notes/kardex_opening.md`, `notes/lab_r8.md` |
| Refine the equipment from the SOP videos and others; register models to frames; use the Pi | 🟡 see the summary | `register.py`, `notes/refine_*.md` |
| "We can atomize far more than 80 grams": four charges, and the 400 cm³ crucible | ✅ | `notes/alloy_atomize.md` |
| Find Kardex's extended brochures | ✅ searched; only 727.5 mm is published | `notes/kardex_opening.md` |
| With a taller opening, what's enabled, e.g. the MX-Lab? | 💬 | `kardex_tall.py` |
| MuJoCo for the collisions | ✅ `interference.py`, plus FCL in `collide.py` | |
| The robot takes the sieve stack apart and depowders, with a second arm or clever hardware if needed | ✅ tipper, wash module, depowdering box | |
| Funnels allowed, but one per material | ✅ in round 5. v5 has no funnel; round 10 revisits it | doser stream |
| The rail's cable chain | ↪ done, then the rail went | |
| Stream cameras from real parts (robot-arms' Pi 5 models), adjustable | ✅ | `services.py` |
| A real balance, not a load cell (an A&D 0.1 mg) | ✅ HR-202i | |
| Cut to the lab's own atomizer footage: rods melting, the stream hitting the plate, the powders; the sieved Cu image | ✅ chapter 2's footage, and Gage's sieved NAB jars in chapter 3 | `out/footage/` |
| The press needs a sliding nest and an ejector | ✅ shuttle, ejector pin and catch ring | `vacuum_press.py` |
| How trays come out for maintenance, given the rail | 💬 Kardex's full tray extraction at the front, once the MiR drives off | `maintenance.py`; round 10 animates it (upkeep-clip) |

### Nov 4 05:03 – 06:55: arm collisions, the press, uploads, the long-form

| Point | Status | Where |
|---|---|---|
| The arm ignored collisions: through the MiR and the vial holder | ✅ FCL checks, IK branch choice and RRT-Connect; every chapter audited | `collide.py`, `notes/arm_collisions.md` |
| The plug pressed home to a tonnage, in a vacuum press: find a model and a video | ✅ Specac Atlas Autotouch 15T, 3.2 t under vacuum | `vacuum_press.py`, `notes/vacuum_press.md` |
| Upload every video | ✅ | `youtube_upload.py` |
| One long-form with chapters | ✅ each round since | `longform.py` |

### Nov 4 18:26: round 7's list

| Point | Status |
|---|---|
| Keyence monitor interference; remote in with a Windows x86 SBC | ✅ The controller *is* the monitor, so it stands sideways, with a PiKVM for remote use |
| AprilTags only facing up → cubes | ✅ |
| Show the UPSs and automatic hookups in storage and in the bay; layout effects | ✅ `vlm_hookups`; the tray plan includes the UPSs |
| The overhead bay camera: its own sequence, operator's view and its own view | ✅ `bay_camera` |
| Storage trays for samples, vials, cups and plugs | ✅ tray J |
| What are the yellow boxes? | 💬 power and network drops; now grey and labelled |
| Assume the 996 mm opening | ✅ |
| A glovebox on a tray | ✅ our design (tray K) |
| A tensile tester on its side on a tray | 🟡 zwickiLine Z5.0 TN, 5 kN |
| Trays used in real workflows, not just presented | ✅ chapters 4-7 |
| The atomizer interfered with the rail | ↪ the rail is gone |
| Why the OT-2? | ✅ tray A's liquid station for the corrosion screen (digital-wetlab PR #83) |
| CubXL volumes to real pipettes; DAL #180's configuration | ✅ |
| Why dose salt? Dose alloy precursors into charge cups and atomized powder for the CubXL | ✅ |
| Do the docks interfere with the lift? | 💬 no, `dock_lift_clearance` |
| Tray A's camera captures the room | ✅ moved |
| Remove the retractable line | ✅ |
| DAL's DAG, introduced gradually | ✅ `route_dag.py` |
| An autonomous CNC | ✅ Makera Carvera |
| A hardness tester | ✅ Mitutoyo HM-220 |
| The vacuum press appearing out of nowhere | ✅ loaded in the set-up |
| MiR storage: no insertion gap, too high | ✅ low pockets with lead-ins |
| The pressed cup unstable on the ejector | ✅ catch ring |
| Mobile manipulator only | ✅ |
| The atomizer lid's clamp; is the base heavy enough? | ✅ latch and bolt; ballast; two arms since round 9 |
| Gripper versus the sealing rod; dropping cups from height; a custom end effector | ✅ the slim tong |
| A camera on the gripper | ✅ RealSense D405 |
| Speed up the melt footage | ✅ 2× |
| Crucible automation is very hard | ✅ written up: `notes/crucible_automation.md`. The crucible stays a person's job |
| Fume hoods | ✅ Labconco ducted (floor) and Sentry Air ductless (tray M) |

### Nov 5 00:37: round 8's list

| Point | Status |
|---|---|
| 9:09 self-inconsistency | ✅ there, 🟡 elsewhere (see the summary) |
| Vibrant service-line flow over the top | ✅ muted in round 8 |
| The whole lab at speed: hour, day, week, month, with dataset sizes and alloys tested | ✅ `timelapse.py`. Round 10 adds maintenance to it |
| The Al 6063 melt-stream "dud" | ✅ replaced by the MS&T 2026 stream |
| Unsieved jar first, then sieved results after the sieving | ✅ |
| Candy-coloured powder | ✅ grey, then a legend, then grey |
| SEM of the Al the lab actually atomized | ✅ c3k0n5, DAL #157 |
| Bars would bounce off the catch shelf | ✅ comb with walled slots |
| Other things like that not yet addressed? | 🟡 this ledger |
| IPA rinse capped first | ✅ |
| Instron's automated loading from their videos; refit the model | ✅ AT6-style |
| An EOS-class printer, aerospace parts, ship-part repair | ✅ EOS M 400-4, Meltio cell |
| The mounting press and its full procedure; machining steps; a metal mount | ✅ MX400, steel mount faced on the Carvera |
| Elevated-temperature tensile tests | ✅ 200 °C |
| Swapping grits with the retaining ring | ✅ pre-loaded discs from a magazine; 🟡 the swaps collide (round 10 fixes) |
| What's the box right of the SEM? | 💬 Oxford AZtecOne, labelled |
| A conductive path from the mount to the SEM stage, mounted on the stage | ✅ grounded holder cup with a spring plunger |
| PIP and nanoindentation need a rigid backing | ✅ steel mount |
| The puck's weird self-motion; what's inside the indenter | ✅ |
| Laser diffraction too quick; show each technique's data | ✅ cutaway and PSD; data panels after each technique |
| MiniFlex angle, door, data, in line with a tray | ✅ |
| Powder XRD sample prep (Edison) | ✅ back-loading, no grinding |
| VHX alignment | ✅ |
| How the XRF sample moves inside | ✅ the S2 PUMA's own lift |
| Why OpenFlexures, and why both kinds? | ↪ dropped |
| Heat treat tensile specimens, not bars | ✅ E8 subsize dogbones |
| What was the CNC for? | ✅ facing the steel mount |
| No HF | ✅ Weck's reagent; ICP-MS sent out |
| Hundreds of powder jars | ✅ 581 |
| One long video, not many uploads | ✅ |

### Nov 5 15:29 – 15:35: the failed runs

| Point | Status |
|---|---|
| Why did it fail again? | 💬 The runner was shut down for overload, not by the token |
| At most three renders at once; pick up the other PRs; check for new comments every 30 min | ✅ `runner_guard.py`, improved again in round 10 |

### Nov 5 22:56: round 9's list

| Point | Status |
|---|---|
| The new multi-doser in vial and cup dosing, the balance underneath | ✅ v5 + HR-202i |
| 8:37 vial lying flat | ✅ upright |
| The CubXL magnet holds one cap: where's the other? | ✅ parked on an empty vial |
| Technicolor jars | ✅ in the clips re-rendered in round 9; 🟡 the set-up, services and finale (round 10: lab, upkeep-model) |
| A real floor under the tray in the bay | ✅ in the model and round 9's renders; 🟡 the same four older clips |
| Both arms to open the atomizer; heavy, low bases | ✅ |
| A PR to make the rePowder faithful | 🟡 #327, first pass |
| Automated sieve-stack cleaning | ✅ wash module |
| Is glass OK for powder jars? | 💬 yes for small lots, with PTFE-lined caps and grounded racks; metal for fines |
| MIDI door swings the wrong way | ✅ lifts about its top edge (from photos of the MIDI+; worth checking on the machine) |
| Mastersizer view | ✅ |
| 27:13: the S2 PUMA goes transparent too late | ✅ |
| 28:08: the vacuuming hits the machine | ✅ 400 mm lance |
| How the depowdering box holds the plate | ✅ zero-point chuck and swing clamps (our design) |
| Tensile bars at several orientations, and a PR for it | 🟡 #328; chapter 5 animates two of three |
| 32:20: can't see the tensile test | ✅ cutaway |
| The polishing holder holds nothing; the pistons press | ✅ |

### Nov 6 06:40: the org README GIF

| Point | Status |
|---|---|
| A GIF to replace the org page's | ✅ #329 |

### Nov 7 03:36: this round

| Point | Round 10 |
|---|---|
| How goes it; comb through everything | this ledger |
| A separate PR: contacts, specs, requests and answers to quote questions for every part, via the Pi | vendors PR |
| Maintenance over the long term, in the workflows | upkeep streams |
| The latest multi-doser with the scale; the cup raised on a platform closer to the nozzle, or a funnel | doser stream |
