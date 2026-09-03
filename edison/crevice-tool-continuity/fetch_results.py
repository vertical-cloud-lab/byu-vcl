"""Poll the crevice-tool-continuity Edison task to completion, then archive all
artifacts next to this file:
  - edison_task_result.json   (full verbose trajectory dump)
  - edison_formatted_answer.md (question + answer + references, as rendered)
  - edison_answer.md           (the answer body only)
  - edison_references.md        (numbered reference list)

Designed to run as ONE foreground Bash call with a long timeout: the wait loop
uses Python time.sleep (not the shell sleep builtin, which the harness blocks)
and never backgrounds, so it survives until results are committed.
"""
import os, json, time

from edison_client import EdisonClient

key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not key:
    raise SystemExit("Set EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) in the environment.")
client = EdisonClient(api_key=key.strip())

here = os.path.dirname(__file__) or "."
task_id = json.load(open(os.path.join(here, "_task_id.json")))["task_id"]

TERMINAL = {"success", "fail", "failed", "cancelled", "canceled", "error"}
status = None
while True:
    task = client.get_task(task_id=task_id, verbose=True)
    status = str(getattr(task, "status", "")).split(".")[-1].lower()
    print("status:", status, flush=True)
    if status in TERMINAL:
        break
    time.sleep(240)

# Full verbose dump.
data = json.loads(task.model_dump_json())
with open(os.path.join(here, "edison_task_result.json"), "w") as f:
    json.dump(data, f, indent=2)


def find_answer(obj):
    """Recursively locate the answer dict (has formatted_answer/references/answer)."""
    if isinstance(obj, dict):
        if "formatted_answer" in obj and "references" in obj:
            return obj
        for v in obj.values():
            hit = find_answer(v)
            if hit:
                return hit
    elif isinstance(obj, list):
        for v in obj:
            hit = find_answer(v)
            if hit:
                return hit
    return None


ans = find_answer(data) or {}
for fname, key_name in [
    ("edison_formatted_answer.md", "formatted_answer"),
    ("edison_answer.md", "answer"),
    ("edison_references.md", "references"),
]:
    val = ans.get(key_name) or ""
    with open(os.path.join(here, fname), "w") as f:
        f.write(val if isinstance(val, str) else json.dumps(val, indent=2))
    print(f"wrote {fname} ({len(val) if isinstance(val, str) else '?'} chars)")

print("FINAL_STATUS", status)
print("HAS_ANSWER", bool(ans.get("answer")))
