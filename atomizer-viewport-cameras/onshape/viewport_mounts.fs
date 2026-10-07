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


// While DEBUG is true a failing feature keeps what it built and records the error and the last step it reached in
// the variables err_<unit> and step_<unit>, which can be read back over the API; with DEBUG false it fails normally.
const DEBUG = false;

function mark(context is Context, key is string, label is string)
{
    setVariable(context, "step_" ~ key, label);
}

function guard(context is Context, key is string, body is function)
{
    try
    {
        body();
    }
    catch (e)
    {
        setVariable(context, "err_" ~ key, toString(e));
        if (!DEBUG)
        {
            throw e;
        }
    }
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
    // Pi 5 standoffs (M2.5 heat-set inserts, 3.6 mm holes)
    const holes = pi5Holes();
    for (var i = 0; i < 4; i += 1)
    {
        const p = holes[i];
        zcyl(context, id + "tray" + "add" + ("so" ~ i), p[0] + d.pi_dx, p[1] + d.pi_dy, zIn - mmv(0.5), zIn + d.pi_standoff, mmv(3.5));
    }
    // two bars across the cavity under the display's top and bottom edges
    for (var i = 0; i < 2; i += 1)
    {
        const sy = (i == 0) ? 1 : -1;
        cbx(context, id + "tray" + "add" + ("ledge" ~ i), mmv(0), sy * (d.disp_h / 2 - mmv(2.5)), cw + mmv(1), mmv(5), zDisp - mmv(3), zDisp);
    }
    cbx(context, id + "tray" + "cut" + "cavity", mmv(0), mmv(0), cw, ch, zIn, zTop + mmv(1));
    for (var i = 0; i < 4; i += 1)
    {
        const p = holes[i];
        zcyl(context, id + "tray" + "cut" + ("soh" ~ i), p[0] + d.pi_dx, p[1] + d.pi_dy, zIn + mmv(1), zIn + d.pi_standoff + mmv(1), mmv(1.8));
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
    annotation { "Name" : "fp_x: front port centre x (at the chamber face)" }
    isLength(definition.fp_x, { (millimeter) : [-3000, -15, 3000] } as LengthBoundSpec);
    annotation { "Name" : "fp_z: front port centre height" }
    isLength(definition.fp_z, { (millimeter) : [0, 1035, 3000] } as LengthBoundSpec);
    annotation { "Name" : "fp_tilt: port axis above horizontal (looks down at the plate)" }
    isAngle(definition.fp_tilt, { (degree) : [-90, 20, 90] } as AngleBoundSpec);
    annotation { "Name" : "fp_yaw: port axis turned towards the left" }
    isAngle(definition.fp_yaw, { (degree) : [-90, 0, 90] } as AngleBoundSpec);
    annotation { "Name" : "fp_nut_d: threaded port nut OD" }
    isLength(definition.fp_nut_d, { (millimeter) : [10, 95, 400] } as LengthBoundSpec);
    annotation { "Name" : "fp_nut_face: nut front face out from the chamber face" }
    isLength(definition.fp_nut_face, { (millimeter) : [1, 45, 400] } as LengthBoundSpec);
    annotation { "Name" : "fp_glass_d: clear glass diameter" }
    isLength(definition.fp_glass_d, { (millimeter) : [5, 63, 300] } as LengthBoundSpec);
    annotation { "Name" : "fp_cover_sides: sides of AMAZEMET's LED cover" }
    isInteger(definition.fp_cover_sides, { (unitless) : [3, 12, 64] } as IntegerBoundSpec);
    annotation { "Name" : "fp_cover_rot: cover polygon rotation (a flat at this angle)" }
    isAngle(definition.fp_cover_rot, { (degree) : [-180, 0, 180] } as AngleBoundSpec);
    annotation { "Name" : "fp_cover_af: cover across flats" }
    isLength(definition.fp_cover_af, { (millimeter) : [10, 162, 400] } as LengthBoundSpec);
    annotation { "Name" : "fp_cover_face: cover front face out from the chamber face" }
    isLength(definition.fp_cover_face, { (millimeter) : [1, 75, 400] } as LengthBoundSpec);
    annotation { "Name" : "fp_cover_len: cover depth" }
    isLength(definition.fp_cover_len, { (millimeter) : [1, 50, 400] } as LengthBoundSpec);
    annotation { "Name" : "fp_cover_open: cover front opening diameter" }
    isLength(definition.fp_cover_open, { (millimeter) : [5, 75, 400] } as LengthBoundSpec);
    annotation { "Name" : "fp_pod_angle: LED cable pod position round the cover (270 = 6 o'clock)" }
    isAngle(definition.fp_pod_angle, { (degree) : [-360, 270, 360] } as AngleBoundSpec);
    annotation { "Name" : "fp_pod_w: pod width (along the cover's flat)" }
    isLength(definition.fp_pod_w, { (millimeter) : [1, 90, 400] } as LengthBoundSpec);
    annotation { "Name" : "fp_pod_h: pod height (radially out from the flat)" }
    isLength(definition.fp_pod_h, { (millimeter) : [1, 45, 400] } as LengthBoundSpec);
    annotation { "Name" : "fp_pod_depth: pod depth (along the port axis)" }
    isLength(definition.fp_pod_depth, { (millimeter) : [1, 55, 400] } as LengthBoundSpec);
    annotation { "Name" : "fp_pod_setback: pod front face behind the cover face" }
    isLength(definition.fp_pod_setback, { (millimeter) : [0, 5, 400] } as LengthBoundSpec);
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
    annotation { "Name" : "door_hinge_y: hinge axis y (back edge)" }
    isLength(definition.door_hinge_y, { (millimeter) : [-3000, 128, 3000] } as LengthBoundSpec);
    annotation { "Name" : "door_open: how far the door opens" }
    isAngle(definition.door_open, { (degree) : [0, 100, 180] } as AngleBoundSpec);
    annotation { "Name" : "lp_y: sight glass centre y" }
    isLength(definition.lp_y, { (millimeter) : [-3000, 20, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lp_z: sight glass centre height" }
    isLength(definition.lp_z, { (millimeter) : [0, 1015, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lp_ring_d: sight glass ring / nut OD" }
    isLength(definition.lp_ring_d, { (millimeter) : [5, 65, 300] } as LengthBoundSpec);
    annotation { "Name" : "lp_protrusion: ring out from the door" }
    isLength(definition.lp_protrusion, { (millimeter) : [1, 30, 300] } as LengthBoundSpec);
    annotation { "Name" : "lp_glass_d: clear glass diameter" }
    isLength(definition.lp_glass_d, { (millimeter) : [5, 45, 300] } as LengthBoundSpec);
    annotation { "Name" : "stack_angle: ultrasonic stack below horizontal" }
    isAngle(definition.stack_angle, { (degree) : [0, 40, 90] } as AngleBoundSpec);
    annotation { "Name" : "stack_z: stack axis at the door's outer face" }
    isLength(definition.stack_z, { (millimeter) : [0, 885, 3000] } as LengthBoundSpec);
    annotation { "Name" : "stack_d: stack (transducer housing) diameter" }
    isLength(definition.stack_d, { (millimeter) : [5, 60, 300] } as LengthBoundSpec);
}

predicate furnaceParams(definition is map)
{
    annotation { "Name" : "furn_r: furnace body radius" }
    isLength(definition.furn_r, { (millimeter) : [10, 135, 1000] } as LengthBoundSpec);
    annotation { "Name" : "furn_top_z: furnace body top (lid seat)" }
    isLength(definition.furn_top_z, { (millimeter) : [0, 1345, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lid_r: lid skirt radius" }
    isLength(definition.lid_r, { (millimeter) : [10, 137.5, 1000] } as LengthBoundSpec);
    annotation { "Name" : "lid_h1: lid round skirt height" }
    isLength(definition.lid_h1, { (millimeter) : [1, 80, 1000] } as LengthBoundSpec);
    annotation { "Name" : "lid_top_z: top of the lid" }
    isLength(definition.lid_top_z, { (millimeter) : [0, 1500, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lid_facet_angle: lid facets from horizontal" }
    isAngle(definition.lid_facet_angle, { (degree) : [5, 50, 85] } as AngleBoundSpec);
    annotation { "Name" : "lid_hinge_x: lid hinge axis x" }
    isLength(definition.lid_hinge_x, { (millimeter) : [-3000, -160, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lid_hinge_z: lid hinge axis height" }
    isLength(definition.lid_hinge_z, { (millimeter) : [0, 1345, 3000] } as LengthBoundSpec);
    annotation { "Name" : "lid_open: lid opening angle" }
    isAngle(definition.lid_open, { (degree) : [0, 105, 180] } as AngleBoundSpec);
    annotation { "Name" : "tw_x: lid window centre x" }
    isLength(definition.tw_x, { (millimeter) : [-1000, 0, 1000] } as LengthBoundSpec);
    annotation { "Name" : "tw_z: lid window centre height" }
    isLength(definition.tw_z, { (millimeter) : [0, 1455, 3000] } as LengthBoundSpec);
    annotation { "Name" : "tw_wid: window clear width (x)" }
    isLength(definition.tw_wid, { (millimeter) : [5, 60, 1000] } as LengthBoundSpec);
    annotation { "Name" : "tw_len: window clear length (along the slope)" }
    isLength(definition.tw_len, { (millimeter) : [5, 64, 1000] } as LengthBoundSpec);
    annotation { "Name" : "tw_plate_w: window frame plate width" }
    isLength(definition.tw_plate_w, { (millimeter) : [5, 112, 1000] } as LengthBoundSpec);
    annotation { "Name" : "tw_plate_l: window frame plate length (along the slope)" }
    isLength(definition.tw_plate_l, { (millimeter) : [5, 105, 1000] } as LengthBoundSpec);
    annotation { "Name" : "aim_z: height of the melt the top camera aims at, on the furnace axis" }
    isLength(definition.aim_z, { (millimeter) : [0, 1240, 3000] } as LengthBoundSpec);
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

// ------------------------------------------------------------------------------------------------ derived geometry
function portAxis(d is map) returns Vector
{
    return vector(-sin(d.fp_yaw) * cos(d.fp_tilt), -cos(d.fp_yaw) * cos(d.fp_tilt), sin(d.fp_tilt));
}

// front port frame: origin on the port axis at distance `out` from the chamber face, z outwards
function frontCS(d is map, out is ValueWithUnits) returns CoordSystem
{
    const n = portAxis(d);
    return coordSystem(vector(d.fp_x, d.ch_front_y, d.fp_z) + n * out, normalize(cross(vector(0, 0, 1), n)), n);
}

// left port frame: origin on the sight glass ring's outer face, z outwards (-x), x towards the operator (-y)
function leftCS(d is map) returns CoordSystem
{
    return coordSystem(vector(d.ch_left_x - d.door_t - d.lp_protrusion, d.lp_y, d.lp_z), vector(0, -1, 0), vector(-1, 0, 0));
}

function doorOpenT(d is map) returns Transform
{
    return rotationAround(line(vector(d.ch_left_x - d.door_t - mmv(4), d.door_hinge_y, mmv(0)), vector(0, 0, 1)), -d.door_open);
}

// lid: the hexagonal frustum's front facet. Returns its outward normal, the slope direction (up the facet) and
// the window centre.
function lidFacet(d is map) returns map
{
    const a = d.lid_facet_angle;
    const rb = d.lid_r * cos(30 * degree);                      // inscribed radius where the facets start
    const z1 = d.furn_top_z + d.lid_h1;
    const nrm = vector(0, -sin(a), cos(a));
    const up = vector(0, cos(a), sin(a));
    const s = (d.tw_z - z1) / sin(a);                           // distance up the slope to the window centre
    const w = vector(d.tw_x, -rb, z1) + up * s;
    return { "normal" : nrm, "up" : up, "window" : w, "rb" : rb, "z1" : z1 };
}

// ------------------------------------------------------------------------------------------------ machine context
annotation { "Feature Type Name" : "rePowder context (approximate)",
        "Feature Type Description" : "The parts of the rePowder round the three viewing windows, from the training videos and AMAZEMET's documents; every size is a variable to measure" }
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
        annotation { "Name" : "Show the door open", "Default" : false }
        definition.showOpenDoor is boolean;
    }
    {
        guard(context, "context", function()
            {
                const d = definition;
                const backY = -d.ch_front_y;
                mark(context, "context", "chamber");
                bx(context, id + "ch" + "flat", d.ch_left_x, d.ch_right_x, d.ch_front_y, backY, d.ch_vert_z, d.ch_top_z);
                zcyl(context, id + "ch" + "round", d.ch_right_x, mmv(0), d.ch_vert_z, d.ch_top_z, backY);
                bx(context, id + "ch" + "plate", d.ch_left_x - mmv(40), d.ch_right_x, d.ch_front_y, backY, d.ch_top_z, d.ch_top_z + mmv(20));
                zcyl(context, id + "ch" + "plateR", d.ch_right_x, mmv(0), d.ch_top_z, d.ch_top_z + mmv(20), backY);
                unite(context, id + "chU", qCreatedBy(id + "ch", EntityType.BODY));
                finish(context, qCreatedBy(id + "ch", EntityType.BODY), "(machine) atomization chamber", C_STEEL);

                mark(context, "context", "front port");
                // port stub and threaded nut, glass at the nut's face; AMAZEMET's LED cover over the nut; its cable pod
                const ra = d.fp_cover_af / 2;
                zcyl(context, id + "fp" + "nut", mmv(0), mmv(0), mmv(-10), d.fp_nut_face, d.fp_nut_d / 2);
                zcyl(context, id + "fp" + "glass", mmv(0), mmv(0), d.fp_nut_face - mmv(12), d.fp_nut_face - mmv(4), d.fp_glass_d / 2);
                ngonPrism(context, id + "fp" + "cover", mmv(0), mmv(0), d.fp_cover_sides, d.fp_cover_af, d.fp_cover_rot,
                    d.fp_cover_face - d.fp_cover_len, d.fp_cover_face);
                bx(context, id + "fp" + "pod", -d.fp_pod_w / 2, d.fp_pod_w / 2, ra - mmv(2), ra + d.fp_pod_h,
                    d.fp_cover_face - d.fp_pod_setback - d.fp_pod_depth, d.fp_cover_face - d.fp_pod_setback);
                zcyl(context, id + "fpcut" + "nutbore", mmv(0), mmv(0), d.fp_nut_face - mmv(4), d.fp_nut_face + mmv(1), d.fp_glass_d / 2);
                zcyl(context, id + "fpcut2" + "open", mmv(0), mmv(0), d.fp_cover_face - d.fp_cover_len - mmv(1), d.fp_cover_face + mmv(1), d.fp_cover_open / 2);
                zcyl(context, id + "fpcut2" + "overNut", mmv(0), mmv(0), d.fp_cover_face - d.fp_cover_len - mmv(1), d.fp_nut_face, d.fp_nut_d / 2 + mmv(0.5));
                subtract(context, id + "fpNutS", qCreatedBy(id + "fp" + "nut", EntityType.BODY), qCreatedBy(id + "fpcut", EntityType.BODY));
                subtract(context, id + "fpCovS", qCreatedBy(id + "fp" + "cover", EntityType.BODY), qCreatedBy(id + "fpcut2", EntityType.BODY));
                place(context, id + "fpPodRot", qCreatedBy(id + "fp" + "pod", EntityType.BODY),
                    rotationAround(line(vector(mmv(0), mmv(0), mmv(0)), vector(0, 0, 1)), d.fp_pod_angle - 90 * degree));
                finish(context, qCreatedBy(id + "fp" + "nut", EntityType.BODY), "(machine) front port nut", C_STEEL);
                finish(context, qCreatedBy(id + "fp" + "glass", EntityType.BODY), "(machine) front port glass", C_GLASS);
                finish(context, qUnion([qCreatedBy(id + "fp" + "cover", EntityType.BODY), qCreatedBy(id + "fp" + "pod", EntityType.BODY)]),
                    "(machine) AMAZEMET LED cover and cable pod", C_DARK);
                place(context, id + "fpPlace", qCreatedBy(id + "fp", EntityType.BODY), toWorld(frontCS(d, mmv(0))));

                mark(context, "context", "door");
                // left door (hinged at its back edge), its sight glass, and the ultrasonic stack leaving it
                const xo = d.ch_left_x - d.door_t;
                bx(context, id + "door" + "plate", xo, d.ch_left_x, -d.door_w / 2, d.door_w / 2, d.door_z0, d.door_z1);
                cyl(context, id + "door" + "ring", vector(xo + mmv(1), d.lp_y, d.lp_z), vector(xo - d.lp_protrusion, d.lp_y, d.lp_z), d.lp_ring_d / 2);
                cyl(context, id + "door" + "glass", vector(xo - d.lp_protrusion + mmv(3), d.lp_y, d.lp_z), vector(xo - d.lp_protrusion + mmv(8), d.lp_y, d.lp_z), d.lp_glass_d / 2);
                const sOut = vector(-cos(d.stack_angle), 0, -sin(d.stack_angle));
                const s0 = vector(xo, mmv(0), d.stack_z);
                cyl(context, id + "door" + "stack", s0, s0 + sOut * mmv(260), d.stack_d / 2);
                cyl(context, id + "doorcut" + "glass", vector(xo - d.lp_protrusion - mmv(1), d.lp_y, d.lp_z), vector(xo - d.lp_protrusion + mmv(3), d.lp_y, d.lp_z), d.lp_glass_d / 2);
                subtract(context, id + "doorS", qCreatedBy(id + "door" + "ring", EntityType.BODY), qCreatedBy(id + "doorcut", EntityType.BODY));
                finish(context, qCreatedBy(id + "door" + "plate", EntityType.BODY), "(machine) chamber door", C_STEEL);
                finish(context, qCreatedBy(id + "door" + "ring", EntityType.BODY), "(machine) door sight glass ring", C_STEEL);
                finish(context, qCreatedBy(id + "door" + "glass", EntityType.BODY), "(machine) door sight glass", C_GLASS);
                finish(context, qCreatedBy(id + "door" + "stack", EntityType.BODY), "(machine) ultrasonic stack (outside the door)", C_STEEL);
                if (d.showOpenDoor)
                {
                    place(context, id + "doorOpen", qCreatedBy(id + "door", EntityType.BODY), doorOpenT(d));
                }

                mark(context, "context", "furnace and lid");
                zcyl(context, id + "furn", mmv(0), mmv(0), d.ch_top_z + mmv(20), d.furn_top_z, d.furn_r);
                finish(context, qCreatedBy(id + "furn", EntityType.BODY), "(machine) furnace body", C_STEEL);
                buildLid(context, id + "lid", d, "(machine) furnace lid", "(machine) lid window", C_STEEL, C_GLASS);
                if (d.showOpenLid)
                {
                    buildLid(context, id + "lidOpen", d, "(machine) furnace lid, open", "(machine) lid window, open", C_GHOST, C_GHOST);
                    place(context, id + "lidOpenRot", qCreatedBy(id + "lidOpen", EntityType.BODY),
                        rotationAround(line(vector(d.lid_hinge_x, mmv(0), d.lid_hinge_z), vector(0, 1, 0)), -d.lid_open));
                }

                mark(context, "context", "frame");
                bx(context, id + "frame", d.fr_x0, d.fr_x1, d.fr_front_y, d.fr_front_y + mmv(500), mmv(175), d.fr_top_z);
                finish(context, qCreatedBy(id + "frame", EntityType.BODY), "(machine) blue frame", C_BLUE);
            });
    });

function buildLid(context is Context, id is Id, d is map, name is string, windowName is string, rgb is array, glassRgb is array)
{
    const f = lidFacet(d);
    const z0 = d.furn_top_z;
    const z1 = f.z1;
    // round skirt, then a hexagonal prism cut down to a frustum by six planes at the facet angle
    zcyl(context, id + "body" + "skirt", mmv(0), mmv(0), z0, z1, d.lid_r);
    ngonPrism(context, id + "body" + "hex", mmv(0), mmv(0), 6, 2 * f.rb, 30 * degree, z1 - mmv(0.01), d.lid_top_z);
    for (var i = 0; i < 6; i += 1)
    {
        bx(context, id + "cut" + ("f" ~ i), mmv(-500), mmv(500), mmv(-500), mmv(500), mmv(0), mmv(500));
    }
    for (var i = 0; i < 6; i += 1)
    {
        const phi = (30 + 60 * i) * degree;
        const u = vector(cos(phi), sin(phi), 0);
        const t = vector(-sin(phi), cos(phi), 0);
        const nrm = u * sin(d.lid_facet_angle) + vector(0, 0, 1) * cos(d.lid_facet_angle);
        place(context, id + "cutPlace" + ("f" ~ i), qCreatedBy(id + "cut" + ("f" ~ i), EntityType.BODY),
            toWorld(coordSystem(u * f.rb + vector(mmv(0), mmv(0), z1), t, nrm)));
    }
    subtract(context, id + "hexS", qCreatedBy(id + "body" + "hex", EntityType.BODY), qCreatedBy(id + "cut", EntityType.BODY));
    unite(context, id + "bodyU", qCreatedBy(id + "body", EntityType.BODY));
    // window frame plate, 4 mm proud of the front facet, glass 4 mm below the plate's face
    const wcs = coordSystem(f.window, vector(1, 0, 0), f.normal);
    cbx(context, id + "plate", mmv(0), mmv(0), d.tw_plate_w, d.tw_plate_l, mmv(-1), mmv(4));
    rrectPrism(context, id + "plateCut", mmv(0), mmv(0), d.tw_wid, d.tw_len, mmv(5), mmv(-2), mmv(5));
    subtract(context, id + "plateS", qCreatedBy(id + "plate", EntityType.BODY), qCreatedBy(id + "plateCut", EntityType.BODY));
    rrectPrism(context, id + "win", mmv(0), mmv(0), d.tw_wid, d.tw_len, mmv(5), mmv(-1), mmv(0));
    place(context, id + "plWin", qUnion([qCreatedBy(id + "plate", EntityType.BODY), qCreatedBy(id + "win", EntityType.BODY)]), toWorld(wcs));
    finish(context, qUnion([qCreatedBy(id + "body", EntityType.BODY), qCreatedBy(id + "plate", EntityType.BODY)]), name, rgb);
    finish(context, qCreatedBy(id + "win", EntityType.BODY), windowName, glassRgb);
}

// ------------------------------------------------------------------------------------------------ front port unit
annotation { "Feature Type Name" : "Front port viewfinder (HQ + wide)",
        "Feature Type Description" : "HQ Camera and Camera Module 3 Wide side by side at AMAZEMET's LED cover, looking through its opening at the plate, a Pi 5 and an HDMI display; a 12-sided socket pushes onto the cover's rim, keyed by its cable pod, with a ball-plunger detent" }
export const frontViewfinder = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        chamberParams(definition);
        frontPortParams(definition);
        trayParams(definition);
        annotation { "Name" : "Socket length over the cover's rim" }
        isLength(definition.sock_len, { (millimeter) : [2, 15, 200] } as LengthBoundSpec);
        annotation { "Name" : "Socket wall" }
        isLength(definition.sock_wall, { (millimeter) : [1, 3, 20] } as LengthBoundSpec);
        annotation { "Name" : "Socket lid thickness (outside the tray)" }
        isLength(definition.sock_lid_t, { (millimeter) : [0.8, 1.6, 10] } as LengthBoundSpec);
        annotation { "Name" : "Notch for the cable pod (0 = none)" }
        isLength(definition.notch_w, { (millimeter) : [0, 94, 300] } as LengthBoundSpec);
        annotation { "Name" : "Ball plunger position round the socket" }
        isAngle(definition.plunger_angle, { (degree) : [-360, 0, 360] } as AngleBoundSpec);
        annotation { "Name" : "Ball plunger thread tap drill" }
        isLength(definition.plunger_tap, { (millimeter) : [1, 5, 20] } as LengthBoundSpec);
        annotation { "Name" : "Camera boards above the cover face" }
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
    }
    {
        guard(context, "front", function()
            {
                const d = definition;
                const n = d.fp_cover_sides;
                const afIn = d.fp_cover_af + 2 * d.fit;
                const afOut = afIn + 2 * d.sock_wall;
                const zb = d.cam_gap + mmv(1.4) + mmv(4);            // tray back plate: HQ board, then 4 mm bosses
                const rcIn = afIn / 2 / cos(180 / n * degree);

                mark(context, "front", "socket");
                // socket over the cover's rim, closed by a thin lid at the tray's back plate
                const zp = -d.sock_len / 2;
                ngonPrism(context, id + "sock" + "add" + "outer", mmv(0), mmv(0), n, afOut, d.fp_cover_rot, -d.sock_len, zb + d.sock_lid_t);
                // ball plunger: radial boss on a flat, pointing at the cover
                cyl(context, id + "sock" + "add" + "plboss", vector(afIn / 2, mmv(0), zp), vector(afOut / 2 + mmv(8), mmv(0), zp), mmv(6));
                ngonPrism(context, id + "sock" + "cut" + "inner", mmv(0), mmv(0), n, afIn, d.fp_cover_rot, -d.sock_len - mmv(1), zb);
                cyl(context, id + "sock" + "cut" + "plhole", vector(afIn / 2 - mmv(1), mmv(0), zp), vector(afOut / 2 + mmv(9), mmv(0), zp), d.plunger_tap / 2);
                if (d.notch_w > mmv(0))
                {
                    bx(context, id + "sock" + "cut" + "notch", -d.notch_w / 2, d.notch_w / 2, afIn / 2 - mmv(5), afOut, -d.sock_len - mmv(1), mmv(-0.01));
                    place(context, id + "sock" + "cut" + "notchRot", qCreatedBy(id + "sock" + "cut" + "notch", EntityType.BODY),
                        rotationAround(line(vector(mmv(0), mmv(0), mmv(0)), vector(0, 0, 1)), d.fp_pod_angle - 90 * degree));
                }
                place(context, id + "sock" + "plRot", qUnion([qCreatedBy(id + "sock" + "add" + "plboss", EntityType.BODY), qCreatedBy(id + "sock" + "cut" + "plhole", EntityType.BODY)]),
                    rotationAround(line(vector(mmv(0), mmv(0), mmv(0)), vector(0, 0, 1)), d.plunger_angle));
                unite(context, id + "sock" + "u", qCreatedBy(id + "sock" + "add", EntityType.BODY));
                subtract(context, id + "sock" + "s", qCreatedBy(id + "sock" + "add", EntityType.BODY), qCreatedBy(id + "sock" + "cut", EntityType.BODY));

                mark(context, "front", "tray");
                const t = viewfinderTray(context, id + "vf", d, zb, "front", "5 in HDMI display");

                mark(context, "front", "cameras");
                hqCamera(context, id + "hq", d.lens_d, d.lens_len, d.lens_start, d.hq_m12);
                place(context, id + "hqPlace", qCreatedBy(id + "hq", EntityType.BODY), transform(vector(d.hq_x, d.hq_y, d.cam_gap)));
                cm3Camera(context, id + "cm", true);
                place(context, id + "cmPlace", qCreatedBy(id + "cm", EntityType.BODY), transform(vector(d.cm_x, d.cm_y, d.cam_gap)));
                for (var i = 0; i < 4; i += 1)
                {
                    const sx = (i % 2 == 0) ? 1 : -1;
                    const sy = (i < 2) ? 1 : -1;
                    const cy = (i < 2) ? mmv(0.1) : mmv(-12.4);
                    zcyl(context, id + "boss" + "add" + ("hq" ~ i), d.hq_x + sx * mmv(15), d.hq_y + sy * mmv(15), d.cam_gap + mmv(1.4), zb + mmv(0.5), mmv(2.75));
                    zcyl(context, id + "boss" + "add" + ("cm" ~ i), d.cm_x + sx * mmv(10.5), d.cm_y + cy, d.cam_gap + mmv(1.12), zb + mmv(0.5), mmv(2.25));
                }
                for (var i = 0; i < 4; i += 1)
                {
                    const sx = (i % 2 == 0) ? 1 : -1;
                    const sy = (i < 2) ? 1 : -1;
                    const cy = (i < 2) ? mmv(0.1) : mmv(-12.4);
                    zcyl(context, id + "boss" + "cut" + ("hqh" ~ i), d.hq_x + sx * mmv(15), d.hq_y + sy * mmv(15), d.cam_gap + mmv(1), zb + d.plate_t + mmv(1), mmv(1.4));
                    zcyl(context, id + "boss" + "cut" + ("cmh" ~ i), d.cm_x + sx * mmv(10.5), d.cm_y + cy, d.cam_gap + mmv(0.8), zb + d.plate_t + mmv(1), mmv(1.2));
                }
                cbx(context, id + "boss" + "cut" + "slotHQ", d.hq_x, d.hq_y + mmv(23), mmv(18), mmv(3), zb - mmv(1), zb + d.plate_t + mmv(1));
                cbx(context, id + "boss" + "cut" + "slotCM", d.cm_x, d.cm_y + mmv(13.5), mmv(18), mmv(3), zb - mmv(1), zb + d.plate_t + mmv(1));
                const printed = qUnion([qCreatedBy(id + "sock" + "add", EntityType.BODY), qCreatedBy(t.trayId + "add", EntityType.BODY),
                            qCreatedBy(id + "boss" + "add", EntityType.BODY)]);
                unite(context, id + "join", printed);
                subtract(context, id + "joinS", printed, qCreatedBy(id + "boss" + "cut", EntityType.BODY));
                finish(context, printed, "FRONT socket + tray (print)", C_PRINT);
                finish(context, qCreatedBy(t.faceId + "add", EntityType.BODY), "FRONT face plate (print)", C_PRINT2);

                place(context, id + "place", qCreatedBy(id, EntityType.BODY), toWorld(frontCS(d, d.fp_cover_face)));
            });
    });

// ------------------------------------------------------------------------------------------------ left port unit
annotation { "Feature Type Name" : "Left port viewfinder",
        "Feature Type Description" : "A Camera Module 3 on the axis of the door's sight glass, a Pi 5 and a DSI display, on a clamp collar round the sight glass ring; rides on the door" }
export const leftViewfinder = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        chamberParams(definition);
        leftPortParams(definition);
        trayParams(definition);
        annotation { "Name" : "Collar length over the ring" }
        isLength(definition.col_len, { (millimeter) : [2, 20, 200] } as LengthBoundSpec);
        annotation { "Name" : "Collar wall" }
        isLength(definition.col_wall, { (millimeter) : [1, 4, 20] } as LengthBoundSpec);
        annotation { "Name" : "Camera board above the ring face" }
        isLength(definition.cam_gap, { (millimeter) : [0, 1, 100] } as LengthBoundSpec);
        annotation { "Name" : "Camera Module 3 Wide (else standard)", "Default" : false }
        definition.wide is boolean;
        annotation { "Name" : "Show it on the open door", "Default" : false }
        definition.showOpenDoor is boolean;
    }
    {
        guard(context, "left", function()
            {
                const d = definition;
                const rIn = d.lp_ring_d / 2 + d.fit;
                const rOut = rIn + d.col_wall;
                const zb = d.cam_gap + mmv(1.12) + mmv(4);

                mark(context, "left", "collar");
                // clamp collar round the ring, split at the bottom, M4 clamp screw across the split
                zcyl(context, id + "col" + "add" + "tube", mmv(0), mmv(0), -d.col_len, zb, rOut);
                bx(context, id + "col" + "add" + "lugs", mmv(-8), mmv(8), -rOut - mmv(9), -rIn, -d.col_len, mmv(0));
                zcyl(context, id + "col" + "cut" + "bore", mmv(0), mmv(0), -d.col_len - mmv(1), zb, rIn);
                bx(context, id + "col" + "cut" + "split", mmv(-1), mmv(1), -rOut - mmv(10), -rIn + mmv(0.5), -d.col_len - mmv(1), mmv(-0.5));
                cyl(context, id + "col" + "cut" + "screw", vector(mmv(-9), -rOut - mmv(4.5), -d.col_len / 2), vector(mmv(9), -rOut - mmv(4.5), -d.col_len / 2), mmv(2.2));
                unite(context, id + "col" + "u", qCreatedBy(id + "col" + "add", EntityType.BODY));
                subtract(context, id + "col" + "s", qCreatedBy(id + "col" + "add", EntityType.BODY), qCreatedBy(id + "col" + "cut", EntityType.BODY));

                mark(context, "left", "tray");
                const t = viewfinderTray(context, id + "vf", d, zb, "left", "DSI display");

                mark(context, "left", "camera");
                cm3Camera(context, id + "cm", d.wide);
                place(context, id + "cmPlace", qCreatedBy(id + "cm", EntityType.BODY), transform(vector(mmv(0), mmv(0), d.cam_gap)));
                for (var i = 0; i < 4; i += 1)
                {
                    const sx = (i % 2 == 0) ? 1 : -1;
                    const cy = (i < 2) ? mmv(0.1) : mmv(-12.4);
                    zcyl(context, id + "boss" + "add" + ("cm" ~ i), sx * mmv(10.5), cy, d.cam_gap + mmv(1.12), zb + mmv(0.5), mmv(2.25));
                }
                for (var i = 0; i < 4; i += 1)
                {
                    const sx = (i % 2 == 0) ? 1 : -1;
                    const cy = (i < 2) ? mmv(0.1) : mmv(-12.4);
                    zcyl(context, id + "boss" + "cut" + ("cmh" ~ i), sx * mmv(10.5), cy, d.cam_gap + mmv(0.8), zb + d.plate_t + mmv(1), mmv(1.2));
                }
                cbx(context, id + "boss" + "cut" + "slotCM", mmv(0), mmv(13.5), mmv(18), mmv(3), zb - mmv(1), zb + d.plate_t + mmv(1));
                const printed = qUnion([qCreatedBy(id + "col" + "add", EntityType.BODY), qCreatedBy(t.trayId + "add", EntityType.BODY),
                            qCreatedBy(id + "boss" + "add", EntityType.BODY)]);
                unite(context, id + "join", printed);
                subtract(context, id + "joinS", printed, qCreatedBy(id + "boss" + "cut", EntityType.BODY));
                finish(context, printed, "LEFT collar + tray (print)", C_PRINT);
                finish(context, qCreatedBy(t.faceId + "add", EntityType.BODY), "LEFT face plate (print)", C_PRINT2);

                const toDoor = d.showOpenDoor ? doorOpenT(d) : identityTransform();
                place(context, id + "place", qCreatedBy(id, EntityType.BODY), toDoor * toWorld(leftCS(d)));
            });
    });

// ------------------------------------------------------------------------------------------------ top window unit
annotation { "Feature Type Name" : "Top window camera (swing arm)",
        "Feature Type Description" : "An HQ Camera looking through the furnace lid's window at the melt, at the end of a 2020 extrusion arm that swings about a post on a magnetic base and clicks into place on a ball-plunger detent; the Pi 5 and a small DSI display sit on the arm above the camera" }
export const topWindowCamera = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        furnaceParams(definition);
        frameParams(definition);
        trayParams(definition);
        annotation { "Name" : "Lens front to the window centre" }
        isLength(definition.cam_dist, { (millimeter) : [20, 250, 2000] } as LengthBoundSpec);
        annotation { "Name" : "Post x" }
        isLength(definition.post_x, { (millimeter) : [-3000, -90, 3000] } as LengthBoundSpec);
        annotation { "Name" : "Post y, from the frame's front face" }
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
        annotation { "Name" : "Arm above the camera board's centre" }
        isLength(definition.hang, { (millimeter) : [10, 45, 500] } as LengthBoundSpec);
        annotation { "Name" : "Arm overhang past the camera" }
        isLength(definition.overhang, { (millimeter) : [0, 60, 500] } as LengthBoundSpec);
        annotation { "Name" : "Detent radius (plunger from the post axis)" }
        isLength(definition.det_r, { (millimeter) : [5, 20, 100] } as LengthBoundSpec);
        annotation { "Name" : "Parked angle (arm swung clear)" }
        isAngle(definition.park, { (degree) : [-180, 90, 180] } as AngleBoundSpec);
        annotation { "Name" : "Show the arm parked", "Default" : false }
        definition.showParked is boolean;
        annotation { "Name" : "Display tilt (down from vertical)" }
        isAngle(definition.disp_tilt, { (degree) : [0, 30, 80] } as AngleBoundSpec);
        annotation { "Name" : "Ball plunger thread tap drill" }
        isLength(definition.plunger_tap, { (millimeter) : [1, 5, 20] } as LengthBoundSpec);
    }
    {
        guard(context, "top", function()
            {
                const d = definition;
                const f = lidFacet(d);
                const w = f.window;
                const u = normalize(w - vector(mmv(0), mmv(0), d.aim_z));          // out of the window, away from the melt
                const lensFront = w + u * d.cam_dist;
                const board = lensFront + u * (d.lens_start + d.lens_len);          // HQ board, lens side, centre
                const xCam = normalize(cross(vector(0, 0, 1), u));
                const camCS = coordSystem(board, xCam, u);
                const px = d.post_x;
                const py = d.fr_front_y + d.post_dy;
                const zArm = board[2] + d.hang;                                      // underside of the extrusion
                const dx = board[0] - px;
                const dy = board[1] - py;
                const reach = sqrt(dx * dx + dy * dy);
                const heading = atan2(dy, dx);
                const armLen = reach + d.overhang;
                const rp = d.post_d / 2;
                const origin = vector(mmv(0), mmv(0), mmv(0));
                const armT = transform(vector(px, py, zArm)) * rotationAround(line(origin, vector(0, 0, 1)), heading);
                const hubR = d.det_r + mmv(7);

                mark(context, "top", "post and base");
                cbx(context, id + "mag", px, py, mmv(50), mmv(58), d.fr_top_z, d.fr_top_z + d.base_h);
                finish(context, qCreatedBy(id + "mag", EntityType.BODY), "(bought) switchable magnetic base", C_DARK);
                zcyl(context, id + "post", px, py, d.fr_top_z + d.base_h, zArm + mmv(70), rp);
                finish(context, qCreatedBy(id + "post", EntityType.BODY), "(bought) post rod", C_STEEL);

                // in the arm's frame: post axis at the origin, x towards the camera, z = 0 at the extrusion's underside
                mark(context, "top", "detent collar");
                zcyl(context, id + "dcol" + "add" + "ring", mmv(0), mmv(0), mmv(-20), mmv(-4.3), hubR);
                bx(context, id + "dcol" + "add" + "lug", -hubR - mmv(10), -hubR + mmv(3), mmv(-6), mmv(6), mmv(-20), mmv(-10));
                zcyl(context, id + "dcol" + "cut" + "bore", mmv(0), mmv(0), mmv(-21), mmv(-3), rp + mmv(0.15));
                bx(context, id + "dcol" + "cut" + "split", -hubR - mmv(11), -rp + mmv(1), mmv(-0.8), mmv(0.8), mmv(-21), mmv(-3));
                cyl(context, id + "dcol" + "cut" + "screw", vector(-hubR - mmv(3.5), mmv(-7), mmv(-15)), vector(-hubR - mmv(3.5), mmv(7), mmv(-15)), mmv(2.2));
                const dims = [0 * degree, d.park];
                for (var i = 0; i < 2; i += 1)
                {
                    const a = dims[i];
                    fCone(context, id + "dcol" + "cut" + ("dimple" ~ i), { "bottomCenter" : vector(d.det_r * cos(a), d.det_r * sin(a), mmv(-6.9)),
                                "topCenter" : vector(d.det_r * cos(a), d.det_r * sin(a), mmv(-3.8)), "bottomRadius" : mmv(0.3), "topRadius" : mmv(3.0) });
                }
                unite(context, id + "dcol" + "u", qCreatedBy(id + "dcol" + "add", EntityType.BODY));
                subtract(context, id + "dcol" + "s", qCreatedBy(id + "dcol" + "add", EntityType.BODY), qCreatedBy(id + "dcol" + "cut", EntityType.BODY));
                finish(context, qCreatedBy(id + "dcol" + "add", EntityType.BODY), "TOP detent collar (print)", C_PRINT2);
                place(context, id + "dcolPlace", qCreatedBy(id + "dcol", EntityType.BODY), armT);

                mark(context, "top", "hub and arm");
                // hub: rides on the collar, ball plunger down into the dimples, socket for the extrusion's end
                zcyl(context, id + "hub" + "add" + "ring", mmv(0), mmv(0), mmv(-4), mmv(26), hubR);
                bx(context, id + "hub" + "add" + "sock", mmv(0), hubR + mmv(28), mmv(-14), mmv(14), mmv(-4), mmv(24));
                zcyl(context, id + "hub" + "cut" + "bore", mmv(0), mmv(0), mmv(-5), mmv(27), rp + mmv(0.25));
                zcyl(context, id + "hub" + "cut" + "plunger", d.det_r, mmv(0), mmv(-5), mmv(27), d.plunger_tap / 2);
                bx(context, id + "hub" + "cut" + "ext", hubR - mmv(2), hubR + mmv(29), mmv(-10.2), mmv(10.2), mmv(-0.2), mmv(20.2));
                cyl(context, id + "hub" + "cut" + "m5", vector(hubR + mmv(14), mmv(0), mmv(-5)), vector(hubR + mmv(14), mmv(0), mmv(25)), mmv(2.7));
                unite(context, id + "hub" + "u", qCreatedBy(id + "hub" + "add", EntityType.BODY));
                subtract(context, id + "hub" + "s", qCreatedBy(id + "hub" + "add", EntityType.BODY), qCreatedBy(id + "hub" + "cut", EntityType.BODY));
                finish(context, qCreatedBy(id + "hub" + "add", EntityType.BODY), "TOP hub (print)", C_PRINT);
                // 2020 extrusion
                bx(context, id + "ext", hubR, armLen, mmv(-10), mmv(10), mmv(0), mmv(20));
                finish(context, qCreatedBy(id + "ext", EntityType.BODY), "(bought) 2020 extrusion arm", C_STEEL);
                const armQ = qUnion([qCreatedBy(id + "hub", EntityType.BODY), qCreatedBy(id + "ext", EntityType.BODY)]);
                place(context, id + "armPlace", armQ, armT);

                mark(context, "top", "camera pod");
                // camera plate behind the HQ board (in the camera's frame), hung from a clamp on the extrusion
                hqCamera(context, id + "hq", d.lens_d, d.lens_len, d.lens_start, false);
                cbx(context, id + "pod" + "add" + "plate", mmv(0), mmv(0), mmv(46), mmv(46), mmv(5.4), mmv(9.4));
                for (var i = 0; i < 4; i += 1)
                {
                    const sx = (i % 2 == 0) ? 1 : -1;
                    const sy = (i < 2) ? 1 : -1;
                    zcyl(context, id + "pod" + "add" + ("boss" ~ i), sx * mmv(15), sy * mmv(15), mmv(1.4), mmv(5.9), mmv(2.75));
                }
                for (var i = 0; i < 4; i += 1)
                {
                    const sx = (i % 2 == 0) ? 1 : -1;
                    const sy = (i < 2) ? 1 : -1;
                    zcyl(context, id + "pod" + "cut" + ("bh" ~ i), sx * mmv(15), sy * mmv(15), mmv(1), mmv(10), mmv(1.4));
                }
                cbx(context, id + "pod" + "cut" + "ribbon", mmv(0), mmv(23), mmv(18), mmv(3), mmv(5), mmv(10));
                place(context, id + "podCam", qUnion([qCreatedBy(id + "pod", EntityType.BODY), qCreatedBy(id + "hq", EntityType.BODY)]), toWorld(camCS));
                // hanger: from the plate up to a saddle round the extrusion, in world coordinates
                const top = board + u * mmv(9.4);
                bx(context, id + "hanger", top[0] - mmv(12), top[0] + mmv(12), top[1] - mmv(5), top[1] + mmv(5), top[2] - mmv(2), zArm + mmv(26));
                place(context, id + "hangerRot", qCreatedBy(id + "hanger", EntityType.BODY),
                    rotationAround(line(top, vector(0, 0, 1)), heading - 90 * degree));
                const sad = transform(vector(px, py, zArm)) * rotationAround(line(origin, vector(0, 0, 1)), heading);
                bx(context, id + "podSad" + "add", reach - mmv(14), reach + mmv(14), mmv(-14), mmv(14), mmv(-4), mmv(24));
                bx(context, id + "podSad" + "cut", reach - mmv(15), reach + mmv(15), mmv(-10.2), mmv(10.2), mmv(-0.2), mmv(20.2));
                place(context, id + "podSadPlace", qCreatedBy(id + "podSad", EntityType.BODY), sad);
                const podQ = qUnion([qCreatedBy(id + "pod" + "add", EntityType.BODY), qCreatedBy(id + "hanger", EntityType.BODY), qCreatedBy(id + "podSad" + "add", EntityType.BODY)]);
                unite(context, id + "podU", podQ);
                subtract(context, id + "podS", podQ, qUnion([qCreatedBy(id + "pod" + "cut", EntityType.BODY), qCreatedBy(id + "podSad" + "cut", EntityType.BODY)]));
                finish(context, podQ, "TOP camera pod (print)", C_PRINT);

                mark(context, "top", "display box");
                // display box on the extrusion's tip, facing along the arm (the operator), tilted down; the extrusion
                // plugs into a socket on its back
                const dir = vector(cos(heading), sin(heading), 0);
                const t = viewfinderTray(context, id + "vf", d, mmv(0), "top", "small DSI display");
                const nOut = dir * cos(d.disp_tilt) + vector(0, 0, -1) * sin(d.disp_tilt);
                const yUp = dir * sin(d.disp_tilt) + vector(0, 0, 1) * cos(d.disp_tilt);
                const tip = vector(px, py, zArm + mmv(10)) + dir * armLen;
                place(context, id + "boxPlace", qCreatedBy(id + "vf", EntityType.BODY), toWorld(coordSystem(tip + dir * mmv(6), cross(yUp, nOut), nOut)));
                bx(context, id + "tipSock" + "add", armLen - mmv(30), armLen + mmv(8), mmv(-14), mmv(14), mmv(-4), mmv(24));
                bx(context, id + "tipSock" + "cut", armLen - mmv(31), armLen + mmv(0.2), mmv(-10.2), mmv(10.2), mmv(-0.2), mmv(20.2));
                place(context, id + "tipSockPlace", qCreatedBy(id + "tipSock", EntityType.BODY), armT);
                const boxQ = qUnion([qCreatedBy(t.trayId + "add", EntityType.BODY), qCreatedBy(id + "tipSock" + "add", EntityType.BODY)]);
                unite(context, id + "boxU", boxQ);
                subtract(context, id + "boxS", boxQ, qCreatedBy(id + "tipSock" + "cut", EntityType.BODY));
                finish(context, boxQ, "TOP display box (print)", C_PRINT);
                finish(context, qCreatedBy(t.faceId + "add", EntityType.BODY), "TOP face plate (print)", C_PRINT2);

                if (d.showParked)
                {
                    const all = qUnion([armQ, qCreatedBy(id + "pod", EntityType.BODY), qCreatedBy(id + "hanger", EntityType.BODY), qCreatedBy(id + "podSad", EntityType.BODY),
                                qCreatedBy(id + "hq", EntityType.BODY), qCreatedBy(id + "vf", EntityType.BODY), qCreatedBy(id + "tipSock", EntityType.BODY)]);
                    place(context, id + "park", all, rotationAround(line(vector(px, py, mmv(0)), vector(0, 0, 1)), d.park));
                }
            });
    });
