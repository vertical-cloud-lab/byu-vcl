// Assembled OpenFlexure Microscope v7 (v7.0.0-beta5) in its reflection
// (epi-) illumination configuration, one part per run, selected with -D PART="...".
// Built on the repo's own rendering/ assembly modules (the ones used for the
// assembly-instruction images).  Additions not in those renders:
//   * RMS optics module with beamsplitter=true (instead of the standard one)
//   * fl_cube, reflection illuminator holder and LED condenser (lens_holder),
//     placed by transforms derived from lib_fl_cube.scad / reflection_illuminator.scad
//   * main body split into the moving XY stage and the rest
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
    // the outer outline of the XY stage, from its underside to above the sample plane
    translate_z(upper_xy_flex_z(params) - 0.3){
        hull(){ xy_stage(params, h=key_lookup("stage_t", params) + 2, on_buildplate=true); }
    }
}

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
    if (name == "main_body") MF() difference(){ render_body(); stage_region(); }
    if (name == "xy_stage") MF() intersection(){ render_body(); stage_region(); }
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
