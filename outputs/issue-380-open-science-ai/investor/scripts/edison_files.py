#!/usr/bin/env python3
"""Download every data-storage file an Edison trajectory created (list_files provenance API) into
edison/<key>_files/, mirroring its /workspace paths. Usage: edison_files.py <key> [<key> ...]"""
import json, os, pathlib, shutil, sys
from edison_client import EdisonClient
c = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
ids = json.load(open("edison/_task_ids.json"))
for key in sys.argv[1:]:
    tid = ids[key]["task_id"]; out = pathlib.Path(f"edison/{key}_files"); out.mkdir(parents=True, exist_ok=True)
    listing = c.list_files(trajectory_id=tid)
    json.dump(listing, open(out / "_listing.json", "w"), indent=1, default=str)
    for e in listing["data"]:
        ds = e.get("data_storage") or {}; did = ds.get("id") or e.get("data_storage_id")
        rel = (ds.get("file_path") or ds.get("name") or did).lstrip("/")
        rel = rel[len("workspace/"):] if rel.startswith("workspace/") else rel
        dest = out / rel; dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            continue
        try:
            r = c.fetch_data_from_storage(did)
        except Exception as ex:
            print("FAIL", rel, type(ex).__name__, str(ex)[:120]); continue
        if isinstance(r, pathlib.Path) and r.is_dir():
            shutil.copytree(r, dest.with_suffix(dest.suffix + ".d"), dirs_exist_ok=True)   # zipped collections arrive unpacked
        elif isinstance(r, pathlib.Path):
            shutil.copy(r, dest)
        elif isinstance(r, list):
            for p in r: shutil.copy(p, dest.parent / pathlib.Path(p).name)
        elif r is None:
            print("EMPTY", rel); continue
        else:
            body = getattr(r, "content", None)
            if body is None: body = json.dumps(r.model_dump(mode="json"), default=str)
            (dest.write_bytes(body) if isinstance(body, bytes) else dest.write_text(body if isinstance(body, str) else json.dumps(body, default=str)))
        print("ok", rel, dest.stat().st_size if dest.exists() else "")
