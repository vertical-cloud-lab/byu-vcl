import sys, site
sys.path.append(site.getusersitepackages())
import trimesh, numpy as np, collections
import shapely.geometry as sg
stl, outdir = sys.argv[1], sys.argv[2]
m = trimesh.load(stl)
print('bounds', m.bounds.round(3).tolist(), 'extents', m.extents.round(3), 'watertight', m.is_watertight)
thin = int(np.argmin(m.extents)); print('thin axis', thin)
mid = m.bounds.mean(axis=0)
normal = np.zeros(3); normal[thin] = 1
sec = m.section(plane_origin=mid, plane_normal=normal)
axes = [i for i in range(3) if i != thin]
polys = [sg.Polygon(np.array(s)[:, axes]) for s in sec.discrete if len(s) > 3]
polys.sort(key=lambda p: -p.area)
outer, holes = polys[0], polys[1:]
print('outer bounds', np.round(outer.bounds, 3), 'n holes', len(holes))
cs = []; sizes = collections.Counter()
for h in holes:
    x0, y0, x1, y1 = h.bounds
    cs.append(((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0))
    sizes[(round(x1 - x0, 2), round(y1 - y0, 2))] += 1
cs = np.array(cs)
print('hole sizes', sizes.most_common(10))
ux = np.unique(np.round(cs[:, 0], 2)); uy = np.unique(np.round(cs[:, 1], 2))
print('unique x', len(ux), ux.tolist()); print('unique y', len(uy), uy.tolist())
np.save(f'{outdir}/holes.npy', cs); np.save(f'{outdir}/outer.npy', np.array(outer.exterior.coords))
