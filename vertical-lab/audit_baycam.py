"""collide.py's arm audit of a clip with the overhead bay camera in it (#303, round 5's fixes).

services.py checks the bay unit against reach.py's poses (bay_arm_clearance(), 197 mm clear). This checks it along a
clip's own arm paths: it adds services.add_bay_camera() to the clip's scene before its first step, so collide.World
picks up the unit, its post and its bar with everything else, and every frame of every arm move is checked against
them. No frames are rendered.

    ARM_AUDIT=1 ARM_AUDIT_TAG=baycam xvfb-run -a python3 audit_baycam.py animate.py workflow
    ARM_AUDIT=1 ARM_AUDIT_TAG=baycam xvfb-run -a python3 audit_baycam.py alloy_charge.py
                                                    # -> out/collisions/<clip>_baycam.json

A clip that already has the bay camera (services.py's own scenes, setup_lab) is left as it is.
"""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.chdir(HERE)
if not os.environ.get("ARM_AUDIT"):
    sys.exit("set ARM_AUDIT=1 (and ARM_AUDIT_TAG=baycam, so the clip's own audit isn't overwritten)")
import scene  # noqa: E402
import services  # noqa: E402

_step = scene.Scene.step


def step(self, *a, **k):
    if not getattr(self, "_baycam", False):
        self._baycam = True
        if "baycam" not in self.gmat:
            services.add_bay_camera(self)          # collide.World.refresh() picks its actors up
            print(f"{self.name}: bay camera added", flush=True)
    return _step(self, *a, **k)


if __name__ == "__main__":
    scene.Scene.step = step
    script, sys.argv = sys.argv[1], sys.argv[1:]
    runpy.run_path(script, run_name="__main__")
