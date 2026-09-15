"""Write an Edison task's answer and every trajectory artifact to docs/edison-6dof/<slug>/.

The verbose task response nests the real payload at
environment_frame["state"]["state"]["response"]["answer"]; `task.answer` does not exist.
Splits that dict so long text fields become .md files and everything else .json, matching
the layout the Q1 fetch produced.
"""

import json
import os
import sys
from pathlib import Path

from edison_client import EdisonClient

OUT = Path(__file__).resolve().parent.parent / "docs" / "edison-6dof"
TEXT_FIELDS = {"answer", "raw_answer", "formatted_answer", "question"}


def main(slug: str) -> None:
    d = OUT / slug
    task_id = json.loads((d / "_task_id.json").read_text())["task_id"]
    client = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
    task = client.get_task(task_id=task_id, verbose=True)
    print("status:", task.status, flush=True)

    state = task.environment_frame["state"]["state"]
    (d / "cost.json").write_text(json.dumps(state.get("cost"), indent=2, default=str))

    answer = state["response"]["answer"]
    for key, val in answer.items():
        if key in TEXT_FIELDS and isinstance(val, str):
            (d / f"{key}.md").write_text(val)
        else:
            (d / f"{key}.json").write_text(json.dumps(val, indent=2, default=str))
        size = len(val) if hasattr(val, "__len__") else 0
        print(f"  {key}: {size}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
