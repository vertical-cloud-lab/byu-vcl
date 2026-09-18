import serial, time, subprocess, os, json
OUT="/tmp/zdiag3"; os.makedirs(OUT, exist_ok=True)
log=[]
def P(*a):
    t=" ".join(str(x) for x in a); print(t, flush=True); log.append(t)

s=serial.Serial("/dev/ttyUSB0",115200,timeout=1); time.sleep(2.0)
P("=== soft reset ===")
s.write(b"\x18"); time.sleep(2.5)
while s.in_waiting:
    l=s.readline().decode(errors="replace").strip()
    if l: P("  banner:", l)
s.reset_input_buffer()

def raw(cmd, wait=0.35):
    s.write((cmd+"\n").encode()); time.sleep(wait)
    o=[]
    while s.in_waiting:
        l=s.readline().decode(errors="replace").strip()
        if l: o.append(l)
        time.sleep(0.01)
    return o
def status():
    for _ in range(8):
        for l in raw("?",0.25):
            if l.startswith("<"): return l
    return "<none>"
def wait_idle(t=90):
    t0=time.time()
    while time.time()-t0<t:
        st=status()
        if st.startswith("<Idle") or st.startswith("<Alarm"): return st
        time.sleep(0.25)
    return status()
def shot(tag):
    for cam,w,h in (("0",1600,900),("1",1600,900)):
        f=f"{OUT}/{tag}_cam{cam}.jpg"
        try:
            subprocess.run(["rpicam-still","--camera",cam,"-n","-t","600","--width",str(w),
                            "--height",str(h),"-o",f],timeout=18,
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            P(f"   [cam{cam}] {tag} {os.path.getsize(f)}B")
        except Exception as e:
            P(f"   [cam{cam}] {tag} FAILED {type(e).__name__}")

P("=== version / state ===")
P("  $I:", raw("$I",0.6))
P("  status:", status())
P("  $X:", raw("$X",0.6))
P("  status:", status())

res={}
P("=== A. baseline frame ===")
shot("A_start"); res["A"]=status(); P("  ", res["A"])

P("=== B. X axis: 60mm toward origin @F1000 (safe direction) ===")
raw("G91",0.3)
t0=time.time(); P("  cmd:", raw("G01 X-60 F1000",0.3)); st=wait_idle()
P(f"  -> {st}  dt={time.time()-t0:.2f}s   (60mm @1000 = 3.6s of motion)")
res["B_x_out"]=st; shot("B_x_minus60")

P("=== C. X back ===")
t0=time.time(); raw("G01 X60 F1000",0.3); st=wait_idle()
P(f"  -> {st}  dt={time.time()-t0:.2f}s"); res["C_x_back"]=st
shot("C_x_back")

P("=== D. Y axis: 60mm toward origin @F1000 ===")
t0=time.time(); raw("G01 Y-60 F1000",0.3); st=wait_idle()
P(f"  -> {st}  dt={time.time()-t0:.2f}s"); res["D_y_out"]=st
shot("D_y_minus60")
t0=time.time(); raw("G01 Y60 F1000",0.3); st=wait_idle()
P(f"  -> {st}  dt={time.time()-t0:.2f}s"); res["D_y_back"]=st

P("=== E. Z axis: 30mm UP @F1000 (safe direction - away from the deck) ===")
t0=time.time(); P("  cmd:", raw("G01 Z30 F1000",0.3)); st=wait_idle()
P(f"  -> {st}  dt={time.time()-t0:.2f}s  Pn={st}"); res["E_z_up"]=st
shot("E_z_up30")

P("=== F. Z axis: 30mm back down @F1000 ===")
t0=time.time(); raw("G01 Z-30 F1000",0.3); st=wait_idle()
P(f"  -> {st}  dt={time.time()-t0:.2f}s"); res["F_z_down"]=st
shot("F_z_down30")
raw("G90",0.3)
P("=== final ==="); P("  ", status())
s.close()
open(f"{OUT}/motiontest.log","w").write("\n".join(log)+"\n")
json.dump(res, open(f"{OUT}/motiontest.json","w"), indent=1)
P("DONE")
