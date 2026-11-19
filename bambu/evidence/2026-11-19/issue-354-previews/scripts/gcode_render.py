import re, sys, math, numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.collections import LineCollection
gc, out = sys.argv[1], sys.argv[2]
segs=[]  # x0,y0,x1,y1,z,feat
x=y=z=0.0; feat="Custom"; started=False
fmap={}
num=re.compile(r'([XYZEIJ])(-?\d*\.?\d+)')
for line in open(gc):
    if line.startswith('; Z_HEIGHT'): started=True; z=float(line.split(':')[1]); continue
    if line.startswith('; FEATURE:'): feat=line.split(':',1)[1].strip(); continue
    if not started: continue
    if line.startswith(('G1 ','G0 ','G2 ','G3 ')):
        c=line.split(';')[0]; d={k:float(v) for k,v in num.findall(c)}
        nx,ny=d.get('X',x),d.get('Y',y)
        if 'Z' in d and 'X' not in d and 'Y' not in d: x,y=nx,ny; continue
        if d.get('E',0)>0 and feat not in ('Custom','Prime tower') and z<40:
            fi=fmap.setdefault(feat,len(fmap))
            if line[1] in '23' and 'I' in d:
                cx,cy=x+d['I'],y+d.get('J',0); r=math.hypot(x-cx,y-cy)
                a0=math.atan2(y-cy,x-cx); a1=math.atan2(ny-cy,nx-cx)
                if line[1]=='2':
                    if a1>=a0: a1-=2*math.pi
                else:
                    if a1<=a0: a1+=2*math.pi
                n=max(2,int(abs(a1-a0)*r/0.5))
                aa=np.linspace(a0,a1,n+1); px=cx+r*np.cos(aa); py=cy+r*np.sin(aa)
                for i in range(n): segs.append((px[i],py[i],px[i+1],py[i+1],z,fi))
            else: segs.append((x,y,nx,ny,z,fi))
        x,y=nx,ny
S=np.array(segs); inv={v:k for k,v in fmap.items()}
np.save(out+"_segs.npy",S); json.dump(inv,open(out+"_feat.json","w"))
print(len(S), fmap, "zmax", S[:,4].max())
