import re, sys, math
g = open(sys.argv[1]).read().splitlines()
x = y = 0.0; feature = None; lz = None; outer = {}
def arcpts(x0, y0, x1, y1, i, j, cw, n=48):
    cx, cy = x0 + i, y0 + j; r = math.hypot(i, j)
    a0 = math.atan2(y0 - cy, x0 - cx); a1 = math.atan2(y1 - cy, x1 - cx)
    if cw:
        while a1 >= a0: a1 -= 2 * math.pi
    else:
        while a1 <= a0: a1 += 2 * math.pi
    if abs(x1 - x0) < 1e-9 and abs(y1 - y0) < 1e-9: a1 = a0 + (-2 * math.pi if cw else 2 * math.pi)
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
for l in g:
    if l.startswith('; FEATURE:'): feature = l.split(':', 1)[1].strip(); continue
    if l.startswith('; Z_HEIGHT:'): lz = round(float(l.split(':')[1]), 2); continue
    if l.startswith(';') or not l.strip(): continue
    c = l.split(';')[0].split()
    if c and c[0] in ('G0', 'G1', 'G2', 'G3'):
        d = {a[0]: float(a[1:]) for a in c[1:] if a[0] in 'XYZEIJ' and re.match(r'^-?[\d.]+$', a[1:])}
        nx, ny = d.get('X', x), d.get('Y', y)
        if 'E' in d and d['E'] > 0 and feature == 'Outer wall':
            if c[0] in ('G2', 'G3'):
                pts = arcpts(x, y, nx, ny, d.get('I', 0), d.get('J', 0), c[0] == 'G2')
            else:
                pts = [(x, y), (nx, ny)]
            outer.setdefault(lz, []).extend(pts)
        x, y = nx, ny
xs = [p[0] for v in outer.values() for p in v]; ys = [p[1] for v in outer.values() for p in v]
cx0, cy0 = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
names = ['w10.0', 'w10.2', 'w10.4', 'w10.5']
cent = [((ci - 1.5) * 22 + cx0, (ri - 0.5) * 36 + cy0, names[ci], ri + 1) for ci in range(4) for ri in range(2)]
print('outer-wall centreline extents incl. arcs; add the 0.42 mm line width for the outside of the part')
for zz in (0.2, 4.0, 12.0, 14.0, 15.4, 16.0, 16.6, 17.0):
    zk = min(outer, key=lambda k: abs(k - zz)); per = {}
    for p in outer[zk]:
        k = min(range(8), key=lambda i: (p[0] - cent[i][0]) ** 2 + (p[1] - cent[i][1]) ** 2)
        per.setdefault(k, []).append(p)
    row = []
    for k in range(8):
        pts = per.get(k, [])
        w = max(p[0] for p in pts) - min(p[0] for p in pts); L = max(p[1] for p in pts) - min(p[1] for p in pts)
        row.append(f'{cent[k][2]}#{cent[k][3]} {w + 0.42:.3f}x{L + 0.42:.3f}')
    print(f'z={zk:5.2f}:', ' | '.join(row))
