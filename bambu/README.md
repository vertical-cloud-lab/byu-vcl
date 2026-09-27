# Printing remotely on the lab's Bambu printers

A runbook for an agent (or a person) sending a print to the lab's **A1 mini** or **H2D**
from CI, written before the first remote print and meant to be followed to the letter.
[`bambu_lan.py`](bambu_lan.py) does the read-only half: it reaches the printer, checks
that it is the right printer and in a fit state to print, grabs a camera frame, and checks
a sliced 3MF against it.

> **Status (2026-09-27).** Read-only access to the A1 mini is verified end to end (below).
> Nothing has been uploaded to or started on either printer from CI yet. The sending half
> (§5) is written from the lab's other repositories and the published protocol, and has
> not been run against this printer.

<!-- sections below are filled in -->
