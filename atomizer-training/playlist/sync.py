"""Titles, descriptions and one playlist for the atomizer videos on the BYU VCL channel, all from catalog.py.

    python sync.py plan [--ref <sha>]               # check the catalog, write descriptions.md; no YouTube calls
    python sync.py backup                           # save every catalogued video's current title, description, tags
    python sync.py apply --ref <sha>                # update the videos, then create, fill and order the playlist
    python sync.py restore <backup.json> [id ...]   # put backed-up titles, descriptions and tags back

`--ref` is the commit the GitHub links point at. It has to be pushed, and its timestamps.md has to carry the catalog's
titles as headings already (tools/make_timestamps.py takes them from videos.json), or the per-video links would miss;
apply checks both and stops otherwise. Once PR #255 is merged, `apply --ref main` points every link at the living docs.

Editing the videos and the playlist needs the full token (the youtube scope), so apply, backup and restore run only in
an @claude-youtube run or a local shell with YOUTUBE_TOKEN_PICKLE_B64 set. Re-running is safe: a video whose title,
description and tags already match is skipped, so an interrupted run (quota, network) resumes where it stopped.
"""
import argparse, json, os, re, subprocess, sys, time, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
sys.path.insert(0, REPO)
from catalog import PLAYLIST, VIDEOS, SUPERSEDED, TAGS

GH = "https://github.com/vertical-cloud-lab/byu-vcl"
PR = f"{GH}/pull/255"
STATE = f"{HERE}/state.json"
WATCH = "https://www.youtube.com/watch?v="


def ts(s):
    s = int(s); h, m, sec = s // 3600, s // 60 % 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def slug(heading):
    """GitHub's anchor for a markdown heading: lower case, letters/digits/marks/_/- kept, spaces to hyphens."""
    s = "".join(c for c in heading.strip().lower() if c in " -_" or unicodedata.category(c)[0] in "LNM")
    return s.replace(" ", "-")


def git_show(ref, path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def load_state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {}


class Docs:
    """What the GitHub links point at, read from the commit itself so that a link is only written if it resolves."""

    def __init__(self, ref):
        self.ref = ref
        # "REF" (plan's placeholder) and "main" (which may not have the files yet) are read from the working tree
        self.checked = ref not in ("REF", "main")
        read = (lambda p: git_show(ref, p)) if self.checked else (lambda p: open(f"{REPO}/{p}", encoding="utf-8").read())
        log = read("atomizer-training/timestamps.md")
        if log is None:
            raise SystemExit(f"{ref} has no atomizer-training/timestamps.md (is it a commit on this repo?)")
        self.headings = {l[3:].strip() for l in log.splitlines() if l.startswith("## ")}
        self.notes = {}
        for g in "ABCDE":
            text = read(f"atomizer-training/notes/group{g}.md") or ""
            for l in text.splitlines():
                m = re.match(r"^## ([A-Za-z0-9_-]{11}) ", l)
                if m:
                    self.notes[m.group(1)] = (f"notes/group{g}.md", slug(l[3:]))

    def url(self, path="", anchor=""):
        kind = "blob" if "." in path.rsplit("/", 1)[-1] else "tree"
        return f"{GH}/{kind}/{self.ref}/atomizer-training" + (f"/{path}" if path else "") + (f"#{anchor}" if anchor else "")

    def links(self, v):
        """The 'On GitHub' block for one video."""
        sop = ("Operating procedure (SOP), each step linked to the moment of video it comes from", self.url("sop.md"))
        if v["kind"] == "recording":
            if v["title"] not in self.headings:
                raise SystemExit(f"{v['id']}: no heading '## {v['title']}' in timestamps.md at {self.ref}. "
                                 f"Update videos.json, run tools/make_timestamps.py, commit and push first.")
            out = [sop, ("This video, moment by moment (timestamp log)", self.url("timestamps.md", slug(v["title"])))]
            if v["id"] in self.notes:
                path, anchor = self.notes[v["id"]]
                out.append(("Notes: summary, steps, numbers, open questions", self.url(path, anchor)))
            else:
                raise SystemExit(f"{v['id']}: no section in notes/ at {self.ref}")
            out.append(("Transcript (Whisper large-v3-turbo)", self.url(f"transcripts/whisper/{v['id']}.txt")))
        elif v["kind"] == "tutorial":
            out = [("How the tutorials are made: scripts, outlines, build", self.url("tutorials/README.md")), sop,
                   ("The 3D model and step animations", self.url("viz3d/README.md"))]
        elif v["kind"] == "stitch":
            out = [("Every clip, with a link to its source moment", self.url("stitch/edl.md")),
                   ("How the cut was made", self.url("stitch/README.md")), sop]
        else:
            out = [sop]
        out.append(("Everything: SOP, timestamp log, transcripts, 3D animations, tutorials", self.url()))
        out.append(("Discussion", PR))
        return out


def describe(v, docs, pid):
    if "body" in v:                          # a description written elsewhere, kept as it is
        lines = [v["body"].rstrip()]
    else:
        lines = [v["summary"]]
        if v.get("status"):
            lines += ["", v["status"]]
        if v.get("chapters"):
            lines += ["", "Chapters:"] + [f"{ts(t)} {label}" for t, label in v["chapters"]]
        if v.get("sources"):
            lines += ["", v.get("sources_intro", "Clips from the training recordings:")]
            lines += [f"{label} at {ts(t)}: {WATCH}{vid}&t={int(t)}s" for vid, t, label in v["sources"]]
        if v.get("context") or v["kind"] in ("recording", "delivery"):
            about = v.get("context", "")
            if v["kind"] in ("recording", "delivery"):
                about += f" Originally titled “{v['was']}”" + (f"; the SOP cites it as {v['cite']}." if v.get("cite") else ".")
            lines += ["", about.strip()]
        lines += ["", "On GitHub (vertical-cloud-lab/byu-vcl):"]
        lines += [f"{name}: {url}" for name, url in v.get("links", []) + docs.links(v)]
    lines += ["", f"Playlist, with the tutorials and every recording in order: https://www.youtube.com/playlist?list={pid}"]
    return "\n".join(lines)


def describe_superseded(s, pid):
    return "\n".join([f"Superseded by {WATCH}{s['by']}. {s['why']}", "",
                      f"The current tutorials, and every atomizer recording: https://www.youtube.com/playlist?list={pid}",
                      "", "This upload is kept only until it is deleted."])


def playlist_description(docs):
    def span(pred):
        n = [i + 1 for i, v in enumerate(VIDEOS) if pred(v)]
        return f"{n[0]}–{n[-1]}" if len(n) > 1 else str(n[0]) if n else "–"
    return PLAYLIST["description"].format(
        tutorials=span(lambda v: v["kind"] == "tutorial"), stitch=span(lambda v: v["kind"] == "stitch"),
        cups=span(lambda v: "body" in v), recordings=span(lambda v: v["kind"] in ("recording", "delivery")),
        folder=docs.url(), sop=docs.url("sop.md"), pr=PR)


def check(title, desc, v=None):
    errs = []
    if len(title) > 100: errs.append(f"title is {len(title)} characters (max 100)")
    for name, text in (("title", title), ("description", desc)):
        if "<" in text or ">" in text: errs.append(f"{name} contains < or >")
    if len(desc.encode()) > 5000: errs.append(f"description is {len(desc.encode())} bytes (max 5000)")
    ch = (v or {}).get("chapters") or []
    if ch:
        if ch[0][0] != 0: errs.append("chapters do not start at 0:00")
        if len(ch) < 3: errs.append("fewer than 3 chapters")
        for (a, _), (b, _) in zip(ch, ch[1:]):
            if b - a < 10: errs.append(f"chapter at {ts(a)} is shorter than 10 s")
        if v.get("seconds") and v["seconds"] - ch[-1][0] < 10: errs.append("last chapter is shorter than 10 s")
    return errs


def seconds(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


DURATION = {v["id"]: seconds(v["duration"]) for v in json.load(open(f"{ROOT}/videos.json"))}


def render_all(docs, pid):
    out, bad = [], []
    ids = [v["id"] for v in VIDEOS] + [s["id"] for s in SUPERSEDED]
    if len(ids) != len(set(ids)):
        bad.append("a video is listed twice")
    for v in VIDEOS:
        d = describe(v, docs, pid)
        bad += [f"{v['id']}: {e}" for e in check(v["title"], d, {**v, "seconds": v.get("seconds") or DURATION.get(v["id"])})]
        out.append((v, v["title"], d))
    for s in SUPERSEDED:
        d = describe_superseded(s, pid)
        bad += [f"{s['id']}: {e}" for e in check(s["title"], d)]
        out.append((s, s["title"], d))
    pd = playlist_description(docs)
    if len(pd.encode()) > 5000 or "<" in pd or ">" in pd: bad.append("playlist description too long or has < >")
    if bad:
        raise SystemExit("catalog problems:\n  " + "\n  ".join(bad))
    return out, pd


def cmd_plan(args):
    st = load_state()
    docs = Docs(args.ref or st.get("ref") or "REF")
    pid = st.get("playlist_id", "PLAYLIST_ID")
    rendered, pd = render_all(docs, pid)
    md = ["# Atomizer videos on YouTube: titles and descriptions", "",
          f"Generated by [`sync.py`](sync.py) `plan` from [`catalog.py`](catalog.py), links at `{docs.ref}`. "
          "This is what `apply` writes; the video's previous title is under each heading.", "",
          f"## Playlist: {PLAYLIST['title']}", "", f"{PLAYLIST['privacy']} · {len(VIDEOS)} videos", "", "```", pd, "```", ""]
    for n, (v, title, d) in enumerate(rendered, 1):
        tag = f"{n}." if n <= len(VIDEOS) else "not in the playlist:"
        md += [f"## {tag} {title}", "", f"[`{v['id']}`]({WATCH}{v['id']}) · was *{v['was']}*", "", "```", d, "```", ""]
    open(f"{HERE}/descriptions.md", "w", encoding="utf-8").write("\n".join(md))
    print(f"ok: {len(VIDEOS)} in the playlist, {len(SUPERSEDED)} superseded; descriptions.md written (links at {docs.ref})")


def youtube():
    from youtube.yt_service import get_youtube_service
    return get_youtube_service("full")


def fetch(yt, ids):
    got = {}
    for k in range(0, len(ids), 50):
        for item in yt.videos().list(part="snippet,status", id=",".join(ids[k:k + 50])).execute()["items"]:
            got[item["id"]] = item
    missing = set(ids) - set(got)
    if missing:
        raise SystemExit(f"not found on the channel: {sorted(missing)}")
    return got


KEEP = ("title", "description", "tags", "categoryId", "defaultLanguage", "defaultAudioLanguage")


def cmd_backup(args):
    yt = youtube()
    ids = [v["id"] for v in VIDEOS] + [s["id"] for s in SUPERSEDED]
    got = fetch(yt, ids)
    path = f"{HERE}/backup-{time.strftime('%Y-%m-%d')}.json"
    if os.path.exists(path):
        raise SystemExit(f"{path} exists; keep the first backup of the day")
    out = {"taken_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "videos": {i: {"snippet": {k: got[i]["snippet"][k] for k in KEEP if k in got[i]["snippet"]},
                          "privacyStatus": got[i]["status"]["privacyStatus"]} for i in ids}}
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("backed up", len(ids), "videos to", os.path.basename(path))


def update_snippet(yt, item, title, desc, tags=None, category=None):
    """videos.update replaces the whole snippet, so carry over every field we do not mean to change."""
    old = item["snippet"]
    new = {k: old[k] for k in ("categoryId", "defaultLanguage", "defaultAudioLanguage") if k in old}
    new["title"], new["description"] = title, desc
    new["tags"] = tags if tags is not None else old.get("tags", [])
    if category:
        new["categoryId"] = category
    same = (old["title"] == title and old.get("description", "") == desc and old.get("tags", []) == new["tags"]
            and old.get("categoryId") == new["categoryId"])
    if same:
        return False
    yt.videos().update(part="snippet", body={"id": item["id"], "snippet": new}).execute()
    return True


def merged_tags(old, extra):
    out = list(old or [])
    for t in extra:
        if t.lower() not in {o.lower() for o in out}:
            out.append(t)
    return out


def ensure_playlist(yt, st, docs):
    pid = st.get("playlist_id")
    if not pid:      # an earlier run may have created it before failing
        token = None
        while True:
            r = yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=token).execute()
            pid = next((p["id"] for p in r["items"] if p["snippet"]["title"] == PLAYLIST["title"]), None)
            token = r.get("nextPageToken")
            if pid or not token:
                break
    if not pid:
        r = yt.playlists().insert(part="snippet,status", body={
            "snippet": {"title": PLAYLIST["title"], "description": playlist_description(docs)},
            "status": {"privacyStatus": PLAYLIST["privacy"]}}).execute()
        pid = r["id"]
        print("created playlist", pid)
    st["playlist_id"] = pid
    json.dump(st, open(STATE, "w"), indent=1)
    return pid


def sync_items(yt, pid, want):
    def items():
        out, token = [], None
        while True:
            r = yt.playlistItems().list(part="snippet", playlistId=pid, maxResults=50, pageToken=token).execute()
            out += r["items"]; token = r.get("nextPageToken")
            if not token:
                return sorted(out, key=lambda i: i["snippet"]["position"])
    have = items()
    for it in have:
        if it["snippet"]["resourceId"]["videoId"] not in want:
            yt.playlistItems().delete(id=it["id"]).execute()
            print("removed from playlist:", it["snippet"]["resourceId"]["videoId"])
    present = {it["snippet"]["resourceId"]["videoId"] for it in have}
    for pos, vid in enumerate(want):
        if vid not in present:
            yt.playlistItems().insert(part="snippet", body={"snippet": {
                "playlistId": pid, "position": pos, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
            print(f"added {vid} at {pos + 1}")
    for pos, vid in enumerate(want):       # then fix the order, one move at a time
        cur = items()
        it = next(i for i in cur if i["snippet"]["resourceId"]["videoId"] == vid)
        if it["snippet"]["position"] != pos:
            yt.playlistItems().update(part="snippet", body={"id": it["id"], "snippet": {
                "playlistId": pid, "position": pos, "resourceId": it["snippet"]["resourceId"]}}).execute()
            print(f"moved {vid} to {pos + 1}")


def cmd_apply(args):
    st = load_state()
    ref = args.ref or st.get("ref")
    if not ref:
        raise SystemExit("--ref <commit> is required the first time")
    if ref != "main" and subprocess.run(["git", "-C", REPO, "branch", "-r", "--contains", ref],
                                        capture_output=True, text=True).stdout.strip() == "":
        raise SystemExit(f"{ref} is not on any remote branch: push it first, or the links would 404")
    docs = Docs(ref)
    yt = youtube()
    render_all(docs, "PLAYLIST_ID")            # validate everything before touching anything
    pid = ensure_playlist(yt, st, docs)
    rendered, pd = render_all(docs, pid)
    got = fetch(yt, [v["id"] for v, _, _ in rendered])
    changed = 0
    for v, title, desc in rendered:
        superseded = "by" in v
        tags = None if superseded else merged_tags(got[v["id"]]["snippet"].get("tags"), TAGS + v.get("tags", []))
        if update_snippet(yt, got[v["id"]], title, desc, tags, v.get("category")):
            changed += 1
            print("updated", v["id"], "->", title)
        else:
            print("unchanged", v["id"])
    sync_items(yt, pid, [v["id"] for v in VIDEOS])
    p = yt.playlists().list(part="snippet,status", id=pid).execute()["items"][0]
    if (p["snippet"]["title"], p["snippet"].get("description", "")) != (PLAYLIST["title"], pd):
        yt.playlists().update(part="snippet,status", body={"id": pid, "snippet": {
            "title": PLAYLIST["title"], "description": pd}, "status": p["status"]}).execute()
        print("playlist title/description updated")
    st.update({"playlist_id": pid, "playlist_url": f"https://www.youtube.com/playlist?list={pid}",
               "privacy": p["status"]["privacyStatus"], "ref": ref,
               "applied_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "order": [{"id": v["id"], "title": v["title"]} for v in VIDEOS],
               "superseded": [{"id": s["id"], "title": s["title"], "by": s["by"]} for s in SUPERSEDED]})
    json.dump(st, open(STATE, "w"), indent=1, ensure_ascii=False)
    print(f"{changed} videos updated; playlist {st['playlist_url']}")


def cmd_restore(args):
    backup = json.load(open(args.backup))["videos"]
    ids = args.ids or list(backup)
    yt = youtube()
    got = fetch(yt, ids)
    for i in ids:
        old = backup[i]["snippet"]
        if update_snippet(yt, got[i], old["title"], old.get("description", ""), old.get("tags", []), old.get("categoryId")):
            print("restored", i, "->", old["title"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan"); p.add_argument("--ref")
    sub.add_parser("backup")
    p = sub.add_parser("apply"); p.add_argument("--ref")
    p = sub.add_parser("restore"); p.add_argument("backup"); p.add_argument("ids", nargs="*")
    args = ap.parse_args()
    {"plan": cmd_plan, "backup": cmd_backup, "apply": cmd_apply, "restore": cmd_restore}[args.cmd](args)


if __name__ == "__main__":
    main()
