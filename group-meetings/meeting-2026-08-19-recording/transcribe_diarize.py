#!/usr/bin/env python3
"""Whisper transcription + speaker diarization for the 2026-08-19 VCL group meeting.

Produces the whisper-diarized-* artifacts in this directory from the original
recording (see README.md for the SharePoint source). Runs fully on CPU with an
ungated model stack: faster-whisper (ASR, word timestamps), SpeechBrain ECAPA-TDNN
(speaker embeddings), scikit-learn agglomerative clustering (speaker count chosen
by silhouette score, overridable with --force-k).

Stages (each caches its result in --workdir so later stages can be re-run alone):
    calib      transcribe a 3-minute slice to measure CPU realtime factor
    asr        full transcription -> asr.json (segments + words)
    embed      speech regions from word timings -> ECAPA embeddings per 1.5 s window
    cluster    agglomerative clustering + temporal smoothing -> turns.json
    attribute  words -> speaker turns -> utterances.json
    map        overlap evidence vs Teams transcript speakers and chapters.txt
    render     final artifacts (needs --names JSON mapping cluster ids to display names)

Example:
    python transcribe_diarize.py --stage asr --audio work/audio.wav --workdir work
    python transcribe_diarize.py --stage render --names work/names.json
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

SAMPLE_RATE = 16000
WINDOW_S = 1.5
HOP_S = 0.75
GRANULE_S = 0.25
CLIP_START = 2440.8  # Audrey & Carl clip boundaries in the original recording
CLIP_END = 3666.6

HOTWORDS = (
    "Sterling Baird, Audrey Christiansen, Carl Robison, Gage, Ronnie, Andrew, "
    "Marcus, Ben Whitney, Xavier Zaitzeff, Sam Charles, Claude Code, Copilot, "
    "tensegrity, powder doser, Opentrons, OT-2, CubXL, Zoo CAD, BYU, Tactiq"
)


def fmt_ts(seconds, vtt=False):
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    if vtt:
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)
    print(f"wrote {path}")


# ---------------------------------------------------------------- ASR stages

def run_asr(args, slice_range=None):
    from faster_whisper import WhisperModel

    audio = args.audio
    if slice_range:
        import soundfile as sf
        data, sr = sf.read(args.audio, start=int(slice_range[0] * SAMPLE_RATE),
                           stop=int(slice_range[1] * SAMPLE_RATE), dtype="float32")
        audio = str(Path(args.workdir) / "calib_slice.wav")
        sf.write(audio, data, sr)

    model = WhisperModel(args.model, device="cpu", compute_type="int8",
                         cpu_threads=args.threads)
    t0 = time.time()
    segments, info = model.transcribe(
        audio, language="en", beam_size=args.beam,
        vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500),
        word_timestamps=True, condition_on_previous_text=False,
        hotwords=HOTWORDS)

    out_segments = []
    for seg in segments:
        words = [{"start": round(w.start, 3), "end": round(w.end, 3),
                  "word": w.word, "p": round(w.probability, 3)}
                 for w in (seg.words or [])]
        out_segments.append({"start": round(seg.start, 3), "end": round(seg.end, 3),
                             "text": seg.text, "words": words})
        if len(out_segments) % 50 == 0:
            pct = 100 * seg.end / info.duration
            print(f"  asr {pct:5.1f}%  ({fmt_ts(seg.end)}  wall {time.time()-t0:.0f}s)",
                  flush=True)
    wall = time.time() - t0
    xrt = info.duration / wall
    print(f"asr done: {info.duration:.0f}s audio in {wall:.0f}s wall -> {xrt:.2f}x realtime")

    if slice_range:
        return xrt
    save_json(Path(args.workdir) / "asr.json",
              {"model": args.model, "beam": args.beam, "duration": info.duration,
               "wall_s": round(wall, 1), "segments": out_segments})


def run_calib(args):
    xrt = run_asr(args, slice_range=(1140, 1320))
    import soundfile as sf
    total = sf.info(args.audio).duration
    print(f"calib: model={args.model} xrt={xrt:.2f} -> full-file ETA <= {total/xrt/60:.1f} min")


# ------------------------------------------------------------- diarization

def speech_regions_from_words(words, pad=0.15, merge_gap=0.4):
    regions = []
    for w in words:
        s, e = w["start"] - pad, w["end"] + pad
        if regions and s - regions[-1][1] <= merge_gap:
            regions[-1][1] = max(regions[-1][1], e)
        else:
            regions.append([max(0.0, s), e])
    return regions


def run_embed(args):
    import numpy as np
    import soundfile as sf
    import torch
    from speechbrain.inference.speaker import EncoderClassifier

    torch.set_num_threads(args.threads)
    asr = load_json(Path(args.workdir) / "asr.json")
    words = [w for seg in asr["segments"] for w in seg["words"]]
    regions = speech_regions_from_words(words)
    total_speech = sum(e - s for s, e in regions)
    print(f"{len(words)} words, {len(regions)} speech regions, {total_speech/60:.1f} min speech")

    audio, sr = sf.read(args.audio, dtype="float32")
    assert sr == SAMPLE_RATE

    win = int(WINDOW_S * SAMPLE_RATE)
    windows = []  # (start_s, end_s, samples)
    for rs, re_ in regions:
        t = rs
        while t < re_:
            t_end = min(t + WINDOW_S, re_)
            a = audio[int(t * SAMPLE_RATE):int(t_end * SAMPLE_RATE)][:win]
            if len(a) < win:
                if len(a) < 0.4 * SAMPLE_RATE and windows and t > rs:
                    break  # tail shorter than 0.4 s already covered by previous window
                a = np.pad(a, (0, win - len(a)))
            windows.append((t, t_end, a))
            t += HOP_S

    clf = EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir=str(Path(args.workdir) / "ecapa"),
        run_opts={"device": "cpu"})

    embs = []
    t0 = time.time()
    for i in range(0, len(windows), 64):
        batch = torch.tensor(np.stack([w[2] for w in windows[i:i + 64]]))
        with torch.no_grad():
            e = clf.encode_batch(batch).squeeze(1).cpu().numpy()
        embs.append(e)
        if (i // 64) % 10 == 0:
            print(f"  embed {i}/{len(windows)}  wall {time.time()-t0:.0f}s", flush=True)
    embs = np.concatenate(embs)
    np.save(Path(args.workdir) / "embeddings.npy", embs)
    save_json(Path(args.workdir) / "windows.json",
              {"regions": regions,
               "windows": [[round(s, 3), round(e, 3)] for s, e, _ in windows]})
    print(f"embedded {len(windows)} windows in {time.time()-t0:.0f}s")


def smooth_labels(labels, passes=2):
    labels = list(labels)
    for _ in range(passes):
        out = list(labels)
        for i in range(1, len(labels) - 1):
            trio = labels[i - 1:i + 2]
            c = Counter(trio).most_common(1)[0]
            if c[1] >= 2:
                out[i] = c[0]
        labels = out
    return labels


def cluster_subset(X, force_k, kmax, tag=""):
    import numpy as np
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score

    D = 1.0 - X @ X.T
    np.clip(D, 0, None, out=D)
    np.fill_diagonal(D, 0.0)
    scores = {}
    for k in range(2, kmax + 1):
        labels = AgglomerativeClustering(n_clusters=k, metric="precomputed",
                                         linkage="average").fit_predict(D)
        scores[k] = float(silhouette_score(D, labels, metric="precomputed"))
    print(f"silhouette{tag} by k:", {k: round(v, 4) for k, v in sorted(scores.items())})
    k = force_k or max(scores, key=scores.get)
    print(f"chosen k={k}" + (" (forced)" if force_k else ""))
    labels = AgglomerativeClustering(n_clusters=k, metric="precomputed",
                                     linkage="average").fit_predict(D)
    # centroid-reassignment passes clean up AHC boundary noise
    for _ in range(2):
        cents = np.stack([X[labels == c].mean(axis=0) for c in range(k)])
        cents /= np.linalg.norm(cents, axis=1, keepdims=True)
        labels = np.argmax(X @ cents.T, axis=1)
    return labels, scores


def finish_cluster(args, labels, windows, regions, scores, sub_of=None):
    import numpy as np

    labels = smooth_labels(list(labels))

    # sample a label at fine granules, then merge runs into turns
    centers = [(s + e) / 2 for s, e in windows]
    centers_np = np.array(centers)
    turns = []
    for rs, re_ in regions:
        t = rs
        cur = None
        while t < re_:
            g_end = min(t + GRANULE_S, re_)
            idx = int(np.argmin(np.abs(centers_np - (t + g_end) / 2)))
            lab = labels[idx]
            if cur is not None and cur["speaker"] == lab and t - cur["end"] < 1e-6:
                cur["end"] = g_end
            else:
                cur = {"speaker": int(lab), "start": round(t, 3), "end": g_end}
                turns.append(cur)
            t = g_end
    for t_ in turns:
        t_["end"] = round(t_["end"], 3)

    # absorb sub-0.6 s islands into the longer neighbor within the same region
    def absorb(turns):
        out = []
        for t_ in turns:
            if out and t_["speaker"] == out[-1]["speaker"] and \
                    abs(t_["start"] - out[-1]["end"]) < 1e-6:
                out[-1]["end"] = t_["end"]
            else:
                out.append(dict(t_))
        changed = True
        while changed:
            changed = False
            for i, t_ in enumerate(out):
                if t_["end"] - t_["start"] >= 0.6:
                    continue
                prev = out[i - 1] if i > 0 and abs(out[i - 1]["end"] - t_["start"]) < 1e-6 else None
                nxt = out[i + 1] if i + 1 < len(out) and abs(out[i + 1]["start"] - t_["end"]) < 1e-6 else None
                tgt = None
                if prev and nxt:
                    tgt = prev if (prev["end"] - prev["start"]) >= (nxt["end"] - nxt["start"]) else nxt
                else:
                    tgt = prev or nxt
                if tgt is not None:
                    t_["speaker"] = tgt["speaker"]
                    changed = True
            merged = []
            for t_ in out:
                if merged and t_["speaker"] == merged[-1]["speaker"] and \
                        abs(t_["start"] - merged[-1]["end"]) < 1e-6:
                    merged[-1]["end"] = t_["end"]
                else:
                    merged.append(t_)
            out = merged
        return out

    turns = absorb(turns)
    durs = Counter()
    for t_ in turns:
        durs[t_["speaker"]] += t_["end"] - t_["start"]
    print("cluster talk time (min):",
          {c: round(d / 60, 1) for c, d in durs.most_common()})
    save_json(Path(args.workdir) / "turns.json",
              {"k": len(set(labels)), "silhouette": scores, "sub_of": sub_of,
               "window_labels": [int(x) for x in labels], "turns": turns})


def run_cluster(args):
    import numpy as np

    embs = np.load(Path(args.workdir) / "embeddings.npy")
    wmeta = load_json(Path(args.workdir) / "windows.json")
    X = embs / np.linalg.norm(embs, axis=1, keepdims=True)
    labels, scores = cluster_subset(X, args.force_k, args.kmax)
    finish_cluster(args, labels, wmeta["windows"], wmeta["regions"], scores)


def run_subcluster(args):
    """Split one level-1 cluster (the shared room mic) into per-voice clusters.

    The subset mean embedding is subtracted first so cosine distance reflects
    voice differences rather than the shared channel/room signature.
    """
    import numpy as np

    embs = np.load(Path(args.workdir) / "embeddings.npy")
    wmeta = load_json(Path(args.workdir) / "windows.json")
    prev = load_json(Path(args.workdir) / "turns.json")
    labels = np.array(prev["window_labels"])
    parent = args.parent
    idx = np.where(labels == parent)[0]
    print(f"subclustering cluster {parent}: {len(idx)} windows")

    X = embs / np.linalg.norm(embs, axis=1, keepdims=True)
    Xs = X[idx] - X[idx].mean(axis=0)
    Xs /= np.linalg.norm(Xs, axis=1, keepdims=True)
    sub, scores = cluster_subset(Xs, args.force_k, args.kmax, tag=f" (sub of {parent})")

    base = int(labels.max()) + 1
    combined = labels.copy()
    combined[idx] = base + sub
    sub_of = {int(base + s): parent for s in set(sub.tolist())}
    finish_cluster(args, combined, wmeta["windows"], wmeta["regions"],
                   {"level1": prev["silhouette"], "sub": scores}, sub_of=sub_of)


def run_attribute(args):
    asr = load_json(Path(args.workdir) / "asr.json")
    turns = load_json(Path(args.workdir) / "turns.json")["turns"]
    words = [w for seg in asr["segments"] for w in seg["words"]]

    starts = [t["start"] for t in turns]

    def label_at(t):
        import bisect
        i = bisect.bisect_right(starts, t) - 1
        best, best_d = None, 2.0
        for j in (i, i + 1, i - 1):
            if 0 <= j < len(turns):
                tr = turns[j]
                if tr["start"] <= t <= tr["end"]:
                    return tr["speaker"]
                d = min(abs(t - tr["start"]), abs(t - tr["end"]))
                if d < best_d:
                    best, best_d = tr["speaker"], d
        return best if best is not None else -1

    for w in words:
        w["speaker"] = label_at((w["start"] + w["end"]) / 2)

    utterances = []
    for w in words:
        brk = (not utterances or utterances[-1]["speaker"] != w["speaker"] or
               w["start"] - utterances[-1]["end"] > 1.2 or
               (w["start"] - utterances[-1]["end"] > 0.5 and
                utterances[-1]["text"].rstrip().endswith((".", "?", "!"))) or
               w["end"] - utterances[-1]["start"] > 30)
        if brk:
            utterances.append({"speaker": w["speaker"], "start": w["start"],
                               "end": w["end"], "text": w["word"].strip(),
                               "words": [w]})
        else:
            u = utterances[-1]
            u["end"] = w["end"]
            u["text"] += w["word"] if w["word"].startswith(" ") else " " + w["word"]
            u["words"].append(w)
    save_json(Path(args.workdir) / "utterances.json", utterances)
    print(f"{len(utterances)} utterances")


# ------------------------------------------------------------------ naming

def parse_chapters(path):
    chapters = []
    for line in Path(path).read_text().splitlines():
        m = re.match(r"^(\d+):(\d\d)(?::(\d\d))?\s+(.*)$", line.strip())
        if not m:
            continue
        a, b, c, title = m.groups()
        t = int(a) * 3600 + int(b) * 60 + int(c) if c else int(a) * 60 + int(b)
        chapters.append({"start": float(t), "title": title})
    for i, ch in enumerate(chapters):
        ch["end"] = chapters[i + 1]["start"] if i + 1 < len(chapters) else 1e9
    return chapters


def overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def run_map(args):
    turns = load_json(Path(args.workdir) / "turns.json")["turns"]
    utts = load_json(Path(args.workdir) / "utterances.json")
    here = Path(__file__).parent
    teams = load_json(here / "transcript.json")["entries"]
    chapters = parse_chapters(here / "chapters.txt")

    def hms(s):
        h, m, rest = s.split(":")
        return int(h) * 3600 + int(m) * 60 + float(rest)

    tt = [(e["speakerDisplayName"], hms(e["startOffset"]), hms(e["endOffset"]))
          for e in teams]

    ev = {}
    for t_ in turns:
        c = t_["speaker"]
        e = ev.setdefault(c, {"dur": 0.0, "teams": defaultdict(float),
                              "chapters": defaultdict(float)})
        e["dur"] += t_["end"] - t_["start"]
        for name, s, x in tt:
            e["teams"][name] += overlap(t_["start"], t_["end"], s, x)
        for ch in chapters:
            e["chapters"][ch["title"]] += overlap(t_["start"], t_["end"],
                                                  ch["start"], ch["end"])

    report = {}
    for c, e in sorted(ev.items(), key=lambda kv: -kv[1]["dur"]):
        samples = [u for u in utts if u["speaker"] == c and len(u["text"]) > 60]
        samples.sort(key=lambda u: -(u["end"] - u["start"]))
        picks = samples[:2] + samples[len(samples) // 2:len(samples) // 2 + 1] \
            + samples[-1:] if samples else []
        report[str(c)] = {
            "minutes": round(e["dur"] / 60, 2),
            "teams_overlap_min": {k: round(v / 60, 2) for k, v in
                                  sorted(e["teams"].items(), key=lambda kv: -kv[1]) if v > 6},
            "top_chapters": {k: round(v / 60, 2) for k, v in
                             sorted(e["chapters"].items(), key=lambda kv: -kv[1])[:5]},
            "samples": [{"at": fmt_ts(u["start"]), "text": u["text"][:220]}
                        for u in picks],
        }
    save_json(Path(args.workdir) / "speaker-map-evidence.json", report)
    print(json.dumps(report, indent=1)[:4000])


# ------------------------------------------------------------------ render

def cue_lines(utt, max_chars=88, max_s=6.5):
    chunks, cur = [], []
    for w in utt["words"]:
        cur.append(w)
        text = "".join(x["word"] for x in cur).strip()
        if len(text) >= max_chars or cur[-1]["end"] - cur[0]["start"] >= max_s:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def render_vtt(utts, names, path, offset=0.0, window=None):
    lines = ["WEBVTT", ""]
    for u in utts:
        if window and (u["end"] <= window[0] or u["start"] >= window[1]):
            continue
        name = names.get(str(u["speaker"]), f"Speaker {u['speaker']}")
        for chunk in cue_lines(u):
            s = max(chunk[0]["start"], window[0] if window else 0) - offset
            e = min(chunk[-1]["end"], window[1] if window else 1e9) - offset
            if e <= s:
                continue
            text = "".join(w["word"] for w in chunk).strip()
            lines += [f"{fmt_ts(max(0, s), vtt=True)} --> {fmt_ts(e, vtt=True)}",
                      f"<v {name}>{text}</v>", ""]
    Path(path).write_text("\n".join(lines))
    print(f"wrote {path}")


def render_timeline(turns, names, order, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    # dataviz-skill reference palette, categorical slots 1-8 (light mode);
    # rows beyond 8 fold to muted gray — identity is carried by the row label
    palette = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
               "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
    muted, surface, grid = "#898781", "#fcfcfb", "#e1e0d9"
    ink, ink2 = "#0b0b0b", "#52514e"

    rows = order
    fig_h = 1.7 + 0.42 * len(rows)
    fig, ax = plt.subplots(figsize=(11.5, fig_h), dpi=150)
    fig.patch.set_facecolor(surface)
    ax.set_facecolor(surface)

    ax.axvspan(CLIP_START / 60, CLIP_END / 60, color="#0b0b0b", alpha=0.045, zorder=0)

    def disp(c):
        return names.get(str(c), f"Speaker {c}")

    dur_by = Counter()
    for t in turns:
        dur_by[disp(t["speaker"])] += t["end"] - t["start"]
    for yi, row in enumerate(rows):
        color = palette[yi] if yi < len(palette) else muted
        spans = [(t["start"] / 60, (t["end"] - t["start"]) / 60)
                 for t in turns if disp(t["speaker"]) == row]
        ax.broken_barh(spans, (yi - 0.31, 0.62), facecolors=color, edgecolors="none")

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{row}  ·  {dur_by[row]/60:.1f} min" for row in rows],
                       fontsize=9.5, color=ink)
    ax.invert_yaxis()

    ax.set_xlim(0, 76)
    ax.set_xticks(range(0, 80, 10))
    ax.set_xticks(range(0, 76, 5), minor=True)
    ax.set_xticklabels([f"{m}" for m in range(0, 80, 10)], fontsize=9, color=ink2)
    ax.set_xlabel("minutes into the recording (original 75:34 timeline)",
                  fontsize=9.5, color=ink2)
    ax.grid(axis="x", which="both", color=grid, linewidth=0.7)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors="#898781", length=3)

    ax.text(CLIP_START / 60 + 0.3, -0.78, "online breakout — Audrey & Carl",
            fontsize=8.5, color=ink2, style="italic")
    ax.set_title("Who spoke when — VCL group meeting 2026-08-19\n"
                 "Whisper (faster-whisper) + ECAPA speaker diarization",
                 fontsize=12, color=ink, loc="left", pad=12)
    fig.tight_layout()
    fig.savefig(path, facecolor=surface, bbox_inches="tight")
    print(f"wrote {path}")


def run_render(args):
    import numpy as np
    import soundfile as sf

    utts = load_json(Path(args.workdir) / "utterances.json")
    turns = load_json(Path(args.workdir) / "turns.json")["turns"]
    names = load_json(args.names) if args.names else {}
    outdir = Path(args.outdir or Path(__file__).parent)
    outdir.mkdir(exist_ok=True)

    # several clusters can share one display name (e.g. one voice split by
    # acoustic context); merge them for every human-facing output
    def disp(c):
        return names.get(str(c), f"Speaker {c}")

    merged = []
    for u in utts:
        if merged and disp(merged[-1]["speaker"]) == disp(u["speaker"]) and \
                u["start"] - merged[-1]["end"] < 1.2 and \
                u["end"] - merged[-1]["start"] < 40:
            m = merged[-1]
            m["end"] = u["end"]
            m["text"] += " " + u["text"]
            m["words"] += u["words"]
        else:
            merged.append(dict(u))
    utts = merged

    dur_by = Counter()
    for t in turns:
        dur_by[disp(t["speaker"])] += t["end"] - t["start"]
    order = [c for c, _ in dur_by.most_common()]

    # plain-text transcript
    lines = []
    for u in utts:
        name = names.get(str(u["speaker"]), f"Speaker {u['speaker']}")
        lines.append(f"[{fmt_ts(u['start'])}] {name}: {u['text']}")
    (outdir / "whisper-diarized-transcript.txt").write_text("\n".join(lines) + "\n")
    print("wrote whisper-diarized-transcript.txt")

    render_vtt(utts, names, outdir / "whisper-diarized-transcript.vtt")
    render_vtt(utts, names, outdir / "audrey-carl-clip.whisper-diarized.vtt",
               offset=CLIP_START, window=(CLIP_START, CLIP_END))

    slim = [{"speaker": names.get(str(u["speaker"]), f"Speaker {u['speaker']}"),
             "cluster": u["speaker"], "start": u["start"], "end": u["end"],
             "text": u["text"]} for u in utts]
    save_json(outdir / "whisper-diarized-transcript.json",
              {"source": "faster-whisper + ECAPA diarization (see transcribe_diarize.py)",
               "names": names, "utterances": slim})

    with open(outdir / "diarization.rttm", "w") as f:
        for t in turns:
            name = names.get(str(t["speaker"]), f"Speaker_{t['speaker']}").replace(" ", "_")
            f.write(f"SPEAKER meeting-2026-08-19 1 {t['start']:.2f} "
                    f"{t['end']-t['start']:.2f} <NA> <NA> {name} <NA> <NA>\n")
    print("wrote diarization.rttm")

    render_timeline(turns, names, order, outdir / "diarization-timeline.png")

    if args.voices:
        vdir = Path(args.voices)
        vdir.mkdir(exist_ok=True)
        audio, sr = sf.read(args.audio, dtype="float32")
        gap = np.zeros(int(0.35 * sr), dtype="float32")
        for rank, name in enumerate(order, 1):
            pieces = []
            for t in turns:
                if disp(t["speaker"]) == name:
                    pieces += [audio[int(t["start"]*sr):int(t["end"]*sr)], gap]
            joined = np.concatenate(pieces)
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            tmp = vdir / f"tmp-{rank}.wav"
            sf.write(tmp, joined, sr)
            out = vdir / f"{rank:02d}-{slug}.m4a"
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                            "-i", str(tmp), "-c:a", "aac", "-b:a", "96k", str(out)],
                           check=True)
            tmp.unlink()
            print(f"wrote {out} ({dur_by[name]/60:.1f} min)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", required=True,
                   choices=["calib", "asr", "embed", "cluster", "subcluster",
                            "attribute", "map", "render"])
    p.add_argument("--parent", type=int, default=None,
                   help="cluster id to split (subcluster stage)")
    p.add_argument("--audio", default="work/audio.wav")
    p.add_argument("--workdir", default="work")
    p.add_argument("--outdir", default=None)
    p.add_argument("--model", default="small.en")
    p.add_argument("--beam", type=int, default=1)
    p.add_argument("--threads", type=int, default=os.cpu_count() or 4)
    p.add_argument("--kmax", type=int, default=14)
    p.add_argument("--force-k", type=int, default=None)
    p.add_argument("--names", default=None, help="JSON: cluster id -> display name")
    p.add_argument("--voices", default=None, help="dir for per-speaker audio")
    args = p.parse_args()
    Path(args.workdir).mkdir(parents=True, exist_ok=True)

    {"calib": run_calib, "asr": run_asr, "embed": run_embed,
     "cluster": run_cluster, "subcluster": run_subcluster,
     "attribute": run_attribute, "map": run_map,
     "render": run_render}[args.stage](args)


if __name__ == "__main__":
    main()
