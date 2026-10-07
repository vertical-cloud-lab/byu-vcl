"""Camera pose from the matched slot centres (plate frame, z = 0 at the plate top).
usage: pose.py <matches.npz> <image_width> <image_height> <out.json>
Intrinsics: Camera Module 3 Wide, f = 2.75 mm, 1.4 um pixels -> 1964.3 px at 4608 wide.
Principal point at the image centre. k1, k2 fitted from the grid itself.
"""
import sys, site, json
sys.path.append(site.getusersitepackages())
import cv2, numpy as np
m = np.load(sys.argv[1]); W, H = int(sys.argv[2]), int(sys.argv[3])
obj = m['obj'].astype(np.float32); P = m['P'].astype(np.float32)
f = 1964.3 * W / 4608.0
K = np.array([[f, 0, W / 2], [0, f, H / 2], [0, 0, 1]])
res = {}
for name, flags in [('pinhole', None), ('k1k2', cv2.CALIB_USE_INTRINSIC_GUESS | cv2.CALIB_FIX_PRINCIPAL_POINT |
                     cv2.CALIB_FIX_FOCAL_LENGTH | cv2.CALIB_ZERO_TANGENT_DIST | cv2.CALIB_FIX_K3)]:
    if flags is None:
        dist = np.zeros(5)
        ok, rvec, tvec = cv2.solvePnP(obj, P, K, dist, flags=cv2.SOLVEPNP_ITERATIVE)
        Kf = K
    else:
        rms, Kf, dist, rvecs, tvecs = cv2.calibrateCamera([obj], [P], (W, H), K.copy(), np.zeros(5), flags=flags)
        rvec, tvec = rvecs[0], tvecs[0]; dist = dist.ravel()
    proj, _ = cv2.projectPoints(obj, rvec, tvec, Kf, dist)
    err = np.hypot(*(proj[:, 0] - P).T)
    R, _ = cv2.Rodrigues(rvec); C = (-R.T @ tvec).ravel()
    axis = R.T @ np.array([0, 0, 1.0])
    tilt = np.degrees(np.arccos(-axis[2]))
    hit = C - axis * C[2] / axis[2]
    res[name] = dict(rms_px=float(np.sqrt((err**2).mean())), max_px=float(err.max()), C=C.tolist(),
                     axis=axis.tolist(), tilt_from_vertical_deg=float(tilt), aim_on_plate=hit[:2].tolist(),
                     dist=dist.tolist(), rvec=rvec.ravel().tolist(), tvec=tvec.ravel().tolist(), K=Kf.tolist())
    print(name, 'rms %.2f px max %.2f px' % (res[name]['rms_px'], res[name]['max_px']),
          'camera at (%.0f, %.0f, %.0f) mm' % tuple(C), 'tilt %.1f deg' % tilt,
          'aims at (%.0f, %.0f)' % tuple(hit[:2]), 'dist', np.round(dist[:2], 4))
json.dump(res, open(sys.argv[4], 'w'), indent=1)
