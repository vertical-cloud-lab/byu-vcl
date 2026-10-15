import re, sys, glob, os, json
# YouTube auto-subs repeat lines in rolling pairs; keep one copy of each new line with its first cue start.
def parse(path):
    cues=[]; ts=None
    for line in open(path, encoding="utf-8"):
        line=line.rstrip("\n")
        m=re.match(r"(\d\d:\d\d:\d\d\.\d+) --> (\d\d:\d\d:\d\d\.\d+)", line)
        if m: ts=m.group(1); continue
        if not line.strip() or line.startswith(("WEBVTT","Kind:","Language:")) or ts is None: continue
        txt=re.sub(r"<[^>]+>","",line).replace("&nbsp;"," ").strip()
        if txt and (not cues or cues[-1][1]!=txt):
            cues.append((ts,txt))
    # drop lines that are the previous cue's second line repeated
    out=[]; seen=set()
    for ts,txt in cues:
        if txt in seen: continue
        seen.add(txt); out.append((ts,txt))
    return out
os.makedirs("/tmp/work/autosubs",exist_ok=True)
for p in sorted(glob.glob("/tmp/work/dl/*.en.vtt")):
    vid=os.path.basename(p).split(".")[0]
    cues=parse(p)
    with open(f"/tmp/work/autosubs/{vid}.txt","w") as f:
        for ts,txt in cues:
            h,m,s=ts.split(":"); f.write(f"[{int(h)*60+int(m):02d}:{int(float(s)):02d}] {txt}\n")
    print(vid, len(cues), "lines")
