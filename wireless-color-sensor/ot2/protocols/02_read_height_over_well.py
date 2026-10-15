"""02 -- READ HEIGHT: hold the sensor over a 96-well plate well.

Drag this file into the Opentrons App and run it. Nothing to install.

WHAT IT IS FOR
--------------
Picks the colour-sensor enclosure up off its base, carries it to one well of a
96-well plate, and stops at a series of heights with a pause at each, so you
can decide by eye -- and by taking a reading -- which height to use.

Heights are given RELATIVE TO THE WELL RIM, not as an absolute deck Z:

    z = +10  ->  aperture 10 mm ABOVE the rim
    z =   0  ->  aperture level with the rim
    z = -1.3 ->  aperture 1.3 mm BELOW the rim  (the AccelerationConsortium's
                 number, from the setup that actually produced good colour data)

That is the point of doing it through labware. Re-calibrate, swap the plate, or
move it to another slot, and the same number still means the same distance from
the liquid -- no constant in this file has to change.

HOW TO USE IT -- change MODE, below, and re-upload:

  1. MODE = "dry"     <- DO THIS FIRST. No pick-up. The bare nozzle visits the
                         ladder heights. Because the enclosure is 84 mm long, a
                         bare nozzle ends up EXACTLY where the aperture will be
                         once it is carried -- so this shows you the real
                         geometry at zero collision risk.
                         It cannot show you the whole ladder: with no tip on, a
                         P300 bottoms out at deck z 29.45 mm, which is about
                         +15 mm over the rim of a 96-well plate. Anything lower
                         is announced and skipped, and is only reachable in
                         MODE = "ladder" with the enclosure actually attached.
  2. MODE = "ladder"  <- the real thing: picks the enclosure up and steps down
                         through LADDER_Z_MM, pausing at each height.
  3. MODE = "hold"    <- goes straight to HOLD_Z_MM and waits there, so you can
                         fire a sensor read at that exact pose, then Resume.

THE LADDER STOPS ABOVE THE RIM ON PURPOSE
-----------------------------------------
LADDER_Z_MM below ends at +2 mm, not at the AC's -1.3 mm. Below the rim the
enclosure body is inside the plate's footprint and a couple of millimetres of
X/Y error becomes a collision instead of a bad reading. Watch the ladder down
to +2 first; if there is clearance to spare, add the lower values yourself.

WHY apiLevel 2.13 AND NOT SOMETHING NEWER
-----------------------------------------
Same reason as protocol 01: on this robot's software (8.8.1) pick_up_tip from
the 2-well dock raises "InvalidStoredData: ... less dense than an SBS 96
standard" at API 2.14 and above. 2.13 uses the older core and works. Labware
Position Check still applies its offsets to 2.13 protocols.
"""

from opentrons import protocol_api  # noqa: F401  (kept for editor autocomplete)

metadata = {
    "protocolName": "02 - read height over a 96-well plate",
    "author": "vertical-cloud-lab/byu-vcl",
    "description": (
        "Carry the colour-sensor enclosure to one well of a 96-well plate and "
        "step through read heights. Calibration aid -- no liquid handling."
    ),
    "apiLevel": "2.13",
}

# ======================================================================
#  EDIT THESE
# ======================================================================

MODE = "dry"            # "dry" | "ladder" | "hold"

PLATE_WELL = "C5"       # which well to sit over. C5 is near the middle of the
                        # plate, so the arm is well away from the deck edges.
PICKUP_WELL = "A1"      # which socket of the base to take the enclosure from:
                        # "A1" = LEFT, "A2" = RIGHT

# The ladder, in mm relative to the WELL RIM, highest first. Delete or add
# entries freely -- this list is exactly what the protocol will do.
LADDER_Z_MM = [30.0, 20.0, 15.0, 10.0, 7.0, 5.0, 3.0, 2.0]

HOLD_Z_MM = 5.0         # used by MODE = "hold": sit here and wait for a read

PLATE_SLOT = 1
PLATE_LOAD_NAME = "corning_96_wellplate_360ul_flat"
DOCK_SLOT = 10
SLOW = True             # 100 mm/s instead of the stock 400, so you can follow it

# ======================================================================
#  Below here you should not need to touch.
# ======================================================================

RELEASE_FROM_TOP_MM = -80.0   # where the nozzle lets go over the base socket
HALF_ANGLE_DEG = 20.0         # AS7341 field of view, typical half-angle

# A P300 GEN2 on the left mount with NO tip bottoms out at deck z = 29.45 mm --
# measured against opentrons 8.8.1, the robot's own version, by walking the
# commanded height down until the move went out of bounds. Carrying the 84 mm
# enclosure the same mount reaches 84 mm lower, so only the dry run is limited.
# 30.0 leaves a little margin.
DRY_MIN_DECK_Z = 30.0

# The charging base as Opentrons labware, embedded so this file is
# self-contained. Byte-for-byte the AccelerationConsortium definition, also
# saved beside this file as ac_color_sensor_charging_port.json.
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


def run(protocol):
    assert MODE in ("dry", "ladder", "hold"), "MODE must be dry/ladder/hold"
    assert PICKUP_WELL in ("A1", "A2"), "PICKUP_WELL must be A1 or A2"

    import math

    dock = protocol.load_labware_from_definition(DOCK_DEF, DOCK_SLOT)
    plate = protocol.load_labware(PLATE_LOAD_NAME, PLATE_SLOT)
    pipette = protocol.load_instrument("p300_single_gen2", "left", tip_racks=[dock])

    if SLOW:
        pipette.default_speed = 100

    well = plate[PLATE_WELL]
    rim_z = round(well.top().point.z, 2)          # rim height above the deck
    well_dia = round(well.diameter or 0.0, 2)     # None for square wells

    def hold(message):
        protocol.comment(message)
        protocol.pause(message)

    def spot_mm(z_above_rim):
        """Rough diameter of the sensor's footprint at the plane of the rim."""
        d = max(z_above_rim, 0.0)
        return round(2.0 * d * math.tan(math.radians(HALF_ANGLE_DEG)), 1)

    def visit(z):
        if MODE == "dry" and rim_z + z < DRY_MIN_DECK_Z:
            protocol.comment(
                "  z = {:+.1f} mm vs the rim | deck z = {:.2f} mm | SKIPPED in the dry "
                "run: a bare nozzle bottoms out at deck z {} mm. This height is only "
                "reachable with the 84 mm enclosure on, so check it in MODE = "
                "'ladder'.".format(z, rim_z + z, DRY_MIN_DECK_Z))
            return
        pipette.move_to(well.top(z=z))
        what = "aperture" if MODE != "dry" else "bare nozzle (stands in for the aperture)"
        protocol.comment(
            "  z = {:+.1f} mm vs the rim | deck z = {:.2f} mm | {} | "
            "footprint at the rim about {} mm across, well is {} mm".format(
                z, rim_z + z, what, spot_mm(z), well_dia))
        hold("Holding at z = {:+.1f} mm relative to the rim of {}. "
             "Look, or take a reading, then Resume.".format(z, PLATE_WELL))

    protocol.comment("=" * 70)
    protocol.comment("MODE = {}   well {} of {} in slot {}   base in slot {}".format(
        MODE, PLATE_WELL, PLATE_LOAD_NAME, PLATE_SLOT, DOCK_SLOT))
    protocol.comment("rim of {} is {} mm above the deck; well is {} mm across "
                     "and {} mm deep".format(
                         PLATE_WELL, rim_z, well_dia, round(well.depth, 2)))
    if MODE == "dry":
        protocol.comment("DRY RUN: nothing is picked up. Its job is the X/Y check -- "
                         "does the nozzle land over the well you meant? -- plus the "
                         "top of the ladder. The lower heights need the enclosure on.")
    protocol.comment("=" * 70)

    protocol.home()

    if MODE != "dry":
        hold("Next: pick the enclosure up from the {} socket. It must be IN that "
             "socket.".format("LEFT (A1)" if PICKUP_WELL == "A1" else "RIGHT (A2)"))
        pipette.pick_up_tip(dock[PICKUP_WELL])
        pipette.move_to(dock[PICKUP_WELL].top(z=40.0))
        hold("Picked up. LOOK: is the enclosure on the nozzle and hanging straight? "
             "Next move carries it over to {} in slot {}.".format(PLATE_WELL, PLATE_SLOT))

    heights = LADDER_Z_MM if MODE in ("dry", "ladder") else [HOLD_Z_MM]
    protocol.comment("Visiting {} height(s) over {}: {}".format(
        len(heights), PLATE_WELL, ", ".join("{:+.1f}".format(z) for z in heights)))

    for z in heights:
        visit(z)

    # Leave the plate before doing anything else.
    pipette.move_to(well.top(z=max(max(heights), 40.0)))

    if MODE != "dry":
        socket = dock[PICKUP_WELL]
        hold("Ladder finished. Next: carry the enclosure back and set it down in "
             "the {} socket.".format(PICKUP_WELL))
        pipette.drop_tip(socket.top(z=RELEASE_FROM_TOP_MM))
        pipette.move_to(socket.top(z=40.0))
        hold("Released into {}. LOOK: is it square in the socket?".format(PICKUP_WELL))

    protocol.home()
    protocol.comment("Done. Note the z you liked and tell it to the next protocol.")
