## The tray coupling, part by part (2026-11-18)

Sterling, PR #318, 2026-11-18: "I think we need something more real and high-fidelity for the liquid, gas, and power
transfer modules (quick disconnect, etc.) for the VLM".

Round 4's coupling (`services.py`) had real catalogue figures behind it, but it drew none of the parts. It was a
200 × 90 mm block with six discs and bars for the inserts, two pins and a box for the dock.
[`coupling.py`](../coupling.py) now draws the parts themselves, from two Stäubli documents (fetched 2026-11-18):
- the CombiTac uniq main catalogue, CT-Main-11014009-en, 08.2026, 152 pages;
- the CombiTac align flyer, 11014023-en.

It puts them in a dock that fits the room the Shuttle leaves beside a tray. `services.py` takes every tray plate and
every dock in the VLM scenes from it.

| | |
|---|---|
| The close-up: docking and letting go, in the order things connect | [`out/mp4/vlm_coupling.mp4`](../out/mp4/vlm_coupling.mp4), [`out/vlm_coupling.gif`](../out/vlm_coupling.gif) |
| The numbers: parts, forces, stroke, clearances | [`out/coupling.json`](../out/coupling.json) |
| The docks against the lift, re-run | [`out/dock_lift_clearance.json`](../out/dock_lift_clearance.json), [`.png`](../out/dock_lift_clearance.png) |

```bash
xvfb-run -a python3 coupling.py movie json      # the close-up and the numbers
python3 services.py clearance                    # the docks against the lift and the trays
```

![The tray's face](../out/vlm_coupling_still.png)

### What is on the tray, and what is on the dock

**Two frames, not one.** Stäubli's safety notes (p. 137): "On permanently fixed installations, electrical contacts
have to be placed above liquid couplings". So the electrical frame sits above the fluid frame. Each frame is a row of
carriers on two supporting rails, between two end pieces.

| Frame | Module (Stäubli type) | Width | What it carries |
|---|---|---|---|
| Electrical, top | CT-LMFB | 6 mm | the Last Mate First Break pair: monitors the mating |
| | CT-E3-2+PE | 10 mm | PE on a Ø3 mm contact (the long pin, which mates first); two spare poles, blind-plugged |
| | CT-E3-3 | 10 mm | L1, L2, N on Ø3 mm contacts, 39 A each |
| | CT-DIP4 | 4 mm | a spacer |
| | CT-10GBIT-RJ45 | 22 mm | Ethernet, Cat 6A, 10 Gbit/s; an RJ45 jack at the back of each half |
| Fluid, bottom | CT-E8-2 + 2 × SCT03 | 18 mm | compressed air and N₂: G1/8, SW12, nominal bore 3 mm |
| | CT-E-UCT08-2 + 2 × LCT06 | 42 mm | chilled water in and out: G1/4, SW17, nominal bore 6 mm, 8.48 L/min at 5 m/s |

- **The ends: CombiTac align 4** (p. 80–81, flyer p. 12–13). On the tray, CT-HME-B/4: a die-cast zinc cone with a
  bronze bushing. On the dock, CT-HME-S/4: a Ø9.8 mm pin standing 50.2 mm proud of an 18 mm body, with an insulating
  cap so it can't touch a live socket. Each end piece is 43 × 34.7 mm. They take up 4 mm radial and ±2° of
  misalignment, for 100,000 mating cycles.
- **Sizes that follow.** Each frame is its modules' widths plus 86 mm of end pieces: 138 mm (electrical) and 146 mm
  (fluid). Each sits in Stäubli's cut-out, L + 54 × 41 mm with R5 corners, with Ø4.2 mm holes at L + 70 (p. 84). The
  carriers are 24 mm deep and the mated plates 25 mm apart (p. 86), so each face sits 12.5 mm in front of its plate.
- **Which half goes where.** The sockets, which are touch-safe (IP2X) when unmated, and the cones go on the tray. The
  pins and the plug couplings go on the dock. Nothing on a tray then stands proud of its side: the faces are 6 mm
  inside it, as before. Every fluid coupling closes behind a flat face, so a tray in transit carries no open line.
- **Behind each half:**
  - crimp barrels and coloured wires into a cable gland (L1 brown, L2 black, N blue, PE green);
  - the RJ45 plug and the Cat 6A cable;
  - push-in fittings with their tubes: blue air, black N₂, blue and red water;
  - on the tray, the LMFB pair bridged by a short loop;
  - on the dock, wired to the relay.

### The order things connect

Stäubli gives the order, not the lengths: "Longer type of pin mates first" (p. 27), and the LMFB contacts "show
whether a CombiTac is fully connected or not" (p. 40). The drawn lengths keep that order:

| s, mm to go | What makes |
|---|---|
| 7.5 | PE (the long pin) |
| 7 | the 10 Gbit contacts |
| 5 | L1, L2, N; the water couplings open |
| 4.5 | air and N₂ open |
| 2 | the LMFB pair, last |
| 0 | the hard-stop screws (CT-SHR-HS, p. 82) touch, so the end force doesn't go through the contacts |

The pin lengths behind this are drawn: PE 12.5 mm proud, power 10, the 10 Gbit pins 12 (that one is Stäubli's), the
LMFB pins 7. The couplings count as open after 6 mm of nose travel.

**Power never makes or breaks under load.** Stäubli: "Connecting and disconnecting when live is permitted.
Connecting and disconnecting under load is not permitted" (p. 137, p. 139).
- **The sequence.** The dock's relay closes the contactor only once the LMFB loop is closed. To let go, the contactor
  opens first (the tray's UPS takes over).
- **The safeguard.** If the head is ever pulled back with the contactor closed, the LMFB pair breaks first and drops
  it before any power pin parts.

**No coupling mates or parts under pressure.** Stäubli prohibits it (p. 73, p. 75, footnote 1).
- **The valves.** Each line on the dock has a solenoid valve (3/2 for air and N₂, venting the coupling's side; 2/2
  for water) and a pressure sensor on the coupling's side.
- **The order.** The valves open only after mating. Before the head pulls back, they shut and vent, and the sensors
  must read 0 bar.

**Inside the couplings** (drawn, not published). Both SCT03 and LCT06 are "leakproof, shut-off on both sides". The
close-up draws the usual flat-face, double shut-off design:
- the socket has a fixed central piston, with a spring-loaded sleeve round it, flush with its face;
- the plug has a spring-loaded poppet, flush with its nose.

As they meet, the nose pushes the sleeve back and the piston pushes the poppet back. The flow opens only once both
seals are inside each other.

### The dock (ours)

The space is the constraint. From the tray's side to the cladding the model has:
- 45 mm to the column side wall;
- the 12 mm wall itself;
- a 108 mm cavity behind it.

That is 165 mm in all, as Kardex's unit width for this tray gives. Pulled back, the align pins' tips must clear the
tray's side, so the stroke is 75 mm. That leaves no room for a cylinder behind the head, so:
- **Carriage:** a plate on two HIWIN MGN12H miniature guides, under the dock's top plate. This is the "stable guide
  system" Stäubli asks for in a permanent installation (p. 81).
- **Floating plate:** the dock's half is on a 6 mm plate held to the carriage by four shoulder screws with springs. The
  springs centre it, and the align pins pull it onto the tray as they enter the cones. The close-up's tray stopped
  2.5 mm off in y and 1.5 mm low (2.9 mm), inside align 4's 4 mm.
- **Drive:** a slider-crank beside the frames: a 37.5 mm crank and a 50 mm rod, turned 180° by a 24 V worm
  gearmotor.
  - Both ends of the stroke are dead centres. Mated, the couplings' springs (175 N) can't push the head back,
    powered or not, and the worm locks itself as well.
  - The head slows into the end of the stroke on its own, as Staubli's 600 mm/min test speed (p. 135) asks.
- **Energy chain:** an igus E2 micro-size chain, bend radius 22 mm, under the dock. It rolls at half the head's speed,
  down to the valve bank.
- **Valve bank:** under the dock. A DIN rail with the mains contactor, the LMFB relay and an RJ45 coupler, four
  solenoid valves with indicator LEDs, and a pressure sensor per fluid line. Short supply lines run from it to the
  column's service riser.
- **End sensors:** two inductive sensors (M8) on the top plate report the end positions.

**Forces** (`coupling.plugging()`):
- **Sliding force: 74 N.**
  - 4 Ø3 mm contacts at 8 N (p. 27);
  - 2 LMFB contacts at 14 N (p. 41);
  - the 10 Gbit module at 14 N (p. 49).
- **Couplings' springs: 175 N.** That is 2 × 43 N (SCT03) and 2 × 44.5 N (LCT06), all without pressure.
- **Plugging: 286 N**, taking Stäubli's plugging force as 1.5 × the sliding force (p. 135), plus the springs.
- **Gearmotor: about 14 N·m at the crank** at the worst point of the last 15 mm. That assumes the whole 286 N acts
  over those 15 mm, so it is a ceiling.

**Clearances** (re-run, `services.py clearance`, every part as its bounding box, so each gap is a lower bound):

| Case | Smallest gap | Before |
|---|---|---|
| The extractor past the front-column and bay docks, any height, empty or loaded | 96 mm | 158 mm |
| The extractor past the rear-column docks | 683 mm | 643 mm |
| A tray past its own dock, pulled back | 18.6 mm (the pins' insulating caps) | 22 mm |
| The bay's dock to the shutter | 20.6 mm | 81 mm |
| The tray's coupling to the extractor's carriages, the tray on the extractor | 11.0 mm | 9.5 mm |

The bay's dock is the tight one. Its drive end is 20.6 mm in front of the shutter's plane. The first layout had 3 mm,
until the crank moved 11 mm and the frame was shortened to suit.

### What is ours, what is drawn, what to ask

- **Ours:**
  - the plates and the tray's bracket;
  - the floating plate, the carriage, the slider-crank and its gearmotor;
  - the chain's size, the valve bank, the sensors' placement.

  The sizes are chosen to fit, not sourced. The gearmotor isn't a selected part.
- **Drawn, not dimensioned:**
  - the carriers' height between the rails (30 mm, from the 10 Gbit module's 28–32 mm drawing);
  - every pin length except the 10 Gbit module's;
  - the couplings' insides;
  - the shape of the die-cast end pieces beyond their published envelope.
- **Ask Stäubli:**
  - Do the align 4 end pieces float in the L + 54 × 41 mm cut-out, or must the panel float? (Our dock floats its
    plate, so either works.)
  - What are the pin lengths, and how many mm apart do PE, power and LMFB make?
  - For water at 3 bar and 8 L/min, is an LCT06 pair right, or is a larger bore in a second frame better?
  - Would one CombiTac align 4 frame with both rows be allowed, if the fluid row is below?
- **Ask Kardex:** Can a dock be built into the side wall of a slot and of the bay? This one needs a window about
  290 × 165 mm and about 140 mm of depth behind the tray's side; the cladding stays where it is.
- **Not done:**
  - The hookups clip shows this dock only once it is re-rendered. The UPS run planned to re-render it with its new
    UPSs.
  - The set-up movie and the long-form still show the old plate.
