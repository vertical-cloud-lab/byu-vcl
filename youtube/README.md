# YouTube automation — BYU Vertical Cloud Lab channel

Target: **BYU Vertical Cloud Lab** ([@BYUVerticalCloudLab](https://www.youtube.com/@BYUVerticalCloudLab),
`UCKC7WzMu6QEh7O55zZlT2lw`), the channel owned directly by byu.vcl@gmail.com. Not
*BYU VCL Hardware Streams* (`UCZ5KNGkEEqDsRVn0Nlfn0IA`), the livestream Brand Account
that the same login can also pick on the consent screen — pick the right one there,
the token script refuses the other.

## Two tokens, two blast radii

An API key cannot upload: `videos.insert` needs OAuth as the channel. Service accounts
cannot be attached to a channel either. So both credentials are refresh tokens, stored
the way [streamingLambda](https://github.com/vertical-cloud-lab/streamingLambda) and
me-en-372 already do it: the pickled `Credentials`, base64-encoded into one string.

| Secret | Scopes | Where | Who can use it |
| --- | --- | --- | --- |
| `YOUTUBE_UPLOAD_TOKEN_PICKLE_B64` | `youtube.upload`, `youtube.readonly` | Repo secret, `claude.yml` env, `.claude/settings.local.json` | Every `@claude` run |
| `YOUTUBE_TOKEN_PICKLE_B64` | `youtube`, `youtube.force-ssl`, `youtube.upload`, `youtube.readonly`, `yt-analytics.readonly` | `youtube-admin` environment only | `@claude-youtube`, from sgbaird, after approval |

`youtube.upload` can add videos and set thumbnails but **cannot delete or edit** anything,
so the worst an upload-only token can do is unwanted uploads. Deleting, editing metadata,
playlists and captions need the full token.

The full token is behind three gates in `.github/workflows/claude-youtube.yml`: the job
only starts for `@claude-youtube` posted by sgbaird; the `youtube-admin` environment
requires sgbaird to approve each run (Actions → the waiting run → *Review deployments*);
and the environment only deploys from `main`. `main` itself is unprotected — public
repos cannot have the push rulesets ME-EN-372 uses to lock `.github/**` — so the
approval step is the gate that actually holds. The upload token, like every other repo
secret, is readable by anyone with write access who writes a workflow for it; that is
accepted given its scope.

`claude.yml` skips any comment containing `@claude-youtube`, since that tag also
contains `@claude` and would otherwise start both workflows.

## Usage

```bash
pip install -r youtube/requirements.txt
python youtube/yt_service.py                        # which channel, which scopes
python youtube/yt_service.py upload clip.mp4 --title "OT-2 run 12"
python youtube/yt_service.py --full                 # full token (admin runs only)
```

```python
from youtube.yt_service import get_youtube_service, upload_video
```

Uploads default to `private`. Videos uploaded through the API from an unaudited Cloud
project are locked private anyway; publish from YouTube Studio.

## The OAuth client

Desktop-app OAuth client in a Cloud project owned by **vcl.hardware.streams@gmail.com**,
not byu.vcl@gmail.com. The client does not have to belong to the account whose channel it
controls — byu.vcl only clicks through consent — and Google Cloud now refuses console
access to any account without 2-step verification, which byu.vcl (a shared login) does
not have. vcl.hardware.streams does.

The consent screen must be **published "In production"**. In "Testing", refresh tokens
expire after 7 days; that, not anything account-specific, is what kept the streamingLambda
and me-en-372 tokens alive. Production with no verification is fine for our own use — the
consent screen just shows "Google hasn't verified this app" (Advanced → continue).

## Minting / re-minting

Needed if access is revoked at [myaccount.google.com/connections](https://myaccount.google.com/connections),
the token sits unused for 6 months, or the scopes change. Save the client JSON as
`youtube/client_secret.json` (gitignored), then:

```bash
python youtube/generate_youtube_token.py --profile upload --to-local --to-github
python youtube/generate_youtube_token.py --profile full --to-github
```

Sign in as byu.vcl@gmail.com and choose **BYU Vertical Cloud Lab**. The script checks
with Google's `tokeninfo` that exactly the profile's scopes were granted (granular consent
lets boxes be unticked, and a widened token would defeat the point of upload-only),
checks the channel id, and only then writes the value — to `settings.local.json` and/or
`gh secret set` over stdin. It never prints it. `--no-browser` prints the consent URL
instead of opening the default browser, for when a particular Chrome profile has to sign in.
