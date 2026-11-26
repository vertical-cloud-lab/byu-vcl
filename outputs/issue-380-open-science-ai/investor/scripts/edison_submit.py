#!/usr/bin/env python3
"""Submit the Edison jobs in edison/queries.json that have no task id yet; record ids in edison/_task_ids.json.

Analysis jobs upload their listed files first (from the folder given by --files-dir) and attach the
data-entry URIs. Run from investor/ with the Python 3.12 venv that has edison-client.
"""
import argparse, datetime as dt, json, os
from edison_client import EdisonClient, JobNames

ap = argparse.ArgumentParser()
ap.add_argument("--files-dir", default="edison/uploads")
ap.add_argument("--only", nargs="*")
a = ap.parse_args()
Q = json.load(open("edison/queries.json"))
P = "edison/_task_ids.json"
ids = json.load(open(P)) if os.path.exists(P) else {}
c = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
for k, v in Q.items():
    if k in ids or (a.only and k not in a.only):
        continue
    job = getattr(JobNames, v["job"])
    uris = []
    for f in v.get("files", []):
        uris.append(c.upload_file(os.path.join(a.files_dir, f), name=f))
    req = {"name": job, "query": v["query"]}
    tid = c.create_task(req, files=uris or None)
    ids[k] = {"task_id": str(tid), "job": job.value, "query": v["query"], "files": v.get("files", []),
              "data_entries": uris, "submitted_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    json.dump(ids, open(P, "w"), indent=1)
    print(k, "submitted", job.value, len(uris), "files")
