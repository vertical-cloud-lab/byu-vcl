"""One STL with 4 bodies: T keys in the left column (-x), V keys in the right (+x), 2 rows (y)."""
import struct, sys
def read(f):
    b = open(f, 'rb').read()
    n = struct.unpack('<I', b[80:84])[0]
    assert len(b) == 84 + 50 * n, f
    return [struct.unpack('<12fH', b[84 + 50*i: 84 + 50*(i+1)]) for i in range(n)]
def bbox(tris):
    xs = [t[3+3*k] for t in tris for k in range(3)]; ys = [t[4+3*k] for t in tris for k in range(3)]; zs = [t[5+3*k] for t in tris for k in range(3)]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))
src = sys.argv[1]
names = ['tiprack', 'vialholder']
keys = {n: read(f'{src}/deck_clip_key_v2_1_tri_w10.4_{n}.stl') for n in names}
for n, t in keys.items():
    print(n, len(t), [tuple(round(v, 3) for v in r) for r in bbox(t)])
pitch_x, pitch_y = 22.0, 36.0
out, layout = [], []
for ci, n in enumerate(names):
    t = keys[n]
    (x0, x1), (y0, y1), (z0, z1) = bbox(t)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for ri in range(2):
        X = (ci - 0.5) * pitch_x; Y = (ri - 0.5) * pitch_y
        dx, dy, dz = X - cx, Y - cy, -z0
        layout.append((n, ri + 1, round(X, 2), round(Y, 2)))
        for tr in t:
            v = list(tr[3:12])
            for k in range(3):
                v[3*k] += dx; v[3*k+1] += dy; v[3*k+2] += dz
            out.append((*tr[0:3], *v, 0))
with open(sys.argv[2], 'wb') as fh:
    fh.write(b'issue-354 pocket-fit keys, 2 T + 2 V'.ljust(80, b' ')); fh.write(struct.pack('<I', len(out)))
    for tr in out: fh.write(struct.pack('<12fH', *tr))
print('wrote', sys.argv[2], len(out), 'triangles; bbox', [tuple(round(v, 2) for v in r) for r in bbox(out)])
for l in layout: print('key', *l)
