"""Power-path check for the wireless colour sensor's Pico W.

Run this ON THE BOARD, over USB, when it has gone silent and the question is
whether the cause is the battery, the LiPo SHIM soldering, or something else:

    mpremote connect id:e6647c15673a2438 run board_power_check.py

Needs no credentials for stages 1-4.  Stage 5 associates with wifi using the
board's own ``my_secrets.py`` and is the one that matters, because it measures
the supply rail *while the radio keys up* -- the moment a marginal cell or a
marginal joint actually fails.  A board that looks perfectly healthy at idle can
brown out here, and that is invisible from the outside: the Pico's buck-boost
regulator holds 3V3 (and therefore both indicator LEDs) steady well below the
point where the CYW43 can be supported.

Reference for the pin assignments -- Pimoroni, on which pins the SHIM uses:
https://forums.pimoroni.com/t/pico-lipo-shim-used-pins/21995
  pin 39 VSYS     "used to power the PICO"
  pin 37 3V3_EN   "turns the PICO on off via the button on the shim"
  pin 35/34 ADC_VREF / GP28  "used for battery state"
"""

import sys
import time

import machine

# Pico's documented VSYS sense divider: GP29/ADC3 sits on a 3:1 network.
VSYS_DIVIDER = 3.0
ADC_FULL_SCALE = 65535
ADC_REF_V = 3.3

# A single 3.7 V LiPo.  Under load the usable floor is higher than the
# protection cutoff, because the radio's transmit bursts pull the cell down.
CELL_FULL_V = 4.05
CELL_NOMINAL_V = 3.70
CELL_LOW_V = 3.40
CELL_CRITICAL_V = 3.20


def _rule(title):
    print("\n" + "-" * 62)
    print(title)
    print("-" * 62)


def stage1_identity():
    _rule("STAGE 1 -- what is actually running")
    uid = "".join("{:02x}".format(b) for b in machine.unique_id())
    print("  unique_id : {}".format(uid))
    print("  machine   : {}".format(sys.implementation._machine))
    print("  build     : {}".format(getattr(sys.implementation, "_build", "?")))
    print("  version   : {}".format(".".join(str(n) for n in sys.implementation.version[:3])))
    if "Pico W" not in sys.implementation._machine:
        print("  FAIL  this is not the Pico W build -- there is no wifi stack here")
        return False
    print("  PASS  Pico W build, so a wifi stack exists")
    return True


def _read_vsys():
    """Read VSYS through the 3:1 divider on ADC3.

    On the Pico W, GP29 is shared with the CYW43's SPI, so this is only
    trustworthy with the radio down.  WL_GPIO1 forces the SMPS into PWM mode,
    which removes the ripple that otherwise makes the reading wander.
    """
    try:
        smps = machine.Pin("WL_GPIO1", machine.Pin.OUT)
        smps.high()
        time.sleep_ms(20)
    except Exception:
        smps = None
    try:
        adc = machine.ADC(3)
        samples = sorted(adc.read_u16() for _ in range(21))
        raw = samples[len(samples) // 2]  # median, to shrug off SMPS ripple
    finally:
        if smps is not None:
            smps.low()
    return raw, raw * ADC_REF_V / ADC_FULL_SCALE * VSYS_DIVIDER


def stage2_supply_rail():
    _rule("STAGE 2 -- supply rail (VSYS) at idle")
    raw, volts = _read_vsys()
    print("  ADC3 raw  : {}".format(raw))
    print("  VSYS      : {:.3f} V".format(volts))
    if volts > 4.4:
        print("  PASS  above 4.4 V -- external 5 V is reaching VBUS.")
        print("        So the board is genuinely on external power, not just docked.")
        return "external", volts
    if volts < 2.0:
        print("  FAIL  implausibly low; suspect the VSYS or GND joint on the SHIM")
        return "broken", volts
    print("  note  under 4.4 V -- running from the cell, NOT from external power.")
    print("        If it is sitting on the wireless dock, the Qi link is not")
    print("        delivering.  That link is all-or-nothing: check that the")
    print("        transmitter's blue LED and the SHIM's red LED are BOTH lit.")
    return "battery", volts


def stage3_cell_voltage(rail_state, vsys):
    _rule("STAGE 3 -- cell charge")
    if rail_state == "external":
        print("  SKIP  external power is present, so VSYS reflects the 5 V input,")
        print("        not the cell.  Unplug external power and re-run to grade")
        print("        the battery itself.")
    else:
        print("  cell  : {:.3f} V  (VSYS is fed from the cell when unplugged)".format(vsys))
        if vsys >= CELL_FULL_V:
            print("  PASS  effectively full")
        elif vsys >= CELL_NOMINAL_V:
            print("  PASS  healthy")
        elif vsys >= CELL_LOW_V:
            print("  WARN  low -- enough to hold 3V3 and light both LEDs, but the")
            print("        radio's transmit bursts may brown the board out")
        elif vsys >= CELL_CRITICAL_V:
            print("  FAIL  nearly flat -- wifi will not associate reliably")
        else:
            print("  FAIL  flat, or VSYS is not connected through the SHIM")

    # The SHIM also brings out a battery-state line on GP28/ADC2.  Reported raw
    # because the divider ratio on that net is not documented by Pimoroni; use
    # it as a relative trend between runs, not as an absolute voltage.
    try:
        raw = machine.ADC(2).read_u16()
        print("  GP28 (SHIM battery-state line) raw={} -> {:.3f} V at the pin".format(
            raw, raw * ADC_REF_V / ADC_FULL_SCALE))
        print("        (relative trend only -- divider ratio unconfirmed)")
    except Exception as exc:
        print("  GP28 unreadable: {!r}".format(exc))


def stage4_vbus_sense():
    _rule("STAGE 4 -- VBUS present?")
    try:
        vbus = machine.Pin("WL_GPIO2", machine.Pin.IN)
        present = bool(vbus.value())
        print("  WL_GPIO2  : {}".format(present))
        if present:
            print("  PASS  external 5 V is present on VBUS (USB or an active Qi link)")
        else:
            print("  note  no external 5 V.  On the dock, this means the Qi link is")
            print("        NOT active -- reseat the sensor and confirm both LEDs.")
        return present
    except Exception as exc:
        print("  could not read WL_GPIO2: {!r}".format(exc))
        return None


def stage5_radio_under_load(rail_state):
    _rule("STAGE 5 -- does the rail hold while the radio keys up?")
    try:
        import my_secrets
    except ImportError:
        print("  SKIP  no my_secrets.py on the board -- cannot associate")
        return
    ssid = getattr(my_secrets, "SSID", None) or getattr(my_secrets, "WIFI_SSID", None)
    pw = getattr(my_secrets, "PASSWORD", None) or getattr(my_secrets, "WIFI_PASSWORD", None)
    if not ssid:
        print("  SKIP  my_secrets.py has no SSID field this script recognises")
        return

    import network

    before_raw, before = _read_vsys()
    print("  VSYS before : {:.3f} V".format(before))

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, pw)

    lowest = before
    for i in range(30):
        time.sleep(1)
        if wlan.isconnected():
            break
        # Only sampled while disconnected: once the radio is up, ADC3 is
        # contended by the CYW43 SPI and the reading stops being meaningful.
        _, v = _read_vsys()
        lowest = min(lowest, v)
        if i % 5 == 0:
            print("    t+{:>2}s  status={}  VSYS={:.3f} V".format(i + 1, wlan.status(), v))

    print("  lowest VSYS seen during association: {:.3f} V".format(lowest))
    sag = before - lowest
    print("  sag         : {:.3f} V".format(sag))

    # Judge on the absolute floor as well as the sag.  A board that is *already*
    # browned out when the baseline is taken shows a sag of zero, so sag alone
    # would clear it of a power fault -- exactly backwards.
    collapsed = lowest < CELL_LOW_V and rail_state != "external"
    sagged = sag > 0.30

    if wlan.isconnected():
        print("  PASS  associated -- IP {}".format(wlan.ifconfig()[0]))
        if sagged or collapsed:
            print("  WARN  but the rail reached {:.2f} V getting there. It will".format(lowest))
            print("        fail intermittently as the cell discharges further.")
    else:
        print("  FAIL  did not associate.  status={}".format(wlan.status()))
        if collapsed:
            print("  ==>   the rail was at {:.2f} V, below the {:.2f} V the radio".format(
                lowest, CELL_LOW_V))
            print("        needs.  This is a POWER problem: a flat cell, or a")
            print("        marginal VSYS/GND joint on the SHIM.  Charge it on a")
            print("        WIRED micro-USB charger -- the Qi link is all-or-nothing")
            print("        and fails silently if the coil is not seated.")
        elif sagged:
            print("  ==>   the rail sagged {:.2f} V while trying.  This is a POWER".format(sag))
            print("        problem: a flat cell, or a marginal VSYS/GND joint on the")
            print("        SHIM that is fine at idle and not under a 150 mA burst.")
        else:
            print("  ==>   the rail held at {:.2f} V throughout, so this is NOT a".format(lowest))
            print("        power problem.  Look at the SSID/password in my_secrets.py,")
            print("        and note that MicroPython does WPA2-PSK on 2.4 GHz only --")
            print("        it cannot join an enterprise network such as eduroam.")
    wlan.active(False)


def main():
    print("=" * 62)
    print("wireless colour sensor -- power path check")
    print("=" * 62)
    if not stage1_identity():
        return
    rail_state, vsys = stage2_supply_rail()
    if rail_state == "broken":
        return
    stage3_cell_voltage(rail_state, vsys)
    stage4_vbus_sense()
    stage5_radio_under_load(rail_state)
    print("\n" + "=" * 62)
    print("done")


main()
