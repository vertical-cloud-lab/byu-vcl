"""Predict what camera 0 sees with the head at the deck origin, from its pose at home.
usage: origin_view.py <home_image> <pose.json> <labware.json> <out_dir> <tag> <occluder.json>
The camera rides on the head, so moving the head from home (361, 278) to (0, 0) moves
the camera by (-361, -278) mm with the same orientation (Z unchanged unless dz given).
"""
import sys, site, json
sys.path.append(site.getusersitepackages())
import cv2, numpy as np
img = cv2.imread(sys.argv[1]); H, W = img.shape[:2]
pose = json.load(open(sys.argv[2]))['k1k2']; lab = json.load(open(sys.argv[3]))
out, tag = sys.argv[4], sys.argv[5]
K = np.array(pose['K']); dist = np.array(pose['dist']); R, _ = cv2.Rodrigues(np.array(pose['rvec'])); C = np.array(pose['C'])
off = np.array([lab['offset_plate_minus_deck']['x_from_vials'], np.mean(lab['offset_plate_minus_deck']['y_vials_if_front_is_vial_1'])])
HOME = np.array([361.0, 278.0])
s = W / 2304.0
# head occluders (they move with the camera, so they stay put in the image): polygon in 2304x1296 px
occ = (np.array(json.load(open(sys.argv[6]))) * s).astype(np.int32)  # head parts, in 2304 x 1296 px
occ_mask = np.zeros((H, W), np.uint8); cv2.fillPoly(occ_mask, [occ], 1)
def project(pts3, Cc):
    t = -R @ Cc
    p, _ = cv2.projectPoints(np.asarray(pts3, np.float64).reshape(-1, 1, 3), cv2.Rodrigues(R)[0], t, K, dist)
    p = p.reshape(-1, 2)
    # points behind the camera or far outside the lens' field are invalid
    cam = (R @ (np.asarray(pts3) - Cc).T).T
    ang = np.degrees(np.arctan2(np.hypot(cam[:, 0], cam[:, 1]), cam[:, 2]))
    p[(cam[:, 2] <= 0) | (ang > 62)] = np.nan
    return p
def visible(pts2, Cc, z=0.0):
    p = project(np.c_[pts2, np.full(len(pts2), z)], Cc)
    ok = np.isfinite(p).all(1) & (p[:, 0] >= 0) & (p[:, 0] < W) & (p[:, 1] >= 0) & (p[:, 1] < H)
    occl = np.zeros(len(p), bool)
    pi = np.where(ok)[0]
    occl[pi] = occ_mask[p[pi, 1].astype(int), p[pi, 0].astype(int)] > 0
    return ok, occl
gx, gy = np.meshgrid(np.arange(0, 480.1, 2.5), np.arange(0, 490.1, 2.5))
plate = np.c_[gx.ravel(), gy.ravel()]
wa0 = off; wa1 = off + HOME
inwa = (plate[:, 0] >= wa0[0]) & (plate[:, 0] <= wa1[0]) & (plate[:, 1] >= wa0[1]) & (plate[:, 1] <= wa1[1])
cases = {'home': np.zeros(3), 'origin': np.r_[-HOME, 0.0], 'origin_z0': np.r_[-HOME, -122.0]}
res = dict(camera_plate_xyz_at_home=C.tolist(), deck_origin_in_plate=off.tolist(),
           camera_offset_from_capper_deck_xy=(C[:2] - off - HOME).tolist())
for name, d in cases.items():
    Cc = C + d
    ok, occl = visible(plate, Cc)
    v = ok & ~occl
    rows = plate[v]
    res[name] = dict(camera_plate_xyz=Cc.tolist(), plate_in_frame_pct=float(100 * ok.mean()), plate_visible_pct=float(100 * v.mean()),
                     workarea_in_frame_pct=float(100 * ok[inwa].mean()), workarea_visible_pct=float(100 * v[inwa].mean()),
                     plate_y_max_in_frame=float(plate[ok][:, 1].max()) if ok.any() else None,
                     plate_y_max_visible=float(rows[:, 1].max()) if len(rows) else None)
    np.save(f'{out}/{tag}_{name}_vis.npy', np.c_[plate, ok, occl])
    print(name, json.dumps({k: (round(v_, 1) if isinstance(v_, float) else v_) for k, v_ in res[name].items() if k != 'camera_plate_xyz'}))
# how much higher would the camera need to be for the plate / the work area to fit at the origin?
for target, mask in [('plate', np.ones(len(plate), bool)), ('workarea', inwa)]:
    for dz in range(0, 1001, 10):
        ok, occl = visible(plate[mask], C + np.r_[-HOME, dz])
        if ok.all():
            res[f'raise_needed_for_{target}_in_frame_mm'] = dz; print(target, 'fits in frame at origin if raised', dz, 'mm'); break
    else:
        res[f'raise_needed_for_{target}_in_frame_mm'] = None; print(target, 'does not fit within +1 m')
json.dump(res, open(f'{out}/{tag}_origin.json', 'w'), indent=1)
# predicted picture from the origin: warp the plate (z = 0) from the home view, keep the head occluders
def H_plane(Cc):
    t = -R @ Cc
    return K @ np.c_[R[:, 0], R[:, 1], t]
und = cv2.undistort(img, K, dist)
Hh, Ho = H_plane(C), H_plane(C + np.r_[-HOME, 0.0])
plate_mask = np.zeros((H, W), np.uint8)
corners = np.array([[0, 0], [480, 0], [480, 490], [0, 490]], np.float64)
cv2.fillPoly(plate_mask, [cv2.perspectiveTransform(corners[None], Hh)[0].astype(np.int32)], 255)
M = Ho @ np.linalg.inv(Hh)
warped = cv2.warpPerspective(und, M, (W, H), borderValue=(40, 40, 40))
wmask = cv2.warpPerspective(plate_mask, M, (W, H))
pred = np.full_like(img, 40); pred[wmask > 0] = warped[wmask > 0]
# working area outline at the origin
wa = np.array([[wa0[0], wa0[1]], [wa1[0], wa0[1]], [wa1[0], wa1[1]], [wa0[0], wa1[1]]], np.float64)
# re-distort for display: map the undistorted prediction back through the lens model
mapx, mapy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
pts = cv2.undistortPoints(np.c_[mapx.ravel(), mapy.ravel()].reshape(-1, 1, 2).astype(np.float64), K, dist, P=K).reshape(H, W, 2).astype(np.float32)
pred_d = cv2.remap(pred, pts[..., 0], pts[..., 1], cv2.INTER_LINEAR, borderValue=(40, 40, 40))
head = img.copy(); pred_d[occ_mask > 0] = head[occ_mask > 0]
for nm, Cc, im in [('home', C, img.copy()), ('origin', C + np.r_[-HOME, 0.0], pred_d)]:
    po = project(np.c_[corners, np.zeros(4)], Cc); pw = project(np.c_[wa, np.zeros(4)], Cc)
    for poly, col in [(po, (0, 255, 255)), (pw, (255, 120, 0))]:
        if np.isfinite(poly).all():
            cv2.polylines(im, [poly.astype(np.int32)], True, col, int(4 * s))
    cv2.polylines(im, [occ], True, (0, 0, 255), int(3 * s))
    cv2.imwrite(f'{out}/{tag}_{nm}_overlay.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 88])
