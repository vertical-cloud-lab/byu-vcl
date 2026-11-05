#!/usr/bin/env python3
"""Keep a shared GitHub-hosted runner (4 cores, 16 GB) alive while several agents render at once.

Two round-8 sessions on PR #318 lost their runner to "The runner has received a shutdown signal" with eight agents
rendering, auditing and encoding at the same moment. This caps the heavy jobs and watches memory:

    python3 runner_guard.py slot [--weight N] [--mem MB] [--quick] [--label TEXT] -- CMD ...
        run CMD once N of the render slots (3 by default, VLAB_SLOTS) are free and MB of memory is available
    python3 runner_guard.py watch
        log memory every minute to /tmp/vlab_memlog.txt; if memory runs out, stop the biggest slotted job
    python3 runner_guard.py status
        who holds the slots, the memory now, and the last lines of the logs
    python3 runner_guard.py bg --log FILE [--weight N] [--mem MB] [--quick] [--label TEXT] -- CMD ...
        the same as slot, started detached (it outlives the calling shell), output to FILE, exit code to FILE.rc;
        prints the pid
    python3 runner_guard.py wait PID [--minutes M] [--log FILE]
        wait up to M minutes (default 50) for PID to finish, then print the end of FILE and its exit code

What takes a slot: anything that builds a 3-D scene (a render, a PREVIEW=1 still, an ARM_AUDIT=1 pass, a tour clip,
interference.py) and the long ffmpeg joins, one slot each. A whole-lab scene (setup_lab.py, animate.py workflow,
timelapse.py, a chapter on the whole floor) peaks near 6 GB (a render of animate.py workflow reached 5.7 GB), so
give it --mem 6500. (Weight 2 was the first rule
in continuation 2; it left a slot and three cores idle behind a single-threaded audit, so it was dropped at 16:45.)
Light work (matplotlib panels, JSON, notes) needs no slot.

* Slots are flock()ed files under /tmp/vlab_slots, so a slot frees itself when its process dies, however it dies.
* Waiters queue in arrival order, except that `--quick` jobs (a PREVIEW=1 still, a tour still: a few minutes) go
  ahead of normal ones, and a normal job that has waited 20 minutes counts as quick. (Until 17:30 on 2026-11-05 it
  was a plain first-come turnstile, and a two-minute preview waited a quarter of an hour behind three renders.)
* A job also waits for memory: MemAvailable, less what the running jobs may still grow into (each one's declared
  --mem less what it already holds, plus 500 MB), must cover its own --mem (default 3 GB, VLAB_MEM_MB_PER_WEIGHT).
  Renders grow as they go, so checking MemAvailable alone at the start isn't enough: at 17:09 on 2026-11-05 two
  whole-lab jobs and a preview, admitted one by one, grew to 15 GB together and the watchdog had to stop one.
* The job runs under ``nice -n 5`` with LP_NUM_THREADS=2 (llvmpipe), OMP_NUM_THREADS=2 and FFMPEG_THREADS=2 unless
  they are already set, and with VLAB_SLOT=<label> in its environment, which is how the watchdog finds it.
* The watchdog sends SIGTERM to a slotted process when MemAvailable falls below 900 MB (VLAB_MEM_FLOOR_MB; 1200 in
  round 8): the youngest one holding at least 1.5 GB, so the least finished work is lost (until 18:40 it took the
  largest, which is often a render twenty minutes in). Losing one job is better than losing the runner and every
  unpushed commit.
"""
from __future__ import annotations

import fcntl
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

SLOT_DIR = Path("/tmp/vlab_slots")
N_SLOTS = int(os.environ.get("VLAB_SLOTS", "3"))
MEM_PER_WEIGHT = int(os.environ.get("VLAB_MEM_MB_PER_WEIGHT", "3000"))
MEM_FLOOR = int(os.environ.get("VLAB_MEM_FLOOR_MB", "900"))
SLOT_LOG = SLOT_DIR / "log.txt"
MEM_LOG = Path("/tmp/vlab_memlog.txt")


def now() -> str:
    return time.strftime("%H:%M:%S", time.gmtime())


def meminfo() -> dict[str, int]:
    out = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        k, v = line.split(":", 1)
        out[k] = int(v.split()[0]) // 1024          # MB
    return out


def log(path: Path, msg: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(f"{now()} {msg}\n")


QUEUE = SLOT_DIR / "queue"
PROMOTE_S = 20 * 60          # a normal job waiting longer than this goes ahead of quick ones that came later


def queue_rank(ticket: Path) -> int:
    """This waiter's place among the live waiters: quick jobs first, then by arrival; a long wait counts as quick."""
    live = []
    for t in QUEUE.iterdir():
        try:
            ts, pid, prio = t.name.split("_")
            if not Path(f"/proc/{pid}").exists():
                t.unlink(missing_ok=True)
                continue
            ts, prio = float(ts), int(prio)
        except (ValueError, OSError):
            continue
        eff = 0 if time.time() - ts > PROMOTE_S else prio
        live.append((eff, ts, t.name))
    live.sort()
    names = [n for _, _, n in live]
    return names.index(ticket.name) if ticket.name in names else 0


def held_infos() -> list[dict]:
    """The info of every slot that is held right now (one entry per holder)."""
    out, seen = [], set()
    for i in range(N_SLOTS):
        lock, info = SLOT_DIR / f"slot{i}.lock", SLOT_DIR / f"slot{i}.info"
        if not lock.exists():
            continue
        with open(lock, "a+") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f, fcntl.LOCK_UN)
                continue
            except BlockingIOError:
                pass
        try:
            d = json.loads(info.read_text())
        except (OSError, ValueError):
            d = dict(pid=-1, mem=MEM_PER_WEIGHT)
        if d.get("pid") not in seen:
            seen.add(d.get("pid"))
            out.append(d)
    return out


def rss_by_holder() -> dict[int, int]:
    """MB resident in the process tree of each slot holder (processes with VLAB_SLOT_PID=<holder>)."""
    out: dict[int, int] = {}
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            env = (d / "environ").read_bytes().split(b"\0")
            hp = next((int(e[14:]) for e in env if e.startswith(b"VLAB_SLOT_PID=")), None)
            if hp is None:
                continue
            for line in (d / "status").read_text().splitlines():
                if line.startswith("VmRSS:"):
                    out[hp] = out.get(hp, 0) + int(line.split()[1]) // 1024
        except (OSError, ValueError):
            continue
    return out


def reserved() -> int:
    """MB the running jobs may still grow into: each one's declared peak less what it holds already, plus a margin."""
    rss = rss_by_holder()
    return sum(max(0, int(d.get("mem", MEM_PER_WEIGHT)) - rss.get(int(d.get("pid", -1)), 0))
               for d in held_infos()) + 500


def holders() -> list[str]:
    out = []
    for i in range(N_SLOTS):
        info = SLOT_DIR / f"slot{i}.info"
        lock = SLOT_DIR / f"slot{i}.lock"
        if not lock.exists():
            continue
        with open(lock, "a+") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f, fcntl.LOCK_UN)
            except BlockingIOError:
                try:
                    d = json.loads(info.read_text())
                    out.append(f"slot{i}: {d['label']} (pid {d['pid']}, {d['mem']} MB, {d['t']})")
                except (OSError, ValueError, KeyError):
                    out.append(f"slot{i}: " + (info.read_text().strip() if info.exists() else "?"))
    return out


def slot(argv: list[str]) -> int:
    weight, label, rcfile, mem, prio = 1, None, None, None, 1
    while argv and argv[0] != "--":
        a = argv.pop(0)
        if a == "--weight":
            weight = int(argv.pop(0))
        elif a == "--mem":
            mem = int(argv.pop(0))
        elif a == "--quick":
            prio = 0
        elif a == "--label":
            label = argv.pop(0)
        elif a == "--rcfile":
            rcfile = argv.pop(0)
        else:
            sys.exit(f"runner_guard slot: unknown option {a}")
    if not argv or argv[0] != "--" or len(argv) < 2:
        sys.exit("usage: runner_guard.py slot [--weight N] [--label TEXT] -- CMD ...")
    cmd = argv[1:]
    weight = max(1, min(weight, N_SLOTS))
    label = label or " ".join(Path(c).name for c in cmd[:4])[:80]
    SLOT_DIR.mkdir(parents=True, exist_ok=True)
    need = mem if mem is not None else MEM_PER_WEIGHT * weight
    t0 = time.time()
    held = []
    QUEUE.mkdir(parents=True, exist_ok=True)
    ticket = QUEUE / f"{time.time():.3f}_{os.getpid()}_{prio}"
    ticket.write_text(label + "\n")
    last_note = 0.0
    try:
        while True:
            rank = queue_rank(ticket)
            free = N_SLOTS - sum(int(d.get("weight", 1)) for d in held_infos())
            if rank < free and meminfo().get("MemAvailable", 0) - reserved() >= need:
                for i in range(N_SLOTS):
                    f = open(SLOT_DIR / f"slot{i}.lock", "a+")
                    try:
                        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        held.append(f)
                        (SLOT_DIR / f"slot{i}.info").write_text(json.dumps(dict(
                            label=label, pid=os.getpid(), weight=weight, mem=need, t=now())) + "\n")
                        if len(held) == weight:
                            break
                    except BlockingIOError:
                        f.close()
                if len(held) == weight:
                    break
                for f in held:                                # not all of them: give the partial ones back now
                    fcntl.flock(f, fcntl.LOCK_UN)
                    f.close()
                held = []
            if time.time() - last_note > 300:
                print(f"[runner_guard] waiting ({'quick' if prio == 0 else 'normal'}, place {rank + 1} in the queue) "
                      f"for {weight} slot(s), {need} MB: {'; '.join(holders()) or 'none held'}",
                      file=sys.stderr, flush=True)
                last_note = time.time()
            time.sleep(4)
    finally:
        ticket.unlink(missing_ok=True)
    waited = time.time() - t0
    log(SLOT_LOG, f"START w{weight} after {waited:.0f}s wait: {label}")
    env = dict(os.environ, VLAB_SLOT=label, VLAB_SLOT_PID=str(os.getpid()))
    for k in ("LP_NUM_THREADS", "OMP_NUM_THREADS", "FFMPEG_THREADS"):
        env.setdefault(k, "2")
    t1 = time.time()
    # The job runs in its own process group, and a SIGTERM or SIGINT to this process is passed on to all of it. Without
    # this, killing the slot process (by hand, or a caller's timeout) freed the slot while the render kept running and
    # kept its memory (2.3 GB once, round 8).
    p = subprocess.Popen(["nice", "-n", "5", *cmd], env=env, start_new_session=True)

    def forward(signum, _frame):
        try:
            os.killpg(p.pid, signum)
        except OSError:
            pass
    signal.signal(signal.SIGTERM, forward)
    signal.signal(signal.SIGINT, forward)
    rc = p.wait()
    log(SLOT_LOG, f"END   w{weight} rc={rc} after {(time.time() - t1) / 60:.1f} min: {label}")
    if rcfile:
        Path(rcfile).write_text(f"{rc}\n")
    return rc


def bg(argv: list[str]) -> int:
    logf = None
    rest = []
    while argv and argv[0] != "--":
        a = argv.pop(0)
        if a == "--log":
            logf = argv.pop(0)
        else:
            rest.append(a)
    if not logf or not argv:
        sys.exit("usage: runner_guard.py bg --log FILE [--weight N] [--label TEXT] -- CMD ...")
    Path(logf).parent.mkdir(parents=True, exist_ok=True)
    rc = Path(logf + ".rc")
    if rc.exists():
        rc.unlink()
    with open(logf, "w") as out:
        p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "slot", *rest, "--rcfile", str(rc),
                              *argv], stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             start_new_session=True, cwd=os.getcwd())
    print(p.pid)
    return 0


def wait(argv: list[str]) -> int:
    pid, minutes, logf = int(argv.pop(0)), 50.0, None
    while argv:
        a = argv.pop(0)
        if a == "--minutes":
            minutes = float(argv.pop(0))
        elif a == "--log":
            logf = argv.pop(0)
    t0 = time.time()
    while Path(f"/proc/{pid}").exists() and time.time() - t0 < minutes * 60:
        try:                                              # a zombie child of this shell counts as finished
            if Path(f"/proc/{pid}/stat").read_text().split(")")[-1].split()[0] == "Z":
                break
        except OSError:
            break
        time.sleep(10)
    running = Path(f"/proc/{pid}").exists()
    print(f"[runner_guard] pid {pid} {'STILL RUNNING' if running else 'finished'} after "
          f"{(time.time() - t0) / 60:.1f} min")
    if logf and Path(logf).exists():
        print("\n".join(Path(logf).read_text(errors="replace").splitlines()[-15:]))
        rc = Path(logf + ".rc")
        print(f"[runner_guard] exit code: {rc.read_text().strip() if rc.exists() else 'none yet'}")
    return 0


def slotted_procs() -> list[tuple[int, int, str]]:
    """(rss MB, pid, label) of every process started under a slot."""
    out = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            env = (d / "environ").read_bytes().split(b"\0")
            lab = next((e[10:].decode(errors="replace") for e in env if e.startswith(b"VLAB_SLOT=")), None)
            if lab is None:
                continue
            rss = 0
            for line in (d / "status").read_text().splitlines():
                if line.startswith("VmRSS:"):
                    rss = int(line.split()[1]) // 1024
            comm = (d / "comm").read_text().strip()
            out.append((rss, int(d.name), f"{lab} [{comm}]"))
        except (OSError, ValueError):
            continue
    return sorted(out, reverse=True)


def age_s(pid: int) -> float:
    """Seconds since the process started."""
    try:
        start = int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19])
        up = float(Path("/proc/uptime").read_text().split()[0])
        return up - start / os.sysconf("SC_CLK_TCK")
    except (OSError, ValueError, IndexError):
        return 1e9


def top_procs(n=5) -> str:
    r = subprocess.run(["ps", "-eo", "rss,comm", "--sort=-rss", "--no-headers"], capture_output=True, text=True)
    items = []
    for line in r.stdout.splitlines()[:n]:
        rss, comm = line.split(None, 1)
        items.append(f"{comm.strip()}:{int(rss) // 1024}")
    return " ".join(items)


def watch():
    peak_used = 0
    while True:
        m = meminfo()
        avail, swapfree = m.get("MemAvailable", 0), m.get("SwapFree", 0)
        used = m.get("MemTotal", 0) - avail
        peak_used = max(peak_used, used)
        load = os.getloadavg()
        log(MEM_LOG, f"avail={avail} used={used} peak_used={peak_used} swapfree={swapfree} "
                     f"load={load[0]:.1f},{load[1]:.1f},{load[2]:.1f} slots=[{' | '.join(holders())}] "
                     f"top: {top_procs()}")
        if avail < MEM_FLOOR:
            procs = slotted_procs()
            # the youngest job holding at least 1.5 GB: the least finished work lost (the biggest is often a render
            # twenty minutes in); the biggest if none is that large
            big = [(age_s(pid), rss, pid, lab) for rss, pid, lab in procs if rss >= 1500]
            if big:
                _, rss, pid, lab = min(big)
                procs = [(rss, pid, lab)]
            if procs:
                rss, pid, lab = procs[0]
                try:
                    os.kill(pid, signal.SIGTERM)
                    log(MEM_LOG, f"LOW MEMORY ({avail} MB): SIGTERM pid {pid} {lab}, {rss} MB")
                    log(SLOT_LOG, f"KILLED by the watchdog, {avail} MB available: pid {pid} {lab}, {rss} MB")
                except OSError:
                    pass
            time.sleep(15)
        else:
            time.sleep(10 if avail < 3000 else 60)


def status():
    m = meminfo()
    print(f"{now()} MemAvailable {m.get('MemAvailable')} MB, SwapFree {m.get('SwapFree')} MB, "
          f"load {os.getloadavg()}")
    print("slots:", "; ".join(holders()) or "none held")
    for p in (SLOT_LOG, MEM_LOG):
        if p.exists():
            print(f"--- {p}")
            print("\n".join(p.read_text().splitlines()[-8:]))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "slot":
        sys.exit(slot(rest))
    elif cmd == "watch":
        watch()
    elif cmd == "status":
        status()
    elif cmd == "bg":
        sys.exit(bg(rest))
    elif cmd == "wait":
        sys.exit(wait(rest))
    else:
        sys.exit(__doc__)
