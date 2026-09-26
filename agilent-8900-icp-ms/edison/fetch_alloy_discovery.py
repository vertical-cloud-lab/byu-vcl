"""Fetch the alloy-discovery high-effort literature result into artifacts/.

Writes the formatted answer to artifacts/alloy_discovery.md. Safe to re-run; it
does nothing useful until the task is terminal.
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

    info = tasks.get("alloy_discovery")
    if not info or not info.get("task_id"):
        raise SystemExit("No alloy_discovery task submitted yet")

    resp = client.get_task(info["task_id"])
    status = getattr(resp, "status", None)
    print(f"[alloy_discovery] {info['task_id']} status={status}")
    info["status"] = str(status)

    answer = getattr(resp, "formatted_answer", None) or getattr(resp, "answer", None)
    if answer:
        out = ART / "alloy_discovery.md"
        out.write_text(answer)
        info["answer_file"] = out.name
        print(f"   wrote {out} ({len(answer)} chars)")
    else:
        print("   No answer available yet.")

    TASKS_FILE.write_text(json.dumps(tasks, indent=2))


if __name__ == "__main__":
    main()
