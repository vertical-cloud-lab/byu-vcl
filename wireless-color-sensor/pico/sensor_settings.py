"""Per-request AS7341 gain and integration time for the Pico W's main.py (MicroPython).

Copy this file to the board's root, next to main.py, and apply main.py.patch.
A read command may then carry an optional "settings" object beside "command":

    {"command": {"R": 0, "Y": 0, "B": 0}, "experiment_id": "...",
     "settings": {"gain": 512, "atime": 200, "astep": 999}}

Any key left out keeps its default. The reading is taken with those settings
and the defaults are put back straight afterwards, so a command without
"settings" reads exactly as every reading before this file did. The reply
carries "sensor_settings": what was asked for, and what the chip itself
reports it used (ASTATUS, latched with the counts).

Why the default gain is 256x, not the 128x main.py asks for: Sensor() passes its
gain *factor* (128) to as7341.set_again(), which wants a *code* (0-10) and
silently ignores anything out of range. So the chip has always stayed at its
power-on AGAIN, code 9 = 256x (datasheet DS000504, CFG1 register 0xAA). Setting
256x explicitly keeps every new reading comparable with the old ones.
"""

GAINS = (0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512)    # index = AGAIN code 0..10
DEFAULT = {"gain": 256, "atime": 200, "astep": 999}     # 2 x 558.8 ms per 8-channel reading
STEP_US = 2.78
SMUX = ("F1F4CN", "F5F8CN")                             # the same two halves as Sensor.all_channels


def gain_code(gain):
    for code, g in enumerate(GAINS):
        if gain == g and not isinstance(gain, bool):
            return code
    raise ValueError("gain must be one of 0.5, 1, 2, 4, ... 512; got %r" % (gain,))


def _int_in(name, value, lo, hi):
    if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
        raise ValueError("%s must be an integer %d-%d; got %r" % (name, lo, hi, value))
    return value


def parse(settings):
    """The full settings to use for one reading, from a command's optional object."""
    s = dict(DEFAULT)
    if settings is None:
        return s
    if not isinstance(settings, dict):
        raise ValueError("settings must be an object")
    for key, value in settings.items():
        if key not in DEFAULT:
            raise ValueError("unknown setting %r (gain, atime, astep)" % (key,))
        s[key] = value
    gain_code(s["gain"])
    _int_in("atime", s["atime"], 0, 255)
    _int_in("astep", s["astep"], 0, 65534)
    return s


def apply(chip, s):
    """Write the settings to the chip. ``chip`` is the as7341.AS7341 object (Sensor().sensor)."""
    chip.set_again(gain_code(s["gain"]))
    chip.set_atime(s["atime"])
    chip.set_astep(s["astep"])


def full_scale(s):
    return min(65535, (s["atime"] + 1) * (s["astep"] + 1))


def _astatus(chip):
    """The ASTATUS byte the driver's bulk read latched with the counts, or None.

    as7341.py reads ASTATUS and the six counts in one transfer into a private
    buffer and returns only the counts. MicroPython does not mangle __names;
    CPython (the test) does, so try both spellings.
    """
    buf = getattr(chip, "__buffer13", None)
    if buf is None:
        buf = getattr(chip, "_AS7341__buffer13", None)
    return None if buf is None else buf[0]


def read(chip, s):
    """One 8-channel reading, the same two SMUX halves as Sensor.all_channels.

    Returns (counts, status). status records, per half, the gain code the chip
    says it used and whether it saturated (analogue: ASTATUS bit 7; digital: a
    count at full scale).
    """
    counts, halves = [], []
    top = full_scale(s)
    for selection in SMUX:
        chip.start_measure(selection)
        f = chip.get_spectral_data()
        a = _astatus(chip)
        counts.extend(f[:4])
        halves.append({"again_code": None if a is None else a & 0x0F,
                       "analog_saturated": None if a is None else bool(a & 0x80),
                       "digital_saturated": max(f[:4]) >= top})
    status = {"gain": s["gain"], "atime": s["atime"], "astep": s["astep"],
              "integration_ms": round((s["atime"] + 1) * (s["astep"] + 1) * STEP_US / 1000, 2),
              "full_scale": top, "halves": halves,
              "saturated": any(h["analog_saturated"] or h["digital_saturated"] for h in halves)}
    return counts, status
