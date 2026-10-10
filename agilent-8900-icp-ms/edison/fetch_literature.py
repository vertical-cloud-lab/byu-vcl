"""Poll the submitted Edison literature tasks and download their artifacts.

Writes each task's formatted answer to artifacts/<key>.md and downloads any
data-storage artifacts referenced by the task. Safe to re-run; it picks up
whatever has finished so far.
"""

import json
import os
from pathlib import Path

from edison_client import EdisonClient

HERE = Path(__file__).resolve().parent
TASKS_FILE = HERE / "tasks.json"
ART = HERE / "artifacts"


def get_client() -> EdisonClient:
    key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
    if not key:
        raise SystemExit("No Edison API key found in environment")
    return EdisonClient(api_key=key)


def main() -> None:
    client = get_client()
    ART.mkdir(parents=True, exist_ok=True)
    tasks = json.loads(TASKS_FILE.read_text())

    for key, info in tasks.items():
        # ANALYSIS tasks have their own fetcher (fetch_analysis.py); skip any of
        # them here so we don't write duplicate artifacts.
        if key.startswith("analysis"):
            continue
        task_id = info["task_id"]
        try:
            resp = client.get_task(task_id)
        except Exception as exc:  # noqa: BLE001
            print(f"[err] {key} {task_id}: {exc}")
            continue

        status = getattr(resp, "status", None)
        print(f"[{key}] {task_id} status={status}")
        info["status"] = str(status)

        answer = (
            getattr(resp, "formatted_answer", None)
            or getattr(resp, "answer", None)
        )
        if answer:
            out = ART / f"{key}.md"
            out.write_text(answer)
            info["answer_file"] = out.name
            print(f"   wrote {out} ({len(answer)} chars)")

    TASKS_FILE.write_text(json.dumps(tasks, indent=2))


if __name__ == "__main__":
    main()
