"""Keep the 3D print timelapses unlisted and together in one public playlist.

Bambu Studio saves a printer's timelapses as video_YYYY-MM-DD_HH-MM-SS.mp4 and
YouTube keeps the uploaded file name, so the channel's print timelapses can be
found by that alone, plus EXTRA_IDS for any renamed before upload. Uploaded
as public, each one notified the channel's subscribers (byu-vcl#282). This
adds all of them to PLAYLIST_ID, oldest print first, and makes all but
KEEP_PUBLIC unlisted: still playable from the playlist or a link, but off the
channel page.

Private videos are never touched or added. Unlisting does not take back a
notification already sent, and making a once-public video public again does
not send another: YouTube notifies only the first time a video goes public
(support.google.com/youtube/answer/9230970).

    python youtube/print_timelapses.py            # dry run, read-only
    python youtube/print_timelapses.py --apply    # full token: @claude-youtube only
"""

import argparse
import re

from yt_service import get_youtube_service

# "3D Print Timelapses", public, created 2026-10-15.
PLAYLIST_ID = "PLTheyaYPoIfU"

BAMBU_NAME = re.compile(r"^video_(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})\.mp4$")

# Bambu timelapses uploaded under another file name.
EXTRA_IDS = {
    "pupnTi0uMsU",  # .2mm Auger and Cap
}

# A few characteristic ones stay public. Placeholders until Audrey picks
# her favourites (byu-vcl#282); replace this set with her list and re-run.
KEEP_PUBLIC = {
    "JH5PSKreZGs",  # Tensegrity T3 (TT3) First Copilot with Manual Supports Print (CS_001)
    "8FelllY-Z4o",  # TT3_01 Figuring Out TPU Print Parameters (part 1)
    "xVBunPal9Kw",  # TT3_01 Successfully Minimized Wobble
    "Si-RoGM2uqA",  # TT3_01 full plate
    "EmCLms7-Bd8",  # TT3_01 1sne## plate
}


def pages(method, **kwargs):
    token = None
    while True:
        response = method(maxResults=50, pageToken=token, **kwargs).execute()
        yield from response["items"]
        token = response.get("nextPageToken")
        if not token:
            return


def print_time(video):
    """Printer clock from the Bambu file name, else the upload time."""
    m = BAMBU_NAME.match(video.get("fileDetails", {}).get("fileName", ""))
    return f"{m[1]}T{m[2]}:{m[3]}:{m[4]}" if m else video["snippet"]["publishedAt"][:19]


def find_timelapses(youtube):
    channel = youtube.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    uploads = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = list(dict.fromkeys(
        item["contentDetails"]["videoId"]
        for item in pages(youtube.playlistItems().list, part="contentDetails", playlistId=uploads)
    ))
    videos = []
    for k in range(0, len(ids), 50):
        videos += youtube.videos().list(
            part="snippet,status,fileDetails", id=",".join(ids[k:k + 50])
        ).execute()["items"]
    found = [
        v for v in videos
        if v["id"] in EXTRA_IDS or BAMBU_NAME.match(v.get("fileDetails", {}).get("fileName", ""))
    ]
    return sorted(found, key=lambda v: (print_time(v), v["snippet"]["publishedAt"]))


def set_privacy(youtube, video, privacy):
    """videos.update resets every mutable status field it isn't sent, so
    carry over the rest. 16 of the timelapses are Creative Commons, and
    would silently go back to the standard YouTube licence."""
    old = video["status"]
    status = {
        "privacyStatus": privacy,
        "embeddable": old["embeddable"],
        "license": old["license"],
        "publicStatsViewable": old["publicStatsViewable"],
        "selfDeclaredMadeForKids": old.get("selfDeclaredMadeForKids", old.get("madeForKids", False)),
    }
    if "containsSyntheticMedia" in old:
        status["containsSyntheticMedia"] = old["containsSyntheticMedia"]
    new = youtube.videos().update(part="status", body={"id": video["id"], "status": status}).execute()["status"]
    if new["privacyStatus"] != privacy or new["license"] != old["license"]:
        raise SystemExit(f"{video['id']}: update came back as {new}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--apply", action="store_true", help="make the changes (full token)")
    args = parser.parse_args()
    youtube = get_youtube_service("full" if args.apply else "upload")

    timelapses = [v for v in find_timelapses(youtube) if v["status"]["privacyStatus"] != "private"]
    in_playlist = {
        item["contentDetails"]["videoId"]
        for item in pages(youtube.playlistItems().list, part="contentDetails", playlistId=PLAYLIST_ID)
    }
    print(f"{len(timelapses)} timelapses; playlist {PLAYLIST_ID}")

    changes = 0
    for video in timelapses:
        vid, title = video["id"], video["snippet"]["title"]
        now = video["status"]["privacyStatus"]
        want = "public" if vid in KEEP_PUBLIC else "unlisted"
        todo = []
        if vid not in in_playlist:
            todo.append("add to playlist")
        if now != want:
            todo.append(f"{now} -> {want}")
        print(f"{print_time(video)}  {vid}  {now:8}  {'; '.join(todo) or 'ok':32}  {title}")
        if not (todo and args.apply):
            continue
        if vid not in in_playlist:
            youtube.playlistItems().insert(part="snippet", body={"snippet": {
                "playlistId": PLAYLIST_ID,
                "resourceId": {"kind": "youtube#video", "videoId": vid},
            }}).execute()
        if now != want:
            set_privacy(youtube, video, want)
        changes += 1
    print(f"{changes} videos changed" if args.apply else "dry run; --apply to make these changes")


if __name__ == "__main__":
    main()
