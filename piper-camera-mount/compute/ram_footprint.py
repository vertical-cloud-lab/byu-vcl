#!/usr/bin/env python3
"""Peak memory of the vision workloads a wrist Pi 5 might run, to size its RAM.

Each case runs in its own fresh Python process and reports its peak resident set (ru_maxrss), so one
case's allocations can't hide in another's. Model weights and activations are the same size on any
CPU, so the peaks carry over to a Pi 5 to within the frameworks' own overhead (tens of MB). The
times are from whatever machine runs this and are only there to compare runtimes with each other;
for Pi 5 speeds see compute/README.md.

    python compute/ram_footprint.py prep       # download the YOLO weights, export ONNX and NCNN
    python compute/ram_footprint.py all        # run every case, write compute/ram_footprint.json
    python compute/ram_footprint.py CASE       # run one case, print its JSON line
"""
from __future__ import annotations

import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get("FOOTPRINT_WORK", "/tmp/footprint"))
HQ = (3040, 4056)        # HQ Camera full frame, rows x cols
CM3W = (2592, 4608)      # Camera Module 3 Wide full frame
RUNS = 5


def mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # Linux reports kB


def rss() -> float:
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def frames(scene=True):
    """Both cameras' full frames. scene=True: a smooth background with 12 AprilTags and mild noise,
    like a bench seen from the wrist. scene=False: pure noise, the worst case for a tag detector."""
    import cv2
    import numpy as np
    rng = np.random.default_rng(0)
    out = []
    for h, w in (HQ, CM3W):
        if not scene:
            out.append(rng.integers(0, 255, (h, w, 3), dtype=np.uint8))
            continue
        # built in uint8 throughout, so making the frames doesn't set the peak itself
        ramp = (90 + 80 * np.linspace(0, 1, 64)[None, :] + 40 * np.linspace(0, 1, 48)[:, None]).astype(np.uint8)
        im = cv2.resize(ramp, (w, h), interpolation=cv2.INTER_LINEAR)
        d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
        for i in range(12):
            tag = cv2.resize(cv2.aruco.generateImageMarker(d, i, 200), (300, 300), interpolation=cv2.INTER_NEAREST)
            y, x = 300 + (i // 4) * 800, 400 + (i % 4) * 1000
            im[y:y + 380, x:x + 380] = 255
            im[y + 40:y + 340, x + 40:x + 340] = tag
        im = cv2.subtract(cv2.add(im, rng.integers(0, 9, im.shape, dtype=np.uint8)), 4)
        out.append(cv2.cvtColor(im, cv2.COLOR_GRAY2BGR))
    return out


def timed(fn, runs=RUNS):
    fn()                                   # warm-up, not timed
    t = time.perf_counter()
    for _ in range(runs):
        fn()
    return (time.perf_counter() - t) / runs * 1000


# ---------------------------------------------------------------- cases
def case_python():
    import numpy  # noqa: F401
    return {}


def case_opencv_apriltag(scene=True):
    import cv2
    imgs = frames(scene)
    det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11))
    loaded = rss()
    found = []

    def run():
        found.clear()
        for im in imgs:
            corners, ids, _ = det.detectMarkers(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY))
            found.append(0 if ids is None else len(ids))
    return {"after load (MB)": loaded, "ms per pair of frames": timed(run, 2), "tags found": sum(found)}


def case_torch_import():
    import torch  # noqa: F401
    import torchvision  # noqa: F401
    return {}


def _ultra(name, imgsz=640):
    from ultralytics import YOLO
    model = YOLO(str(WORK / f"{name}.pt"))
    imgs = frames()
    loaded = rss()
    ms = timed(lambda: model.predict(imgs[0], imgsz=imgsz, verbose=False))
    return {"after load (MB)": loaded, "ms per frame": ms}


def _onnx(name, imgsz=640):
    import numpy as np
    import onnxruntime as ort
    sess = ort.InferenceSession(str(WORK / f"{name}.onnx"), providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0]
    x = np.random.default_rng(0).random((1, 3, imgsz, imgsz), dtype=np.float32)
    loaded = rss()
    ms = timed(lambda: sess.run(None, {inp.name: x}))
    return {"after load (MB)": loaded, "ms per frame": ms}


def _ncnn(name, imgsz=640):
    import ncnn
    import numpy as np
    d = WORK / f"{name}_ncnn_model"
    net = ncnn.Net()
    net.opt.use_vulkan_compute = False
    net.load_param(str(d / "model.ncnn.param"))
    net.load_model(str(d / "model.ncnn.bin"))
    x = np.random.default_rng(0).random((3, imgsz, imgsz), dtype=np.float32)
    loaded = rss()

    def run():
        ex = net.create_extractor()
        ex.input("in0", ncnn.Mat(x))
        ex.extract("out0")
    return {"after load (MB)": loaded, "ms per frame": timed(run)}


def case_unet_torch():
    import segmentation_models_pytorch as smp
    import torch
    model = smp.Unet("resnet34", encoder_weights=None, classes=2).eval()
    x = torch.rand(1, 3, 512, 512)
    loaded = rss()
    with torch.inference_mode():
        ms = timed(lambda: model(x))
    return {"after load (MB)": loaded, "ms per frame": ms, "params (M)": sum(p.numel() for p in model.parameters()) / 1e6}


def case_maskrcnn_torch(full=False):
    """Untrained weights, so it returns its maximum of 100 detections: the top end for a real scene.
    Masks are pasted back at the input's size, so a full 12 MP input costs 100 x 12 MP x 4 bytes."""
    import torch
    import torchvision
    model = torchvision.models.detection.maskrcnn_resnet50_fpn_v2(weights=None, weights_backbone=None).eval()
    x = torch.rand(3, *HQ) if full else torch.rand(3, 800, 1066)  # the model resizes to 800 px either way
    loaded = rss()
    with torch.inference_mode():
        ms = timed(lambda: model([x]), 2)
    return {"after load (MB)": loaded, "ms per frame": ms, "params (M)": sum(p.numel() for p in model.parameters()) / 1e6}


CASES = {
    "python + numpy": case_python,
    "OpenCV: AprilTags on both full 12 MP frames, bench scene": case_opencv_apriltag,
    "OpenCV: AprilTags on both full 12 MP frames, pure noise (worst case)": lambda: case_opencv_apriltag(False),
    "PyTorch + torchvision, imported only": case_torch_import,
    "YOLO11n detect, Ultralytics (PyTorch), 640": lambda: _ultra("yolo11n"),
    "YOLO11n detect, ONNX Runtime, 640": lambda: _onnx("yolo11n"),
    "YOLO11n detect, NCNN, 640": lambda: _ncnn("yolo11n"),
    "YOLO11s detect, Ultralytics (PyTorch), 640": lambda: _ultra("yolo11s"),
    "YOLO11s detect, ONNX Runtime, 640": lambda: _onnx("yolo11s"),
    "YOLO11m detect, ONNX Runtime, 640": lambda: _onnx("yolo11m"),
    "YOLO11n-seg, Ultralytics (PyTorch), 640": lambda: _ultra("yolo11n-seg"),
    "YOLO11n-seg, ONNX Runtime, 640": lambda: _onnx("yolo11n-seg"),
    "YOLO11n-seg, NCNN, 640": lambda: _ncnn("yolo11n-seg"),
    "U-Net (ResNet-34), PyTorch, 512 x 512": case_unet_torch,
    "Mask R-CNN (ResNet-50 FPN v2), PyTorch, frame shrunk to 1066 x 800 first": case_maskrcnn_torch,
    "Mask R-CNN (ResNet-50 FPN v2), PyTorch, full 12 MP frame in": lambda: case_maskrcnn_torch(True),
}


def prep():
    from ultralytics import YOLO
    WORK.mkdir(parents=True, exist_ok=True)
    os.chdir(WORK)
    for name in ("yolo11n", "yolo11s", "yolo11m", "yolo11n-seg"):
        m = YOLO(f"{name}.pt")
        if not (WORK / f"{name}.onnx").exists():
            m.export(format="onnx", imgsz=640, simplify=True)
        if name in ("yolo11n", "yolo11n-seg") and not (WORK / f"{name}_ncnn_model").exists():
            try:
                YOLO(f"{name}.pt").export(format="ncnn", imgsz=640)
            except Exception as e:  # NCNN export needs pnnx; skip the NCNN cases if it fails
                print("ncnn export failed:", e)


def one(name):
    torch_threads = os.environ.get("OMP_NUM_THREADS")
    t = time.perf_counter()
    try:
        extra = CASES[name]()
        ok = True
    except Exception as e:  # report and carry on
        extra, ok = {"error": f"{type(e).__name__}: {e}"[:300]}, False
    out = {"case": name, "ok": ok, "peak RSS (MB)": round(mb(), 1),
           **{k: round(v, 1) if isinstance(v, float) else v for k, v in extra.items()},
           "wall (s)": round(time.perf_counter() - t, 1), "threads": torch_threads}
    print(json.dumps(out))


def run_all():
    rows = []
    for name in CASES:
        p = subprocess.run([sys.executable, __file__, name], capture_output=True, text=True, cwd=WORK)
        line = [l for l in p.stdout.splitlines() if l.startswith("{")]
        row = json.loads(line[-1]) if line else {"case": name, "ok": False, "error": p.stderr[-300:]}
        print(json.dumps(row), flush=True)
        rows.append(row)
    import cv2
    import ncnn
    import numpy
    import onnxruntime
    import torch
    import ultralytics
    cpu = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), platform.machine())
    meta = {
        "machine": f"{platform.machine()}, {os.cpu_count()} CPUs, {cpu}",
        "python": platform.python_version(),
        "versions": {"numpy": numpy.__version__, "opencv": cv2.__version__, "torch": torch.__version__,
                     "onnxruntime": onnxruntime.__version__, "ultralytics": ultralytics.__version__, "ncnn": ncnn.__version__},
        "frames": {"HQ": list(HQ), "CM3 Wide": list(CM3W)},
        "note": __doc__.split("\n\n")[1].replace("\n", " "),
    }
    (HERE / "ram_footprint.json").write_text(json.dumps({"meta": meta, "cases": rows}, indent=1) + "\n")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg == "prep":
        prep()
    elif arg == "all":
        WORK.mkdir(parents=True, exist_ok=True)
        run_all()
    else:
        one(arg)
