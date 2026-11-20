import re, sys, json
g = open(sys.argv[1]).read().splitlines()
cfg = {}
for l in g:
    m = re.match(r'^; (\w+) = (.*)$', l)
    if m: cfg.setdefault(m.group(1), m.group(2))
keys = ['printer_settings_id','print_settings_id','filament_settings_id','nozzle_diameter','layer_height','initial_layer_print_height',
        'wall_loops','sparse_infill_density','sparse_infill_pattern','brim_type','enable_support','curr_bed_type','elefant_foot_compensation',
        'nozzle_temperature','nozzle_temperature_initial_layer','textured_plate_temp','textured_plate_temp_initial_layer','top_shell_layers','bottom_shell_layers',
        'xy_contour_compensation','xy_hole_compensation','enable_prime_tower','timelapse_type','print_sequence','filament_type','filament_colour','default_filament_colour']
for k in keys: print(f'{k} = {cfg.get(k)}')
# Walk moves; record extrusion extents and per-layer outer-wall points
x = y = z = e = 0.0; rel_e = True; feature = None; layer_z = None
ext = [1e9, -1e9, 1e9, -1e9]; zmax = 0
tools = set(); heats = []
outer = {}  # z -> list of (x,y)
for l in g:
    if l.startswith('; FEATURE:'): feature = l.split(':',1)[1].strip(); continue
    if l.startswith('; Z_HEIGHT:'): layer_z = float(l.split(':')[1]); continue
    if l.startswith(';') or not l.strip(): continue
    c = l.split(';')[0].split()
    if not c: continue
    if re.match(r'^T\d+$', c[0]): tools.add(c[0])
    if c[0] in ('M104','M109','M140','M190'): heats.append(' '.join(c))
    if c[0] == 'M83': rel_e = True
    if c[0] == 'M82': rel_e = False
    if c[0] in ('G0','G1','G2','G3'):
        d = {a[0]: float(a[1:]) for a in c[1:] if a[0] in 'XYZEF' and re.match(r'^-?[\d.]+$', a[1:])}
        nx, ny, nz = d.get('X', x), d.get('Y', y), d.get('Z', z)
        if 'E' in d and d['E'] > 0 and ('X' in d or 'Y' in d) and feature not in (None, 'Custom'):
            ext = [min(ext[0], x, nx), max(ext[1], x, nx), min(ext[2], y, ny), max(ext[3], y, ny)]
            zmax = max(zmax, nz)
            if feature == 'Outer wall' and layer_z is not None:
                outer.setdefault(round(layer_z, 2), []).append((nx, ny))
        x, y, z = nx, ny, nz
print('tools', sorted(tools))
print('heat commands', sorted(set(heats)))
print('extrusion extents X %.2f..%.2f  Y %.2f..%.2f  top Z %.2f' % (*ext, zmax))
# Pill widths from the outer wall at z ~ 12, per key cluster (cluster by x)
def clusters(pts, gap=5.0):
    pts = sorted(pts); out = []; cur = [pts[0]]
    for p in pts[1:]:
        if p[0] - cur[-1][0] > gap: out.append(cur); cur = [p]
        else: cur.append(p)
    out.append(cur); return out
res = {}
for zz in (0.2, 4.0, 12.0, 14.0, 16.2, 17.0):
    zk = min(outer, key=lambda k: abs(k - zz))
    pts = outer[zk]
    cols = clusters(pts)
    row = []
    for col in cols:
        # split each column into 2 keys by y
        ys = sorted(col, key=lambda p: p[1])
        mid = (ys[0][1] + ys[-1][1]) / 2
        for half in ([p for p in col if p[1] < mid], [p for p in col if p[1] >= mid]):
            if half:
                w = max(p[0] for p in half) - min(p[0] for p in half); L = max(p[1] for p in half) - min(p[1] for p in half)
                row.append((round(min(p[0] for p in half),2), round(w, 3), round(L, 3)))
    res[zk] = row
    print(f'z={zk}: outer-wall centreline width x length per key (x0, w, L):', row)
