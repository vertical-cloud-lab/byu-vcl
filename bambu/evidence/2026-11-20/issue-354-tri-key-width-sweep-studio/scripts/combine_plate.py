import struct, sys
def read(f):
    b = open(f, 'rb').read()
    n = struct.unpack('<I', b[80:84])[0]
    assert len(b) == 84 + 50 * n, f
    tris = [struct.unpack('<12fH', b[84 + 50*i: 84 + 50*(i+1)]) for i in range(n)]
    return tris
def bbox(tris):
    xs = [t[3+3*k] for t in tris for k in range(3)]; ys = [t[4+3*k] for t in tris for k in range(3)]; zs = [t[5+3*k] for t in tris for k in range(3)]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))
names = ['w10.0_c0.5', 'w10.2_c0.3', 'w10.4_c0.1', 'w10.5_c0.0']
keys = {n: read(f'/tmp/keys/deck_clip_key_v2_1_tri_{n}.stl') for n in names}
for n, t in keys.items():
    print(n, len(t), [tuple(round(v, 3) for v in r) for r in bbox(t)])
# Grid: columns = widths (x), rows = 2 copies (y). Each key is centred at its own bbox centre.
pitch_x, pitch_y = 22.0, 36.0
out = []
layout = []
for ci, n in enumerate(names):
    t = keys[n]
    (x0, x1), (y0, y1), (z0, z1) = bbox(t)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for ri in range(2):
        X = (ci - 1.5) * pitch_x; Y = (ri - 0.5) * pitch_y
        dx, dy, dz = X - cx, Y - cy, -z0
        layout.append((n, ri + 1, round(X, 2), round(Y, 2)))
        for tr in t:
            nrm = tr[0:3]; v = list(tr[3:12])
            for k in range(3):
                v[3*k] += dx; v[3*k+1] += dy; v[3*k+2] += dz
            out.append((*nrm, *v, 0))
hdr = b'issue-354 tri keys width sweep x2'.ljust(80, b' ')
with open(sys.argv[1], 'wb') as fh:
    fh.write(hdr); fh.write(struct.pack('<I', len(out)))
    for tr in out: fh.write(struct.pack('<12fH', *tr))
print('wrote', sys.argv[1], len(out), 'triangles')
print('bbox', [tuple(round(v, 2) for v in r) for r in bbox(out)])
for l in layout: print('key', *l)
