// ============================================================================
//  Dummy pipette for CubXL dry runs -- Opentrons P20 Single-Channel GEN2 form
//  REV 2: bolts directly to the Cubware PAW-V2 "OT2Mount" backboard
//         (Ursa-Laboratories/Cubware: mounts/ot2_backboard)
// ----------------------------------------------------------------------------
//  Purpose: a cheap, sacrificial, 3D-printable stand-in that screws onto the
//  same backboard the real pipette hardware uses, reproduces a P20-like
//  collision envelope, and BREAKS at a frangible neck instead of damaging the
//  ~$1k pipette or the gantry if the machine crashes into deck/labware.
//
//  Spec (issue #169): with the dummy screwed to the backboard, the pipette-tip
//  attachment point (the nozzle end that a disposable tip would press onto)
//  sits exactly NOZZLE_DROP = 100 mm below the backboard's bottom edge.
//
//  Mount interface -- MEASURED from the actual Cubware STL
//  ("PAW-V2 - OT2Mount_REV. 1 - OT2Mount.stl", mounts/ot2_backboard):
//    * The right-hand pipette panel is a vertical strip 46.5 mm wide whose
//      front face is the mounting plane.
//    * Four mounting holes on the panel centerline: dia 4.0 mm through-holes
//      with dia 6.0 mm counterbores opening to the BACK of the panel
//      (i.e. screws insert from behind; the counterbore fits an M3 socket
//      head, dia 5.5 mm). Pattern: two pairs 19.0 mm apart horizontally,
//      pairs 89.06 mm apart vertically. Lower pair is 5.41 mm above the
//      panel's bottom edge.
//    * A raised carriage pocket begins 100.1 mm above the bottom edge -- the
//      dummy's plate stops just below it.
//  The dummy carries trapped M3 hex nuts behind each hole, so the same
//  M3 screws that would hold the real mount hold the dummy.
//
//  Coordinate system of this file:
//    Z = vertical, Z0 = BOTTOM EDGE of the backboard panel (the datum the
//        100 mm spec is measured from), -Z is down toward the deck.
//    Y = out of the backboard face; the dummy's back face is at Y0 and the
//        backboard lies behind it (Y < 0). X = horizontal, panel centerline.
//
//  License: CC-BY-4.0 (matches the open-hardware docs in this repo).
// ============================================================================

// ---------------------------------------------------------------------------
//  WHAT TO RENDER  (set `part`, then Render/Export STL)
// ---------------------------------------------------------------------------
//  "assembly"           - body + nozzle in mounted position (preview)
//  "assembly_backboard" - same, plus a ghost of the backboard panel + screws
//  "body"               - plate + body + shoulder + collar (print this)
//  "nozzle"             - sacrificial break-away nozzle (print spares, cheap)
part = "assembly";

// Model the installed disposable tip as a solid extension of the nozzle?
// false (default): printed part ends at the tip ATTACHMENT point, 100 mm
//                  below the baseplate, exactly per the issue spec.
// true:            adds a solid 20 uL-tip stand-in below the nozzle so the
//                  dummy's lowest point matches a real installed tip
//                  (reach becomes NOZZLE_DROP + TIP_LENGTH).
INCLUDE_TIP = false;

// ===========================================================================
//  THE SPEC NUMBER
// ===========================================================================
NOZZLE_DROP = 100;   // mm from backboard bottom edge DOWN to the nozzle end
                     // (= pipette-tip attachment point). Issue #169: 100 mm.

// ===========================================================================
//  BACKBOARD INTERFACE  --  measured from the Cubware OT2Mount REV.1 STL
//  (change these only if Ursa revises the backboard)
// ===========================================================================
HOLE_DX        = 19.0;   // horizontal spacing within each hole pair, mm
HOLE_DZ        = 89.06;  // vertical spacing between the two pairs, mm
HOLE_Z_LOWER   = 5.41;   // lower pair height above panel bottom edge, mm
PANEL_W        = 46.5;   // backboard pipette-panel width, mm
PANEL_TH       = 6.5;    // panel thickness at the mount face, mm
POCKET_Z       = 100.1;  // raised carriage pocket starts here above the
                         // bottom edge -- keep the plate below it

// Dummy-side fastening: M3 screws come through the backboard from behind
// into hex nuts trapped in the dummy's plate.
SCREW_CLEAR    = 3.4;    // M3 clearance hole in the dummy plate, mm
NUT_AF         = 5.6;    // M3 nut across-flats + fit allowance, mm
NUT_TH         = 2.9;    // M3 nut pocket depth (nut is 2.4 thick), mm

// Dummy back plate (rests on the panel's front face)
PLATE_W        = 40;     // plate width, mm  (< PANEL_W)
PLATE_TH       = 6;      // plate thickness, mm
PLATE_TOP      = 99.5;   // plate top above bottom edge (just under pocket)

// ===========================================================================
//  P20 GEN2 FORM  --  proportions after the real pipette, heights compressed
//  so the nozzle end lands exactly NOZZLE_DROP below the baseplate.
//  COLLAR_H is DERIVED from the others; an assert guards the budget.
// ===========================================================================
BODY_W         = 26;     // housing width (X), mm
BODY_D         = 42;     // housing depth (Y, away from backboard), mm
BODY_H         = 45;     // housing block height, mm (top at Z0 = bottom edge)
BODY_FILLET    = 6;      // corner rounding, cosmetic

SHOULDER_H     = 15;     // taper housing -> ejector collar, mm
COLLAR_DIA     = 16;     // ejector-sleeve stand-in outer dia, mm
NOZZLE_TOP_DIA = 9;      // tip cone dia at its top, mm
NOZZLE_BOT_DIA = 4.5;    // dia at the nozzle end (where the tip seats), mm
NOZZLE_H       = 14;     // tip cone length, mm

// Optional solid stand-in for an installed Opentrons 20 uL tip.
// Match TIP_LENGTH to `tip_length` in the CubOS ursa_tip_rack labware def.
TIP_LENGTH     = 39;
TIP_TOP_DIA    = 7;
TIP_END_DIA    = 1.2;

// ===========================================================================
//  FRANGIBLE (BREAK-AWAY) NOZZLE JOINT
// ===========================================================================
// The nozzle is a separate cheap part: friction peg into the collar, load
// path through a thin shear neck sized to snap well below the force that
// would damage pipette or gantry. Shrink SHEAR_DIA to break easier.
SOCKET_DIA     = 8;      // peg / socket diameter, mm
SOCKET_DEPTH   = 12;     // peg engagement depth, mm
SOCKET_FIT     = 0.20;   // radial press-fit clearance, mm
SHEAR_DIA      = 5;      // frangible neck dia, mm (smaller = weaker)
SHEAR_H        = 2.0;    // frangible neck height, mm

// ---------------------------------------------------------------------------
$fn = 64;
EPS = 0.01;

// ---- derived vertical stack (Z0 = backboard bottom edge, down = -Z) -------
body_top     = 0;
body_bot     = -BODY_H;
shoulder_bot = body_bot - SHOULDER_H;
collar_h     = NOZZLE_DROP - BODY_H - SHOULDER_H - SHEAR_H - NOZZLE_H;
collar_bot   = shoulder_bot - collar_h;
nozzle_top   = collar_bot - SHEAR_H;     // below the frangible neck
nozzle_end   = nozzle_top - NOZZLE_H;    // == -NOZZLE_DROP by construction
tip_end      = nozzle_end - TIP_LENGTH;

assert(collar_h >= 8,
    str("Vertical budget exceeded: collar would be ", collar_h,
        " mm. Reduce BODY_H / SHOULDER_H / NOZZLE_H."));
assert(abs(-nozzle_end - NOZZLE_DROP) < 0.001, "stack math broke");

echo(str(">>> Tip ATTACHMENT point = ", -nozzle_end,
         " mm below backboard bottom edge (spec: ", NOZZLE_DROP, ")"));
echo(str(">>> Lowest printed point = ",
         INCLUDE_TIP ? -tip_end : -nozzle_end, " mm below bottom edge",
         INCLUDE_TIP ? " (solid tip modeled)" : " (no tip modeled)"));
echo(str(">>> Derived collar length = ", collar_h, " mm"));

// hole pair centers, mm above bottom edge
hole_zs = [HOLE_Z_LOWER, HOLE_Z_LOWER + HOLE_DZ];   // 5.41, 94.47

// ===========================================================================
//  MODULES
// ===========================================================================
module rrect_prism(w, d, h, r) {
    linear_extrude(height = h)
        offset(r = r) offset(delta = -r)
            square([w, d], center = true);
}

// -- mount plate: back face on Y0 plane, bolts to the backboard panel -------
module mount_plate() {
    difference() {
        // plate spans from the body region up past both hole pairs
        translate([-PLATE_W/2, 0, body_bot])
            cube([PLATE_W, PLATE_TH, PLATE_TOP - body_bot]);
        for (z = hole_zs, sx = [-1, 1]) {
            // M3 clearance through the plate
            translate([sx*HOLE_DX/2, -EPS, z])
                rotate([-90, 0, 0])
                    cylinder(h = PLATE_TH + 2*EPS, d = SCREW_CLEAR);
            // hex-nut pocket opening to the FRONT face of the plate
            translate([sx*HOLE_DX/2, PLATE_TH - NUT_TH, z])
                rotate([-90, 30, 0])
                    cylinder(h = NUT_TH + EPS, d = NUT_AF/cos(30), $fn = 6);
        }
    }
}

// -- P20-style hanging body -------------------------------------------------
module body_block() {
    // housing block in front of the plate, top flush with the bottom edge
    translate([0, PLATE_TH + BODY_D/2, body_bot])
        rrect_prism(BODY_W, BODY_D, BODY_H, BODY_FILLET);
}

module shoulder() {
    hull() {
        translate([0, PLATE_TH + BODY_D/2, body_bot + EPS])
            rrect_prism(BODY_W, BODY_D, EPS, BODY_FILLET);
        translate([0, PLATE_TH + BODY_D/2, shoulder_bot])
            cylinder(h = EPS, d = COLLAR_DIA);
    }
}

module collar() {
    translate([0, PLATE_TH + BODY_D/2, collar_bot])
        cylinder(h = collar_h, d = COLLAR_DIA);
}

module body_socket_neg() {
    translate([0, PLATE_TH + BODY_D/2, collar_bot - EPS])
        cylinder(h = SOCKET_DEPTH + EPS, d = SOCKET_DIA);
}

module body_part() {
    difference() {
        union() {
            mount_plate();
            body_block();
            shoulder();
            collar();
        }
        body_socket_neg();
    }
}

// -- sacrificial nozzle (peg + shear neck + tip cone [+ optional tip]) ------
module nozzle_part(with_tip = INCLUDE_TIP) {
    translate([0, PLATE_TH + BODY_D/2, 0]) {
        // press peg up into the collar socket
        translate([0, 0, collar_bot - EPS])
            cylinder(h = SOCKET_DEPTH, d = SOCKET_DIA - 2*SOCKET_FIT);
        // frangible neck
        translate([0, 0, nozzle_top - EPS])
            cylinder(h = SHEAR_H + 2*EPS, d = SHEAR_DIA);
        // tip cone; its lower end is the tip ATTACHMENT point (-NOZZLE_DROP)
        translate([0, 0, nozzle_end])
            cylinder(h = NOZZLE_H, d1 = NOZZLE_BOT_DIA, d2 = NOZZLE_TOP_DIA);
        if (with_tip)
            translate([0, 0, tip_end])
                cylinder(h = TIP_LENGTH, d1 = TIP_END_DIA, d2 = TIP_TOP_DIA);
    }
}

// -- ghost backboard panel for context renders ------------------------------
module backboard_ghost() {
    ghost_h = 130;
    difference() {
        translate([-PANEL_W/2, -PANEL_TH, 0])
            cube([PANEL_W, PANEL_TH, ghost_h]);
        for (z = hole_zs, sx = [-1, 1])
            translate([sx*HOLE_DX/2, -PANEL_TH - EPS, z])
                rotate([-90, 0, 0])
                    cylinder(h = PANEL_TH + 2*EPS, d = 4.0);
    }
    // raised carriage pocket above the plate
    translate([-PANEL_W/2, -PANEL_TH - 5, POCKET_Z])
        cube([PANEL_W, 5, ghost_h - POCKET_Z]);
    // M3 screws coming from behind
    for (z = hole_zs, sx = [-1, 1])
        translate([sx*HOLE_DX/2, -PANEL_TH, z])
            rotate([-90, 0, 0]) {
                cylinder(h = PANEL_TH + PLATE_TH - NUT_TH, d = 2.9);
                cylinder(h = 3, d = 5.4);
            }
}

// ===========================================================================
//  PART SELECTOR
// ===========================================================================
if (part == "assembly") {
    color("SteelBlue") body_part();
    color("Tomato")    nozzle_part();
} else if (part == "assembly_backboard") {
    color("Gainsboro", 0.55) backboard_ghost();
    color("SteelBlue") body_part();
    color("Tomato")    nozzle_part();
} else if (part == "body") {
    body_part();
} else if (part == "nozzle") {
    // stand upright for printing: nozzle end on the bed at Z0
    translate([0, -(PLATE_TH + BODY_D/2),
               INCLUDE_TIP ? -tip_end : -nozzle_end])
        nozzle_part();
} else {
    echo("Unknown `part` -- use assembly | assembly_backboard | body | nozzle");
}
