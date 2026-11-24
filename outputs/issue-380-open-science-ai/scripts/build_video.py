#!/usr/bin/env python3
"""Render every scene at its narration length, mux narration, and join into one MP4 with chapters.
Usage: python build_video.py [--render] [--mux] [--join]  (default: all three)"""
import json, subprocess, sys, os, concurrent.futures as cf
NARR = os.environ.get("NARR", "video/narration.json"); DURF = os.environ.get("DURF", "video/durations.json"); OUTMP4 = os.environ.get("OUTMP4", "video/open_science_value_ai.mp4"); CHAP = os.environ.get("CHAP", "video/chapters.txt")
N = json.load(open(NARR)); D = json.load(open(DURF))
MOD = {}
for m, names in [("scenes_data", ["coss_vc", "oss_value", "open_science_value", "epoch_sector", "openalex", "compute_gap", "language"]),
                 ("scenes_companies", ["kinds", "values", "relicense", "lanes_software", "lanes_hardware", "lanes_science", "lanes_ai", "ai_values", "stocks"]),
                 ("scenes_cards", ["title", "quotes", "dal", "takeaways", "end", "gh_threads"]),
                 ("scenes_part3", ["p3_title", "p3_forks", "p3_aiera", "p3_models", "p3_academic", "p3_agents", "p3_takeaways", "p3_end"]),
                 ("scenes_part2", ["p2_title", "p2_time", "p2_pdb", "p2_commons", "p2_language", "p2_igraph", "p2_am", "p2_dal", "p2_takeaways", "p2_end"])]:
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
    with open("video/av/list.txt", "w") as f:  # noqa
        for x in N: f.write(f"file '{x['scene']}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "video/av/list.txt", "-c", "copy", "-movflags", "+faststart",
                    OUTMP4], check=True)
    t = 0; chapters = []
    titles = {"title": "Intro", "oss_value": "What open-source software is worth", "open_science_value": "Open science: PDB, genome, open hardware",
              "values": "Where the money went in commercial open source", "relicense": "Licences move both ways", "lanes_software": "Openness over time: software",
              "stocks": "Open-source-origin stocks vs closed peers", "lanes_hardware": "Openness over time: hardware", "lanes_science": "Physical-science infrastructure",
              "ai_values": "Frontier AI: value sits with closed weights", "lanes_ai": "Big Tech and AI labs over time", "epoch_sector": "Who releases model weights",
              "compute_gap": "The compute gap", "openalex": "Open-access papers by sector", "language": "How the labs talk about open",
              "quotes": "In their own words", "gh_threads": "Our own GitHub threads", "dal": "DAL and the vertical cloud lab (#318)",
              "takeaways": "Takeaways", "end": "Data and sources", "coss_vc": "Venture data: open vs closed startups", "kinds": "Who opens, who closes",
              "p2_title": "Intro", "p2_time": "Openness over time, by sector", "p2_pdb": "Fifty years of open data: the PDB", "p2_commons": "The open-science commons under strain",
              "p2_language": "From open to science: how the labs talk", "p2_igraph": "US open source: growth and licences", "p2_am": "Closed instruments, fragile makers",
              "p2_dal": "A closer audit of DAL and #318", "p2_takeaways": "What Part 2 adds", "p2_end": "Data and sources",
              "p3_title": "Intro", "p3_forks": "Do forks survive closing moves?", "p3_aiera": "AI-era open-source startups", "p3_models": "AI-for-science models: licences over time",
              "p3_academic": "The academic path", "p3_agents": "Agents write our open record", "p3_takeaways": "What Part 3 adds", "p3_end": "Data and sources"}
    for x in N:
        m, sec = divmod(int(t), 60); chapters.append(f"{m}:{sec:02d} {titles.get(x['scene'], x['scene'])}"); t += vdur(x["scene"])
    open(CHAP, "w").write("\n".join(chapters) + "\n")
    print("total seconds", round(t, 1)); print("\n".join(chapters))
