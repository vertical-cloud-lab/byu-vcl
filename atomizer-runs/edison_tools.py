#!/usr/bin/env python3
"""Submit, wait for and fetch Edison Scientific literature tasks for a run record.

    python atomizer-runs/edison_tools.py submit <dir>   # <dir>/queries.json -> <dir>/_task_ids.json
    python atomizer-runs/edison_tools.py wait <dir>     # one blocking call; polls every 4 min
    python atomizer-runs/edison_tools.py fetch <dir>    # <slug>.json (verbose trajectory) + <slug>-answer.md

queries.json: {"issue": N, "tasks": [{"slug": ..., "job_type": "LITERATURE_HIGH", "query": ...}, ...]}
The API key is read from EDISON_PLATFORM_API_KEY and is never printed.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from edison_client import EdisonClient, JobNames

DONE = {"success", "fail", "failed", "cancelled", "error"}


def client():
    return EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])


def submit(d: Path):
    q = json.loads((d / "queries.json").read_text())
    c = client()
    out = {"issue": q.get("issue"), "submitted_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "tasks": []}
    for t in q["tasks"]:
        task_id = c.create_task({"name": getattr(JobNames, t["job_type"]), "query": t["query"]})
        out["tasks"].append({"slug": t["slug"], "job_type": t["job_type"], "task_id": str(task_id), "query": t["query"]})
        print("submitted", t["slug"], t["job_type"], "id length", len(str(task_id)), flush=True)
    (d / "_task_ids.json").write_text(json.dumps(out, indent=2) + "\n")


def statuses(c, tasks):
    return {t["slug"]: str(c.get_task(task_id=t["task_id"]).status) for t in tasks}


def wait(d: Path, every=240):
    tasks = json.loads((d / "_task_ids.json").read_text())["tasks"]
    c = client()
    while True:
        s = statuses(c, tasks)
        print(datetime.now(timezone.utc).strftime("%H:%M:%SZ"), s, flush=True)
        if all(v in DONE for v in s.values()):
            return
        time.sleep(every)


def to_jsonable(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    return json.loads(json.dumps(obj, default=str))


def fetch(d: Path):
    meta = json.loads((d / "_task_ids.json").read_text())
    c = client()
    for t in meta["tasks"]:
        try:
            task = c.get_task(task_id=t["task_id"], verbose=True)
        except Exception as e:  # transient 503s happen; leave the task for the next fetch
            print("skipped", t["slug"], type(e).__name__, flush=True)
            continue
        if str(getattr(task, "status", "")) not in DONE:
            print("not finished", t["slug"], str(getattr(task, "status", "")), flush=True)
            continue
        data = to_jsonable(task)
        (d / f"{t['slug']}.json").write_text(json.dumps(data, indent=2) + "\n")
        status = str(getattr(task, "status", ""))
        answer = getattr(task, "formatted_answer", None) or getattr(task, "answer", None) or ""
        if not answer:  # PRECEDENT and some LITERATURE responses only carry the answer inside the environment frame
            try:
                a = data["environment_frame"]["state"]["state"]["response"]["answer"]
                answer = a.get("formatted_answer") or a.get("answer") or ""
            except (KeyError, TypeError):
                answer = ""
        head = f"# {t['slug']}\n\nEdison Scientific `{t['job_type']}` task `{t['task_id']}`, status `{status}`.\n\n## Query\n\n{t['query']}\n\n## Answer\n\n"
        (d / f"{t['slug']}-answer.md").write_text(head + answer.strip() + "\n")
        t["status"] = status
        print("fetched", t["slug"], status, "answer chars", len(answer), flush=True)
    (d / "_task_ids.json").write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    cmd, d = sys.argv[1], Path(sys.argv[2])
    {"submit": submit, "wait": wait, "fetch": fetch}[cmd](d)
