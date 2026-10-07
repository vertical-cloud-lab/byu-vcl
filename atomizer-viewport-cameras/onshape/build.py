#!/usr/bin/env python3
"""Build (or update) the rePowder viewport-camera document in Onshape over the REST API.

    python build.py variables     # write the Variable Studio from variables.py (1 call)
    python build.py fs            # upload viewport_mounts.fs to the Feature Studio (1 call + 1 to read its specs)
    python build.py features      # add or update the four custom features in the Part Studio (1 call each)

Every machine-dimension parameter of every feature is set to the expression #<same name>, so the feature reads it
from the Variable Studio "Machine dimensions (measure these)". Design parameters (fits, walls, displays, lenses)
are set here, per unit, from UNITS below. State (document, element and feature ids) lives in onshape/state.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from client import Onshape
from variables import VARIABLES, onshape_payload

HERE = Path(__file__).resolve().parent
STATE = HERE / "state.json"
MACHINE = {name for name, *_ in VARIABLES}

# Design values per unit. Displays: outline w x h x t (t includes parts on the back), active area w x h.
COMMON = {"wall": "3 mm", "plate_t": "4 mm", "face_t": "2.5 mm", "skirt_h": "6 mm", "fit": "0.4 mm",
          "pi_standoff": "5 mm", "pi_dx": "0 mm", "pi_dy": "0 mm", "act_dx": "0 mm", "act_dy": "0 mm"}
UNITS = {
    "repowderContext": {"name": "rePowder context (approximate; sizes in the Variable Studio)",
                        "params": {"showOpenLid": True, "showOpenDoor": False}},
    # Elecrow 5 in HDMI (RC050 outline 121.11 x 95.24 x 13, active 108 x 64.8): both MIPI ports carry cameras
    "frontViewfinder": {"name": "Front port viewfinder: HQ (M12) + Camera Module 3 Wide, 5 in HDMI",
                        "params": {**COMMON, "disp_w": "121.11 mm", "disp_h": "95.24 mm", "disp_t": "13 mm",
                                   "act_w": "108 mm", "act_h": "64.8 mm", "act_dy": "7 mm", "tray_depth": "28 mm",
                                   "sock_len": "15 mm", "sock_wall": "3 mm", "sock_lid_t": "1.6 mm", "notch_w": "94 mm",
                                   "plunger_angle": "0 deg", "plunger_tap": "5 mm", "cam_gap": "1 mm",
                                   "hq_x": "-15 mm", "hq_y": "0 mm", "hq_m12": True,
                                   "lens_d": "16 mm", "lens_len": "20 mm", "lens_start": "4 mm",
                                   "cm_x": "18.5 mm", "cm_y": "0 mm"}},
    # Raspberry Pi Touch Display 2, 5 in (outline 143.5 x 91.5, active 110.4 x 62.1)
    "leftViewfinder": {"name": "Left port viewfinder: Camera Module 3 Wide, 5 in Touch Display 2",
                       "params": {**COMMON, "disp_w": "143.5 mm", "disp_h": "91.5 mm", "disp_t": "9 mm",
                                  "act_w": "110.4 mm", "act_h": "62.1 mm", "tray_depth": "28 mm",
                                  "col_len": "20 mm", "col_wall": "4 mm", "cam_gap": "1 mm", "wide": True,
                                  "showOpenDoor": False}},
    # Waveshare 2.8 in DSI (480 x 640 portrait; active 43.2 x 57.6; outline not published as text, 62 x 86 assumed)
    "topWindowCamera": {"name": "Top window camera: HQ + 16 mm C lens on a swing arm, 2.8 in DSI display",
                        "params": {**COMMON, "disp_w": "62 mm", "disp_h": "86 mm", "disp_t": "7 mm",
                                   "act_w": "43.2 mm", "act_h": "57.6 mm", "act_dy": "4 mm", "tray_depth": "28 mm",
                                   "cam_dist": "250 mm", "post_x": "-90 mm", "post_dy": "30 mm", "post_d": "15.875 mm",
                                   "base_h": "51 mm", "lens_d": "39 mm", "lens_len": "50 mm", "lens_start": "17.2 mm",
                                   "hang": "45 mm", "overhang": "60 mm", "det_r": "20 mm", "park": "90 deg",
                                   "showParked": False, "disp_tilt": "30 deg", "plunger_tap": "5 mm"}},
}


def load() -> dict:
    return json.loads(STATE.read_text())


def save(st: dict) -> None:
    STATE.write_text(json.dumps(st, indent=1) + "\n")


def feature_json(spec: dict, ftype: str, namespace: str) -> dict:
    unit = UNITS[ftype]
    params = []
    for p in spec["parameters"]:
        pid = p["parameterId"]
        if p["btType"].startswith("BTParameterSpecBoolean"):
            val = unit["params"].get(pid)
            if val is None:
                continue
            params.append({"btType": "BTMParameterBoolean-144", "parameterId": pid, "value": bool(val)})
            continue
        if pid in MACHINE:
            expr = f"#{pid}"
        elif pid in unit["params"]:
            expr = unit["params"][pid]
        else:
            continue                                    # keep the FeatureScript default
        params.append({"btType": "BTMParameterQuantity-147", "parameterId": pid, "expression": expr,
                       "isInteger": pid == "fp_hood_sides"})
    return {"btType": "BTMFeature-134", "featureType": ftype, "name": unit["name"], "namespace": namespace,
            "parameters": params}


def main() -> None:
    api = Onshape()
    st = load()
    did, wid = st["did"], st["wid"]
    el = st["elements"]
    what = sys.argv[1:] or ["features"]
    if "variables" in what:
        vs = el["Machine dimensions (measure these)"]["id"]
        api.call("POST", f"/variables/d/{did}/w/{wid}/e/{vs}/variables", json=onshape_payload())
        print(f"variables: {len(VARIABLES)} written")
    if "fs" in what:
        fsid = el["viewport_mounts.fs"]["id"]
        r = api.call("POST", f"/featurestudios/d/{did}/w/{wid}/e/{fsid}",
                     json={"contents": (HERE / "viewport_mounts.fs").read_text(), "sourceMicroversion": st["fs_microversion"]})
        st["fs_microversion"] = r["sourceMicroversion"]
        spec = api.call("GET", f"/featurestudios/d/{did}/w/{wid}/e/{fsid}/featurespecs")
        st["specs"] = {f["featureType"]: f for f in spec.get("featureSpecs", [])}
        st["namespace"] = next(iter(st["specs"].values()))["namespace"] if st["specs"] else None
        print("feature studio:", sorted(st["specs"]), st["namespace"])
        save(st)
    if "features" in what:
        ps = el["Part Studio 1"]["id"]
        st.setdefault("features", {})
        only = [a for a in what if a in UNITS]
        for ftype in (only or list(UNITS)):
            feat = feature_json(st["specs"][ftype], ftype, st["namespace"])
            fid = st["features"].get(ftype)
            body = {"btType": "BTFeatureDefinitionCall-1406", "feature": feat}
            if fid:
                feat["featureId"] = fid
                out = api.call("POST", f"/partstudios/d/{did}/w/{wid}/e/{ps}/features/featureid/{fid}", json=body)
            else:
                out = api.call("POST", f"/partstudios/d/{did}/w/{wid}/e/{ps}/features", json=body)
            st["features"][ftype] = out["feature"]["featureId"]
            fs = out.get("featureState", {})
            print(f"{ftype:<18} {fs.get('featureStatus')}  {json.dumps(fs)[:300]}")
            save(st)
    print("API calls so far (successful):", api.calls_ok())


if __name__ == "__main__":
    main()
