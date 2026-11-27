"""The campaign video's narration: the script (twin/video/narration.json), spoken by Kokoro, placed on the cut and mixed
into one track, with subtitles beside it.

    python -m twin.video.narration tts       # speak every line -> out/twin2/video/narration/<id>.flac (committed)
    python -m twin.video.narration plan      # each line's time in the cut, and the caption on screen while it plays
    python -m twin.video.narration check     # every line heard back by faster-whisper -> narration/check.json
    python -m twin.video.narration track     # the mixed track and subtitles for the cut as planned (no video)

The script is short lines at the places that need them (what is simulated and what is real, the function networks,
how to read the plots and the acceleration factor, the first alloy, the switch to the whole lab, the results, the
takeaway and the closing notes); the captions and the pictures carry the rest. Each line is anchored on a segment of
the cut (``seg``, with ``at`` seconds into it) or on a named moment inside one (``mark``, see marks() below),
plus ``offset``, so it follows the cut when segments are re-timed.

The voice is Kokoro v1.0 (82M parameters, Apache-2.0 open weights, run on the runner through kokoro-onnx), its stock
voice af_heart: no reference audio, nobody's voice cloned or imitated. As for the long-form's narration
(longform.py), each line is spoken from phonemes: SAY respells what the voice would misread (letters said as letters,
the American "aluminum"), IPA gives the phonemes of the words no respelling fixes.

Each line's audio is committed as FLAC (out/twin2/video/narration/<id>.flac, with its text, phonemes, voice and speed in
lines.json), so the cut can be rebuilt without the speech model: a line is spoken again only when its phonemes, voice
or speed change.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

from . import data as D

SCRIPT = Path(__file__).with_name("narration3b.json" if D.R3B else "narration3.json" if D.ROUND == 3 else
                                  "narration.json")         # rounds 3 and 3b have their own scripts
NDIR = D.VID / "narration"                                  # committed: each line's FLAC, lines.json, check.json
VOICE = os.environ.get("NARRATION_VOICE", "af_heart")       # Kokoro v1.0's stock voice, best rated in its VOICES.md
SPEED = float(os.environ.get("NARRATION_SPEED", "0.96"))    # as the long-form's narration
SR = 24000                                                  # Kokoro's rate
OUT_SR = 48000                                              # the cut's audio
KOKORO = (os.environ.get("KOKORO_MODEL", "/tmp/kokoro/kokoro-v1.0.onnx"),
          os.environ.get("KOKORO_VOICES", "/tmp/kokoro/voices-v1.0.bin"))
LINE_RMS_DB = -19.0                                         # each line levelled to this RMS (dBFS), peaks under -1.5
GAP_MIN = 0.5                                               # seconds of silence at least between two lines

# How the voice says what the text writes. The text is written as the subtitles should read; these are only for the
# voice. The long-form's (longform.py) first, then this video's own words.
SAY = {
    "MiR250": "MiR two-fifty", "OT-2": "O T two", "UPS": "U P S", "SEM": "S E M", "BYU": "B Y U", "EDM": "E D M",
    "ICP-MS": "I C P M S", "UR12e": "U R twelve E", "aluminium": "aluminum", "AlSi10Mg": "A L S I ten M G",
    "FLAIME": "flame",                    # the proposal's name, said as the word
    "ONR": "O N R", "BOFN": "B O F N", "GP-BO": "G P B O", "LPBF": "L P B F", "DED": "D E D", "HPC": "H P C",
    "EDS": "E D S", "XRD": "X R D", "3-D": "three D", "VHX": "V H X", "labour": "labor",
}
if D.ROUND == 3:                         # round 3's script only, so round 2's committed lines stay reusable
    SAY = dict(SAY, pKGFN="P K G F N")
IPA = {
    "MiR": "mˈiːɹ",                       # longform.py: said "meer"
    "CALPHAD": "kˈælfæd",                 # espeak spells it out letter by letter
    "Kardex": "kˈɑːɹdɛks",
    "Sobol": "sˈoʊbɑːl",
    "doser": "dˈoʊsɚ", "dosed": "dˈoʊsd",  # longform.py: espeak's dˈoʊzɚ was heard back as "dozer"
    "pycalphad": "pˈaɪkælfæd",
}
_TOK = None


def _word(keys):
    return re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, sorted(keys, key=len, reverse=True))) + r")(?![\w-])")


def spoken(text: str) -> str:
    """The line as the voice is to say it (SAY applied)."""
    return _word(SAY).sub(lambda m: SAY[m.group(1)], text)


_DEC = re.compile(r"(?<![\w.])(\d+)\.(\d+)(?![\w]|\.\d)")


def _decimals(t: str) -> str:
    """A decimal as it is to be said: '1.8' -> '1 point 8', '0.73' -> '0 point 7 3'. The phonemizer is asked to keep
    punctuation, and some of its versions then split a number at its point and say 'one. eight' (found by the
    heard-back check on round 3b's lines: every decimal came back without 'point')."""
    return _DEC.sub(lambda m: f"{m.group(1)} point {' '.join(m.group(2))}", t)


def _phon(chunk: str) -> str:
    """One chunk of a line through espeak, its decimals said with 'point' (unstressed, as espeak says it inside a
    number: round 3's recordings have 'fˈɔːɹ pɔɪnt zˈiəɹoʊ')."""
    said = _decimals(chunk)
    ph = _TOK.phonemize(said)
    if said != chunk and not re.search(r"\bpoint", chunk):
        ph = ph.replace("pˈɔɪnt", "pɔɪnt")
    return ph


def phonemes(text: str) -> str:
    """The line's phonemes for Kokoro: espeak's (kokoro-onnx's tokenizer), except IPA's words."""
    global _TOK
    if _TOK is None:
        from kokoro_onnx.tokenizer import Tokenizer
        _TOK = Tokenizer()
    t, out, pos = spoken(text), [], 0
    for m in _word(IPA).finditer(t):
        if t[pos:m.start()].strip():
            out.append(_phon(t[pos:m.start()].strip()))
        out.append(IPA[m.group(1)])
        pos = m.end()
    if t[pos:].strip():
        out.append(_phon(t[pos:].strip()))
    return " ".join(out)


def lines() -> list:
    return json.loads(SCRIPT.read_text())["lines"]


def _key(ph: str) -> str:
    return hashlib.sha256(f"{VOICE}|{SPEED}|{ph}".encode()).hexdigest()[:16]


def _record() -> dict:
    p = NDIR / "lines.json"
    return json.loads(p.read_text()) if p.exists() else {"voice": None, "lines": {}}


def _reusable(ln: dict, rec: dict) -> bool:
    """A line's committed FLAC still holds: same text, same respellings and phonemes for words (SAY, IPA), same voice
    and speed. Then nothing is spoken again, and no speech stack is needed to rebuild the cut."""
    have = rec["lines"].get(ln["id"])
    return bool(have and have.get("text") == ln["text"] and rec.get("say") == SAY and rec.get("ipa") == IPA
                and rec.get("voice_id") == VOICE and rec.get("speed") == SPEED
                and (NDIR / f"{ln['id']}.flac").exists() and not os.environ.get("NARRATION_RESPEAK"))


def speak_all(only: set | None = None) -> dict:
    """Every line's audio at 24 kHz: its committed FLAC where that still holds (_reusable), else spoken now by Kokoro
    from its phonemes and written there; lines.json brought up to date. `only`: speak just these ids."""
    import soundfile as sf
    rec = _record()
    k, out, keep = None, {}, {}
    for ln in lines():
        if only and ln["id"] not in only:
            continue
        path = NDIR / f"{ln['id']}.flac"
        if _reusable(ln, rec):
            have = rec["lines"][ln["id"]]
            ph, key = have["phonemes"], have["key"]
            y, _ = sf.read(str(path), dtype="float32")
        else:
            ph = phonemes(ln["text"])
            key = _key(ph)
            if k is None:
                from kokoro_onnx import Kokoro
                k = Kokoro(*KOKORO)
            y, sr = k.create(ph, voice=VOICE, speed=SPEED, lang="en-us", is_phonemes=True)
            assert sr == SR, sr
            y = np.asarray(y, np.float32)
            NDIR.mkdir(parents=True, exist_ok=True)
            sf.write(str(path), y, SR, format="FLAC", subtype="PCM_16")
            y, _ = sf.read(str(path), dtype="float32")             # as a rebuild will read it
        keep[ln["id"]] = dict(key=key, text=ln["text"], spoken=spoken(ln["text"]), phonemes=ph,
                              seconds=round(len(y) / SR, 2), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        out[ln["id"]] = y
    if not only:                                        # drop the FLACs of lines no longer in the script
        for f in NDIR.glob("*.flac"):
            if f.stem not in keep:
                f.unlink()
        rec["lines"] = keep
    else:
        rec["lines"].update(keep)
    rec.update(voice=f"Kokoro v1.0 {VOICE} (kokoro-onnx, open weights), speed {SPEED}", voice_id=VOICE, speed=SPEED,
               rate=SR, model_sha256={"kokoro-v1.0.onnx": "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
                                      "voices-v1.0.bin": "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"},
               say=SAY, ipa=IPA)
    (NDIR / "lines.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    return out


# ------------------------------------------------------------------------------------------------ placement
def marks(rec: dict) -> dict:
    """Named moments of the cut (s from its start) that lines can anchor on, from the modules' own timelines:
    dag.lane.<campaign>, dag.both, dag.collapse (dag_anim.Dag.T), dag.node.<campaign>.<node> (a card's arrival,
    Dag.node_t); replay.pov.<what> (day 1's first shot of a step),
    replay.grid (the end of day 1), replay.phase.<i>, replay.lab3d (the animated lab takes over), replay.from_above
    (the first view of the whole lab from above), replay.whole_lab (the chapter of that name), replay.end."""
    from . import compose as C
    seg0 = {s["name"]: s["start_s"] for s in rec["segments"]}
    out = {f"{n}.start": t for n, t in seg0.items()}
    dag = C.S("dag")
    for c in D.CAMPAIGNS:
        out[f"dag.lane.{c}"] = seg0["dag"] + dag.T[c][0]
    for k in ("both", "collapse", "icons", "dock"):
        if k in dag.T:
            out[f"dag.{k}"] = seg0["dag"] + dag.T[k][0]
    for (c, key), t in dag.node_t.items():                # each card's arrival (and its caption, if it has one)
        out[f"dag.node.{c}.{key}"] = seg0["dag"] + t
    tl = C.S("tl")
    for s in tl.pov:
        out.setdefault(f"replay.pov.{s['what']}", seg0["replay"] + s["v0"])
        out.setdefault(f"replay.pov.{s['what']}.{s['station']}", seg0["replay"] + s["v0"])
    out["replay.grid"] = seg0["replay"] + tl.t_pov             # day 1 ends: the cameras (or the 3-D lab) take over
    for i, t in enumerate(tl.phase_t):
        out[f"replay.phase.{i}"] = seg0["replay"] + t
    whole = [t for t, title in tl.marks() if "whole lab" in title.lower()]
    if whole:                                           # the chapter "Week by week: the whole lab"
        out["replay.whole_lab"] = seg0["replay"] + whole[0]
    # the first picture of the whole lab from above: a birds-eye still ("be"), or the animated cut's 3-D lab seen from
    # a camera on the whole floor (TWIN_VIDEO_LAB3D: plan, high, sw, se; "towers_c" is the Shuttles up close)
    above = [t for t, p in zip(tl.phase_t, C.PHASES) if p[1] == "be" or (p[1] == "3d" and p[2] in
                                                                         ("plan", "high", "sw", "se"))]
    if above:
        out["replay.from_above"] = seg0["replay"] + above[0]
    lab3d = [t for t, p in zip(tl.phase_t, C.PHASES) if p[1] == "3d"]
    if lab3d:                                           # the animated lab takes over from day 1's shots
        out["replay.lab3d"] = seg0["replay"] + lab3d[0]
    if D.R3B:                                           # round 3b's replay: where it changes run, and where the
        out["replay.switch"] = seg0["replay"] + tl.switch_t     # second run reaches the target it is the median for
        b = C.S("R").parts[1]
        out["replay.b_hit"] = seg0["replay"] + float(np.interp(float(b["day"]) * D.HPD, tl.lab_g, tl.vg))
    out["replay.end"] = seg0["replay"] + tl.dur
    return {k: round(float(v), 2) for k, v in out.items()}


def place(rec: dict, mk: dict) -> list:
    """Each line's start in the cut (s): its segment's start (rec["segments"]) or its mark (marks()),
    plus at/offset; pushed later if the line before is still going. Returns rows with t, end, seg and warnings."""
    seg0 = {s["name"]: (s["start_s"], s["start_s"] + s["seconds"]) for s in rec["segments"]}
    rows = []
    lab3d = os.environ.get("TWIN_VIDEO_LAB3D", "0") == "1"
    for ln in lines():
        if ln.get("needs") == "lab3d" and not lab3d:          # a line about the animated lab, on the cut without it
            continue
        if ln.get("mark"):
            if ln["mark"] not in mk:
                rows.append(dict(ln, t=None, warn=f"no mark {ln['mark']}"))
                continue
            t = mk[ln["mark"]] + float(ln.get("offset", 0.0))
        else:
            t = seg0[ln["seg"]][0] + float(ln.get("at", 0.0)) + float(ln.get("offset", 0.0))
        rows.append(dict(ln, t=round(t, 2)))
    rows = [r for r in rows if r.get("t") is not None] + [r for r in rows if r.get("t") is None]
    rows.sort(key=lambda r: (r["t"] is None, r["t"] or 0.0))
    return rows


def _lufs(wav: Path) -> float | None:
    try:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(wav), "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True)
    except OSError:                                     # no ffmpeg: the loudness is only reported
        return None
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else None


def track(rec: dict, mk: dict, total: float, wav: Path, srt: Path | None = None) -> list:
    """Every line placed at its time, levelled, into one 48 kHz mono WAV of the cut's length (and an SRT beside it).
    A line that would start under GAP_MIN after the one before is pushed later, with a warning; one that runs past its
    segment's end is reported."""
    import soundfile as sf
    from scipy.signal import resample_poly
    au = speak_all()
    rows = place(rec, mk)
    seg_end = {s["name"]: s["start_s"] + s["seconds"] for s in rec["segments"]}
    tr = np.zeros(int((total + 1.0) * OUT_SR), np.float32)
    free, placed = 0.0, []
    for r in rows:
        if r.get("t") is None:
            print(f"  narration: {r['id']}: {r.get('warn')}; left out", flush=True)
            continue
        y = au[r["id"]]
        rms, peak = float(np.sqrt(np.mean(y ** 2))) + 1e-9, float(np.abs(y).max()) + 1e-9
        y = y * min(10 ** (LINE_RMS_DB / 20) / rms, 0.84 / peak)
        y = resample_poly(y, OUT_SR // SR, 1).astype(np.float32)
        t = max(r["t"], free + GAP_MIN)
        warn = []
        if t - r["t"] > 0.3:
            warn.append(f"pushed {t - r['t']:.1f} s later")
        end = t + len(y) / OUT_SR
        seg = r.get("seg") or r["mark"].split(".")[0]
        if end > seg_end.get(seg, total) + 0.05 and not r.get("spill"):
            warn.append(f"runs {end - seg_end[seg]:.1f} s past the end of {seg}")
        i0 = int(round(t * OUT_SR))
        n = max(0, min(len(y), len(tr) - i0))
        tr[i0:i0 + n] += y[:n]
        free = end
        placed.append(dict(id=r["id"], seg=seg, t=round(t, 2), end=round(end, 2), text=r["text"], warn=warn))
        for w in warn:
            print(f"  narration: {r['id']}: {w}", flush=True)
    tr = tr[:int(total * OUT_SR)]
    sf.write(str(wav), tr, OUT_SR, subtype="PCM_16")
    if srt is not None:
        srt.write_text("".join(f"{i + 1}\n{_stamp(p['t'])} --> {_stamp(p['end'])}\n{p['text']}\n\n"
                               for i, p in enumerate(placed)))
    sp = sum(p["end"] - p["t"] for p in placed)
    print(f"narration: {len(placed)} lines, {sp / 60:.1f} min spoken of {total / 60:.1f} ({100 * sp / total:.0f} %); "
          f"integrated loudness {_lufs(wav)} LUFS", flush=True)
    return placed


def _stamp(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d},{ms % 1000:03d}"


def clock(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


# ------------------------------------------------------------------------------------------------ the check
def _norm(s: str) -> str:
    """For comparing a line with what the recognizer heard: numbers as words, no punctuation, one spelling."""
    from num2words import num2words
    s = s.replace("°", " degrees").replace("%", " percent")
    s = re.sub(r"\$([\d.,]+)\s*(million|thousand|billion)?", lambda m: f"{m.group(1)} {m.group(2) or ''} dollars", s)
    s = re.sub(r"(\d),(\d{3})", r"\1\2", s)
    s = re.sub(r"\d+(\.\d+)?", lambda m: " " + num2words(float(m.group()) if "." in m.group() else int(m.group())) +
               " ", s)
    s = re.sub(r"(?<=[A-Z])-(?=[A-Z])", "", s)
    s = s.lower().replace("-", " ").replace("’", "'")
    for a, b in (("aluminium", "aluminum"), ("labour", "labor"), ("colour", "color"), ("metre", "meter"),
                 ("grey", "gray"), ("modelled", "modeled")):
        s = s.replace(a, b)
    s = re.sub(r"[^a-z' ]", " ", s)
    s = re.sub(r"'s\b|s'", "s", s)
    out, single = [], False
    for w in s.split():                                  # letters said one by one, written as one word
        one = len(w) == 1 and w != "a"
        if one and single:
            out[-1] += w
        else:
            out.append(w)
        single = one
    return " ".join(out)


def check(models=("base.en", "small.en")) -> list:
    """Every line heard back by faster-whisper (two model sizes) and compared word by word with its spoken form ->
    narration/check.json, and every line in a row (a second between) -> narration/lines.ogg, to listen to."""
    import jiwer
    import soundfile as sf
    from faster_whisper import WhisperModel
    from scipy.signal import resample_poly
    au = speak_all()
    asr = {m: WhisperModel(m, device="cpu", compute_type="int8") for m in models}
    rows, cat = [], []
    for ln in lines():
        y = au[ln["id"]]
        cat += [y, np.zeros(SR, np.float32)]
        y16 = resample_poly(y, 2, 3).astype(np.float32)
        ref = _norm(spoken(ln["text"]))
        row = dict(id=ln["id"], text=ln["text"], spoken=spoken(ln["text"]), seconds=round(len(y) / SR, 2))
        for m, model in asr.items():
            segs, _ = model.transcribe(y16, language="en", word_timestamps=True, beam_size=5)
            words = [w for sg in segs for w in sg.words]
            heard = "".join(w.word for w in words).strip()
            o = jiwer.process_words(ref, _norm(heard))
            diffs = [(a.type, " ".join(o.references[0][a.ref_start_idx:a.ref_end_idx]),
                      " ".join(o.hypotheses[0][a.hyp_start_idx:a.hyp_end_idx]))
                     for a in o.alignments[0] if a.type != "equal"]
            row[m] = dict(heard=heard, wer=round(o.wer, 3), diffs=diffs,
                          unsure=[(w.word.strip(), round(w.probability, 2)) for w in words if w.probability < 0.5])
        rows.append(row)
        print(f"{ln['id']:8s} {row['seconds']:5.1f} s  " + "  ".join(f"{m} {row[m]['wer']:.2f}" for m in asr) +
              "".join(f"  [{m}: {d}]" for m in asr for d in row[m]["diffs"][:4]), flush=True)
    words = sum(len(_norm(r["spoken"]).split()) for r in rows)
    summ = {m: round(sum(r[m]["wer"] * len(_norm(r["spoken"]).split()) for r in rows) / max(1, words), 4)
            for m in asr}
    (NDIR / "check.json").write_text(json.dumps(dict(
        voice=f"Kokoro v1.0 {VOICE}, speed {SPEED}", recognizers=[f"faster-whisper {m}" for m in models],
        word_error_rate=summ, words=words, lines=rows), indent=1, ensure_ascii=False) + "\n")
    tmp = Path(tempfile.gettempdir()) / "twin_narration_lines.wav"
    sf.write(str(tmp), np.concatenate(cat), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-c:a", "libopus", "-b:a", "40k",
                    str(NDIR / "lines.ogg")], check=True)
    print("word error rate", summ, flush=True)
    return rows


# ------------------------------------------------------------------------------------------------ the plan
def captions_at(name: str, t0: float, t1: float) -> list:
    """The captions on screen in segment `name` between t0 and t1 (seconds into it): the ones each module keeps."""
    from . import compose as C
    caps = []
    if name == "simulated":
        caps = C.SIM_CAPS
    elif name == "dag":
        caps = C.S("dag").captions
    elif name == "figures" and D.ROUND == 3:
        caps = C.S("figs3").explain_caps()
    elif name == "results" and D.ROUND == 3:
        caps = C.S("figs3").results_caps()
    elif name == "labs" and D.R3B:
        caps = C.S("figs3").labs_caps()
    elif name == "figures":
        caps = C.S("figs").EXPLAIN_CAPTIONS
    elif name == "results":
        caps = C.S("figs").RESULTS_CAPTIONS
    elif name == "replay":
        tl = C.S("tl")
        caps = [(s["v0"], s["v1"], f"{C.WHAT_WORDS.get(s['what'], s['what'])}: {s['shot'][3]}") for s in tl.pov]
        caps += [(a, b, f"chapter: {t}") for (a, t), b in zip(tl.marks(), [m[0] for m in tl.marks()[1:]] + [tl.dur])]
    return [c for c in caps if c[0] < t1 and c[1] > t0]


def plan_table(placed: list, rec: dict) -> str:
    seg0 = {s["name"]: s["start_s"] for s in rec["segments"]}
    out = ["| Starts | Ends | Line | On screen meanwhile |", "|---|---|---|---|"]
    for p in placed:
        a, b = p["t"] - seg0[p["seg"]], p["end"] - seg0[p["seg"]]
        caps = captions_at(p["seg"], a, b)
        cap = " / ".join(c[2] for c in caps) if caps else f"({p['seg']})"
        out.append(f"| {clock(p['t'])} | {clock(p['end'])} | {p['text']} | {cap} |")
    return "\n".join(out)


SECTION = {"title": "Opening", "simulated": "Opening", "dag": "The function networks", "figures": "Reading the figures",
           "replay": "The campaign year", "results": "Results", "takeaway": "The takeaway", "notes": "Closing notes",
           "changes": "What changed in round 3", "assume": "The atomizer's assumptions",
           "labs": "The lab comparison, like for like"}
WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "sixteen": 16}


def _resolve(expr: str, n: dict) -> float:
    """A `nums` path in numbers3.numbers(): dotted keys, with one of *K, /K or -<other path> at the end ("a.b*100",
    "a.b/1000", "a.b-a.c"). A key may itself hold dots or bars (the cost per alloy's): the longest match wins."""
    def get(path):
        cur = n
        rest = path
        while rest:
            if not isinstance(cur, dict):
                raise KeyError(path)
            key = next((k for k in sorted(cur, key=len, reverse=True) if rest == k or rest.startswith(k + ".")), None)
            if key is None:
                raise KeyError(f"{path}: no key at '{rest}'")
            cur, rest = cur[key], rest[len(key) + 1:]
        return float(cur)
    m = re.match(r"^(.*?)([*/])(\d+(?:\.\d+)?)$", expr)
    if m:
        v = get(m.group(1))
        return v * float(m.group(3)) if m.group(2) == "*" else v / float(m.group(3))
    if "-" in expr and not expr.startswith("-"):
        a, b = expr.split("-", 1)
        try:
            return get(a) - get(b)
        except KeyError:
            pass
    return get(expr)


def check_numbers() -> list:
    """Every number a line speaks (its `nums`) against numbers3.numbers(), i.e. against round 3's committed
    summaries: the value at the path, in its format, must be the figure in the text (or the number the word names),
    and the figure must be in the text. Also: every digit string in a line must be covered by its nums. Returns the
    rows; raises SystemExit on a mismatch."""
    if D.R3B:                                           # round 3b: its numbers (like3b.json on top of round 3's)
        from . import numbers3b as N3
    else:
        from . import numbers3 as N3
    n = N3.numbers()
    rows, bad = [], []
    for ln in lines():
        text = ln["text"]
        covered = set()
        for tok, path, fmt in ln.get("nums", []):
            v = _resolve(path, n)
            shown = f"{round(v):d}" if fmt == "d" else format(v, fmt)
            want = str(WORDS[tok.lower()]) if tok.lower() in WORDS else tok
            ok = (shown == want) and (tok in text)
            rows.append(dict(id=ln["id"], says=tok, path=path, value=v, shown=shown, ok=ok))
            covered.add(tok)
            if not ok:
                bad.append(rows[-1])
        for fig in re.findall(r"(?<![\w-])\d+(?:\.\d+)?(?![\w-])", text):
            if fig not in covered:
                rows.append(dict(id=ln["id"], says=fig, path=None, value=None, shown=None, ok=False))
                bad.append(rows[-1])
    for r in rows:
        print(f"{'ok ' if r['ok'] else 'BAD'} {r['id']:6s} says {r['says']:8s} {r['shown']!s:8s} <- {r['path']}")
    wrong = [c for c, ok in N3.claims() if not ok]
    for c, ok in N3.claims():
        print(f"{'ok ' if ok else 'BAD'} claim: {c}")
    if bad or wrong:
        raise SystemExit(f"{len(bad)} spoken numbers and {len(wrong)} claims don't match the summaries")
    print(f"{len(rows)} spoken numbers and {len(N3.claims())} claims, all as the summaries have them")
    return rows


def notes_table(record: Path = D.VID / "final_narrated_record.json") -> str:
    """The script with its times in the cut as encoded (the narrated cut's record), for notes/twin_video.md."""
    rec = json.loads(Path(record).read_text())
    rows = rec["narration"]["placed"]
    out = ["| Time | Part | Line |", "|---|---|---|"]
    for r in rows:
        out.append(f"| {_mmss(r['t'])}-{_mmss(r['end'])} | {SECTION.get(r['seg'], r['seg'])} | {r['text']} |")
    return "\n".join(out)


def _mmss(t: float) -> str:
    return f"{int(t // 60)}:{int(t % 60):02d}"


if __name__ == "__main__":
    os.environ.setdefault("TWIN_VIDEO_NARRATION", "1")         # the narrated cut's timing (compose.NARRATE)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "tts":
        a = speak_all(set(sys.argv[2:]) or None)
        print(f"{len(a)} lines, {sum(len(y) for y in a.values()) / SR / 60:.2f} min of speech in {NDIR}")
    elif cmd == "check":
        check()
    elif cmd == "nums":                                        # round 3: every spoken number against the summaries
        check_numbers()
    elif cmd == "table":                                       # the script with its times, for the notes
        print(notes_table(Path(sys.argv[2]) if len(sys.argv) > 2 else D.VID / "final_narrated_record.json"))
    elif cmd in ("plan", "track"):
        from . import compose as C
        rec = C.plan_record()
        wav = Path(tempfile.gettempdir()) / "twin_narration.wav"
        placed = track(rec, marks(rec), rec["total_s"], wav, NDIR / "narration.srt" if cmd == "track" else None)
        for p in placed:
            print(f"{clock(p['t']):>7s}-{clock(p['end']):>7s}  {p['seg']:9s} {p['id']:8s} {p['text'][:90]}"
                  + (f"   !! {'; '.join(p['warn'])}" if p["warn"] else ""))
        if cmd == "plan":
            print(plan_table(placed, rec))
    else:
        raise SystemExit(__doc__)
