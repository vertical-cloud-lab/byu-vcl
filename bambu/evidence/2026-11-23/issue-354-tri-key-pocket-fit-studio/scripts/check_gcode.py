"""Check the sliced plate: settings from the CONFIG_BLOCK, tools and heaters used, and per key the
outer-wall extents (arcs included) + one line width: pill at z 12, nub below its lead-in, top z."""
import math, re, sys, json
g = open(sys.argv[1]).read().splitlines()
cfg = {}
for l in g:
    m = re.match(r'^; (\w+) = (.*)$', l)
    if m: cfg.setdefault(m.group(1), m.group(2))
keys = ['printer_settings_id', 'print_settings_id', 'filament_settings_id', 'nozzle_diameter', 'layer_height',
        'initial_layer_print_height', 'wall_loops', 'sparse_infill_density', 'sparse_infill_pattern', 'brim_type',
        'enable_support', 'curr_bed_type', 'elefant_foot_compensation', 'xy_contour_compensation', 'xy_hole_compensation',
        'enable_circle_compensation', 'outer_wall_line_width', 'nozzle_temperature', 'nozzle_temperature_initial_layer',
        'textured_plate_temp', 'textured_plate_temp_initial_layer', 'top_shell_layers', 'bottom_shell_layers',
        'enable_prime_tower', 'timelapse_type', 'filament_type', 'filament_colour', 'enable_arc_fitting', 'skirt_loops']
for k in keys: print(f'{k} = {cfg.get(k)}')
lw = float(cfg.get('outer_wall_line_width', '0.42').split(',')[0])
x = y = z = 0.0; feature = None; layer_z = None
tools, heats = set(), []
outer = {}   # layer z -> list of (x, y)
topz = {}    # key column/row -> max z with extrusion
ext_all = [1e9, -1e9, 1e9, -1e9]
for l in g:
    if l.startswith('; FEATURE:'): feature = l.split(':', 1)[1].strip(); continue
    if l.startswith('; Z_HEIGHT:'): layer_z = float(l.split(':')[1]); continue
    if l.startswith(';') or not l.strip(): continue
    c = l.split(';')[0].split()
    if not c: continue
    if re.match(r'^T\d+$', c[0]): tools.add(c[0])
    if c[0] in ('M104', 'M109', 'M140', 'M190'): heats.append(' '.join(c))
    if c[0] in ('G0', 'G1', 'G2', 'G3'):
        d = {a[0]: float(a[1:]) for a in c[1:] if a[0] in 'XYZEFIJ' and re.match(r'^-?[\d.]+$', a[1:])}
        nx, ny, nz = d.get('X', x), d.get('Y', y), d.get('Z', z)
        pts = [(nx, ny)]
        if c[0] in ('G2', 'G3') and ('I' in d or 'J' in d):
            cx, cy = x + d.get('I', 0.0), y + d.get('J', 0.0)
            r = math.hypot(x - cx, y - cy)
            a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
            if c[0] == 'G3':   # CCW
                while a1 <= a0: a1 += 2 * math.pi
            else:
                while a1 >= a0: a1 -= 2 * math.pi
            n = max(2, int(abs(a1 - a0) / math.radians(3)))
            pts = [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(1, n + 1)]
        if 'E' in d and d['E'] > 0 and feature not in (None, 'Custom') and (('X' in d) or ('Y' in d)):
            for px, py in [(x, y)] + pts:
                ext_all = [min(ext_all[0], px), max(ext_all[1], px), min(ext_all[2], py), max(ext_all[3], py)]
            if layer_z is not None:
                if feature == 'Outer wall':
                    outer.setdefault(round(layer_z, 2), []).extend([(x, y)] + pts)
        x, y, z = nx, ny, nz
print('tools', sorted(tools))
print('heat commands', sorted(set(heats)))
print('extrusion extents X %.2f..%.2f  Y %.2f..%.2f' % tuple(ext_all))
cxp, cyp = (ext_all[0] + ext_all[1]) / 2, (ext_all[2] + ext_all[3]) / 2
names = {(-1, -1): 'T row 1', (-1, 1): 'T row 2', (1, -1): 'V row 1', (1, 1): 'V row 2'}
def per_key(zk):
    out = {}
    for px, py in outer.get(zk, []):
        k = (1 if px > cxp else -1, 1 if py > cyp else -1)
        out.setdefault(k, []).append((px, py))
    return out
res = {}
for label, zz in (('pill (key z -3)', 12.0), ('nub, key z +0.4', 15.4), ('nub, key z +1.0', 16.0), ('nub, key z +1.4', 16.4)):
    zk = min(outer, key=lambda k: abs(k - zz))
    pk = per_key(zk)
    print(f'{label}: layer z {zk}')
    for k in sorted(pk):
        P = pk[k]
        xs = [p[0] for p in P]; ys = [p[1] for p in P]
        # nub: take only the outline near the key centre (|dx| < 4.5, |dy| < 5) at nub layers
        if zz > 15.1:
            mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        w = max(xs) - min(xs) + lw; L = max(ys) - min(ys) + lw
        print(f'   {names[k]}: x {min(xs):.2f}..{max(xs):.2f}  y {min(ys):.2f}..{max(ys):.2f}  -> {w:.3f} x {L:.3f} (incl. {lw} line width)')
        res.setdefault(names[k], {})[label] = [round(w, 3), round(L, 3)]
# top of each key
tops = {}
for zk, P in outer.items():
    for px, py in P:
        k = names[(1 if px > cxp else -1, 1 if py > cyp else -1)]
        tops[k] = max(tops.get(k, 0), zk)
print('top outer-wall layer per key:', dict(sorted(tops.items())))
print('max layer z', max(outer))
json.dump({'config': {k: cfg.get(k) for k in keys}, 'per_key': res, 'tops': tops}, open(sys.argv[2], 'w'), indent=1)
