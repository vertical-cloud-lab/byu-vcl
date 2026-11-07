## Automating the crucible: what it would take

Sterling on PR #318: *"Things related to the crucible in terms of automation are going to be very difficult. Fragile
graphite materials that are getting screwed onto other graphite materials. Custom end effector attachments,
high-sensitivity force sensing (torque for example), are all things that would be very important for trying to do this
automation."*

He is right. The job can be split into steps a UR10e could try, but not with the arm as it is now. It needs a wrist
force/torque sensor far finer than the UR10e's own, a few custom tools, a fixture that acts as a second hand, and bench
trials with spare graphite before it goes near the machine. Nothing below has been tried.

### What is in the furnace

From the lab's rePowder SOP, top to bottom:
- Graphite sealing rod (12.6 mm, ball tip in the nozzle), brass adapter on top, held by a lever and a safety pin.
- BN-coated graphite crucible (57.1 mm bore, ~225 cm³). Its threaded graphite nozzle-holder shank runs down through the
  bottom insulation, the furnace floor and the chamber's top plate. The nozzle, a small graphite plate with a 0.5 or
  0.7 mm bore, sits in the holder's top recess.
- Under the plate, in the chamber: a graphite seal and a thin graphite nut.
- Alumina-silica insulation (bottom, side tube, top cone), and a Type N thermocouple in a thin ceramic sheath, in a
  hole in the crucible wall.

People strip and rebuild this between runs ([T7 00:09](https://www.youtube.com/embed/FDRTt68Vfvo?start=9)). The nut
goes on from below, through the chamber's left door, while someone holds the crucible still at the top
([T1 47:02](https://www.youtube.com/embed/wRc8p2_FnJo?start=2822)). The crucible is tightened "until it feels tight and
no further" ([T1 46:08](https://www.youtube.com/embed/wRc8p2_FnJo?start=2768)); overtightening cracks the holder thread
([T9 33:45](https://www.youtube.com/embed/9kn-HhXCr1o?start=2025)). Thread engagement is tiny: "you just barely have to
get it on" ([T8 02:26](https://www.youtube.com/embed/HTlUrAr5HVU?start=146)).

### A sequence a robot could follow

Furnace cold, lid open, chamber door open. Steps 1–5 strip it down and 6–13 rebuild it. Each step names the tool,
then what is sensed.

1. Thermocouple out: gripper on it outside the port, pull along the port. Sense the pull force; camera on the sheath.
2. Rod out. The SEALING ROD button lifts it (pressed by the arm, or a PLC signal if AMAZEMET allows one). A hook tool
   pulls the pin and swings the lever up. The rod is lifted by its brass adapter, never by the graphite.
3. Insulation out (top cone, side tube, bottom) with wide, soft paddles. Sense grip force; the camera looks for breaks.
4. Crucible free. A nut tool in the chamber holds the nut and seal while the crucible turns at the top. Log the
   breakaway torque every time. The nut and seal stay in the tool, so nothing falls.
5. Crucible lifted straight out into a cradle. The camera looks for cracks, slag and bare BN, checks the rod's ball
   tip, and checks for light through the nozzle ([OCT2a 10:08](https://www.youtube.com/embed/qYyT39D5Yzo?start=608)).
6. On the bench: nozzle plate into the holder, white side up (vacuum cup or tweezer fingers; the camera reads the side).
   Holder and crucible screwed together in a soft-jawed fixture, to a torque limit.
7. Graphite seal and bottom insulation in. The camera checks they sit flat.
8. Crucible lowered straight into the coil, shank through the floor: light downward force, spiral search if it hangs.
9. Seal and nut on from below (thread finding, below). Before the nut is snug, turn the crucible so its thermocouple
   hole faces the port at the back right. Stop at the torque limit.
10. Side tube (its hole lined up with the port), then the top cone.
11. Thermocouple in along the port, through a guide. Sense the insertion force.
12. Rod stood on the nozzle: lower it until the force rises a little and let the ball centre in its seat. Lever down,
    pin in, SEALING ROD down.
13. The machine checks the work. The furnace pumps down to −1 bar without the "Pressure crucible" warning
    ([T5 34:39](https://www.youtube.com/embed/58wJ_Khwgyk?start=2079)), and the thermocouple reads; the HMI raises
    "master temperature sensor" when it is out ([T1 38:06](https://www.youtube.com/embed/wRc8p2_FnJo?start=2286)).

### The hard parts

- **Two sides at once, one arm.** The crucible is held at the top while the nut turns underneath, so one side has to
  be a fixture. Either a holder grips the crucible at the top while the arm works the nut through the door, or the arm
  holds the crucible while a powered nut driver works from below. The second copies the SOP's two-person method and
  keeps the torque limit in a tool that can be set on the bench. Whether one MiR pose reaches both is for the model.
- **Graphite on graphite.** Both parts are brittle. Engagement is short, so the thread start is easy to miss, and a
  crossed start cuts the graphite. Pitch, turns of engagement and the crucible's outside diameter are not in the SOP.
- **Small torques.** We found no published snug torque. Our estimate is well under 1–2 N·m, set by fingers on a thin
  nut. That is below what the UR10e itself can sense (next section), while its wrist joints are rated to 54 N·m
  ([UR](https://www.universal-robots.com/articles/ur/robot-care-maintenance/max-joint-torques-cb3-and-e-series/)).
- **Brittle sheath.** The thermocouple's ceramic cover "cracks normally"
  ([T1 35:49](https://www.youtube.com/embed/wRc8p2_FnJo?start=2149)), and today the thermocouple is bent by hand.
- **Insulation.** Dusty, and it breaks if dropped ([T4 01:08](https://www.youtube.com/embed/1F9_4ccwhss?start=68)).
  The 2F-85 grips at 20 N at the least (below), so it needs wide pads. Dust on a thread changes its torque.
- **The rod tip** must be clean, smooth and undamaged or it will not seal
  ([T4 01:52](https://www.youtube.com/embed/1F9_4ccwhss?start=112)). The ball must not drag across the crucible floor.
- **Where the robot stands.** The MiR250 docks to a VL-marker within ±3 mm, and drives to a plain position within
  ±60 mm × ±85 mm ([MiR spec](https://www.hartfiel.com/wp-content/uploads/2024/04/MiR250-Specs.pdf)). The arm must find
  the furnace itself each time: camera fiducials, then a light touch-off.

### Sensing

| Sensor | Force | Torque |
|---|---|---|
| UR10e, built in ([datasheet](https://www.universal-robots.com/manuals/latest/en/datasheets/ur10e/)) | ±100 N; precision ±5.0 N; accuracy ±5.5 N | ±10 N·m; precision ±0.2 N·m; accuracy ±0.5 N·m |
| Robotiq FT 300-S ([sheet](https://blog.robotiq.com/hubfs/Product-sheets/FT%20300/ur/Product_sheet-FT300S_FC_EN.pdf)) | ±300 N; noise 0.1 N; contact threshold 1 N | ±30 N·m; noise 0.003 N·m (Mz); contact threshold 0.01 N·m (Mz) |
| ATI Mini45 SI-145-5 ([ATI](https://www.ati-ia.com/products/ft/ft_models.aspx?id=Mini45)) | ±145 N (Fz ±290 N); resolution 1/16 N | ±5 N·m; resolution 1/1504 N·m (Tz) |

- The built-in sensor's torque accuracy, ±0.5 N·m, is about the size of the whole snug torque (estimate). It cannot
  tell "snug" from "about to crack". Its ±5 N force precision is coarser than the light push a thread start needs (a
  few newtons, estimate).
- A sensor between flange and gripper reads Mz to 0.003 N·m (FT 300-S) or finer (Mini45): about 1 % of a 0.3 N·m
  target. The FT 300-S weighs 440 g. The Mini45 weighs 92 g but needs ATI's DAQ or interface
  ([Novanta](https://novanta.com/robotics-automation/product/mini45-force-torque-sensor/)).
- Compliant thread finding, as a person does it:
  1. Press the parts together lightly, at a constant few newtons.
  2. Turn backwards until the axial position drops a little (at most one pitch): that is the thread start.
  3. Turn forwards. Each turn should advance one pitch, with Mz low and the side moments near zero. Torque that
     rises in the first turn, or a short advance, means cross-threading: back off and start again.
  4. Stop at the torque limit from the bench trials. Log the final torque and angle every run.

### Custom tools

- **Crucible gripper.** Holds the outside low down, never the rim or the thread, on wide pads shaped to it. The 2F-85
  opens 85 mm and grips at 20–235 N ([Robotiq](https://assets.robotiq.com/website-assets/support_documents/document/online/2F-85_2F-140_TM_InstructionManual_HTML5_20190503.zip/2F-85_2F-140_TM_InstructionManual_HTML5/Content/6.%20Specifications.htm)).
  With Robotiq's assumed friction of 0.3 and a 40 mm radius (both estimates for this part), that grip carries about
  0.5–5.6 N·m before it slips; less if the outside carries BN, a dry lubricant. Set grip force and torque limit together.
- **Nut tool.** Reaches through the left door and holds the thin nut and the lower seal captive, over a catch cup,
  until the thread has taken. The powered version adds a small motor and a slip clutch set from the bench torque; the
  wrist sensor then reads the reaction through the crucible.
- **Rod-and-pin tool.** Grips the brass adapter, hooks the lever, pulls and pushes the safety pin.
- **Thermocouple guide.** A tube or spring holder at the port, so the thermocouple goes in straight and rests on the
  crucible without being bent each time.
- **Small parts.** A vacuum cup or tweezer fingers for the nozzle plate and seals; a tool changer for all of these.

### Risks

- **Breakage.** Crucible, holder thread and nut crack if overtightened. We have no price for a rePowder crucible; ask
  AMAZEMET. A spare set on the shelf turns a break into a swap.
- **Cross-threading.** It cuts the graphite thread on the first try, and the part is scrap.
- **Dropped parts.** A nut or seal dropped from under the plate falls into the chamber, and graphite breaks when
  dropped ([T4 01:41](https://www.youtube.com/embed/1F9_4ccwhss?start=101)). It has already happened by hand
  ([OCT2b 03:45](https://www.youtube.com/embed/of5-LhkX_VQ?start=225)). Use captive tools and a catch tray.
- **Insulation dust** on threads, seals and the chamber floor. Vacuum afterwards, as people do now.
- **Thermocouple.** The sheath cracks, and a bent or broken thermocouple holds up the run.
- **Downtime.** A crack found at the leak check costs a second strip-down and rebuild. A run takes about 1 h with
  prep ([T5 21:50](https://www.youtube.com/embed/58wJ_Khwgyk?start=1310)); a full cooldown about 30 min
  ([T3 49:52](https://www.youtube.com/embed/txH397FGTAU?start=2992)).
- **Collisions** over the induction coil and under the open lid; the arm can push far harder than graphite can take.

### What to try first

1. Measure what hands do: snug and breakaway torque of both joints (crucible to holder, nut to shank), with a small
   torque screwdriver or a peak-hold torque gauge and an adapter for each part. Several people, several repeats.
2. Measure the parts: thread pitch, turns of engagement, outside diameters, nut thickness, clearance at the door.
3. Break a spare nut and a spare holder on purpose, slowly, in a fixture, and record the torque. Breaking torque over
   snug torque is the robot's margin.
4. Bench rig: a plate with the furnace floor's hole, a spare crucible and nut, and the UR10e with an FT 300-S or a
   Mini45. Find the thread and stop at the limit 50 or more times; count misses and cross-threads. Then try the same
   with the built-in sensor alone.
5. Ask AMAZEMET for the thread spec, any torque figure, part prices, and if a keyed crucible or captive nut is possible.
6. Only then try it on the machine, cold, with a person watching and a spare set on the bench.
