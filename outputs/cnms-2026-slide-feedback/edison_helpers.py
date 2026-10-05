"""Shared helpers for the CNMS 2026 slide-feedback Edison iteration loop (PR #176).

Submit + poll + fetch are separate entry points so the (long) poll can run as a
single blocking foreground call per repo CLAUDE.md rules.
"""

import json
import os
import sys
import time
from pathlib import Path

from edison_client import EdisonClient, JobNames

OUT = Path(__file__).resolve().parent

TERMINAL = {"success", "fail", "failed", "cancelled", "error"}


def client() -> EdisonClient:
    return EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])


def submit(iter_name: str, job_name: str, query: str, file_paths=None) -> str:
    c = client()
    uploaded = []
    for p in file_paths or []:
        try:
            uri = c.upload_file(p, name=Path(p).name)
            uploaded.append(uri)
            print("uploaded:", Path(p).name, "->", uri, flush=True)
        except Exception as e:  # noqa: BLE001 - fall back to fewer attachments
            print("UPLOAD FAILED (continuing):", Path(p).name, type(e).__name__, e, flush=True)
    task_id = c.create_task(
        {"name": job_name, "query": query},
        files=uploaded or None,
    )
    d = OUT / iter_name
    d.mkdir(parents=True, exist_ok=True)
    (d / "_task_id.json").write_text(json.dumps(
        {"task_id": str(task_id), "job": job_name, "uploaded": uploaded}, indent=2))
    (d / "query.md").write_text(query)
    print("SUBMITTED", iter_name, "task_id:", task_id, flush=True)
    return str(task_id)


def wait(iter_name: str, poll_s: int = 240, max_s: int = 3300) -> str:
    d = OUT / iter_name
    task_id = json.loads((d / "_task_id.json").read_text())["task_id"]
    c = client()
    t0 = time.time()
    while True:
        task = c.get_task(task_id=task_id, verbose=True)
        status = str(getattr(task, "status", "unknown"))
        print(f"[{int(time.time()-t0)}s] status: {status}", flush=True)
        if status in TERMINAL:
            break
        if time.time() - t0 > max_s:
            print("TIMEBOX reached, still running", flush=True)
            return "timeout"
        time.sleep(poll_s)
    fetch(iter_name, task)
    return status


def fetch(iter_name: str, task=None) -> None:
    d = OUT / iter_name
    task_id = json.loads((d / "_task_id.json").read_text())["task_id"]
    if task is None:
        task = client().get_task(task_id=task_id, verbose=True)
    # dump everything serializable
    try:
        raw = task.model_dump(mode="json")
    except Exception:
        raw = {k: str(v) for k, v in vars(task).items()}
    (d / "task_raw.json").write_text(json.dumps(raw, indent=2, default=str))
    answer = None
    for attr in ("formatted_answer", "answer", "response"):
        v = getattr(task, attr, None) or (raw.get(attr) if isinstance(raw, dict) else None)
        if v:
            answer = v if isinstance(v, str) else json.dumps(v, indent=2, default=str)
            break
    if answer:
        (d / "answer.md").write_text(answer)
        print("answer saved:", len(answer), "chars", flush=True)
    else:
        print("NO ANSWER FIELD FOUND — inspect task_raw.json", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "wait":
        status = wait(sys.argv[2], max_s=int(sys.argv[3]) if len(sys.argv) > 3 else 3300)
        print("FINAL:", status)
    elif cmd == "fetch":
        fetch(sys.argv[2])
