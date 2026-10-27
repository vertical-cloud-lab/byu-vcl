"""Dimensions for the chain-carousel test rig v2 (issue #128), in mm.

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
P = 9.525            # pitch (3/8")
BUSH_D = 5.08        # #35 is rollerless: the bushing (0.200") is what the teeth seat on
PIN_D = 3.58         # 0.141"
W_IN = 4.78          # width between inner plates (0.188")
PLATE_T = 1.27       # 0.050"
PLATE_H = 9.0        # plate height, 0.354"
PIN_HEAD = 0.45      # riveted pin end beyond the outer plate
N_LINKS = 104        # per chain, cut from a 10 ft roll (two loops use 208 of its 320 links)
INNER_W = W_IN + 2 * PLATE_T              # 7.32, inner link across the plates
OUTER_GAP = INNER_W + 0.05                 # outer plates' inside faces
OUTER_W = OUTER_GAP + 2 * PLATE_T          # 9.91
PIN_LEN = OUTER_W + 2 * PIN_HEAD

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
Z_RUN = 345.0        # bottom run's pitch line above the bench
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
CAR_W = 60.0         # along the travel: 16.2 mm between neighbours on the straights
CAR_T = 5.0          # Sam's base plates are 5 mm
CAR_W0 = -A1_C                                       # plate's inner face (on the tabs)
CAR_X0, CAR_X1 = -23.0, CHAIN_L + 23.0               # tongue ends, beyond both chains
TONGUE_W = 40.0      # along the travel
TONGUE_L = 16.0      # beyond the chain's outer plates
RIB = (4.0, 7.0)     # edge ribs on the inside: width, height
HINGE_W = SAM_DROP + CAR_W0                          # 11.65: hinge axis inside the pitch line
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
ECLIP = (9.0, 0.6)                                    # DIN 6799 size 4 (4 mm groove on a 5 mm pin): OD, thickness
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
POST_Y = 112.0       # post centres: clear of the bearings and the motor standoffs; the frame encloses the carriages
SIDE_GAP = 30.0      # chain centre plane -> side plate's inner face
PLATE_T_SIDE = 6.35  # 1/4 in 6061 side plates
SIDE_W = 2 * POST_Y + EXT                             # 244
_DZ = Z_RUN - 210.0                                   # everything above the bench moved up with the loop (Oct 18)
SIDE_Z = (180.0 + _DZ, 555.0 + _DZ)                   # front side plate bottom, top
SIDE_Z_BACK = (70.0 + _DZ, 555.0 + _DZ)               # the back plate runs down to carry the motor
FOOT_H = 15.0        # leveling foot: bench -> underside of the base rails
Z_BASE = FOOT_H      # base rails' underside
Z_TOP_RAIL = 576.0 + _DZ   # top rails' underside, above the side plates and the post-head brackets
TENSION_TRAVEL = (-6.0, 8.0)  # top shafts' slot travel about nominal: down to fit the chain, up to tension it
DRIVE_TRAVEL = 4.0   # motor slides +-4 mm in its slots to tension the drive chain

# --- shafts and bearings (all four corners alike) ---
SHAFT_D = 15.875     # 5/8 in keyed shafting (the sprockets' bore)
# SBSFL202-10 2-bolt stamped-steel flange unit (Surplus Center 600174): 3.189 x
# 2.3125 x 0.875 in, 2-1/2 in bolt centres, 1/4 in bolts, 7/8 in through the
# insert. Its rear dome sits in a 49 mm hole in the plate (FYH catalogue).
BRG = dict(L=81.0, W=58.7, J=63.5, T=3.0, OUT=12.6, IN=9.6, DOME_D=47.0, RING_D=24.0, BOLT_D=6.35, HOLE=49.0)
SHAFT_CLEAR = R - HINGE_W - GEAR_R - SHAFT_D / 2     # 6.0: gear past a corner shaft

# --- StepperOnline 34HS59-6004D-E1000 (NEMA 34, 12 N*m, 1000-line encoder) ---
M34_FLANGE = 86.0
M34_BOLT_SQ = 69.58
M34_HOLE_D = 5.5
M34_PILOT_D = 73.0
M34_PILOT_H = 1.6
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
LC_L = 80.0
VIAL_DROP = 30.0             # outlet to funnel mouth, world vertical
FUNNEL = dict(top_d=36.0, spout_d=18.0, h=22.0)
