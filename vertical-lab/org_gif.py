"""The org page's GIF, remade in the lab as this branch has it: ``vertical-cloud-lab/.github``'s
``profile/vertical-lab.gif`` ("In a vertical lab, equipment is brought to the operator", PR #318).

Round 8 (PR #329, Sterling, 2026-11-08: "The fork stand looks unstable, just free hanging. Also, is the charge cup
stable when on the fork? Seems like you could have a more clever design for this, not necessarily more complex, but
more robust for sure"):
- the cup stands in a slotted sleeve on the fork (SLEEVE_*), not inside a 2.5 mm lip. The sleeve's 13 mm slot, which
  lets the pedestal's neck through, is narrower than the 19.05 mm cup, so the sleeve holds the cup on every side;
  it can lean only about 4 deg, and to tip it would first have to lift out. To back out from under it at the pedestal,
  the fork drops until the sleeve is under the cup's foot (FORK_UNDER), round a longer neck (PED_H_HIGH);
- the fork's rest stands on the tray at two points, a saddle under the sleeve and a channel under the blade by the
  handle, on two 40 x 40 uprights, a beam and a plate bolted to the tray (fork_meshes). Round 6's was one post under
  the fork's middle;
- the doser stands DOSER_BACK further back on tray B (doser_back), so that the fork and its rest are inside the
  tray's lip; round 6's fork overhung it by 72 mm.

Round 7 (PR #329, Sterling, 2026-11-08: "the repowder is getting even more ridiculous. You need to do a thorough look
back at the training videos, specs, etc."): the rePowder redrawn from the footage (``repowder/model.py``, LID_AZ).
Round 6's own question ("maybe just rotated 90 degrees?") was the answer: PR #327 had turned the lid's whole assembly
90 deg. The hinge is on the furnace's left side (T4 6:05) and the lid swings up to the left, standing outside the
cabinet when open (T1 0:03, 44:00; 2wMgeI-E7zw 10:00); turned back, the latch is on the furnace's right with its
bolt running back into the cabinet (T4 5:16), and the lid's square part is at the back. The cabinet is one plain box
behind the chamber and the furnace again, the panel, the red lamp and the main switch on its flat front face, as in
Blue Power's AUS 500 brochure (round 6's block beside the furnace and its bay for the lid are gone). The window is a
square plate with eight screws on the front-left facet. The arm's moves at the rePowder follow the new latch and lid:
the arm reaches over the furnace to the latch on its right, and lifts the lid by its knob up and over to the left; the
lid now turns about the hand's own axis (the hinge runs front to back), so the hand comes to the open lid's knob along
that axis, from the front.

Round 6 (PR #329, Sterling, 2026-11-07: "the atomizer melting furnace area seems to be misproportioned (maybe just
rotated 90 degrees?). The opening lid ends up intersecting with the furnace behind it ... Instead of having a separate
motion thing going on for getting the crucibles to the right spot, instead the arm should use some kind of gripper
attachment to get it in then, unless the gripper could actually reach in with enough clearance, which would be ideal"):
- (replaced in round 7) the rePowder's cabinet had been cut down behind the furnace into a bay for a lid hinged at the
  back, with a block beside the furnace for the panel. With it came PR #327's second pass (the door hinged at the
  back, the front clamps, the viewport, the panel's keys), which stays;
- the doser's vessel shuttle is left out: the arm carries the cup in on a cup fork (FORK_L ..., fork_meshes), since the
  2F-85 itself can't reach the pedestal (its knuckles span 127-138 mm; the way in, between the doser's frame post and
  its station post, is 117 mm). The fork waits on a rest outside the -y panel, its seat where the shuttle took the cup;
  the arm stands the cup on it, takes the fork by its handle, carries the cup in over the balance and lets it down onto
  the pedestal, takes the fork back out while the doser doses, and back in to take the cup off again.

Round 5 (PR #329, Sterling, 2026-11-07: "it wasn't zoomed out enough for the multi-doser to see it was using
multiple powders. Also, that's a really high distance between the cup and the nozzle. Put the cup on some kind of
pedestal so that it's much closer. Also, show the trays being loaded with some equipment before bringing the arm in to
do some workflows"), on round 4's ("you should have started backed off to see the full overview and then zoomed in
...", the arm at the atomizer, a charge cup dosed and taken there). One Shuttle, loaded as the set-up loads it
(``animate.lab_scene``, Shuttle 1's trays A-F and J), no pallet racking, no second Shuttle and none of its trays
(round 2). One loop, which ends where it starts:

1. the whole lab, wide: the Shuttle, the rePowder atomizer, the sieving cell, the MiR250 + UR10e waiting beside the
   opening (WAIT_AT). Trays A and B are empty (LOADED). The camera closes in on the opening, and the two trays are
   loaded there as the set-up movie loads them (``setup_lab.rig_in``, a time-lapse): each comes down, its
   instruments, its UPS and its camera posts come in through the opening onto it (Load), and tray A goes back up.
   Tray B stays;
2. only then does the MiR come in and dock at the opening;
3. at tray B (chapter 1's tray, ``alloy_charge.Charge``: the charge rack, the vacuum press, the multi-doser v5 on its
   HR-202i), the arm takes an empty 5N Al charge cup out of the rack and stands it on the fork of the doser's vessel
   shuttle. The camera pulls back to take in the doser's chain of 13 powder modules: the four that hold a powder in
   chapter 1 drawn in their powders' colours, two of them labelled as they ride it (Modules). For each powder, Si
   (3.92 g, 26.8 mm up the bore) and then the AlSi10Mg top-up (3.91 g, to 46.1 mm): the chain brings the module to the
   station, the electronics carriage docks and tilts it, and only then does the arm carry the cup in over the balance
   on its cup fork (round 6; round 5 had the doser's shuttle do it) and let it down onto a tall pedestal (HIGH_SEAT),
   its rim 34 mm under the auger's exit; the camera goes in to it (CUP_OFF), the doser doses it by weight, and the fork
   takes it back out so that the carriage can park for the next index. The cup is drawn cut open while it fills. The
   arm puts the fork back on its rest and stands the cup in a pocket of the cup carrier on the MiR's cabinet
   (chapter 2's carrier);
4. tray B goes back up while the MiR drives to the rePowder (PR #327's refined model, its lid turned back to its left
   hinge in round 7: the draw latch and the pneumatic locking bolt as joints, ``repowder/model.py``);
5. at the rePowder, the bolt goes back, the arm pulls the latch's lever out (LATCH_U of its swing) and lifts the lid
   by its knob past its balance point (LID_LET) and lets go: the lid settles onto its stop (RP_LID_U). With chapter
   2's loading tong it takes the cup off the carrier and carries it down #222's path into the crucible
   (``alloy_atomize.tong_path``: tipped 4.1 deg past the sealing rod's adapter, then upright onto the floor cone), puts
   the tong back, takes the knob where the lid rests, lowers the lid, shuts the latch, and the bolt goes in;
6. the rePowder, cut open, melts the cup and atomizes it (a time-lapse, ``Melt``: the coil, the cup glowing and
   slumping into the pool, the sealing rod up, the stream onto the vibrating plate, droplets, the powder in the
   container), while the MiR drives off to where it waited; the camera pulls back out to the wide view, and trays A
   and B's equipment fades out of their slots.

The last frame is the first one again: the MiR beside the opening with its arm parked, trays A and B empty in their
slots, the rePowder shut and cold (powder in its container, too small to see from there). The GIF plays everything at
SPEED x the modelled times and says so; the loading and the atomizer's run, half an hour or so, are compressed much
further, and their captions say so.

Drawn differently for this shot only (all drawing choices):
- Shuttle 2 is left out with its trays, the pallet racking and the second MiR unit (round 2); the south row's floor
  machines and its overhead utilities too (SOUTH_OUT, Y_CUT), since the wide view looks across where they stand.
- The VLM's camera target stands at the opening's right instead of its left (TARGET_DX, round 2): coming from the
  rePowder, a unit drives in from the left. The targets the MiR's drive to the rePowder would run over (the sieving
  cell's and the rePowder's) are left out, and so are the south row's, in the wide view's foreground (floor_edits).
- The doser's pedestal, its vessel shuttle and the port in its -y panel are ours (``carousel.py``), and for this shot
  they are drawn as a proposal, not as chapter 1 has them (HIGH_SEAT, high_pedestal; round 6: no shuttle, the arm's
  cup fork and its rest instead, add_fork). In v5 the cup's rim stands
  153 mm under the auger's exit: the electronics carriage parks 35 mm over the balance's top, so a cup carried in
  through the side door can stand no higher. Once the carriage has docked and tilted the module, it has swung clear:
  a sweep of the fork's path over the balance then meets only the -y acrylic panel, so the port there goes up to
  420 mm, the pedestal stands up through the balance's top door (open throughout), and the cup comes in over the
  balance instead of through its side door. The cup leaves between powders, so the carriage can park to index.
- One cup goes into the crucible, where the lab loads four a run (byu-vcl PR #318), and the melt is drawn for one
  cup's 43 g. Its plug isn't fitted or pressed (chapter 1 does both, on the same tray); the cup goes over open.
- The lid rests open at RP_LID_U of the model's 105 deg, 90 deg, standing up at the furnace's left (round 4 chose it
  so the arm could reach the knob to shut the lid). The arm lets go at 73.5 deg, past the lid's balance point (its
  centre of mass passes over the hinge at about 67 deg, from the shell's outline; the turn of round 7 moves the lid
  and its hinge together, so that is unchanged).
- The arm works the latch and the lid on its own (chapter 2 has a second unit hold the lid down while the latch lets
  go).

    VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py views    # the views, as stills -> /tmp/org_gif_views.png
    ORG_STRIDE=24 VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py   # every 24th frame only -> /tmp/org_stride/ (5 min)
    ARM_AUDIT=1 VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py # no render: every frame's arm checked -> out/collisions/
    VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py          # -> out/mp4/<NAME>.mp4, out/<NAME>.json
    ORG_PART=a:b ORG_NAME=<NAME>_p0 ...                  # render frames a..b-1 only (the rest are counted, not drawn)
    python3 org_gif.py join <NAME>_p0 <NAME>_p1 ...      # the parts -> out/mp4/<NAME>.mp4, out/<NAME>.json
    ORG_AUDIT_PART=a:b ARM_AUDIT=1 ...                   # audit frames a..b-1 -> /tmp/org_audit/<a>.json
    ARM_AUDIT_RENDER=1 ORG_PART=a:b ORG_NAME=<NAME>_p0 ...   # render frames a..b-1 and audit them in the same pass
    ORG_AT_OPEN=1 ORG_VIEWS=dose,cup ... org_gif.py views    # tray B at the opening, the doser docked, the cup dosing
    python3 org_gif.py audit_join                        # the audited parts -> out/collisions/<NAME>.json
    python3 org_gif.py gif                               # -> out/<NAME>.gif (SPEED x), its still, mp4/<NAME>_readme.mp4
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np

NAME = os.environ.get("ORG_NAME", "org_vertical_lab")   # another name renders beside a running pass, without clashing
TITLE = "In a vertical lab, equipment is brought to the operator"
SPEED = 1.5          # the GIF plays the clip at this many times its modelled speed, and says so (12 fps x 1.5: 18 fps,
                     # frame delays of 6 and 5 cs in turn)
GIF_W = int(os.environ.get("ORG_GIF_W", "880"))   # px; the org README shows it about 830 px wide. Round 3's 1280
                     # px gave 37 MB for the first half of round 4's loop alone; 1024 px about two thirds of that.
                     # Round 5's loop: 52.7 MB at 1024 px, 47.5 MB at 960. Round 6's (1815 frames): 55.8 MB at 960,
                     # 51.0 at 900, 49.1 at 880
TEXT = 1.45          # the overlay's text, against the scenes' 720p sizes: the README shows the GIF at about 0.65x
S1_TRAYS = "ABCDEFJ"     # Shuttle 1's trays (setup_lab.TRAYS): the only ones loaded


def _cam(f, az, el, d, va):
    """A view: the camera `d` mm from focal point `f`, `az` degrees right of straight on (from -y) and `el` up."""
    a, e = math.radians(az), math.radians(el)
    return [(f[0] + d * math.sin(a) * math.cos(e), f[1] - d * math.cos(a) * math.cos(e), f[2] + d * math.sin(e)),
            tuple(f), (0, 0, 1), va]


RP_AT = (-3775.0, -1700.0)       # animate.REPOWDER_AT: the rePowder model's origin, the furnace axis on the floor
# the views: camera position, focal point, up (mm; Shuttle 1's centre at the origin, its opening facing -y), view angle
CAMS = {
    "wide": _cam((-1500.0, -1000.0, 1350.0), 2.0, 17.0, 11500.0, 34.0),    # the Shuttle, the rePowder, the cell
    "trayB": _cam((-60.0, -1400.0, 950.0), -22.0, 32.0, 2500.0, 30.0),     # tray B at the opening, from the left
    "load": _cam((150.0, -2050.0, 950.0), 24.0, 20.0, 5600.0, 34.0),       # the opening and the floor in front of it
    "dose": None,                     # the doser's pan from the front right, set once tray B is at the opening
    "rp": _cam((RP_AT[0] - 40.0, RP_AT[1] - 420.0, 1200.0), 38.0, 18.0, 3100.0, 27.0),   # the arm at the rePowder
    "bore": _cam((RP_AT[0] + 0.0, RP_AT[1] - 20.0, 1300.0), 35.0, 55.0, 950.0, 27.0),    # down into the crucible
    "cut": _cam((RP_AT[0] + 60.0, RP_AT[1] + 0.0, 980.0), 18.0, 8.0, 2000.0, 27.0),      # the rePowder cut open
}
CAM = "wide"
# The camera stands behind the south row (its fronts at y = -6238), so the row's overhead utilities (its cable tray at
# 3.2 m with its network cable, hangers, drops and junction boxes, the DED's argon run, the fume hood's duct;
# setup_lab.utilities) and its floor machines (SOUTH_OUT) would stand between it and Shuttle 1. For this shot they are
# left out: every utility cell south of Y_CUT, and every FLOOR_PLAN station in row "S". The north row's stay.
Y_CUT = -4000.0
SOUTH_OUT = bool(int(os.environ.get("ORG_SOUTH_OUT", "1")))
TARGET_DX = 2 * 1330.0           # the VLM's camera target, from x = -1330 (setup_lab.TARGET_AT) to +1330
# the cycle
CUP = 3                          # tray B's rack seat of the cup the run takes: the fourth 5N Al cup (alloy_charge.SLOTS)
CUP_AT = 0                       # its place in the crucible: alloy_atomize.CUP_ANGLES[0], 145 deg, at the back, clear
                                 # of the sealing-rod lever (which lies along +x)
CARRIER_K = 0                    # the carrier pocket it rides in
GRASP_DOWN = 48.0                # a cup taken from above, the pads' centre 48 mm up it (its top 63.5 mm up)
OPEN_CUP = 0.66                  # alloy_charge.OPEN_CUP: 31.6 mm between the pads, clear of the next cup in the rack
GRIP_CUP = 0.80                  # on the 19.05 mm cup (ur_arm.gripper_fk: gap = 28 - 90 (c - 0.70))
RP_STOP = (RP_AT[0] - 120.0, -2380.0)   # the MiR at the rePowder, heading 0: from here the arm follows the latch's
                                 # lever and the lid's knob (an IK sweep of MiR stops, 2026-11-06)
WAIT_AT = (-1700.0, -2380.0)     # where the MiR waits at the loop's start and end, heading 0: in front of the sieving
                                 # cell, left of the trays' load coming in through the opening (x > -700), on the line
                                 # it leaves the rePowder by, and out of the cutaway's view of the melt
RP_LID_U = 0.86                  # the lid rests open at this share of the model's 105 deg (90 deg): further, the knob
                                 # leaves the arm's reach from RP_STOP, and the arm couldn't take it to shut the lid
LID_LET = 0.70                   # the arm lifts the lid this far (73.5 deg) and lets go: past its balance point (its
                                 # centre of mass passes over the hinge at about 67 deg), it settles onto its stop
LATCH_U = 0.5                    # the latch's lever swings out this share of its 95 deg: the loop is well off the keeper
LATCH_AT = (24.0, 0.85, 45.0)    # its grasp: the pads' centre 24 mm out from the furnace's face, 0.85 of the lever up
                                 # from its pivot, the tool tipped 45 deg down from level (fingers on the two flanges)
GRIP_LATCH, OPEN_LATCH = 0.59, 0.45   # the lever's 38 mm channel; 50 mm open
GRIP_KNOB = 0.70                 # the lid's 28 mm ball knob
KNOB_OUT = 4.0                   # the knob taken level from the front, the pads' centre 4 mm in front of the ball's
MOD_LBL = (("Si", (0.02, 0.18)), ("AlSi10Mg", (0.985, 0.18)))   # the two modules labelled, and their boxes
DOSE_OFF = (150.0, -1100.0, 320.0)   # the doser's view: the camera this far from the cup's foot on the pedestal
DOSE_LOOK = (40.0, -60.0, 210.0)     # (world), looking at this point from it: the chain's front run, the station under
DOSE_VA = 37.0                       # it, and the cup, through the 117 mm between the frame's front post and the
#                                      station's post
CUP_OFF, CUP_LOOK, CUP_VA = (35.0, -380.0, 75.0), (0.0, 0.0, 62.0), 30.0   # the cup under the auger's exit, close
FORK_OFF, FORK_LOOK, FORK_VA = (450.0, -750.0, 600.0), (0.0, -250.0, 60.0), 35.0   # round 6: the fork's way in, from
#                                    the front right and above: the arm, the fork, the balance's glass and the chain
CHAIN_AT = (130.0, -140.0, 300.0)    # the chain's label's anchor, from the cup's foot: on its front run


def cut_face() -> float:
    """The turn (deg, about z) that faces a cup's cut (charge.cup(cut=True) keeps its +y half) to the close view."""
    return math.degrees(math.atan2(CUP_OFF[0], -CUP_OFF[1]))
ARM_S = (1.6, 0.9, 0.5, 0.8)     # a pick or a place: joint move, line in, grip, line out (s): the 9:09 clip's
                                 # (animate.pick/place)
HOLD = 0.1
DOSE_F = 0.6                     # the doser's moves at this share of chapter 1's times (its first cup is shown at 0.55)
MIR_V = 1500.0                   # mm/s at most, with the MiR250's 0.3 m/s^2 ramps (props.ramp_secs)
ATOM_SECS = 14.0                 # the atomizer's run, half an hour or so, in this many seconds of the clip (a time-lapse)
# round 5
LOADED = "AB"                    # the trays loaded at the opening at the loop's start (empty in their slots before)
LOAD_F = 0.4                     # their tray moves at this share of the modelled times (a time-lapse, as the set-up's)
LOAD_SECS = 3.2                  # each tray's equipment coming in through the opening, one piece after another
LOAD_OVER = 0.5                  # each piece over this share of LOAD_SECS (setup_lab.stagger's overlap)
LOAD_TRAVEL = 1700.0             # mm in front of the opening it comes from (setup_lab.rig_in)
HIGH_SEAT = 338.0                # the cup's foot on the tall pedestal, rig frame (v5's 219): its rim at 401.5 mm, 34 mm
                                 # under the auger's exit at 435.9 (153 mm in v5). The parked electronics carriage
                                 # comes down to 344.8 mm within 25 mm of the pan's axis: the pedestal's top clears it
HIGH_PORT = (0.0, 67.0, 100.0, 420.0)   # the -y panel's port (x0, x1, z0, z1; v5's ours: z up to 300), for the fork,
                                 # the cup on it (up to 409.5 mm, carried) and the fork's column
# round 6 (Sterling, PR #329, 2026-11-07: "Instead of having a separate motion thing going on for getting the crucibles
# to the right spot, instead the arm should use some kind of gripper attachment to get it in then, unless the gripper
# could actually reach in with enough clearance, which would be ideal"). The gripper can't: the 2F-85's knuckles span
# 127-138 mm, and the way in passes between the doser's frame post and its station post, 117 mm apart (carousel.py).
# So the vessel shuttle is left out, and the arm carries the cup in on a cup fork (ours, assumed design): the shuttle's
# fork made a hand tool, its blade long enough that the gripper stays outside the -y panel, on a handle post that the
# pads clamp (19 mm across, as the loading tong's handle). It waits on a rest outside the panel, its seat where the
# shuttle took the cup from the arm (carousel.Y_HAND), so the arm's place and pick of the cup there are round 5's.
FORK_L = 285.0          # the fork, back end to tip: with the cup on the pedestal, the handle stands 41 mm off the panel
FORK_HANDLE_H = 120.0   # the handle post's top, over the seat
FORK_HANDLE = (19.0, 24.0)   # the post's section (x, across which the pads clamp; y)
FORK_GRASP = 18.0       # the pads' centre, under the post's top
FORK_LIFT = 2.0         # the fork comes up this far off its rest
FORK_BACK = 30.0        # it backs out this far under the cup before it rises or drops clear of the cup's foot
FORK_GAP = 0.2          # the cup is let onto the pedestal, and taken back, this far over it (no contact while held)
GRIP_FORK, OPEN_FORK = 0.80, 0.62
# round 8 (Sterling, PR #329, 2026-11-08: "The fork stand looks unstable, just free hanging. Also, is the charge cup
# stable when on the fork? Seems like you could have a more clever design for this, not necessarily more complex, but
# more robust for sure"). Round 6's cup stood inside a 2.5 mm lip with 0.5 mm of play, and the fork lay across one
# 20 mm post, 334 mm tall, at its middle, its handle overhanging tray B's front lip by 72 mm. Now:
# - the cup stands in a slotted sleeve. The slot that lets the pedestal's neck through (carousel.SLOT_W, 13 mm) is
#   narrower than the 19.05 mm cup, so the sleeve holds the cup on every side; it can lean only about 4 deg (0.95 mm
#   of play over the bore's 14.5 mm under its chamfer), and to tip it would first have to lift out. At the pedestal the fork drops until the sleeve is under the cup's foot (FORK_UNDER), round a
#   longer neck (PED_H_HIGH), and backs out along the slot as round 6's did. The blade joins the sleeve part way up
#   (BLADE_Z), so that, dropped, it still clears the balance's top;
# - the rest stands on the tray at two points, a saddle under the sleeve and a channel under the blade by the handle,
#   both open toward the doser so the fork slides out of them, on two 40 x 40 uprights, a beam and a plate bolted to
#   the tray (REST_*);
# - the doser stands DOSER_BACK further back on tray B than the lab's plan has it (animate.LOADS), so that the fork
#   and its rest are inside the tray's lip. The lip's inner face was 470 mm in front of the doser's origin and the
#   resting fork's back end 542 mm; now the fork ends 13 mm inside it. Its seat stays at the hand-over (CR.Y_HAND,
#   71 mm outside the -y panel), so the arm's place and pick of the cup there are round 5's.
SLEEVE_H = 16.0         # the sleeve round the cup's foot, over the seat: a quarter of the cup's 63.5 mm. The pads
#                         (the cup held 48 mm up, GRASP_DOWN) end 29 mm up it, 13 mm over the sleeve
SLEEVE_R = (10.0, 13.5)  # its bore (the cup's 19.05 mm, with 0.95 mm of play) and its outside
SLEEVE_CH = 1.5         # the lead-in chamfer round the bore's mouth
SLEEVE_FLOOR = 4.0      # the floor under the cup's foot; the slot runs through it and the sleeve from the seat's centre
BLADE_Z = (7.0, 13.0)   # the blade, over the seat: with the sleeve dropped under the cup's foot it is 9 mm over the
#                         balance's top (316 mm)
BLADE_W = 24.0
FORK_UNDER = SLEEVE_H + 4.0   # the seat this far under the cup's foot, for the fork to back out from under it
PED_H_HIGH = 34.0       # the pedestal's neck (carousel.PED_H: 20 mm): the sleeve's floor drops to 10 mm over the riser
DOSER_BACK = 85.0       # the doser this much further back on tray B (animate.LOADS: y 50); its back stays 28 mm in
#                         front of the tray's power strip
REST_BACK = -496.0      # the rest's channel and rear upright, rig frame (y; the saddle and front upright at CR.Y_HAND)


def _load_s1() -> dict:
    """setup_lab.load_all without fab_tour's models: they are trays G-I's, all on Shuttle 2."""
    import setup_lab as SL
    idata = SL.tour_load_safe()
    idata.update(SL.load_r7())
    idata.update(SL.r7_stand_ins(idata))
    return idata


def high_pedestal():
    """The doser's pedestal, vessel shuttle and panel port as this shot draws them (HIGH_SEAT, HIGH_PORT): carousel.py
    reads SEAT_Z and PORT when it draws them and places the vessel, so setting them before the scene is built moves the
    pedestal's neck, the fork's top, the hand-over and the pan's seat together. The panel comes from carousel.py's
    cache with v5's port already cut, and gets the taller one cut over it."""
    import carousel as CR
    if getattr(CR, "_org_high", False):
        return
    CR._org_high = True
    CR.SEAT_Z = HIGH_SEAT
    CR.PORT = HIGH_PORT
    CR.PED_H = PED_H_HIGH                                  # round 8: for the cup fork's sleeve to drop clear round it
    meshes = CR.part_meshes

    def part_meshes():
        out = dict(meshes())
        out["panel_side"] = CR._cut_port(out["panel_side"])
        return out
    CR.part_meshes = part_meshes


def doser_back():
    """Round 8: the doser stands DOSER_BACK further back on tray B (animate.LOADS), so that its cup fork and the fork's
    rest are inside the tray's lip. Set before the scene is built; once."""
    import animate as A
    if getattr(A, "_org_back", False):
        return
    A._org_back = True
    A.LOADS["B"] = [(k, x, y + DOSER_BACK) if k == "carousel" else (k, x, y) for k, x, y in A.LOADS["B"]]


def fork_meshes() -> dict:
    """The cup fork and its rest: {name: (mesh, colour, group)}. The fork in its own frame (origin the seat's centre,
    where the cup's foot stands; y along the blade to its tip; z up), group "cupfork": the slotted sleeve round the
    cup's foot (SLEEVE_*), the blade joining it part way up (BLADE_Z), the handle post and its cap. The rest in the
    rig's frame, group None (the caller puts it in the rig's group): a saddle under the sleeve, open toward the doser,
    and a channel under the blade by the handle, open at both ends, on two 40 x 40 uprights joined by a beam, on a
    plate bolted to the tray (round 8)."""
    import cadquery as cq

    import carousel as CR
    import lab

    def mesh(wp):
        m = lab.to_mesh(wp.val(), 0.05, 0.2).clean()
        m.clear_data()                   # merged parts carry face normals of the wrong length (collide.py warns)
        return m

    def blk(x0, x1, y0, y1, z0, z1):
        return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

    r0, r1 = SLEEVE_R
    sw = CR.SLOT_W / 2
    yb = -(FORK_L - 15.0)                                  # the fork's back end
    hx, hy = FORK_HANDLE[0] / 2, FORK_HANDLE[1]
    # the sleeve and its floor; the bore's mouth chamfered; the slot through both, from round the seat's centre (where
    # the pedestal's neck stands) out through the front
    sleeve = (cq.Workplane("XY").workplane(offset=-SLEEVE_FLOOR).circle(r1).extrude(SLEEVE_FLOOR + SLEEVE_H)
              .faces(">Z").workplane().hole(2 * r0, SLEEVE_H))
    sleeve = sleeve.faces(">Z").edges(cq.selectors.RadiusNthSelector(0)).chamfer(SLEEVE_CH)
    zc0, zc1 = -SLEEVE_FLOOR - 1.0, SLEEVE_H + 1.0
    slot = blk(-sw, sw, 0.0, r1 + 2.0, zc0, zc1).union(
        cq.Workplane("XY").workplane(offset=zc0).circle(sw).extrude(zc1 - zc0))
    sleeve = sleeve.cut(slot)
    blade = blk(-BLADE_W / 2, BLADE_W / 2, yb, -r1 + 2.0, *BLADE_Z)
    post = blk(-hx, hx, yb, yb + hy, BLADE_Z[0], FORK_HANDLE_H)
    web = blk(-4.0, 4.0, yb + hy - 1.0, yb + hy + 45.0, BLADE_Z[1] - 1.0, BLADE_Z[1] + 26.0)
    fork = sleeve.union(blade).union(post).union(web)
    cap = blk(-12.0, 12.0, yb - 2.0, yb + hy + 2.0, FORK_HANDLE_H, FORK_HANDLE_H + 8.0)
    # the rest, rig frame
    x, yh = float(CR.PAN_XY[0]), float(CR.Y_HAND)
    zr = CR.SEAT_Z + CR.SEAT_LIFT                          # the seat, resting
    zs, zb = zr - SLEEVE_FLOOR, zr + BLADE_Z[0]           # the saddle's floor (the sleeve's underside), the channel's
    yr = REST_BACK
    rs = r1 + 0.5                                          # the saddle's pocket round the sleeve
    saddle = blk(x - 22.0, x + 22.0, yh - 22.0, yh + 18.0, zs - 12.0, zs + 6.0).cut(
        cq.Workplane("XY").workplane(offset=zs).center(x, yh).circle(rs).extrude(10.0)).cut(
        blk(x - rs, x + rs, yh, yh + 30.0, zs, zs + 10.0))
    channel = blk(x - 22.0, x + 22.0, yr - 14.0, yr + 14.0, zb - 12.0, zb + 6.0).cut(
        blk(x - BLADE_W / 2 - 1.0, x + BLADE_W / 2 + 1.0, yr - 20.0, yr + 20.0, zb, zb + 10.0))

    def upright(yc, ztop):
        """A 40 x 40 extrusion, a groove down each face, from the plate up to ztop."""
        prof = cq.Workplane("XY").workplane(offset=10.0).center(x, yc).rect(40.0, 40.0).extrude(ztop - 10.0)
        for dx, dy, gx, gy in ((20, 0, 4, 8), (-20, 0, 4, 8), (0, 20, 8, 4), (0, -20, 8, 4)):
            prof = prof.cut(blk(x + dx - gx / 2, x + dx + gx / 2, yc + dy - gy / 2, yc + dy + gy / 2, 10.0, ztop))
        return prof

    zt = zs - 12.0                                         # the front upright's top (the rear's: zb - 12)
    frame = upright(yh, zt).union(upright(yr, zb - 12.0)).union(
        blk(x - 10.0, x + 10.0, yr + 20.0, yh - 20.0, zt - 60.0, zt - 20.0))      # the beam between them
    yp0, yp1 = yr - 36.0, yh + 30.0
    frame = frame.union(blk(x - 50.0, x + 50.0, yp0, yp1, 0.0, 10.0))          # the plate on the tray
    for yc in (yh, yr):                                    # gussets at each upright's foot, across the plate
        for sx in (-1, 1):
            g = (cq.Workplane("XZ").polyline([(x + sx * 20.0, 10.0), (x + sx * 46.0, 10.0), (x + sx * 20.0, 70.0)])
                 .close().extrude(3.0).translate((0.0, yc + 1.5, 0.0)))
            frame = frame.union(g)
    bolts = None
    for bx in (-38.0, 38.0):                               # bolted to the tray's floor
        for by in (yp0 + 12.0, (yp0 + yp1) / 2, yp1 - 12.0):
            b = cq.Workplane("XY").workplane(offset=10.0).center(x + bx, by).polygon(6, 13.0).extrude(5.0)
            bolts = b if bolts is None else bolts.union(b)
    steel, dark, alu = (0.66, 0.68, 0.71), (0.20, 0.21, 0.24), (0.74, 0.76, 0.79)
    return {"cupfork/blade": (mesh(fork), steel, "cupfork"),
            "cupfork/handle": (mesh(cap), dark, "cupfork"),
            "cupfork/rest": (mesh(frame), alu, None),
            "cupfork/rest_pads": (mesh(saddle.union(channel)), dark, None),
            "cupfork/rest_bolts": (mesh(bolts), dark, None)}


def fork_grasp_local() -> np.ndarray:
    """The 2F-85's grasp of the fork's handle, in the fork's frame: pointing down the post, the pads across its x."""
    G = np.eye(4)
    G[:3, 0], G[:3, 1], G[:3, 2] = (1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)
    G[:3, 3] = (0.0, -(FORK_L - 15.0) + FORK_HANDLE[1] / 2, FORK_HANDLE_H - FORK_GRASP)
    return G


def add_fork(sc, K):
    """The cup fork on its rest, riding the doser's rig (so tray B's load brings it in with the doser); the vessel
    shuttle (its rail, carriage, column and fork) left out: hidden, it is out of the audit's world too."""
    import carousel as CR
    from scene import T
    for nm, (mesh, col, grp) in fork_meshes().items():
        sc.add(nm, mesh, col, grp or K.rig, specular=0.5)
    sc.parent["cupfork"] = K.rig
    sc.gmat["cupfork"] = T((float(CR.PAN_XY[0]), CR.Y_HAND, CR.SEAT_Z + CR.SEAT_LIFT))
    for nm in list(sc.actors):
        if "ours_shuttle" in nm:
            sc.alpha[nm] = 0.0
            sc.base_alpha[nm] = 0.0


class Load:
    """Tray k's equipment: every group riding on it (its instruments, its UPS and dock plate, its camera posts), as
    the set-up movie loads a tray (setup_lab.rig_in, stagger). Unloaded (hidden) when made; slide(u) brings it in
    through the opening onto the tray, one piece after another from the left; fade_out() is an update that fades
    whatever rides on the tray then (the cup the run took is in the crucible by then) out of it."""

    def __init__(self, sc, k):
        self.sc, self.k = sc, k
        tg = f"tray_{k}"
        kids = [g for g, p in sc.parent.items() if p == tg]
        self.names = {g: self._names(g) for g in kids}
        self.kids = [g for g in kids if self.names[g]]
        self.kids.sort(key=lambda g: (g.startswith(("ups", "plate", "cam")) or "ups" in g or "cam" in g,
                                      float(sc.gmat[g][0, 3])))
        self.base = {g: sc.gmat[g].copy() for g in self.kids}
        self.a0 = {n: sc.alpha[n] for g in self.kids for n in self.names[g]}
        for n in self.a0:
            sc.alpha[n] = 0.0

    def _names(self, g):
        sc = self.sc
        desc, grew = {g}, True
        while grew:
            grew = False
            for h, p in sc.parent.items():
                if p in desc and h not in desc:
                    desc.add(h)
                    grew = True
        return [n for n, gg in sc.group_of.items() if gg in desc]

    def slide(self, u):
        from scene import T, window
        sc, n = self.sc, len(self.kids)
        for i, g in enumerate(self.kids):
            t0 = 0.0 if n == 1 else i * (1.0 - LOAD_OVER) / (n - 1)
            v = 1.0 - window(u, t0, t0 + (LOAD_OVER if n > 1 else 1.0))
            sc.gmat[g] = T((0, -LOAD_TRAVEL * v, min(1.0, v * 6) * 20.0)) @ self.base[g]
            a = 1.0 if v < 0.7 else max(0.0, 1 - (v - 0.7) / 0.3)
            for nm in self.names[g]:
                sc.alpha[nm] = self.a0[nm] * a

    def fade_out(self):
        sc = self.sc
        tg = f"tray_{self.k}"
        now = {n: sc.alpha[n] for g in [h for h, p in sc.parent.items() if p == tg] for n in self._names(g)}

        def up(u):
            for n, a in now.items():
                sc.alpha[n] = a * (1.0 - u)
        return up


class Modules:
    """The doser's modules that hold a powder in chapter 1 (alloy_charge.MODULE: Si, Ni and the two top-ups), each
    auger drawn in its powder's colour (charge.POWDERS, alloy_press.TOPUP_COL, a shade darker against the white
    augers), so that the chain shows several
    powders; and the anchors of the labelled ones (MOD_LBL) at the middle of their augers. A frame hook: both follow
    their modules round the chain (Carousel._last, the rig frame; the sleeves ride in the rig's group, so they come in
    with tray B's load)."""

    def __init__(self, sc, car):
        import pyvista as pv

        import alloy_charge as AC
        import alloy_press as AP
        import charge as C
        self.sc, self.car = sc, car
        pl = car._pl()
        col = {k: tuple(0.86 * c for c in v) for k, v in {**{k: v[0] for k, v in C.POWDERS.items()},
                                                             **AP.TOPUP_COL}.items()}
        a = car.parts["auger"]
        r = (a.bounds[1] - a.bounds[0]) / 2 + 0.6
        z0, z1 = a.bounds[4], a.bounds[5]
        sleeve = pv.Cylinder(center=(0, 0, z0 + 0.55 * (z1 - z0)), direction=(0, 0, 1), radius=r,
                             height=0.62 * (z1 - z0), resolution=40).triangulate()
        self.idx, self.at = {}, {}
        for pname, m in AC.MODULE.items():
            i = next(j for j, p in enumerate(pl) if p.module == m and p.key == "auger")
            g = f"mdpw_{m}"
            sc.add(f"md powder {pname}", sleeve, col[pname], g, specular=0.15, ambient=0.3)
            sc.parent[g] = car.group
            self.idx[g] = i
        for pname, _ in MOD_LBL:
            i = next(j for j, p in enumerate(pl) if p.module == AC.MODULE[pname] and p.key == "auger")
            self.at[pname] = (i, np.r_[a.center, 1.0], [0.0, 0.0, 0.0])
        self(sc)

    def point(self, pname):
        return self.at[pname][2]

    def __call__(self, sc):
        last = self.car._last
        for g, i in self.idx.items():
            sc.gmat[g] = last[i]
        Mg = sc.world(self.car.group)
        for i, c, anchor in self.at.values():
            anchor[:] = (Mg @ last[i] @ c)[:3]


class Melt:
    """The rePowder's run as a frame hook (Scene.frame_hooks), ATOM_SECS from start(): the furnace and chamber cut open,
    the coil on, the cup glowing and slumping into the pool, the sealing rod up, the stream onto the vibrating plate,
    droplets flying off it and the powder heap rising in the container; then all off, the cut shut. alloy_atomize's
    effects (its port of #124's training animation), under names of their own, sized for one cup."""

    def __init__(self, sc, cup_group):
        import pyvista as pv

        import alloy_atomize as AT
        import charge as C
        from scene import T
        M = AT.M
        self.sc, self.AT, self.M, self.cg = sc, AT, M, cup_group
        v = M.variant_meshes()
        self.pool_levels, self.pool_meshes = v["pool_levels"], v["pool_half"]
        self.pw_levels, self.pw_meshes = v["powder_levels"], v["powder_half"]
        sc.add("rp pool", self.pool_meshes[0][0], AT.MELT, AT.g("crucible"), ambient=0.75, diffuse=0.45, specular=0.5)
        sc.add("rp pool#cut", self.pool_meshes[0][1], AT.lighter(AT.MELT, 0.3), AT.g("crucible"), ambient=0.85,
               diffuse=0.3, specular=0.0, smooth_shading=False)
        col = C.POWDERS["Al"][0]
        sc.add("rp powder", self.pw_meshes[0][0], col, AT.g("container"), specular=0.05, ambient=0.3)
        sc.add("rp powder#cut", self.pw_meshes[0][1], AT.lighter(col, 0.25), AT.g("container"), smooth_shading=False,
               ambient=0.6, specular=0.0)
        h = AT.STREAM_TOP - M.IMPACT[2]
        sc.add("rp stream", pv.Cylinder(center=(0, 0, M.IMPACT[2] + h / 2), direction=(0, 0, 1), radius=1.4, height=h,
                                        resolution=16), AT.MELT, "rp_stream", ambient=0.85, diffuse=0.4, shown=False)
        sc.parent["rp_stream"] = "rp"
        self.spray = AT.Particles(sc, "rp spray", (0.40, 0.41, 0.46), size=5.5)
        self.drops = AT.Particles(sc, "rp drops", AT.MELT, size=7.0, slowmo=0.35, seed=2)
        # one cup's metal: the pool and the powder heap at the levels its 43 g makes (alloy_atomize.POOL_LEVEL and
        # POWDER_END are for four)
        m = AT.RUN["charge_g"] / 4
        self.pool_top = AT.level_for(AT.pool_volume, m / AT.AL_LIQUID, -14.0, 37.0)
        self.powder_top = AT.level_for(AT.powder_volume, m * 0.912 / AT.POWDER_BULK, 3.0, 70.0)
        self.n0 = self.n1 = None
        self.cup_names = [n for n, g in sc.group_of.items() if g in (cup_group, f"{cup_group}_pw", f"{cup_group}_pw2")]
        self.cup_col = {n: sc.color.get(n) for n in self.cup_names}
        self.T = T
        self.pool(-30.0)
        self.powder(-1.0)

    def pool(self, level, color=None):
        sc, AT = self.sc, self.AT
        color = color or AT.MELT
        on = level > self.pool_levels[0] - 0.5
        i = int(np.argmin(np.abs(self.pool_levels - level)))
        sc.set_mesh("rp pool", self.pool_meshes[i][0])
        sc.set_mesh("rp pool#cut", self.pool_meshes[i][1])
        for n, c in (("rp pool", color), ("rp pool#cut", AT.lighter(color, 0.3))):
            sc.alpha[n] = 1.0 if on else 0.0
            sc.color[n] = c

    def powder(self, level):
        sc = self.sc
        on = level >= self.pw_levels[0]
        i = int(np.argmin(np.abs(self.pw_levels - level)))
        sc.set_mesh("rp powder", self.pw_meshes[i][0])
        sc.set_mesh("rp powder#cut", self.pw_meshes[i][1])
        sc.alpha["rp powder"] = sc.alpha["rp powder#cut"] = 1.0 if on else 0.0

    def start(self, sc):
        self.n0 = sc.n
        self.seat = sc.gmat[self.cg].copy()

    def __call__(self, sc):
        from scene import FPS, S, window
        if self.n0 is None or (self.n1 is not None and sc.n > self.n1 + 1):
            return
        AT, M = self.AT, self.M
        u = min(1.0, max(0.0, (sc.n - self.n0) / (ATOM_SECS * FPS)))
        AT.set_cut(sc, window(u, 0.0, 0.08) * (1.0 - window(u, 0.92, 1.0)), AT.FUR_G + AT.CH_G)
        heat = window(u, 0.08, 0.30)
        glow = heat * (1.0 - window(u, 0.80, 0.90))
        AT.coil_glow(sc, glow)
        temp = 24.0 + (720.0 - 24.0) * heat
        f = 1.0 - 0.95 * window(u, 0.28, 0.42)              # the cup slumps into the pool
        sc.gmat[self.cg] = self.seat @ S((1 + 0.12 * (1 - f), 1 + 0.12 * (1 - f), f))
        for n in self.cup_names:
            sc.alpha[n] = (sc.alpha[n] if f > 0.07 else 0.0) if u < 0.999 else sc.alpha[n]
            if sc.alpha.get(n, 0.0) > 0.0:
                sc.color[n] = AT.temp_color(temp)
                sc.ambient[n] = 0.18 + 0.55 * max(0.0, min(1.0, (temp - 450) / 400))
        drain = window(u, 0.50, 0.80)
        level = (-14.0 + (self.pool_top + 14.0) * window(u, 0.29, 0.42)) * (1.0 - drain) + (-12.0) * drain
        self.pool(level if 0.29 < u < 0.82 else -30.0)
        AT.rod_lift(sc, 12.0 * window(u, 0.44, 0.50) * (1.0 - window(u, 0.80, 0.86)))
        flow = window(u, 0.48, 0.52) * (1.0 - window(u, 0.78, 0.82))
        sc.alpha["rp stream"] = 1.0 if flow > 0.02 else 0.0
        sc.gmat["rp_stream"] = S((1.0, 1.0, max(flow, 0.01)), (0, 0, AT.STREAM_TOP))
        on = 0.50 < u < 0.82
        sc.gmat[AT.g("connector")] = self.T(M.STACK_DIR * (1.2 if (on and (sc.n * 15 // FPS) % 2) else 0.0))
        if 0.52 < u < 0.80:
            self.spray.emit_spray(int(round(30 * AT.PER_FRAME)))
            if sc.n % max(1, 3 * FPS // 15) == 0:
                self.drops.emit_drops(2, M.IMPACT + np.array([0, 0, 3]), M.PLATE_UP * 250 + M.STACK_DIR * 500)
        if u > 0.88:
            self.spray.clear()
            self.drops.clear()
        else:
            self.spray.step()
            self.drops.step()
        self.powder(-1.0 if u < 0.53 else 3.0 + (self.powder_top - 3.0) * window(u, 0.53, 0.86))
        if u >= 1.0 and self.n1 is None:
            self.n1 = sc.n


def build(data):
    """Shuttle 1 in the lab (animate.lab_scene), stripped (strip, floor_edits, clear_view), with chapter 1's charge on
    tray B (alloy_charge.Charge: the rack of cups and plugs, the vacuum press, the MiR's cup carrier), the rePowder by
    its parts (alloy_atomize.load_rp, PR #327's model), chapter 2's loading tong on the MiR and the melt (Melt); and
    the cycle's start: the MiR beside the opening (WAIT_AT), its arm parked, trays A and B empty in their slots
    (L.loads), the extractor at B's, the doser's tall pedestal (high_pedestal) and its powder modules (L.modules).
    -> (scene, lab, charge, melt)."""
    import alloy_atomize as AT
    import alloy_charge as AC
    import animate as A
    import carousel as CR
    import setup_lab as SL
    import vlm as V
    os.environ.setdefault("VLAB_ONLY_TRAYS", S1_TRAYS)
    SL.load_all = _load_s1
    high_pedestal()
    doser_back()                                       # round 8: the doser further back on tray B, for the fork
    sc, L = A.lab_scene(data, name=NAME, title=TITLE)
    sc.gif = False                                     # gif() makes the GIF from the MP4
    sc.text_scale = TEXT
    L.show_gauges = False
    L.extra_gauges = []
    strip(sc, L)
    floor_edits(sc)
    clear_view(sc, L)
    u = L.units[0]
    u.set((*WAIT_AT, 0.0))                             # waiting beside the opening while the trays are loaded
    # chapter 1's charge on tray B. Its MiR group "amr" rides on this unit's cabinet; the unit's one-vial holder goes
    sc.parent["amr"] = L.amr_group
    sc.gmat["amr"] = np.eye(4)
    for nm in (f"{u.name}/holder",):
        sc.alpha[nm] = 0.0
        sc.base_alpha[nm] = 0.0
    K = AC.Charge(sc, L)
    for nm in ("vial/glass", f"{L.eq_groups['B'][0]}/rack", f"{L.eq_groups['B'][0]}/vials"):
        sc.base_alpha[nm] = 0.0
    sc.parent["stream"] = K.rig
    add_fork(sc, K)                                    # the cup fork on its rest; the vessel shuttle left out (round 6)
    L.powder_h = L.liquid_h = 0.0
    L.set_fill()
    # the rePowder by its parts; the merged copy goes
    for nm in list(sc.actors):
        if nm.startswith("repowder:"):
            sc.alpha[nm] = 0.0
            sc.base_alpha[nm] = 0.0
    AT.load_rp(sc, ghost={"stack_cover": 0.35})
    L.tong_home = AT.add_tong(sc, None)
    fx = Melt(sc, f"cup{CUP}")
    # trays A and B in their slots, the extractor at B's (where the cycle leaves it), the shutter shut
    L.use(1)
    for k in ("A", "B"):
        L.tray[k] = [*V.SLOTS[A.HOME[k]]]
        L.where[k] = A.HOME[k]
    L.lift_z = V.SLOTS[A.HOME["B"]][1]
    L.shutter = 0.0
    L.skin(1.0)(1.0)
    # the doser's top door stays open: the tall pedestal stands up through it (high_pedestal)
    L.carousel.set(top_door=CR.TOP_OPEN)
    L.modules = Modules(sc, L.carousel)
    sc.frame_hooks.insert(0, L.modules)
    L.apply_state()
    L.loads = {k: Load(sc, k) for k in LOADED}       # trays A and B empty until they are loaded at the opening
    return sc, L, K, fx


def strip(sc, L):
    """Leave out Shuttle 2 (its u2_* groups, its bay camera, its trays and everything riding on them), the pallet
    racking and the second unit."""
    import setup_lab as SL
    import vlm as V
    s2 = {f"tray_{k}" for k, (slot, _) in SL.TRAYS.items() if V.SLOT_SHUTTLE.get(slot, 1) == 2}
    other = [u.name for u in L.units[1:]]
    out = set()
    for g in set(sc.group_of.values()):
        h, n = g, 0
        while h is not None and n < 64:
            if h in s2 or h.startswith(("u2_", "baycam2", "baycamrig2")) or h == "racking" or \
                    any(h == o or h.startswith(o + "_") or h.startswith(o + "ur_") for o in other):
                out.add(g)
                break
            h, n = sc.parent.get(h), n + 1
    for nm, g in sc.group_of.items():
        if g in out:
            sc.alpha[nm] = 0.0
            sc.base_alpha[nm] = 0.0


def floor_edits(sc):
    """The floor marks for Shuttle 2 go (its dock tape, its camera target, the tape round its footprint), and the VLM's
    camera target moves from the opening's left to its right (TARGET_DX): the merged meshes warehouse.Floor._tape and
    setup_lab.footprints draw them in, edited in place."""
    import pyvista as pv

    import setup_lab as SL
    import vlm as V
    x2 = V.SHUTTLE_X[2]
    tx, ty = SL.TARGET_AT["vlm"]
    xo, yo = V.UNIT_W / 2 + V.SKIN + 300.0, V.UNIT_D / 2 + V.SKIN + 300.0
    for nm in ("dock tape", "target posts", "target black", "target white", "footprints"):
        if nm not in sc.actors:
            continue
        mesh = pv.wrap(sc.actors[nm].GetMapper().GetInput()).copy()
        c = mesh.cell_centers().points
        if nm == "footprints":            # the tape round Shuttle 2's footprint (setup_lab.footprints)
            keep = np.flatnonzero(~((np.abs(c[:, 0] - x2) < xo) & (np.abs(c[:, 1]) < yo)))
        else:                             # its dock and its camera target; the targets the MiR's drive to the
            #                               rePowder runs over (the cell's and the rePowder's); the south row's
            keep = np.flatnonzero(~(((np.abs(c[:, 0] - x2) < 1900) & (c[:, 1] > -2700) & (c[:, 1] < -1400)) |
                                    (nm != "dock tape") & (((c[:, 0] > -4300) & (c[:, 0] < -400) & (c[:, 1] > -2750) &
                                                            (c[:, 1] < -1800)) | (c[:, 1] < -3500))))
        if len(keep) < mesh.n_cells:
            mesh = mesh.extract_cells(keep).extract_surface(algorithm="dataset_surface")
        p = np.array(mesh.points)
        sel = (np.abs(p[:, 0] - tx) < 200) & (np.abs(p[:, 1] - ty) < 200)
        p[sel, 0] += TARGET_DX
        mesh.points = p
        sc.set_mesh(nm, mesh)


def clear_view(sc, L=None):
    """Leave the south row's overhead utilities out of the shot (Y_CUT), and its floor machines (SOUTH_OUT); and the
    utilities' cells over Shuttle 2's footprint, its cable drops."""
    import pyvista as pv

    import setup_lab as SL
    import vlm as V
    F = getattr(L, "floor", None)
    if SOUTH_OUT and F is not None:
        for key, (_, row, *_r) in SL.FLOOR_PLAN.items():
            if row == "S" or key == "vlm2":
                for nm in F.groups.get(key, []):
                    sc.alpha[nm] = 0.0
    x2, half = V.SHUTTLE_X[2], V.UNIT_W / 2 + V.SKIN
    for nm in [n for n in sc.actors if n.startswith("util/")]:
        mesh = pv.wrap(sc.actors[nm].GetMapper().GetInput())
        if mesh.n_cells == 0:
            continue
        c = mesh.cell_centers().points
        drop = (c[:, 1] <= Y_CUT) | ((np.abs(c[:, 0] - x2) < half) & (c[:, 1] > -V.UNIT_D / 2 - 400) &
                                     (c[:, 2] < 3000.0))
        keep = np.flatnonzero(~drop)
        if len(keep) == mesh.n_cells:
            continue
        if len(keep) == 0:
            sc.alpha[nm] = 0.0
            continue
        sc.set_mesh(nm, mesh.extract_cells(keep).extract_surface(algorithm="dataset_surface"))


def set_cam(sc, key):
    cam = CAMS[key]
    sc.cam = [tuple(float(v) for v in c) for c in cam[:3]]
    sc.view_angle = cam[3] if len(cam) > 3 else 30.0


def views():
    """Stills of the views (ORG_VIEWS=a,b,... picks some), with the scene at the cycle's start; ORG_AT_OPEN=1 has tray
    B at the opening and loaded, the doser's Si module docked and tilted, and the cup on the pedestal, part dosed and
    cut open (the dose view's set-up). ORG_CAMS='key=dx,dy,dz,lx,ly,lz,va;...' adds views relative to the cup's foot."""
    from PIL import Image, ImageDraw

    import alloy_charge as AC
    import carousel as CR
    import lab
    import vlm as V
    import pyvista as pv
    import warehouse as W
    from scene import T, R
    sc, L, K, fx = build(lab.meshes())
    if os.environ.get("ORG_LID"):            # the rePowder's lid open this share of its 105 deg (RP_LID_U: as the arm
        import alloy_atomize as AT           # leaves it)
        sc.gmat[AT.g("hood")] = AT.M.joint_matrix("lid", float(os.environ["ORG_LID"]))
    if os.environ.get("ORG_AT_OPEN"):
        car, cg = L.carousel, f"cup{CUP}"
        for k in LOADED:
            L.loads[k].slide(1.0)
        L.tray["B"] = [*V.SLOTS["open"]]
        L.where["B"] = "open"
        L.apply_state()
        car.set(shift=car.index_to(AC.MODULE["Si"]), ext=CR.DOCK_EXT, tilt=CR.TILT, shuttle=0.0, fork=1.0,
                magnet_on=True)
        sc.parent[cg] = K.rig
        sc.gmat[cg] = T(CR.vessel_at("cup", 0.0, 1.0)) @ R((0, 0, 1), cut_face())
        L.units[0].set(W.dock_pose("vlm"))
        K.powder_h[CUP] = K.powder_h2[CUP] = 15.0
        K._point[CUP] = True
        K.apply()
        K.cut(CUP, True, sleeve=None)
        pts = AC.stream_points(L, K, CUP, 0.3, 1.0)
        sc.set_mesh("stream", pv.PolyData(pts))
        sc.alpha["stream"] = 1.0
        bal = K.bal_cup()
        CAMS["dose"] = [tuple(bal + DOSE_OFF), tuple(bal + DOSE_LOOK), (0, 0, 1), DOSE_VA]
        for item in filter(None, os.environ.get("ORG_CAMS", "").split(";")):
            key, v = item.split("=")
            v = [float(x) for x in v.split(",")]
            CAMS[key] = [tuple(bal + v[0:3]), tuple(bal + v[3:6]), (0, 0, 1), v[6]]
        mods = L.modules
        mods(sc)
        b = np.array([sc.world(car.group) @ np.r_[p, 1.0] for p in
                      np.array(pv.merge([pv.wrap(sc.actors[n].GetMapper().GetInput()) for n in sc.actors
                                         if sc.group_of[n] == car.group]).points)[::50]])[:, :3]
        print(f"cup foot {np.round(bal, 1)}; exit {np.round(sc.world(car.group) @ np.r_[car.exit_point(), 1.0], 1)}; "
              f"doser x {b[:, 0].min():.0f}..{b[:, 0].max():.0f} y {b[:, 1].min():.0f}..{b[:, 1].max():.0f} "
              f"z {b[:, 2].min():.0f}..{b[:, 2].max():.0f}; modules "
              f"{ {p: np.round(mods.point(p), 0).tolist() for p, _ in MOD_LBL} }", flush=True)
        sc.sticky_labels = [(f"the {p} module", mods.point(p), box) for p, box in MOD_LBL] + [
            ("13 powder modules on a chain,\none powder in each", tuple(bal + CHAIN_AT), (0.985, 0.46))]
    keys = [k for k in CAMS if CAMS[k] and (not os.environ.get("ORG_VIEWS") or k in os.environ["ORG_VIEWS"].split(","))]
    shots = []
    for key in keys:
        set_cam(sc, key)
        base = sc.render_base()
        if os.environ.get("ORG_AT_OPEN"):
            sc.labels = [(t, xyz, box, 1.0) for t, xyz, box in sc.sticky_labels]
            try:
                im = sc.overlay(Image.fromarray(base), sc.text_scale, [sc.project(xyz) for _, xyz, _, _ in sc.labels])
            except Exception as e:              # the overlay's own label format: fall back to the bare render
                print("overlay:", e, flush=True)
                im = Image.fromarray(base)
        else:
            im = Image.fromarray(base)
        shots.append((key, im.convert("RGB")))
    tw, th = 640, 360
    cols = 3
    sheet = Image.new("RGB", (tw * cols, th * ((len(shots) + cols - 1) // cols)), "white")
    d = ImageDraw.Draw(sheet)
    for i, (lbl, im) in enumerate(shots):
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(im.resize((tw, th)), (x, y))
        d.text((x + 6, y + 4), lbl, fill=(200, 0, 0))
        im.save(f"/tmp/org_gif_{lbl}.png")
    sheet.save("/tmp/org_gif_views.png")
    sc.pl.close()
    print("views -> /tmp/org_gif_views.png", flush=True)


# ============================================================================================ running moves side by side
class Track:
    """A generator of (seconds, factory) segments run against a clock. factory() -> update(u) or None is called when
    its segment starts, so each move starts from the state the ones before it left; the generator's own code between
    its yields (a grasp, a tray's lamp) runs as one segment ends and the next starts."""

    def __init__(self, gen):
        self.gen, self.t0, self.dur, self.up, self.done = gen, 0.0, 0.0, None, False
        self._next(0.0)

    def _next(self, t0):
        try:
            dur, fac = next(self.gen)
        except StopIteration:
            self.done, self.up = True, None
            return
        self.t0, self.dur = t0, float(dur)
        self.up = fac() if fac is not None else None

    def end(self):
        return self.t0 + self.dur

    def advance(self, t):
        from scene import ease
        while not self.done:
            if t < self.end() - 1e-9:
                if self.up is not None:
                    self.up(ease((t - self.t0) / self.dur))
                return
            if self.up is not None:
                self.up(1.0)
            self._next(self.end())


def run(sc, main, *background):
    """Run the `main` track step by step (Scene.step: one step a segment, each eased) with the `background` tracks
    advancing on the same clock; then whatever is left of the background ones."""
    import props as P
    from scene import FPS
    bg = [Track(g) for g in background]
    clock = 0.0

    def step(d, up):
        nonlocal clock
        n = max(1, int(round(d * FPS)))
        t0, dd = clock, n / FPS

        def upd(e):
            if up is not None:
                up(e)
            for b in bg:
                b.advance(t0 + P.unease(e) * dd)
        sc.step(sc.label, "", dd, upd, hold=0.0)
        clock += dd
    for dur, fac in main:
        step(dur, fac() if fac is not None else None)
    while any(not b.done for b in bg):
        d = min(b.end() for b in bg if not b.done) - clock
        if d < 0.5 / FPS:            # a segment ending within half a frame: finish it between frames
            for b in bg:
                if not b.done and b.end() - clock < 0.5 / FPS:
                    b.advance(b.end() + 1e-6)
            continue
        step(d, None)


def wait(seconds):
    yield seconds, None


def call(f):
    """A track step that only runs f (a caption, labels, a lamp) between the segments around it."""
    f()
    return
    yield


def both(*fs):
    def up(u):
        for f in fs:
            if f is not None:
                f(u)
    return up


def pick(rb, M_grasp, M_pre, group, grip, opening=0.0, s=ARM_S):
    """animate.pick as a track: joint move to M_pre opening the gripper to `opening`, line to M_grasp, close, take
    `group`, line back."""
    yield s[0], lambda: both(rb.joint_to(Tw=M_pre), rb.grip_to(opening))
    yield HOLD, None
    yield s[1], lambda: rb.line_to(M_grasp)
    yield HOLD, None
    yield s[2], lambda: rb.grip_to(grip)
    rb.grasp(group)
    yield HOLD, None
    yield s[3], lambda: rb.line_to(M_pre)
    yield HOLD, None


def place(rb, M_place, M_pre, new_parent, opening=0.0, s=ARM_S):
    """animate.place as a track; the gripper opens to `opening` to let go."""
    yield s[0], lambda: rb.joint_to(Tw=M_pre)
    yield HOLD, None
    yield s[1], lambda: rb.line_to(M_place)
    yield HOLD, None
    yield s[2], lambda: rb.grip_to(opening)
    rb.release(new_parent)
    yield HOLD, None
    yield s[3], lambda: rb.line_to(M_pre)
    yield HOLD, None


def park(rb, secs=1.2):
    import animate as A
    yield secs, lambda: rb.joint_to(A.PARK_RAD)
    yield HOLD, None


def fetch(L, k, f=1.0):
    """setup_lab.TwoLab.fetch as a track: the same moves and times (f x them: the loading's time-lapse)."""
    import vlm as V
    L.use(L.unit.get(k, 1))
    ys, zs = V.SLOTS[L.where[k]]
    yt, zt = V.SLOTS["open"]
    if abs(L.lift_z - zs) > 1:
        yield f * max(0.6, abs(L.lift_z - zs) / 1333), lambda: L.lift_to(zs)
        yield f * 0.1, None
    L.where[k] = None
    L.apply_state()
    yield f * 2.2, lambda: L.slide(k, 0.0)
    yield f * 0.1, None
    yield f * max(0.6, abs(zs - zt) / 1333), lambda: L.lift_to(zt, carry=k)
    yield f * 0.1, None
    yield f * 0.7, lambda: L.shut(1.0)
    yield f * 2.2, lambda: L.slide(k, yt)
    yield f * 0.7, lambda: L.shut(0.0)
    L.where[k] = "open"
    L.apply_state()
    yield f * 0.3, None


def store(L, k, f=1.0):
    """setup_lab.TwoLab.store as a track (f x its times)."""
    import animate as A
    import vlm as V
    L.use(L.unit.get(k, 1))
    L.where[k] = None
    L.apply_state()
    ys, zs = V.SLOTS[A.HOME[k]]
    yield f * 0.7, lambda: L.shut(1.0)
    yield f * 2.2, lambda: L.slide(k, 0.0)
    yield f * 0.7, lambda: L.shut(0.0)
    yield f * 0.1, None
    yield f * max(0.6, abs(L.lift_z - zs) / 1333), lambda: L.lift_to(zs, carry=k)
    yield f * 0.1, None
    yield f * 2.2, lambda: L.slide(k, ys)
    L.where[k] = A.HOME[k]
    L.apply_state()
    yield f * 0.3, None


def drive(L, to, follow=None, cams=None):
    """The docked unit to `to` (x, y; heading 0) along props.s_curve, from rest to rest at the MiR250's 0.3 m/s^2
    (props.ramp_frac); `follow` is a label's anchor (a list), moved with it. With `cams` (k0, k1), the camera goes from
    view k0 to view k1 at the MiR's own pace: the share of the way it has driven is the share of the way between."""
    import props as P
    u, rb, sc = L.units[0], L.robot, L.sc
    x0, y0, hd = u.pose
    at, ps, s = P.s_curve(x0, y0, to[0], to[1])
    d0 = None if follow is None else [follow[0] - x0, follow[1] - y0]

    def fac():
        def up(e):
            f = P.ramp_frac(P.unease(e), s[-1], MIR_V)
            x, y, h = at(float(np.interp(f * s[-1], s, ps)))
            u.set((x, y, h))
            if d0 is not None:
                follow[0], follow[1] = x + d0[0], y + d0[1]
            if cams is not None:
                cam_between(sc, cams[0], cams[1], f)
            if rb.held is not None:
                rb.set()
        return up
    yield max(1.4, P.ramp_secs(s[-1], MIR_V)), fac
    yield HOLD, None


def cam_between(sc, k0, k1, f):
    """The camera f of the way from view k0 to view k1 (position, focal point and view angle, each in a line)."""
    a, b = CAMS[k0], CAMS[k1]
    sc.cam = [tuple(float(p + (q - p) * f) for p, q in zip(pa, pb)) for pa, pb in zip(a[:3], b[:3])]
    sc.view_angle = float(a[3] + (b[3] - a[3]) * f)


def cam_to(sc, key, secs):
    """A track segment: the camera from wherever it is to view `key`."""
    def fac():
        a = [np.array(v, float) for v in sc.cam]
        va = sc.view_angle
        b = CAMS[key]

        def up(e):
            sc.cam = [tuple(p + (np.array(q, float) - p) * e) for p, q in zip(a, b[:3])]
            sc.view_angle = float(va + (b[3] - va) * e)
        return up
    yield secs, fac


# ============================================================================================ the parts of a long render
STILL_EVERY = int(os.environ.get("ORG_STILL_EVERY", "12"))


def still_skip(hook, every=STILL_EVERY):
    """The audit's frame hook, run on every frame where an arm has moved since the last one it checked (its joints, its
    MiR's pose, what it holds), and on every `every`-th frame while none has (ORG_STILL_EVERY; 1 checks every frame).
    In this loop an arm stands still only parked: at the rePowder while the trays are loaded and while the cup melts,
    and at the opening while the doser doses, its shuttle 300 mm and more from the folded arm."""
    last = [None]

    def h(sc):
        key = tuple((tuple(np.round(rb.q, 6)), tuple(np.round(sc.world(rb.root)[:3, :].ravel(), 3)),
                     rb.held[0] if rb.held else None) for rb in getattr(sc, "robots", []))
        if every > 1 and key == last[0] and sc.n % every:
            return
        last[0] = key
        hook(sc)
    return h


def frame_range(env):
    v = os.environ.get(env)
    if not v:
        return None
    a, b = v.split(":")
    return int(a), int(b)


def part_snap(sc, a, b):
    """Draw only frames a..b-1 (ORG_PART): the others are counted, not drawn, so parts rendered side by side join into
    the whole clip."""
    snap = sc.snap

    def f(n=1):
        n0 = sc.n
        k = len(range(max(n0, a), min(n0 + n, b)))
        if k == 0:
            sc.want_still = False
            sc.n = n0 + n
            return None
        sc.n = max(n0, a)
        hi = snap(k)
        sc.n = n0 + n
        return hi
    sc.snap = f


def stride_snap(sc, every, out="/tmp/org_stride"):
    """Draw only every `every`-th frame, to `out` as JPEGs (ORG_STRIDE): the whole loop checked in a few minutes."""
    import time

    from PIL import Image
    os.makedirs(out, exist_ok=True)
    t0 = time.time()

    def f(n=1):
        n0 = sc.n
        lo, hi = frame_range("ORG_STRIDE_RANGE") or (0, 10 ** 9)
        hit = [k for k in range(n0, n0 + n) if k % every == 0 and lo <= k < hi]
        if hit:
            base = sc.render_base()
            anchors = [sc.project(xyz) for _, xyz, _, _ in sc.labels]
            hi = sc.overlay(Image.fromarray(base), sc.text_scale, anchors)
            hi.convert("RGB").resize((960, 540)).save(f"{out}/{hit[0]:05d}.jpg", quality=82)
            print(f"stride: frame {hit[0]} ({sc.label}), {time.time() - t0:.0f} s", flush=True)
        sc.n = n0 + n
        return None
    sc.snap = f


def cam_up(sc, key):
    """An update(e) taking the camera from where it is now to view `key` (call it as its segment starts)."""
    a = [np.array(v, float) for v in sc.cam]
    va = sc.view_angle
    b = CAMS[key]

    def up(e):
        sc.cam = [tuple(p + (np.array(q, float) - p) * e) for p, q in zip(a, b[:3])]
        sc.view_angle = float(va + (b[3] - va) * e)
    return up


# ============================================================================================ the cycle
def movie():
    """The cycle, rendered real-time. The scene draws only the leader labels: the title, the step captions and the
    speed badge go in the GIF's header band (gif()), from the phases written into out/<NAME>.json."""
    import alloy_atomize as AT
    import alloy_charge as AC
    import alloy_press as AP
    import animate as A
    import carousel as CR
    import charge as C
    import lab
    import props as P
    import pyvista as pv
    import scene as SC
    import vlm as V
    import warehouse as W
    from scene import OUT, R, T
    M, RP = AT.M, AT.RP
    sc, L, K, fx = build(lab.meshes())
    sc.title = ""
    part, apart = frame_range("ORG_PART"), frame_range("ORG_AUDIT_PART")
    if os.environ.get("ORG_STRIDE") and not (SC.PREVIEW or SC.AUDIT):
        stride_snap(sc, int(os.environ["ORG_STRIDE"]))
    elif part and not (SC.PREVIEW or SC.AUDIT):
        part_snap(sc, *part)
    if apart and SC.AUDIT and sc.auditor is not None:      # this pass checks frames a..b-1 only
        aud = sc.auditor
        sc.frame_hooks[sc.frame_hooks.index(aud)] = still_skip(lambda s, aud=aud: aud(s) if apart[0] <= s.n < apart[1]
                                                               else None)
    if os.environ.get("ARM_AUDIT_RENDER") and not (SC.PREVIEW or SC.AUDIT):
        import collide                      # ARM_AUDIT=1's audit in the render's own pass: one pass for both (with
        sc.auditor = aud = collide.Auditor(sc)      # ORG_PART, of the part's own frames, for audit_join)
        lo, hi = part or (0, 10 ** 9)
        sc.frame_hooks.append(still_skip(lambda s, aud=aud: aud(s) if lo <= s.n < hi else None))
    sc.frame_hooks.insert(0, fx)            # the melt, before the audit sees the frame
    rb, car = L.robot, L.carousel
    cg = f"cup{CUP}"
    PR = AP.pressed_recipe()["runs"]["Al-10Si"]
    h_si, h_set = float(PR["column_mm_alloying"]), float(PR["column_mm_set"])
    set_cam(sc, CAM)
    sc.intro = 0.8
    phases = []

    def phase(text):
        phases.append(dict(start_frame=sc.n, text=text))

    def labels(*ls):
        sc.sticky_labels = list(ls)

    # ------------------------------------------------------------------ the labels (box: fractions of the frame; a
    # box left of the middle has its left edge at fx, one right of it its right edge; fy is its middle)
    dock = W.dock_pose("vlm")
    arm_at = [WAIT_AT[0], WAIT_AT[1] - 250.0, 1250.0]      # moves with the MiR (drive's `follow`)
    lbl_arm = ("the operator: a MiR250 + UR10e", arm_at, (0.40, 0.93))
    lbl_vlm = ("the VLM, a Kardex Shuttle XP 500:\nits trays come to the opening", (-700.0, -900.0, 2950.0),
               (0.985, 0.08))
    lbl_rp = ("AMAZEMET rePowder atomizer", (RP[0] + 120.0, RP[1] + 250.0, 1750.0), (0.02, 0.08))
    lbl_cell = ("sieving cell", (-1982.5, -1250.0, 1650.0), (0.30, 0.18))
    _gl = M.latch_geom()
    lbl_latch = ("draw latch", tuple(RP + M.lid_to_model((_gl["x"], _gl["yface"] - 16.0, _gl["zf"] + 0.6 * _gl["length"]))),
                 (0.985, 0.62))
    lbl_lid = ("the lid, hinged on its left", tuple(RP + (-60.0, 0.0, 1560.0)), (0.02, 0.10))
    lbl_tong = ("loading tong", None, (0.985, 0.30))
    lbl_melt = ("the melt (time-lapse)", tuple(RP + (-10.0, 5.0, M.Z_CR + 10.0)), (0.02, 0.22))
    lbl_plate = ("droplets off the vibrating plate", tuple(RP + tuple(M.IMPACT + np.array([60.0, 0.0, -30.0]))),
                 (0.985, 0.50))
    lbl_pw = ("powder", tuple(RP + (M.CHUTE_X, 0.0, 230.0)), (0.985, 0.82))
    at_start = [lbl_vlm, lbl_rp, lbl_arm]
    labels(*at_start)
    loads = L.loads

    # ------------------------------------------------------------------ 1. the whole lab; trays A and B loaded at the
    # opening (a time-lapse, as the set-up movie loads them); tray A back up, tray B left there
    def item_at(k, key):
        g = next(g for kk, g, _, _ in L.items.get(k, []) if kk == key)
        return np.array(sc.world(g)[:3, 3])

    def load_labels(k):
        """Tray k's instruments, named as the set-up names them (setup_lab.item_label), over where they stand; tray
        B's three side by side are placed by hand."""
        if k == "B":
            return [("the multi-doser v5, 13 powders,\non its HR-202i balance",
                     tuple(K.bal_cup() + (150.0, 80.0, 560.0)), (0.985, 0.10)),
                    ("the vacuum press", tuple(K._w("tray_B", (*AP.PRESS_AT, 420.0))), (0.30, 0.10)),
                    ("charge cups, 5N Al", tuple(K.rack_cup(1) + (0.0, 0.0, 70.0)), (0.02, 0.30))]
        lbls = [(nm, tuple(np.array(sc.world(g)[:3, 3]) + (0.0, 0.0, 420.0))) for key, g, names, nm in
                L.items.get(k, []) if key not in ("ups", "cam") and any(loads[k].a0.get(n, 0.0) > 0 for n in names)]
        return W.auto(sc, CAMS["load"][:3], lbls, dy=0.16)

    def overview():
        yield from call(lambda: phase("A vertical lab: storage that brings each instrument to the operator, a "
                                      "mobile robot arm."))
        yield 1.4, None
        yield from call(lambda: phase("First its trays are loaded (a time-lapse): each comes down to the opening, "
                                      "and people put its instruments on."))
        yield from cam_to(sc, "load", 3.6)

    def seq(*gens):
        for g in gens:
            yield from g
    run(sc, overview(), seq(wait(1.4), fetch(L, "A", LOAD_F)))

    def load(k, text):
        yield from call(lambda: (phase(text), labels(*load_labels(k))))
        yield LOAD_SECS, lambda: loads[k].slide
        yield 0.6, None
    names_A = [nm for key, g, names, nm in L.items.get("A", []) if key not in ("ups", "cam")]
    run(sc, load("A", f"Tray A: {', '.join(names_A)}, with its UPS and its camera posts."))

    def swap():
        yield from call(lambda: (phase("Tray A goes back up to its slot, where it has power, and tray B comes down."),
                                 labels(lbl_vlm)))
        yield from store(L, "A", LOAD_F)
        yield from fetch(L, "B", LOAD_F)
    run(sc, swap())
    run(sc, load("B", "Tray B: the multi-doser v5 on its balance, the charge cups in their rack, and the vacuum "
                      "press."))

    # ------------------------------------------------------------------ 2. the MiR in, to the opening
    lbl_B = ("tray B at the opening:\nthe multi-doser v5 on its balance", tuple(K.bal_cup() + (150.0, 80.0, 560.0)),
             (0.985, 0.10))
    lbl_rack = ("charge cups, 5N Al", tuple(K.rack_cup(1) + (0.0, 0.0, 70.0)), (0.02, 0.62))

    def come_in():
        yield from call(lambda: (phase("Only then does the robot come in: it docks at the opening, to work at tray B."),
                                 labels(lbl_arm, lbl_B)))
        yield from drive(L, dock[:2], arm_at, ("load", "trayB"))
    run(sc, come_in())

    # ------------------------------------------------------------------ 3. the cup dosed: Si, then the top-up, each
    # with the module docked and tilted before the shuttle brings the cup in over the balance (high_pedestal)
    bal = K.bal_cup()                 # the cup's foot on the tall pedestal
    CAMS["dose"] = [tuple(bal + DOSE_OFF), tuple(bal + DOSE_LOOK), (0, 0, 1), DOSE_VA]
    CAMS["cup"] = [tuple(bal + CUP_OFF), tuple(bal + CUP_LOOK), (0, 0, 1), CUP_VA]
    CAMS["fork"] = [tuple(bal + FORK_OFF), tuple(bal + FORK_LOOK), (0, 0, 1), FORK_VA]
    mods = L.modules
    lbl_mods = [(f"the {pname} module", mods.point(pname), box) for pname, box in MOD_LBL]
    lbl_chain = ("13 powder modules on a chain,\none powder in each", tuple(bal + CHAIN_AT), (0.985, 0.46))
    lbl_cup = ("the cup, cut open, 34 mm under\nthe auger, on a tall pedestal", tuple(bal + (0.0, 0.0, 40.0)),
               (0.985, 0.74))
    f = DOSE_F
    p_rack = K.rack_cup(CUP) + (0, 0, GRASP_DOWN)
    p_hand = K.hand_cup() + (0, 0, GRASP_DOWN)

    def dose_up(layer, h0, h1):
        spin0 = car.state["spin"]
        stt = car.to(spin=spin0 + 2 * math.pi * 2.0)         # eight quarter turns, a reading after each

        def up(u):
            stt(u)
            on = 1.0 if 0.05 < u < 0.95 else 0.0
            pts = AC.stream_points(L, K, CUP, u * 6.0, on)
            sc.alpha["stream"] = 1.0 if len(pts) else 0.0
            if len(pts):
                sc.set_mesh("stream", pv.PolyData(pts))
            k = min(1.0, max(0.0, (u - 0.12) / 0.83))
            if layer == 0:
                K._point[CUP] = k > 0.02
                K.powder_h[CUP] = h1 * max(0.0, (k - 0.08) / 0.92)
                K.powder_h2[CUP] = K.powder_h[CUP]
            else:
                K.powder_h2[CUP] = h0 + (h1 - h0) * k
            K.apply()
            K.cut(CUP, True, sleeve=None)
        return up

    turned = []
    # the fork's seat (its frame's origin, where the cup's foot stands), rig frame: carried level, at z_hover; let down
    # until the cup's foot is FORK_GAP over the pedestal; dropped until the sleeve is 4 mm clear under its foot
    # (FORK_UNDER), to back out round the pedestal's neck; FORK_GAP under it, to take it
    px, py = float(CR.PAN_XY[0]), float(CR.PAN_XY[1])
    z_rest = CR.SEAT_Z + CR.SEAT_LIFT
    z_hover = z_rest + FORK_LIFT
    z_let, z_take = CR.SEAT_Z + FORK_GAP, CR.SEAT_Z - FORK_GAP
    z_under = CR.SEAT_Z - FORK_UNDER

    def fork_to(y, z):
        """A straight move of the held fork, level, to its seat at (px, y, z) in the rig's frame."""
        return rb.line_to(sc.world(K.rig) @ T((px, y, z)) @ G_fork[0])

    def reset_held():
        """The cup has gone onto or off the held fork: the checkers re-read what the arm is holding."""
        for chk in [rb._checker] + list(getattr(sc.auditor, "checkers", {}).values()):
            if chk is not None:
                chk.held_group = None

    G_fork, on_seat = [], []

    def fork_grasp():
        """The handle's grasp (world), the pads across the post's x or, if the arm can't reach that, its other way
        round; picked once, nearest the arm's joints now."""
        if not G_fork:
            best = None
            for flip in (False, True):
                G = fork_grasp_local() @ (R((0, 0, 1), 180.0) if flip else np.eye(4))
                try:
                    q = rb.solve(sc.world("cupfork") @ G, rb.q)
                except ValueError:
                    continue
                d = float(np.abs(q - rb.q).max())
                if best is None or d < best[0]:
                    best = (d, G)
            G_fork.append(best[1] if best else fork_grasp_local())
        return sc.world("cupfork") @ G_fork[0]

    fork_at = [0.0, 0.0, 0.0]          # the fork's label rides its handle (a frame hook)

    def fork_hook(s_):
        fork_at[:] = (sc.world("cupfork") @ np.r_[0.0, -(FORK_L - 15.0) + FORK_HANDLE[1] / 2,
                                                  FORK_HANDLE_H + 10.0, 1.0])[:3]
    sc.frame_hooks.insert(0, fork_hook)
    fork_hook(sc)
    lbl_fork = ("the cup fork: the gripper\ncan't reach in itself", fork_at, (0.02, 0.80))

    def take_fork():
        """The fork by its handle, off its rest (from wherever the arm is: parked, or over the cup's rack)."""
        yield ARM_S[0], lambda: both(rb.joint_to(Tw=T((0, 0, 100)) @ fork_grasp()), rb.grip_to(OPEN_FORK),
                                     cam_up(sc, "fork"))
        yield HOLD, None
        yield ARM_S[1], lambda: rb.line_to(fork_grasp())
        yield ARM_S[2], lambda: rb.grip_to(GRIP_FORK)
        rb.grasp("cupfork")
        yield 0.4, lambda: fork_to(CR.Y_HAND, z_hover)

    def leave_fork(*also):
        """The fork back down on its rest and let go; the hand up off it. `also`: updates run alongside (the doser's
        own moves)."""
        yield 0.4, lambda: both(fork_to(CR.Y_HAND, z_rest), *[a() for a in also[:1]])
        yield ARM_S[2], lambda: both(rb.grip_to(OPEN_FORK), *[a() for a in also[1:2]])
        rb.release(K.rig)
        yield HOLD, None
        yield ARM_S[3], lambda: both(rb.line_to(T((0, 0, 100)) @ rb.tcp_world()), *[a() for a in also[2:3]])

    def cup_in():
        """The arm carries the cup in on the fork over the balance and lets it down onto the pedestal; the fork drops
        until its sleeve is clear under the cup's foot, backs out from under it (the pedestal's neck out along the
        slot), rises and comes back out past the -y panel. Then a cut to the cup, close (the camera's way in would pass
        through the arm)."""
        yield 1.6, lambda: fork_to(py, z_hover)
        yield 0.5, lambda: fork_to(py, z_let)
        Mw = sc.world(cg)
        p = Mw[:3, 3] - np.array([0.0, 0.0, FORK_GAP])          # onto the pedestal
        if not turned:
            # set down with its cut face (charge.cup(cut=True) keeps the +y half) to the close view: a whole cup looks
            # the same whichever way it is turned about its axis
            Mw = T(p) @ R((0, 0, 1), cut_face())
            turned.append(True)
        else:
            Mw = Mw.copy()
            Mw[:3, 3] = p
        sc.parent[cg] = K.rig
        sc.gmat[cg] = AT.inv(sc.world(K.rig)) @ Mw
        reset_held()
        K.cut(CUP, True, sleeve=None)
        yield 0.3, lambda: fork_to(py, z_under)
        yield 0.4, lambda: fork_to(py - FORK_BACK, z_under)
        yield 0.3, lambda: fork_to(py - FORK_BACK, z_hover)
        yield 1.3, lambda: fork_to(CR.Y_HAND, z_hover)
        yield from call(lambda: set_cam(sc, "cup"))

    def cup_out(whole=False):
        """A cut back out to the fork's view; the fork back in, short of the cup; down, and in under its foot round
        the pedestal's neck (along the slot); up, the sleeve round the cup's foot, to take it off the pedestal, and out
        past the -y panel (whole: the cup drawn whole again, its last dose in)."""
        yield from call(lambda: set_cam(sc, "fork"))
        yield 1.3, lambda: fork_to(py - FORK_BACK, z_hover)
        yield 0.3, lambda: fork_to(py - FORK_BACK, z_under)
        yield 0.4, lambda: fork_to(py, z_under)
        yield 0.3, lambda: fork_to(py, z_take)
        Mw = sc.world(cg)
        sc.parent[cg] = "cupfork"
        sc.gmat[cg] = AT.inv(sc.world("cupfork")) @ Mw
        reset_held()
        if whole:
            K.cut(CUP, False, sleeve=None)
        yield 0.5, lambda: fork_to(py, z_hover)
        sc.gmat[cg][:3, 3] = on_seat[0]                         # on the seat (it was taken FORK_GAP under its foot)
        yield 1.4, lambda: fork_to(CR.Y_HAND, z_hover)

    def at_B():
        yield from call(lambda: (phase("The arm stands an empty charge cup on its cup fork: its gripper can't reach "
                                       "into the doser."), labels(lbl_arm, lbl_B, lbl_rack, lbl_fork)))
        yield from pick(rb, A.down(p_rack, spin=0.0), A.down(p_rack + (0, 0, 110), spin=0.0), cg, GRIP_CUP, OPEN_CUP)
        yield from place(rb, A.down(p_hand, spin=180.0), A.down(p_hand + (0, 0, 120), spin=180.0), "cupfork",
                         OPEN_CUP)
        on_seat.append(sc.gmat[cg][:3, 3].copy())          # the cup standing on the fork's seat, in the fork's frame
        fork_grasp()                                       # (picked now, with the arm over the fork)
        # the arm out of the way while the chain indexes; the camera back to take in the doser's chain
        yield 1.4, lambda: both(rb.joint_to(A.PARK_RAD), cam_up(sc, "dose"))
        yield from call(lambda: labels(*lbl_mods, lbl_chain))
        for layer, pname, h0, h1, text in (
                (0, "Si", 0.0, h_si, f"One powder in each module: the chain brings the Si to the balance, and "
                                     f"{PR['alloying_g']:.2f} g of it goes into the cup ..."),
                (1, "AlSi10Mg", h_si, h_set, f"... then the AlSi10Mg module: {PR['top_up_g']:.2f} g on top, for "
                                             f"Al-10Si.")):
            m = AC.MODULE[pname]
            yield from call(lambda text=text: phase(text))
            yield 2.6 * f, lambda m=m: car.to(shift=car.index_to(m))
            yield 1.2 * f, lambda: car.to(ext=CR.DOCK_EXT, magnet_on=True)
            yield 1.3 * f, lambda: car.to(tilt=CR.TILT)
            # the arm takes the fork, with the cup on it, and carries it in
            yield from call(lambda layer=layer: labels(lbl_mods[layer], lbl_fork))
            yield from take_fork()
            yield from cup_in()
            yield from call(lambda: labels(lbl_cup))
            yield 3.4 * 0.8, lambda layer=layer, h0=h0, h1=h1: dose_up(layer, h0, h1)
            sc.alpha["stream"] = 0.0
            if layer == 0:
                K.powder_h[CUP] = h1
                K._point[CUP] = True
            K.powder_h2[CUP] = h1
            K.apply()
            K.cut(CUP, True, sleeve=None)
            yield 0.3, None
            yield from call(lambda: labels(lbl_mods[layer], lbl_fork))
            yield from cup_out(whole=layer == 1)
            # the fork, the cup on it, back on its rest while the module tilts back and undocks
            undock = (lambda: car.to(tilt=0.0), lambda: car.to(spin=car.state["spin"] - 2 * math.pi),
                      lambda: car.to(ext=0.0, magnet_on=False))
            if layer == 0:
                yield from leave_fork(*undock)
                yield 1.2, lambda: both(rb.joint_to(A.PARK_RAD), cam_up(sc, "dose"))
                yield from call(lambda: labels(*lbl_mods, lbl_chain))
            else:
                yield from call(lambda: (phase("The arm puts the fork back, and stands the charged cup in the carrier "
                                               "on the robot."), labels(lbl_arm, lbl_B, lbl_fork)))
                yield from leave_fork(*undock)
                yield 1.0, lambda: cam_up(sc, "trayB")
        K.cut(CUP, False, sleeve=None)
        yield from pick(rb, A.down(p_hand, spin=180.0), A.down(p_hand + (0, 0, 120), spin=180.0), cg, GRIP_CUP,
                        OPEN_CUP)
        p_car = K.carrier_seat(CARRIER_K) + (0, 0, GRASP_DOWN)
        yield from place(rb, A.down(p_car, spin=0.0), A.down(p_car + (0, 0, 120), spin=0.0), "amr", OPEN_CUP)
        yield from park(rb)
    run(sc, at_B())

    # ------------------------------------------------------------------ 4. tray B back up; the MiR to the rePowder
    def go():
        yield from call(lambda: (phase("Tray B goes back into storage, and the robot takes the cup to the atomizer."),
                                 labels(lbl_arm)))
        yield from drive(L, RP_STOP, arm_at, ("trayB", "rp"))
    run(sc, go(), store(L, "B"))

    # ------------------------------------------------------------------ 5. at the rePowder: latch, lid, tong, cup in
    gl = M.latch_geom()

    def lid(s):
        sc.gmat[AT.g("hood")] = M.joint_matrix("lid", s * RP_LID_U)

    def latch(s):
        sc.gmat[AT.g("latch_lever")] = M.joint_matrix("latch", s * LATCH_U)

    def bolt(s0, s1):
        def up(e):
            sc.gmat[AT.g("latch_bolt")] = M.joint_matrix("bolt", s0 + (s1 - s0) * e)
        return up

    def latch_grasp(s):
        out, up_, tilt = LATCH_AT
        a = math.radians(tilt)
        Mx = P.tcp_frame(np.array([gl["x"], gl["yface"] - out, gl["zf"] + up_ * gl["length"]]),
                         (0.0, math.cos(a), -math.sin(a)), 0.0)
        return T(RP) @ M.joint_matrix("latch", s * LATCH_U) @ M.LID_FRAME @ Mx     # latch_geom: the lid's frame

    kc = M.knob_centre()

    def knob_grasp(s):
        Mx = P.tcp_frame(kc + np.array([0.0, -KNOB_OUT, 0.0]), (0.0, 1.0, 0.0), 0.0)
        return T(RP) @ M.joint_matrix("lid", s * RP_LID_U) @ Mx

    def arc(pose, s0, s1, n):
        return AT.follow(rb, [pose(s0 + (s1 - s0) * x) for x in np.linspace(0.0, 1.0, n)])

    def jaws(f0, f1):
        def up(e):
            AT.tong_jaws(sc, f0 + (f1 - f0) * e)
        return up

    def hold_cup():
        """The tong has shut on the cup: the arm holds the cup now, the tong riding on it (alloy_atomize's
        bookkeeping, for the audit: a held part may touch where it came from and where it goes)."""
        tw, cw = sc.world("tong"), sc.world(cg)
        rb.events.append((sc.n, "release", "tong", None))
        sc.parent.pop(cg, None)
        sc.gmat[cg] = cw
        rb.held = (cg, AT.inv(rb.tcp_world()) @ cw)
        rb.events.append((sc.n, "grasp", cg, "amr"))
        sc.parent["tong"] = cg
        sc.gmat["tong"] = AT.inv(cw) @ tw

    def hold_tong():
        tw, cw = sc.world("tong"), sc.world(cg)
        sc.parent.pop("tong", None)
        sc.gmat["tong"] = tw
        if sc.parent.get(cg) is None:
            sc.parent[cg] = "tong"
            sc.gmat[cg] = AT.inv(tw) @ cw
        rb.events.append((sc.n, "release", cg, None))
        rb.held = ("tong", AT.inv(rb.tcp_world()) @ tw)
        rb.events.append((sc.n, "grasp", "tong", None))

    def cup_down():
        """The jaws open: the cup stays, standing on the floor cone at its place."""
        sc.parent[cg] = AT.g("crucible")
        sc.gmat[cg] = AT.inv(sc.world(AT.g("crucible"))) @ T(RP) @ AT.cup_pose(CUP_AT, AT.CUP_R,
                                                                                AT.cup_seat(CUP_AT)[2], 0.0)
        rb.events.append((sc.n, "release", cg, AT.g("crucible")))
        for chk in [rb._checker] + list(getattr(sc.auditor, "checkers", {}).values()):
            if chk is not None:
                chk.held_group = None

    st = {}

    def to_arc(key, grasp, pose, move, close, skip, pres, opening, n=17):
        """A joint move to the first reachable of the poses `pres` (world), in an IK branch from which the arm can
        follow pose(s) as move(s) swings the part, touching nothing but `skip` (alloy_atomize.arc_branch's test), and
        whose approach pose is clear with the gripper open to `opening`; the gripper opens to it on the way."""
        def fac():
            import collide
            chk = rb.checker()
            cands = collide.ik_all(rb.model, AT.inv(sc.world(rb.root)) @ grasp, rb.q) or [rb.solve(grasp)]
            got = None
            for q in cands:
                ok, qq = True, q.copy()
                for u in np.linspace(0.0, 1.0, n):
                    move(u)
                    try:
                        q_new = rb.solve(pose(u), qq)
                    except ValueError:
                        ok = False
                        break
                    if np.abs(q_new - qq).max() > math.radians(20):
                        ok = False
                        break
                    qq = q_new
                    if any(not any(k in h[2] for k in skip) for h in chk.collisions(qq, close, chk.snapshot())):
                        ok = False
                        break
                move(0.0)
                if not ok:
                    continue
                for pre in pres:
                    try:
                        q_pre = rb.solve(pre, q)
                    except ValueError:
                        continue
                    if np.abs(q_pre - q).max() < math.radians(60) and not chk.collisions(q_pre, opening,
                                                                                         chk.snapshot()):
                        got = q_pre
                        break
                if got is not None:
                    break
            if got is None:
                print(f"warning: {key}: no IK branch clear along the swing and at the approach", file=sys.stderr,
                      flush=True)
                got = rb.solve(pres[-1], cands[0])
            st[key] = got
            if os.environ.get("ORG_DEBUG"):
                w = chk.snapshot()
                print(f"debug {key} frame {sc.n}: start hits {chk.collisions(rb.q, rb.close, w)[:3]}; "
                      f"end hits at {opening} {chk.collisions(got, opening, w)[:3]}; "
                      f"at close {rb.close:.2f} {chk.collisions(got, rb.close, w)[:3]}", flush=True)
            return both(rb.joint_to(q1=got), rb.grip_to(opening))
        return fac

    def clear_line(cands, close):
        """The first of the poses `cands` (world) that the grasp point can reach in a straight line from where it is,
        clear of everything all the way (the same samples as robot.line_to), with the gripper at `close`."""
        import collide
        from scipy.spatial.transform import Rotation, Slerp
        chk = rb.checker()
        w = chk.snapshot()
        T0 = rb.tcp_world()
        for T1 in cands:
            sl = Slerp([0.0, 1.0], Rotation.from_matrix(np.stack([T0[:3, :3], T1[:3, :3]])))
            q, ok = rb.q.copy(), True
            for s_ in np.linspace(0.0, 1.0, 21)[1:]:
                Mx = np.eye(4)
                Mx[:3, :3] = sl([s_]).as_matrix()[0]
                Mx[:3, 3] = T0[:3, 3] + (T1[:3, 3] - T0[:3, 3]) * s_
                try:
                    qn = rb.solve(Mx, q)
                except ValueError:
                    ok = False
                    break
                if np.abs(qn - q).max() > math.radians(25) or chk.collisions(qn, close, w):
                    ok = False
                    break
                q = qn
            if ok:
                return T1
        print(f"warning: frame {sc.n}: no clear line among {len(cands)} back-offs", file=sys.stderr, flush=True)
        return cands[-1]

    def at_rp():
        yield from call(lambda: (phase("At the atomizer, the arm pulls the lid's draw latch open and lifts the lid by "
                                       "its knob."), labels(lbl_arm, lbl_latch, lbl_lid)))
        yield 0.8, lambda: bolt(0.0, 1.0)                       # the pneumatic locking bolt goes back
        yield ARM_S[0], to_arc("latch", latch_grasp(0.0), latch_grasp, latch, GRIP_LATCH, ("latch",),
                               [latch_grasp(0.0) @ T((0, 0, -100))], OPEN_LATCH)
        yield HOLD, None
        yield ARM_S[1], lambda: rb.line_to(latch_grasp(0.0))
        yield ARM_S[2], lambda: rb.grip_to(GRIP_LATCH)
        rb.events.append((sc.n, "grasp", AT.g("latch_lever"), None))
        yield 1.4, lambda: both(arc(latch_grasp, 0.0, 1.0, 9), latch)
        yield ARM_S[2], lambda: rb.grip_to(OPEN_LATCH)
        rb.events.append((sc.n, "release", AT.g("latch_lever"), None))
        # off the lever: straight back along the tool, as far as is clear (100 mm back, the upper arm met the furnace)
        yield ARM_S[3], lambda: rb.line_to(clear_line([latch_grasp(1.0) @ T((0, 0, -d)) for d in (60.0, 45.0, 30.0)] +
                                                      [T((0, 0, -d)) @ latch_grasp(1.0) for d in (40.0, 25.0)],
                                                      OPEN_LATCH))
        # the knob from above: backed off level, the flange would come within the UR10e's reach of its own base axis.
        # Lifted past its balance point and let go, the lid settles onto its stop; the hand is left in the clear
        yield ARM_S[0], to_arc("knob", knob_grasp(0.0), lambda s: knob_grasp(LID_LET * s),
                               lambda s: lid(LID_LET * s), GRIP_KNOB, ("knob",), [T((0, 0, 100)) @ knob_grasp(0.0)],
                               0.45)
        yield HOLD, None
        yield ARM_S[1], lambda: rb.line_to(knob_grasp(0.0))
        yield ARM_S[2], lambda: rb.grip_to(GRIP_KNOB)
        rb.events.append((sc.n, "grasp", AT.g("knob"), None))
        yield 1.9, lambda: both(arc(knob_grasp, 0.0, LID_LET, 10), lambda e: lid(LID_LET * e))
        yield 0.3, lambda: rb.grip_to(0.2)
        rb.events.append((sc.n, "release", AT.g("knob"), None))
        # it falls back onto its stop as the hand backs off (left where it let go, the fingertips met the shell)
        yield 0.5, lambda: both(lambda e: lid(LID_LET + (1.0 - LID_LET) * e * e),
                                rb.line_to(clear_line([knob_grasp(LID_LET) @ T((0, 0, -d)) for d in (50.0, 35.0, 20.0)] +
                                                      [T((0.0, -d, dz)) @ knob_grasp(LID_LET)
                                                       for d, dz in ((60.0, 40.0), (40.0, 60.0), (0.0, 60.0))], 0.2)))
        # the loading tong out of its holder on the MiR's cabinet (alloy_atomize: chapter 2's moves)
        yield from call(lambda: (phase("With a loading tong, the arm takes the cup and sets it on the crucible's "
                                       "floor, past the sealing rod."), labels(lbl_arm, lbl_tong_at())))
        home = AT.tong_tcp(sc.world("tong"))
        yield 1.6, lambda: both(rb.joint_to(Tw=T((0, 0, 130)) @ home), rb.grip_to(0.0))
        yield 0.8, lambda: rb.line_to(home)
        yield 0.4, lambda: rb.grip_to(AT.GRIP_TONG)
        rb.grasp("tong")
        yield 0.9, lambda: rb.line_to(T((0, 0, 210)) @ rb.tcp_world())
        xm = sc.world(L.amr_group)[:3, 0]
        top = (sc.world(cg) @ np.r_[0.0, 0.0, C.SLUG_L, 1.0])[:3]
        F = np.eye(4)
        F[:3, 0], F[:3, 1], F[:3, 2], F[:3, 3] = xm, np.cross((0, 0, 1.0), xm), (0, 0, 1), top
        g_pick = AT.tong_tcp(F)
        yield 1.4, lambda: both(rb.joint_to(Tw=T((0, 0, 90)) @ g_pick), rb.grip_to(AT.GRIP_TONG_OPEN), jaws(0.0, 1.0))
        yield 0.7, lambda: rb.line_to(g_pick)
        yield 0.4, lambda: both(rb.grip_to(AT.GRIP_TONG), jaws(1.0, 0.0))
        hold_cup()
        yield 0.6, lambda: rb.line_to(T((0, 0, 150)) @ rb.tcp_world())
        path = AT.tong_path(CUP_AT)
        grips = [AT.tong_tcp(T(RP) @ AT.tong_frame_for(CUP_AT, Mx)) for Mx in path]
        # over the crucible from straight above its first pose (chapter 2 swung it in from 200 mm in front, its lever
        # up: with the lever down, that line took the cup across the rod's adapter)
        stage = T((0, 0, 80)) @ grips[0]
        yield 1.3, lambda: both(rb.joint_to(Tw=stage), cam_up(sc, "bore"))
        yield 0.6, lambda: rb.line_to(grips[0])
        # down the bore in three legs, the arm's "held" part swapping between the cup and the tong (alloy_atomize)
        yield 1.2, lambda: AT.follow(rb, grips[:4])
        hold_tong()
        yield 0.8, lambda: AT.follow(rb, grips[3:5])
        hold_cup()
        yield 1.4, lambda: AT.follow(rb, grips[4:])
        hold_tong()
        yield 0.4, lambda: both(rb.grip_to(AT.GRIP_TONG_OPEN), jaws(0.0, 1.0))
        cup_down()
        yield 0.8, lambda: rb.line_to(T((0, 0, 170)) @ rb.tcp_world())
        home2 = AT.tong_tcp(sc.world("amr") @ L.tong_home)
        yield 1.6, lambda: both(rb.joint_to(Tw=T((0, 0, 220)) @ home2), rb.grip_to(AT.GRIP_TONG), jaws(1.0, 0.0),
                                cam_up(sc, "rp"))
        yield 0.9, lambda: rb.line_to(home2)
        yield 0.4, lambda: rb.grip_to(0.0)
        rb.release("amr")
        yield 0.6, lambda: rb.line_to(T((0, 0, 120)) @ rb.tcp_world())
        # the lid down and the latch shut, the bolt in
        yield from call(lambda: (phase("The arm shuts the lid and the latch, and the locking bolt goes in."),
                                 labels(lbl_arm, lbl_latch, lbl_lid)))
        # the knob where the lid rests: a planned joint move straight to it, the hand wide open (backed off from it
        # either way, the arm runs out of reach), then the lid pulled back over its balance point and lowered
        # (round 7: the lid turns about the hand's own axis now, so the hand comes in along it, from the front)
        yield 1.6, to_arc("knob_open", knob_grasp(1.0), lambda s: knob_grasp(1.0 - s), lambda s: lid(1.0 - s),
                          GRIP_KNOB, ("knob",), [knob_grasp(1.0) @ T((0, 0, -d)) for d in (60.0, 40.0, 25.0)] +
                          [T((0, 0, z)) @ knob_grasp(1.0) for z in (40.0, 25.0)], 0.45)
        yield 0.5, lambda: rb.line_to(knob_grasp(1.0))
        yield 0.4, lambda: rb.grip_to(GRIP_KNOB)
        rb.events.append((sc.n, "grasp", AT.g("knob"), None))
        yield 2.0, lambda: both(arc(knob_grasp, 1.0, 0.0, 12), lambda e: lid(1.0 - e))
        yield 0.4, lambda: rb.grip_to(0.45)
        rb.events.append((sc.n, "release", AT.g("knob"), None))
        yield 0.7, lambda: rb.line_to(clear_line([T((0, 0, d)) @ knob_grasp(0.0) for d in (100.0, 60.0, 40.0)], 0.45))
        # (round 7: the lever is on the furnace's right now, its open grasp out towards the panel and the HMI, so the
        # hand may come to it from above or from the front as well as back along the tool)
        yield 1.4, to_arc("latch_open", latch_grasp(1.0), lambda s: latch_grasp(1.0 - s), lambda s: latch(1.0 - s),
                          GRIP_LATCH, ("latch",), [latch_grasp(1.0) @ T((0, 0, -d)) for d in (100.0, 70.0, 50.0)] +
                          [T((0, 0, d)) @ latch_grasp(1.0) for d in (80.0, 50.0)] +
                          [T((0, -d, 0)) @ latch_grasp(1.0) for d in (80.0, 50.0)], OPEN_LATCH)
        yield 0.7, lambda: rb.line_to(latch_grasp(1.0))
        yield 0.4, lambda: rb.grip_to(GRIP_LATCH)
        rb.events.append((sc.n, "grasp", AT.g("latch_lever"), None))
        yield 1.4, lambda: both(arc(latch_grasp, 1.0, 0.0, 9), lambda e: latch(1.0 - e))
        yield 0.4, lambda: rb.grip_to(OPEN_LATCH)
        rb.events.append((sc.n, "release", AT.g("latch_lever"), None))
        yield 0.7, lambda: rb.line_to(clear_line([latch_grasp(0.0) @ T((0, 0, -d)) for d in (100.0, 60.0, 40.0)],
                                                 OPEN_LATCH))
        yield 0.6, lambda: both(bolt(1.0, 0.0), rb.joint_to(A.PARK_RAD))
        yield from park(rb, 0.8)

    def lbl_tong_at():
        return ("loading tong", tuple(sc.world("tong")[:3, 3] + (0.0, 0.0, 200.0)), (0.985, 0.30))
    run(sc, at_rp())

    # ------------------------------------------------------------------ 6. melted and atomized; out to the wide view,
    # and trays A and B emptied again: the last frame is the first
    def melt():
        yield from call(lambda: (phase("The atomizer melts the cup and sprays the melt into powder (a time-lapse, "
                                       "cut open)."), fx.start(sc), labels(lbl_melt, lbl_plate, lbl_pw)))
        yield 1.6, lambda: cam_up(sc, "cut")
        yield ATOM_SECS - 1.6 - 4.6, None
        yield from call(lambda: (phase("The robot has moved off, to wait for its next job."), labels(*at_start)))
        yield from cam_to(sc, "wide", 4.6)
        yield 0.5, None
        yield 1.2, lambda: both(*[loads[k].fade_out() for k in LOADED])
        yield 0.3, None

    def away():                       # off the rePowder as the cut opens, out of the cutaway's view
        yield from drive(L, WAIT_AT, arm_at)
    run(sc, melt(), away())
    out = sc.save()
    if sc.auditor is not None and not SC.AUDIT and not part:      # ARM_AUDIT_RENDER=1, the whole loop
        sc.auditor.save()
    if sc.auditor is not None and (apart and SC.AUDIT or part and not SC.AUDIT):
        os.makedirs("/tmp/org_audit", exist_ok=True)
        with open(f"/tmp/org_audit/{(apart or part)[0]:05d}.json", "w") as fh:
            json.dump(dict(frames=sc.auditor.frames, parent=sc.parent,
                           events={r.prefix: [list(e) for e in r.events] for r in sc.robots}), fh)
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm; {sc.n} frames; the melt ran frames {fx.n0}-{fx.n1}",
          flush=True)
    for p in rb.plans:
        if p.get("reason"):
            print(f"unplanned joint move at frame {p.get('frame')}: {p.get('reason')}", flush=True)
    if fx.n1 is None:
        print("warning: the melt had not ended by the last frame, so the loop jumps", file=sys.stderr)
    meta_path = OUT / f"{NAME}.json"
    if meta_path.exists() and not os.environ.get("ARM_AUDIT") and not os.environ.get("PREVIEW"):
        meta = json.loads(meta_path.read_text())
        meta.update(title=TITLE, speed=SPEED, camera=CAM, phases=phases)
        meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return out


def join(*names):
    """Parts rendered side by side (ORG_PART, each under its own ORG_NAME) -> out/mp4/<NAME>.mp4 and out/<NAME>.json."""
    from scene import OUT
    names = names or sorted(p.stem for p in (OUT / "mp4").glob(f"{NAME}_p*.mp4"))
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        for nm in names:
            fh.write(f"file '{(OUT / 'mp4' / f'{nm}.mp4').resolve()}'\n")
        lst = fh.name
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags",
                    "+faststart", str(OUT / "mp4" / f"{NAME}.mp4")], check=True)
    meta = json.loads((OUT / f"{names[0]}.json").read_text())
    meta["name"] = NAME
    (OUT / f"{NAME}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    print(f"joined {len(names)} parts -> {NAME}.mp4", flush=True)


def audit_join():
    """The audited parts (ORG_AUDIT_PART, /tmp/org_audit/) -> one report, out/collisions/<NAME>.json, by
    collide.Auditor's own rules over every frame."""
    import glob
    from types import SimpleNamespace

    import collide
    frames, parent, events = [], {}, {}
    for pth in sorted(glob.glob("/tmp/org_audit/*.json")):
        d = json.load(open(pth))
        frames += d["frames"]
        parent, events = d["parent"], d["events"]
    frames.sort(key=lambda fr: fr["n"])
    aud = collide.Auditor.__new__(collide.Auditor)
    aud.sc = SimpleNamespace(name=NAME, parent=parent,
                             robots=[SimpleNamespace(prefix=p, events=ev) for p, ev in events.items()])
    aud.frames, aud.checkers, aud.snap_frames = frames, {}, set()
    rep = aud.save()
    if STILL_EVERY > 1:          # the report says what was checked: still_skip passed over frames where nothing moved
        from scene import OUT
        pth = OUT / "collisions" / f"{NAME}.json"
        r = json.loads(pth.read_text())
        r["method"] = r["method"].replace(
            "every frame of the clip, after its update",
            f"every frame of the clip where an arm has moved (its joints, its MiR's pose, what it holds), and every "
            f"{STILL_EVERY}th while none has (org_gif.still_skip), after its update")
        pth.write_text(json.dumps(r, indent=1) + "\n")
    print(f"{rep['frames_with_collisions']} of {rep['frames_checked']} frames with collisions", flush=True)


BAND = 86            # px at 1280 wide: the white header band over the render that holds the GIF's text


def header(img, caption: str):
    """The frame under a white band: the org page's title, the step's caption and the speed badge."""
    from PIL import Image, ImageDraw

    import scene as SC
    w = img.width
    k = w / 1280
    H = int(round(BAND * k / 2)) * 2      # even, for the h264 copy
    out = Image.new("RGB", (w, img.height + H), "white")
    out.paste(img, (0, H))
    d = ImageDraw.Draw(out)
    d.text((18 * k, 9 * k), TITLE, font=SC.font(29 * k, bold=True), fill=(20, 20, 24))
    d.text((18 * k, 50 * k), caption, font=SC.font(21 * k), fill=(55, 58, 66))
    fb = SC.font(20 * k, bold=True)
    badge = f"{SPEED:g}× speed"
    x1 = w - 18 * k
    x0 = x1 - d.textlength(badge, font=fb) - 26 * k
    d.rounded_rectangle((x0, 12 * k, x1, 46 * k), 6 * k, fill=(30, 60, 140))
    d.text((x0 + 13 * k, 17 * k), badge, font=fb, fill=(255, 255, 255))
    d.line([(0, H - 1), (w, H - 1)], fill=(30, 60, 140), width=max(1, int(round(2 * k))))
    return out


def gif(width=GIF_W, lossy=0, colors=112, sticky=int(os.environ.get("ORG_STICKY", "8"))):
    """out/mp4/<NAME>.mp4 -> out/<NAME>.gif, every frame at SPEED x the MP4's rate, each under the header band; and the
    same frames as out/mp4/<NAME>_readme.mp4 (SPEED x, h264), for anyone who would rather embed a video. One palette
    for the whole clip (the camera holds still), no dithering, gifsicle -O3 and no --lossy: lossy re-encoding drifts
    where things moved, and the loop then flickers where the last frame meets the first. On a first cut of round 1's
    clip, --lossy=40 gave 3.3 MB with 38,771 px of the last frame off the first; lossless, 4.3 MB and 5,819 px, nearly
    all by a shade (the MP4's own noise). Round 2's loop is 702 frames: 192 colours gave 8.7 MB, 128 give 7.7 MB with
    no banding to see at the README's size.
    Round 3's is 962 frames of closer views: 47.5 MB as it was. The MP4's noise flickers pixels in the parts that hold
    still, so each frame stored more than what moved. `sticky` keeps a pixel from the frame before wherever no channel
    has changed by more than that many levels (of 255), so those parts are the same bytes from frame to frame: 40.0 MB
    at 6. Most of what is left is the two pans, which change every pixel for about 115 frames. Motion isn't held back:
    something moving across a pixel changes it by far more than 6 levels.
    Round 4's is 1331 frames, wide and close, with the camera moving for about a third of them (the zoom in and out,
    the push in to the pan and back, the pan with the MiR, the bore and the cutaway). Its first half alone came to
    37.2 MB at 1280 px, 128 colours and `sticky` 6; 26.0 MB at 1024 px; 28.3 MB at 1120 px, 112 colours and 8. So
    1024 px, 112 colours and 8.
    Round 5's is 1563 frames (the trays loaded, the doser's close views): 52.7 MB at 1024 px, 47.5 MB at 960 px.
    Round 6's is 1815 frames (the arm carries the cup in on its fork): 55.8 MB at 960 px, 51.0 at 900, 49.1 at 880."""
    from PIL import Image

    from scene import OUT
    mp4, out = OUT / "mp4" / f"{NAME}.mp4", OUT / f"{NAME}.gif"
    meta = json.loads((OUT / f"{NAME}.json").read_text())
    phases = meta["phases"]
    fps = meta["fps"] * SPEED
    sw, sh = meta["size"]
    w, h = width, int(round(sh * width / sw / 2)) * 2
    def frames():
        dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", str(mp4), "-vf",
                                f"scale={w}:{h}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                               stdout=subprocess.PIPE)
        while True:
            buf = dec.stdout.read(w * h * 3)
            if len(buf) < w * h * 3:
                break
            yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        dec.wait()

    def held(a, prev):
        if prev is None or sticky <= 0:
            return a
        keep = (np.abs(a.astype(np.int16) - prev.astype(np.int16)).max(axis=2) <= sticky)[..., None]
        return np.where(keep, prev, a)
    prev = None
    if sticky > 0:     # a first pass to where the held pixels end up, so the first frame starts from there: held
        for a in frames():         # from a fresh first frame instead, the loop's seam differed in 8,375 px by over 16
            prev = held(a, prev)   # levels, against 2,837 with nothing held
    with tempfile.TemporaryDirectory() as tmp:
        n = 0
        for a in frames():
            prev = held(a, prev)
            cap = [p["text"] for p in phases if p["start_frame"] <= n][-1]
            header(Image.fromarray(prev), cap).save(f"{tmp}/{n:05d}.png", compress_level=1)
            n += 1
        seq_ = ["-framerate", f"{fps:g}", "-i", f"{tmp}/%05d.png"]
        pal = f"{tmp}/pal.png"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *seq_, "-vf",
                        f"palettegen=max_colors={colors}:stats_mode=full", pal], check=True)
        raw = f"{tmp}/raw.gif"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *seq_, "-i", pal, "-lavfi",
                        "[0:v][1:v]paletteuse=dither=none:diff_mode=rectangle", "-loop", "0", raw], check=True)
        subprocess.run(["gifsicle", "-O3", f"--lossy={lossy}", "-o", str(out), raw], check=True)
        vid = OUT / "mp4" / f"{NAME}_readme.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *seq_, "-c:v", "libx264", "-crf", "20", "-preset", "slow",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(vid)], check=True)
        Image.open(f"{tmp}/00000.png").save(OUT / f"{NAME}_still.png", optimize=True)   # its first frame
    msg = (f"{out.name}: {out.stat().st_size / 1e6:.2f} MB, {w} x {h + int(round(BAND * w / 1280 / 2)) * 2}, {n} frames at "
           f"{fps:g} fps ({n / fps:.1f} s); {vid.name}: {vid.stat().st_size / 1e6:.2f} MB")
    print(msg, flush=True)
    return msg


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "movie"
    {"views": views, "movie": movie, "gif": gif, "join": join, "audit_join": audit_join}[arg](*sys.argv[2:])
