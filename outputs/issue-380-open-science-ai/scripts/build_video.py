#!/usr/bin/env python3
"""Render every scene at its narration length, mux narration, and join into one MP4 with chapters.
Usage: python build_video.py [--render] [--mux] [--join]  (default: all three)"""
import json, subprocess, sys, os, concurrent.futures as cf
N = json.load(open("video/narration.json")); D = json.load(open("video/durations.json"))
MOD = {}
for m, names in [("scenes_data", ["coss_vc", "oss_value", "open_science_value", "epoch_sector", "openalex", "compute_gap", "language"]),
                 ("scenes_companies", ["kinds", "values", "relicense", "lanes_software", "lanes_hardware", "lanes_science", "lanes_ai", "ai_values", "stocks"]),
                 ("scenes_cards", ["title", "quotes", "dal", "takeaways", "end", "gh_threads"])]:
    for n in names: MOD[n] = m
LEAD, TAIL = 0.5, 1.0
steps = set(a.strip("-") for a in sys.argv[1:]) or {"render", "mux", "join"}
os.makedirs("video/av", exist_ok=True)
def vdur(s): return round(D[s] + LEAD + TAIL, 2)
def render(s):
    r = subprocess.run(["python3", f"scripts/{MOD[s]}.py", s, str(vdur(s))], capture_output=True, text=True)
    return s, r.returncode, r.stderr[-300:]
if "render" in steps:
    only = [t for t in os.environ.get("SCENES", "").split(",") if t]
    todo = [x["scene"] for x in N if x["scene"] in D and (not only or x["scene"] in only)]
    with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "4"))) as ex:
        for s, rc, err in ex.map(render, todo):
            print("render", s, "ok" if rc == 0 else f"FAIL {err}", flush=True)
if "mux" in steps:
    for x in N:
        s = x["scene"]; d = vdur(s)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", f"video/scenes/{s}.mp4", "-i", f"video/audio/{s}.wav",
               "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.35,fade=t=out:st={d-0.45}:d=0.45[v];[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{d}[a]",
               "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "24",
               "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-t", str(d), f"video/av/{s}.mp4"]
        r = subprocess.run(cmd, capture_output=True, text=True); print("mux", s, "ok" if r.returncode == 0 else r.stderr[-300:], flush=True)
if "join" in steps:
    with open("video/av/list.txt", "w") as f:
        for x in N: f.write(f"file '{x['scene']}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "video/av/list.txt", "-c", "copy", "-movflags", "+faststart",
                    "video/open_science_value_ai.mp4"], check=True)
    t = 0; chapters = []
    titles = {"title": "Intro", "oss_value": "What open-source software is worth", "open_science_value": "Open science: PDB, genome, open hardware",
              "values": "Where the money went in commercial open source", "relicense": "Licences move both ways", "lanes_software": "Openness over time: software",
              "stocks": "Open-source-origin stocks vs closed peers", "lanes_hardware": "Openness over time: hardware", "lanes_science": "Physical-science infrastructure",
              "ai_values": "Frontier AI: value sits with closed weights", "lanes_ai": "Big Tech and AI labs over time", "epoch_sector": "Who releases model weights",
              "compute_gap": "The compute gap", "openalex": "Open-access papers by sector", "language": "How the labs talk about open",
              "quotes": "In their own words", "gh_threads": "Our own GitHub threads", "dal": "DAL and the vertical cloud lab (#318)",
              "takeaways": "Takeaways", "end": "Data and sources", "coss_vc": "Venture data: open vs closed startups", "kinds": "Who opens, who closes"}
    for x in N:
        m, sec = divmod(int(t), 60); chapters.append(f"{m}:{sec:02d} {titles.get(x['scene'], x['scene'])}"); t += vdur(x["scene"])
    open("video/chapters.txt", "w").write("\n".join(chapters) + "\n")
    print("total seconds", round(t, 1)); print("\n".join(chapters))
