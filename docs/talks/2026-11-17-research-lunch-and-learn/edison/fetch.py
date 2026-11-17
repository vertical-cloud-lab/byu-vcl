"""Fetch finished Edison tasks listed in _task_ids.json and save every artifact.

    python -I fetch.py            # from this directory; needs EDISON_PLATFORM_API_KEY

For each finished task <key> it writes:
    <key>.md         the answer, with the question and the reference list
    <key>.json.gz    the whole task record as returned by the API (answer, contexts,
                     tool history, artifacts), gzipped, so nothing from the trajectory is lost
"""

import gzip
import json
import os
from pathlib import Path

from edison_client import EdisonClient

HERE = Path(__file__).resolve().parent


def main():
    client = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
    ids = json.loads((HERE / "_task_ids.json").read_text())
    for key, meta in ids.items():
        task = client.get_task(task_id=meta["task_id"], verbose=True)
        status = str(task.status)
        print(key, status)
        if status != "success":
            continue
        record = task.model_dump(mode="json")
        with gzip.open(HERE / f"{key}.json.gz", "wt", encoding="utf-8") as fh:
            json.dump(record, fh, default=str)
        ans = record["environment_frame"]["state"]["state"]["response"]["answer"]
        md = [
            f"<!-- Edison {meta['job']} task {meta['task_id']}, submitted {meta['submitted_utc']}. "
            f"Full record: {key}.json.gz -->",
            "",
            f"**Question.** {meta['query']}",
            "",
            ans.get("answer") or ans.get("formatted_answer") or "",
            "",
            "## References",
            "",
            ans.get("references") or "",
        ]
        (HERE / f"{key}.md").write_text("\n".join(md).rstrip() + "\n")


if __name__ == "__main__":
    main()
