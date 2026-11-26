"""The campaign video's narration (twin/video/narration.py): the script and its committed audio agree, the cut can be
rebuilt from the committed FLACs without the speech model, and every line fits the narrated, animated cut."""
import builtins
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
SCRIPT = HERE / "twin" / "video" / "narration.json"
NDIR = HERE / "out" / "twin2" / "video" / "narration"


def test_every_line_has_its_audio():
    lines = json.loads(SCRIPT.read_text())["lines"]
    rec = json.loads((NDIR / "lines.json").read_text())
    ids = [ln["id"] for ln in lines]
    assert ids and len(set(ids)) == len(ids)
    assert set(rec["lines"]) == set(ids)
    for ln in lines:
        assert rec["lines"][ln["id"]]["text"] == ln["text"], ln["id"]
        assert (NDIR / f"{ln['id']}.flac").exists(), ln["id"]
        assert ln.get("src"), f"{ln['id']}: say where its numbers come from"


def test_rebuilds_without_the_speech_model(monkeypatch):
    real = builtins.__import__

    def no_kokoro(name, *a, **k):
        if name.startswith("kokoro_onnx"):
            raise ImportError("the committed FLACs should be enough")
        return real(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", no_kokoro)
    sys.path.insert(0, str(HERE))
    from twin.video import narration as N
    audio = N.speak_all()
    assert set(audio) == {ln["id"] for ln in N.lines()}
    assert all(len(y) > N.SR for y in audio.values())


def test_lines_fit_the_narrated_cut():
    env = dict(os.environ, TWIN_VIDEO_NARRATION="1", TWIN_VIDEO_LAB3D="1")
    r = subprocess.run([sys.executable, "-m", "twin.video.narration", "plan"], cwd=HERE, env=env, capture_output=True,
                       text=True)
    assert r.returncode == 0, r.stderr[-3000:]
    out = r.stdout + r.stderr
    assert "!!" not in out and "left out" not in out and "pushed" not in out, out[-3000:]
