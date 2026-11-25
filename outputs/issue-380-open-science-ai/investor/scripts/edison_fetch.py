#!/usr/bin/env python3
"""Fetch finished Edison tasks listed in edison/_task_ids.json and save every artifact.

For each finished task: <key>_task.json (full verbose response, including the trajectory),
<key>_answer.md (formatted answer with the exact query) and <key>_references.md (if returned separately).
Already-saved tasks are skipped. With --wait, loops (Python-side sleep, foreground) until every task has
finished or --max-minutes has passed. Run from investor/ with the Python 3.12 venv that has edison-client."""
import argparse, json, os, time
from edison_client import EdisonClient
ap = argparse.ArgumentParser(); ap.add_argument("--wait", action="store_true"); ap.add_argument("--max-minutes", type=float, default=40)
ap.add_argument("--poll", type=int, default=120); a = ap.parse_args()
D = "edison"; DONE = {"success", "fail", "failed", "cancelled", "error"}
c = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
t0 = time.time()
while True:
    ids = json.load(open(os.path.join(D, "_task_ids.json")))
    pending = []
    for k, v in ids.items():
        if os.path.exists(os.path.join(D, f"{k}_task.json")):
            continue
        t = c.get_task(task_id=v["task_id"], verbose=True)
        st = str(t.status)
        if st not in DONE:
            pending.append(k); continue
        d = t.model_dump(mode="json")
        json.dump(d, open(os.path.join(D, f"{k}_task.json"), "w"), indent=1, default=str)
        env = d.get("environment_frame") or {}
        state = (env.get("state") or {}).get("state") or {}
        resp = state.get("response") or {}
        ans = resp.get("answer") or {}
        formatted = ans.get("formatted_answer") or d.get("formatted_answer") or ans.get("answer") or d.get("answer") or ""
        refs = ans.get("references") or ""
        files = ", ".join(v.get("files", [])) or "none"
        with open(os.path.join(D, f"{k}_answer.md"), "w") as f:
            f.write(f"# Edison {v['job']}: {k}\n\nTask `{v['task_id']}` · status {st} · files attached: {files}\n\n"
                    f"**Query.** {v['query']}\n\n---\n\n{formatted}\n")
        if refs:
            open(os.path.join(D, f"{k}_references.md"), "w").write(refs if isinstance(refs, str) else json.dumps(refs, indent=1))
        print(time.strftime("%H:%M:%S"), k, st, "answer chars", len(formatted), "refs chars", len(str(refs)), flush=True)
    if not a.wait or not pending or (time.time() - t0) / 60 > a.max_minutes:
        print(time.strftime("%H:%M:%S"), "pending:", pending, flush=True); break
    print(time.strftime("%H:%M:%S"), "waiting on", len(pending), flush=True)
    time.sleep(a.poll)
