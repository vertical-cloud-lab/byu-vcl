"""Submit / wait / fetch Edison LITERATURE_HIGH queries for the 6DOF robotics scan (issue #199).

Usage:
    python scripts/edison_6dof.py submit <slug> <prompt-file>
    python scripts/edison_6dof.py wait   <slug>          # blocking; Python-side sleep
    python scripts/edison_6dof.py fetch  <slug>          # write answer + all artifacts

Artifacts land in docs/edison-6dof/<slug>/. Never run `wait` in the background: the
GitHub Actions runner is destroyed as soon as the final comment is posted.
"""

import json
import os
import sys
import time
from pathlib import Path

from edison_client import EdisonClient, JobNames

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "edison-6dof"
TERMINAL = {"success", "fail", "failed", "cancelled", "error", "TaskStatus.SUCCESS"}


def client() -> EdisonClient:
    return EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])


def done(status: str) -> bool:
    s = status.lower().replace("taskstatus.", "")
    return s in {"success", "fail", "failed", "cancelled", "error"}


def submit(slug: str, prompt_file: str) -> None:
    d = OUT / slug
    d.mkdir(parents=True, exist_ok=True)
    query = Path(prompt_file).read_text()
    (d / "query.md").write_text(query)
    task = client().create_task({"name": JobNames.LITERATURE_HIGH, "query": query})
    task_id = getattr(task, "task_id", None) or getattr(task, "id", None) or str(task)
    (d / "_task_id.json").write_text(json.dumps({"task_id": task_id, "slug": slug}, indent=2))
    print("submitted", slug, "->", task_id, flush=True)


def wait(slug: str, interval: int = 60, budget: int = 3300) -> None:
    task_id = json.loads((OUT / slug / "_task_id.json").read_text())["task_id"]
    c, start = client(), time.time()
    while True:
        status = str(c.get_task(task_id=task_id).status)
        elapsed = int(time.time() - start)
        print(f"[{elapsed:>5}s] {slug}: {status}", flush=True)
        if done(status):
            print("TERMINAL", status, flush=True)
            return
        if time.time() - start > budget:
            print("BUDGET_EXCEEDED still-running", flush=True)
            return
        time.sleep(interval)


def _dump(obj):
    for attr in ("model_dump", "dict"):
        if hasattr(obj, attr):
            try:
                return getattr(obj, attr)()
            except Exception:
                pass
    return {k: v for k, v in vars(obj).items()} if hasattr(obj, "__dict__") else {"repr": repr(obj)}


def fetch(slug: str) -> None:
    d = OUT / slug
    task_id = json.loads((d / "_task_id.json").read_text())["task_id"]
    task = client().get_task(task_id=task_id, verbose=True)
    print("status:", task.status, flush=True)

    for name in ("answer", "formatted_answer"):
        val = getattr(task, name, None)
        if val:
            (d / f"{name}.md").write_text(str(val))
            print("wrote", name, len(str(val)), flush=True)

    raw = _dump(task)
    (d / "task.json").write_text(json.dumps(raw, indent=2, default=str))

    # environment_frame / trajectory artifacts, when the API exposes them
    for name in ("environment_frame", "trajectory", "steps", "metadata"):
        val = getattr(task, name, None)
        if val is not None:
            (d / f"{name}.json").write_text(json.dumps(_dump(val), indent=2, default=str))
            print("wrote", name, flush=True)
    print("fetched ->", d, flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "submit":
        submit(sys.argv[2], sys.argv[3])
    elif cmd == "wait":
        wait(sys.argv[2], *(int(a) for a in sys.argv[3:]))
    elif cmd == "fetch":
        fetch(sys.argv[2])
    else:
        raise SystemExit(f"unknown command {cmd}")
