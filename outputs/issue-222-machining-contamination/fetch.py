"""Wait for the Edison tasks in _task_id.json, then save every artifact next to this file.

Blocks in Python (time.sleep), so run it as one foreground call (see CLAUDE.md).
"""
import json
import os
import time
from pathlib import Path

from edison_client import EdisonClient

HERE = Path(__file__).parent
DONE = {"success", "fail", "failed", "cancelled", "error"}

client = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
ids = json.loads((HERE / "_task_id.json").read_text())
deadline = time.time() + float(os.environ.get("EDISON_WAIT_S", 1500))
pending = dict(ids)
while pending and time.time() < deadline:
    for key, tid in list(pending.items()):
        task = client.get_task(task_id=tid, verbose=True)
        status = str(task.status)
        print(time.strftime("%H:%M:%S"), key, status, flush=True)
        if status in DONE:
            data = task.model_dump(mode="json")
            (HERE / f"{key}_task.json").write_text(json.dumps(data, indent=1) + "\n")
            ans = data["environment_frame"]["state"]["state"]["response"]["answer"]
            (HERE / f"{key}_answer.md").write_text(ans.get("formatted_answer") or ans.get("answer") or "")
            (HERE / f"{key}_references.md").write_text(ans.get("references") or "")
            del pending[key]
    if pending:
        time.sleep(60)
print("still pending:", list(pending))
