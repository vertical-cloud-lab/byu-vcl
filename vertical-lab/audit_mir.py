"""collide.py's arm audit of an alloy-route chapter with warehouse.MirCheck added (#303, round 5's fixes): the MiR250's
own body, cabinet, carriers and whatever stands on them, against everything visible, every frame. collide.py checks
the arm and what it holds but not the base it rides on; the warehouse checks its MiRs this way already.

    ARM_AUDIT=1 xvfb-run -a python3 audit_mir.py alloy_print     # -> out/collisions/alloy_print.json (the arm)
                                                                 #    and out/collisions/alloy_print_mir.json
The chapters' single MiR is the group "amr" and its arm's prefix "ur" (alloy_workflow.Mir). No frames are rendered.
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
    sys.exit("set ARM_AUDIT=1")
import scene  # noqa: E402
import warehouse as WH  # noqa: E402

_init, _save, checks = scene.Scene.__init__, scene.Scene.save, {}


def init(self, *a, **k):
    _init(self, *a, **k)
    checks[id(self)] = WH.MirCheck(self, ("amr",), arms={"amr": "ur"})
    self.frame_hooks.append(checks[id(self)])


def save(self):
    out = _save(self)
    if id(self) in checks:
        checks[id(self)].save()
    return out


if __name__ == "__main__":
    scene.Scene.__init__, scene.Scene.save = init, save
    name = Path(sys.argv[1]).stem
    sys.argv = [f"{name}.py"] + sys.argv[2:]
    runpy.run_path(f"{name}.py", run_name="__main__")
