import numpy as np, trimesh, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
d,od=sys.argv[1],sys.argv[2]
def shade(ax,m,color=(0.25,0.27,0.3),light=(0.4,-0.6,0.8)):
    n=m.face_normals; L=np.array(light)/np.linalg.norm(light)
    i=0.35+0.65*np.clip(n@L,0,1)
    cols=np.c_[np.outer(i,color),np.ones(len(i))]
    ax.add_collection3d(Poly3DCollection(m.triangles,facecolors=cols,edgecolors='none'))
    b=m.bounds; ax.set_xlim(b[0,0],b[1,0]); ax.set_ylim(b[0,1],b[1,1]); ax.set_zlim(b[0,2],b[1,2])
    ax.set_box_aspect(b[1]-b[0]); ax.set_axis_off()
def crop(m,lo,hi):
    for ax in range(3):
        if lo[ax] is not None: m=m.slice_plane([0,0,0] if False else np.eye(3)[ax]*lo[ax],np.eye(3)[ax],cap=True)
        if hi[ax] is not None: m=m.slice_plane(np.eye(3)[ax]*hi[ax],-np.eye(3)[ax],cap=True)
    return m
R=trimesh.load(f"{d}/vial_rack_9x20mL_v2.stl"); K=trimesh.load(f"{d}/deck_clip_key_v2.stl"); B=trimesh.load(f"{d}/magnet_bar_v2.stl")
for n,m in (("rack",R),("key",K),("bar",B)): print(n,m.bounds.round(2).tolist(),len(m.faces))
fig=plt.figure(figsize=(16,10))
ax=fig.add_subplot(2,2,1,projection='3d'); shade(ax,R); ax.view_init(30,-35); ax.set_title("Vial rack ×1 (whole, 297 mm long)")
c=crop(R,[None,-50,None],[None,17,None])
ax=fig.add_subplot(2,2,2,projection='3d'); shade(ax,c); ax.view_init(40,-60); ax.set_title("Rack close-up: cups 1–2, two spring arms + rigid rib per cup")
ax=fig.add_subplot(2,2,3,projection='3d'); shade(ax,K); ax.view_init(15,-40); ax.set_title("Deck clip key ×4: stem (top), locating pill, barbed latch arms")
ax=fig.add_subplot(2,2,4,projection='3d'); shade(ax,B); ax.view_init(25,-60); ax.set_title("Gantry bar ×1: two hook prongs, dovetail channel, pin hole")
fig.tight_layout(); fig.savefig(f"{od}/cad_parts_overview.png",dpi=120); plt.close(fig)
fig=plt.figure(figsize=(14,6.5))
for i,(e,a) in enumerate(((20,-30),(20,150),(-25,60))):
    ax=fig.add_subplot(1,3,i+1,projection='3d'); shade(ax,K); ax.view_init(e,a)
fig.suptitle("Deck clip key, three views (z = 0 is the deck top; stem goes up into the rack, latch below the deck)"); fig.tight_layout(); fig.savefig(f"{od}/cad_key_views.png",dpi=120); plt.close(fig)
fig=plt.figure(figsize=(16,6))
for i,(e,a) in enumerate(((25,-60),(25,120),(-30,-120))):
    ax=fig.add_subplot(1,3,i+1,projection='3d'); shade(ax,B); ax.view_init(e,a)
fig.suptitle("Gantry bar, three views (as mounted; it prints on its side)"); fig.tight_layout(); fig.savefig(f"{od}/cad_bar_views.png",dpi=120); plt.close(fig)
