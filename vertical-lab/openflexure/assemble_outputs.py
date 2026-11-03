"""Collect the rendered OpenFlexure parts into /tmp/openflexure/out/{v7,delta}, apply the
delta-stage assembly transforms (derived from the .scad sources), decimate anything above
300k triangles (keeping the original) and write manifest.json."""
import json, os, shutil
import numpy as np
import trimesh

W = '/tmp/openflexure/work'
OUT = '/tmp/openflexure/out'
MAXTRI = 300_000

V7 = dict(repo='https://gitlab.com/openflexure/openflexure-microscope', tag='v7.0.0-beta5',
          commit='4828ffa5c4a115caa1970b71efdc32e3a05c09e1')
DS = dict(repo='https://gitlab.com/openflexure/openflexure-delta-stage', tag='v1.2.3',
          commit='d882d18b2c125441961c428bdd135490fab83792')
DS_OFM = dict(repo='https://gitlab.com/openflexure/openflexure-microscope',
              tag='(delta-stage submodule pin, v6.1.5 era)',
              commit='f57655b65f28bac6d160f7bfbd41fe63dd7e396b')
OSC = 'OpenSCAD 2026.11.01 nightly, --backend=manifold'

PLA_BODY, DARK, EXTRA = '#F5F5F5', '#404040', '#1E90FF'  # OpenFlexure render_settings.scad colours


def Rz(deg):
    a = np.radians(deg); c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.]])


def T(x, y, z):
    m = np.eye(4); m[:3, 3] = [x, y, z]; return m


def M3(rows, t=(0, 0, 0)):
    m = np.eye(4); m[:3, :3] = np.array(rows, float); m[:3, 3] = t; return m


manifest = {
    'units': 'mm', 'up_axis': '+z', 'handedness': 'right',
    'generated_with': OSC + '; python trimesh ' + trimesh.__version__,
    'instruments': {},
}


def bbox(m):
    return [[round(float(v), 3) for v in m.bounds[0]], [round(float(v), 3) for v in m.bounds[1]]]


def emit(inst, name, mesh, info):
    d = os.path.join(OUT, inst); os.makedirs(d, exist_ok=True)
    f = os.path.join(d, name + '.stl')
    mesh.export(f)
    entry = dict(file=f'{inst}/{name}.stl', triangles=int(len(mesh.faces)), bbox_mm=bbox(mesh), **info)
    if len(mesh.faces) > MAXTRI:
        shutil.move(f, os.path.join(d, name + '.full.stl'))
        target = int(MAXTRI * 0.8)
        red = mesh.simplify_quadric_decimation(face_count=target)
        red.export(f)
        entry.update(file_full_resolution=f'{inst}/{name}.full.stl', triangles_full=entry['triangles'],
                     triangles=int(len(red.faces)))
    manifest['instruments'][inst]['parts'][name] = entry
    print(f'{inst}/{name}: {entry["triangles"]} tris  bbox {entry["bbox_mm"]}')


# ------------------------------------------------------------------ v7
shutil.rmtree(OUT, ignore_errors=True)
manifest['instruments']['v7'] = dict(
    name='OpenFlexure Microscope v7, reflection (epi-) illumination, motorised, RMS optics',
    source=V7, parts={})
src_r = 'rendering/assemble_v7_reflection.scad (this work; uses rendering/*.scad + openscad/*.scad)'
Z_STAGE = ['x', 'y']
v7 = {
    # name: (colour, moves_with, source modules, notes)
    'stand': (DARK, [], 'rendering/prepare_stand.scad: render_stand -> openscad/libs/lib_microscope_stand.scad', 'microscope_stand.stl geometry (stand with electronics drawer bay)'),
    'main_body': (PLA_BODY, [], 'openscad/libs/main_body_structure.scad: main_body() via rendering/librender/rendered_main_body.scad', 'main_body.stl MINUS the xy_stage region, the four legs and the two XY actuator columns; contains the z-axis objective mount (the mount itself moves in z with the optics).'),
    'xy_stage': (PLA_BODY, Z_STAGE, 'main_body() INTERSECT hull(xy_stage()) slab z>=upper_xy_flex_z', 'moving XY stage platform cut out of the one-piece main body; top surface = sample plane'),
    'leg_x': (PLA_BODY, Z_STAGE, 'main_body() INTERSECT leg_region(actuated) in mirror([1,0,0]) leg_frame(45) (actuator_leg: leg + lever arm), less the stage', 'X actuator leg: parallelogram leg + horizontal arm to the X column; pivots on its bottom flexure'),
    'leg_y': (PLA_BODY, Z_STAGE, 'main_body() INTERSECT leg_region(actuated) in leg_frame(45) (actuator_leg: leg + lever arm), less the stage', 'Y actuator leg, as leg_x'),
    'leg_back_left': (PLA_BODY, Z_STAGE, 'main_body() INTERSECT leg_region() in leg_frame(135) (leg), less the stage', 'passive parallelogram leg'),
    'leg_back_right': (PLA_BODY, Z_STAGE, 'main_body() INTERSECT leg_region() in mirror([1,0,0]) leg_frame(135) (leg), less the stage', 'passive parallelogram leg'),
    'actuator_column_x': (PLA_BODY, Z_STAGE, 'main_body() INTERSECT column_region() at actuating_nut_r in the X leg frame (actuator_column)', 'X actuator column (nut trap, band hooks); moves up and down with the end of the X arm'),
    'actuator_column_y': (PLA_BODY, Z_STAGE, 'main_body() INTERSECT column_region() at actuating_nut_r in the Y leg frame (actuator_column)', 'Y actuator column'),
    'actuator_x': (EXTRA, [], 'rendering/actuator_assembly.scad: x_actuator_assembly', 'foot, viton band, M3x25 lead screw, large gear, washers, brass nut'),
    'actuator_y': (EXTRA, [], 'rendering/actuator_assembly.scad: y_actuator_assembly', 'as actuator_x'),
    'actuator_z': (EXTRA, [], 'rendering/actuator_assembly.scad: z_actuator_assembly', 'as actuator_x, tilted z actuator'),
    'motor_x': ('#C0C0C0', [], 'rendering/mount_motors.scad: mirror y_motor_and_cap', '28BYJ-48 motor, small gear, screws, side cable tidy'),
    'motor_y': ('#C0C0C0', [], 'rendering/mount_motors.scad: y_motor_and_cap', ''),
    'motor_z': ('#C0C0C0', [], 'rendering/mount_motors.scad: z_motor_and_cap(cap=true)', 'includes front cable tidy'),
    'optics_module_beamsplitter': (DARK, ['z'], 'openscad/libs/lib_optics.scad: optics_module_rms(rms_f50d13_config(beamsplitter=true)) = optics_picamera_2_rms_f50d13_beamsplitter.stl', 'focus (z) moves the whole optics stack'),
    'objective': ('#B8860B', ['z'], 'rendering/librender/optics.scad: rendered_objective', 'render model of a 45 mm parfocal RMS objective'),
    'tube_lens': ('#87CEEB', ['z'], 'rendering/librender/optics.scad: tube_lens', 'render model'),
    'picamera2_with_cover': ('#2E8B57', ['z'], 'rendering/rms_optics_assembly.scad: camera_and_screws', 'Pi camera v2 board + picamera_2_cover + 2 screws'),
    'camera_ribbon_cable': ('#D2B48C', ['z'], 'librender/electronics.scad: picamera_cable(curled_ribbon_pos())', 'render-only curled ribbon'),
    'fl_cube': (DARK, ['z'], 'openscad/fl_cube.scad (libs/lib_fl_cube.scad: fl_cube)', 'transform derived: translate([0,8,fl_cube_bottom]) rotate_x(90); fl_cube_bottom=-9.4 (main-body frame)'),
    'reflection_illuminator_holder': (DARK, ['z'], 'openscad/reflection_illuminator.scad: illuminator_holder()', 'transform derived: translate([0,-8,fl_cube_bottom+24.3]) rotate_x(180) (slip plate on top)'),
    'reflection_led_condenser': (DARK, ['z'], 'openscad/reflection_illuminator.scad: lens_holder()', 'transform derived: multmatrix [[-1,0,0,0],[0,0,1,-30.5],[0,1,0,fl_cube_bottom+10]]; y position is adjustable along the slip-plate slots (-45..-23)'),
    'led_star_placeholder': ('#FFD700', ['z'], 'placeholder (not OpenFlexure geometry)', '20 mm star LED board + emitter, on the back of lens_holder'),
    'sample_clips': (EXTRA, Z_STAGE, 'rendering/mount_sample_clips.scad: render_sample_clips', 'two clips + M3 screws, mounted on the stage'),
    'sample_slide_placeholder': ('#E0FFFF', Z_STAGE, 'placeholder (not OpenFlexure geometry)', '75x25x1 mm glass slide lying on the stage top, centred on the optical axis'),
    'electronics_drawer': (DARK, [], 'openscad/electronics_drawer.scad via mount_electronics.scad', ''),
    'raspberry_pi_4b': ('#228B22', [], 'rendering/prepare_pi_and_sangaboard.scad: pi_and_sd_card', 'render model'),
    'sangaboard_v0_5': ('#1F3F8F', [], 'rendering/electronics/sangaboard.scad (KiCad export)', 'render model; some source sub-meshes are not closed'),
    'hardware': ('#A9A9A9', [], 'rendering/librender/hardware.scad (+hardware.zip STLs)', 'nuts/screws: stand, stage, motor lugs, cable tidies, objective clamp, drawer, Pi/Sangaboard'),
}
for name, (col, moves, srcmod, note) in v7.items():
    m = trimesh.load(os.path.join(W, 'v7_parts', name + '.stl'), force='mesh')
    emit('v7', name, m, dict(colour=col, moves_with_stage=moves, source=dict(**V7, file=srcmod, assembly=src_r), notes=note,
                             placeholder='placeholder' in srcmod))
ref = os.path.join(OUT, 'v7', 'reference'); os.makedirs(ref)
shutil.copy(os.path.join(W, 'v7_parts', 'main_body_full.stl'), os.path.join(ref, 'main_body_one_piece.stl'))
manifest['instruments']['v7'].update(
    world_frame='OpenSCAD render frame of rendering/: stand bottom at z=0, optical axis at x=y=0; main-body frame = world + (0,0,75)',
    sample_plane_z=150.0, stage_top_surface_z=150.0,
    stage_notes='Stage top = main_body sample_z (75) + stand offset (75). Nominal focus of the 45 mm parfocal objective is this plane. A slide lies on the stage top (placeholder slide occupies z 150-151). Stage travel ~ +/-6 mm in x/y; focus moves the optics module (z) not the stage.',
    reference_files={'reference/main_body_one_piece.stl': 'main body as printed (main_body + xy_stage + legs + actuator columns); do not render together with them'},
    omitted='transmission illumination (illumination_dovetail, condenser) - not part of the reflection configuration; motor wires; band/assembly tools')

# ------------------------------------------------------------------ delta
manifest['instruments']['delta'] = dict(
    name='OpenFlexure Delta Stage, reflection illumination, Raspberry Pi + Sangaboard base',
    source=DS, microscope_submodule=DS_OFM, parts={})
ZB = 79.0          # main-body z=0 sits 2 mm below the base top (base_raspi_sangaboard.scad stage_connection)
B = T(0, 0, ZB) @ Rz(120)   # main body sits on the base rotated 120 deg so the illuminator exits through the base window (base_raspi_sangaboard.scad window_cubes rotate(-60))
OPT = B @ Rz(60)             # optics module: objective mount is rotate(60) in delta_stage.scad casing()
FCB = -9.5         # fl_cube_bottom echoed by optics.scad (delta_stage=true, beamsplitter=true)
R = np.eye(4)      # fl cube exits at 120 deg in the optics frame (fl_cube_rotation=-60); OPT's +60 brings it back to 180 deg in the main-body frame
cube_m = B @ R @ M3([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (0, 8, FCB))
holder_m = B @ R @ M3([[1, 0, 0], [0, -1, 0], [0, 0, -1]], (0, 0, FCB + 22.3))
cond_m = B @ R @ M3([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], (0, -30.5, FCB + 10))
PI = T(-28, 52.5, 7) @ Rz(-90)
SANGA = T(-28, 52.5, 7 + 15) @ Rz(-90)
N, H = os.path.join(W, 'delta_native'), os.path.join(W, 'delta_helpers')
mb = 'openscad/delta_stage.scad (-D transmission_illumination=true -D reflection_illumination=true -D stage_connectors=true, = delta_stage_microscope.stl)'
helper = 'byu-vcl work file v7 rendering/delta_helpers.scad (v7 render models, see report)'
delta = {
    # name: (files, matrix, colour, moves, source, notes)
    'base_raspi_sangaboard': ([f'{N}/base_raspi_sangaboard.stl'], np.eye(4), DARK, [], ('DS', 'openscad/base_raspi_sangaboard.scad'), 'base at z=0'),
    'casing': ([f'{N}/casing.stl'], B, PLA_BODY, [], ('DS', mb + ': casing() + condenser_mount()'), 'static part of the main body incl. objective mount; mesh not closed'),
    **{f'leg{i}': ([f'{N}/leg{i}.stl'], B, PLA_BODY, ['x', 'y', 'z'], ('DS', mb + f': legs() -> rotate({120 * i}) translate([0,stage_r,0]) leg()'), 'parallelogram leg: its foot hinges on the lever, its top on the stage') for i in range(3)},
    **{f'lever{i}': ([f'{N}/lever{i}.stl'], B, PLA_BODY, ['x', 'y', 'z'], ('DS', mb + f': legs() -> rotate({120 * i}) translate([0,stage_r,0]) {{lever(); lever_flexures();}}'), 'lever: pivots on lever_flexures at the casing; the actuator column lifts its far end') for i in range(3)},
    **{f'column{i}': ([f'{N}/column{i}.stl'], B, PLA_BODY, ['x', 'y', 'z'], ('DS', mb + f': legs() -> rotate({120 * i}) translate([0,stage_r+nut_y,0]) actuator_column(actuator_h)'), 'actuator column: the nut on the lead screw moves it up and down') for i in range(3)},
    'moving_stage': ([f'{N}/moving_stage.stl'], B, PLA_BODY, ['x', 'y', 'z'], ('DS', mb + ': moving_stage()'), 'top surface = sample plane'),
    'feet': ([f'{N}/feet_assembled.stl'], B, PLA_BODY, [], ('DS', 'openscad/feet.scad: foot(hover=2, lie_flat=false) at each actuator column'), ''),
    'optics_module_beamsplitter': ([f'{N}/optics_picamera2_rms_f50d13_beamsplitter_delta.stl'], OPT, DARK, [], ('OFM', 'openscad/optics.scad -D optics="rms_f50d13" -D camera="picamera_2" -D delta_stage=true -D beamsplitter=true (= optics_picamera2_rms_f50d13_beamsplitter_delta.stl)'), 'native frame = delta main-body frame rotated -60 deg (objective mount is rotate(60))'),
    'fl_cube': ([f'{N}/fl_cube.stl'], cube_m, DARK, [], ('OFM', 'openscad/fl_cube.scad'), 'transform derived from optics.scad optical_path_fl; exits towards the casing fl_cube_cutout (-y of main body)'),
    'reflection_illuminator_holder': ([f'{N}/illuminator_holder.stl'], holder_m, DARK, [], ('OFM', 'openscad/reflection_illuminator_LED_star.scad: illuminator_holder()'), 'flipped, slip plate on top'),
    'reflection_led_condenser': ([f'{N}/illuminator_lens_holder.stl'], cond_m, DARK, [], ('OFM', 'openscad/reflection_illuminator_LED_star.scad: lens_holder()'), 'adjustable along slip-plate slots'),
    'led_star_placeholder': ([f'{H}/led_star_local.stl'], cond_m, '#FFD700', [], ('PH', 'placeholder'), '20 mm star LED'),
    'objective': ([f'{H}/objective.stl'], OPT, '#B8860B', [], ('V7', helper + ': rendered_objective at shoulder z=30.1'), 'v7 render model'),
    'tube_lens': ([f'{H}/tube_lens.stl'], OPT, '#87CEEB', [], ('V7', helper + ': tube_lens at z=18.44 (optics.scad thin-lens calc)'), 'v7 render model'),
    'picamera2_with_cover': ([f'{H}/camera.stl'], OPT, '#2E8B57', [], ('V7', helper + ': camera_and_screws, PCB at z=-17.5, rot 90'), 'v7 render model; rotation inferred'),
    'motors_and_small_gears': ([f'{H}/motor_local.stl'] * 3, [B @ Rz(a) @ T(0, 72, 0) @ Rz(180) for a in (0, 120, 240)], '#C0C0C0', [], ('V7', helper + ': motor_with_gear in v7 lug geometry, raised 4.48 mm'), 'approximate placement; wires clipped'),
    'lead_screws_and_large_gears': ([f'{H}/lead_local.stl'] * 3, [B @ Rz(a) @ T(0, 72, 0) @ Rz(180) for a in (0, 120, 240)], EXTRA, [], ('V7', helper + ': lead_screw_assembly on column axis, raised 4.48 mm'), 'approximate placement'),
    'raspberry_pi_4b': ([f'{H}/pi_local.stl'], PI, '#228B22', [], ('V7', helper + ': pi_and_sd_card at base raspi_center'), 'approximate placement'),
    'sangaboard_v0_5': ([f'{H}/sanga_local.stl'], SANGA, '#1F3F8F', [], ('V7', helper + ': sangaboard_v0_5 stacked 15 mm above the Pi'), 'approximate placement'),
    'sample_clips': ([f'{N}/sample_clip_local.stl'] * 2, [T(27.05, 2.86, ZB + 75) @ Rz(90), T(-27.05, 2.86, ZB + 75) @ Rz(-90)], EXTRA, ['x', 'y', 'z'],
                     ('OFM', 'openscad/sample_clips.scad: sample_clip([0,20,-1], w=7, roc=7) (= sample_clips.stl)'),
                     'placement chosen here: the two stage screw holes on the x axis (+/-27.05, 2.86), clips pointing at the optical axis; the relaxed (unloaded) clip tip dips 1 mm below the stage top, i.e. it overlaps a slide until deflected'),
}
srcs = dict(DS=DS, OFM=DS_OFM, V7=V7, PH={})
for name, (files, mats, col, moves, (sk, sfile), note) in delta.items():
    mats = mats if isinstance(mats, list) else [mats]
    meshes = []
    for f, m in zip(files, mats):
        mm = trimesh.load(f, force='mesh'); mm.apply_transform(m); meshes.append(mm)
    mesh = trimesh.util.concatenate(meshes)
    emit('delta', name, mesh, dict(colour=col, moves_with_stage=moves, source=dict(**srcs[sk], file=sfile),
                                   transform_applied=[np.round(m, 6).tolist() for m in mats], notes=note,
                                   placeholder=sk == 'PH'))
slide = trimesh.creation.box(extents=(75, 25, 1)); slide.apply_translation((0, 0, ZB + 75 + 0.5))
emit('delta', 'sample_slide_placeholder', slide, dict(colour='#E0FFFF', moves_with_stage=['x', 'y', 'z'],
     source=dict(file='placeholder'), notes='75x25x1 mm slide on the stage top', placeholder=True))
ref = os.path.join(OUT, 'delta', 'reference'); os.makedirs(ref)
for f in ['main_body_full.stl']:
    m = trimesh.load(os.path.join(N, f), force='mesh'); m.apply_transform(B); m.export(os.path.join(ref, 'main_body_one_piece.stl'))
manifest['instruments']['delta'].update(
    world_frame='base bottom at z=0, optical axis at x=y=0; world = translate(0,0,79) * rotate_z(120) * delta main-body frame (stage_connection recess 2 mm below base top; 120 deg so the illuminator exits through the base window)',
    sample_plane_z=ZB + 75, stage_top_surface_z=ZB + 75,
    stage_notes='moving_stage top at main-body z=75 (flex_z2 + 5). The v6-era optics put the objective shoulder at z=30, so a 45 mm parfocal objective focuses on the stage top. The delta moves the stage (and sample) in x, y and z; optics, illuminator and camera are fixed.',
    reference_files={'reference/main_body_one_piece.stl': 'delta_stage_microscope main body as printed (= casing + legs + levers + columns + moving_stage); do not render together with them'},
    omitted='clip screws, petri-dish holders/risers, transmission condenser, motor wires, star-LED wiring')
for inst in manifest['instruments'].values():
    allb = np.array([p['bbox_mm'] for p in inst['parts'].values() if not p.get('placeholder')])
    inst['overall_bbox_mm'] = [allb[:, 0].min(0).round(2).tolist(), allb[:, 1].max(0).round(2).tolist()]
json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
print({k: v['overall_bbox_mm'] for k, v in manifest['instruments'].items()})
