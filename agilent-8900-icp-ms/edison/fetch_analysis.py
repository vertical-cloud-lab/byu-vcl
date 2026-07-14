"""Fetch the Edison ANALYSIS task result and write it into the repo.

ANALYSIS (Finch) responses put the synthesized answer at
environment_frame.state.state.answer; we fall back to the top-level
answer/formatted_answer fields if needed. Any output data files written by the
analysis agent are downloaded into artifacts/analysis/.

Safe to re-run in a later session; nothing happens until the task is terminal.
"""

import json
import os
from pathlib import Path

from edison_client import EdisonClient

HERE = Path(__file__).resolve().parent
TASKS_FILE = HERE / "tasks.json"

# Map each analysis task key to the artifact it writes.
OUTPUTS = {
    "analysis": HERE / "artifacts" / "analysis_synthesis.md",
    "analysis_hf_free": HERE / "artifacts" / "analysis_synthesis_hf_free.md",
}


def get_client() -> EdisonClient:
    key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
    if not key:
        raise SystemExit("No Edison API key found in environment")
    return EdisonClient(api_key=key)


def extract_answer(resp) -> str | None:
    # Preferred path for Finch/ANALYSIS responses.
    try:
        ans = resp.environment_frame.state.state.answer
        if ans:
            return ans
    except AttributeError:
        pass
    return getattr(resp, "answer", None) or getattr(resp, "formatted_answer", None)


def main() -> None:
    client = get_client()
    tasks = json.loads(TASKS_FILE.read_text())

    for key, out in OUTPUTS.items():
        info = tasks.get(key)
        if not info or not info.get("task_id"):
            continue
        task_id = info["task_id"]
        resp = client.get_task(task_id)
        status = getattr(resp, "status", None)
        print(f"[{key}] {task_id} status={status}")

        answer = extract_answer(resp)
        if answer:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(answer)
            print(f"   wrote {out} ({len(answer)} chars)")
        else:
            print("   No answer available yet.")

        info["status"] = str(status)
        TASKS_FILE.write_text(json.dumps(tasks, indent=2))


if __name__ == "__main__":
    main()
