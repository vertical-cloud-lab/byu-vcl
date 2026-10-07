FeatureScript 3083;
import(path : "onshape/std/common.fs", version : "3083.0");

/*
 * rePowder viewport cameras (byu-vcl #198): a Raspberry Pi 5 "viewfinder" on each of three viewing windows of the
 * AMAZEMET rePowder atomizer, each with its own small display, plus an approximate model of the machine around them.
 *
 * Machine coordinates are those of atomizer-training/viz3d/model.py (#255): x to the operator's right, y away from
 * the operator (the chamber's front face is at y = ch_front_y), z up from the floor, furnace axis at x = y = 0.
 *
 * Every machine dimension that is a guess is a feature parameter whose expression is a variable (#name) of the
 * Variable Studio "Machine dimensions (measure these)". Change a value there and everything follows. Design
 * choices (wall thicknesses, fits, display sizes, lens) are ordinary feature parameters with their defaults here.
 *
 * Camera and Pi sizes are Raspberry Pi's drawings, as in #241's mount.py: HQ Camera 38 x 38 board, 4 x M2.5 on
 * 30 x 30; Camera Module 3 25 x 23.862, 4 x M2 on 21 x 12.5, lens axis 14.4 mm from the far edge; Pi 5 85 x 56,
 * 4 x M2.5 on 58 x 49, 3.5 mm in from the microSD end.
 */

// ------------------------------------------------------------------------------------------------ colours
const C_PRINT = [0.12, 0.12, 0.13];       // black PETG / ASA
const C_PRINT2 = [0.93, 0.47, 0.10];      // orange: the second printed part of a unit
const C_PCB = [0.05, 0.42, 0.20];
const C_LENS = [0.04, 0.04, 0.05];
const C_SCREEN = [0.10, 0.22, 0.50];
const C_STEEL = [0.74, 0.75, 0.77];
const C_DARK = [0.30, 0.31, 0.33];
const C_BLUE = [0.08, 0.24, 0.62];
const C_GLASS = [0.55, 0.80, 0.95];
const C_GHOST = [0.95, 0.80, 0.55];

// ------------------------------------------------------------------------------------------------ helpers
function mmv(x is number) returns ValueWithUnits
{
    return x * millimeter;
}

function bx(context is Context, id is Id, x0 is ValueWithUnits, x1 is ValueWithUnits, y0 is ValueWithUnits,
    y1 is ValueWithUnits, z0 is ValueWithUnits, z1 is ValueWithUnits)
{
    fCuboid(context, id, { "corner1" : vector(min(x0, x1), min(y0, y1), min(z0, z1)),
                "corner2" : vector(max(x0, x1), max(y0, y1), max(z0, z1)) });
}

// box centred on (cx, cy) in x and y
function cbx(context is Context, id is Id, cx is ValueWithUnits, cy is ValueWithUnits, w is ValueWithUnits,
    h is ValueWithUnits, z0 is ValueWithUnits, z1 is ValueWithUnits)
{
    bx(context, id, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2, z0, z1);
}

function zcyl(context is Context, id is Id, x is ValueWithUnits, y is ValueWithUnits, z0 is ValueWithUnits,
    z1 is ValueWithUnits, r is ValueWithUnits)
{
    fCylinder(context, id, { "bottomCenter" : vector(x, y, z0), "topCenter" : vector(x, y, z1), "radius" : r });
}

function cyl(context is Context, id is Id, p0 is Vector, p1 is Vector, r is ValueWithUnits)
{
    fCylinder(context, id, { "bottomCenter" : p0, "topCenter" : p1, "radius" : r });
}

// regular n-gon prism along z, given across flats, with a flat facing angle rot
function ngonPrism(context is Context, id is Id, cx is ValueWithUnits, cy is ValueWithUnits, n is number,
    af is ValueWithUnits, rot is ValueWithUnits, z0 is ValueWithUnits, z1 is ValueWithUnits)
{
    const rc = af / 2 / cos(180 / n * degree);
    var pts = [];
    for (var i = 0; i < n; i += 1)
    {
        const a = rot + (i + 0.5) * (360 / n) * degree;
        pts = append(pts, vector(cx + rc * cos(a), cy + rc * sin(a)));
    }
    pts = append(pts, pts[0]);
    const sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : plane(vector(mmv(0), mmv(0), z0), vector(0, 0, 1), vector(1, 0, 0)) });
    skPolyline(sk, "poly", { "points" : pts });
    skSolve(sk);
    opExtrude(context, id + "ex", { "entities" : qSketchRegion(id + "sk"), "direction" : vector(0, 0, 1),
                "endBound" : BoundingType.BLIND, "endDepth" : z1 - z0 });
    opDeleteBodies(context, id + "del", { "entities" : qCreatedBy(id + "sk", EntityType.BODY) });
}

// rounded rectangle prism along z (window in the furnace lid)
function rrectPrism(context is Context, id is Id, cx is ValueWithUnits, cy is ValueWithUnits, w is ValueWithUnits,
    h is ValueWithUnits, r is ValueWithUnits, z0 is ValueWithUnits, z1 is ValueWithUnits)
{
    const rr = max(min(r, min(w, h) / 2 - mmv(0.01)), mmv(0.01));
    cbx(context, id + "a", cx, cy, w - 2 * rr, h, z0, z1);
    cbx(context, id + "b", cx, cy, w, h - 2 * rr, z0, z1);
    for (var i = 0; i < 4; i += 1)
    {
        const sx = (i % 2 == 0) ? 1 : -1;
        const sy = (i < 2) ? 1 : -1;
        zcyl(context, id + ("c" ~ i), cx + sx * (w / 2 - rr), cy + sy * (h / 2 - rr), z0, z1, rr);
    }
    opBoolean(context, id + "u", { "tools" : qCreatedBy(id, EntityType.BODY), "operationType" : BooleanOperationType.UNION });
}

function unite(context is Context, id is Id, q is Query)
{
    if (size(evaluateQuery(context, q)) > 1)
    {
        opBoolean(context, id, { "tools" : q, "operationType" : BooleanOperationType.UNION });
    }
}

function subtract(context is Context, id is Id, targets is Query, tools is Query)
{
    if (size(evaluateQuery(context, tools)) > 0)
    {
        opBoolean(context, id, { "targets" : targets, "tools" : tools, "operationType" : BooleanOperationType.SUBTRACTION });
    }
}

function finish(context is Context, q is Query, name is string, rgb is array)
{
    setProperty(context, { "entities" : q, "propertyType" : PropertyType.NAME, "value" : name });
    setProperty(context, { "entities" : q, "propertyType" : PropertyType.APPEARANCE, "value" : color(rgb[0], rgb[1], rgb[2]) });
}

function place(context is Context, id is Id, q is Query, t is Transform)
{
    opTransform(context, id, { "bodies" : q, "transform" : t });
}

// ------------------------------------------------------------------------------------------------ bought parts
// HQ Camera, in its own frame: lens axis along z, looking towards -z, the board's lens-side face at z = 0.
function hqCamera(context is Context, id is Id, lensD is ValueWithUnits, lensLen is ValueWithUnits,
    lensStart is ValueWithUnits, m12 is boolean)
{
    cbx(context, id + "pcb", mmv(0), mmv(0), mmv(38), mmv(38), mmv(0), mmv(1.4));
    cbx(context, id + "conn", mmv(0), mmv(16), mmv(22), mmv(5), mmv(1.4), mmv(4.0));   // ribbon connector, top edge
    if (m12)
    {
        cbx(context, id + "holder", mmv(0), mmv(0), mmv(17), mmv(17), mmv(-8), mmv(0));   // M12 lens holder
    }
    else
    {
        zcyl(context, id + "housing", mmv(0), mmv(0), mmv(-10.35), mmv(0), mmv(18));      // CS housing + back-focus ring
    }
    zcyl(context, id + "lens", mmv(0), mmv(0), -lensStart - lensLen, -lensStart, lensD / 2);
    finish(context, qCreatedBy(id + "pcb", EntityType.BODY), "(bought) HQ Camera", C_PCB);
    finish(context, qCreatedBy(id + "conn", EntityType.BODY), "(bought) HQ Camera connector", C_DARK);
    finish(context, qUnion([qCreatedBy(id + "holder", EntityType.BODY), qCreatedBy(id + "housing", EntityType.BODY)]),
        "(bought) HQ Camera lens mount", C_DARK);
    finish(context, qCreatedBy(id + "lens", EntityType.BODY), "(bought) lens", C_LENS);
}

// Camera Module 3 (standard or Wide), in its own frame: lens axis at the origin looking towards -z, board's lens side
// at z = 0, ribbon connector at the +y edge.
function cm3Camera(context is Context, id is Id, wide is boolean)
{
    bx(context, id + "pcb", mmv(-12.5), mmv(12.5), mmv(-14.4), mmv(9.462), mmv(0), mmv(1.12));
    cbx(context, id + "conn", mmv(0), mmv(6.5), mmv(20), mmv(5.5), mmv(1.12), mmv(3.87));
    cbx(context, id + "holder", mmv(0), mmv(0), mmv(8.5), mmv(8.5), mmv(-6.5), mmv(0));
    zcyl(context, id + "lens", mmv(0), mmv(0), wide ? mmv(-10.3) : mmv(-9.4), mmv(-6.5), wide ? mmv(4.6) : mmv(3.5));
    finish(context, qUnion([qCreatedBy(id + "pcb", EntityType.BODY), qCreatedBy(id + "conn", EntityType.BODY)]),
        wide ? "(bought) Camera Module 3 Wide" : "(bought) Camera Module 3", C_PCB);
    finish(context, qUnion([qCreatedBy(id + "holder", EntityType.BODY), qCreatedBy(id + "lens", EntityType.BODY)]),
        "(bought) Camera Module 3 lens", C_LENS);
}

// Pi 5 with Active Cooler, in its own frame: board centred at the origin, 85 along x (USB/Ethernet end at +x),
// underside at z = 0.
function pi5(context is Context, id is Id)
{
    cbx(context, id + "pcb", mmv(0), mmv(0), mmv(85), mmv(56), mmv(0), mmv(1.6));
    bx(context, id + "cooler", mmv(-42.5 + 4), mmv(-42.5 + 4 + 63.5), mmv(-21.25), mmv(21.25), mmv(1.6), mmv(10.6));
    bx(context, id + "ports", mmv(42.5 - 21.5), mmv(44.5), mmv(-26.5), mmv(26.5), mmv(1.6), mmv(17.6));
    finish(context, qCreatedBy(id + "pcb", EntityType.BODY), "(bought) Raspberry Pi 5", C_PCB);
    finish(context, qUnion([qCreatedBy(id + "cooler", EntityType.BODY), qCreatedBy(id + "ports", EntityType.BODY)]),
        "(bought) Pi 5 Active Cooler and ports", C_STEEL);
}

function pi5Holes() returns array
{
    return [vector(mmv(-39), mmv(-24.5)), vector(mmv(19), mmv(-24.5)), vector(mmv(-39), mmv(24.5)), vector(mmv(19), mmv(24.5))];
}

// display module, in its own frame: centred, back at z = 0, glass at z = t
function displayModule(context is Context, id is Id, w is ValueWithUnits, h is ValueWithUnits, t is ValueWithUnits,
    aw is ValueWithUnits, ah is ValueWithUnits, adx is ValueWithUnits, ady is ValueWithUnits, name is string)
{
    cbx(context, id + "body", mmv(0), mmv(0), w, h, mmv(0), t - mmv(0.3));
    cbx(context, id + "screen", adx, ady, aw, ah, t - mmv(0.3), t);
    finish(context, qCreatedBy(id + "body", EntityType.BODY), "(bought) " ~ name, C_DARK);
    finish(context, qCreatedBy(id + "screen", EntityType.BODY), "(bought) " ~ name ~ " screen", C_SCREEN);
}

// ------------------------------------------------------------------------------------------------ viewfinder tray
// The box every unit shares: back plate at z in [z0, z0 + t], walls up to the display, a Pi 5 inside on four
// standoffs, the display under a face plate (second printed part) with a window for the active area.
// Returns the outer size and the z of the face plate's top, for the callers' own features.
function viewfinderTray(context is Context, id is Id, d is map, z0 is ValueWithUnits, name is string,
    displayName is string) returns map
{
    const fit = d.fit;
    const wall = d.wall;
    const cw = max(d.disp_w, mmv(89)) + 2 * fit;            // cavity: the display, or the Pi 5 if bigger
    const ch = max(d.disp_h, mmv(60)) + 2 * fit;
    const tw = cw + 2 * wall;
    const th = ch + 2 * wall;
    const zIn = z0 + d.plate_t;                              // top of the back plate
    const zDisp = zIn + d.tray_depth;                        // the display's back
    const zTop = zDisp + d.disp_t;                           // the display's glass = the face plate's underside

    // tray: walls and back plate
    cbx(context, id + "tray" + "add" + "outer", mmv(0), mmv(0), tw, th, z0, zTop);
    cbx(context, id + "tray" + "cut" + "cavity", mmv(0), mmv(0), cw, ch, zIn, zTop + mmv(1));
    // Pi 5 standoffs (M2.5 heat-set inserts, 3.6 mm holes)
    const holes = pi5Holes();
    for (var i = 0; i < 4; i += 1)
    {
        const p = holes[i];
        zcyl(context, id + "tray" + "add" + ("so" ~ i), p[0] + d.pi_dx, p[1] + d.pi_dy, zIn - mmv(0.5), zIn + d.pi_standoff, mmv(3.5));
        zcyl(context, id + "tray" + "cut" + ("soh" ~ i), p[0] + d.pi_dx, p[1] + d.pi_dy, zIn + mmv(1), zIn + d.pi_standoff + mmv(1), mmv(1.8));
    }
    // two bars across the cavity under the display's top and bottom edges
    for (var i = 0; i < 2; i += 1)
    {
        const sy = (i == 0) ? 1 : -1;
        cbx(context, id + "tray" + "add" + ("ledge" ~ i), mmv(0), sy * (d.disp_h / 2 - mmv(2.5)), cw + mmv(1), mmv(5), zDisp - mmv(3), zDisp);
    }
    // vents in the two short walls, level with the Pi's cooler; power cable slot in the bottom wall
    for (var i = 0; i < 4; i += 1)
    {
        const yv = (i - 1.5) * mmv(7);
        bx(context, id + "tray" + "cut" + ("ventL" ~ i), -tw / 2 - mmv(1), -cw / 2 + mmv(1), yv - mmv(1.5), yv + mmv(1.5),
            zIn + d.pi_standoff + mmv(3), zIn + d.pi_standoff + mmv(16));
        bx(context, id + "tray" + "cut" + ("ventR" ~ i), tw / 2 + mmv(1), cw / 2 - mmv(1), yv - mmv(1.5), yv + mmv(1.5),
            zIn + d.pi_standoff + mmv(3), zIn + d.pi_standoff + mmv(16));
    }
    cbx(context, id + "tray" + "cut" + "cable", d.pi_dx - mmv(31.3), -th / 2, mmv(16), wall * 3, zIn + d.pi_standoff - mmv(1),
        zIn + d.pi_standoff + mmv(10));
    unite(context, id + "tray" + "u", qCreatedBy(id + "tray" + "add", EntityType.BODY));
    subtract(context, id + "tray" + "s", qCreatedBy(id + "tray" + "add", EntityType.BODY), qCreatedBy(id + "tray" + "cut", EntityType.BODY));

    // face plate: covers the top, holds the display down, skirt round the outside of the walls
    const so = mmv(2.4);                                     // skirt thickness
    cbx(context, id + "face" + "add" + "plate", mmv(0), mmv(0), tw + 2 * (fit + so), th + 2 * (fit + so), zTop, zTop + d.face_t);
    cbx(context, id + "face" + "add" + "skirt", mmv(0), mmv(0), tw + 2 * (fit + so), th + 2 * (fit + so), zTop - d.skirt_h, zTop);
    cbx(context, id + "face" + "cut" + "inner", mmv(0), mmv(0), tw + 2 * fit, th + 2 * fit, zTop - d.skirt_h - mmv(1), zTop);
    cbx(context, id + "face" + "cut" + "window", d.act_dx, d.act_dy, d.act_w + mmv(1), d.act_h + mmv(1), zTop - mmv(1), zTop + d.face_t + mmv(1));
    unite(context, id + "face" + "u", qCreatedBy(id + "face" + "add", EntityType.BODY));
    subtract(context, id + "face" + "s", qCreatedBy(id + "face" + "add", EntityType.BODY), qCreatedBy(id + "face" + "cut", EntityType.BODY));

    // bought parts inside
    pi5(context, id + "pi");
    place(context, id + "piPlace", qCreatedBy(id + "pi", EntityType.BODY), transform(vector(d.pi_dx, d.pi_dy, zIn + d.pi_standoff)));
    displayModule(context, id + "disp", d.disp_w, d.disp_h, d.disp_t, d.act_w, d.act_h, d.act_dx, d.act_dy, displayName);
    place(context, id + "dispPlace", qCreatedBy(id + "disp", EntityType.BODY), transform(vector(mmv(0), mmv(0), zDisp)));

    return { "tw" : tw, "th" : th, "zIn" : zIn, "zTop" : zTop, "trayId" : id + "tray", "faceId" : id + "face" };
}

predicate trayParams(definition is map)
{
    annotation { "Name" : "Display outline width" }
    isLength(definition.disp_w, { (millimeter) : [10, 121, 400] } as LengthBoundSpec);
    annotation { "Name" : "Display outline height" }
    isLength(definition.disp_h, { (millimeter) : [10, 77, 400] } as LengthBoundSpec);
    annotation { "Name" : "Display thickness incl. parts on its back" }
    isLength(definition.disp_t, { (millimeter) : [1, 9, 60] } as LengthBoundSpec);
    annotation { "Name" : "Active area width" }
    isLength(definition.act_w, { (millimeter) : [5, 108, 400] } as LengthBoundSpec);
    annotation { "Name" : "Active area height" }
    isLength(definition.act_h, { (millimeter) : [5, 65, 400] } as LengthBoundSpec);
    annotation { "Name" : "Active area offset x" }
    isLength(definition.act_dx, { (millimeter) : [-100, 0, 100] } as LengthBoundSpec);
    annotation { "Name" : "Active area offset y" }
    isLength(definition.act_dy, { (millimeter) : [-100, 0, 100] } as LengthBoundSpec);
    annotation { "Name" : "Tray depth (back plate to display)" }
    isLength(definition.tray_depth, { (millimeter) : [10, 30, 200] } as LengthBoundSpec);
    annotation { "Name" : "Pi 5 standoff height" }
    isLength(definition.pi_standoff, { (millimeter) : [2, 5, 50] } as LengthBoundSpec);
    annotation { "Name" : "Pi 5 offset x" }
    isLength(definition.pi_dx, { (millimeter) : [-100, 0, 100] } as LengthBoundSpec);
    annotation { "Name" : "Pi 5 offset y" }
    isLength(definition.pi_dy, { (millimeter) : [-100, 0, 100] } as LengthBoundSpec);
    annotation { "Name" : "Wall" }
    isLength(definition.wall, { (millimeter) : [1, 3, 10] } as LengthBoundSpec);
    annotation { "Name" : "Back plate thickness" }
    isLength(definition.plate_t, { (millimeter) : [1, 4, 20] } as LengthBoundSpec);
    annotation { "Name" : "Face plate thickness" }
    isLength(definition.face_t, { (millimeter) : [1, 2.5, 10] } as LengthBoundSpec);
    annotation { "Name" : "Face plate skirt" }
    isLength(definition.skirt_h, { (millimeter) : [1, 6, 30] } as LengthBoundSpec);
    annotation { "Name" : "Fit clearance (per side)" }
    isLength(definition.fit, { (millimeter) : [0, 0.4, 3] } as LengthBoundSpec);
}

// ------------------------------------------------------------------------------------------------ machine parameters
predicate chamberParams(definition is map)
{
    annotation { "Name" : "ch_front_y: chamber front face" }
    isLength(definition.ch_front_y, { (millimeter) : [-3000, -120, 3000] } as LengthBoundSpec);
    annotation { "Name" : "ch_left_x: chamber left face (under the door)" }
    isLength(definition.ch_left_x, { (millimeter) : [-3000, -115, 3000] } as LengthBoundSpec);
    annotation { "Name" : "ch_right_x: start of the rounded right end" }
    isLength(definition.ch_right_x, { (millimeter) : [-3000, 230, 3000] } as LengthBoundSpec);
    annotation { "Name" : "ch_top_z: chamber top plate" }
    isLength(definition.ch_top_z, { (millimeter) : [0, 1130, 3000] } as LengthBoundSpec);
    annotation { "Name" : "ch_vert_z: bottom of the vertical walls" }
    isLength(definition.ch_vert_z, { (millimeter) : [0, 765, 3000] } as LengthBoundSpec);
}

predicate frontPortParams(definition is map)
{
    annotation { "Name" : "fp_x: front port centre x" }
    isLength(definition.fp_x, { (millimeter) : [-3000, 5, 3000] } as LengthBoundSpec);
    annotation { "Name" : "fp_z: front port centre height" }
    isLength(definition.fp_z, { (millimeter) : [0, 1030, 3000] } as LengthBoundSpec);
    annotation { "Name" : "fp_tilt: port axis above horizontal" }
    isAngle(definition.fp_tilt, { (degree) : [-90, 20, 90] } as AngleBoundSpec);
    annotation { "Name" : "fp_yaw: port axis towards the left" }
    isAngle(definition.fp_yaw, { (degree) : [-90, 8, 90] } as AngleBoundSpec);
    annotation { "Name" : "fp_hood_sides: sides of the faceted hood" }
    isInteger(definition.fp_hood_sides, { (unitless) : [3, 12, 64] } as IntegerBoundSpec);
    annotation { "Name" : "fp_hood_rot: hood polygon rotation (a flat at this angle from horizontal)" }
    isAngle(definition.fp_hood_rot, { (degree) : [-180, 0, 180] } as AngleBoundSpec);
    annotation { "Name" : "fp_hood_af: hood across flats" }
    isLength(definition.fp_hood_af, { (millimeter) : [10, 100, 400] } as LengthBoundSpec);
    annotation { "Name" : "fp_hood_depth: hood face out from the chamber face" }
    isLength(definition.fp_hood_depth, { (millimeter) : [1, 40, 300] } as LengthBoundSpec);
    annotation { "Name" : "fp_hood_bore: hood bore diameter" }
    isLength(definition.fp_hood_bore, { (millimeter) : [5, 55, 300] } as LengthBoundSpec);
    annotation { "Name" : "fp_glass_d: clear glass diameter" }
    isLength(definition.fp_glass_d, { (millimeter) : [5, 50, 300] } as LengthBoundSpec);
    annotation { "Name" : "fp_glass_recess: glass below the hood face" }
    isLength(definition.fp_glass_recess, { (millimeter) : [0, 25, 300] } as LengthBoundSpec);
}

predicate leftPortParams(definition is map)
{
    annotation { "Name" : "door_t: door thickness" }
    isLength(definition.door_t, { (millimeter) : [1, 16, 100] } as LengthBoundSpec);
    annotation { "Name" : "door_w: door width (front to back)" }
    isLength(definition.door_w, { (millimeter) : [10, 236, 1000] } as LengthBoundSpec);
    annotation { "Name" : "door_z0: door bottom" }
    isLength(definition.door_z0, { (millimeter) : [0, 775, 3000] } as LengthBoundSpec);
    annotation { "Name" : "door_z1: door top" }
    isLength(definition.door_z1, { (millimeter) : [0, 1115, 3000] } as LengthBoundSpec);
    annotation { "Name" : "door_hinge_y: hinge axis (front edge)" }
    isLength(definition.door_hinge_y, { (millimeter) : [-3000, -128, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lp_y: sight glass centre y" }
    isLength(definition.lp_y, { (millimeter) : [-3000, -60, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lp_z: sight glass centre height" }
    isLength(definition.lp_z, { (millimeter) : [0, 1065, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lp_flange_d: sight glass flange OD" }
    isLength(definition.lp_flange_d, { (millimeter) : [5, 55, 300] } as LengthBoundSpec);
    annotation { "Name" : "lp_protrusion: flange out from the door" }
    isLength(definition.lp_protrusion, { (millimeter) : [1, 25, 300] } as LengthBoundSpec);
    annotation { "Name" : "lp_glass_d: clear glass diameter" }
    isLength(definition.lp_glass_d, { (millimeter) : [5, 30, 300] } as LengthBoundSpec);
    annotation { "Name" : "stack_angle: ultrasonic stack below horizontal" }
    isAngle(definition.stack_angle, { (degree) : [0, 40, 90] } as AngleBoundSpec);
    annotation { "Name" : "stack_z: stack axis at the door's outer face" }
    isLength(definition.stack_z, { (millimeter) : [0, 850, 3000] } as LengthBoundSpec);
    annotation { "Name" : "stack_d: stack (transducer) diameter" }
    isLength(definition.stack_d, { (millimeter) : [5, 60, 300] } as LengthBoundSpec);
}

predicate furnaceParams(definition is map)
{
    annotation { "Name" : "furn_r: furnace body radius" }
    isLength(definition.furn_r, { (millimeter) : [10, 135, 1000] } as LengthBoundSpec);
    annotation { "Name" : "furn_top_z: furnace body top (lid seat)" }
    isLength(definition.furn_top_z, { (millimeter) : [0, 1345, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lid_r: lid radius at its rim" }
    isLength(definition.lid_r, { (millimeter) : [10, 152, 1000] } as LengthBoundSpec);
    annotation { "Name" : "lid_h1: lid straight part" }
    isLength(definition.lid_h1, { (millimeter) : [1, 75, 1000] } as LengthBoundSpec);
    annotation { "Name" : "lid_h2: lid tapered part" }
    isLength(definition.lid_h2, { (millimeter) : [1, 90, 1000] } as LengthBoundSpec);
    annotation { "Name" : "lid_top_r: lid radius at its top" }
    isLength(definition.lid_top_r, { (millimeter) : [5, 92, 1000] } as LengthBoundSpec);
    annotation { "Name" : "lid_hinge_x: lid hinge axis x" }
    isLength(definition.lid_hinge_x, { (millimeter) : [-3000, -164, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lid_hinge_z: lid hinge axis height" }
    isLength(definition.lid_hinge_z, { (millimeter) : [0, 1343, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lid_open: lid opening angle" }
    isAngle(definition.lid_open, { (degree) : [0, 100, 180] } as AngleBoundSpec);
    annotation { "Name" : "tw_x: lid window centre x" }
    isLength(definition.tw_x, { (millimeter) : [-1000, 0, 1000] } as LengthBoundSpec);
    annotation { "Name" : "tw_y: lid window centre y" }
    isLength(definition.tw_y, { (millimeter) : [-1000, 0, 1000] } as LengthBoundSpec);
    annotation { "Name" : "tw_len: lid window length (x)" }
    isLength(definition.tw_len, { (millimeter) : [5, 80, 1000] } as LengthBoundSpec);
    annotation { "Name" : "tw_wid: lid window width (y)" }
    isLength(definition.tw_wid, { (millimeter) : [5, 60, 1000] } as LengthBoundSpec);
    annotation { "Name" : "tw_corner_r: lid window corner radius" }
    isLength(definition.tw_corner_r, { (millimeter) : [0, 8, 500] } as LengthBoundSpec);
}

predicate frameParams(definition is map)
{
    annotation { "Name" : "fr_front_y: blue frame front face" }
    isLength(definition.fr_front_y, { (millimeter) : [-3000, 165, 3000] } as LengthBoundSpec);
    annotation { "Name" : "fr_top_z: blue frame top" }
    isLength(definition.fr_top_z, { (millimeter) : [0, 1600, 3000] } as LengthBoundSpec);
    annotation { "Name" : "fr_x0: blue frame left side" }
    isLength(definition.fr_x0, { (millimeter) : [-3000, -115, 3000] } as LengthBoundSpec);
    annotation { "Name" : "fr_x1: blue frame right side" }
    isLength(definition.fr_x1, { (millimeter) : [-3000, 630, 3000] } as LengthBoundSpec);
}

// local frames of the three ports
function frontPortCS(d is map) returns CoordSystem
{
    const n = vector(-sin(d.fp_yaw) * cos(d.fp_tilt), -cos(d.fp_yaw) * cos(d.fp_tilt), sin(d.fp_tilt));
    const o = vector(d.fp_x, d.ch_front_y, d.fp_z) + n * d.fp_hood_depth;
    return coordSystem(o, normalize(cross(vector(0, 0, 1), n)), n);
}

function leftPortCS(d is map) returns CoordSystem
{
    const o = vector(d.ch_left_x - d.door_t - d.lp_protrusion, d.lp_y, d.lp_z);
    return coordSystem(o, vector(0, -1, 0), vector(-1, 0, 0));
}

function lidTopZ(d is map) returns ValueWithUnits
{
    return d.furn_top_z + d.lid_h1 + d.lid_h2;
}

// ------------------------------------------------------------------------------------------------ machine context
annotation { "Feature Type Name" : "rePowder context (approximate)",
        "Feature Type Description" : "The parts of the rePowder around the three viewing windows, from the training videos and AMAZEMET's documents; every size is a variable to measure" }
export const repowderContext = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        chamberParams(definition);
        frontPortParams(definition);
        leftPortParams(definition);
        furnaceParams(definition);
        frameParams(definition);
        annotation { "Name" : "Show the lid open", "Default" : true }
        definition.showOpenLid is boolean;
    }
    {
        const d = definition;
        const backY = -d.ch_front_y;
        // chamber, upper (vertical-walled) part: flat front, half-round right end
        bx(context, id + "ch" + "flat", d.ch_left_x, d.ch_right_x, d.ch_front_y, backY, d.ch_vert_z, d.ch_top_z);
        zcyl(context, id + "ch" + "round", d.ch_right_x, mmv(0), d.ch_vert_z, d.ch_top_z, backY);
        bx(context, id + "ch" + "plate", d.ch_left_x - mmv(40), d.ch_right_x, d.ch_front_y, backY, d.ch_top_z, d.ch_top_z + mmv(20));
        zcyl(context, id + "ch" + "plateR", d.ch_right_x, mmv(0), d.ch_top_z, d.ch_top_z + mmv(20), backY);
        unite(context, id + "chU", qCreatedBy(id + "ch", EntityType.BODY));
        finish(context, qCreatedBy(id + "ch", EntityType.BODY), "(machine) atomization chamber", C_STEEL);

        // front port: the faceted hood and the glass at the bottom of its bore
        const fcs = frontPortCS(d);
        ngonPrism(context, id + "fp" + "hood", mmv(0), mmv(0), d.fp_hood_sides, d.fp_hood_af, d.fp_hood_rot,
            -d.fp_hood_depth - mmv(5), mmv(0));
        zcyl(context, id + "fpcut" + "bore", mmv(0), mmv(0), -d.fp_glass_recess, mmv(1), d.fp_hood_bore / 2);
        subtract(context, id + "fpS", qCreatedBy(id + "fp" + "hood", EntityType.BODY), qCreatedBy(id + "fpcut", EntityType.BODY));
        zcyl(context, id + "fp" + "glass", mmv(0), mmv(0), -d.fp_glass_recess - mmv(8), -d.fp_glass_recess, d.fp_glass_d / 2);
        finish(context, qCreatedBy(id + "fp" + "hood", EntityType.BODY), "(machine) front port hood", C_DARK);
        finish(context, qCreatedBy(id + "fp" + "glass", EntityType.BODY), "(machine) front port glass", C_GLASS);
        place(context, id + "fpPlace", qCreatedBy(id + "fp", EntityType.BODY), toWorld(fcs));

        // left door, its sight glass, and the ultrasonic stack leaving it at stack_angle
        const xo = d.ch_left_x - d.door_t;
        bx(context, id + "door", xo, d.ch_left_x, -d.door_w / 2, d.door_w / 2, d.door_z0, d.door_z1);
        finish(context, qCreatedBy(id + "door", EntityType.BODY), "(machine) chamber door", C_STEEL);
        cyl(context, id + "lp" + "flange", vector(xo, d.lp_y, d.lp_z), vector(xo - d.lp_protrusion, d.lp_y, d.lp_z), d.lp_flange_d / 2);
        cyl(context, id + "lp" + "glass", vector(xo - d.lp_protrusion - mmv(0.5), d.lp_y, d.lp_z),
            vector(xo - d.lp_protrusion + mmv(0.1), d.lp_y, d.lp_z), d.lp_glass_d / 2);
        finish(context, qCreatedBy(id + "lp" + "flange", EntityType.BODY), "(machine) left sight glass flange", C_STEEL);
        finish(context, qCreatedBy(id + "lp" + "glass", EntityType.BODY), "(machine) left sight glass", C_GLASS);
        const sOut = vector(-cos(d.stack_angle), 0, -sin(d.stack_angle));
        const s0 = vector(xo, mmv(0), d.stack_z);
        cyl(context, id + "stack", s0, s0 + sOut * mmv(260), d.stack_d / 2);
        finish(context, qCreatedBy(id + "stack", EntityType.BODY), "(machine) ultrasonic stack (outside the door)", C_STEEL);

        // furnace body, lid with its window
        zcyl(context, id + "furn", mmv(0), mmv(0), d.ch_top_z + mmv(20), d.furn_top_z, d.furn_r);
        finish(context, qCreatedBy(id + "furn", EntityType.BODY), "(machine) furnace body", C_STEEL);
        buildLid(context, id + "lid", d, "(machine) furnace lid", "(machine) lid window", C_STEEL, C_GLASS);
        if (d.showOpenLid)
        {
            buildLid(context, id + "lidOpen", d, "(machine) furnace lid, open", "(machine) lid window, open", C_GHOST, C_GHOST);
            place(context, id + "lidOpenRot", qCreatedBy(id + "lidOpen", EntityType.BODY),
                rotationAround(line(vector(d.lid_hinge_x, mmv(0), d.lid_hinge_z), vector(0, 1, 0)), -d.lid_open));
        }

        // blue frame (cabinet) behind the chamber
        bx(context, id + "frame", d.fr_x0, d.fr_x1, d.fr_front_y, d.fr_front_y + mmv(500), mmv(175), d.fr_top_z);
        finish(context, qCreatedBy(id + "frame", EntityType.BODY), "(machine) blue frame", C_BLUE);
    });

function buildLid(context is Context, id is Id, d is map, name is string, windowName is string, rgb is array, glassRgb is array)
{
    const z0 = d.furn_top_z;
    const z1 = z0 + d.lid_h1;
    const z2 = z1 + d.lid_h2;
    zcyl(context, id + "body" + "a", mmv(0), mmv(0), z0, z1, d.lid_r);
    fCone(context, id + "body" + "b", { "bottomCenter" : vector(mmv(0), mmv(0), z1), "topCenter" : vector(mmv(0), mmv(0), z2),
                "bottomRadius" : d.lid_r, "topRadius" : d.lid_top_r });
    unite(context, id + "bodyU", qCreatedBy(id + "body", EntityType.BODY));
    rrectPrism(context, id + "winCut", d.tw_x, d.tw_y, d.tw_len, d.tw_wid, d.tw_corner_r, z2 - mmv(3), z2 + mmv(1));
    subtract(context, id + "bodyS", qCreatedBy(id + "body", EntityType.BODY), qCreatedBy(id + "winCut", EntityType.BODY));
    rrectPrism(context, id + "win", d.tw_x, d.tw_y, d.tw_len, d.tw_wid, d.tw_corner_r, z2 - mmv(3), z2 - mmv(0.5));
    finish(context, qCreatedBy(id + "body", EntityType.BODY), name, rgb);
    finish(context, qCreatedBy(id + "win", EntityType.BODY), windowName, glassRgb);
}

// ------------------------------------------------------------------------------------------------ front port unit
annotation { "Feature Type Name" : "Front port viewfinder (HQ + wide)",
        "Feature Type Description" : "HQ Camera (M12) and Camera Module 3 Wide side by side in front of the view port glass, a Pi 5 and an HDMI display, on a socket that slides over the port's faceted hood" }
export const frontViewfinder = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        chamberParams(definition);
        frontPortParams(definition);
        trayParams(definition);
        annotation { "Name" : "Socket length over the hood" }
        isLength(definition.sock_len, { (millimeter) : [2, 18, 200] } as LengthBoundSpec);
        annotation { "Name" : "Socket wall" }
        isLength(definition.sock_wall, { (millimeter) : [1, 3, 20] } as LengthBoundSpec);
        annotation { "Name" : "Camera boards above the hood face" }
        isLength(definition.cam_gap, { (millimeter) : [0, 1, 100] } as LengthBoundSpec);
        annotation { "Name" : "HQ lens axis offset x" }
        isLength(definition.hq_x, { (millimeter) : [-200, -14, 200] } as LengthBoundSpec);
        annotation { "Name" : "HQ lens axis offset y" }
        isLength(definition.hq_y, { (millimeter) : [-200, 0, 200] } as LengthBoundSpec);
        annotation { "Name" : "HQ is the M12 version", "Default" : true }
        definition.hq_m12 is boolean;
        annotation { "Name" : "HQ lens diameter" }
        isLength(definition.lens_d, { (millimeter) : [5, 16, 100] } as LengthBoundSpec);
        annotation { "Name" : "HQ lens length" }
        isLength(definition.lens_len, { (millimeter) : [1, 18, 200] } as LengthBoundSpec);
        annotation { "Name" : "HQ lens start (board to lens back)" }
        isLength(definition.lens_start, { (millimeter) : [0, 8, 100] } as LengthBoundSpec);
        annotation { "Name" : "Wide camera lens axis offset x" }
        isLength(definition.cm_x, { (millimeter) : [-200, 18, 200] } as LengthBoundSpec);
        annotation { "Name" : "Wide camera lens axis offset y" }
        isLength(definition.cm_y, { (millimeter) : [-200, 0, 200] } as LengthBoundSpec);
        annotation { "Name" : "Ball plunger thread tap drill" }
        isLength(definition.plunger_tap, { (millimeter) : [1, 5, 20] } as LengthBoundSpec);
    }
    {
        const d = definition;
        const n = d.fp_hood_sides;
        const afIn = d.fp_hood_af + 2 * d.fit;
        const afOut = afIn + 2 * d.sock_wall;
        const zb = d.cam_gap + mmv(1.4) + mmv(4);            // tray back plate: HQ board, then 4 mm bosses

        // socket over the hood, up to the tray's back plate
        ngonPrism(context, id + "sock" + "add" + "outer", mmv(0), mmv(0), n, afOut, d.fp_hood_rot, -d.sock_len, zb + d.plate_t);
        ngonPrism(context, id + "sock" + "cut" + "inner", mmv(0), mmv(0), n, afIn, d.fp_hood_rot, -d.sock_len - mmv(1), mmv(0));
        // camera space between the hood face and the back plate: open to the hood's bore
        zcyl(context, id + "sock" + "cut" + "camspace", mmv(0), mmv(0), mmv(-0.5), zb + mmv(0.01), afIn / 2 / cos(180 / n * degree) - mmv(1));
        // ball plunger boss on the top flat, pointing at the hood
        const rIn = afIn / 2;
        const zp = -d.sock_len / 2;
        cyl(context, id + "sock" + "add" + "plboss", vector(mmv(0), rIn, zp), vector(mmv(0), rIn + d.sock_wall + mmv(8), zp), mmv(6));
        cyl(context, id + "sock" + "cut" + "plhole", vector(mmv(0), rIn - mmv(1), zp), vector(mmv(0), rIn + d.sock_wall + mmv(9), zp), d.plunger_tap / 2);
        unite(context, id + "sock" + "u", qCreatedBy(id + "sock" + "add", EntityType.BODY));
        subtract(context, id + "sock" + "s", qCreatedBy(id + "sock" + "add", EntityType.BODY), qCreatedBy(id + "sock" + "cut", EntityType.BODY));

        // tray, Pi 5 and display
        const t = viewfinderTray(context, id + "vf", d, zb, "front", "5 in HDMI display");

        // cameras hang under the back plate, boards' lens side d.cam_gap above the hood face
        hqCamera(context, id + "hq", d.lens_d, d.lens_len, d.lens_start, d.hq_m12);
        place(context, id + "hqPlace", qCreatedBy(id + "hq", EntityType.BODY), transform(vector(d.hq_x, d.hq_y, d.cam_gap)));
        cm3Camera(context, id + "cm", true);
        place(context, id + "cmPlace", qCreatedBy(id + "cm", EntityType.BODY), transform(vector(d.cm_x, d.cm_y, d.cam_gap)));

        // bosses under the back plate for both cameras, with ribbon slots through the plate
        for (var i = 0; i < 4; i += 1)
        {
            const sx = (i % 2 == 0) ? 1 : -1;
            const sy = (i < 2) ? 1 : -1;
            zcyl(context, id + "boss" + "add" + ("hq" ~ i), d.hq_x + sx * mmv(15), d.hq_y + sy * mmv(15), d.cam_gap + mmv(1.4), zb + mmv(0.5), mmv(2.75));
            zcyl(context, id + "boss" + "cut" + ("hqh" ~ i), d.hq_x + sx * mmv(15), d.hq_y + sy * mmv(15), d.cam_gap + mmv(1), zb + d.plate_t + mmv(1), mmv(1.4));
            const cy = (i < 2) ? mmv(0.1) : mmv(-12.4);
            zcyl(context, id + "boss" + "add" + ("cm" ~ i), d.cm_x + sx * mmv(10.5), d.cm_y + cy, d.cam_gap + mmv(1.12), zb + mmv(0.5), mmv(2.25));
            zcyl(context, id + "boss" + "cut" + ("cmh" ~ i), d.cm_x + sx * mmv(10.5), d.cm_y + cy, d.cam_gap + mmv(0.8), zb + d.plate_t + mmv(1), mmv(1.2));
        }
        cbx(context, id + "boss" + "cut" + "slotHQ", d.hq_x, d.hq_y + mmv(23), mmv(18), mmv(3), zb - mmv(1), zb + d.plate_t + mmv(1));
        cbx(context, id + "boss" + "cut" + "slotCM", d.cm_x, d.cm_y + mmv(13.5), mmv(18), mmv(3), zb - mmv(1), zb + d.plate_t + mmv(1));
        unite(context, id + "join", qUnion([qCreatedBy(id + "sock" + "add", EntityType.BODY), qCreatedBy(t.trayId + "add", EntityType.BODY),
                        qCreatedBy(id + "boss" + "add", EntityType.BODY)]));
        subtract(context, id + "joinS", qUnion([qCreatedBy(id + "sock" + "add", EntityType.BODY), qCreatedBy(t.trayId + "add", EntityType.BODY),
                        qCreatedBy(id + "boss" + "add", EntityType.BODY)]), qCreatedBy(id + "boss" + "cut", EntityType.BODY));
        finish(context, qUnion([qCreatedBy(id + "sock" + "add", EntityType.BODY), qCreatedBy(t.trayId + "add", EntityType.BODY),
                    qCreatedBy(id + "boss" + "add", EntityType.BODY)]), "FRONT socket + tray (print)", C_PRINT);
        finish(context, qCreatedBy(t.faceId + "add", EntityType.BODY), "FRONT face plate (print)", C_PRINT2);

        place(context, id + "place", qCreatedBy(id, EntityType.BODY), toWorld(frontPortCS(d)));
    });

// ------------------------------------------------------------------------------------------------ left port unit
annotation { "Feature Type Name" : "Left port viewfinder",
        "Feature Type Description" : "A Camera Module 3 on the axis of the door's sight glass, a Pi 5 and a DSI display, on a clamp collar round the sight glass flange; rides on the door" }
export const leftViewfinder = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        chamberParams(definition);
        leftPortParams(definition);
        trayParams(definition);
        annotation { "Name" : "Collar length over the flange" }
        isLength(definition.col_len, { (millimeter) : [2, 14, 200] } as LengthBoundSpec);
        annotation { "Name" : "Collar wall" }
        isLength(definition.col_wall, { (millimeter) : [1, 4, 20] } as LengthBoundSpec);
        annotation { "Name" : "Camera board above the flange face" }
        isLength(definition.cam_gap, { (millimeter) : [0, 1, 100] } as LengthBoundSpec);
        annotation { "Name" : "Camera Module 3 Wide (else standard)", "Default" : false }
        definition.wide is boolean;
    }
    {
        const d = definition;
        const rIn = d.lp_flange_d / 2 + d.fit;
        const rOut = rIn + d.col_wall;
        const zb = d.cam_gap + mmv(1.12) + mmv(4);

        // clamp collar round the flange, split at the bottom, with an M4 clamp screw across the split
        zcyl(context, id + "col" + "add" + "tube", mmv(0), mmv(0), -d.col_len, zb, rOut);
        zcyl(context, id + "col" + "cut" + "bore", mmv(0), mmv(0), -d.col_len - mmv(1), mmv(0), rIn);
        zcyl(context, id + "col" + "cut" + "camspace", mmv(0), mmv(0), mmv(-0.5), zb + mmv(0.01), rIn - mmv(1));
        bx(context, id + "col" + "add" + "lugs", mmv(-8), mmv(8), -rOut - mmv(9), -rIn, -d.col_len, mmv(0));
        bx(context, id + "col" + "cut" + "split", mmv(-1), mmv(1), -rOut - mmv(10), -rIn + mmv(0.5), -d.col_len - mmv(1), mmv(-0.5));
        cyl(context, id + "col" + "cut" + "screw", vector(mmv(-9), -rOut - mmv(4.5), -d.col_len / 2), vector(mmv(9), -rOut - mmv(4.5), -d.col_len / 2), mmv(2.2));
        unite(context, id + "col" + "u", qCreatedBy(id + "col" + "add", EntityType.BODY));
        subtract(context, id + "col" + "s", qCreatedBy(id + "col" + "add", EntityType.BODY), qCreatedBy(id + "col" + "cut", EntityType.BODY));

        const t = viewfinderTray(context, id + "vf", d, zb, "left", "DSI display");

        cm3Camera(context, id + "cm", d.wide);
        place(context, id + "cmPlace", qCreatedBy(id + "cm", EntityType.BODY), transform(vector(mmv(0), mmv(0), d.cam_gap)));
        for (var i = 0; i < 4; i += 1)
        {
            const sx = (i % 2 == 0) ? 1 : -1;
            const cy = (i < 2) ? mmv(0.1) : mmv(-12.4);
            zcyl(context, id + "boss" + "add" + ("cm" ~ i), sx * mmv(10.5), cy, d.cam_gap + mmv(1.12), zb + mmv(0.5), mmv(2.25));
            zcyl(context, id + "boss" + "cut" + ("cmh" ~ i), sx * mmv(10.5), cy, d.cam_gap + mmv(0.8), zb + d.plate_t + mmv(1), mmv(1.2));
        }
        cbx(context, id + "boss" + "cut" + "slotCM", mmv(0), mmv(13.5), mmv(18), mmv(3), zb - mmv(1), zb + d.plate_t + mmv(1));
        const printed = qUnion([qCreatedBy(id + "col" + "add", EntityType.BODY), qCreatedBy(t.trayId + "add", EntityType.BODY),
                    qCreatedBy(id + "boss" + "add", EntityType.BODY)]);
        unite(context, id + "join", printed);
        subtract(context, id + "joinS", printed, qCreatedBy(id + "boss" + "cut", EntityType.BODY));
        finish(context, printed, "LEFT collar + tray (print)", C_PRINT);
        finish(context, qCreatedBy(t.faceId + "add", EntityType.BODY), "LEFT face plate (print)", C_PRINT2);

        place(context, id + "place", qCreatedBy(id, EntityType.BODY), toWorld(leftPortCS(d)));
    });

// ------------------------------------------------------------------------------------------------ top window unit
annotation { "Feature Type Name" : "Top window camera (swing arm)",
        "Feature Type Description" : "An HQ Camera looking straight down through the furnace lid's window, on an arm that swings about a post on a magnetic base and clicks into place on a ball-plunger detent; the Pi 5 and a small DSI display ride on the post" }
export const topWindowCamera = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        furnaceParams(definition);
        frameParams(definition);
        trayParams(definition);
        annotation { "Name" : "Lens front above the window" }
        isLength(definition.cam_h, { (millimeter) : [20, 250, 2000] } as LengthBoundSpec);
        annotation { "Name" : "Post x" }
        isLength(definition.post_x, { (millimeter) : [-3000, -60, 3000] } as LengthBoundSpec);
        annotation { "Name" : "Post y (from the frame's front face)" }
        isLength(definition.post_dy, { (millimeter) : [-500, 30, 500] } as LengthBoundSpec);
        annotation { "Name" : "Post diameter" }
        isLength(definition.post_d, { (millimeter) : [4, 16, 60] } as LengthBoundSpec);
        annotation { "Name" : "Magnetic base height" }
        isLength(definition.base_h, { (millimeter) : [0, 55, 300] } as LengthBoundSpec);
        annotation { "Name" : "HQ lens diameter" }
        isLength(definition.lens_d, { (millimeter) : [5, 40, 100] } as LengthBoundSpec);
        annotation { "Name" : "HQ lens length" }
        isLength(definition.lens_len, { (millimeter) : [1, 68, 300] } as LengthBoundSpec);
        annotation { "Name" : "HQ lens start (board to lens back)" }
        isLength(definition.lens_start, { (millimeter) : [0, 17.2, 100] } as LengthBoundSpec);
        annotation { "Name" : "Arm width" }
        isLength(definition.arm_w, { (millimeter) : [5, 24, 100] } as LengthBoundSpec);
        annotation { "Name" : "Arm thickness" }
        isLength(definition.arm_t, { (millimeter) : [3, 10, 60] } as LengthBoundSpec);
        annotation { "Name" : "Detent radius (plunger from the post axis)" }
        isLength(definition.det_r, { (millimeter) : [5, 20, 100] } as LengthBoundSpec);
        annotation { "Name" : "Parked angle (arm swung clear)" }
        isAngle(definition.park, { (degree) : [-180, 90, 180] } as AngleBoundSpec);
        annotation { "Name" : "Show the arm parked", "Default" : false }
        definition.showParked is boolean;
        annotation { "Name" : "Display box centre height" }
        isLength(definition.disp_z, { (millimeter) : [0, 1450, 3000] } as LengthBoundSpec);
        annotation { "Name" : "Display box: post axis behind the back plate" }
        isLength(definition.br_len, { (millimeter) : [5, 22, 300] } as LengthBoundSpec);
        annotation { "Name" : "Display tilt (up from vertical)" }
        isAngle(definition.disp_tilt, { (degree) : [0, 0, 60] } as AngleBoundSpec);
        annotation { "Name" : "Ball plunger thread tap drill" }
        isLength(definition.plunger_tap, { (millimeter) : [1, 5, 20] } as LengthBoundSpec);
    }
    {
        const d = definition;
        const lidTop = lidTopZ(d);
        const px = d.post_x;
        const py = d.fr_front_y + d.post_dy;
        const zLens = lidTop + d.cam_h;                                   // lens front
        const zBoard = zLens + d.lens_start + d.lens_len;                // HQ board, lens side
        const zArm = zBoard + mmv(1.4) + mmv(4);                          // underside of the arm
        const dx = d.tw_x - px;
        const dy = d.tw_y - py;
        const armLen = sqrt(dx * dx + dy * dy);
        const heading = atan2(dy, dx);
        const rp = d.post_d / 2;
        const origin = vector(mmv(0), mmv(0), mmv(0));
        const armT = transform(vector(px, py, zArm)) * rotationAround(line(origin, vector(0, 0, 1)), heading);

        // bought: magnetic base on the frame top, post
        cbx(context, id + "mag", px, py, mmv(50), mmv(58), d.fr_top_z, d.fr_top_z + d.base_h);
        finish(context, qCreatedBy(id + "mag", EntityType.BODY), "(bought) switchable magnetic base", C_DARK);
        zcyl(context, id + "post", px, py, d.fr_top_z + d.base_h, zArm + d.arm_t + mmv(40), rp);
        finish(context, qCreatedBy(id + "post", EntityType.BODY), "(bought) post rod", C_STEEL);

        // everything below is built in the arm's frame (post axis at the origin, x towards the window,
        // z = 0 at the arm's underside), then placed with armT

        // detent collar, clamped to the post under the arm's hub; dimples for "working" (0) and "parked"
        const rc = d.det_r + mmv(7);
        zcyl(context, id + "dcol" + "add" + "ring", mmv(0), mmv(0), mmv(-16), mmv(-0.3), rc);
        bx(context, id + "dcol" + "add" + "lug", -rc - mmv(10), -rc + mmv(3), mmv(-6), mmv(6), mmv(-16), mmv(-6));
        zcyl(context, id + "dcol" + "cut" + "bore", mmv(0), mmv(0), mmv(-17), mmv(1), rp + mmv(0.15));
        bx(context, id + "dcol" + "cut" + "split", -rc - mmv(11), -rp + mmv(1), mmv(-0.8), mmv(0.8), mmv(-17), mmv(1));
        cyl(context, id + "dcol" + "cut" + "screw", vector(-rc - mmv(3.5), mmv(-7), mmv(-11)), vector(-rc - mmv(3.5), mmv(7), mmv(-11)), mmv(2.2));
        const dims = [0 * degree, d.park];
        for (var i = 0; i < 2; i += 1)
        {
            const a = dims[i];
            fCone(context, id + "dcol" + "cut" + ("dimple" ~ i), { "bottomCenter" : vector(d.det_r * cos(a), d.det_r * sin(a), mmv(-2.9)),
                        "topCenter" : vector(d.det_r * cos(a), d.det_r * sin(a), mmv(0.2)), "bottomRadius" : mmv(0.3), "topRadius" : mmv(3.0) });
        }
        unite(context, id + "dcol" + "u", qCreatedBy(id + "dcol" + "add", EntityType.BODY));
        subtract(context, id + "dcol" + "s", qCreatedBy(id + "dcol" + "add", EntityType.BODY), qCreatedBy(id + "dcol" + "cut", EntityType.BODY));
        finish(context, qCreatedBy(id + "dcol" + "add", EntityType.BODY), "TOP detent collar (print)", C_PRINT2);
        place(context, id + "dcolPlace", qCreatedBy(id + "dcol", EntityType.BODY), armT);

        // arm: hub round the post with the ball plunger, beam, camera plate with the HQ Camera hanging under it
        zcyl(context, id + "arm" + "add" + "hub", mmv(0), mmv(0), mmv(0), d.arm_t + mmv(6), rc);
        zcyl(context, id + "arm" + "cut" + "bore", mmv(0), mmv(0), mmv(-1), d.arm_t + mmv(7), rp + mmv(0.25));
        zcyl(context, id + "arm" + "cut" + "plunger", d.det_r, mmv(0), mmv(-1), d.arm_t + mmv(7), d.plunger_tap / 2);
        bx(context, id + "arm" + "add" + "beam", mmv(0), armLen, -d.arm_w / 2, d.arm_w / 2, mmv(0), d.arm_t);
        cbx(context, id + "arm" + "add" + "pod", armLen, mmv(0), mmv(46), mmv(46), mmv(0), d.arm_t);
        for (var i = 0; i < 4; i += 1)
        {
            const sx = (i % 2 == 0) ? 1 : -1;
            const sy = (i < 2) ? 1 : -1;
            zcyl(context, id + "arm" + "add" + ("boss" ~ i), armLen + sx * mmv(15), sy * mmv(15), mmv(-4), mmv(0.5), mmv(2.75));
            zcyl(context, id + "arm" + "cut" + ("bh" ~ i), armLen + sx * mmv(15), sy * mmv(15), mmv(-5), d.arm_t + mmv(1), mmv(1.4));
        }
        cbx(context, id + "arm" + "cut" + "ribbon", armLen, mmv(23), mmv(18), mmv(3), mmv(-1), d.arm_t + mmv(1));
        unite(context, id + "arm" + "u", qCreatedBy(id + "arm" + "add", EntityType.BODY));
        subtract(context, id + "arm" + "s", qCreatedBy(id + "arm" + "add", EntityType.BODY), qCreatedBy(id + "arm" + "cut", EntityType.BODY));
        finish(context, qCreatedBy(id + "arm" + "add", EntityType.BODY), "TOP swing arm + camera plate (print)", C_PRINT);

        hqCamera(context, id + "hq", d.lens_d, d.lens_len, d.lens_start, false);
        place(context, id + "hqPlace", qCreatedBy(id + "hq", EntityType.BODY), transform(vector(armLen, mmv(0), zBoard - zArm)));

        const swing = d.showParked ? rotationAround(line(vector(px, py, mmv(0)), vector(0, 0, 1)), d.park) : identityTransform();
        place(context, id + "armPlace", qUnion([qCreatedBy(id + "arm", EntityType.BODY), qCreatedBy(id + "hq", EntityType.BODY)]), swing * armT);

        // display box in front of the post (towards the operator), its back plate br_len in front of the post axis
        const t = viewfinderTray(context, id + "vf", d, mmv(0), "top", "small DSI display");
        cbx(context, id + "vf" + "br" + "add", mmv(0), mmv(0), mmv(30), mmv(24), -d.br_len - rp - mmv(6), mmv(0.5));
        const nOut = vector(0, -cos(d.disp_tilt), sin(d.disp_tilt));
        const yUp = vector(0, sin(d.disp_tilt), cos(d.disp_tilt));
        const o = vector(px, py, d.disp_z) + nOut * d.br_len;
        place(context, id + "boxPlace", qCreatedBy(id + "vf", EntityType.BODY), toWorld(coordSystem(o, cross(yUp, nOut), nOut)));
        // clamp ring round the post, built in place (vertical), split at the back
        zcyl(context, id + "ring" + "add" + "ring", px, py, d.disp_z - mmv(12), d.disp_z + mmv(12), rp + mmv(6));
        bx(context, id + "ring" + "add" + "lug", px - mmv(6), px + mmv(6), py + rp + mmv(3), py + rp + mmv(15), d.disp_z - mmv(12), d.disp_z + mmv(12));
        zcyl(context, id + "ring" + "cut" + "bore", px, py, d.disp_z - mmv(13), d.disp_z + mmv(13), rp + mmv(0.15));
        bx(context, id + "ring" + "cut" + "split", px - mmv(0.8), px + mmv(0.8), py + rp - mmv(1), py + rp + mmv(16), d.disp_z - mmv(13), d.disp_z + mmv(13));
        cyl(context, id + "ring" + "cut" + "screw", vector(px - mmv(7), py + rp + mmv(10), d.disp_z), vector(px + mmv(7), py + rp + mmv(10), d.disp_z), mmv(2.2));
        const printed = qUnion([qCreatedBy(id + "ring" + "add", EntityType.BODY), qCreatedBy(t.trayId + "add", EntityType.BODY),
                    qCreatedBy(id + "vf" + "br" + "add", EntityType.BODY)]);
        unite(context, id + "ring" + "u", printed);
        subtract(context, id + "ring" + "s", printed, qCreatedBy(id + "ring" + "cut", EntityType.BODY));
        finish(context, printed, "TOP display box + post clamp (print)", C_PRINT);
        finish(context, qCreatedBy(t.faceId + "add", EntityType.BODY), "TOP face plate (print)", C_PRINT2);
    });
