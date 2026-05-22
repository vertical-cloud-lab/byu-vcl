# BYU-VCL OT-2 Wireless Color Sensor (WCS) Protocols

Test protocols for driving the Acceleration Consortium-style wireless color
sensor (WCS) on an Opentrons OT-2 using a `p20_single_gen2` pipette on the
right mount.

These scripts were derived from the Acceleration Consortium's
[`ac-dev-lab`](https://github.com/AccelerationConsortium/ac-dev-lab/blob/e85dd45e19480068f9e8323dad1a6294dabe8075/src/ac_training_lab/ot-2/_scripts/prefect/device.py)
reference and packaged as standalone OT-2 protocols you can download and
run.

## Contents

| File | Purpose |
| --- | --- |
| `labware/byu_color_sensor_charging_port.json` | Custom labware definition for the WCS charging port (2 wells, treated as a tip rack so the pipette can "pick up" the sensor). Also available as an inline `dict` inside each protocol so the protocols are self-contained. |
| `wcs_actions.py` | Reusable, importable helper module. Wraps the low-level Opentrons API calls into named actions (`pick_up_wcs`, `return_wcs`, `move_wcs_to`, `pick_up_and_return_wcs`, `pick_up_move_and_return_wcs`). Use this when authoring new protocols. |
| `protocol_pick_and_place.py` | **Test 1** — pick the WCS up and put it back down. Self-contained, single-file protocol. |
| `protocol_pick_move_return.py` | **Test 2** — pick the WCS up, move it over a 96-well plate, dwell, and return it. Self-contained, single-file protocol. |

## Deck layout

| Slot | Labware |
| --- | --- |
| 1 (Test 2 only) | `corning_96_wellplate_360ul_flat` |
| 10 | BYU wireless color sensor charging port (custom) |

The wireless color sensor sits in well **A2** of the charging port; well A1
is left empty (matches the AC reference).

## Pipette

* Right mount: `p20_single_gen2`

## Running

The two `protocol_*.py` files are self-contained: they embed the custom
labware definition inline, so you can download and run either file
directly without any extra setup.

### Upload to the Opentrons App (recommended for end users)

1. Open the Opentrons App and connect to the OT-2.
2. Go to *Protocols* → *Import* and select either
   `protocol_pick_and_place.py` or `protocol_pick_move_return.py`.
3. Calibrate as prompted and run.

### Simulate locally

```bash
pip install opentrons
cd ot2/wireless_color_sensor
opentrons_simulate protocol_pick_and_place.py
opentrons_simulate protocol_pick_move_return.py
```

### Run directly on the OT-2 over SSH

```bash
scp protocol_pick_and_place.py root@<ot2-ip>:/data/user_storage/
ssh root@<ot2-ip> "opentrons_execute /data/user_storage/protocol_pick_and_place.py"
```

## Extending

The reusable functions live in `wcs_actions.py`. To add a new test
protocol that reuses the packaged actions (instead of inlining everything),
import the helpers and call them from a standard OT-2 `run(protocol)`
function. When running this way, keep `wcs_actions.py` and the `labware/`
folder next to your new protocol (or copy them onto the OT-2 via SSH so
that `import wcs_actions` resolves):

```python
from wcs_actions import load_wcs_charging_port, pick_up_wcs, move_wcs_to, return_wcs

metadata = {"protocolName": "My WCS test", "apiLevel": "2.12"}

def run(protocol):
    charging_port = load_wcs_charging_port(protocol, slot=10)
    pipette = protocol.load_instrument(
        "p20_single_gen2", mount="right", tip_racks=[charging_port]
    )
    plate = protocol.load_labware("corning_96_wellplate_360ul_flat", 1)

    pick_up_wcs(pipette, charging_port)
    move_wcs_to(pipette, plate["B3"].top(z=-1.3))
    protocol.delay(seconds=2)
    return_wcs(pipette, charging_port)
```

## References

* AC reference protocol: [`ac-dev-lab .../prefect/device.py`](https://github.com/AccelerationConsortium/ac-dev-lab/blob/e85dd45e19480068f9e8323dad1a6294dabe8075/src/ac_training_lab/ot-2/_scripts/prefect/device.py)
* AC charging-port labware: [`ac_color_sensor_charging_port.json`](https://github.com/AccelerationConsortium/ac-dev-lab/blob/e85dd45e19480068f9e8323dad1a6294dabe8075/src/ac_training_lab/ot-2/_scripts/ac_color_sensor_charging_port.json)
* AC successful pick-up / move / return demo: [comment on issue #64](https://github.com/AccelerationConsortium/ac-dev-lab/issues/64#issuecomment-2427523115)
