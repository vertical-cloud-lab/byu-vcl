#!/usr/bin/env python3
"""Fetch finished Edison tasks listed in edison/_task_ids.json and save every artifact.

For each finished task: <key>_task.json (full verbose response), <key>_answer.md (formatted
answer) and <key>_references.md (references, if returned separately). Already-saved tasks
are skipped. Run with the Python 3.12 venv that has edison-client.
"""
import json, os, sys
from edison_client import EdisonClient
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "edison")
c = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
ids = json.load(open(os.path.join(D, "_task_ids.json")))
for k, v in ids.items():
    if os.path.exists(os.path.join(D, f"{k}_task.json")):
        continue
    t = c.get_task(task_id=v["task_id"], verbose=True)
    st = str(t.status)
    if st not in {"success", "fail", "failed", "cancelled", "error"}:
        print(k, st); continue
    d = t.model_dump(mode="json")
    json.dump(d, open(os.path.join(D, f"{k}_task.json"), "w"), indent=1, default=str)
    env = d.get("environment_frame") or {}
    state = (env.get("state") or {}).get("state") or {}
    resp = state.get("response") or {}
    ans = resp.get("answer") or {}
    formatted = ans.get("formatted_answer") or d.get("formatted_answer") or ans.get("answer") or d.get("answer") or ""
    refs = ans.get("references") or ""
    with open(os.path.join(D, f"{k}_answer.md"), "w") as f:
        f.write(f"# Edison {v['job']}: {k}\n\nTask `{v['task_id']}` · status {st}\n\n**Query.** {v['query']}\n\n---\n\n{formatted}\n")
    if refs:
        open(os.path.join(D, f"{k}_references.md"), "w").write(refs)
    print(k, st, "answer chars", len(formatted), "refs chars", len(refs))
