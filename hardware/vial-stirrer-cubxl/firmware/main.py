# main.py -- single-vial stirrer, closed-loop fan speed on a Seeed XIAO RP2040.
#
# UNTESTED SKETCH (nothing has been built yet). MicroPython >= 1.22.
#
# Same idea as the Pioreactor's stirring job (pioreactor/background_jobs/stirring.py):
# drive a PC fan that carries two magnets, read its tachometer, and close the loop
# on rpm. Here the loop runs on the module itself, so the host only sends a target.
#
# Wiring (see ../README.md):
#   D0  (GP26) -> fan PWM input (blue wire), 25 kHz
#   D1  (GP27) <- fan tach (green/yellow wire), open collector, 10 k pull-up to 3V3
#   D2  (GP28) -> gate of the low-side MOSFET in the fan's ground (true stop)
#   5V  (VBUS) -> fan +5 V (red), GND -> MOSFET source; fan black -> MOSFET drain
#
# USB serial, one command per line:
#   RPM <n>   set the target in rpm (0 stops). The setpoint ramps at RAMP rpm/s
#   STOP      same as RPM 0
#   ?         one status line: target, setpoint, measured rpm, duty, flags
#   ID        firmware name and version
import sys
import time

import select
from machine import PWM, Pin, disable_irq, enable_irq

PWM_PIN, TACH_PIN, EN_PIN = 26, 27, 28
PWM_HZ = 25_000            # Intel 4-wire fan spec
PULSES_PER_REV = 2         # standard PC-fan tach
RAMP = 150.0               # rpm per second; ramp so the bar stays coupled
KP, KI = 0.00025, 0.0006   # duty per rpm error, per rpm*s; tune on the bench
DUTY_MIN = 0.20            # below this many 4-wire fans run at their floor speed
RPM_MAX = 2000             # safety ceiling; the bar decouples long before the fan's max
PERIOD = 0.25              # control period, s

pwm = PWM(Pin(PWM_PIN))
pwm.freq(PWM_HZ)
en = Pin(EN_PIN, Pin.OUT, value=0)
tach = Pin(TACH_PIN, Pin.IN, Pin.PULL_UP)

_count = 0


def _edge(_pin):
    global _count
    _count += 1


tach.irq(trigger=Pin.IRQ_FALLING, handler=_edge)


def set_duty(d):
    pwm.duty_u16(int(max(0.0, min(1.0, d)) * 65535))


target = 0.0
setpoint = 0.0
integral = 0.0
duty = 0.0
rpm = 0.0
stalled = False
stall_t = 0.0
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
        target = max(0.0, min(float(parts[1]), RPM_MAX))
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
    # read any complete command lines without blocking the loop
    while poll.poll(0):
        ch = sys.stdin.read(1)
        if ch in ("\n", "\r"):
            handle(line)
            line = ""
        else:
            line += ch

    now = time.ticks_ms()
    dt = time.ticks_diff(now, last) / 1000
    if dt < PERIOD:
        time.sleep_ms(5)
        continue
    last = now

    irq = disable_irq()
    n, _count = _count, 0
    enable_irq(irq)
    rpm = n / PULSES_PER_REV / dt * 60

    # ramp the setpoint toward the target
    step = RAMP * dt
    setpoint = min(target, setpoint + step) if setpoint < target else max(target, setpoint - step)

    if setpoint <= 0:
        en.value(0)
        set_duty(0)
        duty, integral = 0.0, 0.0
        continue

    en.value(1)
    err = setpoint - rpm
    integral = max(-1.0 / KI, min(1.0 / KI, integral + err * dt))   # anti-windup
    duty = max(DUTY_MIN, min(1.0, KP * err + KI * integral))
    set_duty(duty)

    # stall: full duty for 3 s with no tach pulses -> cut power and flag it
    if rpm < 1 and duty >= 0.99:
        stall_t += dt
        if stall_t > 3:
            stalled, target, setpoint = True, 0.0, 0.0
            en.value(0)
            set_duty(0)
            print("err stalled")
    else:
        stall_t = 0.0
