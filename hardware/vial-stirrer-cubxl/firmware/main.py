# main.py -- single-vial stirrer, closed-loop stirring on a Seeed XIAO RP2040.
#
# UNTESTED SKETCH: nothing has been built yet. MicroPython >= 1.22.
#
# Follows the Pioreactor's stirring job (pioreactor/background_jobs/stirring.py at
# 0ae14c0), moved onto the module so the host only sends a target rpm:
#   - a 2-wire fan, PWM'd at 200 Hz through a low-side N-MOSFET (Pioreactor: GPIO17,
#     software PWM, pwm_hz=200),
#   - rpm from a Hall sensor that sees the two opposite-pole magnets go by: one
#     pulse per turn (Pioreactor: DRV5021A3 switch on GPIO21, falling edges),
#   - an additive P controller (each step clamped to +-7.5 % duty), a full-power
#     kick from standstill, and a kick when it stalls.
# Changes from the Pioreactor: a bipolar latch (US1881) instead of the DRV5021,
# because the sensor sits beside the magnets rather than over them; updates
# every 2 s instead of 23 s; and a setpoint ramp, so the bar is not asked to
# jump speed (Edison coupling summary in outputs/issue-169-magnetic-stirrer/).
#
# Wiring (see ../README.md):
#   D1 (GP27) -> 100 R -> MOSFET gate; 10 k gate-to-source pull-down
#   D2 (GP28) <- US1881 output (open drain; internal pull-up + 10 k to 3V3)
#   5V (VBUS) -> fan red, US1881 VDD;  fan black -> MOSFET drain;  source -> GND
#   1N5819 across the fan, cathode to 5V
#
# USB serial, one command per line:
#   RPM <n>   target in rpm, 0 stops. The setpoint ramps at RAMP rpm/s
#   STOP      same as RPM 0
#   ?         status line: target, setpoint, measured rpm, duty, stalled
#   ID        firmware name and version
import sys
import time

import select
from machine import PWM, Pin, disable_irq, enable_irq

GATE_PIN, HALL_PIN = 27, 28
PWM_HZ = 200                 # as the Pioreactor
PULSES_PER_REV = 1           # one latch toggle pair per turn (opposite-pole magnets)
KP = 0.0002                  # duty fraction per rpm of error, per update. The Pioreactor's
                             # Kp is 0.005 %/rpm, but it starts from a calibrated duty; this
                             # starts from DC_START, so it needs more gain. Tune on the bench
MAX_STEP = 0.075             # Pioreactor clamps each update to 7.5 points
UPDATE_S = 2.0               # control update period
RAMP = 100.0                 # setpoint ramp, rpm per second
DC_START = 0.30              # Pioreactor initial_duty_cycle = 30
RPM_MIN, RPM_MAX = 100, 2000  # Pioreactor: ~125 rpm practical floor, 2000 cap

pwm = PWM(Pin(GATE_PIN))
pwm.freq(PWM_HZ)
pwm.duty_u16(0)
hall = Pin(HALL_PIN, Pin.IN, Pin.PULL_UP)

_count = 0


def _edge(_pin):
    global _count
    _count += 1


hall.irq(trigger=Pin.IRQ_FALLING, handler=_edge)


def set_duty(d):
    pwm.duty_u16(int(max(0.0, min(1.0, d)) * 65535))


def kick(after):
    """Full power briefly to break the fan free, then drop to `after`."""
    set_duty(1.0)
    time.sleep_ms(500)
    set_duty(after)


target = 0.0
setpoint = 0.0
duty = 0.0
rpm = 0.0
stalled = False
zero_updates = 0
poll = select.poll()
poll.register(sys.stdin, select.POLLIN)
line = ""
last = time.ticks_ms()


def status():
    return "target=%d setpoint=%d rpm=%d duty=%.3f stalled=%d" % (target, setpoint, rpm, duty, stalled)


def handle(cmd):
    global target, stalled
    parts = cmd.strip().split()
    if not parts:
        return
    word = parts[0].upper()
    if word == "RPM" and len(parts) == 2:
        t = float(parts[1])
        target = 0.0 if t <= 0 else max(RPM_MIN, min(t, RPM_MAX))
        stalled = False
        print("ok", status())
    elif word == "STOP":
        target = 0.0
        print("ok", status())
    elif word == "?":
        print(status())
    elif word == "ID":
        print("vial-stirrer 0.1 (byu-vcl #169)")
    else:
        print("err unknown command:", cmd.strip())


while True:
    while poll.poll(0):
        ch = sys.stdin.read(1)
        if ch in ("\n", "\r"):
            handle(line)
            line = ""
        else:
            line += ch

    now = time.ticks_ms()
    dt = time.ticks_diff(now, last) / 1000
    if dt < UPDATE_S:
        time.sleep_ms(10)
        continue
    last = now

    irq = disable_irq()
    n, _count = _count, 0
    enable_irq(irq)
    rpm = n / PULSES_PER_REV / dt * 60

    if target <= 0:
        setpoint, duty, zero_updates = 0.0, 0.0, 0
        set_duty(0)
        continue

    if setpoint == 0:                       # starting from rest
        setpoint = min(target, RPM_MIN)
        duty = DC_START
        kick(duty)
        continue

    step = RAMP * dt
    setpoint = min(target, setpoint + step) if setpoint < target else max(target, setpoint - step)

    if rpm < 1:                             # spinning nothing: kick, give up after 5 tries
        zero_updates += 1
        if zero_updates > 5:
            stalled, target = True, 0.0
            set_duty(0)
            print("err stalled: no Hall pulses")
            continue
        duty = min(duty * 1.01, 0.60)       # Pioreactor's "avoid the death spiral" cap
        set_duty(0)
        time.sleep_ms(750)
        kick(duty)
        continue
    zero_updates = 0

    delta = max(-MAX_STEP, min(MAX_STEP, KP * (setpoint - rpm)))
    duty = max(0.0, min(1.0, duty + delta))
    set_duty(duty)
