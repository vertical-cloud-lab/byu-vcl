# Floor space: three labs, the same equipment (video segment)

Sterling, on PR 400 (2026-11-27): a video segment that compares three labs on floor space: a conventional lab, an
automated "flat" lab on the same floor plan, and the vertical lab, as one continuous animation from a whole-lab view,
with each layout's area computed from its footprints, clearances and aisles, and Emerald Cloud Lab as a reference.

**Everything here is a design layout, not a built lab.** The equipment is the 3-D lab's (PR 318's scene); the layouts
and their areas are ours, from the rules below.

Work in progress: this file is filled in as the segment is built.

## The equipment

`twin/video/floorspace.py` takes one list for all three layouts: every instrument on the Shuttles' trays, as
`setup_lab.py fit` measured it (`out/tray_plan.json`), and every floor machine, measured from the built scene
(`out/twin2/video/birdseye/high.json`). 43 instruments: 31 benchtop and 12 floor machines, plus the sample stores and
powder-jar racks.

## Emerald Cloud Lab, as published

- **South San Francisco:** "the 1,400 square metre (15,000 square feet) lab", where "more than 100 items of high-end
  bioscience equipment whirr away on workbenches" (The Guardian, Tom Ireland, 11 September 2022, "Cloud labs and remote
  research aren't the future of science - they're here"; reprinted by Carnegie Mellon:
  https://www.cmu.edu/ambassadors/december-2022/pdf/guardian_cloud-labs.pdf).
- **Carnegie Mellon's cloud lab,** built and run with Emerald: "the new 1,500 square metre (16,000 square feet) site"
  (the same article).
- **Austin:** "The 105,000-square-foot facility will house over 230 unique types of instruments" (Emerald Cloud Lab
  press release, PR Newswire, 28 February 2023,
  https://www.prnewswire.com/news-releases/emerald-cloud-lab-to-relocate-state-of-the-art-facility-from-south-san-francisco-to-austin-301758704.html).
  That counts types, not instruments, and the building's area, so it gives no instruments-per-area figure. A Texas
  Department of Licensing and Regulation record for the project (TABS2023016373) lists 40,000 sq ft for the renovation,
  which may cover only part of the building; the sources don't say.

## The rules

- Benches 30 in (762 mm) deep, 36 in (914 mm) where an instrument is deeper than 712 mm; aisles 5 ft (1524 mm) between
  rows: NIH Office of Research Facilities, "Lab Module Design Considerations", Technical Bulletin issue 23,
  December 2013 ("a 5'-6" center aisle with 30" deep lab benches on both sides, and a 5' aisle with equipment up to
  36" deep on one side"; "5' is the minimum ADA turning radius").
- The vertical lab's aisle is the 3-D lab's: 3.0 m, two MiR250s pass (MiR250 specification sheet, 2023-06-28).
- Our choices, the same in every layout: 150 mm between instruments on a bench and at its ends, bench runs in whole
  feet, 600 mm of service clearance behind and beside every floor machine, a 6 ft corridor, 150 mm walls, 4 ft doors.
- An area is the outer rectangle of the layout's walls: walls, corridor, aisles and clearances included.
