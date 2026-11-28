## Getting a tray out for maintenance, with the mobile base

Asked on PR #318: how do trays come off for maintenance, and can the tray service dock work with the rail there?
Since then the rail is gone (Sterling, PR #318: "Just stick with the mobile manipulator setup"). With the MiR250, the
front opening works for maintenance as Kardex intends.

![Plan and side view at the opening](../out/maintenance_access.png)

[`maintenance.py`](../maintenance.py) draws this to scale. It reads the geometry from the scene modules' own
constants: `vlm.py`, `animate.py`, `props.py`, `services.py` and `setup_lab.py`. The numbers are in
[`out/maintenance_access.json`](../out/maintenance_access.json).

### The tray service dock is not a way out

It is round 4's coupling ([`services.py`](../services.py), [services notes](services.md)). A Stäubli plate on the
tray's back-right corner carries mains, Ethernet, air, N₂ and chilled water. It mates with a dock in the side wall of
each slot and of the bay. Every dock is inside the VLM, and none of them moves a tray anywhere.

### Kardex's way out: full tray extraction onto a cart

From the Kardex Remstar Shuttle XP brochure ([dealer PDF](https://www.supplycore.com/wp-content/uploads/2022/01/Shuttle-XP-Vertical-Lift-Module-1108-1.pdf)):
- **p. 6:** "With the full tray extraction device, a tray is placed in front of the access opening for loading and
  unloading purposes. This can be loaded onto the optional transport cart for safe and easy handling."
- **p. 5, the options list:**
  - automatic and manual tray extraction;
  - a transit trolley;
  - a factory-fitted crane;
  - tray extraction for forklift operation;
  - up to six access openings per unit.
- **p. 7:** "Automatic or manual tray extraction also make the use of hoists and cranes trouble-free."

Kardex publishes no size for the extraction table or the cart. So the drawing shows only the tray, pulled clear of the
opening. That is the least floor extraction can need: the tray's 864 mm in front of the cladding, after 964 mm of
travel.

### With the mobile base, the front works

- **Nothing fixed stands in front of the opening.** The MiR250 docks there to work (its body 80-660 mm in front of the
  cladding, its cabinet 780 mm high) and drives off before a tray comes out.
- **The VLM's AprilTag target stands outside the opening's width,** on a post at x = -1330 mm. The post is 80 mm clear
  of the tray's side, so the extracted tray passes it. Only the post's 12 mm foot plate reaches under the tray's
  corner, on the floor (setup_lab.TARGET_AT).
- **The extraction table, the cart and a person have the floor in front of the opening,** and the 3.0 m aisle beyond
  the dock.
- **The second Shuttle stands 800 mm to the right.** That gap is the MiRs' turning spot, so keep it clear while a tray
  is out.

What the rail would have cost, for the record (round 4's drawing): its beam filled 26-442 mm in front of the cladding,
436-699 mm high, with a leg under the opening. That left no floor for the extracted tray, and put the tray's front
edge 464 mm from the beam. A rear service opening was the fix then. With the mobile base it isn't needed, and it would
have cost two rear slots.

### What to ask Kardex

- Is full tray extraction offered on the XP 500 2450 × 864, with the 996 mm opening?
- What does the extraction table measure, and how much clear floor does it need?
- What load is the transit trolley rated for, against our heaviest tray?
