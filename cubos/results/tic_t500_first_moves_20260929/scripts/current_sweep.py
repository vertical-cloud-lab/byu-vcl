"""Run as root. No motion: step the Tic's temporary current limit and average
VIN at each setting. If the coils carry the set current, VIN sags more at
higher settings. Ends at the configured 990 mA, energized."""
import os, re, subprocess, time
TIC = f"/home/{os.environ['SUDO_USER']}/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd"

def tic(*a):
    return subprocess.run([TIC, *a], capture_output=True, text=True, check=True).stdout

def field(s, name):
    m = re.search(rf"^{name}:\s+(.*)$", s, re.M)
    return m.group(1).strip() if m else "?"

def row(label, n=12):
    vins = []
    for _ in range(n):
        vins.append(float(field(tic("--status"), "VIN voltage").split()[0]))
        time.sleep(0.15)
    s = tic("--status", "--full")
    print(f"{time.strftime('%H:%M:%S')}  {label:<16} limit={field(s, 'Current limit'):<8} "
          f"energized={field(s, 'Energized'):<3}  VIN mean={sum(vins)/n:.3f}  min={min(vins):.3f}  max={max(vins):.3f}", flush=True)

tic("--deenergize"); time.sleep(1); row("de-energized")
for c in (174, 343, 634, 990):
    tic("--current", str(c)); tic("--energize"); time.sleep(1); row(f"energized@{c}")
tic("--deenergize"); time.sleep(1); row("de-energized")
tic("--current", "990"); tic("--energize"); time.sleep(1); row("energized@990")
