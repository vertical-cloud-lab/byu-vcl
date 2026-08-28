# pipette_test.yaml — 2026-08-28 rev 2 (offline audit)

@benwhitney5463 attached a revised `pipette_test.yaml` on 2026-08-28 (PR #171)
with the request "try again with the same deck and gantry file, but with this
new protocol. The Pi should be online."

**The Pi was not online.** `tailscale status` reported the CubXL host
`Online: false`, last seen `2026-08-28T00:26:57Z`, and `tailscale ping` got no
reply across the session. Nothing was sent to the machine. This directory is
the offline audit that was done instead.

Config trio audited:

| | |
|---|---|
| gantry | `cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml` (`safe_z: 87`) |
| deck | `cubos/configs/deck/ben_6vials_tiprack.yaml` (byte-identical to the branch) |
| protocol | the rev-2 attachment, preserved verbatim as `pipette_test_as_attached.yaml` |

CubOS used: `Ursa-Laboratories/CubOS` @ `cbc33dc` (the Pi's checkout) with both
Pi-side patches applied — `pawduino-connect-boot-banner` and
`cap-release-confirm-after-retract`.

## What rev 2 changed, and what happened

Against rev 1, the attachment changed exactly two things: `travel_z: 87` on the
step-1 park move, and a new `move` back to `park_position` inserted between
`aspirate` and `cap vial_1` — the retract rev 1 was missing. The intent was
right; two things stopped it.

### 1. `instrumet:` — the file cannot load

`validate_asattached.log`:

```
protocol.5.instrument   Field required
protocol.5.instrumet    Extra inputs are not permitted
RESULT: ERROR - could not load protocol
```

Protocol YAML is validated against a strict per-command Pydantic schema at
**load** time — `protocol_engine/registry.py::_build_schema_from_signature`
builds one model per command from the handler's signature with
`extra="forbid"`, and `yaml_schema.py:62` validates every step before the run
starts. So the typo aborts before step 0. Nothing runs, nothing moves. That is
the safe failure mode, but it is a hard stop.

### 2. With the typo fixed, the retract move made the shear worse

`shadow_typofixed.log` — 4 interferences, the first of which ends the run:

```
step  5 move      moving=PawduinoCapper   passive=pipette (tip=on)
     -> vial_1: 0.0 mm from its axis, tool point down to Z 36.065 vs obstacle top 55.0
     (206.0, 27.0, 36.06) -> (258.0, 27.0, 36.06)
```

`travel_z` is applied in the **moving instrument's tool frame**
(`gantry/instrument_mount.py:71` — `gantry_travel_z = travel_z + depth`). Named
to the capper (`depth: -15.935`), `travel_z: 87` resolves to gantry **71.065**.
After `aspirate` the head is already at gantry **75** (tip end 15 mm inside
vial_1 at deck Z 40). So the retract step *lowered* the head 3.9 mm — driving
the tip deeper — and then translated X 52 mm, shearing the tip out through the
vial neck 19 mm below the rim.

The driver never interpolates a diagonal: `gantry_driver/driver.py:956`
transits lift → X → Y → descend, one axis per G-code line. That is why the X
translation happens entirely at the travel plane.

### Fix: name the pipette, not the capper

```yaml
positions:
  park_position: [206.0, 170.0, 87.0]   # capper frame
  pipette_park:  [258.0, 182.0, 87.0]   # SAME head pose, pipette frame

  - move:
      instrument: pipette
      position: pipette_park
      travel_z: 87
```

`pipette deck = gantry + (52, 12)`, and with a 35 mm tip the pipette's deck Z
is `gantry_z - 35`. So gantry `(206, 170, 122)` is capper deck
`(206, 170, 87)` **and** pipette deck `(258, 182, 87)` — the same physical
pose, reached from either frame. Named to the pipette, `travel_z: 87` resolves
to gantry `87 + 35 = 122`, so the tip lifts clear of the rim before any XY
motion.

## The gantry file needed one change too: capper `park_position` → `[206, 50]`

`decap`/`cap` each end with a hardcoded park move at the capper's `safe_z` →
gantry 71.065. The pipette is the lowest thing on the head, so an attached tip
rides those legs with its end at deck Z **36.065** — 19 mm below the rims,
32 mm below the cap tops. Vertically that cannot be fixed at `safe_z: 87`; the
only question is whether the legs ever pass *laterally* over a vial.

`[125, 50]` is off the vial column (deck X 206), so every leg carries an X
component and walks the tip across the column — the remaining three
interferences in `shadow_typofixed.log`:

```
step  6 cap       -> vial_1: 12.0 mm from its axis, Z 36.065 vs cap top 68.0
step  7 decap     -> vial_2:  2.0 mm from its axis, Z 36.065 vs cap top 68.0
step  7 decap     -> vial_2: 12.0 mm from its axis, Z 36.065 vs rim 55.0
```

`[206, 50]` puts the park on the column's own X. Every capper leg becomes a
pure-Y move and the tip holds deck X 258 — 52 mm clear of the column, over
ground the capper's own engages already sweep 19 mm lower.

This is the reason `safe_z: 87` is workable **without** the tipped-hover-clamp
patch. The 2026-08-28 rev-1 note that the `safe_z` window was "empty by 32 mm"
was a vertical-clearance argument; moving the park on-column removes the
requirement rather than satisfying it.

Caveat: the capper then parks over vial_2's footprint (Y 46..74) at deck Z 87.
Holding a ~13 mm cap, the cap's underside sits near deck 74 vs vial_2's cap top
at 68 — about 6 mm, unmeasured. `[206, 5]` or `[206, 220]` clears every
footprint and also sweeps clean.

## Results

| check | as attached | typo fixed only | corrected (committed) |
|---|---|---|---|
| `validate_setup` | **ERROR — cannot load** | PASS | **PASS**, 20 steps |
| `run_protocol --mock` | aborts pre-step-0 | 20/20 | **20/20** |
| `passive_shadow` | n/a | **4 interferences** | **0** |
| `passive_shadow --tip-stuck` | n/a | **25 interferences** | **3** |

## The residual risk: a stuck tip at step 10

`shadow_corrected_tipstuck.log` — the three remaining interferences are all at
step 10 (`cap vial_2`, immediately after `drop_tip`) and all against the tip
rack:

```
step 10 cap  -> tip_rack.A1: 0.0 mm from its axis, Z 36.065 vs obstacle top 60.0
                (317.0, 13.0, 60.0) -> (317.0, 13.0, 36.06)
step 10 cap  -> tip_rack.A1: (317.0, 13.0, 36.06) -> (258.0, 13.0, 36.06)
step 10 cap  -> tip_rack.A2: (317.0, 13.0, 36.06) -> (258.0, 13.0, 36.06)
```

`drop_tip` calls `clear_attached_tip_extension()` unconditionally, so from step
10 on CubOS plans in the bare-nozzle frame regardless of what physically
happened. If the tip is still on, `cap vial_2` lowers it into the rack and
drags it across.

There is no config fix. After `drop_tip` the modelled frame is bare, and a
bare-pipette `move` is capped at `travel_z <= safe_z` = gantry 87, which puts a
stuck tip's end at deck 52 — still below the rack top at 60. The two real
options are a `breakpoint:` between steps 9 and 10 (foreground terminal only —
headless runs log *"Breakpoint skipped because stdin is not interactive"* and
continue), or splitting the run at step 9.

@benwhitney5463 accepted this risk explicitly on 2026-08-28: *"don't worry
about ensuring the tip has been dropped. I am watching the machine, and will
manually remove the tip mid-run if needed."*

## `drop_z: 60` — still does nothing, and it shrinks the rack's model

At `cbc33dc`, `drop_z` is read in exactly one place —
`deck/labware/tip_rack.py:158-160` — to derive the rack's modeled height as
`max(abs(pickup_z - drop_z), 1.0)`. With `pickup_z: 60` that evaluates to
**1.0 mm**, overriding the explicit `height: 22` and collapsing the rack's
bounding box. No command reads it for motion. `drop_tip` engages the **tip
end** to the rack's `location.z` (60 → gantry 95) while a seated tip has its
end at deck 25, so the release still happens a full tip-length above the slot.

Set `drop_z` back to `null`. The real fix is a `tip_disposal` deck entry —
that is what `drop_tip` is built for; it ejects at *that* entry's own
`location.z`.

## Files

| | |
|---|---|
| `pipette_test_as_attached.yaml` | the rev-2 attachment, verbatim |
| `validate_asattached.log` | the load error |
| `validate_typofixed.log`, `shadow_typofixed*.log` | typo fixed, nothing else |
| `validate_corrected.log`, `shadow_corrected*.log`, `mock_corrected.log` | the committed configs |

No hardware log — the Pi was unreachable for the whole session.
