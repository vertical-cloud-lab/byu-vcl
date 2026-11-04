## The alloy route, chapter 5: the build through the characterization trays

![Chapter 5](../out/alloy_characterize.gif)

Sterling, on PR #318: "It seems a bit redundant to have the trays come to the opening with nothing else happening when
we already saw them getting loaded. Better would be to see them being used in an actual workflow." And earlier: "we
want to see the full alloy workflow going on, start to finish". So this chapter carries on from chapter 4 (a printed
AlSi10Mg plate, one bar broken in the 68FM-100). Samples of the same build go through trays F, E and D at the VLM's
opening. Each tray comes down only when it is needed, the UR10e on its MiR250 loads and unloads each instrument, and
each instrument runs its own joints from `instruments.py`, sped up, with a clock on screen. Then the tray goes back.

[`alloy_characterize.py`](../alloy_characterize.py) is the scene. It is `animate.Lab` (the VLM, the MiR at the opening)
plus trays D-F as `line.py` builds them. Every instrument is placed from `line.TRAY_LOADS` and its own frame, never a
hard-coded position, so a re-planned tray layout is picked up on the next run.

| | |
|---|---|
| MP4, 1280 × 720, 10 fps, 143 s (1431 frames) | [`out/mp4/alloy_characterize.mp4`](../out/mp4/alloy_characterize.mp4) (8.1 MB) |
| GIF, 640 × 360, 5 fps | [`out/alloy_characterize.gif`](../out/alloy_characterize.gif) (4.8 MB) |
| Frame range of every sub-step | [`out/alloy_characterize.json`](../out/alloy_characterize.json) |
| The still: the SEM step, with the inset | [`out/alloy_characterize_still.png`](../out/alloy_characterize_still.png) |
| Eight moments, from the MP4 | [`out/alloy_characterize_sheet.png`](../out/alloy_characterize_sheet.png) |
| Collision audit, every frame | [`out/collisions/alloy_characterize.json`](../out/collisions/alloy_characterize.json) |

![Eight moments: the holder onto the PX500's head, grinding, the holder back face up, the SEM loaded, the SEM's inset,
the iMicro loaded, the pour, the Mastersizer measuring](../out/alloy_characterize_sheet.png)

### The steps

1. **The samples arrive.** The MiR250 drives up to the opening from the line. It carries the coupon, cut from the
   plate and hot-mounted in a 1.25 in Bakelite mount, sitting in the PX500's 6-position holder on a rest. It also
   carries a 20 mL vial of the sieved powder in a two-pocket caddy.
2. **Tray F: grinding and polishing on the LECO PX500.**
   - The head lifts 70 mm for a holder change.
   - The arm takes the holder off its rest by a tab, carries it in level under the head, 4 mm low, and lifts it onto
     the spindle's coupling.
   - Grinding follows the lab's SOP: 320 to 1200 grit SiC with water, 30 s a paper; the platen and the holder turn.
     Then 1 µm alumina on a white cloth for 3 min. The clock shows the SOP's own time, 9 min.
   - The head lifts. The arm takes the holder off and rolls it over on the way back, so it lies face up on the rest.
   - The arm lifts the mount out by its polished end while tray F goes back.
3. **Tray D: the Hitachi TM4000PlusII.**
   - The SEM vents and its door comes out with the stage. The arm sets the mount, face up, in a cup on the stage.
   - Door in, pump-down, BSE images and an EDS map (the clock shows about 20 min). The door comes out again and the
     arm takes the mount back.
   - Tray D goes back up; the arm holds the mount meanwhile.
4. **Tray E: the KLA iMicro, then the Mastersizer 3000.**
   - The hood lifts and the stage runs out to a load position. The arm sets the mount on the stage.
   - Hood down; the stage carries the mount under the microscope, then the indenter, for a 5 × 5 grid of indents,
     and back (the clock shows 45 min).
   - The arm puts the mount in the caddy on the MiR.
   - It takes the powder vial by its side, the Aero S's cover lifts off, and a 120° roll of the wrist pours the powder
     into the hopper. The vial goes back to the caddy.
   - Cover on; the tray feeds the powder through the venturi to the cell, past the laser (drawn see-through).
   - Tray E goes back.

### What is assumed

None of these are the makers' published arrangements. They are our design choices, at assumed sizes:
- **The coupon is already cut and mounted.** Cutting it from the plate (the wire EDM can do it in chapter 4's
  fixture) and hot-mounting it are not shown. The lab has no mounting press in these models.
- **The PX500's holder is changed by the arm, whole.** The head takes interchangeable specimen holders (LECO's
  brochure: fixed and individual holders). These are ours:
  - a 55 × 24 × 12 mm tab on the holder's rim for the gripper;
  - a quick-change coupling the holder is lifted onto from 4 mm below;
  - a 70 mm head lift for the change (LECO publishes no stroke);
  - the other five pockets hold mounts from the same build.

  Under the head, the holder's pockets can't be reached from above, and the 13 mm the mounts stand proud are too
  little for the fingers from below, so the holder is swapped whole rather than the mounts.
- **The mount is 25 mm tall.** It stands 13 mm proud of the holder's face side, and the back is flush.
- **The coupon's pocket is slotted for the fingertips.** So with the holder face up, the arm can take the mount by its
  polished end. The gripper's grasp point is 5 mm outside the face, so the pads hold the top 13 mm and stop short of a
  cup's rim.
- **The holder's rest and the caddy are low blocks on the MiR's cabinet top.** That is the round-7 rule for the MiR's
  storage (`props.pocket_block`): no post, 1 mm clearance, lead-ins at the pockets.
  - The holder's rim sits on a ledge 16 mm up inside a 4 mm wall, with a notch for the tab.
  - The caddy's mount pocket is 10 mm deep (40 % of the mount); the vial's is 26 mm (43 %).
- **The SEM's mount cup is ours.** It is an 18 mm cup with an 8 mm bore and a set screw, on the stage 30 mm ahead of
  the stage's socket. At the socket itself, 40 mm in front of the SEM's face with the door out, every IK solution puts
  the wrist into the SEM's front.
- **The iMicro's stage loads 60 mm out in x and 60 mm forward.** The model's stage moves in x only. The y travel is
  drawn as the mount's own move on the stage.
  - A probe of 8 IK branches × 4 gripper turns × 7 stage positions found this the only clear load position.
  - Further in, the forearm or the wrist runs into the cabinet.
- **The Aero S's cover is lifted by an actuator.** Malvern's is lifted off by hand.
- **The SEM inset is real data, but not of this section.** It is chapter 4's image of the lab's AlSi10Mg powder: BYU's
  Apreo, Gage Erickson, 2 April 2026, byu-vcl#48. No image of a polished section of this build exists yet. The inset
  says so.
- **No results are shown for the indents or the size distribution.** None have been measured for this build.

### The arm's collisions

`ARM_AUDIT=1 VIZ3D_FPS=10 xvfb-run -a python3 alloy_characterize.py` checks every rendered frame. The result is
**0 of 1266 frames in collision**. At 15 fps it is 0 of 1883: the same moves, sampled more finely. The rules are
`collide.Auditor`'s:
- the gripper may touch what it is picking up or putting down, within 4 s of the grasp or the release;
- a held part may touch where it came from and where it goes.

The first draft had 245 frames in collision in its polisher steps alone, and the first full draft had 132 of 1875.

It took these changes to get there:
- The holder's rest and the caddy moved behind the arm. Beside the arm's base, the upper arm swept through them.
  Pointing at the arm, the tab put the flange inside the UR's unreachable cylinder over its base.
- The tab is gripped across its sides, not top and bottom. That way the gripper is its 75 mm thickness tall, not its
  130 mm finger span, where it passes over the bowl's lip.
- The holder goes in 4 mm low and is lifted onto the coupling. Slid in at its final height, the mounts would run
  into the spindle.
- The SEM cup sits ahead of the socket, and the iMicro's load position moved, as above.
- Mounts are taken with the wrist camera on the side away from the instrument (gripper turned 180°). Otherwise the
  D405 on the coupling hits the SEM's and the iMicro's fronts.
- Each approach's joint move goes to the IK branch that is clear where its straight line ends (`branch_q`, as in
  `alloy_workflow.py`).

### Not done

- **The tray plan's re-arranged trays D-F,** if they land after this render, need a re-run. Nothing is hard-coded,
  but the load positions above were checked only for the layout in `line.TRAY_LOADS` at the time.
- **The PIP, the XRD, the OpenFlexures and the furnace are only seen, not used.** The PIP's bay is 77 mm tall between
  the platen and the crosshead, so its sample can't go in on the 2F-85's fingers; Plastometrex's AutoStage would be
  the way in.
- **The SiC papers and the cloth are changed off screen.**
- **Rendered at 10 fps,** like chapters 1-4 in the long-form.
