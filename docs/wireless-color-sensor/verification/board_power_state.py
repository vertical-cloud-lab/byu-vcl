from machine import ADC, Pin
import time
for label, mk in (("ADC(3)", lambda: ADC(3)), ("ADC(Pin(29))", lambda: ADC(Pin(29)))):
    try:
        Pin(25, Pin.OUT, value=1); time.sleep(0.1)
        a = mk(); raw = sum(a.read_u16() for _ in range(32)) / 32
        print("%-14s raw=%8.0f  ->  %.3f V" % (label, raw, raw * 3.3 * 3 / 65535))
    except Exception as e:
        print("%-14s failed: %r" % (label, e))
print("VBUS:", bool(Pin("WL_GPIO2", Pin.IN).value()))
