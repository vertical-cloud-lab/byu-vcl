// the three delta-stage feet in their assembled position (main-body frame)
include <parameters.scad>
use <feet.scad>
for (a = [0, 120, 240]) rotate(a) translate([0, stage_r + nut_y, 0]) foot(hover=2, lie_flat=false);
