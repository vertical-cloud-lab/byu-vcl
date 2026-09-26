"""Mint a YouTube OAuth token for the BYU Vertical Cloud Lab channel.

Run locally; it needs a browser for the one-time consent. The token is stored
the same way as in vertical-cloud-lab/streamingLambda and me-en-372: the whole
pickled google.oauth2.credentials.Credentials, base64-encoded into one string.
The value is never printed. It goes straight to where it is used:

    python youtube/generate_youtube_token.py --profile upload --to-local --to-github
    python youtube/generate_youtube_token.py --profile full --to-github

Profiles (see youtube/README.md for why there are two):

    upload  youtube.upload + youtube.readonly. Can add videos, cannot delete
            or edit anything. Secret YOUTUBE_UPLOAD_TOKEN_PICKLE_B64, a plain
            repo secret available to every @claude run.
    full    Full channel control, including delete. Secret
            YOUTUBE_TOKEN_PICKLE_B64, stored only in the protected
            `youtube-admin` environment that claude-youtube.yml uses.

--no-browser prints the consent URL instead of opening the default browser,
for when a specific Chrome profile has to do the signing in.
"""

import argparse
import base64
import json
import os
import pickle
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
REPO = "vertical-cloud-lab/byu-vcl"

# "BYU Vertical Cloud Lab" (@BYUVerticalCloudLab), byu.vcl@gmail.com's own
# channel. Not "BYU VCL Hardware Streams" (UCZ5KNGkEEqDsRVn0Nlfn0IA), a Brand
# Account that the same login can also pick on the consent screen.
TARGET_CHANNEL_ID = "UCKC7WzMu6QEh7O55zZlT2lw"

YT = "https://www.googleapis.com/auth/"
PROFILES = {
    "upload": {
        "scopes": [YT + "youtube.upload", YT + "youtube.readonly"],
        "secret": "YOUTUBE_UPLOAD_TOKEN_PICKLE_B64",
        "environment": None,
    },
    "full": {
        "scopes": [
            YT + "youtube",
            YT + "youtube.force-ssl",
            YT + "youtube.upload",
            YT + "youtube.readonly",
            YT + "yt-analytics.readonly",
        ],
        "secret": "YOUTUBE_TOKEN_PICKLE_B64",
        "environment": "youtube-admin",
    },
}


def granted_scopes(creds):
    """Ask Google which scopes the access token really carries.

    Checking what we *requested* is not enough: granular consent lets the
    user untick boxes, and a stray include_granted_scopes would widen the
    token with earlier grants. Upload-only has to mean upload-only.
    """
    query = urllib.parse.urlencode({"access_token": creds.token})
    with urllib.request.urlopen(f"https://oauth2.googleapis.com/tokeninfo?{query}") as r:
        return set(json.load(r)["scope"].split())


def verify(creds, profile, channel_id):
    from googleapiclient.discovery import build

    wanted = set(PROFILES[profile]["scopes"])
    got = granted_scopes(creds)
    if got != wanted:
        print(f"Scope mismatch.\n  missing: {sorted(wanted - got)}\n  extra:   {sorted(got - wanted)}")
        return False
    print("Granted scopes match the profile:", ", ".join(sorted(s.removeprefix(YT) for s in got)))

    youtube = build("youtube", "v3", credentials=creds)
    items = youtube.channels().list(part="id,snippet", mine=True).execute().get("items", [])
    if not items:
        print("The chosen identity owns no YouTube channel.")
        return False
    channel = items[0]
    print(f"Token controls: {channel['snippet']['title']} ({channel['id']})")
    if channel["id"] != channel_id:
        print(f"Expected {channel_id}. Re-run and pick that channel on the chooser page.")
        return False
    return True


def write_local(name, value):
    """Set env[name] in .claude/settings.local.json, keeping everything else."""
    path = REPO_ROOT / ".claude" / "settings.local.json"
    settings = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    settings.setdefault("env", {})[name] = value
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)
    print(f"Wrote env.{name} to {path.relative_to(REPO_ROOT)}")


def write_github(name, value, environment):
    """gh reads the value from stdin, so it never appears in argv or a log."""
    cmd = ["gh", "secret", "set", name, "--repo", REPO]
    if environment:
        cmd += ["--env", environment]
    subprocess.run(cmd, input=value, text=True, check=True)
    where = f"environment {environment}" if environment else "repo secrets"
    print(f"Set {name} in {REPO} {where}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--profile", choices=PROFILES, required=True)
    parser.add_argument("--client-secret", type=Path, default=HERE / "client_secret.json")
    parser.add_argument("--channel-id", default=TARGET_CHANNEL_ID)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--to-local", action="store_true", help="write .claude/settings.local.json")
    parser.add_argument("--to-github", action="store_true", help="gh secret set on byu-vcl")
    args = parser.parse_args()

    if not (args.to_local or args.to_github):
        parser.error("choose at least one of --to-local / --to-github; the value is never printed")
    if not args.client_secret.exists():
        raise SystemExit(
            f"Missing {args.client_secret}. Download the Desktop-app OAuth client JSON "
            "(see youtube/README.md) and save it there; it is gitignored."
        )

    from google_auth_oauthlib.flow import InstalledAppFlow

    profile = PROFILES[args.profile]
    flow = InstalledAppFlow.from_client_secrets_file(str(args.client_secret), profile["scopes"])
    # Force the account/channel chooser and the consent screen: without it
    # Google may silently reuse whichever identity the browser has active,
    # and "consent" guarantees a refresh token even on a repeat grant.
    creds = flow.run_local_server(
        port=8765,
        prompt="consent select_account",
        open_browser=not args.no_browser,
    )
    if not creds.refresh_token:
        raise SystemExit("No refresh token returned. Revoke the app at "
                         "https://myaccount.google.com/connections and re-run.")
    if not verify(creds, args.profile, args.channel_id):
        raise SystemExit("Not storing a token that failed verification.")

    value = base64.b64encode(pickle.dumps(creds)).decode()
    if args.to_local:
        write_local(profile["secret"], value)
    if args.to_github:
        write_github(profile["secret"], value, profile["environment"])


if __name__ == "__main__":
    sys.exit(main())
