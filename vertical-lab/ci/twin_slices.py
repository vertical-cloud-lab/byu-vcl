"""The round-6 grid's compute slices on GitHub Actions: the helper the workflow (``ci/twin-slices.yml``) runs. Standard
library only, so the plan and fold steps need no numerical packages. Run from ``vertical-lab``.

    python ci/twin_slices.py jobs PLAN                 # JSON list of the plan's jobs that still have runs without a
                                                       # row on this checkout (the workflow's matrix)
    python ci/twin_slices.py ids PLAN JOB              # the job's run ids, one a line (for ``bench6 ids``)
    python ci/twin_slices.py check-tree PLAN           # exit 1 unless twin/ at HEAD is the tree the plan was made for
    python ci/twin_slices.py done                      # the run ids with a row on this checkout, one a line
    python ci/twin_slices.py manifest PLAN JOB LOG STAGE [BEFORE]   # after ``bench6 ids``: what became of each of
                                                       # the job's runs (row, checkpoint and its day, not started,
                                                       # neither), and the files to upload, staged under STAGE
    python ci/twin_slices.py fold ARTIFACTS PLAN [RUN] # merge every job's artifact into out/twin6 (rows into
                                                       # runs/<experiment>.slice-<plan>-<job>.jsonl, one per run id;
                                                       # event logs; the GP checks and manifests) and write the
                                                       # wave's status, with the runs still waiting on a checkpoint

A job's slice is ``<plan>-<job>`` (``bench6 ids --slice tier1-7``), so its rows go to
``out/twin6/runs/<experiment>.slice-tier1-7.jsonl``: the same file in every wave, and never another job's. A run's id
is read from its row's ``events_file`` (``out/twin6/events/<run id>.json.xz``, which ``bench6.run_one`` sets), so
nothing here needs the engine.
"""
from __future__ import annotations

import json
import lzma
import re
import shutil
import subprocess
import sys
from pathlib import Path

VL = Path.cwd()
OUT = VL / "out" / "twin6"
RUNS, EVENTS, CKPTS, SLICES = OUT / "runs", OUT / "events", OUT / "checkpoints", OUT / "slices"


def load_plan(path) -> dict:
    p = Path(path)
    if not p.is_absolute() and not p.exists():
        p = VL / path
    return json.loads(p.read_text())


def plan_name(plan: dict, path) -> str:
    return plan.get("name") or Path(path).stem


def rid_of(row: dict) -> str | None:
    f = row.get("events_file") or ""
    m = re.search(r"events/(.+?)\.json(?:\.xz)?$", f)
    return m.group(1) if m else None


def _row_lines(p: Path) -> list:
    if not p.exists():
        return []
    b = p.read_bytes()
    txt = lzma.decompress(b).decode() if p.suffix == ".xz" else b.decode()
    return [l for l in txt.splitlines() if l.strip()]


def done_ids(runs_dir: Path = RUNS) -> set:
    """Run ids with a row anywhere under runs/: packed, appended or in a slice's file (errors are not rows)."""
    out = set()
    if not runs_dir.exists():
        return out
    for p in sorted(runs_dir.iterdir()):
        if p.name.endswith(".errors.jsonl") or not (p.name.endswith(".jsonl") or p.name.endswith(".jsonl.xz")):
            continue
        for line in _row_lines(p):
            try:
                r = rid_of(json.loads(line))
            except json.JSONDecodeError:
                continue
            if r:
                out.add(r)
    return out


def job_of(plan: dict, job: int) -> dict:
    for j in plan["jobs"]:
        if int(j["job"]) == int(job):
            return j
    raise SystemExit(f"no job {job} in the plan")


def cmd_jobs(path):
    plan = load_plan(path)
    done = done_ids()
    left = [j["job"] for j in plan["jobs"] if any(r not in done for r in j["runs"])]
    print(json.dumps(left))


def cmd_ids(path, job):
    for r in job_of(load_plan(path), job)["runs"]:
        print(r)


def cmd_check_tree(path):
    plan = load_plan(path)
    tree = subprocess.run(["git", "rev-parse", "HEAD:vertical-lab/twin"], capture_output=True, text=True,
                          cwd=VL).stdout.strip()
    if tree != plan["twin_tree"]:
        print(f"twin/ at HEAD is {tree}, the plan was made for {plan['twin_tree']}: its time estimates, the GP "
              f"check's reference and the rows it describes belong to that engine")
        return 1
    print(f"twin/ at HEAD is the plan's engine ({tree})")
    return 0


def cmd_done():
    for r in sorted(done_ids()):
        print(r)


def cmd_manifest(path, job, log, stage, before=None):
    """After ``bench6 ids``: what became of each of the job's runs in this wave (a row, a checkpoint and the day it
    stopped at, not started, or neither: an error, or the job ended first), from the files ``ids`` left and its log,
    written with the files to upload to ``stage`` (``runs/``, ``events/`` and ``slices/<plan>/job-<job>/`` as under
    out/twin6): the job's slice files, the event logs of its runs that got their row in this wave, its GP check, its
    log and the manifest. ``before``: the run ids that had rows before the wave (``done``), to tell the new rows from
    an earlier wave's in the same slice file. Checkpoints of runs that have a row are removed."""
    plan = load_plan(path)
    name = plan_name(plan, path)
    j = job_of(plan, job)
    slice_k = f"{name}-{job}"
    mine = set(j["runs"])
    prior = set(Path(before).read_text().split()) if before and Path(before).exists() else set()
    rows, files = {}, []
    for p in sorted(RUNS.glob(f"*.slice-{slice_k}.jsonl")):
        files.append(p)
        for line in _row_lines(p):
            r = rid_of(json.loads(line))
            if r in mine:
                rows[r] = p.name
    errors = []
    for p in sorted(RUNS.glob(f"*.slice-{slice_k}.errors.jsonl")):
        files.append(p)
        for line in _row_lines(p):
            e = json.loads(line)
            errors.append(((e.get("error") or "").strip().splitlines() or [""])[-1])
    text = Path(log).read_text() if log and Path(log).exists() else ""
    days = {m.group(1): float(m.group(2)) for m in re.finditer(r"\s(\S+): stopped at day ([0-9.]+) and saved", text)}
    not_started = {m.group(1) for m in re.finditer(r"\s(\S+): not started", text)}
    done = done_ids()
    ck = {}
    for p in sorted(CKPTS.glob("*.ckpt.xz")) if CKPTS.exists() else []:
        r = p.name[:-len(".ckpt.xz")]
        if r in done:
            p.unlink()                                   # a run with a row needs no checkpoint
            continue
        if r in mine:
            ck[r] = dict(day=days.get(r), bytes=p.stat().st_size)
    status = {}
    for r in j["runs"]:
        if r in prior:
            status[r] = "row (an earlier wave)"
        elif r in rows:
            status[r] = "row"
        elif r in ck:
            status[r] = "checkpoint"
        elif r in not_started:
            status[r] = "not started"
        else:
            status[r] = "no row, no checkpoint"
    m = dict(plan=name, job=int(job), slice=slice_k, runs=status, checkpoints=ck, errors=errors,
             n_rows=sum(1 for v in status.values() if v == "row"),
             n_waiting=sum(1 for r, v in status.items() if not v.startswith("row")))
    st = Path(stage)
    jd = st / "slices" / name / f"job-{job}"
    jd.mkdir(parents=True, exist_ok=True)
    (st / "runs").mkdir(parents=True, exist_ok=True)
    for p in files:
        shutil.copyfile(p, st / "runs" / p.name)
    for r, v in status.items():
        ev = EVENTS / f"{r}.json.xz"
        if v == "row" and ev.exists():
            (st / "events").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ev, st / "events" / ev.name)
    src = SLICES / name / f"job-{job}"
    if src.exists():
        for p in src.iterdir():
            if p.is_file():
                shutil.copyfile(p, jd / p.name)
    (jd / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    print(json.dumps({k: m[k] for k in ("plan", "job", "n_rows", "n_waiting")} | dict(checkpoints=len(ck))))


def merge_rows(src: Path, dst: Path) -> tuple:
    """Lines of ``src`` added to ``dst`` (created if need be), one per run id, those already in ``dst`` kept."""
    have = {}
    for line in _row_lines(dst):
        have.setdefault(rid_of(json.loads(line)), line)
    new = 0
    out = list(have.values())
    for line in _row_lines(src):
        r = rid_of(json.loads(line))
        if r is None or r in have:
            continue
        have[r] = line
        out.append(line)
        new += 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("".join(l + "\n" for l in out))
    return new, len(out)


def cmd_fold(artifacts, path, run=None):
    """Every job's artifact (``rows-<plan>-<job>``, holding ``runs/``, ``events/`` and ``slices/`` under out/twin6)
    merged into this checkout, and the wave's status written to ``slices/<plan>/status.md`` (also printed)."""
    plan = load_plan(path)
    name = plan_name(plan, path)
    art = Path(artifacts)
    lines = []
    manifests = {}
    n_new = 0
    for d in sorted(p for p in art.iterdir() if p.is_dir()) if art.exists() else []:
        for src in sorted((d / "runs").glob("*.jsonl")) if (d / "runs").exists() else []:
            if src.name.endswith(".errors.jsonl"):
                dst = RUNS / src.name                     # errors: kept beside the rows, each line once
                have = _row_lines(dst)
                add = [l for l in _row_lines(src) if l not in set(have)]
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text("".join(l + "\n" for l in have + add))
                continue
            new, tot = merge_rows(src, RUNS / src.name)
            n_new += new
            lines.append(f"{d.name}: {src.name}: {new} new rows ({tot} in the file)")
        kept = set()
        for src in sorted((d / "runs").glob("*.slice-*.jsonl")) if (d / "runs").exists() else []:
            if not src.name.endswith(".errors.jsonl"):
                for line in _row_lines(src):
                    row = json.loads(line)
                    if row.get("events_kept", True):
                        kept.add(rid_of(row))
        for src in sorted((d / "events").glob("*.json.xz")) if (d / "events").exists() else []:
            if src.name[:-len(".json.xz")] in kept:
                EVENTS.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, EVENTS / src.name)
        sd = d / "slices"
        if sd.exists():
            for src in sorted(sd.rglob("*")):
                if src.is_file():
                    dst = SLICES / src.relative_to(sd)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dst)
                    if src.name == "manifest.json":
                        mm = json.loads(src.read_text())
                        manifests[int(mm["job"])] = mm
    done = done_ids()
    waiting, never = [], []
    for j in plan["jobs"]:
        m = manifests.get(int(j["job"]))
        for r in j["runs"]:
            if r in done:
                continue
            if m is None:
                never.append((j["job"], r, "the job left no manifest (it failed, was cancelled, or had nothing to do)"))
            elif (m["checkpoints"].get(r) is not None):
                waiting.append((j["job"], r, m["checkpoints"][r].get("day")))
            else:
                never.append((j["job"], r, m["runs"].get(r, "?")))
    n_all = sum(len(j["runs"]) for j in plan["jobs"])
    n_done = sum(1 for j in plan["jobs"] for r in j["runs"] if r in done)
    S = [f"# Round 6 plan `{name}`: status after workflow run {run or '(local)'}", "",
         f"{n_done} of {n_all} runs have rows ({n_new} new in this wave); {len(waiting)} are waiting on a checkpoint "
         f"and {len(never)} have neither. Everything is simulated.", ""]
    if waiting or never:
        S += ["**To carry on:** dispatch the workflow again with the same branch and plan and "
              f"`resume_run_id` = `{run or 'this run'}`: each job restores its checkpoints from this run's "
              "`ckpt-...` artifacts and carries those runs on first.", ""]
    if waiting:
        S += ["## Waiting on a checkpoint", "", "| Job | Run | Stopped at day |", "|---|---|---|"]
        S += [f"| {j} | `{r}` | {'' if d is None else f'{d:g}'} |" for j, r, d in waiting]
        S.append("")
    if never:
        S += ["## No row and no checkpoint", "", "| Job | Run | Why |", "|---|---|---|"]
        S += [f"| {j} | `{r}` | {w} |" for j, r, w in never]
        S.append("")
    S += ["## Files", ""] + [f"* {x}" for x in lines]
    txt = "\n".join(S) + "\n"
    (SLICES / name).mkdir(parents=True, exist_ok=True)
    (SLICES / name / "status.md").write_text(txt)
    print(txt)
    return 0


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    c = argv[0]
    if c == "jobs":
        return cmd_jobs(argv[1]) or 0
    if c == "ids":
        return cmd_ids(argv[1], int(argv[2])) or 0
    if c == "check-tree":
        return cmd_check_tree(argv[1])
    if c == "done":
        return cmd_done() or 0
    if c == "manifest":
        return cmd_manifest(argv[1], int(argv[2]), argv[3], argv[4], argv[5] if len(argv) > 5 else None) or 0
    if c == "fold":
        return cmd_fold(argv[1], argv[2], argv[3] if len(argv) > 3 else None)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
