# Tip handling arrives: tip racks, `pick_up_tip`, and why `mix` wanted gantry 149

*2026-08-06 → 2026-08-26 — 21 comments, migrated verbatim from [PR #171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171).*

Every comment below is reproduced exactly as posted, with its author and a link back to the original. `@`-mentions carry a zero-width space so that re-reading this file cannot notify anyone or re-trigger CI.

---

## @benwhitney5463 — 2026-08-06 21:08:12 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5209135743)

@claude write a protocol given these deck and gantry files. Note the first step should be moving to a park position so the pipette does not risk hitting the x rail. The goal of this protocol is to decap vial_1 then move the pipette over to the tip rack (not on the deck file) whose position is: x = 255.5, y = 33.5, z = 60. The pipette should drop down to z = 60 when over the x/y position to pick up the pipette tip. Once that is done, insert the pipette into vial_1 (note the pipette tip adds 35mm to the pipette). retract the pipette and cap vial_1. uncap vial_2 and insert the pipette into vial_2, retract, then cap it. continue this process until all 6 vials have been tested. Do not run the protocol, just write it. 
[sterling_6vials.yaml](https://github.com/user-attachments/files/30803786/sterling_6vials.yaml)
[cub_xl_ben_pipette_capper.yaml](https://github.com/user-attachments/files/30803792/cub_xl_ben_pipette_capper.yaml)

---

## @benwhitney5463 — 2026-08-07 00:13:05 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5210219073)

@claude address the above comment

---

## @claude[bot] — 2026-08-07 00:13:35 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5210223219)

**Claude finished @benwhitney5463's task in 22m 55s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/31133861643)

---
### Protocol written — but as measured, the pipette cannot reach any of the six vials

- [x] Download the two attachments, diff against the branch (both differ substantially — new deck frame, re-measured offsets)
- [x] Set up CubOS offline and check how tips are modeled (`pick_up_tip` + `TipRack.tip_length` → tracked tip extension)
- [x] Work out the tip-extension geometry (35 mm tip carried through motion **and** validation)
- [x] Write the protocol — park first, then per vial decap → insert → retract → cap, tip pickup after vial_1's decap
- [x] `validate_setup` + `run_protocol --mock` (fails on the reach blocker as written; a +30 mm X shift passes and mock-runs 28/28)
- [x] Commit and push (`c4672eb`)

Per your instruction, **nothing was sent to the CubXL** — this is written and offline-checked only, against current CubOS `main` (the Pi's `cbc33dc` checkout is an ancestor with zero capper/pipette engine changes since, so behavior matches the Pi + its two local patches).

Wrote [`cubos/configs/protocol/vcl/capper_decapper_tip_test.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/c4672eb/cubos/configs/protocol/vcl/capper_decapper_tip_test.yaml) — 28 steps: home → pipette to a mid-deck park (your requested first move, explicit `travel_z` so it never drops near the X rail) → decap vial_1 → `pick_up_tip` at (255.5, 33.5), nozzle pressing to deck Z 60 exactly as you specified → insert → retract → cap → same for vials 2–6 → end parked.

### 🔴 Blocker: deck X ≈ 113 is 22 mm past the pipette's reach

The pipette is mounted `offset_x: +135.0`, so the lowest deck X its tip can ever reach is **135.0** (gantry X 0 — a physical hard stop, not a soft limit). Every vial in `sterling_6vials.yaml` is at deck X 112.5–113.0, so all 12 insert/retract moves need gantry X −22.0/−22.5:

```
pipette -> vial_1_insert.location.target: gantry (-22.0, 31.5, 75.0) violates x_min=0.0
```

The decap/cap steps are fine (capper has zero XY offset) and the tip pickup is fine (rack → gantry X 120.5). Only the insertions are blocked — same shape as the old vial_1 Y-reach problem, now on X for the whole row. Options:

- **Shift the vial holder ≥ +22.5 mm in +X and re-measure.** I tested a uniform +30 mm on every vial's `location.x` (deck X ≈ 143, gantry X ≈ 8) on shifted copies: `RESULT: PASS` and a clean 28-step mock run. After the physical shift, update both the deck X values and the matching `vial_N_insert`/`vial_N_retract` X in the protocol.
- Or remount the pipette closer to the capper and re-measure `offset_x`.

I left vials 1–6 in the file as you asked, with the failure and fixes documented in the header, so `validate_setup` tells you the same thing.

### How the 35 mm tip is handled

I added one thing to your deck file: a 1×1 `tip_rack` labware at (255.5, 33.5), `pickup_z: 60.0`, `tip_length: 35.0`. That's because CubOS only models an attached tip's length through `pick_up_tip` + a `TipRack` — a raw `move` to the rack would leave both the runtime and the validator blind to the extra 35 mm. With it, after pickup every pipette deck-frame Z in the protocol means the **tip end**: insert Z 40.0 commands gantry Z 75.0, verified in the mock log. Insertion is 15 mm below the Z 55.0 rim, so only the tip enters — the nozzle stays 20 mm above the rim. If your rack is physically bigger than one tip, tell me the layout and I'll model it properly.

### The validator caught something real: no final `home` with the tip on

A closing `home` (like the previous protocol had) puts the tip end at deck (515, 291, **86**) in the homed corner — inside the Cub XL right X-max rail box (top Z 100), and `validate_setup` flags exactly that. So the protocol ends **parked mid-deck** at (250, 150) with the tip end at Z 80. Pull the tip off by hand there, then home. Related caveat, documented in the header: with the tip attached, never add pipette steps that travel at `safe_z` (deck-target `move`, `measure`, `aspirate`, `drop_tip`) — `safe_z` is applied in the instrument-tip frame, so 114 + 35 = gantry 149, which is 25 mm past the machine's Z travel. Named positions with explicit `travel_z`, as written, are the only safe pattern for a tipped pipette.

### ⚠️ Eyeball this before any hardware run: the tip sweeps a corridor 35 mm below every capper move

Same rigid-coupling issue as the 2026-08-03 X-rail drag, made worse by the tip. During every decap/cap **after** the tip is attached, the tip end passes through deck Z **~16** (nozzle Z 51) at x = vial_x + 135 ≈ **248**, y = vial_y + 13, and through Z **62** across x ≈ 248–260 during capper transit/park. The offline validator cannot see any of this — it never models the passive instrument. Two specifics:

- Your tip rack at (255.5, 33.5) sits **inside that corridor in X**. The closest engage shadow passes at (248, 57.5) — 24 mm away in Y — so a single tip clears, but anything extending ≥ ~20 mm in +Y from the tip position gets hit at tip-end height. Relocating the rack to deck X ≥ 300 removes the hazard entirely.
- Please confirm the strip x ≈ 240–275, y ≈ 20–240 is empty above deck Z ~10 before running. (If the holder shifts +30 mm in X, the corridor moves to x ≈ 278.)

### Numbers

| | |
|---|---|
| Vial rim | deck Z 55.0 (bare-vial `location.z` **is** the rim in this deck format) |
| Tip pickup | nozzle to (255.5, 33.5, 60.0), gantry (120.5, 20.5, 60.0) — as specified |
| Insert | tip end Z 40.0 → gantry 75.0 (15 mm into an 83 mm vial) |
| Tipped transit | tip-end Z 80.0 → gantry 115.0, under `z_max` 121 and above cap tops |
| Capper engage | deck 68 (rim 55 + `engage_depth_mm` 13) → gantry 51 with `depth: −17` |

### Committed — [`c4672eb`](https://github.com/vertical-cloud-lab/byu-vcl/commit/c4672eb)

- [`cubos/configs/protocol/vcl/capper_decapper_tip_test.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/c4672eb/cubos/configs/protocol/vcl/capper_decapper_tip_test.yaml) — the protocol, with all of the above in its header
- [`cubos/configs/deck/sterling_6vials.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/c4672eb/cubos/configs/deck/sterling_6vials.yaml) — your vials byte-identical, plus the `tip_rack` entry
- [`cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/c4672eb/cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml) — your 2026-08-06 attachment, verbatim
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/c4672eb/cubos/README.md) — marked the old capper test as passed on hardware, added this protocol's status

**Not done:** nothing ran on hardware and no connection to the Pi was made. The X-reach fix is physical and yours to make — say the word once the holder (or pipette mount) has moved and the deck is re-measured, and I'll update the numbers and re-validate. The tip rack is modeled as a single tip from the three numbers you gave; update me if it's a larger rack.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @jarrettshupe — 2026-08-08 00:53:50 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5223680699)

@claude I want to make the same protocol as the one above, but with a few changes. 
Here are the new files: 
[j_config_1.yaml](https://github.com/user-attachments/files/30848429/j_config_1.yaml)
[cub_xl_ben_pipette_capper.yaml](https://github.com/user-attachments/files/30848437/cub_xl_ben_pipette_capper.yaml)
Here are the new coordinates for the pipette tip: x: 262.460, y: 32.792, z: 59.152
Here are some things to keep in mind: The z position on each vial is the z coordonate where the capper_decapper should be engaging with the vial caps to pick them up. Set the engage depth with that in mind. (the engage depth should already be what it needs to be, so you might only have to change it by a millimeter).

The pipette tip position measured with the pipette on the pipette tip, but the reference instrument was the capper_decapper, so instead of sending the pipette to that exact position you will need to offset it by the distance from the pipette to the capper_decapper.

---

## @claude[bot] — 2026-08-08 00:54:11 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5223682486)

**Claude finished @jarrettshupe's task in 15m 24s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/31231321631)

---
### Protocol written — `capper_decapper_tip_test_j1.yaml`, validated offline, 28/28 mock

- [x] Download the two attachments, diff against the branch (gantry recalibrated + pipette physically remounted; brand-new deck)
- [x] Set up CubOS offline (`main` @ `3ff7e65`) and read the source for the frame conventions your measurements were taken in
- [x] Work out the geometry (engage depth, capper-frame → pipette-frame tip conversion)
- [x] Write the protocol + commit the deck/gantry configs
- [x] `validate_setup` → **PASS** · `run_protocol --mock` → **28/28 steps**
- [x] Commit and push (`5d7baf5`)

Per Ben's standing instruction, **nothing was sent to the CubXL** — written and offline-checked only.

Wrote [`cubos/configs/protocol/vcl/capper_decapper_tip_test_j1.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/5d7baf5/cubos/configs/protocol/vcl/capper_decapper_tip_test_j1.yaml) — 28 steps: home → pipette to mid-deck park first → for each vial: decap → (tip pickup once, after the first decap) → insert → retract → cap → end parked with the tip on. Also committed [`j_config_1.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/5d7baf5/cubos/configs/deck/j_config_1.yaml) (your vials byte-identical + a `tip_rack` entry) and [`cub_xl_ben_pipette_capper.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/5d7baf5/cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml) (three changes, marked `CHANGED` inline).

### The engage depth needed 4.25 mm, not 1 — here's why

I checked what the jog widget actually reports before trusting either number: it displays **raw work coordinates (WPos), no instrument offset or depth applied** (`GantryPositionWidget` shows `work_x/y/z` at 3 decimals — the precision of your values). CubOS commands the engage at `gantry_z = location.z + engage_depth_mm + depth`, so with your `location.z` being the measured engage WPos, the right value is `engage_depth_mm = −depth = `**`17.248`** — that makes the commanded plane reproduce each vial's own measurement *exactly*. The old `13` was calibrated against Ben's deck, where `location.z` meant the vial **rim** (a different convention); keeping it would have pressed the head 4.25 mm past your measured plane on every engage. The mock trace confirms it lands to the micron:

```
Moving PawduinoCapper to (212.143, 106.365, 71.948) -> gantry (212.143, 106.365, 54.700)   # vial_2
Moving PawduinoCapper to (212.143, 137.615, 71.543) -> gantry (212.143, 137.615, 54.295)   # vial_3..7
```

### The tip position, converted as you described

Your (262.460, 32.792, 59.152) is a capper-frame (= raw WPos) reading, so the pipette deck-frame target is WPos + the pipette↔capper offset **(+51.97, +12.0)** in XY; Z passes through unchanged because the pipette's `depth` is 0. That lives in the deck's `tip_rack` entry as (314.430, 44.792), `pickup_z 59.152`, `tip_length 35`. The mock commands the gantry to **exactly your measured numbers**:

```
Moving OpentronsPipette to (314.430, 44.792, 59.152) -> gantry (262.460, 32.792, 59.152)
```

### 🔴 One change I made beyond your two: capper `park_position` [125, 50] → [212.143, 40.0]

The remount put the pipette only 51.97 mm from the capper, and every `decap`/`cap` ends with a hardcoded park move at capper `safe_z` (gantry 96.75) — where the attached tip end rides at WPos **61.75, ~10 mm below cap-top height (~71.5)**. With the park off-column at [125, 50], those transits are diagonals whose passive-pipette path crosses the capped-vial column — e.g. returning from vial_7, the tip passes within ~1 mm of vial_4's cap edge, below its top. Parking at the vial column's own X makes every capper transit a pure-Y move: the trace shows the head shuttling at constant X 212.143, with the passive pipette holding X 264.1 — 38 mm clear of the vials, 50 mm clear of the rack. No offline check models the passive instrument, so `validate_setup` can never catch this. (Third change: `serial_port` COM5 → `/dev/ttyUSB0` for the Pi, as usual.)

### Things to know before anyone runs it

- **Deck keys vs. labels are off by one.** Your deck's keys are `vial_2`…`vial_7` but the `name:` fields say vial_1…vial_6. CubOS resolves protocol targets by **key**, so `decap: vial: vial_2` opens the physical vial labeled "vial 1". The protocol uses the keys, with the physical label commented at every block.
- **Insert depth is derived, not measured.** Your deck gives engage planes, not rims. From the hardware-verified 2026-08-03 relation (rim = engage WPos + 4.25), your rims sit near WPos 58.5–59; insert is tip-end Z 44.0 (~14.5 mm in, nozzle ~20 mm above the rim), tipped transits at travel_z 82.0 (gantry 117, under z_max 120.99, ~10 mm above cap tops).
- **Eyeball the strip x ≈ 255–275 before a hardware run.** During every engage the passive pipette's tip end descends to WPos **~19.3** at deck X ~264 — 31 mm lower than anything the 2026-08-03 runs swept. The vial holder must not extend ~52 mm in +X from the vial centers at that height, and the X-rail structure that dragged the old mount (then at deck X ~297) must be clear of X ~264.
- The protocol ends **parked mid-deck with the tip attached** (a `drop_tip` would travel at safe_z in the tip frame = gantry 149, past the machine's Z travel — same trap as before). Pull the tip off by hand, then home.

### Committed — [`5d7baf5`](https://github.com/vertical-cloud-lab/byu-vcl/commit/5d7baf5)

- [`cubos/configs/protocol/vcl/capper_decapper_tip_test_j1.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/5d7baf5/cubos/configs/protocol/vcl/capper_decapper_tip_test_j1.yaml) — the protocol, full frame derivation + pre-run checklist in the header
- [`cubos/configs/deck/j_config_1.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/5d7baf5/cubos/configs/deck/j_config_1.yaml) — your six vials byte-identical, plus the converted `tip_rack`
- [`cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/5d7baf5/cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml) — your recalibrated attachment with the port, engage-depth, and park changes documented inline
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/5d7baf5/cubos/README.md) — status section; note that the older sterling configs predate the remount and no longer describe the machine

**Not done:** no hardware run and no connection to the Pi. The rim/insert depth and cap-top clearance are derived from Ben's 2026-08-03 numbers rather than measured on your holder — if your caps or holder differ much from Ben's, say so and I'll re-derive. When you want it run on the CubXL, ask with the run request explicitly.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-08-24 23:58:35 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5403089570)

@claude add a vial rack to this deck file. take the dimensions and tip locations from the specs on CubXL docs. the position of the bottom-right tip is x = 265 y = 1 given this gantry file. This coordinate is when the pipette is hovering over the pipette tip (but the capper / decapper is the reference instrument so take that into account). 
[cub_xl_ben_pipette_capper.yaml](https://github.com/user-attachments/files/31397472/cub_xl_ben_pipette_capper.yaml)
[sterling_6vials_tiprack.yaml](https://github.com/user-attachments/files/31397474/sterling_6vials_tiprack.yaml)

---

## @claude[bot] — 2026-08-24 23:59:01 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5403092518)

**Claude finished @benwhitney5463's task in 16m 55s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32791699664)

---
### Tip rack added to `sterling_6vials_tiprack.yaml` from the CubXL docs spec — validated offline, committed

- [x] Download the two attachments, diff against the branch
- [x] Find the rack dimensions / tip locations in the CubXL docs
- [x] Convert the (265, 1) capper-frame anchor into the pipette's deck frame
- [x] Add the rack to the deck file, validate offline with CubOS
- [x] Commit and push (`b73d281`)

Per the standing rule, **nothing was sent to the CubXL** — offline validation only, no connection to the Pi.

One reading note: you wrote "vial rack," but every detail — *tip locations*, *bottom-right tip*, *pipette hovering over the pipette tip*, and the deck's own `_tiprack` filename — describes the pipette tip rack, so that's what I added. If you also want a second rack of *vials*, give me its anchor and I'll add that too.

### The spec, from the CubXL docs

[`docs/deck.md`](https://github.com/Ursa-Laboratories/CubOS/blob/main/docs/deck.md) prescribes exactly this workflow: geometry comes from a registered labware definition, and the deck file supplies only the measured calibration. The registered CubXL rack is [`ursa_tip_rack`](https://github.com/Ursa-Laboratories/CubOS/blob/main/packages/core/src/cubos/deck/labware/definitions/ursa_tip_rack/TipRack.yaml) — **2 columns × 15 rows = 30 tips, 8.5 mm pitch on both axes, body 66 × 138 × 22 mm**. So the deck entry is `load_name: ursa_tip_rack` plus your measured numbers, and the loader derives all 30 tip positions — none are hand-typed.

### The anchor, converted as you described

Same arithmetic as Jarrett's tip conversion on 2026-08-08, with your recalibrated offsets: the jog display reads the reference instrument's frame (capper, offset 0/0 = raw WPos), so the pipette deck-frame coordinate is WPos + pipette offset (52.0, 12.0):

```
(265.0 + 52.0, 1.0 + 12.0) = (317.0, 13.0)  ->  calibration.a1  (the bottom-right tip = tip A1)
```

Verified through the CubOS loader: commanding the pipette to `tip_rack.A1` sends the gantry to **exactly (265.0, 1.0, 60.0)** — your measured point, reproduced. The derived grid: column 1 at x 317.0, column 2 at x 308.5, rows A–O at y 13.0 → 132.0; all 30 tips inside the working volume (pipette gantry x {256.5, 265.0}, y [1.0, 120.0]). Note row A sits exactly **1.0 mm above the Y soft limit**.

### ⚠️ The one thing derived instead of measured

Two-point calibration needs `a2`, and you measured one point. I set `a2` one 8.5 mm column step in **−X** of `a1` (308.5, 13.0), which assumes the rack sits square to the machine axes and its second column is *left* of the measured tip ("bottom-right" in Operator-UI orientation). Rows then advance +Y automatically (the legacy convention — `TipRackYamlEntry` has no `row_direction` field, so this is forced, and it's the direction we want). **If the rack is actually mirrored** (your measured tip is bottom-*left*), the fix is one number: `a2.x: 308.5 → 325.5`. A 30-second jog over any second tip (say the far corner, should read WPos ≈ (256.5, 120.0)) would confirm squareness too — worth doing before the first pickup.

### Z values — flag before hardware

| | |
|---|---|
| `pickup_z: 60.0` | Carried from your 2026-08-06 measurement ("drop down to z = 60"). Justified because vial rims read z 55 under both that calibration and this one, so the Z datum agrees — but no fresh Z came with (265, 1), so **confirm by jog before the first hardware pickup**. |
| `tip_length: 35.0` | Your measured tip extension. The definition's 59.3 is a placeholder it explicitly says to override. |
| `drop_z: null` | Overrides the definition's 174.8 — a PANDA-frame number beyond this machine's Z travel that would otherwise silently ride along and poison any future `drop_tip`. Tips still come off by hand. |

`tip_present` defaults to all 30 loaded — if the physical rack is partially consumed, mark those slots false (or refill) before the first state-tracked run.

### Validation

`validate_setup` **PASS** (12 targets) and a 7-step `--mock` run: home → bare-nozzle hovers over all four corner tips (A1, A2, O1, O2) → `pick_up_tip: tip_rack.A1` → tipped move at travel_z 80. The smoke protocol lives in `/tmp` only — deliberately not committed, so this session adds nothing hardware-runnable.

### Gantry file + two heads-ups

Committed [byte-identical to your attachment](https://github.com/vertical-cloud-lab/byu-vcl/blob/b73d281/cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml) — the first rev that already carried `/dev/ttyUSB0`, so no edit at all was needed.

- **GRBL settings check:** the file expects `max_travel` 389.333 / 235.0 / 125.0, but the controller last reported (2026-08-20) `$130/$131/$132` = 389.693 / 281.218 / 123.99. If your recalibration flow rewrote the controller, fine; if not, the next hardware run will refuse to connect with *"Critical GRBL settings mismatch"*. The Y travel shrank 46 mm — confirm that's deliberate.
- **Capper shadow during pickups:** the capper head rides 52 mm in −X of the pipette, so tip pickups sweep it over the strip deck x 256.5–265 at deck Z ≈ 44.1 — about 15 mm left of the rack body's edge (≈ x 279.7). Eyeball that strip empty; no offline check models the passive instrument.

### Committed — [`b73d281`](https://github.com/vertical-cloud-lab/byu-vcl/commit/b73d281)

- [`cubos/configs/deck/sterling_6vials_tiprack.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b73d281/cubos/configs/deck/sterling_6vials_tiprack.yaml) — your six vials byte-identical + the `tip_rack` entry, full derivation and the unverified assumptions in the header
- [`cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b73d281/cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml) — your 2026-08-24 recalibration, verbatim
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b73d281/cubos/README.md) — status section; notes that the j_config_1 numbers now predate this recalibration

**Not done:** no hardware run and no Pi connection. Rack squareness, the −X column direction, and `pickup_z` are the three unverified assumptions — all called out in the deck header. When you want a protocol against this deck (or the same decap → tip → insert → cap sequence retargeted at it), ask and I'll write it; per the standing rule I'll only run it when you explicitly say so.

--- · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-08-25 00:40:05 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5403396903)

@claude using that deck and gantry file, write a protocol based on this file
[capper_decapper_test.yaml](https://github.com/user-attachments/files/31398089/capper_decapper_test.yaml)
name is pipette_test. You will need to change the positions of each vial according to the deck file, and please add a pick_up_tip command to tip_rack.A1, and add a mix command in vial_1. Then drop the tip at the park position before moving on to decapping and capping the rest of the vials. Please let me know if I need to change anything in the deck file when it comes to drop_z.

---

## @claude[bot] — 2026-08-25 00:40:31 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5403401043)

**Claude finished @benwhitney5463's task in 20m 40s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32794549632)

---
### `pipette_test.yaml` written — validate_setup PASS, 27/27 mock. And the `drop_z` answer is: leave it alone — no deck change needed

- [x] Download the attached base protocol (it's the 2026-08-03 sterling-deck rev; all positions remapped to the new deck)
- [x] Read the b73d281 deck (`sterling_6vials_tiprack.yaml`) + gantry (`cub_xl_ben_pipette_capper.yaml`)
- [x] Set up CubOS offline at the Pi's commit `cbc33dc` (and cross-checked `main`); read the `pick_up_tip`/`mix`/`drop_tip` source
- [x] Work out the geometry — found and proved a hard blocker for the literal `mix:`/`drop_tip:` commands
- [x] Write `pipette_test.yaml` — same physical sequence via primitives that do validate
- [x] `validate_setup` → **PASS** (16 targets) · `run_protocol --mock` → **27/27 steps**
- [x] Answer the `drop_z` question
- [x] Commit and push (`43e7fd5`)

Per the standing rule, **nothing was sent to the CubXL** — written and offline-validated only, no Pi connection.

Wrote [`cubos/configs/protocol/vcl/pipette_test.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/43e7fd5/cubos/configs/protocol/vcl/pipette_test.yaml) — 27 steps: home → pipette to park → decap vial_1 → `pick_up_tip: tip_rack.A1` (descends to your measured gantry (265, 1, 60) — re-verified through the loader) → three mix strokes inside vial_1 → retract → tipped move to the park position → **breakpoint: pull the tip off by hand, press Enter** → cap vial_1 → decap+cap vials 2–6 → home. Vial positions all come from the new deck (x 187, y 26–191, rim z 55).

### 🔴 Why there is no literal `mix:` or `drop_tip:` command in the file

I wrote the literal version first and ran `validate_setup` on it. It cannot run on this machine:

```
step 6 (mix): mix 'vial_1' safe_z gantry z=149.0 is outside working volume [0.0, 122.0] for instrument 'pipette'.
step 8 (drop_tip): drop_tip 'tip_disposal' safe_z gantry z=149.0 is outside working volume [0.0, 122.0] for instrument 'pipette'.
```

Every engage-based pipette command (`mix`, `drop_tip`, `aspirate`, `transfer`…) travels at safe_z **applied in the tip frame** — with the 35 mm tip that's 114 + 35 = **gantry Z 149** on a machine whose Z tops out at 122. Unlike `move`, these commands take no `travel_z`, so no protocol or deck edit can route around it. Lowering `safe_z` doesn't work either: a tipped engage needs safe_z ≤ 87, but capper transits ride at safe_z − 15.935, which at 87 is deck Z 71 — level with the cap tops (~68–70). The window is empty. This is identical at the Pi's `cbc33dc` and current CubOS `main`; it's a third upstream limitation to raise with Ursa (engage commands need a `travel_z`, or travel clamped to `z_max − tip extension`).

There's a second, independent reason the substitutions are actually more honest: **the pipette is `offline: true` / `port: ''`** in this gantry file. A real `mix:` would have pantomimed the plunger (no liquid moves), and a real `drop_tip:` would have *reported success while leaving the tip physically on the nozzle* — the ejector never fires. So: mix = three gentle tip-frame Z strokes (40↔48, 15 to 7 mm below the rim, XY fixed — motion-wise the same test), and the drop = a tipped move to the park spot + `breakpoint` while you pull the tip off.

### Your `drop_z` question — **no deck-file change needed; leave `drop_z: null`**

Three findings from the source, in decreasing order of surprise:

1. **No command reads the tip rack's `drop_z` at this CubOS version.** I grepped the whole engine: it appears only in the schema and in a bounding-box derivation.
2. A runnable `drop_tip` doesn't use the rack at all — it targets a separate **`tip_disposal`** deck entry (a labware type that exists for exactly this) and ejects at *that entry's own `location.z`*. That's the future deck change, not `drop_z`.
3. Setting `drop_z` today is mildly harmful: when both are set, the rack's modeled height becomes `|pickup_z − drop_z|`, distorting its bounding box.

When (a) the pipette goes online and (b) the CubOS travel fix lands, the whole deck edit is a ~6-line `tip_disposal` entry at the park coordinates — say the word then and I'll add it; I already confirmed one loads and resolves correctly.

### Safety structure worth knowing before you run it

- **No capper motion happens while the tip is on** (steps 4–14 are pipette-only, and the breakpoint comes *before* `cap vial_1`). This is load-bearing: every decap/cap ends parked at [125, 50] at gantry Z 98.065, which hangs the passive pipette at deck (177, 62) — a 35 mm tip's end would be at Z 63, *below* cap-top height and only **10.4 mm from vial_2's axis**. A capper park move with the tip on rams the tip into vial_2's cap. Bare nozzle clears by ~28 mm.
- **Run it from a foreground terminal (your normal SSH session), not nohup/the API server.** In a non-interactive run CubOS logs `Breakpoint skipped because stdin is not interactive` and *continues* — straight into the capper motion above with the tip still on. (Confirmed in the mock log.)
- **Vials 2–6 are decap+cap only, no pipette insertion** — your wording, and also the only honest option: after the hand removal the engine still models the tip as attached (nothing runnable clears it), so any later pipette Z would aim 35 mm high. If you want tip-in-vial insertions for all six, that's a different structure — keep the tip on the whole run, move the capper's `park_position` out of the vial column first, remove the tip at the end (the j1 protocol's pattern). Ask and I'll write it.
- Eyeball strips (the validator never models the passive instrument): capper head sweeps x ≈ 118–135 down to deck Z ~59 during the vial_1 strokes, and descends to Z ≈ 44 over (256.5–265, 1) during the tip pickup; the bare nozzle rides at Z ~52 through x ≈ 239 during capper engages.
- `pickup_z: 60.0` is still the un-re-verified 2026-08-06 number — worth the 30-second jog check before the first real pickup. Each run consumes A1 in the model; refill the slot or retarget `pick_up_tip`.

### Committed — [`43e7fd5`](https://github.com/vertical-cloud-lab/byu-vcl/commit/43e7fd5)

- [`cubos/configs/protocol/vcl/pipette_test.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/43e7fd5/cubos/configs/protocol/vcl/pipette_test.yaml) — the protocol; the full derivation, the verbatim violations, and the tip-on invariant are in its header
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/43e7fd5/cubos/README.md) — status section for this protocol

**Not done:** no hardware run and no Pi connection (per your standing rule — ask explicitly when you want it run). The deck and gantry files are untouched. The literal `mix:`/`drop_tip:` remain impossible on this machine until the CubOS engage-travel limitation is fixed upstream and the pipette is brought online — neither is a config edit.

--- · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-08-25 23:39:52 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418480213)

@claude visibly, the gantry can move freely above all obstacles on the deck with a pipette tip attached (according to the gantry this is at z = 122). Why does the mix command require the pipette to go higher (z = 160), and is there any way I can change that.

---

## @claude[bot] — 2026-08-25 23:40:17 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418484459)

**Claude finished @benwhitney5463's task in 22m 0s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32911771091)

---
### The answer is a formula, not a fixed number: `mix` always asks for gantry Z = safe_z + 35, because safe_z is a promise about the **tip end**, not the carriage

- [x] Read the committed configs (safe_z 114, z_max 122, tip 35) and the CubOS source for the `mix` code path
- [x] Reproduce your 160 and my earlier 149 offline — both are the same formula at different safe_z values
- [x] Check every knob: protocol, deck, gantry config — none exists; verified at the Pi's `cbc33dc` **and** current CubOS `main`
- [x] Quantify the "lower safe_z" route (it validates, but leaves ~3 mm of cap clearance on capper legs)
- [x] Build the actual fix as a third local CubOS patch, offline-validated — committed but **deliberately NOT applied to the Pi** ([`144c349`](https://github.com/vertical-cloud-lab/byu-vcl/commit/144c349))

### Why 160 (or 149)

Every engage-based pipette command — `mix`, `aspirate`, `transfer`, `drop_tip` — travels between labware by hovering at `safe_z`, and CubOS measures `safe_z` **at the instrument's tool point**. Once a tip is on, the tool point is the tip end, 35 mm below the nozzle. So "hover at safe_z" means *tip end* at safe_z, which puts the carriage at:

```
required gantry Z = safe_z + tip_length
                  = 114 + 35 = 149   (the branch's gantry file)
                  = 125 + 35 = 160   (safe_z raised to 125)
```

I reproduced both messages verbatim offline — your 160 appears exactly when `safe_z` is 125 ([`instrument_mount.py` → `move_to_labware`](https://github.com/Ursa-Laboratories/CubOS/blob/main/packages/core/src/cubos/gantry/instrument_mount.py) hovers at `(x, y, safe_z)`; `engage_at_labware` in [`_movement.py`](https://github.com/Ursa-Laboratories/CubOS/blob/main/packages/core/src/cubos/protocol_engine/commands/_movement.py) calls it; the tip enters via `effective_depth = depth + attached_tip_extension`).

Your observation and CubOS's demand aren't actually in conflict: you saw the **carriage** clear everything at gantry 122 — that's the tip end at deck **87**. CubOS is insisting the tip end get all the way up to **114/125**, which the machine physically cannot do, and unlike `move`, engage commands accept **no `travel_z`** — so nothing in the protocol or deck file can route around it. Two corollaries:

- **Raising safe_z can never fix this** — the requirement rises 1:1 with it (that's why you saw 160 after raising it). Also, if you raised `working_volume.z_max` to 125 to make safe_z 125 legal: the controller's last-read Z travel was `$132 = 123.99` (2026-08-20), so commanding 122–125 risks a soft-limit alarm — I'd put z_max back to 122.
- **Lowering safe_z to 87** (= 122 − 35) does make a literal `mix` validate — I confirmed PASS — but safe_z is shared with the capper, whose park legs are raw moves at `safe_z − 15.935` = deck **71**: the bare nozzle then sweeps ~**3 mm above the cap tops** (~68) diagonally across the vial column, 12×/run, and on the Pi's CubOS version every capper approach leg does the same. Plus every explicit `travel_z` in the protocol must drop to ≤ 87. It works on paper; I wouldn't run it.

### The way to change it — a patch, written and tested, waiting on your go-ahead

Committed [`cubos/patches/tipped-hover-clamp-and-ceiling-travel.patch`](https://github.com/vertical-cloud-lab/byu-vcl/blob/144c349/cubos/patches/tipped-hover-clamp-and-ceiling-travel.patch) (+ a full entry in [`patches/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/144c349/cubos/patches/README.md)). **NOT applied to the Pi** — unlike the two bug-fix patches, this one changes motion planning for every protocol, so applying it is your call. What it does:

1. **Backports Ursa's own 2026-08-24 commit** (`0cc5028`, landed upstream *after* the Pi's checkout): XY travel rides the working-volume ceiling so passive tools clear the deck.
2. **The new part — hover clamp:** when the tool point is too deep to reach safe_z (exactly the tipped case), hover at the highest carriage-reachable plane instead of refusing: tip end at **87, carriage at 122** — the precise plane you verified by eye. A WARNING is logged every time it clamps.
3. Mirrors the clamp in both offline validators and seeds the mock gantry's working volume (mock runs previously planned travel differently from hardware — found and fixed while testing).

Evidence: with the **unchanged** committed configs, a literal `mix` goes from FAIL to `validate_setup` PASS + clean mock run, and the trace shows `Moving OpentronsPipette to (187, 26, 87) -> gantry (135, 14, 122)` where unpatched code commands 149. Upstream suite: 2020 tests pass (3 pre-existing failures verified identical without my patch). Out-of-reach *actions* still fail validation. The committed `pipette_test.yaml` is unaffected (27/27 unchanged). Behavior changes to know: capper XY transits rise from gantry 98 to 122 (higher = safer, slightly slower), and **if you ever switch to longer tips** (the rack definition's default is 59.3 mm), the clamped plane 122 − 59.3 ≈ 63 would be *below* the cap tops — that caveat is written into the patch README.

To apply on the Pi: `cd ~/CubOS && git apply ~/byu-vcl/cubos/patches/tipped-hover-clamp-and-ceiling-travel.patch` (or say the word and I'll do it next session). Two things it does **not** change: the pipette is still `offline: true` / `port: ''`, so a literal `mix` would pantomime the plunger until the Opentrons link is brought online; and current CubOS `main` (`5b3376c`) still has this limitation — the clamp is ours to send to Ursa (not filed yet).

**Not done:** no Pi connection, nothing run on hardware, no config files touched.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-08-26 00:06:36 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418717095)

@claude run a protocol with these files: 
[sterling_6vials_tiprack.yaml](https://github.com/user-attachments/files/31442467/sterling_6vials_tiprack.yaml)
[cub_xl_ben_pipette_capper.yaml](https://github.com/user-attachments/files/31442472/cub_xl_ben_pipette_capper.yaml)
[pipette_test.yaml](https://github.com/user-attachments/files/31442477/pipette_test.yaml)

---

## @claude[bot] — 2026-08-26 00:07:00 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418720200)

**Claude encountered an error after 7m 41s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32913702719)

---
I'll analyze this and get back to you.

---

## @benwhitney5463 — 2026-08-26 00:18:49 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418807749)

@claude try again, and if node.js is outdated, download the necessary updates.

---

## @claude[bot] — 2026-08-26 00:19:11 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418810397)

**Claude encountered an error after 1s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32914558002)

---
I'll analyze this and get back to you.

---

## @benwhitney5463 — 2026-08-26 00:27:04 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418866769)

@claude what is stopping you from connecting to the RPi5

---

## @claude[bot] — 2026-08-26 00:27:25 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418869142)

**Claude encountered an error after 1s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32915136461)

---
I'll analyze this and get back to you.

---

## @benwhitney5463 — 2026-08-26 17:48:04 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5428960518)

@claude run a protocol with these files:
[sterling_6vials_tiprack.yaml](https://github.com/user-attachments/files/31442467/sterling_6vials_tiprack.yaml)
[cub_xl_ben_pipette_capper.yaml](https://github.com/user-attachments/files/31442472/cub_xl_ben_pipette_capper.yaml)
[pipette_test.yaml](https://github.com/user-attachments/files/31442477/pipette_test.yaml)

---

## @claude[bot] — 2026-08-26 17:48:25 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5428964937)

**Claude encountered an error after 1s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32996181849)

---
I'll analyze this and get back to you.

---

## @benwhitney5463 — 2026-08-26 17:55:22 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5429050592)

@claude run a protocol with these files:
[sterling_6vials_tiprack.yaml](https://github.com/user-attachments/files/31442467/sterling_6vials_tiprack.yaml)
[cub_xl_ben_pipette_capper.yaml](https://github.com/user-attachments/files/31442472/cub_xl_ben_pipette_capper.yaml)
[pipette_test.yaml](https://github.com/user-attachments/files/31442477/pipette_test.yaml)

---

## @claude[bot] — 2026-08-26 17:55:49 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5429055892)

**Claude finished @benwhitney5463's task in 18m 10s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32996824743)

---
### I couldn't run it — the runner has no route to the Pi since the Tailscale step was removed from `main` 2 h ago. Audited the trio offline instead, and it has two collision paths

- [x] Download the three attachments, diff against the branch
- [x] Diagnose why the Pi is unreachable — found the exact commit
- [x] Rebuild the Pi's exact CubOS (`cbc33dc` + both patches) and validate the trio against it
- [x] Audit the two config changes (`safe_z` 114→87, pipette online on `/dev/ttyACM0`)
- [x] Commit the trio + the audit (`6079c87`)
- [ ] **Hardware run — blocked on the workflow, and on two things below**

### 🔴 The blocker: `429fe34` deleted `Connect to Tailscale` from `main`'s workflow

[`429fe34`](https://github.com/vertical-cloud-lab/byu-vcl/commit/429fe34) — *"Remove Tailscale connection step from workflow"*, 2026-08-26 15:57 UTC, ~2 h before this comment. `issue_comment` events always run the **default branch's** workflow, so from that commit on every `@claude` job starts with no tailnet:

```
$ tailscale status
bash: tailscale: command not found
$ ip -brief link
lo / eth0 / enP5134s1 / docker0        # no tailscale0
```

Tailscale SSH is the only path in (residential NAT), so nothing can reach the CubXL — no `run_protocol`, no port check, no GRBL read. The job step lists confirm it: the 2026-08-26 00:xx runs show `Connect to Tailscale=success`; [this one](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32996824743) has no such step at all. `TS_OAUTH_CLIENT_ID` / `TS_OAUTH_SECRET` / `TAILNET_ID` are still passed to the job — only the step that uses them is gone.

The fix is the four lines that were removed, before `Run Claude Code`:

```yaml
      - name: Connect to Tailscale
        uses: tailscale/github-action@v2
        with:
          oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tags: tag:stream-cam-test
```

I'm unable to make that edit myself — the GitHub App can't modify `.github/workflows`. [Fix this →](https://claude.ai/code?q=On%20the%20main%20branch%20of%20vertical-cloud-lab%2Fbyu-vcl%2C%20re-add%20the%20%22Connect%20to%20Tailscale%22%20step%20to%20.github%2Fworkflows%2Fclaude.yml%20that%20commit%20429fe34%20removed.%20It%20uses%20tailscale%2Fgithub-action%40v2%20with%20oauth-client-id%3A%20%24%7B%7B%20secrets.TS_OAUTH_CLIENT_ID%20%7D%7D%2C%20oauth-secret%3A%20%24%7B%7B%20secrets.TS_OAUTH_SECRET%20%7D%7D%2C%20tags%3A%20tag%3Astream-cam-test%2C%20and%20must%20run%20before%20the%20%22Run%20Claude%20Code%22%20step.%20Without%20it%20the%20runner%20has%20no%20tailnet%20route%20to%20the%20lab%20Raspberry%20Pi.&repo=vertical-cloud-lab/byu-vcl) (The three errored jobs at 00:06–00:27 still had the step; those failed for an unrelated reason.)

So I rebuilt the Pi's exact software locally — CubOS `cbc33dc` + `pawduino-connect-boot-banner` + `cap-release-confirm-after-retract` — and ran the trio against that.

### `safe_z: 87.0` is the right fix for the problem you aimed it at

It's the **only** value that makes a literal `mix:`/`drop_tip:` validate on the Pi's CubOS, for exactly the reason from last time: those commands hover at `safe_z` measured **at the tool point**, so a 35 mm tip needs `gantry Z = safe_z + 35`. 114 + 35 = 149 > `z_max` 122; **87 + 35 = 122 exactly**.

| CubOS tree | `safe_z` | `validate_setup` |
|---|---|---|
| Pi (`cbc33dc` + 2 patches) | **87** | **PASS** — 19 steps, mock 19/19 |
| Pi | 114 | FAIL — `gantry z=149.0 outside [0.0, 122.0]` ×4 |
| current `main` (`5b3376c`) | 114 | FAIL — same 4 |
| Pi + hover-clamp patch | 114 | **PASS** |

### 🔴 …but it drops the nozzle to ~3 mm over the caps, and 20 of 24 capper legs cross them

`safe_z` is shared with the capper (`depth: -15.935`), so every decap/cap leg now travels at gantry **71.065** — and the pipette (`depth: 0.0`) is the lowest thing on the head, so the **bare nozzle rides at deck Z 71.065**. Cap tops are at about deck **68** (the engage plane: rim 55 + `engage_depth_mm` 13). At `safe_z: 114` that same nozzle rode at deck 98 — ~30 mm clear.

And `park_position: [125, 50]` is off the vial column, so each leg is a diagonal whose nozzle shadow (`gantry + (52, 12)`) crosses deck X 187 partway through. With `diameter: 28` vials:

| leg | nozzle Y at deck X 187 | nearest cap |
|---|---|---|
| park ↔ vial_1 | 58.1 | vial_2 — **0.9 mm** from centre |
| park ↔ vial_2 | 63.5 | vial_2 — 4.5 mm |
| park ↔ vial_3 | 68.8 | vial_2 — 9.8 mm |
| park ↔ vial_4 | 74.1 | vial_2 — 15.1 mm (just clear) |
| park ↔ vial_5 | 79.4 | vial_3 — 12.6 mm |
| park ↔ vial_6 | 84.7 | vial_3 — 7.3 mm |

Neither `validate_setup` nor `--mock` says a word — no offline check models the passive instrument. Two ways to keep the tipped commands without the 3 mm margin:

1. **Apply the hover-clamp patch and put `safe_z` back to 114.** That's what [`tipped-hover-clamp-and-ceiling-travel.patch`](https://github.com/vertical-cloud-lab/byu-vcl/blob/6079c87/cubos/patches/tipped-hover-clamp-and-ceiling-travel.patch) was written for: the tipped hover clamps to gantry 122 (tip end at deck 87 — the plane you verified by eye) while capper legs return to gantry 98.065. Verified PASS + 19/19 mock, trace in the audit. `cd ~/CubOS && git apply ~/byu-vcl/cubos/patches/tipped-hover-clamp-and-ceiling-travel.patch`.
2. **Keep 87 and move `park_position` onto the vial column's X (187)** so every leg is a pure-Y move and the nozzle stays at deck X 239, never over a cap — same trick as Jarrett's j1 config. Needs an eyeball of the X ≈ 239 strip first.

### 🔴 Everything after step 6 assumes the tip came off, and nothing checks

Steps 3–6 are the only tipped steps; from step 7 (`cap vial_1`) on it's all capper legs at gantry 71.065. **If the tip is still on, that's the tip end at deck 36.065** — 19 mm below the rims, 32 mm below the cap tops — sweeping the vial column on every park leg. Hard crash, 20 times.

`drop_tip` calls `clear_attached_tip_extension()` whether or not the tip left, and the position it drives to is not a measured number. In `instruments/pipette/models.py`, unchanged at `cbc33dc` and on `main`:

```python
"p20_single_gen2": PipetteConfig(
    prime_position=5.0,       # placeholder
    blowout_position=7.0,     # placeholder
    drop_tip_position=10.0,   # placeholder
    mm_to_ul=0.025,           # placeholder
```

Same bucket as the old `CAPPER_ENGAGE_DEPTH_MM`. `connect()` also runs `home()` + `prime()` against these the first time the plunger isn't homed. For the first live-plunger run I'd either split the file after step 6 and eyeball the nozzle, or put a `breakpoint:` between 6 and 7 **and run it from a foreground terminal** — headless runs log *"Breakpoint skipped because stdin is not interactive"* and continue straight into the capper legs.

### ⚠️ Two smaller ones

**`mix` never enters the vial.** The signature is `mix(position, volume_ul, repetitions=3, speed=50.0, height=0.0)` and the engage descends the tool point to `coord.z + height` — with `height` defaulted that's deck Z **55.0**, the rim exactly, tip end level with the mouth. Adding `height: -15.0` reaches deck Z 40 (gantry 75), the same depth the old stroke version used; validates PASS on both trees. Separately, `mm_travel = volume_ul * mm_to_ul` = `20 × 0.025` = **0.5 mm of plunger**, so "20 µL" isn't microlitres yet. And `drop_tip` releases the tip 35 mm above the rack (its engage puts the *tip end* at `pickup_z` 60, but the tip was seated with its end at deck 25), so it won't seat back in A1.

**The shared `/dev/ttyACM0` is right in principle, unarbitrated in practice.** Upstream CubOS does drive the Opentrons plunger from the capper's Arduino — *"the capper and lights share this Arduino via one link per port"* — routing both through `PawduinoLink.acquire(port, baud)`. That class **doesn't exist at `cbc33dc`**: `instruments/controllers/pawduino.py` 404s at that ref and the pipette driver opens its own `serial.Serial(port=...)`. Two uncoordinated handles on one Arduino — a second open can re-toggle DTR and reset the board mid-session, a close resets it under the other driver, and both read one reply stream. It landed upstream at `1a9987f` (2026-08-20), so updating the Pi past that fixes it.

### One thing that would stop the run at connect anyway

`Gantry._validate_grbl_settings` treats `$130/$131/$132` as critical at 0.001 mm tolerance. The gantry file expects **389.333 / 235.0 / 125.0**; the last live read (2026-08-20) was **389.693 / 281.218 / 123.99** → `Critical GRBL settings mismatch — motion would be wrong`, before any motion. If your recalibration rewrote the controller, fine — otherwise that's the first thing you'll hit.

### Committed — [`6079c87`](https://github.com/vertical-cloud-lab/byu-vcl/commit/6079c87)

- [`cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/6079c87/cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml) and [`cubos/configs/protocol/vcl/pipette_test.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/6079c87/cubos/configs/protocol/vcl/pipette_test.yaml) — your attachments, **comments only** (I checked the parsed YAML is identical to what you sent). The protocol's old header described the substitutions your revision replaces, so I rewrote it. The deck was byte-identical to the branch, untouched.
- [`cubos/results/pipette_test_20260826/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/6079c87/cubos/results/pipette_test_20260826/README.md) — the full audit: version matrix, the crossing table, the recommended-config trace, all source citations
- [`SOP/raspberry-pi-cubos-setup.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/6079c87/SOP/raspberry-pi-cubos-setup.md) — notes that remote hardware access depends on that workflow step

**Not done:** nothing was sent to the CubXL and no connection to the Pi was made — no homing, no motion, no port opened. Restore the Tailscale step and say "run it" and I'll pick this up; tell me which of the two `safe_z` routes you want first, and whether you'd rather split the file at step 6 than trust `drop_tip` on its placeholder eject position for the first live-plunger run.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---
