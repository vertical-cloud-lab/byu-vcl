#!/usr/bin/env python3
"""Submit / wait on / fetch the Edison Scientific literature tasks for issue #213.

Usage:
    python scripts/edison_sdl_futures.py wait [max_seconds]
    python scripts/edison_sdl_futures.py fetch

The five queries ask about state of the art and future directions for closed-loop
electrolyte-formulation workflows (dosing + conductivity + spectroscopy) in the
self-driving-lab space. Task IDs live in outputs/edison-sdl-futures/_task_ids.json
so a later session can pick the results up even if this runner dies.

Per CLAUDE.md the wait MUST happen inside a single blocking foreground call --
never background the poller, the runner is destroyed when the final comment posts.
"""
import json
import os
import pathlib
import sys
import time

from edison_client import EdisonClient

OUT = pathlib.Path("outputs/edison-sdl-futures")
TERMINAL = {"success", "fail", "failed", "cancelled", "error"}


def _client():
    return EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])


def _ids():
    return json.loads((OUT / "_task_ids.json").read_text())


def wait(max_seconds=2400, interval=60):
    client, ids = _client(), _ids()
    deadline = time.time() + float(max_seconds)
    pending = dict(ids)
    while pending and time.time() < deadline:
        done = []
        for key, meta in pending.items():
            status = str(client.get_task(task_id=meta["task_id"]).status).split(".")[-1].lower()
            print(f"  {key}: {status}", flush=True)
            if status in TERMINAL:
                done.append(key)
        for key in done:
            pending.pop(key)
        if pending:
            print(f"-- {len(pending)} still running, sleeping {interval}s --", flush=True)
            time.sleep(interval)
    print("still pending:", list(pending), flush=True)
    return not pending


def fetch():
    client, ids = _client(), _ids()
    for key, meta in ids.items():
        task = client.get_task(task_id=meta["task_id"], verbose=True)
        blob = task.model_dump(mode="json") if hasattr(task, "model_dump") else dict(task)
        (OUT / f"{key}.json").write_text(json.dumps(blob, indent=2, default=str))
        answer = (blob.get("environment_frame") or {}).get("state", {}).get("state", {})
        text = answer.get("answer") or answer.get("formatted_answer") or ""
        if text:
            (OUT / f"{key}.md").write_text(text)
        print(f"fetched {key}: status={blob.get('status')} answer_chars={len(text)}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "wait"
    if cmd == "wait":
        wait(*(sys.argv[2:3] or []))
    elif cmd == "fetch":
        fetch()
    else:
        raise SystemExit(f"unknown command {cmd}")
