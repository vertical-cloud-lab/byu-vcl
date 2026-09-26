# `pipette_test.yaml` — 2026-08-26 offline audit (no hardware run)

@benwhitney5463 asked for a hardware run of the trio attached to PR #171 on
2026-08-26. **Nothing was sent to the CubXL**: the GitHub runner had no route
to the Pi. Everything below is offline analysis against the Pi's exact CubOS
version.

## Why the run did not happen

`.github/workflows/claude.yml` on `main` gained the runner's tailnet
membership from a `Connect to Tailscale` step. Commit
[`429fe34`](https://github.com/vertical-cloud-lab/byu-vcl/commit/429fe34)
("Remove Tailscale connection step from workflow", 2026-08-26 15:57 UTC)
deleted it. `issue_comment` events always run the **default branch's**
workflow, so from that commit onward every `@claude` job starts with no
`tailscale` binary, no `tailscaled`, and no `tailscale0` interface:

```
$ tailscale status
bash: tailscale: command not found
$ ip -brief link
lo / eth0 / enP5134s1 / docker0        # no tailscale0
```

Tailscale SSH is the only path to the Pi (residential NAT), so no
`validate_setup`, `run_protocol`, port check, or GRBL read can reach it.
`TS_OAUTH_CLIENT_ID` / `TS_OAUTH_SECRET` / `TAILNET_ID` are still passed into
the job — only the step that consumes them is gone.

Restoring it is the four lines that were removed, before the
`Run Claude Code` step:

```yaml
      - name: Connect to Tailscale
        uses: tailscale/github-action@v2
        with:
          oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tags: tag:stream-cam-test
```

(The three `@claude` jobs that errored on 2026-08-26 between 00:06 and 00:27
still had the step and failed for an unrelated reason.)

## Versions used for the audit

| tree | contents |
|---|---|
| `V_PI` | CubOS `cbc33dc` + `pawduino-connect-boot-banner` + `cap-release-confirm-after-retract` — the Pi's state as of 2026-08-20 |
| `V_PATCHED` | the above + `tipped-hover-clamp-and-ceiling-travel.patch` (committed on this branch, **not** applied to the Pi) |
| `main` | CubOS `5b3376c` |

## Validation matrix

| CubOS tree | `safe_z` | protocol | `validate_setup` |
|---|---|---|---|
| `V_PI` | 87 | as attached | **PASS** (19 steps, mock 19/19) |
| `V_PI` | 114 | as attached | FAIL — 4 violations, `gantry z=149.0 outside [0.0, 122.0]` |
| `main` | 114 | as attached | FAIL — same 4 |
| `V_PATCHED` | 114 | as attached | **PASS** |
| `V_PATCHED` | 114 | `mix` + `height: -15.0` | **PASS** (mock 19/19) |
| `V_PI` | 87 | `mix` + `height: -15.0` | **PASS** |

So `safe_z: 87.0` is a correct fix for the problem it targets: it is the only
value that lets a literal `mix:`/`drop_tip:` validate on the Pi's current
CubOS, because those commands hover at `safe_z` measured **at the tool point**
and a 35 mm tip needs `gantry Z = safe_z + 35` (114 + 35 = 149 > `z_max` 122;
87 + 35 = 122 exactly).

## What `safe_z: 87.0` costs

`safe_z` is shared with the capper. Capper `depth: -15.935`, so every
decap/cap leg travels at gantry Z `87 - 15.935 = 71.065`. The pipette
(`depth: 0.0`) is the lowest thing on the head, so the bare nozzle rides at
**deck Z 71.065**. Cap tops sit at about **deck Z 68** — the engage plane,
rim 55 + `engage_depth_mm` 13. Roughly **3 mm**, and it has never been
measured.

`park_position: [125, 50]` is off the vial column (deck X 187), so each leg is
a diagonal and the nozzle shadow (`gantry + (52, 12)`) crosses X 187 partway
through. With `diameter: 28` vials:

| leg | nozzle Y at deck X 187 | nearest cap |
|---|---|---|
| park ↔ vial_1 | 58.1 | vial_2, **0.9 mm** from centre |
| park ↔ vial_2 | 63.5 | vial_2, 4.5 mm |
| park ↔ vial_3 | 68.8 | vial_2, 9.8 mm |
| park ↔ vial_4 | 74.1 | vial_2, 15.1 mm (just clear) |
| park ↔ vial_5 | 79.4 | vial_3, 12.6 mm |
| park ↔ vial_6 | 84.7 | vial_3, 7.3 mm |

20 of the 24 legs pass the nozzle directly over vial_2's or vial_3's cap at
~3 mm. At `safe_z: 114` that nozzle rides at deck 98 — about 30 mm clear.
No offline check models the passive instrument, which is why both
`validate_setup` and `--mock` are silent about all of this.

Two ways to keep the tipped commands without the 3 mm margin:

1. Apply `cubos/patches/tipped-hover-clamp-and-ceiling-travel.patch` on the Pi
   and set `safe_z` back to `114.0`. The tipped hover is then clamped to
   gantry 122 (tip end at deck 87 — the plane Ben verified by eye) while
   capper legs return to gantry 98.065. Verified: PASS + 19/19 mock, trace
   below.
2. Keep `87.0` and move `park_position` onto the vial column's own X (187) so
   every leg is a pure-Y move and the nozzle stays at deck X 239, never over a
   cap. Needs an eyeball of the X ≈ 239 strip first.

Recommended-configuration trace (option 1):

```
Step 2: decap(vial_1)
  PawduinoCapper  deck (187, 26, 114) -> gantry (187, 26, 98.065)
  PawduinoCapper  deck (187, 26,  68) -> gantry (187, 26, 52.065)
Step 3: pick_up_tip(tip_rack.A1)
  OpentronsPipette deck (317, 13,  60) -> gantry (265, 1, 60)
Step 4: mix(vial_1, 20.0 uL, height=-15.0)
  OpentronsPipette deck (187, 26,  87) -> gantry (135, 14, 122)   # clamped
  OpentronsPipette deck (187, 26,  40) -> gantry (135, 14, 75)
```

## Bringing the pipette online — three things that are not ready

**1. The plunger constants are placeholders.** `instruments/pipette/models.py`,
`p20_single_gen2`, unchanged at `cbc33dc` and on `main`:

```python
prime_position=5.0,       # placeholder
blowout_position=7.0,     # placeholder
drop_tip_position=10.0,   # placeholder
mm_to_ul=0.025,           # placeholder
```

Same bucket as the old `CAPPER_ENGAGE_DEPTH_MM`. Consequences: a "20 µL" mix
moves the plunger `20 * 0.025 = 0.5 mm`, and `drop_tip` drives to an assumed
eject position. `connect()` also calls `home()` + `prime()` against these
numbers the first time the plunger is not homed.

**2. Nothing verifies the tip left, and the rest of the protocol assumes it
did.** `drop_tip` calls `clear_attached_tip_extension()` whether or not the
tip came off. If it stays on, steps 7–17 sweep the tip end at deck Z 36.065 —
19 mm below the rims, 32 mm below the cap tops — across the vial column on
every park leg. The capper's sensor interlock has no equivalent here.

**3. The shared `/dev/ttyACM0` is not arbitrated at the Pi's version.**
Pointing the pipette at the capper's Arduino matches the upstream design —
current CubOS says *"the capper and lights share this Arduino via one link per
port"* and routes both through `PawduinoLink.acquire(port, baud)`. That class
does not exist at `cbc33dc`; `instruments/controllers/pawduino.py` 404s at
that ref and the pipette driver opens its own `serial.Serial(port=...)`. Two
uncoordinated handles on one Arduino: a second open can re-toggle DTR and
reset the board mid-session, a close resets it under the other driver, and
both read one reply stream. It landed upstream at `1a9987f` (2026-08-20).

## Before any run: the GRBL settings check

`Gantry._validate_grbl_settings` treats `$130/$131/$132` as critical with a
0.001 mm tolerance and raises `Critical GRBL settings mismatch — motion would
be wrong` at connect. The gantry file expects **389.333 / 235.0 / 125.0**; the
last live read (2026-08-20) was **389.693 / 281.218 / 123.99**. Unless a
recalibration rewrote the controller, a run stops there before any motion.

## Machine state

Untouched. No connection was made, no port opened, no motion commanded. The
Pi was last seen (2026-08-20) at CubOS `cbc33dc` with both patches applied and
both serial devices free.
