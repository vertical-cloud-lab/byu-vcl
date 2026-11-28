// Assembled OpenFlexure Microscope v7 (v7.0.0-beta5) in its reflection
// (epi-) illumination configuration, one part per run, selected with -D PART="...".
// Built on the repo's own rendering/ assembly modules (the ones used for the
// assembly-instruction images).  Additions not in those renders:
//   * RMS optics module with beamsplitter=true (instead of the standard one)
//   * fl_cube, reflection illuminator holder and LED condenser (lens_holder),
//     placed by transforms derived from lib_fl_cube.scad / reflection_illuminator.scad
//   * main body split into the moving XY stage, the four flexure legs (two of
//     them with their actuating levers), the two XY actuator columns and the rest
//   * placeholder star LED and glass slide (not OpenFlexure geometry)
// Transmission illumination (dovetail + condenser) is deliberately left out.

use <../openscad/libs/microscope_parameters.scad>
use <../openscad/libs/utilities.scad>
use <../openscad/libs/libdict.scad>
use <../openscad/libs/lib_microscope_stand.scad>
use <../openscad/libs/lib_optics.scad>
use <../openscad/libs/optics_configurations.scad>
use <../openscad/libs/lib_fl_cube.scad>
use <../openscad/libs/main_body_structure.scad>
use <../openscad/libs/main_body_transforms.scad>
use <../openscad/libs/compact_nut_seat.scad>
use <../openscad/reflection_illuminator.scad>
use <librender/assembly_parameters.scad>
use <librender/render_utils.scad>
use <librender/render_settings.scad>
use <librender/hardware.scad>
use <librender/electronics.scad>
use <librender/optics.scad>
use <mount_motors.scad>
use <mount_sample_clips.scad>
use <mount_microscope.scad>
use <mount_electronics.scad>
use <prepare_stand.scad>
use <prepare_main_body.scad>
use <actuator_assembly.scad>
use <rms_optics_assembly.scad>

PART = "main_body";
// Position of the LED condenser along the slip-plate slots (module -y), see report.
LED_CONDENSER_Y = -30.5;

function bs_config() = rms_f50d13_config(beamsplitter=true);
function fcb() = fl_cube_bottom(render_params(), bs_config());

module MF(){ mounted_microscope_frame(manual=false, post=false){ children(); } }

module stage_region(){
    params = render_params();
    // the outer outline of the XY stage, from its underside to above the sample plane, grown by 0.1 mm so that it
    // takes the hair-thin edge of the top flexure ring that runs along the outline between the legs
    translate_z(upper_xy_flex_z(params) - 0.3){
        minkowski(){
            hull(){ xy_stage(params, h=key_lookup("stage_t", params) + 2, on_buildplate=true); }
            cylinder(r=0.1, h=tiny(), $fn=8);
        }
    }
}

// ---- The XY mechanism's moving parts, cut out of the one-piece body (main_body_structure.scad).
// Four legs carry the stage, at 45, 135, -135 and -45 deg (each_leg). Each is a parallelogram linkage: two vertical
// bars between a block at the top and one at the bottom, joined by flexures (leg_flexures), so the top can slide
// sideways (tangentially). A flexure under the bottom block hinges the whole leg to the inner wall (xy_flexures,
// bottom), so the top can also swing radially, and a ring of flexures at the top joins the leg to the stage
// (xy_flexures, top). The two front legs are actuator_leg()s: a horizontal arm out to the actuator column (also
// via a flexure), so a leg and its arm pivot together on the bottom flexure like a bell crank. Frames are
// leg_frame()'s: local y points radially out, x along the tangent, z up; "y" is leg_frame(45), which carries the
// Y actuator, and "x" is its mirror image (each_actuator); the back legs are leg_frame(135) and its mirror.
module in_leg_frame(which){
    params = render_params();
    if (which == "y") leg_frame(params, 45) children();
    if (which == "x") mirror([1, 0, 0]) leg_frame(params, 45) children();
    if (which == "back_left") leg_frame(params, 135) children();
    if (which == "back_right") mirror([1, 0, 0]) leg_frame(params, 135) children();
}

// A region holding one leg (and, if actuated, its arm) and nothing static: the leg's convex hull, plus the strip
// of the top flexure ring between the leg's top block (local y >= 0) and the stage's edge (y = -flex_dims().y).
// The bottom flexures (y < 0) stay with the body.
module leg_region(actuated=false){
    params = render_params();
    e = 0.2;
    fy = flex_dims().y;
    ow = leg_outer_w(params);
    brace = actuated ? 20 : flex_dims().x;      // actuator_leg() uses leg(brace=20); leg()'s default is flex_dims().x
    base_y = flex_dims().x + brace;              // the bars widen to this at the bottom
    hull(){
        translate([-ow/2 - e, -0.01, -1]) cube([ow + 2*e, base_y + e + 0.01, key_lookup("leg_block_t", params) + 1 + e]);
        translate([-ow/2 - e, -0.01, -1]) cube([ow + 2*e, leg_dims(params).y + e + 0.01, leg_height(params) + 1 + e]);
    }
    translate([-(leg_middle_w()/2 + fy), -fy - 0.01, upper_xy_flex_z(params) - 0.3])
        cube([leg_middle_w() + 2*fy, fy + 0.02, flex_dims().z + 2.3]);
    if (actuated) arm_region();
}

// The actuator column sits in its housing at local y = actuating_nut_r. It joins the arm through a flexure at its
// foot, z < flex_dims().z. Above that the two are apart: the arm's actuator_end_cutout(lever_tip=2.5) ends it at
// y' = -flex_dims().y/2 and, higher up, at y' + z = 2.5 (y' measured out from the column axis); the column's slot
// ("space for lever and flexure", lever_tip=3) starts at y' = +flex_dims().y/2 and y' + z = 4.5. This region is the
// column's side of that gap (y' >= 0 up to z = c, then y' + z >= c, c = 3.5 in the middle), inside the housing's
// stadium-shaped void (nut_seat_void) shrunk by 0.4 mm so that it takes none of the housing.
module column_region(){
    params = render_params();
    fz = flex_dims().z;
    c = fz + (2.5 + 3)/2;
    translate_y(actuating_nut_r(params)) intersection(){
        translate_z(-1) linear_extrude(key_lookup("actuator_h", params) + 2.5)
            nut_seat_silhouette(offset=-actuator_wall_t() - 0.4);
        rotate([90, 0, 90]) linear_extrude(100, center=true)
            polygon([[0, -1], [50, -1], [50, 50], [c - 50, 50], [0, c]]);
    }
}

// The arm (actuator_leg()'s horizontal bit) from the leg's foot to its column: actuator_dims() wide and high,
// widening to leg_middle_w() where it meets the leg; the column side of the flexure is left out.
module arm_region(){
    params = render_params();
    e = 0.2;
    w = actuator_dims(params).x;
    difference(){
        union(){
            translate([-w/2 - e, -0.01, -1]) cube([w + 2*e, actuating_nut_r(params) + 6, actuator_dims(params).z + 1 + e]);
            translate([-leg_middle_w()/2 - e, -0.01, -1]) cube([leg_middle_w() + 2*e, 20 + flex_dims().x + e, 4 + 1 + e]);
        }
        column_region();
    }
}

module actuated_legs_region(){ in_leg_frame("x") leg_region(true); in_leg_frame("y") leg_region(true); }
module back_legs_region(){ in_leg_frame("back_left") leg_region(); in_leg_frame("back_right") leg_region(); }
module columns_region(){ in_leg_frame("x") column_region(); in_leg_frame("y") column_region(); }
module mechanism_region(){ actuated_legs_region(); back_legs_region(); columns_region(); }

// fl_cube.scad models the cube "as printed" (its Y = optical axis up, its Z = slide-in axis)
module fl_cube_placed(){
    translate([0, fl_cube_w()/2, fcb()]) rotate_x(90) fl_cube();
}
// illuminator_holder() is flipped (slip plate on top) and pushed onto the cube's outer face
function holder_c() = fcb() + (fl_cube_w()/2 + 2) + (slip_plate_thickness() + filter_cube_z() + fl_cube_w()/2);
module holder_placed(){
    translate([0, -fl_cube_w()/2, holder_c()]) rotate_x(180) illuminator_holder();
}
// lens_holder(): optical axis (local z) -> module +y (towards the cube),
// flat face (local +y) -> up against the underside of the slip plate.
module condenser_frame(){
    multmatrix([[-1, 0, 0, 0],
                [ 0, 0, 1, LED_CONDENSER_Y],
                [ 0, 1, 0, fcb() + fl_cube_w()/2 + 2],
                [ 0, 0, 0, 1]]) children();
}

module part(name){
    params = render_params();
    stand_params = render_stand_params(manual=false, post=false);
    if (name == "stand") render_stand(params, stand_params);
    if (name == "main_body_full") MF() render_body();
    if (name == "main_body") MF() difference(){ render_body(); stage_region(); mechanism_region(); }
    if (name == "xy_stage") MF() intersection(){ render_body(); stage_region(); }
    // the legs and columns: what of the body is in each one's region, less the stage
    for (leg = ["x", "y", "back_left", "back_right"]) if (name == str("leg_", leg)) MF() difference(){
        intersection(){ render_body(); in_leg_frame(leg) leg_region(actuated=(leg == "x" || leg == "y")); }
        stage_region();
    }
    for (leg = ["x", "y"]) if (name == str("actuator_column_", leg)) MF()
        intersection(){ render_body(); in_leg_frame(leg) column_region(); }
    if (name == "actuator_x") MF() x_actuator_assembly();
    if (name == "actuator_y") MF() y_actuator_assembly();
    if (name == "actuator_z") MF() z_actuator_assembly();
    if (name == "motor_x") MF() mirror([1, 0, 0]) y_motor_and_cap(params, mirror_connector=true);
    if (name == "motor_y") MF() y_motor_and_cap(params);
    if (name == "motor_z") MF() z_motor_and_cap(params, optics_version="rms", cap=true);
    if (name == "optics_module_beamsplitter") MF() coloured_render(optics_module_colour()) optics_module_rms(params, bs_config());
    if (name == "objective") MF() translate_z(30.1) rendered_objective();
    if (name == "tube_lens") MF() translate_z(18.5) tube_lens();
    if (name == "picamera2_with_cover") MF() camera_and_screws(create_placement_dict([0, 0, -17.5], [0, 0, 135]));
    if (name == "camera_ribbon_cable") MF() {
        ribbon_start = create_placement_dict([0, 0, -18.75], [0, 0, 135], [0, 180, 0], init_translation=[15, 0, 0]);
        picamera_cable(concat([ribbon_start], curled_ribbon_pos()));
    }
    if (name == "fl_cube") MF() fl_cube_placed();
    if (name == "reflection_illuminator_holder") MF() holder_placed();
    if (name == "reflection_led_condenser") MF() condenser_frame() lens_holder();
    if (name == "led_star_placeholder") MF() condenser_frame() {
        translate_z(-1.6) cylinder(d=20, h=1.6, $fn=6);   // star LED board
        cylinder(d=5, h=1.8, $fn=24);                       // emitter dome
    }
    if (name == "sample_clips") MF() render_sample_clips();
    if (name == "electronics_drawer") render_electronics_drawer(slide=false);
    if (name == "raspberry_pi_4b") render_rpi_4b(slide=false);
    if (name == "sangaboard_v0_5") render_sangaboard_v0_5(slide=false);
    if (name == "hardware") {
        for (i = [0:3]) { stand_nut(params, stand_params, nut_num=i); stand_lug_screw(params, stand_params, i); }
        MF() {
            reflect_x(){ y_motor_nut(params, right=true); y_motor_nut(params, right=false); }
            z_motor_nut(params, right=false); z_motor_nut(params, right=true);
            for (i = [0:3]) stage_nut(params, nut_num=i);
            cable_tidy_screws(params, exploded=false);
            place_part(optics_module_nut_pos()) m3_nut();
            place_part(optics_module_screw_pos()) m3_cap_x10();
        }
        render_drawer_nut(slide=false);
        render_rpi_4b_screws(slide=false);
        render_sangaboard_screws(slide=false);
        render_electronics_drawer_screw(exploded=false);
    }
    if (name == "sample_slide_placeholder") MF() translate([0, 0, key_lookup("sample_z", params) + 0.5]) cube([75, 25, 1], center=true);
}

part(PART);
