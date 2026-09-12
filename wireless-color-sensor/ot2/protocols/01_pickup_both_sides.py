"""01 -- CHARGING BASE: can the P300 use BOTH sockets?

Drag this file into the Opentrons App and run it. Nothing to install.

WHAT IT IS FOR
--------------
The base has two sockets. In Opentrons terms they are wells of a tip rack:

    A1 = LEFT  (low X)  -- the one that already works on this machine
    A2 = RIGHT (high X) -- never tried

Each step pauses so you can look before it commits to anything, and the run
log prints the deck height of every move.

HOW TO USE IT -- change ONE line (MODE, below) and re-upload. In this order:

  1. MODE = "hover"    <- zero risk. Empty nozzle stops above each socket so
                          you can see how well it lines up.
  2. MODE = "inplace"  <- picks the enclosure up from SIDE and puts it back in
                          the same socket. Set SIDE = "A1" first (proven), then
                          put the enclosure in the RIGHT socket by hand and run
                          SIDE = "A2".
  3. MODE = "shuttle"  <- the real test: A1 -> A2 -> A1, which exercises all
                          four operations. Enclosure must START in A1.

THE ONE THING WORTH KNOWING BEFORE YOU START
--------------------------------------------
Labware Position Check CANNOT separate A1 from A2. LPC stores one offset for
the whole labware, so it slides both sockets together by the same amount.

  * Nozzle off by the SAME amount over both sockets -> that is LPC's job.
  * Off over ONE socket only -> LPC cannot fix it. Edit wells.A2.x / .y in
    ac_color_sensor_charging_port.json (next to this file) and re-upload.

That is the whole reason MODE = "hover" visits both sockets in one run: so you
can tell those two cases apart by eye.

WHY apiLevel 2.13 AND NOT SOMETHING NEWER
-----------------------------------------
On this robot's software (8.8.1) pick_up_tip from a 2-well tip rack raises
"InvalidStoredData: ... less dense than an SBS 96 standard" at API 2.14 and
above. The newer tip-tracking code assumes a rack at least 12 wells wide and
8 wells tall and divides by those, and a 2-well dock fails the check. API 2.13
and below use the older core and are unaffected. Verified by simulating all of
2.13 / 2.14 / 2.16 / 2.18 against opentrons 8.8.1, the robot's own version.

The cost is that API 2.13 has no runtime parameters, so the settings below are
edited here instead of chosen in the app. Labware Position Check still works
normally -- offsets are applied to 2.13 protocols too.
"""

from opentrons import protocol_api  # noqa: F401  (kept for editor autocomplete)

metadata = {
    "protocolName": "01 - charging base: pick up from both sides",
    "author": "vertical-cloud-lab/byu-vcl",
    "description": (
        "Hover over, and optionally pick up from, both sockets of the wireless "
        "colour-sensor charging base. Calibration aid -- no liquid handling."
    ),
    "apiLevel": "2.13",
}

# ======================================================================
#  EDIT THESE
# ======================================================================

MODE = "hover"        # "hover" | "inplace" | "shuttle"
SIDE = "BOTH"         # "A1" (left) | "A2" (right) | "BOTH"   -- ignored by shuttle

DOCK_SLOT = 10        # deck slot the charging base sits in
HOVER_MM = 30.0       # how far above the socket the nozzle stops to be looked at
LIFT_MM = 40.0        # how far up the enclosure is carried after a pick-up
SLOW = True           # 100 mm/s instead of the stock 400, so you can follow it
PAUSE_AT_EACH_STEP = True   # set False once you trust it and just want a cycle

# ======================================================================
#  Below here you should not need to touch.
# ======================================================================

# Where the nozzle lets go, as an offset from the top of the socket. -80 mm on
# an 84 mm socket leaves the enclosure 4 mm off the socket floor before release.
# This is the AccelerationConsortium's own number, unchanged.
RELEASE_FROM_TOP_MM = -80.0

# The charging base as Opentrons labware, embedded so this file is
# self-contained. Byte-for-byte the AccelerationConsortium definition, also
# saved beside this file as ac_color_sensor_charging_port.json -- that copy is
# the one you import into the app for the tip-length calibration. Keep them
# in step: if you edit a socket coordinate, edit it in both.
DOCK_DEF = {'ordering': [['A1'], ['A2']],
     'brand': {'brand': 'AC', 'brandId': []},
     'metadata': {'displayName': 'ac color sensor charging port',
                  'displayCategory': 'tipRack',
                  'displayVolumeUnits': 'µL',
                  'tags': []},
     'dimensions': {'xDimension': 128, 'yDimension': 86, 'zDimension': 100},
     'wells': {'A1': {'depth': 84,
                      'totalLiquidVolume': 1000,
                      'shape': 'circular',
                      'diameter': 66,
                      'x': 36,
                      'y': 43,
                      'z': 16},
               'A2': {'depth': 84,
                      'totalLiquidVolume': 1000,
                      'shape': 'circular',
                      'diameter': 66,
                      'x': 91.95,
                      'y': 43,
                      'z': 16}},
     'groups': [{'metadata': {}, 'wells': ['A1', 'A2']}],
     'parameters': {'format': 'irregular',
                    'quirks': ['centerMultichannelOnWells', 'touchTipDisabled'],
                    'isTiprack': True,
                    'tipLength': 84,
                    'isMagneticModuleCompatible': False,
                    'loadName': 'ac_color_sensor_charging_port'},
     'namespace': 'custom_beta',
     'version': 1,
     'schemaVersion': 2,
     'cornerOffsetFromSlot': {'x': 0, 'y': 0, 'z': 0}}

SIDE_NAME = {"A1": "LEFT (A1)", "A2": "RIGHT (A2)"}


def run(protocol):
    assert MODE in ("hover", "inplace", "shuttle"), "MODE must be hover/inplace/shuttle"
    assert SIDE in ("A1", "A2", "BOTH"), "SIDE must be A1/A2/BOTH"

    dock = protocol.load_labware_from_definition(DOCK_DEF, DOCK_SLOT)
    pipette = protocol.load_instrument("p300_single_gen2", "left", tip_racks=[dock])

    # default_speed is the gantry speed for move_to, in mm/s (400 is stock).
    if SLOW:
        pipette.default_speed = 100

    def hold(message):
        """Always say it in the run log; only actually stop if asked to."""
        protocol.comment(message)
        if PAUSE_AT_EACH_STEP:
            protocol.pause(message)

    def deck_z(well, z_from_top):
        """Height above the deck of a point given relative to the socket top."""
        return round(well.top().point.z + z_from_top, 2)

    def hover_over(name):
        well = dock[name]
        hold("Next: hover {:.0f} mm over the {} socket. Stand clear.".format(
            HOVER_MM, SIDE_NAME[name]))
        pipette.move_to(well.top(z=HOVER_MM))
        hold(
            "Nozzle is {:.0f} mm over {}, deck z = {} mm. LOOK: is it centred? "
            "Same error over BOTH sockets -> Labware Position Check. "
            "Error over this one only -> edit wells.{}.x/.y in the JSON.".format(
                HOVER_MM, SIDE_NAME[name], deck_z(well, HOVER_MM), name))

    def pick_up_from(name):
        well = dock[name]
        hold("Next: press onto the {} socket to pick up. The enclosure must be "
             "IN that socket.".format(SIDE_NAME[name]))
        pipette.pick_up_tip(well)
        pipette.move_to(well.top(z=LIFT_MM))
        hold("Picked up from {} and lifted {:.0f} mm. LOOK: is the enclosure "
             "actually on the nozzle, and hanging straight?".format(
                 SIDE_NAME[name], LIFT_MM))

    def release_into(name):
        well = dock[name]
        hold("Next: set the enclosure down into the {} socket, releasing at "
             "deck z = {} mm.".format(SIDE_NAME[name], deck_z(well, RELEASE_FROM_TOP_MM)))
        pipette.drop_tip(well.top(z=RELEASE_FROM_TOP_MM))
        pipette.move_to(well.top(z=LIFT_MM))
        hold("Released into {}. LOOK: is it square in the socket, and did the "
             "nozzle come away cleanly?".format(SIDE_NAME[name]))

    protocol.comment("=" * 70)
    protocol.comment("MODE = {}   SIDE = {}   base in slot {}".format(
        MODE, SIDE, DOCK_SLOT))
    protocol.comment("socket rim is {} mm above the deck".format(deck_z(dock["A1"], 0.0)))
    protocol.comment("a pick-up presses about 10 mm past the rim, i.e. to ~{} mm -- "
                     "which is the press depth the hand-tuned runs settled on".format(
                         deck_z(dock["A1"], -10.0)))
    protocol.comment("=" * 70)

    protocol.home()

    if MODE == "shuttle":
        protocol.comment("SHUTTLE: the enclosure must START in the LEFT (A1) socket.")
        hover_over("A1")
        pick_up_from("A1")
        hover_over("A2")          # look at the new side before committing to it
        release_into("A2")
        pick_up_from("A2")
        release_into("A1")
        protocol.comment("Shuttle complete -- enclosure back in LEFT (A1).")
    else:
        for name in (["A1", "A2"] if SIDE == "BOTH" else [SIDE]):
            hover_over(name)
            if MODE == "inplace":
                pick_up_from(name)
                release_into(name)

    protocol.home()
    protocol.comment("Done. Nothing is on the nozzle.")
