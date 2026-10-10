# OpenRAMAN on the CubXL

Work in progress for [#213](https://github.com/vertical-cloud-lab/byu-vcl/issues/213):
pricing the [OpenRAMAN](https://www.open-raman.org/) base spectrometer, and bringing it
onto the CubXL's PandaDeck peg board with a pipette-tip sampling dock.

- [`bom/`](bom/): bill of materials. `build_bom.py` turns the price data in `bom/raw/`
  (fetched 2026-10-10 from the stream-cam Pi) into `bom.csv` and `bom_tables.md`.
- `cad/`, `layout/`, `render/`: CAD, layout optimisation and assembly render (to follow).

OpenRAMAN design files are by Luc Boussemaere, CC BY-SA 4.0,
`https://git.thepulsar.be/openraman/cad.git` at commit `778dfda`.
