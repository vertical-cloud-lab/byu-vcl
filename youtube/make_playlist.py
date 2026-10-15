"""Create (or extend) an unlisted playlist on the BYU VCL channel from a list of video ids.

Needs the FULL token (playlists.insert requires the youtube / youtube.force-ssl scope, which the upload-only token
does not have), so this only works in an @claude-youtube run (or locally with YOUTUBE_TOKEN_PICKLE_B64 set):

    python youtube/make_playlist.py --title "rePowder atomizer tutorials (draft)" --ids A1b2C3d4E5f ... [--privacy unlisted]
    python youtube/make_playlist.py --playlist-id PLxxxx --ids ...        # add to an existing playlist

Prints the playlist URL. Idempotent on the video side: ids already in the playlist are skipped.
"""
import argparse
from yt_service import get_youtube_service


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title")
    ap.add_argument("--description", default="")
    ap.add_argument("--privacy", choices=["private", "unlisted", "public"], default="unlisted")
    ap.add_argument("--playlist-id")
    ap.add_argument("--ids", nargs="+", required=True, help="video ids in playlist order")
    a = ap.parse_args()
    yt = get_youtube_service("full")
    pid = a.playlist_id
    if not pid:
        if not a.title:
            raise SystemExit("--title is required when creating a playlist")
        r = yt.playlists().insert(part="snippet,status", body={
            "snippet": {"title": a.title, "description": a.description},
            "status": {"privacyStatus": a.privacy}}).execute()
        pid = r["id"]
        print("created playlist", pid)
    have = set()
    token = None
    while True:
        r = yt.playlistItems().list(part="snippet", playlistId=pid, maxResults=50, pageToken=token).execute()
        have |= {i["snippet"]["resourceId"]["videoId"] for i in r["items"]}
        token = r.get("nextPageToken")
        if not token:
            break
    for vid in a.ids:
        if vid in have:
            print("already in playlist:", vid); continue
        yt.playlistItems().insert(part="snippet", body={"snippet": {
            "playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
        print("added", vid)
    print(f"https://www.youtube.com/playlist?list={pid}")


if __name__ == "__main__":
    main()
