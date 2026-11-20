#!/usr/bin/env python3
"""The existing clips audited with the base cameras in place (#364): what the cameras changed.

Each clip ran as ``ARM_AUDIT=1 ARM_AUDIT_TAG=basecams`` (nothing rendered; the joint moves planned round everything
drawn, the cameras now included; the round-11 strict rules), writing out/collisions/<clip>_basecams.json. This reads
them and counts, per clip, the frames whose collisions involve a camera part (a run whose touched bodies include an
"amr cam" part, or a mover run with one), next to all the frames in collision and the clip's committed audit:

    python3 base_cams_audit.py            # -> out/collisions/basecams_summary.json, and a table on stdout
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLL = HERE / "out" / "collisions"
CLIPS = ["alloy_charge", "alloy_atomize", "alloy_powder", "alloy_prep", "alloy_print", "alloy_characterize",
         "alloy_workflow", "vlm_workflow", "bay_camera", "upkeep_clip", "atom_bn", "atom_container", "atom_crucible_in",
         "atom_crucible_out", "atom_latch", "atom_plate", "atom_vacuum"]
# the committed audit each is compared with (the latest strict one on the branch)
BASE = {"alloy_powder": "alloy_powder_r13fix15", "alloy_print": "alloy_print_r13fix15",
        "atom_container": "atom_container_r13fix", "atom_crucible_in": "atom_crucible_in_r13fix",
        "atom_latch": "atom_latch_r13fix", "atom_plate": "atom_plate_r13fix", "atom_vacuum": "atom_vacuum_r13fix",
        "bay_camera": "bay_camera_r11"}


def cam(name: str) -> bool:
    return "amr cam " in str(name) or "/amr cam" in str(name)


def summary() -> dict:
    out = {}
    for c in CLIPS:
        p = COLL / f"{c}_basecams.json"
        if not p.exists():
            out[c] = dict(missing=True)
            continue
        d = json.loads(p.read_text())
        cam_runs = [r for r in d["runs"] if any(cam(b) for b in r.get("bodies", []))]
        mv = d.get("movers") or {}
        cam_mv = [r for r in mv.get("runs", []) if any(cam(q.get("body")) or cam(q.get("other")) for q in r["pairs"])]
        b = COLL / f"{BASE.get(c, c)}.json"
        base = json.loads(b.read_text()) if b.exists() else None
        nc = COLL / f"{c}_nocams.json"          # the same audit with VLAB_BASE_CAMS=0, where it was run
        nocams = json.loads(nc.read_text()) if nc.exists() else None
        out[c] = dict(fps=d["fps"], frames=d["frames_checked"], arm_frames_in_collision=d["frames_with_collisions"],
                      all_frames_in_collision=d.get("frames_with_collisions_all"),
                      camera_frames=sum(r["frames"] for r in cam_runs) + sum(r["frames"] for r in cam_mv),
                      camera_runs=[dict(label=r["label"], frames=r["frames"], first=r["first_frame"],
                                        bodies=[x for x in r.get("bodies", []) if cam(x)],
                                        parts=sorted({q["part"] for q in r["pairs"]})) for r in cam_runs] +
                                  [dict(label=r["label"], frames=r["frames"], first=r["first_frame"], mover=True,
                                        pairs=[(q["body"], q["other"]) for q in r["pairs"][:4]]) for r in cam_mv],
                      committed=dict(file=b.name, fps=base.get("fps"), arm_frames_in_collision=base.get("frames_with_collisions"),
                                     all_frames_in_collision=base.get("frames_with_collisions_all"))
                      if base else None,
                      nocams=dict(file=nc.name, fps=nocams.get("fps"), arm_frames_in_collision=nocams["frames_with_collisions"],
                                  all_frames_in_collision=nocams.get("frames_with_collisions_all")) if nocams else None)
    return out


if __name__ == "__main__":
    s = summary()
    (COLL / "basecams_summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print("| Clip | frames (15 fps) | touching a camera part | in collision with the cameras: arm (all) | the same "
          "without them (`VLAB_BASE_CAMS=0`): arm (all) | the committed audit: arm (all) |")
    print("|---|---|---|---|---|---|")
    for c, r in s.items():
        if r.get("missing"):
            print(f"| `{c}` | not run | | | | |")
            continue
        cm, nc = r["committed"], r["nocams"]
        print(f"| `{c}` | {r['frames']:,} | **{r['camera_frames']}** | {r['arm_frames_in_collision']} "
              f"({r['all_frames_in_collision']}) | " +
              (f"{nc['arm_frames_in_collision']} ({nc['all_frames_in_collision']})" if nc else "not run") + " | " +
              (f"{cm['arm_frames_in_collision']} ({cm['all_frames_in_collision']}) at {cm['fps']} fps"
               if cm and cm.get("fps") else "older format" if cm else "none") + " |")
