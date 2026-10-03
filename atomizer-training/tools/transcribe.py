import json, os, subprocess, sys, time
import numpy as np
from faster_whisper import WhisperModel, BatchedInferencePipeline
PRIORITY = ["u-KjR5TENN4","f8KL31PN8bA","LSQmxwmlTkQ","naePD8o9_Gk","9kn-HhXCr1o","58wJ_Khwgyk","txH397FGTAU","FDRTt68Vfvo","1F9_4ccwhss","HTlUrAr5HVU","Pk0K5sBz-sQ","tfb4fsVNIFI","TFpU4uqVF9c","of5-LhkX_VQ","qYyT39D5Yzo","2wMgeI-E7zw","QXSj0j1OqL8","z6rwmQW_3Vg","07QOPRHIEvw","Kv9DT3Vo0GE","cKwQbKdE22Q","w02MRlZhpNk","prj_xgeuQtM","BxA7Z9Fliss","dXRB7c6GeDw","wRc8p2_FnJo"]
DL="/tmp/work/dl"; OUT="/tmp/work/transcripts"
REMOTE=os.environ["RPI_STREAM_CAM_USERNAME"]+"@"+os.environ["RPI_STREAM_CAM_HOSTNAME"]+":atomizer-dl/"
def load(path):
    raw = subprocess.run(["ffmpeg","-v","error","-i",path,"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw, np.float32)
def fmt(t):
    h=int(t//3600); m=int(t%3600//60); s=t%60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".",",")
model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=4)
pipe = BatchedInferencePipeline(model=model)
pending = list(PRIORITY)
for attempt in range(3):
    still = []
    for vid in pending:
        m4a = f"{DL}/{vid}.m4a"
        if os.path.exists(f"{OUT}/{vid}.json"): continue
        if not os.path.exists(m4a):
            subprocess.run(["rsync","-aq","--bwlimit=3000",REMOTE+vid+".m4a",DL+"/"],capture_output=True)
        if not os.path.exists(m4a):
            still.append(vid); print(time.strftime("%H:%M:%S"), vid, "audio not available yet", flush=True); continue
        t=time.time(); audio=load(m4a)
        segs, info = pipe.transcribe(audio, language="en", batch_size=8, vad_filter=True)
        out=[]
        with open(f"{OUT}/{vid}.srt","w") as srt, open(f"{OUT}/{vid}.txt","w") as txt:
            for i,s in enumerate(segs,1):
                out.append({"start":round(s.start,2),"end":round(s.end,2),"text":s.text.strip()})
                srt.write(f"{i}\n{fmt(s.start)} --> {fmt(s.end)}\n{s.text.strip()}\n\n")
                txt.write(f"[{int(s.start//60):02d}:{int(s.start%60):02d}] {s.text.strip()}\n")
        json.dump({"video_id":vid,"model":"faster-whisper large-v3-turbo int8 (batched, vad)","duration":info.duration,"segments":out},open(f"{OUT}/{vid}.json","w"),indent=0)
        print(time.strftime("%H:%M:%S"), vid, f"done {info.duration/60:.1f} min audio in {(time.time()-t)/60:.1f} min", flush=True)
    pending = still
    if not pending: break
    time.sleep(60)
print("TRANSCRIPTION LOOP FINISHED", flush=True)
