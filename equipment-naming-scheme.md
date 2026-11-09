# Equipment Naming Scheme for the Vertical Cloud Lab

Tracks: [issue #50](https://github.com/vertical-cloud-lab/byu-vcl/issues/50)

This document assesses the working name **"Gary the Gantry"** (christened for the
OT-2 after the Brother P-Touch label maker arrived) and proposes a lab-wide
naming scheme so that future equipment can be labeled consistently with the
P-Touch.

## 1. Assessment of "Gary the Gantry"

**Verdict: keep it — it's a good name and a good template.**

What works:

- **Alliterative** (`G`ary the `G`antry) — easy to remember and to say out loud
  during demos/livestreams.
- **Descriptive** — the `<Name> the <Equipment-type>` form tells a new lab
  member what the instrument *is*, not just what we call it. This matches how
  other labs name furnaces "Smaug" only after explaining it's a furnace.
- **Friendly / personifying** — encourages a culture of treating instruments
  as named teammates (helpful for SOPs: "Gary needs a tip refill" reads better
  than "the OT-2 in bay 2 needs a tip refill").
- **Locally appropriate** — BYU's mascot is "Cosmo the Cougar," so the
  `<First name> the <Noun>` pattern already feels native to campus.

What to formalize before adopting it lab-wide:

- Pick a **theme** that constrains the first names so they're not arbitrary
  (otherwise every new instrument re-opens the bikeshed).
- Pick a rule for **what noun follows "the"** (equipment class vs. nickname for
  the form factor).
- Decide whether **frugal twins** share a name with their high-cost
  counterpart (e.g., `Gary` and `Mini-Gary`) or get their own.

## 2. Candidate themes

Surveyed naming conventions used by similar self-driving / cloud labs and by
the broader instrument-naming tradition (e.g., dragon names — Norbert, Smaug —
on CVD/furnace systems; Greek-god names on telescopes; storm names on HPC
clusters). Each theme below is scored on fit with the lab's identity
(*vertical automation*, *cloud experimentation*, *frugal twins*; aerospace,
energy, alloys; BYU/Provo).

| # | Theme | Example names | Pros | Cons |
|---|-------|---------------|------|------|
| 1 | **Alliterative human first names** (current "Gary the Gantry" pattern) | Gary the Gantry, Vera the Vacuum, Polly the Printer | Already in use; friendly; descriptive; low overhead | No deeper story; risk of inconsistent first-name choices |
| 2 | **Sky / weather / cloud** (ties to "Cloud Lab") | Cirrus, Nimbus, Stratus, Zephyr, Tempest, Mistral, Squall | Direct tie to lab identity ("cloud" experimentation); aerospace-adjacent; plenty of names | Some ("Nimbus") are already famous brands |
| 3 | **Aerospace / aviation pioneers** (ties to aerospace alloy thrust) | Wright, Earhart, Yeager, Goddard, Glenn, Armstrong, Ride, Hughes | Strong fit with aerospace alloy research; recognizable; inspiring | Limited pool; can feel reverential/heavy |
| 4 | **Mountains / Wasatch peaks** (Provo geography) | Timpanogos (Timp), Nebo, Cascade, Provo, Squaw, Lone Peak, Olympus | Local flavor; vertical/elevation theme matches "vertical automation" | Long names; some have politically sensitive original names |
| 5 | **Dragons / mythical beasts** (precedent for furnaces) | Smaug, Norbert, Saphira, Drogon, Falkor | Fun; precedent in materials labs | Doesn't match a *cloud* lab thematically; better reserved for any future furnace/CVD |
| 6 | **Greek/Roman gods by function** | Hephaestus (forge/LPBF), Hermes (gantry/transport), Athena (vision/camera), Boreas (vacuum/wind), Vulcan (heater) | Functionally meaningful; classic; expandable | Heavy/serious tone; risk of mismatched mythology |
| 7 | **Famous scientists** (Curie, Tesla, Faraday, Lovelace, Hopper, Mendeleev) | Curie (echem), Tesla (power), Faraday (electrochem), Hopper (compute) | Educational; recognizable | Overused at large; some names are already trademarked products |
| 8 | **Sci-fi robots** | Wall-E, R2, Bender, Marvin, Bishop, HAL, K-2SO | Fun; appropriate for an automation lab | Trademark ambiguity; HAL has bad connotations |

## 3. Recommendation

**Adopt a layered scheme:** keep the `<First name> the <Equipment>` *form*
(Theme 1) and **constrain the first names with a sky/weather theme** (Theme 2)
so the lab identity ("Cloud Lab") shows through and future names are easy to
choose.

- **Form:** `<First name> the <Equipment-type-noun>` (e.g., "Cirrus the
  Color Sensor"). Optional shortening to just `<First name>` ("Cirrus") in
  conversation and on the printed P-Touch label, with the type noun appearing
  on a second label below.
- **First names drawn from:** clouds, winds, weather phenomena, and a few
  aviation pioneers as a secondary pool when a sky word doesn't fit. This
  keeps the rule simple ("if you can find it on a weather map or in a
  meteorology textbook, it's eligible") while leaving room for special cases.
- **Grandfathered exception:** "Gary the Gantry" stays. It predates the
  scheme, it's already labeled, and its alliteration is too good to retire.
  Treat it as the lab's honorary mascot.
- **Frugal-twin convention:** the twin takes the high-cost system's name with
  a `Mini-` prefix (e.g., `Hephaestus` and `Mini-Hephaestus`) so the
  pairing is obvious on labels and in code.

## 4. Per-equipment name suggestions

Pulled from the open issues in this repo. Top pick is **bold**; a few
alternates are listed for discussion. Equipment-type noun shown after "the".

| Equipment (issue) | Top pick | Alternates | Notes |
|-------------------|----------|------------|-------|
| OT-2 liquid handler (#9, #34) | **Gary the Gantry** *(grandfathered)* | — | Keep as-is. |
| Wireless color sensor (#33, #86) | **Iris the Color Sensor** | Prism, Spectra, Cirrus | "Iris" is both a sky/atmosphere word and an eye reference. |
| Overhead camera for OT-2 (#34, #40) | **Argus the Overhead Cam** | Hawkeye, Nimbus | Argus = mythological many-eyed watchman; pairs with Gary. |
| Bambu Lab printer (#82) | **Bambi the Bambu** | Pixie, Whirlwind | Alliterative; lightweight workhorse. |
| Squidstat Plus potentiostat (#26) | **Squall the Squidstat** | Tesla, Faraday | Alliteration + weather theme. |
| Heater/shaker module (#81) | **Sirocco the Shaker** | Vulcan, Khamsin | Sirocco = hot Mediterranean wind. |
| Autotrickler / Opentrickler (#14, #63, #73) | **Drizzle the Trickler** | Mizzle, Sprinkle | Weather word that literally describes the action. |
| Explosion-proof vacuum (Nilfisk 118EXP) (#24, #79) | **Vera the Vacuum** | Boreas, Cyclone | Alliterative; Boreas = Greek north wind if a sky word is preferred. |
| Glovebox (LC-180) (#30, #75) | **Haven the Glovebox** | Stratos, Aegis | Captures the "inert, protected" feel. |
| Vertical lift module (#53) | **Otis the Lift** | Ascend, Skylift | "Otis" nods to the elevator company; pairs nicely with the vertical-automation thrust. |
| Laser powder bed fusion printer (#45, #61) | **Hephaestus the LPBF** | Smaug, Vulcan | One of the rare cases where Theme 6 (gods) fits better than weather; LPBF is literally a forge. |
| AMPERE-2 frugal twin | **Ampere** *(keep existing)* | — | Project name is already established; treat as exception. |
| Future furnace / CVD (none yet) | **Smaug the Furnace** | Norbert, Drogon | Reserve a dragon name per the well-known precedent. |
| Dehumidifier (#42) | **Aria the Dehumidifier** | Drylin, Zephyr | "Aria" = air; quiet background utility. |
| Plate reader (#68) | **Spectra the Plate Reader** | Iris, Prism | Avoid clash with color sensor pick by giving color sensor "Iris" first. |
| Label maker (#50) — *this issue* | **Pip the P-Touch** | Scribe, Stencil | Tiny name for a tiny tool; "Pip" matches "P-Touch". |

## 5. Label format on the Brother P-Touch

To keep the actual printed labels consistent, suggest:

```
<First name> the <Equipment>
```

on the first line, optionally followed by a second label with:

```
<Asset tag / make-model>      issue #NN
```

Example for the OT-2:

```
Gary the Gantry
Opentrons OT-2 (#9)
```

This keeps the friendly nickname visible from across the room while still
giving a maintainer the model number and a link back to the GitHub issue
where the equipment is tracked.

## 6. Next steps

1. Lab discussion / 👍-react on this PR for the **theme** (sky/weather +
   alliterative form) before printing more labels.
2. Lock in the per-equipment names in a follow-up table — happy to convert
   the table in §4 to a checklist once names are agreed.
3. Print and apply the first round of labels using the format in §5.
4. Add a one-line "name" field to the equipment SOPs in
   `byu-engineering-sop-template.md` so the nickname is captured in the SOP
   header alongside the make/model.
