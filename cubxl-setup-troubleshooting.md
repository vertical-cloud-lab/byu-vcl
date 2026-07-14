# CubXL setup: gantry connection troubleshooting

This note summarizes likely causes and troubleshooting for the issue reported during CubXL calibration:

> "I was able to complete Gantry Bring-Up using UGS, but my computer wouldn't connect to the Gantry when trying to run the calibration commands."

## Relevant official CubOS docs

- Getting Started → setup sequence and bring-up dependency: https://cubos.readthedocs.io/en/latest/getting-started/
- Calibration → preflight requires a reachable serial connection and correct gantry YAML: https://cubos.readthedocs.io/en/latest/calibration/
- Configuration (Gantry YAML) → `serial_port` must match active device: https://cubos.readthedocs.io/en/latest/configuration/
- Gantry Bring-Up → GRBL status expectations (`$10=0`, `WPos`, homing/jog direction): https://cubos.readthedocs.io/en/latest/admin/gantry-bring-up/

## Most likely cause

Given UGS worked but `setup/calibrate_gantry.py` did not connect, the most likely issue is **serial connection mismatch or contention**:

1. `serial_port` in the gantry YAML points to the wrong device (port changed after reconnect/reboot).
2. UGS (or another serial monitor) still has the port open, so CubOS cannot claim it.
3. OS permissions/driver assignment changed between UGS and Python runtime.

## Recommended troubleshooting steps

1. **Close UGS completely** before running CubOS scripts.
2. **Confirm active serial device** and update gantry YAML `serial_port` if needed.
3. Verify CubOS environment is active and run calibration exactly as documented:

   ```bash
   PYTHONPATH=src python setup/calibrate_gantry.py configs/gantry/cub_xl_asmi.yaml
   ```

4. If connection still fails, run Gantry Bring-Up checks to confirm controller state:
   - `$10=0` and status includes `WPos`
   - homing/jog behavior matches CubOS frame (+X right, +Y back, +Z up)
5. Re-run calibration and then run the interactive jog test:

   ```bash
   PYTHONPATH=src python setup/hello_world.py --gantry configs/gantry/cub_xl_asmi.yaml
   ```

## Follow-up questions to unblock diagnosis

1. What exact error text/trace do you get from `setup/calibrate_gantry.py`?
2. Which OS are you using (Windows/macOS/Linux)?
3. What is the current `serial_port` value in your gantry YAML?
4. Are you able to reconnect immediately if you close UGS and retry calibration?
5. Did the COM/tty device name change after unplugging/replugging USB?

## Quick fix checklist

- [ ] Close any app using the serial port (UGS, serial monitor, IDE terminals).
- [ ] Replug USB and identify the current COM/tty port.
- [ ] Update `serial_port` in gantry YAML to that exact port.
- [ ] Re-run calibration, then run `hello_world.py` jog check.
