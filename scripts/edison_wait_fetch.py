#!/usr/bin/env python3
"""Block until a set of Edison tasks finish, then write every artifact to disk.

Usage:
    python scripts/edison_wait_fetch.py outputs/<dir>            # wait, then fetch
    python scripts/edison_wait_fetch.py outputs/<dir> --fetch-only

The directory must contain a ``_task_id.json`` of the form::

    {"job": "job-futurehouse-paperqa3-high",
     "tasks": {"<label>": "<task-id>", ...}}

The wait loop lives inside this process on purpose. Per CLAUDE.md, an Edison
wait must never run in the background on a GitHub Actions runner: the runner is
destroyed as soon as the agent posts its comment, which kills any background
process. Run this as a single foreground call with a long timeout instead.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time

from edison_client import EdisonClient

TERMINAL = {"success", "fail", "failed", "cancelled", "canceled", "error", "crashed"}
POLL_SECONDS = 120


def _status(task) -> str:
    """Normalize a task's status to a bare lowercase word."""
    raw = str(getattr(task, "status", "") or "")
    return raw.rsplit(".", 1)[-1].lower()


def _dump(path: pathlib.Path, obj) -> None:
    """Serialize a pydantic model or plain object to pretty JSON."""
    if hasattr(obj, "model_dump_json"):
        path.write_text(obj.model_dump_json(indent=2))
    else:
        path.write_text(json.dumps(obj, indent=2, default=str))


def wait(client: EdisonClient, tasks: dict[str, str], deadline: float) -> dict[str, str]:
    """Poll until every task is terminal or the deadline passes."""
    final: dict[str, str] = {}
    while len(final) < len(tasks) and time.time() < deadline:
        for label, task_id in tasks.items():
            if label in final:
                continue
            status = _status(client.get_task(task_id=task_id))
            print(f"  {label}: {status}", flush=True)
            if status in TERMINAL:
                final[label] = status
        if len(final) == len(tasks):
            break
        remaining = int(deadline - time.time())
        print(f"-- sleeping {POLL_SECONDS}s ({remaining}s of budget left)", flush=True)
        time.sleep(POLL_SECONDS)
    for label in tasks:
        final.setdefault(label, "timed-out-waiting")
    return final


def _answer_payload(traj: dict) -> dict:
    """Dig the PaperQA answer object out of a verbose trajectory.

    For paperqa3 jobs it is buried at
    ``environment_frame.state.state.response.answer`` rather than being exposed
    as a top-level attribute on the task model.
    """
    node = traj
    for key in ("environment_frame", "state", "state", "response", "answer"):
        if not isinstance(node, dict):
            return {}
        node = node.get(key)  # type: ignore[assignment]
    return node if isinstance(node, dict) else {}


def fetch(client: EdisonClient, outdir: pathlib.Path, tasks: dict[str, str]) -> None:
    """Write the verbose trajectory, the prose answer, and any files, per task."""
    for label, task_id in tasks.items():
        print(f"\n=== fetching {label} ({task_id}) ===", flush=True)
        try:
            task = client.get_task(task_id=task_id, verbose=True)
        except Exception as exc:  # noqa: BLE001 - keep going for the other tasks
            print(f"  get_task failed: {exc}", flush=True)
            continue

        _dump(outdir / f"{label}.trajectory.json", task)
        print(f"  status: {_status(task)}", flush=True)

        traj = json.loads(json.dumps(task, default=lambda o: getattr(o, "__dict__", str(o))))
        if hasattr(task, "model_dump"):
            traj = json.loads(task.model_dump_json())
        payload = _answer_payload(traj)

        for key, ext in (
            ("formatted_answer", "md"),
            ("answer", "md"),
            ("references", "md"),
        ):
            text = payload.get(key)
            if isinstance(text, str) and text.strip():
                (outdir / f"{label}.{key}.{ext}").write_text(text)
                print(f"  wrote {label}.{key}.{ext} ({len(text)} chars)", flush=True)

        for key in ("artifacts", "used_contexts", "tool_history"):
            if payload.get(key):
                _dump(outdir / f"{label}.{key}.json", payload[key])
                print(f"  wrote {label}.{key}.json", flush=True)

        env_frame = getattr(task, "environment_frame", None)
        if env_frame is not None:
            _dump(outdir / f"{label}.environment_frame.json", env_frame)

        try:
            files = client.list_files(trajectory_id=task_id)
        except Exception as exc:  # noqa: BLE001
            print(f"  list_files failed: {exc}", flush=True)
            continue
        if files:
            _dump(outdir / f"{label}.files.json", files)
            print(f"  file manifest entries: {len(files.get('data', []))}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir", type=pathlib.Path)
    ap.add_argument("--fetch-only", action="store_true")
    ap.add_argument(
        "--budget-seconds",
        type=int,
        default=1800,
        help="how long to keep polling before giving up (default 1800)",
    )
    args = ap.parse_args()

    info = json.loads((args.outdir / "_task_id.json").read_text())
    tasks = info["tasks"] if "tasks" in info else {"task": info["task_id"]}

    client = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])

    if not args.fetch_only:
        statuses = wait(client, tasks, deadline=time.time() + args.budget_seconds)
        print(f"\nfinal statuses: {statuses}", flush=True)
        info["statuses"] = statuses
        (args.outdir / "_task_id.json").write_text(json.dumps(info, indent=2) + "\n")

    fetch(client, args.outdir, tasks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
