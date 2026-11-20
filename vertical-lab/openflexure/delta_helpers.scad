// Helper exports of v7 rendering models (objective, tube lens, Pi camera, motors,
// gears, Pi, Sangaboard) in frames chosen for the OpenFlexure Delta Stage assembly.
// Transforms to the delta frame are applied afterwards (see assemble_delta.py).
use <../openscad/libs/microscope_parameters.scad>
use <../openscad/libs/utilities.scad>
use <librender/assembly_parameters.scad>
use <librender/render_utils.scad>
use <librender/render_settings.scad>
use <librender/hardware.scad>
use <librender/electronics.scad>
use <librender/optics.scad>
use <./electronics/sangaboard.scad>
use <motor_assembly.scad>
use <actuator_assembly.scad>
use <rms_optics_assembly.scad>
use <prepare_pi_and_sangaboard.scad>

PART = "objective";
TUBE_LENS_Z = 18.44;     // from optics.scad (v6) thin-lens calculation for the delta optics module
CAMERA_ROT = 90;         // v7 render uses 135 for camera_rotation 0; delta camera_mount_rotation is -45
DELTA_COLUMN_DZ = 0;     // delta (actuator_h + travel) minus v7 (actuator_h + travel)

params = render_params();
if (PART == "objective") translate_z(30.1) rendered_objective();
if (PART == "tube_lens") translate_z(TUBE_LENS_Z) tube_lens();
if (PART == "camera") camera_and_screws(create_placement_dict([0, 0, -17.5], [0, 0, CAMERA_ROT]));
// in the lens_holder() local frame (optical axis = +z, LED end at z=0)
if (PART == "led_star_local") { translate_z(-1.6) cylinder(d=20, h=1.6, $fn=6); cylinder(d=5, h=1.8, $fn=24); }
// actuator-column local frame: column axis at origin, +y radially outward, z=0 at column bottom
if (PART == "motor_local") intersection(){ translate([-40, -30, -20]) cube([80, 80, 110]); motor_with_gear(create_placement_dict([0, 20, y_motor_z_pos(params) + DELTA_COLUMN_DZ], [0, 0, 180])); }
if (PART == "lead_local") translate_z(xy_lead_assembly_height() + DELTA_COLUMN_DZ) rotate_z(90) lead_screw_assembly();
if (PART == "pi_local") pi_and_sd_card();
if (PART == "sanga_local") sangaboard_v0_5();
if (PART == "echo") echo(v7_travel=xy_actuator_travel(params), v7_actuator_h=key_lookup("actuator_h", params), lead_h=xy_lead_assembly_height(), motor_z=y_motor_z_pos(params), pi_dims=pi_board_dims());
