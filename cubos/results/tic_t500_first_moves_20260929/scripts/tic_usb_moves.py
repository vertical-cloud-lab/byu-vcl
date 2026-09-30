"""Run as root. Drive the plunger from the Tic itself over USB, bypassing the
Arduino's STEP/DIR wires, then put the Tic back exactly as it was.

1. save the current settings (STEP/DIR mode)
2. load a copy with control_mode: serial and command_timeout: 0
3. exit safe start, energize, and make four moves: +1 mm, back, +5 mm, back
   (796 microsteps = 1 mm at 1/8 step), polling position/velocity/VIN
4. reload the saved settings and check they read back byte-identical
"""
import os, re, subprocess, sys, time
OUT = sys.argv[1]
TIC = f"/home/{os.environ['SUDO_USER']}/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd"
log = open(f"{OUT}/tic_usb_moves.log", "w")

def say(msg):
    line = f"{time.strftime('%H:%M:%S')}.{int(time.time() % 1 * 1000):03d}  {msg}"
    print(line, flush=True); log.write(line + "\n"); log.flush()

def tic(*a, check=True):
    r = subprocess.run([TIC, *a], capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"ticcmd {' '.join(a)} -> {r.returncode}: {r.stderr.strip()}")
    return r.stdout

def field(s, name):
    m = re.search(rf"^{name}:\s+(.*)$", s, re.M)
    return m.group(1).strip() if m else "?"

def errors_now(s):
    m = re.search(r"Errors currently stopping the motor:(.*?)\nErrors that occurred", s, re.S)
    return " ".join(x.strip(" -") for x in m.group(1).strip().splitlines()) if m else "?"

def state(tag=""):
    s = tic("--status")
    say(f"{tag:<10} pos={field(s, 'Current position'):>6}  vel={field(s, 'Current velocity'):>9}  "
        f"target={field(s, 'Target'):<28} VIN={field(s, 'VIN voltage'):<9} energized={field(s, 'Energized')}  "
        f"errors_now={errors_now(s)}")
    return s

def move_to(pos, timeout=40):
    tic("--position", str(pos))
    say(f"--position {pos} sent")
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = state("moving")
        if field(s, "Current position") == str(pos) and field(s, "Current velocity") == "0":
            say(f"reached {pos} in {time.time() - t0:.1f} s")
            return
        time.sleep(0.25)
    say(f"TIMEOUT waiting for {pos}")

saved = f"{OUT}/settings_saved_stepdir.txt"
tic("--get-settings", saved)
temp = f"{OUT}/settings_temp_serial.txt"
txt = open(saved).read()
txt = re.sub(r"^control_mode: .*$", "control_mode: serial", txt, flags=re.M)
txt = re.sub(r"^command_timeout: .*$", "command_timeout: 0", txt, flags=re.M)
open(temp, "w").write(txt)
say("saved settings; loading temporary copy with control_mode: serial, command_timeout: 0")
try:
    tic("--settings", temp)
    time.sleep(0.5)
    state("loaded")
    tic("--halt-and-set-position", "0")
    tic("--max-speed", "8000000")   # 800 microsteps/s = 1 mm/s at 1/8 step
    tic("--max-accel", "800000")    # 8000 microsteps/s^2
    tic("--max-decel", "800000")
    tic("--exit-safe-start")
    tic("--energize")
    time.sleep(0.3)
    state("ready")
    for target in (796, 0, 3980, 0):
        move_to(target)
        time.sleep(2.0)
finally:
    tic("--settings", saved)
    time.sleep(0.5)
    back = f"{OUT}/settings_restored_readback.txt"
    tic("--get-settings", back)
    same = open(back).read() == open(saved).read()
    say(f"restored saved settings; read-back byte-identical: {same}")
    s = tic("--status", "--full")
    say(f"after restore: energized={field(s, 'Energized')}  step mode={field(s, 'Step mode')}  "
        f"limit={field(s, 'Current limit')}  errors_now={errors_now(s)}")
