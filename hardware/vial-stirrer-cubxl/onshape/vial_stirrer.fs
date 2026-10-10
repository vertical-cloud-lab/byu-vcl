FeatureScript 3095;
import(path : "onshape/std/common.fs", version : "3095.0");

// Single-vial magnetic stirrer for the CubXL deck, after the Pioreactor's
// stirring stack (fan + two magnets on the hub, stir bar in the vial).
// vertical-cloud-lab/byu-vcl, PR #269 / issue #169. All lengths in mm.
// z = 0 is the top face of the CubXL deck plate.

// ---- vial (Ben's 20 mL vials: 28 mm OD in ben_2vials_tiprack.yaml) --------
const VIAL_OD = 28.0;
const VIAL_H = 57.0;
const VIAL_WALL = 1.3;
const VIAL_BOT = 1.6;
const NECK_OD = 24.0;
const FILL_H = 19.4;          // ~10 mL in a 25.4 mm bore
const BAR_L = 15.0;           // PTFE stir bar, length
const BAR_D = 6.0;            // PTFE stir bar, diameter

// ---- 40 x 40 x 10 mm fan ---------------------------------------------------
const FAN_W = 40.0;
const FAN_T = 10.0;
const FAN_PITCH = 32.0;
const FAN_HOLE = 3.4;
const FAN_BORE = 38.0;
const HUB_D = 22.0;

// ---- magnets ---------------------------------------------------------------
const MAG_D = 6.35;           // 1/4 in
const MAG_T = 3.175;          // 1/8 in
const MAG_CC = 12.0;          // centre-to-centre, one N up and one S up

// ---- printed parts -----------------------------------------------------------
const FOOT = 56.0;            // square footprint
const FOOT_R = 5.0;
const CAV = 47.0;             // base cavity
const FLOOR_T = 2.5;
const Z_FAN0 = 8.0;           // fan bottom face
const Z_FAN1 = Z_FAN0 + FAN_T;
const Z_WALL = Z_FAN1 + 0.5;  // base wall top = holder underside
const FLANGE_T = 6.0;
const RECESS_D = 35.0;        // pocket the magnets turn in
const RUN_GAP = 1.0;          // magnet top to pocket ceiling
const VFLOOR_T = 1.2;         // printed floor under the vial
const Z_RECESS = Z_FAN1 + MAG_T + RUN_GAP;
const Z_VIAL = Z_RECESS + VFLOOR_T;   // vial outer bottom
const BORE_D = 28.8;
const RIB_R = 14.0;           // crush-rib crest radius (28.0 mm vial)
const TOWER_D = 39.0;
const Z_TOP = Z_VIAL + 25.1;
const POST = 23.5;            // holder screw / insert positions, +-x +-y
const INSERT_HOLE = 4.0;      // M3 x 5.7 heat-set insert
const INSERT_OD = 4.6;
const INSERT_L = 5.7;

// ---- CubXL peg interface (PLACEHOLDER until the deck is measured) --------
const PEG_D = 6.0;
const PEG_L = 5.0;
const PEG_PITCH = 25.0;
const BOARD_T = 6.0;

// ---- assembly sequence -------------------------------------------------------
const S_BASE = 1;
const S_INSERTS = 2;
const S_CTRL = 3;
const S_FAN = 4;
const S_FANSCREWS = 5;
const S_MAGNETS = 6;
const S_HOLDER = 7;
const S_HSCREWS = 8;
const S_PLACE = 9;
const S_VIAL = 10;
const N_STEPS = 10;
const LIFT = 30.0;

function pt(x is number, y is number, z is number) returns Vector
{
    return vector(x, y, z) * millimeter;
}

function mkBox(context is Context, id is Id, x0 is number, y0 is number, z0 is number, x1 is number, y1 is number, z1 is number) returns Query
{
    fCuboid(context, id, { "corner1" : pt(x0, y0, z0), "corner2" : pt(x1, y1, z1) });
    return qCreatedBy(id, EntityType.BODY);
}

function mkCyl(context is Context, id is Id, x is number, y is number, z0 is number, z1 is number, r is number) returns Query
{
    fCylinder(context, id, { "bottomCenter" : pt(x, y, z0), "topCenter" : pt(x, y, z1), "radius" : r * millimeter });
    return qCreatedBy(id, EntityType.BODY);
}

function mkCylX(context is Context, id is Id, x0 is number, x1 is number, y is number, z is number, r is number) returns Query
{
    fCylinder(context, id, { "bottomCenter" : pt(x0, y, z), "topCenter" : pt(x1, y, z), "radius" : r * millimeter });
    return qCreatedBy(id, EntityType.BODY);
}

function mkCone(context is Context, id is Id, x is number, y is number, z0 is number, z1 is number, r0 is number, r1 is number) returns Query
{
    fCone(context, id, { "bottomCenter" : pt(x, y, z0), "topCenter" : pt(x, y, z1), "bottomRadius" : r0 * millimeter, "topRadius" : r1 * millimeter });
    return qCreatedBy(id, EntityType.BODY);
}

function mkConeX(context is Context, id is Id, x0 is number, x1 is number, y is number, z is number, r0 is number, r1 is number) returns Query
{
    fCone(context, id, { "bottomCenter" : pt(x0, y, z), "topCenter" : pt(x1, y, z), "bottomRadius" : r0 * millimeter, "topRadius" : r1 * millimeter });
    return qCreatedBy(id, EntityType.BODY);
}

function mkUnite(context is Context, id is Id, bodies is Query)
{
    if (size(evaluateQuery(context, bodies)) > 1)
    {
        opBoolean(context, id, { "tools" : bodies, "operationType" : BooleanOperationType.UNION });
    }
}

function mkSub(context is Context, id is Id, targets is Query, tools is Query)
{
    opBoolean(context, id, { "tools" : tools, "targets" : targets, "operationType" : BooleanOperationType.SUBTRACTION });
}

// Rounded-rectangle prism centred on (cx, cy).
function mkRBox(context is Context, id is Id, cx is number, cy is number, w is number, d is number, z0 is number, z1 is number, r is number) returns Query
{
    const hw = w / 2;
    const hd = d / 2;
    mkBox(context, id + "a", cx - hw + r, cy - hd, z0, cx + hw - r, cy + hd, z1);
    mkBox(context, id + "b", cx - hw, cy - hd + r, z0, cx + hw, cy + hd - r, z1);
    var i = 0;
    for (var sx in [-1, 1])
    {
        for (var sy in [-1, 1])
        {
            mkCyl(context, id + ("c" ~ i), cx + sx * (hw - r), cy + sy * (hd - r), z0, z1, r);
            i += 1;
        }
    }
    mkUnite(context, id + "u", qCreatedBy(id, EntityType.BODY));
    return qCreatedBy(id, EntityType.BODY);
}

function mkZRot(deg is number) returns Transform
{
    return rotationAround(line(pt(0, 0, 0), vector(0, 0, 1)), deg * degree);
}

function mkLook(context is Context, q is Query, name is string, c is Color)
{
    setProperty(context, { "entities" : q, "propertyType" : PropertyType.NAME, "value" : name });
    setProperty(context, { "entities" : q, "propertyType" : PropertyType.APPEARANCE, "value" : c });
}

// ---------------------------------------------------------------------------
// Parts
// ---------------------------------------------------------------------------

function makeBase(context is Context, id is Id) returns Query
{
    const body = mkRBox(context, id + "body", 0, 0, FOOT, FOOT, 0, Z_WALL, FOOT_R);
    mkRBox(context, id + "cav", 0, 0, CAV, CAV, FLOOR_T, Z_WALL + 1, 3);
    mkSub(context, id + "s1", body, qCreatedBy(id + "cav", EntityType.BODY));
    // fan posts and corner posts
    var i = 0;
    for (var sx in [-1, 1])
    {
        for (var sy in [-1, 1])
        {
            mkCyl(context, id + ("fp" ~ i), sx * FAN_PITCH / 2, sy * FAN_PITCH / 2, FLOOR_T - 0.01, Z_FAN0, 4.0);
            mkCyl(context, id + ("cp" ~ i), sx * POST, sy * POST, FLOOR_T - 0.01, Z_WALL, 4.0);
            i += 1;
        }
    }
    // controller rails and stop
    mkBox(context, id + "rail1", -22.6, -8.9, FLOOR_T - 0.01, -2.0, -7.4, 3.0);
    mkBox(context, id + "rail2", -22.6, 7.4, FLOOR_T - 0.01, -2.0, 8.9, 3.0);
    mkBox(context, id + "stop", -1.6, -5.0, FLOOR_T - 0.01, -0.4, 5.0, 5.5);
    // pegs into the CubXL deck (placeholder geometry)
    mkCyl(context, id + "peg1", -PEG_PITCH, 0, -PEG_L, 0.01, PEG_D / 2 - 0.1);
    mkCyl(context, id + "peg2", PEG_PITCH, 0, -PEG_L, 0.01, PEG_D / 2 - 0.1);
    mkUnite(context, id + "u1", qCreatedBy(id, EntityType.BODY));
    // insert holes
    i = 0;
    for (var sx in [-1, 1])
    {
        for (var sy in [-1, 1])
        {
            mkCyl(context, id + ("fh" ~ i), sx * FAN_PITCH / 2, sy * FAN_PITCH / 2, Z_FAN0 - 6.5, Z_FAN0 + 1, INSERT_HOLE / 2);
            mkCyl(context, id + ("ch" ~ i), sx * POST, sy * POST, Z_WALL - 6.5, Z_WALL + 1, INSERT_HOLE / 2);
            i += 1;
        }
    }
    // USB-C notch (-x wall), vents (+-y and +x walls)
    mkBox(context, id + "usb", -FOOT / 2 - 1, -6.5, 2.0, -CAV / 2 + 0.5, 6.5, Z_WALL + 1);
    for (var k = 0; k < 3; k += 1)
    {
        const z0 = 9.5 + k * 3.0;
        mkBox(context, id + ("vy" ~ k), -13, -FOOT / 2 - 1, z0, 13, FOOT / 2 + 1, z0 + 1.6);
        mkBox(context, id + ("vx" ~ k), 0, -13, z0, FOOT / 2 + 1, 13, z0 + 1.6);
    }
    const cuts = qUnion([qCreatedBy(id + "fh0", EntityType.BODY), qCreatedBy(id + "fh1", EntityType.BODY), qCreatedBy(id + "fh2", EntityType.BODY), qCreatedBy(id + "fh3", EntityType.BODY),
                qCreatedBy(id + "ch0", EntityType.BODY), qCreatedBy(id + "ch1", EntityType.BODY), qCreatedBy(id + "ch2", EntityType.BODY), qCreatedBy(id + "ch3", EntityType.BODY),
                qCreatedBy(id + "usb", EntityType.BODY), qCreatedBy(id + "vy0", EntityType.BODY), qCreatedBy(id + "vy1", EntityType.BODY), qCreatedBy(id + "vy2", EntityType.BODY),
                qCreatedBy(id + "vx0", EntityType.BODY), qCreatedBy(id + "vx1", EntityType.BODY), qCreatedBy(id + "vx2", EntityType.BODY)]);
    mkSub(context, id + "s2", qSubtraction(qCreatedBy(id, EntityType.BODY), cuts), cuts);
    const q = qCreatedBy(id, EntityType.BODY);
    mkLook(context, q, "Base (printed)", color(0.27, 0.29, 0.33));
    return q;
}

function makeHolder(context is Context, id is Id) returns Query
{
    mkRBox(context, id + "flange", 0, 0, FOOT, FOOT, Z_WALL, Z_WALL + FLANGE_T, FOOT_R);
    mkCyl(context, id + "tower", 0, 0, Z_WALL, Z_TOP, TOWER_D / 2);
    mkUnite(context, id + "u1", qCreatedBy(id, EntityType.BODY));
    const body = qUnion(evaluateQuery(context, qCreatedBy(id, EntityType.BODY)));
    var tools = [];
    tools = append(tools, mkCyl(context, id + "recess", 0, 0, Z_WALL - 1, Z_RECESS, RECESS_D / 2));
    tools = append(tools, mkCyl(context, id + "bore", 0, 0, Z_VIAL, Z_TOP + 1, BORE_D / 2));
    tools = append(tools, mkCone(context, id + "lead", 0, 0, Z_TOP - 1.2, Z_TOP + 0.01, BORE_D / 2, BORE_D / 2 + 1.2));
    tools = append(tools, mkBox(context, id + "window", -3.5, -TOWER_D / 2 - 1, Z_VIAL + 3, 3.5, 0, Z_VIAL + 17));
    var i = 0;
    for (var sx in [-1, 1])
    {
        for (var sy in [-1, 1])
        {
            tools = append(tools, mkCyl(context, id + ("head" ~ i), sx * FAN_PITCH / 2, sy * FAN_PITCH / 2, Z_WALL - 1, Z_FAN1 + 3.6, 3.6));
            tools = append(tools, mkCyl(context, id + ("thru" ~ i), sx * POST, sy * POST, Z_WALL - 1, Z_WALL + FLANGE_T + 1, 1.7));
            i += 1;
        }
    }
    mkSub(context, id + "s1", body, qUnion(tools));
    // three crush ribs in the bore
    const rib = mkBox(context, id + "rib0", RIB_R, -0.8, Z_VIAL + 1.0, BORE_D / 2 + 0.3, 0.8, Z_TOP - 1.5);
    opPattern(context, id + "ribs", { "entities" : rib, "transforms" : [mkZRot(120), mkZRot(240)], "instanceNames" : ["r1", "r2"] });
    mkUnite(context, id + "u2", qCreatedBy(id, EntityType.BODY));
    const q = qCreatedBy(id, EntityType.BODY);
    mkLook(context, q, "Vial holder (printed)", color(0.10, 0.58, 0.60));
    return q;
}

function makeFan(context is Context, id is Id) returns Query
{
    const frame = mkRBox(context, id + "frame", 0, 0, FAN_W, FAN_W, Z_FAN0, Z_FAN1, 3.0);
    var tools = [mkCyl(context, id + "bore", 0, 0, Z_FAN0 - 1, Z_FAN1 + 1, FAN_BORE / 2)];
    var i = 0;
    for (var sx in [-1, 1])
    {
        for (var sy in [-1, 1])
        {
            tools = append(tools, mkCyl(context, id + ("h" ~ i), sx * FAN_PITCH / 2, sy * FAN_PITCH / 2, Z_FAN0 - 1, Z_FAN1 + 1, FAN_HOLE / 2));
            i += 1;
        }
    }
    mkSub(context, id + "s1", frame, qUnion(tools));
    // motor mount + struts on the bottom (exhaust) face
    mkCyl(context, id + "mount", 0, 0, Z_FAN0, Z_FAN0 + 2.0, 10.5);
    const strut = mkBox(context, id + "strut0", 9.0, -0.9, Z_FAN0, FAN_BORE / 2 + 0.3, 0.9, Z_FAN0 + 2.0);
    opPattern(context, id + "struts", { "entities" : strut, "transforms" : [mkZRot(90), mkZRot(180), mkZRot(270)], "instanceNames" : ["s1", "s2", "s3"] });
    // rotor: hub cup + seven blades
    mkCyl(context, id + "hub", 0, 0, Z_FAN0 + 2.0, Z_FAN1, HUB_D / 2);
    const blade = mkBox(context, id + "blade0", HUB_D / 2 - 1.0, -0.5, Z_FAN0 + 2.8, FAN_BORE / 2 - 0.6, 0.5, Z_FAN1 - 0.8);
    opTransform(context, id + "tilt", { "bodies" : blade, "transform" : rotationAround(line(pt(0, 0, (Z_FAN0 + Z_FAN1) / 2 + 0.6), vector(1, 0, 0)), 38 * degree) });
    var tr = [];
    var names = [];
    for (var k = 1; k < 7; k += 1)
    {
        tr = append(tr, mkZRot(k * 360 / 7));
        names = append(names, "b" ~ k);
    }
    opPattern(context, id + "blades", { "entities" : blade, "transforms" : tr, "instanceNames" : names });
    mkUnite(context, id + "u1", qCreatedBy(id, EntityType.BODY));
    // trim blade tips that the tilt pushed outside the frame faces
    const keep = qCreatedBy(id, EntityType.BODY);
    const t1 = mkBox(context, id + "trimTop", -30, -30, Z_FAN1, 30, 30, Z_FAN1 + 10);
    const t2 = mkBox(context, id + "trimBot", -30, -30, Z_FAN0 - 10, 30, 30, Z_FAN0);
    mkSub(context, id + "s2", qSubtraction(keep, qUnion([t1, t2])), qUnion([t1, t2]));
    const q = qCreatedBy(id, EntityType.BODY);
    mkLook(context, q, "Fan 40x40x10 mm, 5 V, 4-wire (purchased)", color(0.08, 0.08, 0.09));
    return q;
}

function makeCarrier(context is Context, id is Id) returns Query
{
    const disc = mkCyl(context, id + "disc", 0, 0, Z_FAN1, Z_FAN1 + MAG_T, HUB_D / 2 - 0.5);
    const p1 = mkCyl(context, id + "p1", -MAG_CC / 2, 0, Z_FAN1 - 1, Z_FAN1 + MAG_T + 1, MAG_D / 2 + 0.15);
    const p2 = mkCyl(context, id + "p2", MAG_CC / 2, 0, Z_FAN1 - 1, Z_FAN1 + MAG_T + 1, MAG_D / 2 + 0.15);
    mkSub(context, id + "s1", disc, qUnion([p1, p2]));
    const q = qCreatedBy(id, EntityType.BODY);
    mkLook(context, q, "Magnet carrier (printed)", color(0.96, 0.55, 0.10));
    return q;
}

function makeMagnet(context is Context, id is Id, x is number, northUp is boolean) returns Query
{
    const q = mkCyl(context, id, x, 0, Z_FAN1, Z_FAN1 + MAG_T, MAG_D / 2);
    if (northUp)
    {
        mkLook(context, q, "Magnet N52 1/4 x 1/8 in, N up", color(0.85, 0.13, 0.13));
    }
    else
    {
        mkLook(context, q, "Magnet N52 1/4 x 1/8 in, S up", color(0.13, 0.30, 0.85));
    }
    return q;
}

// M3 socket head cap screw, head on top, seat at z = zSeat
function makeScrew(context is Context, id is Id, x is number, y is number, zSeat is number, len is number, name is string) returns Query
{
    const head = mkCyl(context, id + "head", x, y, zSeat, zSeat + 3.0, 2.75);
    const shank = mkCyl(context, id + "shank", x, y, zSeat - len, zSeat + 0.01, 1.5);
    const tip = mkCone(context, id + "tip", x, y, zSeat - len - 0.3, zSeat - len, 1.2, 1.5);
    mkUnite(context, id + "u", qUnion([head, shank, tip]));
    const socket = mkCyl(context, id + "socket", x, y, zSeat + 1.5, zSeat + 3.5, 1.3);
    mkSub(context, id + "s", qSubtraction(qCreatedBy(id, EntityType.BODY), socket), socket);
    const q = qCreatedBy(id, EntityType.BODY);
    mkLook(context, q, name, color(0.13, 0.13, 0.14));
    return q;
}

function makeInsert(context is Context, id is Id, x is number, y is number, zTop is number) returns Query
{
    const b = mkCyl(context, id + "b", x, y, zTop - INSERT_L, zTop, INSERT_OD / 2);
    const g1 = mkCyl(context, id + "g1", x, y, zTop - 2.2, zTop - 1.6, INSERT_OD / 2 + 1);
    const g2 = mkCyl(context, id + "g2", x, y, zTop - 4.4, zTop - 3.8, INSERT_OD / 2 + 1);
    const inner1 = mkCyl(context, id + "g1i", x, y, zTop - 2.3, zTop - 1.5, INSERT_OD / 2 - 0.35);
    const inner2 = mkCyl(context, id + "g2i", x, y, zTop - 4.5, zTop - 3.7, INSERT_OD / 2 - 0.35);
    mkSub(context, id + "s0", g1, inner1);
    mkSub(context, id + "s0b", g2, inner2);
    const hole = mkCyl(context, id + "hole", x, y, zTop - INSERT_L - 1, zTop + 1, 1.5);
    mkSub(context, id + "s1", b, qUnion([g1, g2, hole]));
    const q = qCreatedBy(id, EntityType.BODY);
    mkLook(context, q, "Heat-set insert M3 x 5.7 mm", color(0.80, 0.62, 0.25));
    return q;
}

function makeController(context is Context, id is Id) returns Query
{
    const pcb = mkBox(context, id + "pcb", -22.6, -8.9, 3.0, -1.6, 8.9, 4.2);
    mkLook(context, pcb, "Seeed XIAO RP2040 (purchased)", color(0.05, 0.25, 0.45));
    const usb = mkBox(context, id + "usb", -23.6, -4.47, 4.2, -16.25, 4.47, 7.46);
    mkLook(context, usb, "XIAO USB-C receptacle", color(0.78, 0.78, 0.80));
    const chip = mkBox(context, id + "chip", -12.5, -3.5, 4.2, -5.5, 3.5, 5.0);
    mkLook(context, chip, "XIAO RP2040 chip", color(0.06, 0.06, 0.06));
    return qCreatedBy(id, EntityType.BODY);
}

function makeVial(context is Context, id is Id) returns Query
{
    const z0 = Z_VIAL;
    const ro = VIAL_OD / 2;
    const ri = ro - VIAL_WALL;
    const zs = z0 + VIAL_H - 7;
    mkCyl(context, id + "body", 0, 0, z0, zs, ro);
    mkCone(context, id + "shoulder", 0, 0, zs - 0.01, zs + 2.0, ro, NECK_OD / 2);
    mkCyl(context, id + "neck", 0, 0, zs + 1.99, z0 + VIAL_H, NECK_OD / 2);
    mkUnite(context, id + "u", qCreatedBy(id, EntityType.BODY));
    const outer = qUnion(evaluateQuery(context, qCreatedBy(id, EntityType.BODY)));
    const c1 = mkCyl(context, id + "c1", 0, 0, z0 + VIAL_BOT, zs, ri);
    const c2 = mkCone(context, id + "c2", 0, 0, zs - 0.01, zs + 2.0, ri, NECK_OD / 2 - 1.6);
    const c3 = mkCyl(context, id + "c3", 0, 0, zs + 1.99, z0 + VIAL_H + 1, NECK_OD / 2 - 1.6);
    mkSub(context, id + "s", outer, qUnion([c1, c2, c3]));
    const q = qCreatedBy(id, EntityType.BODY);
    mkLook(context, q, "Vial 20 mL, 28 mm OD (glass)", color(0.80, 0.90, 1.0, 0.30));
    return q;
}

function makeLiquid(context is Context, id is Id) returns Query
{
    const z0 = Z_VIAL + VIAL_BOT;
    const q = mkCyl(context, id + "l", 0, 0, z0, z0 + FILL_H, VIAL_OD / 2 - VIAL_WALL);
    mkLook(context, q, "Sample, ~10 mL", color(0.35, 0.60, 0.95, 0.35));
    return q;
}

function makeBar(context is Context, id is Id) returns Query
{
    const zc = Z_VIAL + VIAL_BOT + BAR_D / 2;
    const h = BAR_L / 2;
    mkCylX(context, id + "c", -h + 1.5, h - 1.5, 0, zc, BAR_D / 2);
    mkConeX(context, id + "e1", h - 1.51, h, 0, zc, BAR_D / 2, BAR_D / 2 - 1.2);
    mkConeX(context, id + "e2", -h + 1.51, -h, 0, zc, BAR_D / 2, BAR_D / 2 - 1.2);
    mkCylX(context, id + "ring", -1.0, 1.0, 0, zc, BAR_D / 2 + 0.4);
    mkUnite(context, id + "u", qCreatedBy(id, EntityType.BODY));
    const q = qCreatedBy(id, EntityType.BODY);
    mkLook(context, q, "Stir bar, PTFE, 15 x 6 mm", color(0.97, 0.97, 0.97));
    return q;
}

function makeBoard(context is Context, id is Id) returns Query
{
    const body = mkBox(context, id + "plate", -62.5, -50, -BOARD_T, 62.5, 50, 0);
    var tools = [];
    var i = 0;
    for (var ix = -2; ix <= 2; ix += 1)
    {
        for (var iy = -1; iy <= 1; iy += 1)
        {
            tools = append(tools, mkCyl(context, id + ("h" ~ i), ix * PEG_PITCH, iy * PEG_PITCH, -BOARD_T - 1, 1, PEG_D / 2 + 0.1));
            i += 1;
        }
    }
    mkSub(context, id + "s", body, qUnion(tools));
    const q = qCreatedBy(id, EntityType.BODY);
    mkLook(context, q, "CubXL deck plate (section, reference only)", color(0.72, 0.74, 0.77));
    return q;
}

// ---------------------------------------------------------------------------

annotation { "Feature Type Name" : "Single-vial stirrer (CubXL)" }
export const vialStirrer = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Assembly step (0 = assembled)" }
        isInteger(definition.step, { (unitless) : [0, 0, 20] } as IntegerBoundSpec);

        annotation { "Name" : "Exploded view" }
        definition.exploded is boolean;

        annotation { "Name" : "Section at y = 0" }
        definition.section is boolean;
    }
    {
        setVariable(context, "dbg", "start");
        try
        {
        // [query, install step, explode offset (mm, z), exploded-view z]
        var groups = [];
        groups = append(groups, [makeBoard(context, id + "board"), 0, 0, -40]);
        setVariable(context, "dbg", "board");
        groups = append(groups, [makeBase(context, id + "base"), S_BASE, 0, 0]);
        setVariable(context, "dbg", "base");
        var ins = [];
        var i = 0;
        for (var sx in [-1, 1])
        {
            for (var sy in [-1, 1])
            {
                ins = append(ins, makeInsert(context, id + ("insF" ~ i), sx * FAN_PITCH / 2, sy * FAN_PITCH / 2, Z_FAN0));
                ins = append(ins, makeInsert(context, id + ("insC" ~ i), sx * POST, sy * POST, Z_WALL));
                i += 1;
            }
        }
        groups = append(groups, [qUnion(ins), S_INSERTS, 14, 16]);
        setVariable(context, "dbg", "inserts");
        groups = append(groups, [makeController(context, id + "ctrl"), S_CTRL, 16, 24]);
        setVariable(context, "dbg", "ctrl");
        groups = append(groups, [makeFan(context, id + "fan"), S_FAN, 18, 32]);
        setVariable(context, "dbg", "fan");
        var fs = [];
        var hs = [];
        i = 0;
        for (var sx in [-1, 1])
        {
            for (var sy in [-1, 1])
            {
                fs = append(fs, makeScrew(context, id + ("fs" ~ i), sx * FAN_PITCH / 2, sy * FAN_PITCH / 2, Z_FAN1, 16, "M3 x 16 socket head cap screw"));
                hs = append(hs, makeScrew(context, id + ("hs" ~ i), sx * POST, sy * POST, Z_WALL + FLANGE_T, 12, "M3 x 12 socket head cap screw"));
                i += 1;
            }
        }
        groups = append(groups, [qUnion(fs), S_FANSCREWS, 16, 52]);
        setVariable(context, "dbg", "fanscrews");
        groups = append(groups, [makeCarrier(context, id + "carrier"), S_MAGNETS, 10, 58]);
        const m1 = makeMagnet(context, id + "mag1", -MAG_CC / 2, true);
        const m2 = makeMagnet(context, id + "mag2", MAG_CC / 2, false);
        groups = append(groups, [qUnion([m1, m2]), S_MAGNETS, 20, 68]);
        setVariable(context, "dbg", "magnets");
        groups = append(groups, [makeHolder(context, id + "holder"), S_HOLDER, 26, 80]);
        setVariable(context, "dbg", "holder");
        groups = append(groups, [qUnion(hs), S_HSCREWS, 16, 100]);
        const vial = makeVial(context, id + "vial");
        const liq = makeLiquid(context, id + "liq");
        groups = append(groups, [qUnion([vial, liq]), S_VIAL, 45, 118]);
        groups = append(groups, [makeBar(context, id + "bar"), S_VIAL, 85, 150]);
        setVariable(context, "dbg", "parts");

        const step = definition.step;
        var n = 0;
        for (var g in groups)
        {
            const q = g[0];
            const s = g[1];
            var dz = 0;
            var drop = false;
            if (definition.exploded)
            {
                dz = g[3];
            }
            else if (step > 0)
            {
                if (s == 0 && step < S_PLACE)
                {
                    drop = true;
                }
                else if (s > step)
                {
                    drop = true;
                }
                else if (s == step)
                {
                    dz = g[2];
                }
                if (!drop && s > 0 && s < S_PLACE && step <= S_PLACE)
                {
                    dz += LIFT;
                }
            }
            if (drop)
            {
                opDeleteBodies(context, id + ("del" ~ n), { "entities" : q });
            }
            else if (dz != 0)
            {
                opTransform(context, id + ("mv" ~ n), { "bodies" : q, "transform" : transform(pt(0, 0, dz)) });
            }
            n += 1;
        }
        setVariable(context, "dbg", "steps");
        if (definition.section)
        {
            const cutter = mkBox(context, id + "cutter", -200, -200, -100, 200, 0, 300);
            var toCut = [];
            var toDel = [];
            for (var b in evaluateQuery(context, qSubtraction(qCreatedBy(id, EntityType.BODY), cutter)))
            {
                const bb = evBox3d(context, { "topology" : b });
                if (bb.maxCorner[1] <= 0.0001 * millimeter)
                {
                    toDel = append(toDel, b);
                }
                else if (bb.minCorner[1] < -0.0001 * millimeter)
                {
                    toCut = append(toCut, b);
                }
            }
            if (size(toDel) > 0)
            {
                opDeleteBodies(context, id + "secDel", { "entities" : qUnion(toDel) });
            }
            if (size(toCut) > 0)
            {
                opBoolean(context, id + "cut", { "tools" : cutter, "targets" : qUnion(toCut), "operationType" : BooleanOperationType.SUBTRACTION });
            }
            else
            {
                opDeleteBodies(context, id + "cutterDel", { "entities" : cutter });
            }
        }
        setVariable(context, "dbg", "done");
        }
        catch (error)
        {
            setVariable(context, "err", error);
        }
    });
