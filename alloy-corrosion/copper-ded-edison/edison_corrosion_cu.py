"""Edison queries for the copper version of the CubXL corrosion plan (PR #278).
Same layout as digital-alloy-lab PR #117's edison_cu_ded.py, so later batches
can be added to queries.py and run the same way.

Usage (from repo root):
    python alloy-corrosion/copper-ded-edison/edison_corrosion_cu.py submit <batch>
    python alloy-corrosion/copper-ded-edison/edison_corrosion_cu.py wait <batch> [max_minutes]
    python alloy-corrosion/copper-ded-edison/edison_corrosion_cu.py fetch
    python alloy-corrosion/copper-ded-edison/edison_corrosion_cu.py status

`wait` blocks in a foreground Python loop (time.sleep) until every task in the
batch is terminal or max_minutes passes; run it as ONE long-timeout foreground
call, never in the background. `fetch` writes one markdown answer per
finished task (batchN/<name>.md) and the gzipped verbose trajectory
(raw/<name>.json.gz).

Requires: pip install edison-client ; EDISON_PLATFORM_API_KEY in the env.
"""

import gzip
import json
import os
import pathlib
import sys
import time
from datetime import datetime, timezone

from edison_client import EdisonClient, JobNames, TaskRequest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from queries import BATCHES  # noqa: E402

TASK_FILE = HERE / "_task_ids.json"
RAW_DIR = HERE / "raw"
TERMINAL = {"success", "fail", "failed", "cancelled", "error", "truncated"}


def client() -> EdisonClient:
    return EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load() -> dict:
    return json.loads(TASK_FILE.read_text()) if TASK_FILE.exists() else {}


def save(records: dict) -> None:
    TASK_FILE.write_text(json.dumps(records, indent=2) + "\n")


def submit(batch: int) -> None:
    records = load()
    c = client()
    for name, spec in BATCHES[batch].items():
        if name in records:
            print(f"{name}: already submitted ({records[name]['task_id']})", flush=True)
            continue
        req = TaskRequest(name=getattr(JobNames, spec["job"]), query=spec["query"])
        task_id = str(c.create_task(task_data=req))
        records[name] = {
            "batch": batch,
            "task_id": task_id,
            "job": spec["job"],
            "submitted": now(),
        }
        save(records)
        print(f"{name}: {spec['job']} -> {task_id}", flush=True)


def poll(c: EdisonClient, records: dict, names: list[str]) -> dict:
    statuses = {}
    for name in names:
        try:
            statuses[name] = str(c.get_task(task_id=records[name]["task_id"]).status)
        except Exception as exc:  # transient API errors: keep polling
            statuses[name] = f"poll-error: {type(exc).__name__}"
    return statuses


def wait(batch: int, max_minutes: float = 40.0, interval: int = 60) -> None:
    c = client()
    records = load()
    mine = [n for n, r in records.items() if r["batch"] == batch]
    start = time.time()
    while True:
        statuses = poll(c, records, mine)
        elapsed = (time.time() - start) / 60
        done = sum(s in TERMINAL for s in statuses.values())
        pending = {n: s for n, s in statuses.items() if s not in TERMINAL}
        print(f"[{now()} +{elapsed:.1f} min] batch {batch}: {done}/{len(mine)} "
              f"done; pending {pending}", flush=True)
        if not pending:
            break
        if elapsed > max_minutes:
            print("Stopping wait: max_minutes reached.", flush=True)
            break
        time.sleep(interval)


def fetch() -> None:
    c = client()
    records = load()
    RAW_DIR.mkdir(exist_ok=True)
    for name, rec in records.items():
        if "fetched" in rec:
            continue
        task = c.get_task(task_id=rec["task_id"])
        status = str(task.status)
        rec["status"] = status
        if status not in TERMINAL:
            print(f"{name}: still {status}", flush=True)
            continue
        verbose = c.get_task(task_id=rec["task_id"], verbose=True)
        with gzip.open(RAW_DIR / f"{name}.json.gz", "wt", encoding="utf-8") as fh:
            json.dump({"task": task.model_dump(mode="json"),
                       "verbose": verbose.model_dump(mode="json")}, fh)
        answer = (getattr(task, "formatted_answer", None)
                  or getattr(task, "answer", None)
                  or "(no answer returned)")
        rec["fetched"] = now()
        out_dir = HERE / f"batch{rec['batch']}"
        out_dir.mkdir(exist_ok=True)
        header = (
            "<!--\n"
            f"Edison Scientific {rec['job']} task (batch {rec['batch']})\n"
            f"- Task ID: {rec['task_id']}\n"
            f"- Submitted: {rec['submitted']}\n"
            f"- Fetched: {rec['fetched']} (status: {status})\n"
            f"- Raw trajectory JSON: ../raw/{name}.json.gz\n"
            "- Synthesis: ../README.md\n"
            "-->\n\n"
        )
        query = BATCHES[rec["batch"]][name]["query"].strip()
        body = f"Question:\n\n{query}\n\n---\n\n{answer.strip()}\n"
        (out_dir / f"{name}.md").write_text(header + body)
        print(f"{name}: {status}, {len(answer)} chars -> batch{rec['batch']}/{name}.md",
              flush=True)
        save(records)
    save(records)


def status() -> None:
    c = client()
    records = load()
    print(poll(c, records, list(records)))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "submit":
        submit(int(sys.argv[2]))
    elif cmd == "wait":
        wait(int(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else 40.0)
    elif cmd == "fetch":
        fetch()
    elif cmd == "status":
        status()
