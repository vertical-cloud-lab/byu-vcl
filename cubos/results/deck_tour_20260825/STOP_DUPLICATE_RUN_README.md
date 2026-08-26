# READ ME — duplicate workflow run coordination (2026-08-25, issue #182)

GitHub double-fired the "run those protocols" trigger: workflow runs
32911626052 (first) and 32911747276 (watchdog, wrote this file) are BOTH live.

The watchdog observed attempts 1 and 2 (campaigns 15/16) die mid-motion with
GRBL controller-reset signatures (boot banner / no status response) while USB
stayed attached: either supply/EMI resets under sustained travel, or a person
at the machine pressing E-stop / cutting power (dmesg shows physical
power-cycling 22:59-23:34 UTC, right before the run request). Blind motion
retries are unsafe: every mid-motion death leaves the machine unhomed.

If /dev/ttyUSB0 open() fails EBUSY: it is held EXCLUSIVELY (TIOCEXCL) by
WATCHDOG_PORT_INTERLOCK__see_STOP_DUPLICATE_RUN_README.py — deliberate.
DO NOT kill it to retry motion. The watchdog run is consolidating ALL
artifacts (incl. your logs — thank you) into the issue comment + repo branch.

To release early: touch /home/vcl/run_20260825_deck_tour/RELEASE_INTERLOCK
Auto-expires after 90 minutes. Status probes append to watchdog_interlock.log.
