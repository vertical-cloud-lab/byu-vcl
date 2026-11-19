import numpy as np, json, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.collections import LineCollection
S=np.load("/tmp/pv/g_segs.npy"); F={int(k):v for k,v in json.load(open("/tmp/pv/g_feat.json")).items()}
P=json.load(open("/tmp/pv/Metadata/plate_1.json"))
od=sys.argv[1]
sup=[k for k,v in F.items() if v=='Support'][0]
walls=[k for k,v in F.items() if v in('Outer wall','Overhang wall')]
PART='#2b2b2b'; SUPC='#e8a33d'
names={"vial_rack_9x20mL_v2.stl":"vial rack (×1)","magnet_bar_v2_on_side.stl":"gantry bar, on its side (×1)","deck_clip_key_v2.stl":"deck key"}
# A: top view, whole plate
fig,ax=plt.subplots(figsize=(9,9.5))
m=S[:,5]!=sup
ax.add_collection(LineCollection(S[m][:,[0,1,2,3]].reshape(-1,2,2),colors=PART,linewidths=0.25,alpha=0.35))
ms=S[:,5]==sup
ax.add_collection(LineCollection(S[ms][:,[0,1,2,3]].reshape(-1,2,2),colors=SUPC,linewidths=0.3))
ax.plot([0,350,350,0,0],[0,0,320,320,0],color='#999',lw=1)
done=set()
for o in P['bbox_objects']:
    x0,y0,x1,y1=o['bbox']; n=o['name']
    ax.add_patch(plt.Rectangle((x0,y0),x1-x0,y1-y0,fill=False,ec='#3a7bd5',lw=0.8,ls='--'))
    if n=='deck_clip_key_v2.stl':
        if n in done: continue
        ax.annotate("deck keys (×4)",(140,150),(60,110),arrowprops=dict(arrowstyle='->',color='#3a7bd5'),color='#3a7bd5',fontsize=11)
    elif 'rack' in n: ax.text(205,160,names[n],rotation=90,va='center',color='#3a7bd5',fontsize=11)
    else: ax.text(35,280,names[n],color='#3a7bd5',fontsize=11)
    done.add(n)
ax.set_xlim(-5,355); ax.set_ylim(-5,325); ax.set_aspect('equal')
ax.set_title("H2D plate, top view of the G-code that was sent (all 175 layers)\nblack = part, orange = tree support; grey box = 350 × 320 bed",fontsize=11)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
fig.tight_layout(); fig.savefig(f"{od}/gcode_plate_top.png",dpi=130); plt.close(fig)

def view3d(fname, box, title, elev=28, azim=-60, kinds=None, every=1, lw=0.4):
    x0,x1,y0,y1=box
    m=(S[:,0]>=x0)&(S[:,0]<=x1)&(S[:,1]>=y0)&(S[:,1]<=y1)
    if kinds is not None: m&=np.isin(S[:,5],kinds+[sup])
    T=S[m]
    if every>1:
        keep=np.isin(np.round(T[:,4]/0.2).astype(int)%every,[0]) | (T[:,5]==sup)
        T=T[keep]
    fig=plt.figure(figsize=(10,7.5)); ax=fig.add_subplot(111,projection='3d')
    sm=T[:,5]==sup
    for mm,c,a in((~sm,PART,0.5),(sm,SUPC,0.6)):
        L=T[mm]
        if len(L)==0: continue
        segs=np.stack([L[:,[0,1,4]],L[:,[2,3,4]]],1)
        ax.add_collection3d(Line3DCollection(segs,colors=c,linewidths=lw,alpha=a))
    zmax=max(T[:,4].max(),1)
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_zlim(0,zmax)
    ax.set_box_aspect((x1-x0,y1-y0,zmax))
    ax.view_init(elev,azim); ax.set_title(title,fontsize=11)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    fig.tight_layout(); fig.savefig(f"{od}/{fname}",dpi=130); plt.close(fig)
view3d("gcode_plate_iso.png",(25,205,5,315),"Whole plate, 3D toolpath (outer walls + support)",kinds=walls,elev=30,azim=-50,lw=0.3)
view3d("gcode_rack_end_iso.png",(162,205,235,312),"Rack, last two cups (toolpath, outer walls every layer)",kinds=walls,elev=35,azim=-55,lw=0.5)
view3d("gcode_keys_iso.png",(110,166,145,187),"Deck keys ×4 (toolpath, all features)",elev=30,azim=-60,lw=0.5)
view3d("gcode_bar_iso.png",(28,168,284,312),"Gantry bar on its side, hooks at left, dovetail end with tree supports at right (toolpath)",elev=35,azim=-75,lw=0.4)
# Layer slices
def slice_(fname,box,zs,title):
    x0,x1,y0,y1=box
    fig,axs=plt.subplots(1,len(zs),figsize=(4.2*len(zs),4.6))
    for ax,zz in zip(axs,zs):
        m=(np.abs(S[:,4]-zz)<1e-3)&(S[:,0]>=x0)&(S[:,0]<=x1)&(S[:,1]>=y0)&(S[:,1]<=y1)
        L=S[m]; c=np.where(L[:,5]==sup,SUPC,PART)
        ax.add_collection(LineCollection(L[:,[0,1,2,3]].reshape(-1,2,2),colors=c,linewidths=0.6))
        ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.set_title(f"layer at Z = {zz:.1f} mm",fontsize=10)
        ax.tick_params(labelsize=7)
    fig.suptitle(title,fontsize=11); fig.tight_layout(); fig.savefig(f"{od}/{fname}",dpi=140); plt.close(fig)
slice_("gcode_rack_cup_slices.png",(164,203,272,311),[1.0,10.0,20.0,30.0],"Rack, end cup: G-code layers (floor → pedestal → seat → spring arms + rib)")
slice_("gcode_keys_slices.png",(110,168,145,187),[0.6,4.0,8.0,14.0],"Deck keys: G-code layers")
