"""Poll the per-alloy literature tasks and download finished answers.

Writes each finished answer to artifacts/alloys/<slug>.md and records status in
alloy_tasks.json. Safe to re-run across sessions; it picks up whatever has
finished so far and reports how many are still in progress.
"""

import json
import os
from pathlib import Path

from edison_client import EdisonClient

HERE = Path(__file__).resolve().parent
ALLOY_TASKS = HERE / "alloy_tasks.json"
ART = HERE / "artifacts" / "alloys"


def get_client() -> EdisonClient:
    key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
    if not key:
        raise SystemExit("No Edison API key found in environment")
    return EdisonClient(api_key=key)


def main() -> None:
    if not ALLOY_TASKS.exists():
        raise SystemExit(f"{ALLOY_TASKS} not found; run submit_alloy_queries.py first")
    tasks = json.loads(ALLOY_TASKS.read_text())
    ART.mkdir(parents=True, exist_ok=True)
    client = get_client()

    done = 0
    pending = 0
    for key, info in tasks.items():
        out = ART / f"{key}.md"
        # Skip work already fetched, unless the file is missing.
        if info.get("status") == "success" and out.exists():
            done += 1
            continue
        try:
            resp = client.get_task(info["task_id"])
        except Exception as exc:  # noqa: BLE001
            print(f"[err] {key} {info['task_id']}: {exc}")
            continue
        status = str(getattr(resp, "status", None))
        info["status"] = status
        answer = getattr(resp, "formatted_answer", None) or getattr(resp, "answer", None)
        if answer and status == "success":
            out.write_text(answer)
            info["answer_file"] = out.name
            done += 1
            print(f"[done] {key} ({len(answer)} chars)")
        else:
            pending += 1
            print(f"[wait] {key} status={status}")

    ALLOY_TASKS.write_text(json.dumps(tasks, indent=2))
    print(f"\n{done} finished, {pending} still pending of {len(tasks)} alloys")


if __name__ == "__main__":
    main()
