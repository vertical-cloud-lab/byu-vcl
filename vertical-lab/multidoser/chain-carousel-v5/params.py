"""Dimensions for the chain-carousel test rig v5 (issue #128), in mm.

v5 is v4 with a real balance under the station (sgbaird, 2026-11-04: "the multi-doser needs to be using a real scale").
The dose falls straight into a beaker on an A&D HR-202i (220 g x 0.1 mg, 51 g x 0.01 mg fine range), the higher-capacity
0.1 mg sibling of the lab's HR-100A that design/brainstorming.md names. Nothing touches the balance but the beaker on its
riser. To make room, v4's station column (the P16, its guide cradle and cradle post, all standing in the balance's chamber)
is gone: the EC now rides on an 8 mm lift bar through its base, carried by two P16s beside the balance, and the bar's end
shoes run in vertical guides on two station posts (keeping the EC square on the rise, as v4's cradle walls did). The whole
carousel is 80 mm higher so the parked EC, the bar and the NEMA 34 clear the balance's top; the frame's front base rail
and both station rails are gone (the balance stands where they were), and the latch rail hangs from a 2020 beam off the
-y side. Everything down to "v4" below is v4's, unchanged unless a comment says "v5".


v4 is v3 with Sam's item 7 of 2026-10-29: the augers ride OUTSIDE the loop. Each module sits on its carriage's outer face
(the carriage still bolts to the A-1 tabs from outside), so at the loading position the auger faces the side hatch and comes
straight off its plate against the side tabs; at the station the module hangs under the bottom run and the electronics
carriage reaches up round the auger to dock on the plate's auger side. Everything else is v3's (below).

v3 was v2 with Sam's critiques of 2026-10-29 applied (augers still inside the loop): a kinematic dock with magnets
between his small electronics carriage and a new mounting plate, a guide that the carriage parks in on its own
kinematic seat, a spring-loaded door on every auger's outlet that the docked carriage pushes open, a latch that holds
the plate on its carriage upside down and is opened by a cam at the station, an acrylic enclosure with a front hatch
(scale) and a side hatch (swaps), side tabs at the loading position, no funnel, and the lab's A&D HR-100A modelled.
Everything down to "v3" below is v2's, unchanged unless a comment says so.

v2 is a vertical twin-chain loop: two #35 chains in vertical planes, one at
the front of the carriages (the auger's outlet/hinge end) and one at the
back (cap end). Each chain runs round four 32T sprockets on the corners of a
rectangle; the front and back sprockets at each corner share one shaft, so
the two chains can't drift out of step. The carriages bolt to an A-1 lug on
each chain from the outside of the loop and the modules ride on the inside,
between the chains. The station is on the bottom straight.

One place for every number the model uses. Purchased-part dimensions come
from the vendor's own tables (sources in BOM.md); printed-part numbers are
design choices. World frame: x along the augers (front chain's centre plane
at x = 0, back chain's at x = CHAIN_L), y across the loop (a positive chain
shift moves the bottom run toward +y; the machine runs the other way,
RUN_DIRECTION = -1), z up, bench top at z = 0.
"""
from __future__ import annotations

import math

# --- ANSI #35 roller chain (ASME B29.1; the Aobbmok listing on the ME order) ---
# Checked against Nitro's RC35 dimension table (nitrochain.com/35-roller-chain-10ft, read 2026-10-27; cad/vendor/AUDIT_other.md):
# P 3/8, b1 3/16, d1 (bushing) 0.200, L 0.488, d2 0.141, h2 0.346, T 0.050 in.
P = 9.525            # pitch (3/8")
BUSH_D = 5.08        # #35 is rollerless: the bushing (0.200") is what the teeth seat on
CHAIN_PIN_D = 3.58   # 0.141". Was PIN_D, which the 5 mm hinge pin further down overrode: the chain was drawn with 5 mm pins
W_IN = 4.78          # width between inner plates (0.188")
PLATE_T = 1.27       # 0.050"
PLATE_H = 8.79       # plate height, 0.346" (Nitro h2; was 9.0 = 0.354")
N_LINKS = 104        # per chain, cut from a 10 ft roll (two loops use 208 of its 320 links)
INNER_W = W_IN + 2 * PLATE_T              # 7.32, inner link across the plates
OUTER_GAP = INNER_W + 0.05                 # outer plates' inside faces
OUTER_W = OUTER_GAP + 2 * PLATE_T          # 9.91
PIN_LEN = 0.488 * 25.4                     # 12.40: Nitro's overall width L, riveted pin ends 1.24 mm proud (was 0.45 mm proud)

# A-1 attachment connecting link (bent tab, one hole): Nitro CL35-A1, which
# matches Tsubaki's RS35 A-1 table: S = 0.250 in pitch line -> tab face,
# C = 0.375 in chain centre plane -> hole, X = 0.562 in -> tab end, N = 0.312
# in tab width, hole 0.133 in (M3; Red Boar's is 0.10 in). With the chain in a vertical plane
# the tab lies along the pins, on the outside of the loop, and its hole is
# radial: vertical at the station, square to the augers and to the travel.
A1_C = 6.35          # S: pitch line -> tab mounting face (radially outward)
A1_HOLE_D = 3.38
A1_TAB_L = 7.9       # N
A1_HOLE_C = 9.525    # C, from the chain centre plane toward the modules
A1_X = 14.3          # X, tab end from the chain centre plane

# --- 32T ANSI 35 sprockets, type B (hub one side): 35BS32-5/8, Surplus Center 601139 ---
# 32 teeth: four 90-degree wraps of exactly 8 links each, and a pitch radius
# big enough that the auger's 44T gear clears the corner shafts (see SHAFT_CLEAR).
N_TEETH = 32
PD = P / math.sin(math.pi / N_TEETH)                 # 97.13 pitch diameter
R = PD / 2                                           # 48.57
OD = P * (0.6 + 1 / math.tan(math.pi / N_TEETH))     # 102.42 outside diameter
TOOTH_W = 4.27       # 0.168" single-strand #35 tooth
SEAT_D = 1.005 * BUSH_D + 0.076                      # ANSI seating-curve diameter
HUB_D = 50.8         # 2 in hub
LTB = 22.225         # length through bore, 7/8 in
SPROCKET_BORE = 15.875  # 5/8 in finished bore, 3/16 x 3/32 in keyway, 2 set screws
KEYWAY = (4.76, 2.38)

# --- loop: four sprockets on a rectangle, 104 links ---
LOOP_M, LOOP_N = 12, 24  # links on the bottom/top runs and on each side
LOOP_B = LOOP_M * P  # 114.3 horizontal centre distance: 32T tips (102.4 OD) clear by 11.9 mm
LOOP_A = LOOP_N * P  # 228.6 vertical centre distance: room to tilt module 1 to 90 deg
assert 2 * (LOOP_M + LOOP_N) + N_TEETH == N_LINKS   # closes exactly: 24 + 48 + 32
LOOP_Y = LOOP_B / 2  # corner shafts at y = +-57.15
# Raised from 210 mm (Oct 13) so the station's Actuonix P16-150 fits under the hinge standing upright, as in the
# paternoster: rod end 72 mm under the hinge, 197.4 mm retracted + 20 mm docking stroke, 21.7 mm base clevis on a
# base rail (top at 35 mm). That needs the hinge at 351 mm or more; Z_RUN 345 puts it at 356.65.
Z_RUN = 465.0        # bottom run's pitch line above the bench (v4: 385; v5: 80 mm higher, so the HR-202i stands under the station)
Z_BOT = Z_RUN + R    # bottom corner shafts
Z_TOP = Z_BOT + LOOP_A                               # top corner shafts (as built, before tensioning)
CHAIN_L = 305.0      # front chain -> back chain, centre plane to centre plane

# --- modules ---
MODULE_LINKS = 8                                      # 8 pitches = 76.2 mm
N_MODULES = N_LINKS // MODULE_LINKS                   # 13

# --- the module on a carriage (Sam's Oct 8 mounting plate + the lab auger) ---
# Sam's studio frame: hinge axis = his y, auger axis = his x at z = 0, the
# plate's underside at z = -18. On a carriage his x points front -> back,
# his y along the travel and his z into the loop.
HINGE_X = 33.0       # hinge axis, from the front chain's centre plane
SAM_DROP = 18.0      # hinge axis above the plate's underside
GEAR_R = 23.0        # the auger's 44T gear (46 OD), its widest part
AUGER_Z0_XS = 0.4    # auger STEP z = 0 (outlet end) in Sam's x
AUGER_LEN = 250.0

# --- printed carriage ---
# Carriage frame: u along the travel, w radially inward (into the loop), x
# front -> back. Origin on the front chain's pitch line, mid-way between the
# A-1 link's pins. The plate sits on the two A-1 tabs, outside the chains.
CAR_W = 66.0         # along the travel: 10.2 mm between neighbours (v4: wider, the module swings through its 51.6 mm opening)
CAR_T = 5.0          # Sam's base plates are 5 mm
CAR_W0 = -A1_C                                       # plate's inner face (on the tabs)
CAR_X0, CAR_X1 = -23.0, CHAIN_L + 23.0               # tongue ends, beyond both chains
TONGUE_W = 40.0      # along the travel
TONGUE_L = 16.0      # beyond the chain's outer plates
RIB = (4.0, 7.0)     # edge ribs on the inside: width, height
HINGE_W = CAR_W0 - CAR_T - SAM_DROP                  # -29.35 (v4): hinge axis outside the carriage plate, the module outside the loop
LUG_U = 25.5         # hinge lug inner faces, 0.5 mm outside Sam's 50 mm knuckle
LUG_T = 4.0          # lugs end at u = +-29.5, inside the carriage's +-30
# On a corner two neighbours are 90 deg apart about the sprocket axis, so a
# point (u, w) on one meets the other unless |u| + w < R (48.6). The lugs are
# chamfered to |u| + w <= INNER_CORNER and the hinge screws are flush.
INNER_CORNER = 45.0
HINGE_D = 5.3        # Sam's knuckle holes (5.3 mm) and the lugs' pin holes
# Hinge pins: 5 mm clevis pins with a retaining-ring groove, head flush in a counterbore on the lug's outer
# face, an e-clip on the inner end between Sam's knuckle (|u| 15) and the auger tube (|u| 12.5). A threaded
# pin would loosen with the vibration and the roll over the top; a protruding thumb screw hits the next
# carriage on a corner (the |u| + w <= INNER_CORNER rule).
PIN_D = 5.0
PIN_HEAD = (8.0, 1.6)                                 # head diameter, height
PIN_CBORE = (8.6, 1.8)                                # counterbore in the lug for the head
PIN_GROOVE_U = 14.4                                   # e-clip groove (outer face), from the carriage centre along u: 0.6 mm inside the knuckle face
ECLIP = (8.85, 0.7)                                   # DIN 6799-4 (4 mm groove, 0.74 wide, on a 5 mm pin): McMaster 98543A112, OD 8.85, 0.7 thick
# Station reach-through: Sam's electronics carriage (his x 2.3-73.3, y +-18),
# the gear (his x 78.3-88.3) and the outlet's powder path when tilted.
WIN_X = (HINGE_X - 14.0, HINGE_X + 116.0)             # 130 mm: the docked electronics carriage sweeps the window's back edge at about 28 deg of tilt
WIN_U = 23.5                 # the U-yoke's steel arms pass at |y| 19.5-21.5 and their e-clips at 22.3
# Snap hooks that keep Sam's plate shut upside down (top of the loop): they
# overhang the plate's edge where it is 50 mm wide (his x 40-65).
SNAP_X = HINGE_X + 52.0
SNAP_LAP = 0.8       # overhang onto the plate's top edge

# --- 2020 frame, built vertically ---
EXT = 20.0
POST_Y = 180.0       # post centres (v4): the side runs' modules reach y +-161 outside the loop
SIDE_GAP = 30.0      # chain centre plane -> side plate's inner face
PLATE_T_SIDE = 6.35  # 1/4 in 6061 side plates
SIDE_W = 2 * POST_Y + EXT                             # 380 (v4)
_DZ = Z_RUN - 210.0                                   # everything above the bench moved up with the loop (Oct 18)
SIDE_Z = (180.0 + _DZ, 555.0 + _DZ)                   # front side plate bottom, top
SIDE_Z_BACK = (70.0 + _DZ, 555.0 + _DZ)               # the back plate runs down to carry the motor
FOOT_H = 15.0        # leveling foot: bench -> underside of the base rails
Z_BASE = FOOT_H      # base rails' underside
Z_TOP_RAIL = 576.0 + _DZ   # 751 (v4): top rails' underside, 21 mm over the side plates as v3; the top run's gears reach z 763
TENSION_TRAVEL = (-6.0, 8.0)  # top shafts' slot travel about nominal: down to fit the chain, up to tension it
DRIVE_TRAVEL = 4.0   # motor slides +-4 mm in its slots to tension the drive chain

# --- shafts and bearings (all four corners alike) ---
SHAFT_D = 15.875     # 5/8 in keyed shafting (the sprockets' bore)
# Surplus Center 600174. Its rear dome sits in a 49 mm hole in the plate (FYH catalogue).
# SBSFL202-10 = SBPFL202-10 2-bolt pressed-steel flangette, 5/8 in SB insert. USA Bearings & Belts' SBPFL202-10 table
# and drawing (read 2026-10-27; Surplus Center's own page is behind a bot check): a 3-3/16 (81.0), e 2-1/2 (63.5),
# B 2-5/16 (58.7), t 0.079 (2.0 mm sheet: two halves, so 4.0 at the bolt lobes), b 5/8 (15.9 dome to dome),
# S 9/32 (7.1 bolt hole), L .8661 (22.0 inner ring), n .236, k 1-1/4. The bearing's centre plane is one sheet (2.0)
# above the mounting face, the housing +-7.95 about it, and the inner ring runs from flush with the rear dome to 6.1 mm
# beyond the front one (set-screw collar outward). Was T 3.0, OUT 12.6, IN 9.6 (domes 10.6 / 8.6). cad/vendor/AUDIT_other.md
BRG = dict(L=81.0, W=58.7, J=63.5, T=4.0, OUT=16.05, IN=5.95, DOME_D=47.0, DOME_OUT=9.95, DOME_IN=5.95, RING_D=24.0,
           BOLT_D=6.35, HOLE=49.0)
SHAFT_CLEAR = R - HINGE_W - GEAR_R - SHAFT_D / 2     # 6.0: gear past a corner shaft

# --- StepperOnline 34HS59-6004D-E1000 (NEMA 34, 12 N*m, 1000-line encoder) ---
M34_FLANGE = 86.0
M34_BOLT_SQ = 69.58
M34_HOLE_D = 5.5
M34_PILOT_D = 73.0
M34_PILOT_H = 2.0      # StepperOnline STEP (paternoster/reference): 73 x 2.0 (was 1.6); its holes are 6.5 (M34_HOLE_D is our plate's slot)
M34_SHAFT_D = 14.0
M34_SHAFT_L = 37.0   # 25 mm of it keyed
M34_KEY_W = 5.0
M34_BODY_L = 150.0
M34_ENC_L = 19.0

# --- drive: NEMA 34 inside the frame on the back plate, #35 drive chain up to the B+ shaft ---
# Two 35BS15H sprockets (Surplus Center: 5/8 in keyed on the shaft, 1/2 in
# re-bored to 14 mm + 5 mm keyway on the motor): 1.99 in OD, 1-11/32 in hub,
# 3/4 in through the bore. 44 links from the roll's spare, 1:1.
N15 = 15
PD15 = P / math.sin(math.pi / N15)                   # 45.81
HUB15_D, LTB15 = 34.1, 19.05
DRIVE_LINKS = 44
C_DRIVE = (DRIVE_LINKS - N15) / 2 * P                # 138.11: closes exactly with 14-link spans (as v1's loop)
Z_MOTOR = Z_BOT - C_DRIVE                            # 120.46: motor axis, under the B+ shaft

# --- station test fixtures ---
HOLD_DOWN_GAP = 2.0          # lip above the tongue (was 0.5): the PyBullet runs showed tongues snagging on a 0.5 mm lip
HOLD_DOWN_LEAD = 3.0         # lead-in chamfers on the lip and the foot, 3 mm deep
# The foot under the tongue was 2 mm below it. The physics sim (sim/carousel_sim.py) found that a tongue's leading
# corner dips about 1.2 mm below the run line while its carriage swings off the B- sprocket, and that corner then
# hit the foot's end face and stalled the drive. 4 mm clears it with the lead-in chamfer to spare.
HOLD_DOWN_FOOT_GAP = 4.0
# Slider rails under the station carriage: two UHMW-topped bars along the travel, just under the carriage plate, so
# the plate rides on them at the station and its height no longer depends on how much the bottom run sags
# (the sim showed 2-4 mm of sag at 40 N chain tension, enough to hang a tongue on the hold-down foot).
SLIDER_GAP = 0.3                 # rail top below the plate's nominal outer face
SLIDER_X = ((152.0, 168.0), (256.0, 282.0))   # under solid plate: between the window and the first lightening hole, and behind the last one
LIGHTEN_XC = (190.0, 232.0)                  # lightening holes in the carriage plate, 34 mm long, 36 wide
SLIDER_HALF_L = 25.0             # along the travel, about the station: a carriage corner swinging off a sprocket dips below the run line beyond this
SLIDER_RAMP, SLIDER_RAMP_L = 3.0, 10.0   # lead-in at each end of a rail: drop, length
MAGNET_D, MAGNET_H = 6.35, 3.18                       # K&J D42-N52, 1/4 x 1/8 in


# --- carriage to chain: slide-on hooks with captive locknuts (through-bolted, from the outside) ---
# Each tab slides into a printed hook under it (between the tab and the chain's pitch line); an M3 nylon-insert
# locknut sits in a hex pocket in the hook, and an M3 x 12 button head goes in from the carriage's outer face
# through the plate and the tab into it. To take a carriage off: two screws out, slide it 10 mm along the run so
# the hooks clear the tabs, lift it out. Nothing has to be reached from inside the loop.
TAB_SCREW_L = 12.0
TAB_SCREW_CB = 1.8                                    # counterbore for its head in the plate's outer face: the head sits flush
SCREW_OUT = 10.0                                      # backed out this far to swap, the tips clear the tabs and stay in the plate
HOOK_SLIDE = 10.0                                     # slide along u to engage / free the hooks
NUT_AF, NUT_H = 5.5, 4.0                              # M3 nylon-insert locknut (DIN 985)

# --- chain tension and speeds (sim and test plan) ---
CHAIN_TENSION_N = 80.0       # per chain: 3-4 mm under a 5 N side push on a 228.6 mm side

# --- frame pitch (evaluated and rejected, kept as a parameter) ---
# Pitching the whole frame outlet-end up would keep every outlet up all the way round (each module rolls about an
# axis parallel to its auger). The auger-leakage study (../auger-leakage/) found no measurable difference at 0, 5,
# 10 and 15 deg: the only afterflow leaves while the module is still above 10 deg on the way back from the dose,
# where no rest pitch can catch it. A pitch also makes the dose stream drift back into the docked electronics
# carriage's footprint (layout.stream_check): the fixed D-funnel catches it only up to about 2.4 deg. So 0.
FRAME_PITCH_DEG = 0.0
# Run direction. Each lap turns every module once about its own axis, which acts like one auger turn. With the
# bottom run travelling toward +y (counter-clockwise seen from the back) that turn is a forward one and a primed
# auger pumped about one revolution's dose out during a lap (proxy sim); the other way it retracts powder from the
# exit. So v2 runs with the bottom run travelling toward -y. kinematics.py keeps +shift = toward +y; the
# machine's normal travel is RUN_DIRECTION * shift.
RUN_DIRECTION = -1           # -1: bottom run toward -y (clockwise seen from the back)

# --- station: Actuonix P16-150-22-12-P, pinned at both ends (as the paternoster) ---
ACT_STROKE = 150.0
ACT_RETRACTED = 197.4        # hole to hole, retracted (Actuonix STEP): stroke + 47.4
CLEVIS_GAP = 8.4             # between the base clevis cheeks: the P16's rear tab is 8 thick (datasheet)
SHOULDER_CLEVIS_L = 16.0     # McMaster 4 x 16 mm shoulder screw (M3 thread) through cheek, tab, cheek
ACT_CLEVIS_D = 4.25          # both clevis holes
# Carriage pin at the carriage's centre-of-mass height. The P16 is pinned at both ends, so it gives the carriage no
# moment: the dock (rim + locating pins + magnet face) has to hold the carriage's attitude. With the pin under the
# carriage (the paternoster's (40, -72)) the carriage is an inverted pendulum on it, COM 39 mm above, and the dock opens
# at a few newtons of gear load once tilted (station sim + the main session's tooth-contact model). At COM height the
# carriage hangs balanced: two 4 mm steel stub pins pressed through the carriage's solid side post (x 29-35) and a
# printed boss, a U-yoke on the rod end with 2 mm steel arms up both sides (outside the carriage's |y| 18), so the
# carriage can turn freely in it. Station sim, dock-opening separating force at 30 deg: 13.3 N here, 10.2 N at
# (45, -34), 6.1 N for the old pin, 0.4 N with the pin on the mesh line (83.4, -52).
YOKE_X, YOKE_Z = 32.0, -34.0 # carriage stub-pin axis, Sam's frame (carriage as drawn)
UFORK_L = 60.0               # stub-pin axis -> the P16's rod-end hole, along the actuator: the crossbar clears the carriage's
                             # front-bottom corner (51 mm from the pins) as the carriage turns 92 deg in the yoke
UFORK_Y = (19.5, 21.5)       # steel arm, |y| (2 mm); printed boss on the post |y| 18-19.5; e-clip outside at 21.7-22.3
TONGUE_X, TONGUE_Y = YOKE_X, 15.0   # guide tongue under the yoke's crossbar, rides the approach fork
YOKE_STOP_Z = -11.0 - 0.3 - 4.0     # stop blocks on the arms (yoke frame z of the block's bottom): 0.3 mm under the pin plate's
                                    # tail. Was a block under the carriage's back bottom (|y| 15.5-19.5), which the carriage's
                                    # front-bottom corner swept into past 70 deg of tilt (check_interference --tilt); now, as the
                                    # paternoster, the stop and the tail sit at |y| 18.2-19.5, outside the carriage's |y| 18
DOCK_EXT = 20.0              # actuator extension when the carriage meets the plate; 90 deg needs 282.5 of the P16's 347.4 mm
# Locating pins on the carriage rim (steel dowels, conical tips) into a hole and a slot in the plate's underside: they
# carry the along-plate load at tilt instead of friction; the slot runs along x to take the 40 mm pin spacing's tolerance.
LOCPIN_D, LOCPIN_PROUD = 4.0, 3.0    # dowel diameter; protrudes 3 mm above the rim (2.1 mm into the plate when docked)
LOCPIN_XY = ((30.0, 16.0), (70.0, -16.0))   # Sam's frame; the first goes in a 4.2 mm hole, the second in a 4.2 x 6 slot
LOCPIN_HOLE, LOCPIN_SLOT = 4.2, 6.0
SEP_RATIO_STEEL = 0.55       # separating / tangential force at the mesh with the steel pinion and dry PTFE lube
DOCK_RISE = 0.9              # Sam's Part Studio leaves the carriage 0.9 mm under the plate; docked, they touch
CLEVIS_H = 21.7              # base clevis pin above its foot
FORK_H = 36.0
TILT_DOSE_WORLD = 30.0       # default dose tilt, degrees from horizontal in the world (frame tilt = this + pitch)
TILT_MAX_FRAME = 90.0        # hinge travel limit (the P16-150 reaches 90 deg with 65 mm of stroke to spare)
NEMA11_X, NEMA11_Z = 68.3, -33.15  # NEMA 11 mounting face on the inside of Sam's carriage's back wall (x 68.3-73.3), boss in his
                                   # pilot recess, M2.5 screws from outside; its 20 mm shaft ends at x 88.3, the pinion's back face.
                                   # Pinion axis 32.25 mm under the auger axis when docked (Sam's pilot is at -33.0: the motor sits
                                   # 0.15 mm low in the 22.1 mm recess); 32.25 mm leaves 0.12 mm of backlash after the plate bends
                                   # under the magnet (gear-mesh study: 32.1 mm jammed with printed-gear runout)
PINION_X0 = NEMA11_X + 10.0        # pinion's motor-side face: 78.3-88.3, on the shaft's last 10 mm
SOL_X, SOL_Z = 12.0, -24.0   # solenoid under the auger tube near the outlet, plunger up
GEAR_X = 78.4                # the auger's 44T gear face nearest the outlet, in Sam's x (gear 10 mm wide)

# Dock electromagnet behind the pinion + steel armature tab under each plate's back strip (the gear-mesh
# preload: the module's weight alone can't hold the 20T:44T mesh against the NEMA 11, see cad/gear-mesh/).
# Adafruit 3872 P20/15: 20 x 15 mm, 5 V, 0.22 A, about 24.5 N holding at zero gap. Sam's frame, carriage as
# drawn (top face z -18.9; docked it rises DOCK_RISE so the rim touches the plate and sets the 32.25 mm centre
# distance). The face sits 0.15 mm under the armature when docked, so the rim, not the magnet, locates.
DOCK_MAG_D, DOCK_MAG_H = 20.0, 15.0
DOCK_MAG_XY = (99.5, 0.0)
DOCK_MAG_FACE_Z = -18.0 - 2.0 - 0.15 - DOCK_RISE  # -21.05 as drawn
ARMATURE_X = (89.0, 111.0)   # low-carbon steel tab, 2 mm, |y| <= 14, top face on the plate's underside (z -18)
ARMATURE_HW, ARMATURE_T = 14.0, 2.0
ARMATURE_SCREWS = ((94.0, -10.0), (94.0, 10.0))   # M3 x 6 flat heads into M3 inserts in the plate's back strip

# vial on a 100 g load cell (gravity-referenced: plumb in the world)
VIAL_H = 61.0
VIAL_D = 28.0
LC_L = 47.0                  # TAL221 (SparkFun SEN-14727) is 47 x 12 x 6 (datasheet); was 80, the TAL220's length
CUP_ARM = 63.0               # vial cup's arm (printed): 33 mm longer than with the 80 mm stand-in, so the real 47 mm cell's fixed end stays on the level wedge
VIAL_DROP = 30.0             # outlet to funnel mouth, world vertical
FUNNEL = dict(top_d=36.0, spout_d=18.0, h=22.0)


# =====================================================================================================================
# v3 (Sam's critiques of 2026-10-29). Sam's frame, docked at the station unless a comment says otherwise: x along the
# auger from the hinge axis (outlet end at x = 0.4), y along the hinge axis (the travel at the station), z away from
# the plate (auger axis z = 0, plate underside z = -18).
# =====================================================================================================================

# --- 1. kinematic dock between the electronics carriage (EC) and the mounting plate (a Kelvin clamp) ---------------
# Sam's Aug 27 carriage (his fit-together video) located the plate with four cone-tipped posts in four holes, which is
# one more constraint than a rigid pair needs. v3 uses exactly six contacts: two 1/4 in chrome-steel balls pressed into
# the plate's underside sit in a cone (A, +y) and a vee (B, -y, its groove along y, toward A) on the EC, and a third
# ball on the EC presses on the plate's steel armature (the flat, C). Preload: a small N52 magnet under the cone and
# under the vee (each pulls its ball in) and v2's switchable dock electromagnet, now just in front of the flat.
KC_BALL_D = 6.35                     # McMaster 9642K23-class 52100 chrome steel ball, 1/4 in (grade 25)
KC_A = (30.0, 18.5)                  # plate ball over the EC's cone seat (x, y): the cone stays 1 mm off the NEMA 11 (|y| 14)
KC_B = (30.0, -18.5)                 # plate ball over the EC's vee (8 mm dowels: y -22.5..-14.5)
KC_C = (114.5, 0.0)                  # EC ball under the plate's armature (the flat), 0.8 mm behind the electromagnet
KC_BALL_Z = -18.6                    # plate balls' centres: 3.8 mm proud of the underside (pressed 2.6 mm into the plate)
KC_SEAT_TOP = -19.6                  # top of the EC's seat ears when docked: 1.6 mm under the plate
KC_CONE_HALF = 45.0                  # cone seat half-angle (printed, line contact: about 11 MPa at 5 N)
VEE_DOWEL_D, VEE_DOWEL_L = 3.175, 12.7   # 1/8 x 1/2 in hardened dowels, two per vee (steel on steel: point contacts)
VEE_SPACING = 2 * (KC_BALL_D / 2 + VEE_DOWEL_D / 2) * math.sin(math.radians(45.0))   # 6.73: 90 deg vee
KC_MAG_D, KC_MAG_H = 6.35, 6.35      # K&J D44-N52 (1/4 x 1/4 in) under the cone and under the vee
KC_MAG_GAP = 0.6                     # magnet face below the seated ball's lowest point
DOCK_RISE_V3 = 0.9                   # EC as drawn -> docked: the pinion's centre distance stays 32.25 mm (v2)
EC_RIM_CUT = 1.8                     # Sam's carriage top rim cut down 1.8 mm (to 0.2 under the seat ears): only the three contacts touch the plate
ARMATURE_X3 = (89.5, 121.0)          # steel armature (2 mm, |y| <= ARMATURE_HW3): from behind the 44T gear's slot out past the plate
ARMATURE_HW3 = 11.0
ARMATURE_SCREWS3 = ((92.0, -7.0), (92.0, 7.0))   # M3 flat heads into heat-set inserts in the plate's back strip
DOCK_MAG_XY3 = (100.0, 0.0)          # Adafruit 3872 face 0.15 mm under the armature (as v2), 12 mm ahead of the flat

# --- 2. the guide: the EC parks on its own kinematic seat below the passing carriages and rises square ------------------
# A printed cradle on a 2020 post: a floor with a second Kelvin clamp for three balls under the EC (cone, vee, flat), side
# walls 0.3 mm off the EC's narrow lower body (|y| 15) and a front wall 0.3 mm ahead of its front face. No back wall above
# the floor: the tilt carries the EC backward and up out of the cradle, parallel to the side walls. The P16 pushes the EC
# through a pin in a slotted clevis under its back half, so the EC's centre of mass is ahead of the pin and it leans on the
# front wall while it rises; the slot (lost motion) lets the actuator stop anywhere near the dock or the seat without
# forcing either: the magnets hold the dock, the EC's weight holds the seat.
EC_BASE_T = 3.0                      # printed base under Sam's carriage (as drawn its bottom is at z -60.8)
EC_BASE_Z = -60.8                    # base's top face, as drawn
EC_BALLS = ((69.0, 11.5), (69.0, -11.5), (40.0, 0.0))   # cone, vee (along y), flat, under the base: the EC's centre of mass
                                                     # (x 52) is inside their triangle and clear of the clevis
EC_PIN = (58.0, -76.0)               # clevis pin (x, z), as drawn: 6 mm behind the EC's centre of mass, so it leans forward;
                                     # 12 mm under the base, so at 90 deg the P16's rod passes under the flat ball
EC_CHEEK_Y = (4.8, 9.8)              # clevis cheeks: 9.6 mm apart, the rod (8.94) swings between them at any tilt; two 0.8 mm
                                     # PTFE washers each side take up the gap round the rod end's 6 mm tab
EC_SLOT = 2.0                        # lost motion in the clevis slots
GUIDE_CLEAR = 0.3                    # side and front walls off the EC's lower body
GUIDE_WALL_T = 2.5
PARK_DROP = 20.0                     # parked EC sits this far below its docked position (v2's DOCK_EXT)

# --- 4. the outlet door: a spring-loaded shutter on every auger, pushed open by the docked EC --------------------------
# A printed housing between Sam's knuckle arms holds a 1.5 mm shutter 0.3 mm in front of the auger's end face. A
# stainless compression spring pushes it down over the 3 mm exit. Its push rod runs down beside the exit (y = DOOR_ROD_Y,
# out of the dose stream) to below the plate; a finger on the EC's front lifts it DOOR_TRAVEL in the last 10 mm of the
# dock, so the exit is uncovered only while the EC holds the module, and the door closes before the EC lets go.
DOOR_GAP = 0.3                       # shutter's back face to the auger's end face
DOOR_T = 1.5                         # shutter thickness
DOOR_W = 10.0                        # shutter width (y)
DOOR_CLOSED_Z = (-3.5, 4.0)          # shutter's bottom and top edges, closed (covers the exit, z -1.5..1.5, by 2-2.5 mm)
DOOR_TRAVEL = 6.0                    # open: bottom edge at +2.5, 1 mm above the exit
DOOR_ROD_Y = 7.5                     # push strip beside the exit (y 6-9)
DOOR_ROD_D = 3.0                     # push strip width (it is the shutter's own +y strip, 1.5 thick)
DOOR_ROD_BOTTOM = -22.0              # rod's lower end, closed (inside the carriage window, above its outer face)
DOOR_SPRING = (3.0, 16.0, 0.06)      # OD, free length, rate N/mm (stainless): 11.5 mm fitted shut (0.27 N), 5.5 open (0.63 N)
DOOR_TOP = 19.5                      # housing's top (z): |u| 13 + w 31.2 = 44.2, inside the 45 mm corner rule
DOOR_SPRING_SEAT = DOOR_TOP - 3.0    # the cap's underside, where the spring's fixed end sits
DOOR_SPRING_SHUT = DOOR_SPRING_SEAT - (DOOR_CLOSED_Z[1] + 1.0)   # 11.5: seat to the shutter's boss, door shut

# --- 4a. the plate latch: holds the plate on its carriage upside down; a cam at the station opens it ------------------------
# A printed bolt slides along x in a housing on the carriage's inner face behind the plate, at y = LATCH_Y (beside the auger
# tube). A spring pushes it forward over a keeper on the plate's back end. Its follower pin runs down through a slot in the
# carriage plate; at the station a fixed rail along the travel pushes the follower back LATCH_TRAVEL, so every carriage's
# latch is open while it sits at the station (module right side up, resting on the carriage) and closes as it leaves.
LATCH_Y = 19.0                       # v4: his y is the world's -y at the station, so +19 puts the follower and the station's rail on
                                     # the world's -y side, within +-28 mm of the station where no carriage tips round a corner
LATCH_W = 8.0                        # bolt width (y)
LATCH_KEEPER_X = (98.0, 103.0)       # keeper block on the plate's back end, |y| 14-24, top face z -13
LATCH_LAP = 3.0                      # bolt over the keeper when closed
LATCH_TRAVEL = 4.5                   # bolt stroke: open leaves 1.5 mm between the bolt and the keeper's back edge
LATCH_RAIL_FLAT = 4.0                # rail flat, +- about the station follower (the index repeats to +-0.5 mm)
LATCH_FOLLOW_X = 120.0               # follower pin (closed), x
LATCH_FOLLOW_PROUD = 4.0             # follower tip below the carriage's outer face
LATCH_SPRING = (4.0, 12.7, 0.25)     # OD, free length, rate N/mm: 0.9 N closed, 2.0 N open

# --- 5. enclosure: clear acrylic on the 2020 frame, a front hatch for the scale, a side hatch for swaps -------------------
ACRYLIC_T = 3.0                      # 1/8 in cast acrylic (actual 0.118 in)
PANEL_STANDOFF = 6.0                 # panels on spacers outside the frame: the side runs' carriages reach y +-117, the side tabs +-124
WIN_BACK_V3 = 125.0                  # v3 carriage window's back edge (Sam's x): EC v3's flat ball and boss reach x 119
PAD_X0_V3 = 90.5                     # pads under the plate's back corners start here (EC v3's bracket arms end at x 90)
PAD_U0_V3 = 15.5                     # pads at |u| 15.5-23.5: the EC's base and its seat balls sweep |y| <= 14.7 through the
                                     # carriage's plane at 30-35 deg of tilt
SIDE_TAB_FOOT_GAP = 4.0              # side tab foot outside the tongue (v4 makes it 1 mm: the auger pull goes through it)
HATCH_FRONT = (300.0, 330.0)         # v5: front hatch (y width, z height), centred on the station, from the bench up: the
                                     # HR-202i's display pokes out under the door, and a hand reaches its side doors (v4: 180 x 230)
HATCH_SIDE = (330.0, 230.0)          # side hatch on +y (x width, z height), centred on the loading position
HATCH_OPEN_DEG = 110.0

# --- 6. the scale: A&D HR-100A (the lab's balance: 102 g x 0.1 mg), from A&D's manual (HR-A/HR-AZ manual section 22) ------
HR_W, HR_D, HR_H = 198.0, 253.0, 315.0       # base 198 wide, 61.5 + 191.5 deep; 315 tall over the breeze break
HR_PAN_D, HR_PAN_Z = 90.0, 86.5              # weighing pan, height of the pan
HR_CHAMBER_D_IN, HR_CHAMBER_H_IN = 156.0, 198.0   # round glass breeze break: inside diameter, inside height above the pan
HR_PAN_FROM_FRONT = 162.0                    # pan centre behind the front (display) edge, measured off the drawing
BEAKER_D, BEAKER_H = 38.0, 49.0              # 25 mL low-form beaker (DWK/Kimble 14000-25 class)


# =====================================================================================================================
# v4 (Sam's item 7): the augers outside the loop. Sam's frame on a carriage: his x along the auger, his z AWAY from the
# carriage (outward), his y = -u. The plate's underside (z -18) sits on the carriage's outer face.
# =====================================================================================================================
OPEN_U = 25.8                        # the carriage's opening: the module (plate +-25, gear +-23) swings up through it into the loop
OPEN_X = (HINGE_X - 14.0, HINGE_X + 255.0)   # carriage x 19-288: from in front of the hinge to past the cap (Sam x 252.4)
OPEN_U_BACK = 27.6                   # wider over Sam's x 52-104, where his plate is +-27.02 (its back strip)
OPEN_BACK_X = (52.0, 104.0)          # Sam's x (carriage x = HINGE_X + these), ahead of the latch housing
LUG_U4 = 26.0                        # hinge lugs on the outer face, |u| 26-30, round the plate's knuckles (|u| 15-25)
TILT_MAX_V4 = 50.0                   # the module swings into the loop; at about 55 deg its cap reaches the top run
# kinematic dock on the plate's auger side (the EC docks from outside, round the auger): the side strips between the clamps
KC4_A = (44.0, 19.5)                 # cone (plate ball)
KC4_B = (44.0, -19.5)                # vee along y (plate ball)
KC4_C = (64.0, 19.5)                 # flat: a steel washer on the plate's top face, the EC's ball C on it
KC4_BALL_Z = -13.0 + KC_BALL_D / 2 - 2.6     # -12.425: plate balls pressed 2.6 mm into the top face, 3.8 proud toward +z
KC4_SEAT_TOP = KC4_BALL_Z + 1.0              # -11.425: the seats' faces, 1.6 mm off the plate's top face
KC4_PAD = (10.0, 1.0)                # M5 steel washer (OD, thickness) bonded in a pocket in the plate's top face at KC4_C
DOCK_RISE_V4 = -0.9                  # EC v4 (Sam's carriage mirrored through the auger axis) moves 0.9 toward the plate to dock:
                                     # the pinion sits 32.25 mm from the auger axis on the auger's far side
EC4_ARM = (15.5, 23.5)               # the arms' |y| (between the clamps' 14.55 and the plate's 25)
EC4_ARM_X = ((38.5, 68.3), (38.5, 49.5))     # +y arm (cone and C), -y arm (vee)
# plate latch (v4): a pin in a hole, so it holds the plate both ways (the opening leaves nothing under the plate)
LATCH4_KEEPER_X = (98.0, 106.0)      # keeper block on the plate's back end, |y| 14-24, z -18..-9, a 4.2 mm hole along x at z -13.5
LATCH4_PIN = (4.0, -13.5)            # bolt pin diameter, its axis z
LATCH4_ENGAGE = 4.0                  # pin in the hole when closed
LATCH4_FOLLOW_TIP = 24.0             # the follower runs from the bolt beside the tube out to z +24 (beside the cap's +14.5)
# cap rest at the station: with the latch open the module rests 0.5 mm down on it, on its cap, until the EC docks
CAP_REST_X = (229.0, 247.0)          # Sam's x, under the cap (Sam x 224.7-252.4, radius 14.5)
CAP_REST_GAP = 0.5
SIDE_TAB_FOOT_GAP_V4 = 1.0           # v4's side tabs: the foot 1 mm outside the tongue, so pulling an auger off barely moves the carriage
SIDE_TAB_FOOT_GAP = SIDE_TAB_FOOT_GAP_V4
LUG_U = LUG_U4                       # parts.clevis_pin sizes the hinge pins' grip from LUG_U
TUBE_REST_X = (106.0, 116.0)         # the station's rest under the auger tube (Sam's x, behind the keeper), face 0.5 mm off the tube

# Park depth (2026-10-30, check_interference --sweep): at v3's 20 mm the parked EC v4's arms still straddle the auger, and
# the augers passing the station hit them 2 links either side of it (up to 242 mm3). 8 mm deeper cleared every pose tried
# (checks/sweep.json, park_drop_test). The P16's base pin drops with it (the base clevis rises 20.2 mm above its rail).
PARK_DROP = 28.0


# =====================================================================================================================
# v5: the balance under the station. A&D HR-202i (HR-i series), from A&D's HR-i instruction manual, 15.1 "External
# Dimensions" (as read for byu-vcl's lab_models; checked again here, see README "The balance"). Display toward the
# front (-x), the weighing chamber under the dose point, the mechanism tower behind it (+x).
# =====================================================================================================================
HR2_W, HR2_W_DOORS = 200.0, 217.0            # body width; over the side doors' grips
HR2_D, HR2_D_ALL = 428.0, 442.0              # body depth; overall
HR2_H, HR2_H_ALL = 310.0, 316.0              # body height; over the top door's grip
HR2_PAN_D, HR2_PAN_Y, HR2_PAN_TOP = 90.0, 163.0, 50.0   # pan dia., its centre behind the front, its top above the bench (all printed on p.60)
HR2_CH = (183.0, 164.5, 250.0)               # chamber inside: width, depth, height above the pan
HR2_CH_Y = HR2_PAN_Y - 86.5                  # chamber's front glass behind the front (the pan is 86.5 mm behind it)
HR2_DOOR = (148.5, 251.0)                    # side doors (depth, height); both slide back
HR2_TOP_DOOR = (164.0, 148.5)                # top door (width, depth); slides back over the tower
HR2_FEET_X = 166.0                           # rear feet apart
HR2_GLASS, HR2_FRAME = 4.0, 7.0
HR2_NOSE = (24.0, 46.0)                      # display section's top: 28 at the nose, 50 at the glass (A&D's DXF; + 4 in the builder)
HR2_FLOOR = 40.0                             # chamber floor and the side doors' sills (A&D's DXF)
HR2_CAP_G, HR2_READ_MG = 220.0, 0.1
HR2_FINE = (51.0, 0.01)                      # fine range: g, mg
HR2_TOP_GAP = 10.0                           # the parked EC, the lift bar and the NEMA 34 stay this far over the balance's top
HR2_REAR = (276.0, 244.0, 221.0)             # rear housing: starts this far behind the front; its top at its front, at the back (A&D's DXF)
HR2_DOOR_TRAVEL = 205.0                      # the top and side doors slide straight back about this far (A&D's DXF, open outlines)
HR2_KG = 7.9

# the beaker on a printed riser, so the dose falls about 150 mm instead of 340 (the beaker's rim stays under the side doors'
# opening, so it comes out through a side door; the top door is under the station)
BRISER_FOOT_D, BRISER_TUBE_D, BRISER_WALL = 80.0, 44.0, 1.6
BEAKER_RIM_Z = 282.0                         # beaker rim above the bench: 9 mm under the side doors' opening's top (291, A&D's DXF), so
                                             # it clears it lifted 6 mm out of the riser's cup
BEAKER_RISER_H = BEAKER_RIM_Z - BEAKER_H - HR2_PAN_TOP + 5.0   # 194: the beaker sits 5 mm down in the riser's cup

# lift bar and the two P16s (v5's station column, moved out of the balance's chamber)
LIFT_BAR_D = 8.0                             # 8 mm precision steel shaft (h6), through the EC's base on v4's clevis-pin axis
P16_Y = 146.0                                # the P16s' axes, +-y (the balance's side doors reach +-108.5 about its centre)
LIFT_BAR_L = 2 * 132.0                       # bar ends in the end blocks' clamps, |y| 120-132
SHOE = (14.0, 10.0, 20.0)                    # guide shoe on each bar end: x, y, z (in its guide's 14.2 mm slot)
GUIDE_SLOT_W = 14.2
STATION_POST_Y = POST_Y                      # station posts on the side base rails, at the P16s' x
LATCH_BEAM_Z = 0.0                           # set in layout: the latch rail's pad sits on the beam where v4's post ended
TILT_MAX_V5 = 40.0                           # v5: the lift bar passes under the neighbouring modules; past about 41 deg it rises into
                                             # them (check_interference --tilt: 42 deg touches module 13's plate). v4: 50
