"""Round 5: folding the six compute slices' rows into the packed files (PR 405), and the check of it.

    cd vertical-lab
    python out/twin5/slices/fold_check.py before   # the slice files as merged: every check below -> fold_check.json
    python out/twin5/slices/fold_check.py fold     # append each <experiment>.slice-<k>.jsonl (k = 1..6) to
                                                   # <experiment>.jsonl and delete the slice file
    python -m twin.bench5 pack                     # <experiment>.jsonl -> <experiment>.jsonl.xz, and left.md
    python out/twin5/slices/fold_check.py after    # the packed files against the record: every planned run once, every
                                                   # slice row there byte for byte, no slice or errors file left

What ``before`` checks, for each of the 69 slice rows: its run is one that was left, in exactly one slice, and not
already packed; its config is bench5's for that run id; ``code.twin_dirty`` is false and ``twin/`` at the recorded
commit is identical to ``b410477``'s; its ``env`` equals this PR's own rows' apart from the CPU (pin, kernels, threads,
hashing, package versions); it drew nothing from torch's global generator; it includes notes 1-4; its event log is
there and names the same run. And for each slice: no errors file, and the record of its determinism check (a rerun of
``arms``' ``r5_conventional_external_fast_lean_s0`` against the committed row). It also records, for the rows this PR
already had, the commit, the dirty flag and the CPU each was made with, and which files of ``twin/`` differ between
that commit and ``b410477``.
"""
from __future__ import annotations

import collections
import hashlib
import json
import lzma
import subprocess
import sys
from pathlib import Path

VL = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(VL))
RUNS = VL / "out" / "twin5" / "runs"
EVENTS = VL / "out" / "twin5" / "events"
SLICES = VL / "out" / "twin5" / "slices"
RECORD = SLICES / "fold_check.json"
BASE = "b410477a3e41dd8d6eb40cb566c8eb11deed70d7"
FOLDED = ("net", "net_more", "plans_net")
PRS = {1: 421, 2: 419, 3: 423, 4: 420, 5: 422, 6: 418}
ENV_NOT_COMPARED = ("cpu", "avx512")            # the machine; everything else in env has to match


def git(*args):
    return subprocess.run(["git", *args], cwd=VL, capture_output=True, text=True)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def packed_lines(name):
    p = RUNS / f"{name}.jsonl.xz"
    return [l for l in lzma.decompress(p.read_bytes()).decode().splitlines() if l.strip()] if p.exists() else []


def slice_files(name):
    return {int(p.name.split(".slice-")[1].split(".")[0]): p for p in sorted(RUNS.glob(f"{name}.slice-*.jsonl"))
            if not p.name.endswith(".errors.jsonl")}


def twin_diff(commit):
    """The files of twin/ that differ between a commit and b410477 (None if the commit isn't in this repository)."""
    if git("cat-file", "-e", f"{commit}^{{commit}}").returncode:
        return None
    return [l for l in git("diff", "--name-only", commit, BASE, "--", "twin").stdout.splitlines() if l.strip()]


def determinism_records():
    """Each slice's own record of its check (a rerun of the committed cheap-policy row on its runner)."""
    out = {}

    def js(name):
        return json.loads((SLICES / name).read_text())
    d = js("verify_slice_1.json")
    out[1] = dict(file="verify_slice_1.json", run_id=d["run_id"], cpu=d["env_rerun"]["cpu"],
                  row_identical=d["identical_apart_from_timing_and_provenance"], events_identical=d["event_log_identical"])
    out[2] = dict(file=None, note="no record file: the check is reported in PR 419's text and in commit 21d9b1a's message "
                  "only (the rerun matched apart from seconds, env.cpu and code.commit; event log byte-identical)")
    txt = (SLICES / "run_slice_3.check.txt").read_text().splitlines()
    d = json.loads([l for l in txt if l.startswith("{")][-1])
    out[3] = dict(file="run_slice_3.check.txt", run_id=d["run_id"], cpu=d["cpu"][1], row_identical=d["row_identical"],
                  events_identical=d["event_log_identical"])
    d = js("slice-4.check.json")
    out[4] = dict(file="slice-4.check.json", run_id=d["run_id"], cpu=d["cpu"][0], row_identical=d["identical"],
                  events_identical=d["events_identical"])
    d = js("check_slice_5.json")
    out[5] = dict(file="check_slice_5.json", run_id=d["run_id"], cpu=d["rerun"]["env"]["cpu"], row_identical=d["identical"],
                  events_identical=d["event_log_identical"])
    d = js("check.slice-6.json")
    out[6] = dict(file="check.slice-6.json", run_id=d["run_id"], cpu=d["provenance"]["env_differs"]["cpu"][0],
                  row_identical=d["row_identical"], events_identical=d["events_identical"])
    # the two slices that also reran a committed BOFN or pKGFN row (the cheap-policy row fits no GP)
    d = js("verify_slice_1_bofn.json")
    out[1]["gp_check"] = dict(file="verify_slice_1_bofn.json", run_id=d["run_id"],
                              row_identical=d["identical_apart_from_timing_and_provenance"],
                              events_identical=d["event_log_identical"])
    d = js("check-gp.slice-6.json")
    out[6]["gp_check"] = dict(file="check-gp.slice-6.json", runs=[dict(run_id=x["run_id"], row_identical=x["row_identical"],
                                                                       events_identical=x["events_identical"],
                                                                       first_diffs=x["first_diffs"][:3])
                                                                  for x in d["reruns_vs_committed"]],
                              deterministic_on_its_runner=not d["determinism"]["A_vs_B_diffs"]
                              and not d["determinism"]["A_vs_C_diffs"])
    return out


def before():
    from twin import bench5 as B5
    planned = {name: [B5.run_id(c) for c in cfgs] for name, cfgs in B5.EXPERIMENTS.items()}
    cfg_of = {name: {B5.run_id(c): c for c in cfgs} for name, cfgs in B5.EXPERIMENTS.items()}
    problems, rows, earlier = [], [], {}
    ref_env = None
    for name in B5.EXPERIMENTS:
        lines = packed_lines(name)
        ids = [B5.run_id(json.loads(l)["cfg"]) for l in lines]
        dup = sorted(k for k, v in collections.Counter(ids).items() if v > 1)
        if dup:
            problems.append(f"{name}: packed rows repeated: {dup}")
        extra = sorted(set(ids) - set(planned[name]))
        if extra:
            problems.append(f"{name}: packed rows that aren't planned: {extra}")
        groups = collections.Counter()
        for l in lines:
            r = json.loads(l)
            groups[(r["code"]["commit"], r["code"]["twin_dirty"], r["env"]["cpu"])] += 1
            if name == "net" and ref_env is None:
                ref_env = r["env"]
        earlier[name] = dict(planned=len(planned[name]), packed=len(ids), made_with=[
            dict(rows=n, commit=c[:7], twin_dirty=d, cpu=cpu, twin_files_differing_from_b410477=twin_diff(c))
            for (c, d, cpu), n in sorted(groups.items(), key=lambda kv: -kv[1])])
    env_ref = {k: v for k, v in ref_env.items() if k not in ENV_NOT_COMPARED}
    seen = collections.Counter()
    commits = {}
    for name in FOLDED:
        have = {B5.run_id(json.loads(l)["cfg"]) for l in packed_lines(name)}
        left = [r for r in planned[name] if r not in have]
        got = []
        for k, p in sorted(slice_files(name).items()):
            for line in p.read_text().splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                if "error" in r:
                    problems.append(f"{p.name}: an error row for {B5.run_id(r['cfg'])}")
                    continue
                rid = B5.run_id(r["cfg"])
                got.append(rid)
                seen[(name, rid)] += 1
                c = r["code"]["commit"]
                if c not in commits:
                    td = twin_diff(c)
                    commits[c] = dict(twin_identical_to_b410477=(td == []), twin_files_differing=td,
                                      in_this_branch=git("merge-base", "--is-ancestor", c, "HEAD").returncode == 0)
                ev = VL / r["events_file"]
                ev_ok, ev_sha = False, None
                if ev.exists():
                    b = ev.read_bytes()
                    ev_sha = sha(b)
                    try:
                        meta = json.loads(lzma.decompress(b)).get("meta") or {}
                        ev_ok = meta.get("run_id") == rid and meta.get("cfg") == r["cfg"]
                    except Exception:
                        ev_ok = False
                env_diff = sorted(k for k in (set(env_ref) | set(r["env"])) - set(ENV_NOT_COMPARED)
                                  if r["env"].get(k) != env_ref.get(k))
                rec = dict(experiment=name, run_id=rid, slice=k, pr=PRS[k], sha256=sha(line.encode()),
                           commit=c[:7], twin_dirty=r["code"]["twin_dirty"], cpu=r["env"]["cpu"],
                           pin=r["env"]["pin"], hash_pinned=r["env"]["hash_pinned"], pin_late=r["env"]["pin_late"],
                           env_differs_at=env_diff, torch_rng_used=r["torch_rng_used"], notes=r["r5"].get("notes"),
                           planned=rid in planned[name], was_left=rid in left, already_packed=rid in have,
                           cfg_is_bench5s=cfg_of[name].get(rid) == r["cfg"], seconds=r["seconds"],
                           gp_fits=r["gp"]["fits"], events_file=r["events_file"], events_ok=ev_ok, events_sha256=ev_sha)
                rows.append(rec)
                for cond, msg in ((not rec["planned"], "not a planned run"), (rec["already_packed"], "already packed"),
                                  (not rec["cfg_is_bench5s"], "config differs from bench5's"),
                                  (rec["twin_dirty"] is not False, "twin_dirty is not false"),
                                  (not commits[c]["twin_identical_to_b410477"], f"twin/ at {c[:7]} differs from b410477"),
                                  (bool(env_diff), f"env differs at {env_diff}"),
                                  (rec["pin"] != "avx2" or not rec["hash_pinned"] or rec["pin_late"], "not pinned as ours"),
                                  (rec["torch_rng_used"] is not False, "drew from torch's global generator"),
                                  (rec["notes"] != ["n1", "n2", "n3", "n4"], "notes aren't n1-n4"),
                                  (not ev_ok, "event log missing or for another run")):
                    if cond:
                        problems.append(f"{name} {rid} (slice {k}): {msg}")
        missing = sorted(set(left) - set(got))
        if missing:
            problems.append(f"{name}: left and in no slice: {missing}")
    twice = sorted(k for k, v in seen.items() if v > 1)
    if twice:
        problems.append(f"in more than one slice row: {twice}")
    errs = sorted(p.name for p in RUNS.glob("*.errors.jsonl"))
    if errs:
        problems.append(f"errors files: {errs}")
    det = determinism_records()
    for k, d in det.items():
        if d.get("file") is None:
            problems.append(f"slice {k}: {d['note']}")
        elif not (d["row_identical"] and d["events_identical"]):
            problems.append(f"slice {k}: its determinism check did not match")
    for k, d in det.items():
        g = d.get("gp_check")
        if g and "runs" in g and not all(x["row_identical"] for x in g["runs"]):
            problems.append(f"slice {k} ({d['cpu']}): its extra reruns of committed BOFN and pKGFN rows (made on an AMD "
                            f"EPYC 9V45) did not reproduce them: {[x['run_id'] for x in g['runs'] if not x['row_identical']]}")
    by_cpu = collections.Counter((r["cpu"], r["slice"]) for r in rows)
    rec = dict(what="the six compute slices' rows, checked as merged and before folding (fold_check.py before)",
               base_commit=BASE, slice_rows=len(rows), slice_rows_by_experiment=dict(collections.Counter(
                   r["experiment"] for r in rows)),
               slice_rows_by_cpu=[dict(cpu=c, slice=k, rows=n) for (c, k), n in sorted(by_cpu.items(), key=lambda kv: kv[0][1])],
               env_compared_with="this PR's own net rows (every key but " + ", ".join(ENV_NOT_COMPARED) + ")",
               env_reference=env_ref, recorded_commits=commits, determinism_checks=det, earlier_rows=earlier,
               problems=problems, rows=rows)
    RECORD.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"{len(rows)} slice rows; {len(problems)} things to report:")
    for p in problems:
        print("  -", p)
    print("recorded commits:", {c[:7]: v for c, v in commits.items()})
    return 0


def fold():
    n = 0
    for name in FOLDED:
        with (RUNS / f"{name}.jsonl").open("a") as fh:
            for k, p in sorted(slice_files(name).items()):
                for line in p.read_text().splitlines():
                    if line.strip():
                        fh.write(line + "\n")
                        n += 1
                p.unlink()
    print(f"{n} rows appended; the slice files are removed (run python -m twin.bench5 pack next)")
    return 0


def after():
    from twin import bench5 as B5
    rec = json.loads(RECORD.read_text())
    problems = []
    counts = {}
    for name, cfgs in B5.EXPERIMENTS.items():
        lines = packed_lines(name)
        ids = collections.Counter(B5.run_id(json.loads(l)["cfg"]) for l in lines)
        want = [B5.run_id(c) for c in cfgs]
        miss = [r for r in want if ids.get(r, 0) == 0]
        dup = sorted(r for r, v in ids.items() if v > 1)
        extra = sorted(set(ids) - set(want))
        counts[name] = dict(planned=len(want), packed=len(lines), each_once=not (miss or dup or extra))
        for what, v in (("missing", miss), ("repeated", dup), ("not planned", extra)):
            if v:
                problems.append(f"{name}: {what}: {v}")
        if (RUNS / f"{name}.jsonl").exists():
            problems.append(f"{name}: an appended file is still there (not packed)")
    shas = {name: {sha(l.encode()) for l in packed_lines(name)} for name in FOLDED}
    lost = [r["run_id"] for r in rec["rows"] if r["sha256"] not in shas[r["experiment"]]]
    if lost:
        problems.append(f"slice rows not in the packed files byte for byte: {lost}")
    ev = [r["run_id"] for r in rec["rows"] if not (VL / r["events_file"]).exists()
          or sha((VL / r["events_file"]).read_bytes()) != r["events_sha256"]]
    if ev:
        problems.append(f"event logs changed or missing since the check: {ev}")
    left = sorted(p.name for p in RUNS.glob("*.slice-*")) + sorted(p.name for p in RUNS.glob("*.errors.jsonl"))
    if left:
        problems.append(f"slice or errors files left: {left}")
    rec["after_folding"] = dict(experiments=counts, planned_runs=sum(c["planned"] for c in counts.values()),
                                packed_rows=sum(c["packed"] for c in counts.values()),
                                every_planned_run_exactly_once=all(c["each_once"] for c in counts.values()),
                                slice_rows_packed_byte_for_byte=not lost, event_logs_unchanged=not ev,
                                problems=problems)
    RECORD.write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps(rec["after_folding"], indent=1))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit({"before": before, "fold": fold, "after": after}.get(cmd, lambda: (print(__doc__), 2)[1])())
