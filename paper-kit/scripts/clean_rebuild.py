"""make rebuild-check: rebuild every figure in a clean environment.

Copies only vcl_style.py, requirements.txt, data/ and the figure scripts into
an empty temporary folder, makes a new virtual environment there from
requirements.txt alone, runs every figures/fig*.py with VCL_STRICT_DATA=1, and
compares what it makes with figures/out/.  It fails if a script fails (a
file it needs is not in data/, or a package is missing from
requirements.txt), if a figure is missing on either side, or if a figure
differs in more than a few pixels.  Byte-identical is reported as such;
"same pixels" means only metadata differs; a small pixel difference is
usually a different font or matplotlib version, which the report names.

Run it before G4 (internal review) and before submission; the tracker asks
for its last line.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

import numpy as np
from PIL import Image

KIT = Path(__file__).resolve().parents[1]
MAX_DIFF_SHARE = 1e-4          # pixels allowed to differ (antialiasing noise)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def png_diff_share(a: Path, b: Path) -> float:
    with Image.open(a) as ia, Image.open(b) as ib:
        if ia.size != ib.size:
            return 1.0
        x = np.asarray(ia.convert("RGB"), dtype=np.int16)
        y = np.asarray(ib.convert("RGB"), dtype=np.int16)
    return float(np.mean(np.any(np.abs(x - y) > 8, axis=-1)))


def main() -> int:
    work = Path(tempfile.mkdtemp(prefix="vcl-rebuild-"))
    print(f"clean copy in {work}")
    for name in ("vcl_style.py", "requirements.txt"):
        shutil.copy2(KIT / name, work / name)
    shutil.copytree(KIT / "data", work / "data")
    (work / "figures").mkdir()
    scripts = sorted((KIT / "figures").glob("fig*.py"))
    for s in scripts:
        shutil.copy2(s, work / "figures" / s.name)

    print("new virtual environment from requirements.txt ...")
    venv.create(work / "venv", with_pip=True)
    py = work / "venv" / ("Scripts" if os.name == "nt" else "bin") / "python"
    pip = subprocess.run([str(py), "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
                          "-r", str(work / "requirements.txt")])
    if pip.returncode:
        print("FAIL: pip could not install requirements.txt")
        return 1

    env = dict(os.environ, VCL_STRICT_DATA="1", PYTHONHASHSEED="0")
    env.pop("PYTHONPATH", None)
    failed = []
    for s in scripts:
        r = subprocess.run([str(py), str(work / "figures" / s.name)], cwd=work, env=env,
                           capture_output=True, text=True)
        if r.returncode:
            failed.append(s.name)
            print(f"FAIL {s.name}:\n{r.stderr.strip()[-1500:]}")
    if failed:
        print(f"\n{len(failed)} script(s) failed in the clean environment (kept: {work})")
        return 1

    new_out, old_out = work / "figures" / "out", KIT / "figures" / "out"
    new = {p.name for p in new_out.iterdir() if p.is_file()}
    old = {p.name for p in old_out.iterdir() if p.is_file()} if old_out.exists() else set()
    bad = 0
    for name in sorted(old - new):
        print(f"FAIL {name}: in figures/out/ but no script makes it (delete it, or restore its script)")
        bad += 1
    for name in sorted(new - old):
        print(f"FAIL {name}: made by a script but not in figures/out/ (run make figures, commit)")
        bad += 1
    for name in sorted(new & old):
        a, b = old_out / name, new_out / name
        if sha(a) == sha(b):
            print(f"ok   {name}: byte-identical")
        elif name.endswith(".png"):
            share = png_diff_share(a, b)
            if share == 0:
                print(f"ok   {name}: same pixels (metadata differs)")
            elif share <= MAX_DIFF_SHARE:
                print(f"ok   {name}: {share:.2e} of pixels differ (antialiasing)")
            else:
                print(f"FAIL {name}: {share:.2%} of pixels differ: the committed figure is not what "
                      "the scripts and data make now (or fonts differ: see the PDF fonts)")
                bad += 1
        elif name.endswith(".pdf"):
            print(f"note {name}: bytes differ (judge by the PNG of the same figure)")
        else:
            print(f"FAIL {name}: differs (caption stub out of date: run make figures, commit)")
            bad += 1
    if bad:
        print(f"\n{bad} problem(s); the clean build is kept in {work} for comparison")
        return 1
    shutil.rmtree(work, ignore_errors=True)
    print(f"\nclean rebuild OK: {len(scripts)} figure scripts, python "
          f"{sys.version.split()[0]} outside, requirements.txt inside")
    return 0


if __name__ == "__main__":
    sys.exit(main())
