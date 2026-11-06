"""Before / after sheet for the rePowder lid refinement (#303): per registered frame, the footage with the OLD model's
outline (main at 9a5dc71: hexagonal hood hinged on the left), and with the refined model's, both drawn with the cameras
fitted to the refined model (so the comparison favours the new model a little: the camera was solved with it).

    git show 9a5dc71:vertical-lab/repowder/model.py > /tmp/old/oldmodel.py
    xvfb-run -a python3 repowder/refine_sheet.py /tmp/old/oldmodel.py     -> out/repowder_refine/before_after.jpg
"""
import importlib.util
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "repowder"))
import register as R  # noqa: E402
import tour  # noqa: E402
from instruments import Instrument, Joint  # noqa: E402

OLD_LID = ("hood", "hood_window", "hood_hot_label", "hood_knob")


def old_instrument(path):
    spec = importlib.util.spec_from_file_location("oldmodel", path)
    om = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(om)
    inst = Instrument("repowder_old", "old", "old", (1000, 800, 1600), "main 9a5dc71")
    inst.meshes = {"body": [], "lid": []}
    for name, d in om.meshes().items():
        if d["group"] not in {"furnace", "hood", "machine", "rod", "arm", "arm_base", "top_ins", "tc", "chamber", "door"}:
            continue
        if d["whole"] is not None and d["whole"].n_points:
            inst.meshes["lid" if name in OLD_LID else "body"].append((d["whole"], d["color"], 1.0))
    inst.joints["lid"] = Joint("hinge", axis=(0, 1, 0), pivot=tuple(float(c) for c in om.HINGE), deg=-105.0)
    return inst


def outline(img, rgb, mask, colour):
    out = img.copy()
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    cr = (cv2.Canny(gray, 40, 110) > 0) & (cv2.erode(mask.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
    out[cr] = (0, 230, 255)
    cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(out, cnts, -1, colour, 3)
    return out


def main(old_path, out):
    fit = json.loads((R.REFS / "repowder" / "fit.json").read_text())
    new_build = R.build
    old = old_instrument(old_path)
    rows = []
    for name, fv in fit["views"].items():
        view = json.loads((R.REFS / "repowder" / f"{name}.json").read_text())
        size, cam = tuple(fv["size"]), np.asarray(fv["camera"])
        und = R._undistort(np.asarray(Image.open(R.frame_path("repowder", name, view)).convert("RGB")), cam, size)
        R.build = new_build
        rn, mn = R.render("repowder", cam, size, view.get("pose", {}), fit["params"])
        R.build = lambda key, params=None: (old, tour.piece_entries(old))
        rgb_o, mo = R.render("repowder", cam, size, view.get("pose", {}), None)
        R.build = new_build
        cols = [und, outline(und, rgb_o, mo, (255, 80, 60)), outline(und, rn, mn, (255, 225, 0))]
        row = np.concatenate(cols, axis=1)
        im = Image.fromarray(row).resize((1800, int(row.shape[0] * 1800 / row.shape[1])), Image.LANCZOS)
        cv2.putText(np.asarray(im), "", (0, 0), 0, 1, 0)
        a = np.asarray(im).copy()
        tag = "HELD OUT" if fv["holdout"] else "fitted"
        cv2.rectangle(a, (0, 0), (1800, 30), (0, 0, 0), -1)
        cv2.putText(a, f"{name} ({tag}) | footage | old model (red) | refined model (yellow), rms {fv['rms_px']} px of {size[0]}",
                    (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        rows.append(a)
    Image.fromarray(np.concatenate(rows, axis=0)).save(out, quality=86)
    print(out)


if __name__ == "__main__":
    out = HERE / "out" / "repowder_refine"
    out.mkdir(parents=True, exist_ok=True)
    main(sys.argv[1], out / "before_after.jpg")
