"""Mock-run a protocol with CubOS's own per-move trace switched on.

`run_protocol --mock` does not print where each move goes. The line
"Moving <instrument> to (deck) -> gantry (...)" is logged by
cubos.gantry.instrument_mount at DEBUG/INFO, so this raises that one logger
and otherwise runs run_protocol unchanged. Never touches hardware.

    python trace_mock.py GANTRY DECK PROTOCOL
"""
import logging
import sys
import tempfile

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("cubos.gantry.instrument_mount").setLevel(logging.DEBUG)

from cubos.tools import run_protocol  # noqa: E402

db = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
sys.argv = ["run_protocol", "--mock", "--database", db, *sys.argv[1:]]
raise SystemExit(run_protocol.main())
