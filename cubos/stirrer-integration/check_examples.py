"""Check the approach-1 example configs against a CubOS checkout.

Run it with a Python that has CubOS core installed (`pip install -e
packages/core` in a CubOS clone):

    python cubos/stirrer-integration/check_examples.py <label>

It runs CubOS's own offline checks, `validate_setup` and `run_protocol
--mock`, three times:

1. on the three example files as they are. These are expected to fail,
   because `stirrer` and `stir` don't exist in CubOS yet. The failure shows
   where.
2. on copies with the stirrer taken out (the `stirrer_1` instrument and every
   `stir` step removed; the deck file is used unchanged). This shows what the
   rest of the files do on that CubOS, so that the stirrer is the only
   difference.
3. on the 2026-11-05 files the examples started from (Ben's gantry, deck and
   protocol, which ran 11/11 on the CubXL), for comparison with 2.

Nothing here touches hardware: `validate_setup` is offline and `--mock`
never opens a port. Logs go to cubos/stirrer-integration/checks/<label>/.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
EXAMPLES = HERE / "approach-1"
ORIGINAL = (
    REPO / "cubos/configs/gantry/cub_xl_ben_3_instrument.yaml",
    REPO / "cubos/configs/deck/stir_module_trial.yaml",
    REPO / "cubos/configs/protocol/vcl/stir_module_trial.yaml",
)
OUT = HERE / "checks" / (sys.argv[1] if len(sys.argv) > 1 else "cubos")


def run(label: str, args: list[str]) -> int:
    proc = subprocess.run(
        [sys.executable, "-m", *args], capture_output=True, text=True,
    )
    log = OUT / f"{label}.log"
    log.write_text(
        f"$ python -m {' '.join(args)}\n(exit {proc.returncode})\n\n"
        + proc.stdout + proc.stderr
    )
    print(f"{label}: exit {proc.returncode} -> {log.relative_to(REPO)}")
    return proc.returncode


def strip_stirrer(tmp: Path) -> tuple[Path, Path, Path]:
    gantry = yaml.safe_load((EXAMPLES / "gantry.yaml").read_text())
    gantry["instruments"] = {
        name: entry for name, entry in gantry["instruments"].items()
        if entry.get("type") != "stirrer"
    }
    protocol = yaml.safe_load((EXAMPLES / "protocol.yaml").read_text())
    protocol["protocol"] = [
        step for step in protocol["protocol"]
        if not (isinstance(step, dict) and "stir" in step)
    ]
    g, p = tmp / "gantry_no_stirrer.yaml", tmp / "protocol_no_stir.yaml"
    g.write_text(yaml.safe_dump(gantry, sort_keys=False))
    p.write_text(yaml.safe_dump(protocol, sort_keys=False))
    return g, EXAMPLES / "deck.yaml", p


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    full = [str(EXAMPLES / f) for f in ("gantry.yaml", "deck.yaml", "protocol.yaml")]
    run("1_validate_full", ["cubos.tools.validate_setup", *full])
    run("1_mock_full", ["cubos.tools.run_protocol", "--mock", *full])
    with tempfile.TemporaryDirectory() as tmp:
        stripped = [str(p) for p in strip_stirrer(Path(tmp))]
        run("2_validate_without_stirrer", ["cubos.tools.validate_setup", *stripped])
        run("2_mock_without_stirrer", ["cubos.tools.run_protocol", "--mock", *stripped])
    original = [str(p) for p in ORIGINAL]
    run("3_validate_original_20261105", ["cubos.tools.validate_setup", *original])
    run("3_mock_original_20261105", ["cubos.tools.run_protocol", "--mock", *original])


if __name__ == "__main__":
    main()
