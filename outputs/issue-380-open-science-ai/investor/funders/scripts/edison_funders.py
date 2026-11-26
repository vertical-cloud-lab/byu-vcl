#!/usr/bin/env python3
"""Submit (`submit`) or fetch (`fetch [--wait]`) this part's Edison jobs: edison/queries.json -> edison/_task_ids.json.

Same artifacts as ../scripts/edison_fetch.py: <key>_task.json (full verbose response with the trajectory),
<key>_answer.md and <key>_references.md. Run from funders/ with the Python 3.12 venv that has edison-client.
"""
import argparse, datetime as dt, json, os, time
from edison_client import EdisonClient, JobNames

ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["submit", "fetch"])
ap.add_argument("--wait", action="store_true"); ap.add_argument("--max-minutes", type=float, default=40)
ap.add_argument("--poll", type=int, default=120); ap.add_argument("--files-dir", default="edison/uploads")
a = ap.parse_args()
D = "edison"; P = os.path.join(D, "_task_ids.json"); DONE = {"success", "fail", "failed", "cancelled", "error"}
c = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
ids = json.load(open(P)) if os.path.exists(P) else {}
if a.cmd == "submit":
    for k, v in json.load(open(os.path.join(D, "queries.json"))).items():
        if k in ids:
            continue
        job = getattr(JobNames, v["job"])
        uris = [c.upload_file(os.path.join(a.files_dir, f), name=f) for f in v.get("files", [])]
        tid = c.create_task({"name": job, "query": v["query"]}, files=uris or None)
        ids[k] = {"task_id": str(tid), "job": job.value, "query": v["query"], "files": v.get("files", []),
                  "data_entries": uris, "submitted_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
        json.dump(ids, open(P, "w"), indent=1)
        print(k, "submitted", job.value, len(uris), "files")
    raise SystemExit
t0 = time.time()
while True:
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
        state = ((d.get("environment_frame") or {}).get("state") or {}).get("state") or {}
        ans = (state.get("response") or {}).get("answer") or {}
        text = ans.get("formatted_answer") or d.get("formatted_answer") or ans.get("answer") or d.get("answer") or ""
        if not text and isinstance(state.get("answer"), str):
            text = state["answer"]
        refs = ans.get("references") or ""
        with open(os.path.join(D, f"{k}_answer.md"), "w") as f:
            f.write(f"# Edison {v['job']}: {k}\n\nTask `{v['task_id']}` · status {st} · files attached: "
                    f"{', '.join(v.get('files', [])) or 'none'}\n\n**Query.** {v['query']}\n\n---\n\n{text}\n")
        if refs:
            open(os.path.join(D, f"{k}_references.md"), "w").write(refs if isinstance(refs, str) else json.dumps(refs, indent=1))
        print(time.strftime("%H:%M:%S"), k, st, "answer chars", len(text), flush=True)
    if not a.wait or not pending or (time.time() - t0) / 60 > a.max_minutes:
        print(time.strftime("%H:%M:%S"), "pending:", pending, flush=True); break
    print(time.strftime("%H:%M:%S"), "waiting on", len(pending), flush=True)
    time.sleep(a.poll)
