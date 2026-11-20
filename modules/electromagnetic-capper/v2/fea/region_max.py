"""Peak principal strain/stress inside a box, from a CalculiX .frd (nodal values).
usage: region_max.py run.frd xmin ymin zmin xmax ymax zmax"""
import sys, numpy as np
def read(frd):
    blocks = {}; cur = None; nodes = {}; mode = None
    for line in open(frd):
        if line.startswith("    2C"): mode = "nodes"; continue
        if mode == "nodes":
            if line.startswith(" -1"):
                nid = int(line[3:13]); nodes[nid] = [float(line[13+12*i:25+12*i]) for i in range(3)]
                continue
            if line.startswith(" -3"): mode = None; continue
        if line.startswith(" -4"): cur = line.split()[1]; blocks[cur] = {}
        elif line.startswith(" -1") and cur:
            nid = int(line[3:13]); blocks[cur][nid] = [float(line[13+12*i:25+12*i]) for i in range((len(line.rstrip())-13)//12)]
        elif line.startswith(" -3"): cur = None
    return nodes, blocks
if __name__ == "__main__":
    nodes, b = read(sys.argv[1]); box = list(map(float, sys.argv[2:8]))
    E = b["TOSTRAIN"]; S = b["STRESS"]
    best = (0, None); bests = (0, None)
    for nid, e in E.items():
        x, y, z = nodes[nid]
        if not (box[0] <= x <= box[3] and box[1] <= y <= box[4] and box[2] <= z <= box[5]): continue
        T = np.array([[e[0], e[3], e[5]], [e[3], e[1], e[4]], [e[5], e[4], e[2]]])
        v = np.linalg.eigvalsh(T); m = max(abs(v[0]), abs(v[-1]))
        if m > best[0]: best = (m, (x, y, z))
        s = S[nid]; Ts = np.array([[s[0], s[3], s[5]], [s[3], s[1], s[4]], [s[5], s[4], s[2]]])
        vs = np.linalg.eigvalsh(Ts); ms = max(abs(vs[0]), abs(vs[-1]))
        if ms > bests[0]: bests = (ms, (x, y, z))
    print(f"max |principal strain| {best[0]*100:.2f} % at {np.round(best[1],2).tolist()};  max |principal stress| {bests[0]:.1f} MPa at {np.round(bests[1],2).tolist()}")
