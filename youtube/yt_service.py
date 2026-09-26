"""Authenticated YouTube client for the BYU Vertical Cloud Lab channel.

Two credentials, both base64-encoded token.pickle files minted by
generate_youtube_token.py:

    YOUTUBE_UPLOAD_TOKEN_PICKLE_B64  upload + read only. Every @claude run
                                     and .claude/settings.local.json.
    YOUTUBE_TOKEN_PICKLE_B64         full control, including delete. Only in
                                     the `youtube-admin` environment, i.e.
                                     only in @claude-youtube runs.

Refreshing replaces the short-lived access token in memory; the refresh
token inside the pickle never changes, so nothing is written back.

    python youtube/yt_service.py                  # which channel, which scopes
    python youtube/yt_service.py upload clip.mp4 --title "OT-2 run 12"
"""

import argparse
import base64
import os
import pickle

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ENV_VARS = {
    "upload": "YOUTUBE_UPLOAD_TOKEN_PICKLE_B64",
    "full": "YOUTUBE_TOKEN_PICKLE_B64",
}


def get_credentials(access="upload"):
    name = ENV_VARS[access]
    b64 = os.environ.get(name, "").strip()
    if not b64:
        hint = " It only exists in @claude-youtube runs." if access == "full" else ""
        raise SystemExit(f"{name} is not set.{hint} See youtube/README.md.")
    if b64.startswith(name + "="):
        # Pasting "NAME=value" into the secret box breaks unpickling with a
        # confusing "invalid load key" -- it happened in me-en-372.
        print(f"WARNING: {name} starts with its own name; stripping it. Fix the stored secret.")
        b64 = b64[len(name) + 1:]
    creds = pickle.loads(base64.b64decode(b64))
    if not creds.valid:
        creds.refresh(Request())
    return creds


def get_youtube_service(access="upload"):
    return build("youtube", "v3", credentials=get_credentials(access))


def upload_video(path, title, description="", privacy="private", tags=None, category_id="28", access="upload"):
    """Resumable upload; returns the new video id.

    Defaults to private: uploads from an unaudited API project are locked
    private by YouTube regardless, so publish from YouTube Studio.
    """
    youtube = get_youtube_service(access)
    body = {
        "snippet": {"title": title, "description": description, "tags": tags or [], "categoryId": category_id},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(path, chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"uploaded {status.progress():.0%}", flush=True)
    return response["id"]


def main():
    parser = argparse.ArgumentParser(description="YouTube helper for the BYU VCL channel")
    parser.add_argument("--full", action="store_true", help="use the full-control token")
    sub = parser.add_subparsers(dest="cmd")
    up = sub.add_parser("upload")
    up.add_argument("path")
    up.add_argument("--title", required=True)
    up.add_argument("--description", default="")
    up.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    args = parser.parse_args()
    access = "full" if args.full else "upload"

    if args.cmd == "upload":
        video_id = upload_video(args.path, args.title, args.description, args.privacy, access=access)
        print(f"https://www.youtube.com/watch?v={video_id}")
        return

    creds = get_credentials(access)
    channel = build("youtube", "v3", credentials=creds).channels().list(part="snippet", mine=True).execute()["items"][0]
    print(f"{ENV_VARS[access]} -> {channel['snippet']['title']} ({channel['id']})")
    print("scopes:", ", ".join(creds.scopes or []))


if __name__ == "__main__":
    main()
