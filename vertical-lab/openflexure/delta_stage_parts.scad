/*

OpenFlexure Delta Stage

This project aims to be a high-performance flexure stage, with
long-ish travel in 3D.

*/
include <parameters.scad> //Delta-stage params
use <z_axis.scad>;
use <delta_stage_logo.scad>;
use <../openflexure-microscope/openscad/utilities.scad>;
use <../openflexure-microscope/openscad/compact_nut_seat.scad>;
use <../openflexure-microscope/openscad/reflection_illuminator.scad>;
use <../openflexure-microscope/openscad/z_axis.scad>;
use <../openflexure-microscope/openscad/illumination.scad>;
use <../openflexure-microscope/openscad/logo.scad>;

module lever(){
    // The levers go from the centre to the actuator columns
    // We anchor to the y=0 plane.
    w = leg_strut_l; // width of strut part

    // Flexures that join the lever to the leg
    reflect([1,0,0]) translate([-w/2, lever_l-d, dz]) cube(zflex + [0,2*d,0]);
    
    // This is the main horizontal lever
    difference(){
        hull(){
            translate([-w/2, zflex[1], 0]) cube([w, d, 2]); // flexures attach here
            translate([-w/2+1, zflex[1], 0]) cube([w-2, d, 6]); // flexures attach here
            translate([0, lever_l/2, 12]) cube([10,20,d],center=true); //top
            reflect([1,0,0]) translate([w/2-4, lever_l+zflex[1], 0]) cylinder(r=4, h=2);
            reflect([1,0,0]) translate([w/2-4-3, lever_l+zflex[1], 0]) cylinder(r=4, h=12);
        }
        // cut out a hole for the strut that joins the outer parts of the leg
        translate([-99, lever_l-zflex[0]-1.5, -1]) cube([999, zflex[0]+1.5+zflex[1], 6.5]);
    }
    
    // This part connects to the actuator column
    difference(){
        cbr = column_base_radius(); // from compact_nut_seat.scad
        translate([-cbr, lever_l+zflex[1], 0]) 
            cube([cbr*2, nut_y+zflex[1]/2+d - lever_l-zflex[1], 6]);
        translate([0,nut_y,0]) actuator_end_cutout();
    }
}

module lever_swept(){
    hull() for(a=[-1,1]*asin(flex_a)) rotate([a,0,0]) lever();
}

module lever_flexures(){
    // The flexures that form the main hinge for the leg
    w = leg_strut_l; // width of strut part
    reflect([1,0,0]) hull(){
        translate([-w/2-zflex[1]*tan(30), -d, dz]) cube([zflex[0],d,zflex[2]]);
        translate([-w/2, zflex[1], dz]) cube([zflex[0],d,zflex[2]]);
    }
}

module leg(){
    // The parallelogram leg that connects each lever to the moving stage
    w = leg_strut_l; // width of strut part
    iw = w + 2*zflex[1]; // distance between outer parts of leg
    ow = w + 2*leg_t; // outside width of whole leg
    
    // Start with the bridges between the sides, at top and bottom
    for(p=[[-d, zflex[1], flex_z2], 
            [-d, lever_l-zflex[0], 0]]) reflect([1,0,0]) translate(p){
        cube([w/2+d, zflex[0], 4]); //strut
        cube([iw/2+2*d, zflex[0], zflex[2]]); //flexure
    }
    
    // Now make the sides
    reflect([1,0,0]) hull(){
        translate([w/2+zflex[1], lever_l-zflex[0], 0]) cube([d, zflex[0], 4]); //bottom flexure
        translate([iw/2+leg_t/2, lever_l-leg_t/2, 0]) cylinder(d=leg_t, h=4); //bottom corner near the flexure
        translate([iw/2+leg_t/2, 15, 0]) cylinder(d=leg_t, h=4); //bottom corner near centre
        translate([iw/2, zflex[1], flex_z2]) cube([leg_t, zflex[0], 4]); //top
    }
    
    // Tie the outer bits together - some of these ties may need to be snipped later.
    translate([0,15,4]) cube([ow, 2, dz], center=true);
    for(p=[0.25,0.5,0.75]) translate([0, zflex[0]/2 + (1-p)*(lever_l-zflex[0]), flex_z2*p]) cube([ow, 2, dz], center=true);
}

module leg_swept(){
    hull() for(d=[-1,1]) translate([0,lever_l,d*lever_l*flex_a]){
        rotate([-d*asin(flex_a), 0, 0]) for(e=[-1,1]){
            smatrix(xz=flex_a*e) translate([0,-lever_l,0]) leg();
        }
    }
}

module stage_flexures(h=zflex[2], z=flex_z2+dz){
    // flexures bridging between the tops of the legs
    w = leg_strut_l; // width of strut part
    for(a=[0,120,240]) hull(){
        r = stage_r+zflex[1];
        s = [zflex[0], d, h];
        rotate(a) mirror([1,0,0]) translate([-w/2, r, z]) cube(s);
        rotate(a-120) translate([-w/2, r, z]) cube(s);
    }
}

module each_lever(){
    // Repeat 3 times, each time starting at the base of a lever.
    for(a=[0,120,240]){
        rotate(a) translate([0,stage_r,0]) children();
        
    }
}
module each_mounting_hole(){
    // Repeat 3 times, in between the levers (i.e. 60 degrees out).
    for(a=[0,120,240]){
        rotate(a+60) translate([0,mounting_hole_r,0]) children();
        
    }
}
    

module stage_edges(h=5-2*dz, z=flex_z2+2*dz){
    // The edges of the moving stage
    w = leg_strut_l+zflex[0]*2*tan(60); // width
    each_lever(){
        translate([-w/2, -zflex[0], z]) cube([w, zflex[0], h]);
    }
}

module stage_mounting_holes(z_translate=0){
    //Generate all the mounting holes for the stage
    each_stage_mounting_hole(z_translate) trylinder_selftap(3,h=999);
}

module each_stage_mounting_hole(z_translate =0){
    // Each of the mounting holes on the stage (3 per leg)
    each_lever() translate([0,-zflex[0]/2,z_translate]) repeat([leg_strut_l/2,0,0],3,center=true) children();
}

module each_stage_mounting_hole_without_center(z_translate =0){
    //The mounting holes (not including the center mounting hole) (2 per leg)
    each_lever() translate([0,-zflex[0]/2,z_translate]) repeat([leg_strut_l,0,0],2,center=true) children();
}

module each_stage_mounting_hole_just_center(z_translate =0){
    //Only the center mounting hold (1 per leg)
    each_lever() translate([0,-zflex[0]/2,z_translate]) children();
}

module each_base_mounting_point(){
    // The locations of the mounting points to the base.
    for(a = [0,120,240]){
        rotate(a)translate([0,mounting_point,0]) children();
    }
}

module moving_stage(){
    // the moving stage is printed suspended between the legs.
    // we start by joining the legs together
    difference(){
        union(){
            stage_flexures();
    
            // start to join the flexure bridges together
            intersection(){
                hull() stage_flexures(h=999);
                stage_edges();
            }
            // continue building up the bridges between the legs
            intersection(){
                stage_flexures(h=999);
                hull() stage_edges();
            }
        }
        //mounting holes for stage
        stage_mounting_holes(z_translate=flex_z2+4*dz);
    }
}

module leg_and_lever_clearance(){
    // A convex space big enough for the leg and lever to move in
    minkowski(){
        union(){
            leg_swept();
            lever_swept();
        }
        translate([0,0,-d]) cylinder(h=2,r=zflex[1]);
    }
}
module motor_and_small_gear_clearance(h=actuator_h+actuator_travel){
    // Cylinders for the small gear and the motor
    gear_pos = [0, nut_y-20, h];
    motor_pos = gear_pos + [0, 7.8, 10];
    translate(gear_pos) cylinder(d=24, h=999);
    translate(motor_pos) cylinder(d=29, h=999);
}

// Cut out hole for reflection illuminator
module fl_cube_cutout(){

    // Create a trapezoid with min width (cube_width) at top
    hull() {
        translate([-(bottom_cutout_w)/2, -49, -0.5]) cube([bottom_cutout_w, 49, 1]);
        translate([-(mid_cutout_w)/2, -49, 10]) cube([mid_cutout_w, 49, 1]); // Highest we usually need
        translate([-top_cutout_w/2, -49, 20]) cube([top_cutout_w, 49, 1]);
        translate([0,-49,20])cylinder_with_45deg_top(r = top_cutout_w/2, h = 49);
    }
}

module casing(){
    difference(){
        union(){
            // casing around the leg&lever
            difference (){
                each_lever() minkowski(){
                    leg_and_lever_clearance();
                    cylinder(r1=wall_t,r2=0.5, h=0.9);
                }
                translate([0,0,casing_height]) cylinder(r=999, h=999, $fn=4); //ensure it doesn't go too high
            }
            // casing for the actuator
            each_lever() translate([0,nut_y,0]) screw_seat(h=actuator_h, travel=actuator_travel, motor_lugs=true, lug_angle=180);
            // join the casings up, by adding a big block in the middle.
            cylinder(r=casing_radius, h=casing_height, $fn=6);
            // add the base mounting points
            if(stage_connectors) {
                base_mounting_points();
            } 
        }
        // hollow out space for the levers and legs and actuators
        each_lever() leg_and_lever_clearance(); //hole for the leg&lever
        each_lever() translate([0,nut_y,0]) nut_seat_void(h=actuator_h+actuator_travel);        
        // clearance for gears and motors
        each_lever() motor_and_small_gear_clearance();

        // hollow out space in the centre
        difference(){
            intersection(){
                rotate(30)cylinder(h = 999, r = casing_radius-wall_t, $fn = 3);
                cylinder(h = 999, r = casing_radius-wall_t, $fn = 6);
            }
            // make the objective mount by not hollowing it out
            if (optics_module_mount){
                rotate(60){
                    union(){
                        objective_mount();
                        translate([-stage_r/2,casing_apothem-17.5,0])cube([stage_r,17.5,casing_height]);
                    }
                }
            }
        }
        // bolt slot access slot
        if (optics_module_mount){
            objective_bolt_access();
        }

        if (reflection_illumination){
            fl_cube_cutout();
        }

        mirror([0,0,1]) cylinder(r=999, h=999, $fn=4); //ensure it doesn't go below the bottom

        //add logos to the side
        logos();
        // mounting holes (screw through from bottom)
        each_mounting_hole() {
            trylinder_selftap(nominal_d=3, h=40, center=true);
            translate([15, 5, 0]) trylinder_selftap(nominal_d=3, h=40, center=true);
            translate([-15, 5, 0]) trylinder_selftap(nominal_d=3, h=40, center=true);
        }       
    }
}
module objective_bolt_access(){
        rotate(60) hull(){
            translate([0, objective_mount_y+wall_t, z_flexures_z1+6]) rotate([-90,0,0]) cylinder(d=6.5,h=99);
            translate([0, objective_mount_y+wall_t, z_flexures_z2-5]) rotate([-90,0,0]) cylinder(d=6.5,h=99);
        }
}

module condenser_mount(){
    difference(){
        hull(){
            rotate(60) translate([0,0,7])hull()each_illumination_arm_screw() mirror([0,0,1]) cylinder(r=5,h=7);
            rotate(60)translate([0,stage_r,0.5])cube([stage_r/2,1,1], center = true);
        }
        // holes for mounting illumination arm
        rotate(60) translate([0,0,7])reflect([1,0,0]) right_illumination_arm_screw(){
            trylinder_selftap(3, h=16, center=true); 
            hull() rotate(110) repeat([100,0,0],2) translate([0,0,-6]) cylinder(d=6.9,h=2.8,$fn=6);
        }
        objective_bolt_access();
    }
}

module logos(){
    //The OSHW and OpenFlexure logos (goes on the side of the casing without the access holes)
    rotate(30)translate([casing_apothem+0.3,8,casing_height*0.15])rotate([90,0,-90])scale([0.2,0.2,1])oshw_logo_and_text(version_numstring);
    mirror([1,0,0])rotate(150)translate([casing_apothem+0.3,4,casing_height*0.35])rotate([90,0,-90])scale([0.2,0.2,1])openflexure_delta_stage_logo();
}

module legs(){
    each_lever(){
        leg();
        lever_flexures();
        lever();
        translate([0,nut_y,0]) actuator_column(actuator_h);
    } 
}

module base_mounting_points(){
// The supports attached to each leg that slot into the base.
    each_base_mounting_point(){
        difference(){
            union(){
                cylinder(d=8, h=6, $fn = 50);
                translate([0,0,4]){
                    hull(){
                        cylinder(d=8,h=2,$fn=50);
                        linear_extrude(5) projection()translate([0,nut_y+stage_r-mounting_point,0]) screw_seat(h=actuator_h);
                    }
                }
            }
            translate([0,0,4])cylinder(d = 6, h = 100, $fn=50);
            translate([0,0,-50])cylinder(d = 3.5, h = 100, $fn=50);
        }
    }
}

module main_body(){
    legs();
    moving_stage();
    casing();
    if (transmission_illumination) condenser_mount();
}

brim_radius = 0;

PART = "main_body_full";
if (PART == "main_body_full") main_body();
if (PART == "moving_stage") moving_stage();
if (PART == "legs_and_levers") legs();
// legs() one moving part at a time, i = 0, 1, 2 at rotate(i*120) as in each_lever(): the parallelogram leg, the
// lever with the flexures that hinge it to the casing (lever_flexures), and the actuator column on the lever's end
for (i = [0:2]) {
    if (PART == str("leg", i)) rotate(i*120) translate([0, stage_r, 0]) leg();
    if (PART == str("lever", i)) rotate(i*120) translate([0, stage_r, 0]) { lever(); lever_flexures(); }
    if (PART == str("column", i)) rotate(i*120) translate([0, stage_r + nut_y, 0]) actuator_column(actuator_h);
}
if (PART == "casing") { casing(); if (transmission_illumination) condenser_mount(); }


module thick_section(h, z=0, center=false){
    linear_extrude(h, center=center) projection(cut=true){
        translate([0,0,-z]) children();
    }
} 

// Best to put echo statements here, so they only happen once...
//echo("Radius of mounting holes is", mounting_hole_r);
