// ============================================================================
//  Dummy pipette for CubXL P20 (Opentrons P20 Single-Channel GEN2) dry runs
// ----------------------------------------------------------------------------
//  Purpose: a cheap, sacrificial, 3D-printable stand-in that mounts exactly
//  where the real P20 goes, reproduces its collision envelope (so clearance /
//  dry-run tests are valid), and BREAKS at a frangible neck instead of bending
//  the ~$1k pipette or the gantry if the machine crashes into deck/labware.
//
//  Design intent
//    * Same mounting datum as the real pipette -> tool origin is unchanged, so
//      motion paths tested with the dummy transfer 1:1 to the real pipette.
//    * Same lowest point (installed-tip end) -> Z-clearance tests are truthful.
//    * A deliberately weak "shear neck" just above the nozzle: a crash snaps a
//      10-cent printed nozzle, not the pipette. Print the nozzle separately in
//      the cheapest filament and keep spares.
//
//  !!! READ FIRST -------------------------------------------------------------
//  The numbers below are BALLPARK ESTIMATES for a P20 GEN2 + 20 uL tip. Before
//  you trust this for a real dry run, put calipers on your actual pipette and
//  overwrite the "MEASURE ME" block. The single most safety-critical number is
//  MOUNT_TO_TIP_END (datum -> lowest point). If you set MATCH_TOTAL_REACH the
//  model auto-adjusts the nozzle gap so the printed part hits that reach even
//  if the sub-dimensions are rough.
//  ---------------------------------------------------------------------------
//  License: CC-BY-4.0 (matches the open-hardware docs in this repo).
// ============================================================================

// ---------------------------------------------------------------------------
//  WHAT TO RENDER  (set `part`, then Render/Export STL)
// ---------------------------------------------------------------------------
//  "assembly"    - body + nozzle in place (preview / print-in-one option)
//  "body"        - body + backplate, nozzle socket only (print this)
//  "nozzle"      - the sacrificial break-away nozzle (print several, cheap)
//  "backplate"   - just the mount interface, to fit-check before a full print
part = "assembly";

// ===========================================================================
//  MEASURE ME  --  overwrite with calipers on your actual P20 GEN2
// ===========================================================================
// Body block (the fat part of the pipette housing) -- rounded rectangular prism
BODY_W       = 24;   // width  (X), mm
BODY_D       = 46;   // depth  (Y), mm   (front-to-back, connector side = +Y)
BODY_H       = 78;   // height (Z) of the main block, mm
BODY_FILLET  = 6;    // corner rounding, cosmetic

// Shoulder: taper from the body down to the nozzle/ejector sleeve
SHOULDER_H   = 22;   // vertical length of the taper, mm

// Ejector sleeve / nozzle collar (the cylindrical bit above the tip cone)
COLLAR_DIA   = 16;   // outer dia of the ejector sleeve, mm
COLLAR_H     = 30;   // length of that sleeve, mm

// Nozzle cone (where a disposable tip presses on)
NOZZLE_TOP_DIA = 9;  // dia at the top of the tip cone, mm
NOZZLE_BOT_DIA = 4;  // dia at the very nozzle tip, mm
NOZZLE_H       = 14; // cone length, mm

// Installed disposable tip (Opentrons 20 uL). This is modeled SOLID so the
// dummy's lowest point == the real tip end. tipLength ~ 39 mm (verify: the
// labware def value that CubOS uses for Z during pipetting).
TIP_LENGTH   = 39;   // length of installed tip below the nozzle, mm
TIP_TOP_DIA  = 7;    // tip dia where it meets the nozzle, mm
TIP_END_DIA  = 1.2;  // tip dia at the very end, mm

// --- Safety override -------------------------------------------------------
// If your calipers give you the datum->tip-end reach directly, put it here and
// set MATCH_TOTAL_REACH = true. The model stretches the tip so total reach is
// exact regardless of the rough sub-dims above. 0 = use dims as-is.
MATCH_TOTAL_REACH = false;
MOUNT_TO_TIP_END  = 0;   // mm, datum (mount face, top of body) -> lowest point

// ===========================================================================
//  MOUNT INTERFACE  --  how the dummy attaches to the CubXL carriage
// ===========================================================================
// The real P20 bolts to the Cubware PAW-V2 "OT2Mount", which bolts to the
// "OT2Backboard" (Ursa-Laboratories/Cubware: mounts/ot2_backboard). Two ways
// to attach the dummy -- pick with MOUNT_STYLE:
//
//   "backboard_plate" (default, simplest): a flat back plate with an M3 bolt
//        grid that bolts the dummy straight to the OT2Backboard. Measure your
//        backboard's hole pattern and set the grid below.
//
//   "mount_clone": a placeholder tab meant to seat in the SAME PAW-V2 OT2Mount
//        pocket the real pipette uses -- the truest collision test. The pocket
//        geometry isn't published dimensionally, so treat this as a starting
//        block: import "PAW-V2 - OT2Mount_REV. 1 - OT2Mount.stl" alongside this
//        file and trim MOUNT_TAB_* until it drops into the real pocket.
MOUNT_STYLE = "backboard_plate";

// Back plate (both styles use a plate against the body's +Y face)
PLATE_TH     = 6;    // plate thickness, mm
PLATE_MARGIN = 6;    // how far the plate extends past the body outline, mm

// M3 bolt grid for "backboard_plate" -- MEASURE your OT2Backboard holes
BOLT_DIA     = 3.4;  // clearance for M3
BOLT_DX      = 16;   // horizontal spacing, mm
BOLT_DZ      = 30;   // vertical spacing, mm
BOLT_COLS    = 2;
BOLT_ROWS    = 2;

// "mount_clone" tab placeholder (fit-check against the real OT2Mount pocket)
MOUNT_TAB_W  = 20;
MOUNT_TAB_H  = 40;
MOUNT_TAB_TH = 8;

// ===========================================================================
//  FRANGIBLE (BREAK-AWAY) NOZZLE JOINT
// ===========================================================================
// The nozzle is a separate part. It plugs into a socket in the body with a
// friction peg, and the load path runs through a thin "shear web" sized to
// snap well below the force that would damage the pipette/gantry. Tune the web
// down if you want it to break easier (cheap PLA, ~0.3-0.5 mm wall).
SOCKET_DIA   = 8;    // peg / socket diameter, mm
SOCKET_DEPTH = 12;   // how deep the peg sits in the body, mm
SOCKET_FIT   = 0.20; // radial clearance for a snug press fit, mm
SHEAR_DIA    = 5;    // dia of the frangible neck, mm  (smaller = breaks easier)
SHEAR_H      = 2.0;  // height of the frangible neck, mm

// ---------------------------------------------------------------------------
$fn = 64;
EPS = 0.01;

// ---- derived heights (top of body = Z0 datum, build downward in -Z) --------
body_top   = 0;
body_bot   = -BODY_H;
shoulder_bot = body_bot - SHOULDER_H;
collar_bot = shoulder_bot - COLLAR_H;
socket_top = collar_bot;                 // frangible joint lives here
nozzle_top = socket_top - SHEAR_H;       // nozzle starts below the shear web
nozzle_bot = nozzle_top - NOZZLE_H;
tip_end_nominal = nozzle_bot - TIP_LENGTH;

// stretch the tip if the user pinned the total reach
tip_len_eff = (MATCH_TOTAL_REACH && MOUNT_TO_TIP_END > 0)
    ? (nozzle_bot + MOUNT_TO_TIP_END) * -1   // solve nozzle_bot - L = -reach
    : TIP_LENGTH;
tip_end = nozzle_bot - tip_len_eff;

echo(str(">>> Datum (mount face) -> tip end reach = ", -tip_end, " mm"));
echo(str(">>> Body envelope (WxDxH) = ", BODY_W, " x ", BODY_D, " x ", BODY_H, " mm"));

// ===========================================================================
//  MODULES
// ===========================================================================
module rrect_prism(w, d, h, r) {
    // rounded-corner rectangular prism, base at z=0 growing +z
    linear_extrude(height = h)
        offset(r = r) offset(delta = -r)
            square([w, d], center = true);
}

module body_block() {
    // main housing block, top face at Z0
    translate([0, 0, body_bot])
        rrect_prism(BODY_W, BODY_D, BODY_H, BODY_FILLET);
}

module shoulder() {
    // taper from body footprint down to the collar diameter
    hull() {
        translate([0, 0, body_bot + EPS])
            rrect_prism(BODY_W, BODY_D, EPS, BODY_FILLET);
        translate([0, 0, shoulder_bot])
            cylinder(h = EPS, d = COLLAR_DIA);
    }
}

module collar() {
    translate([0, 0, collar_bot])
        cylinder(h = COLLAR_H, d = COLLAR_DIA);
}

module nozzle_solid(with_tip = true) {
    // shear web + tip cone + solid tip, as ONE piece (the sacrificial part)
    // frangible neck
    translate([0, 0, nozzle_top])
        cylinder(h = SHEAR_H + EPS, d = SHEAR_DIA);
    // tip cone
    translate([0, 0, nozzle_bot])
        cylinder(h = NOZZLE_H, d1 = NOZZLE_BOT_DIA, d2 = NOZZLE_TOP_DIA);
    // press peg that goes up into the body socket
    translate([0, 0, socket_top - SOCKET_DEPTH])
        cylinder(h = SOCKET_DEPTH + EPS, d = SOCKET_DIA - 2*SOCKET_FIT);
    if (with_tip)
        translate([0, 0, tip_end])
            cylinder(h = tip_len_eff, d1 = TIP_END_DIA, d2 = TIP_TOP_DIA);
}

module body_socket_neg() {
    // bore in the body that receives the nozzle peg
    translate([0, 0, socket_top - SOCKET_DEPTH])
        cylinder(h = SOCKET_DEPTH + EPS, d = SOCKET_DIA);
}

module backplate() {
    w = BODY_W + 2*PLATE_MARGIN;
    h = BODY_H + 2*PLATE_MARGIN;
    // plate on the +Y face of the body
    difference() {
        translate([0, BODY_D/2, -BODY_H/2])
            cube([w, PLATE_TH, h], center = true);
        if (MOUNT_STYLE == "backboard_plate") {
            for (c = [0 : BOLT_COLS-1], r = [0 : BOLT_ROWS-1]) {
                x = (c - (BOLT_COLS-1)/2) * BOLT_DX;
                z = -BODY_H/2 + (r - (BOLT_ROWS-1)/2) * BOLT_DZ;
                translate([x, BODY_D/2, z])
                    rotate([90, 0, 0])
                        cylinder(h = PLATE_TH + 2, d = BOLT_DIA, center = true);
            }
        }
    }
    // mount_clone: add a placeholder tab standing off the plate
    if (MOUNT_STYLE == "mount_clone")
        translate([0, BODY_D/2 + PLATE_TH/2 + MOUNT_TAB_TH/2, -BODY_H/2])
            cube([MOUNT_TAB_W, MOUNT_TAB_TH, MOUNT_TAB_H], center = true);
}

module body_part() {
    difference() {
        union() {
            body_block();
            shoulder();
            collar();
            backplate();
        }
        body_socket_neg();
    }
}

// ===========================================================================
//  PART SELECTOR
// ===========================================================================
if (part == "assembly") {
    color("SteelBlue")  body_part();
    color("Tomato")     nozzle_solid(true);
} else if (part == "body") {
    body_part();
} else if (part == "nozzle") {
    // print upright: move peg to Z0
    translate([0, 0, -tip_end])
        nozzle_solid(true);
} else if (part == "backplate") {
    backplate();
} else {
    echo("Unknown `part` -- use assembly | body | nozzle | backplate");
}
