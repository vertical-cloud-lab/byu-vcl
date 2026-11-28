#!/usr/bin/env bash
# The workflow's steps (ci/twin-slices.yml), run here on two short runs: what can be tested without Actions.
#
#   cd vertical-lab && bash ci/test_twin_slices.sh [WORKDIR] [DAYS]
#
# 1. A plan of two jobs, one run each (seed 5 of the automated lab's BOFN and of the conventional lab's heuristic and
#    funnel), shortened to DAYS simulated days (TWIN6_DAYS), in a scratch copy of out/twin6 (TWIN6_OUT).
# 2. Wave 1: each job runs the exact slice command with --hours small enough that its run stops part way and is
#    saved; the manifest step stages its files and the checkpoint is "uploaded" (copied aside).
# 3. Wave 2: the checkpoints are "restored", the same command carries the runs on to their rows.
# 4. The same two runs unbroken, in a third directory: the rows must be the same, apart from timing and provenance.
# 5. The fold step on the two jobs' artifacts plus fabricated ones (a job whose run is still waiting on a checkpoint,
#    a job that left no manifest, a row that comes twice), folded twice to show it is idempotent.
set -euo pipefail
VL=$(pwd)
W=${1:-/tmp/twin_slices_test}
DAYS=${2:-40}
H1=${H1:-0.004}                              # wave 1's --hours: about 15 s, so each run stops part way
rm -rf "$W"; mkdir -p "$W"
export TWIN_PIN=portable PYTHONHASHSEED=0 TWIN6_DAYS=$DAYS
TREE=$(git rev-parse HEAD:vertical-lab/twin)
R1=r6_vertical_parallel_bofn3_reorder_s5
R2=r6_conventional_external_fast_reorder_s5
# a scratch vertical-lab: the helper reads out/twin6 under its working directory
mk() { mkdir -p "$1/out/twin6/slices" "$1/ci"; cp "$VL/ci/twin_slices.py" "$1/ci/"; }
mk "$W/vl"
python - "$W/vl/out/twin6/slices/test2.json" "$TREE" "$R1" "$R2" <<'EOF'
import json, sys
p, tree, r1, r2 = sys.argv[1:]
json.dump(dict(name="test2", twin_tree=tree, hours=5.2, workers=4,
               jobs=[dict(job=1, runs=[r1]), dict(job=2, runs=[r2])]), open(p, "w"), indent=1)
EOF
PLAN=out/twin6/slices/test2.json
job() {                                      # job K HOURS WAVE: the slice job's steps, as the workflow runs them
  local K=$1 HOURS=$2 WAVE=$3 OUT="$W/vl/out/twin6" ST="$W/art/wave$3/rows-test2-$1"
  ( cd "$W/vl"
    mkdir -p "out/twin6/slices/test2/job-$K"
    python ci/twin_slices.py done-ids > "$W/done_before_$K.txt"
    python ci/twin_slices.py ids "$PLAN" "$K" > "$W/ids_$K.txt"
    set +e
    ( cd "$VL" && TWIN6_OUT="$OUT" python -m twin.bench6 ids "$W/ids_$K.txt" --slice "test2-$K" --workers 4 \
        --hours "$HOURS" ) 2>&1 | grep -v -i warn | tee "out/twin6/slices/test2/job-$K/ids.log"
    echo "bench6 ids exit: ${PIPESTATUS[0]}"
    set -e
    python ci/twin_slices.py manifest "$PLAN" "$K" "out/twin6/slices/test2/job-$K/ids.log" "$ST" "$W/done_before_$K.txt"
    mkdir -p "$W/art/wave$WAVE/ckpt-test2-$K"
    cp out/twin6/checkpoints/*.ckpt.xz "$W/art/wave$WAVE/ckpt-test2-$K/" 2>/dev/null || true )
}
echo "== wave 1: --hours $H1 (each run stops part way and is saved)"
job 1 "$H1" 1 & job 2 "$H1" 1 & wait
ls -la "$W/vl/out/twin6/checkpoints" || true
echo "== wave 2: checkpoints restored from wave 1's artifacts, the same command"
rm -rf "$W/vl/out/twin6/checkpoints"; mkdir -p "$W/vl/out/twin6/checkpoints"
cp "$W"/art/wave1/ckpt-test2-*/*.ckpt.xz "$W/vl/out/twin6/checkpoints/" 2>/dev/null || true
job 1 1 2 & job 2 1 2 & wait
echo "== the same runs unbroken"
( cd "$VL" && TWIN6_OUT="$W/unbroken" python -m twin.bench6 ids "$R1" "$R2" --slice ref --workers 2 ) 2>&1 | grep -v -i warn
python - "$W" "$R1" "$R2" <<'EOF'
import json, sys, glob
W, r1, r2 = sys.argv[1:]
skip = ("seconds", "timing", "gp", "env", "code", "events_file")     # gpcheck6's NOT_IN_ROW: timing, provenance
def rows(pat):
    out = {}
    for p in glob.glob(pat):
        for l in open(p):
            if l.strip():
                r = json.loads(l); out[r["events_file"].split("/")[-1][:-8]] = r
    return out
a = rows(f"{W}/vl/out/twin6/runs/*.slice-test2-*.jsonl"); b = rows(f"{W}/unbroken/runs/*.slice-ref.jsonl")
res = {}
for r in (r1, r2):
    x, y = a.get(r), b.get(r)
    same = x is not None and y is not None and {k: v for k, v in x.items() if k not in skip} == \
        {k: v for k, v in y.items() if k not in skip}
    segs = (x or {}).get("timing", {}).get("segments")
    ev = (x or {}).get("events_sha256") == (y or {}).get("events_sha256")
    res[r] = dict(row_same=same, events_same=ev, segments=[(s["from_day"], s["to_day"]) for s in segs or []])
print(json.dumps(res, indent=1))
json.dump(res, open(f"{W}/carry_on_check.json", "w"), indent=1)
assert all(v["row_same"] and v["events_same"] and len(v["segments"]) == 2 for v in res.values()), "carry-on differs"
EOF
echo "== the fold step: the two jobs' wave-2 artifacts, wave 1's, and fabricated ones"
F="$W/fold"; mk "$F/vl"; cp "$W/vl/$PLAN" "$F/vl/$PLAN"
A="$W/fold_art"; mkdir -p "$A"
cp -r "$W/art/wave2/rows-test2-1" "$W/art/wave2/rows-test2-2" "$A/"
python - "$W" "$A" "$TREE" <<'EOF'
import json, shutil, sys
from pathlib import Path
W, A, tree = sys.argv[1:]
A = Path(A)
plan = json.loads(Path(f"{W}/vl/out/twin6/slices/test2.json").read_text())
# a fabricated third and fourth job in the plan: job 3's run waits on a checkpoint, job 4 left no manifest
plan["jobs"] += [dict(job=3, runs=["r6_vertical_parallel_pkgfn3_reorder_s9", "r6_vertical_parallel_fast_reorder_s9"]),
                 dict(job=4, runs=["r6_conventional_external_bofn3_reorder_s9"])]
Path(f"{W}/fold/vl/out/twin6/slices/test2.json").write_text(json.dumps(plan, indent=1))
d = A / "rows-test2-3"
(d / "runs").mkdir(parents=True); (d / "events").mkdir(); (d / "slices/test2/job-3").mkdir(parents=True)
fake = dict(cfg=dict(lab="vertical", plan="parallel", policy="fast", stock="reorder", seed=9),
            events_file="out/twin6/events/r6_vertical_parallel_fast_reorder_s9.json.xz", events_kept=True, fake=True)
(d / "runs/arms.slice-test2-3.jsonl").write_text(json.dumps(fake) + "\n" + json.dumps(fake) + "\n")   # twice
(d / "events/r6_vertical_parallel_fast_reorder_s9.json.xz").write_bytes(b"fake")
(d / "slices/test2/job-3/manifest.json").write_text(json.dumps(dict(
    plan="test2", job=3, slice="test2-3", runs={"r6_vertical_parallel_pkgfn3_reorder_s9": "checkpoint",
                                                 "r6_vertical_parallel_fast_reorder_s9": "row"},
    checkpoints={"r6_vertical_parallel_pkgfn3_reorder_s9": dict(day=311.0, bytes=9000000)}, errors=[],
    n_rows=1, n_waiting=1)))
EOF
count() { python -c 'import json, sys; from pathlib import Path; print(json.dumps({p.name: sum(1 for l in p.read_text().splitlines() if l.strip()) for p in sorted(Path(sys.argv[1]).glob("*.jsonl"))}))' "$F/vl/out/twin6/runs"; }
( cd "$F/vl" && python ci/twin_slices.py fold "$A" "$PLAN" 999 > "$W/fold1.md" )
count > "$W/fold1_counts.json"
( cd "$F/vl" && python ci/twin_slices.py fold "$A" "$PLAN" 999 > "$W/fold2.md" )
count > "$W/fold2_counts.json"
cat "$W/fold2.md"
python - "$W" <<'EOF'
import json, sys
from pathlib import Path
W = sys.argv[1]
n1, n2 = json.load(open(f"{W}/fold1_counts.json")), json.load(open(f"{W}/fold2_counts.json"))
ev = sorted(p.name for p in Path(f"{W}/fold/vl/out/twin6/events").glob("*"))
st = Path(f"{W}/fold/vl/out/twin6/slices/test2/status.md").read_text()
out = dict(rows_per_file=n2, folded_twice_same=n1 == n2, events=ev,
           waiting_listed="r6_vertical_parallel_pkgfn3_reorder_s9" in st and "311" in st,
           no_manifest_listed="r6_conventional_external_bofn3_reorder_s9" in st,
           manifests=sorted(str(p.relative_to(Path(f"{W}/fold/vl"))) for p in
                            Path(f"{W}/fold/vl/out/twin6/slices/test2").rglob("manifest.json")))
print(json.dumps(out, indent=1))
assert n2.get("arms.slice-test2-3.jsonl") == 1, "a row that came twice was kept twice"
assert out["folded_twice_same"] and out["waiting_listed"] and out["no_manifest_listed"]
json.dump(out, open(f"{W}/fold_check.json", "w"), indent=1)
EOF
echo "ALL STEPS OK"
