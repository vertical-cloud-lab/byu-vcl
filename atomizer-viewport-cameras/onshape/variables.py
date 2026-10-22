"""The machine dimensions that are guesses, as Onshape Variable Studio variables.

Each entry: name, value, unit, and where the value comes from. The descriptions go into Onshape with the variable,
so whoever measures the machine sees the source and the uncertainty next to the number they are replacing.
Coordinates are those of atomizer-training/viz3d/model.py (#255): x to the operator's right, y away from the
operator, z up from the floor, furnace axis at x = y = 0.
"""
from __future__ import annotations

# (name, value, unit, description)
VARIABLES: list[tuple[str, float, str, str]] = [
    # --- chamber (#255's model, scaled to the documented 1000 x 800 x 1600 envelope and 57 L)
    ("ch_front_y", -120, "mm", "Chamber front face, y. #255 model, +-15 mm."),
    ("ch_left_x", -115, "mm", "Chamber left face under the door, x. #255 model; the port centre is ~100 mm right of it (frames)."),
    ("ch_right_x", 230, "mm", "Where the chamber's half-round right end starts, x. #255 model, +-15 %."),
    ("ch_top_z", 1130, "mm", "Underside of the chamber's top plate, above the floor. #255 model; every absolute height scales with it."),
    ("ch_vert_z", 765, "mm", "Bottom of the chamber's vertical walls. #255 model."),
    # --- front view port: threaded port nut, glass, and AMAZEMET's push-on 12-sided LED cover with its cable pod
    ("fp_x", -15, "mm", "Front port centre x at the chamber face. Frames FDRTt68Vfvo 51:00, 2wMgeI-E7zw 10:00; +-25."),
    ("fp_z", 1035, "mm", "Front port centre height above the floor; ~95 below the chamber top. Frames as fp_x; +-40."),
    ("fp_tilt", 20, "deg", "Port axis above horizontal (it looks down at the plate). Inferred from the view through the port, DWH1CEygsTI 34:28; +-12 (weak). Measure with an inclinometer on the glass."),
    ("fp_yaw", 0, "deg", "Port axis turned towards the left (-x). Not measured."),
    ("fp_nut_d", 95, "mm", "Threaded port nut (hook-wrench ring) OD. 1F9_4ccwhss 7:58 (bare port); +-15. Looks like a DN50 dairy-fitting sight glass (nut ~92)."),
    ("fp_nut_face", 45, "mm", "Nut front face (the glass) out from the chamber face. Weak: cover face minus its overhang."),
    ("fp_glass_d", 63, "mm", "Clear glass diameter. FDRTt68Vfvo 51:00, 58wJ_Khwgyk 25:11, 1F9_4ccwhss 7:58; +-12."),
    ("fp_cover_sides", 12, "", "Sides of AMAZEMET's LED cover. Counted."),
    ("fp_cover_rot", 0, "deg", "Cover polygon rotation: a flat at this angle (0 puts flats at 3, 6, 9 and 12 o'clock)."),
    ("fp_cover_af", 162, "mm", "Cover across flats (168 across corners). FDRTt68Vfvo 51:00, 2wMgeI-E7zw 10:00; +-25."),
    ("fp_cover_face", 75, "mm", "Cover front face out from the chamber face. wRc8p2_FnJo 35:10, 1F9_4ccwhss 7:49; +-25 (weak)."),
    ("fp_cover_len", 45, "mm", "Cover depth along the axis. Guess."),
    ("fp_cover_open", 75, "mm", "Cover front opening diameter. 58wJ_Khwgyk 25:11; +-15."),
    ("fp_pod_angle", 270, "deg", "Cable pod position round the cover, 270 = 6 o'clock (where it has been since 30 Sep; 3 o'clock on 29 Sep). It turns with the cover."),
    ("fp_pod_w", 90, "mm", "Pod size along the cover's flat. FDRTt68Vfvo 51:00; +-30 %."),
    ("fp_pod_h", 45, "mm", "Pod size radially out from the flat. +-30 %."),
    ("fp_pod_depth", 55, "mm", "Pod size along the port axis. +-30 %."),
    ("fp_pod_setback", 5, "mm", "Pod front face behind the cover's front face. Guess."),
    # --- left door (hinged at its back edge) and its sight glass
    ("door_t", 16, "mm", "Chamber door thickness. #255 model."),
    ("door_w", 236, "mm", "Door width, front edge to back edge. #255 model, +-15 %."),
    ("door_z0", 775, "mm", "Door bottom height. #255 model."),
    ("door_z1", 1115, "mm", "Door top height. #255 model; the sight glass is ~90 below it (frames)."),
    ("door_hinge_y", 128, "mm", "Door hinge axis y: the BACK edge (58wJ_Khwgyk 24:54, 1F9_4ccwhss 7:49; all three swing bolts anchor at the front). #255 had it at the front."),
    ("door_open", 100, "deg", "How far the door opens. Guess."),
    ("lp_y", 20, "mm", "Door sight glass centre y: between the door's middle and its back edge. 58wJ_Khwgyk 77:00, 77:25; +-50 (weak)."),
    ("lp_z", 1015, "mm", "Door sight glass centre height, ~130 above the stack's entry. 9kn-HhXCr1o 25:06; +-50."),
    ("lp_ring_d", 65, "mm", "Sight glass ring / nut OD. 58wJ_Khwgyk 77:25; +-15. KF40 clamp or a small threaded sight glass: check."),
    ("lp_protrusion", 30, "mm", "Ring out from the door's outer face. 9kn-HhXCr1o 25:06 (profile); +-10."),
    ("lp_glass_d", 45, "mm", "Sight glass clear diameter. +-12."),
    ("stack_angle", 40, "deg", "Ultrasonic stack below horizontal, leaving the door. #255 (35-45 from frames)."),
    ("stack_z", 885, "mm", "Height where the stack's axis crosses the door's outer face (~130 below the sight glass)."),
    ("stack_d", 60, "mm", "Stack (transducer housing) outer diameter outside the door. Guess."),
    # --- furnace lid and its window (on the lid's front facet)
    ("furn_r", 135, "mm", "Furnace body radius: the scale reference for every frame measurement (+-10 %). #255 model."),
    ("furn_top_z", 1345, "mm", "Top of the furnace body, where the lid seats. #255 model."),
    ("lid_r", 137.5, "mm", "Lid skirt radius (round, ~275 across). DWH1CEygsTI 25:40; +-12."),
    ("lid_h1", 80, "mm", "Height of the lid's round skirt, up to where the six facets start. From lid_top_z, the facet angle and the window centre."),
    ("lid_top_z", 1500, "mm", "Top of the lid above the floor (lid ~150 above the body). wRc8p2_FnJo 35:10, 1F9_4ccwhss 5:16; +-60."),
    ("lid_facet_angle", 50, "deg", "Lid facets from horizontal; the window is on the front one. 9kn-HhXCr1o 20:04, DWH1CEygsTI 25:40; +-15 (weak)."),
    ("lid_hinge_x", -160, "mm", "Lid hinge pin x (on the left, axis along y). DWH1CEygsTI 25:40, 1F9_4ccwhss 5:05; +-20."),
    ("lid_hinge_z", 1345, "mm", "Lid hinge pin height, about the lid/body joint; +-30."),
    ("lid_open", 105, "deg", "Lid opening: up and over to the left, just past vertical. 1F9_4ccwhss 5:05, 2wMgeI-E7zw 10:00; +-10."),
    ("tw_x", 0, "mm", "Lid window centre x."),
    ("tw_z", 1455, "mm", "Lid window centre height (its y follows from the facet). +-60."),
    ("tw_wid", 60, "mm", "Window clear width. 58wJ_Khwgyk 58:06 (face-on), DWH1CEygsTI 25:40; +-12."),
    ("tw_len", 64, "mm", "Window clear length along the slope. As tw_wid; +-12."),
    ("tw_plate_w", 112, "mm", "Window frame plate width at its top screw row (8 hex-socket screws, ~M5). +-20."),
    ("tw_plate_l", 105, "mm", "Window frame plate length along the slope. +-20."),
    ("aim_z", 1240, "mm", "Height on the furnace axis the top camera aims at: the crucible datum (1219, #222/#255) plus ~20 mm of melt."),
    # --- blue frame
    ("fr_front_y", 165, "mm", "Blue frame (cabinet) front face, y. #255 model (depth inferred)."),
    ("fr_top_z", 1600, "mm", "Top of the blue frame (envelope 1600 H, O&MM). The top camera's magnetic base sits on it."),
    ("fr_x0", -115, "mm", "Blue frame left side, x. #255 model."),
    ("fr_x1", 630, "mm", "Blue frame right side, x. #255 model (745 W)."),
]


def onshape_payload(variables=VARIABLES) -> list[dict]:
    out = []
    for name, value, unit, desc in variables:
        kind = {"mm": "LENGTH", "deg": "ANGLE", "": "NUMBER"}[unit]
        expr = f"{value:g} {unit}".strip()
        out.append({"name": name, "type": kind, "expression": expr, "description": desc})
    return out
