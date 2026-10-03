# The atomizer videos on YouTube: one playlist, titles and descriptions

**Playlist: <https://www.youtube.com/playlist?list=PLB8wxmcPAjLM>** (unlisted, 34 videos, BYU Vertical Cloud Lab channel)

The atomizer videos went up fast during installation and training week. Their titles were things like *Atomizer
Training Video 6* and *Atomizer Fri Oct 2 pt1*, almost none had a description, and there was no playlist. On
2026-10-03 every one of them was renamed and described from [`catalog.py`](catalog.py), then gathered into one playlist
in this order:

| # | What |
| --- | --- |
| 1–4 | Narrated tutorials 0–3: the machine, then before, during and after a run (draft 3, [`../tutorials/`](../tutorials/README.md)) |
| 5 | Tutorial: making the aluminum cups and plugs (issue #248) |
| 6–7 | Every recorded step in the order of a run, a 6 h 49 min raw cut in two parts ([`../stitch/`](../stitch/README.md)) |
| 8–34 | The recordings, in the order they were made: delivery and installation (Jun–Sep), commissioning (Sep 28), training day 1 (Sep 29), day 2 (Sep 30), dosing the next charge (Sep 30), the first run on our own (Oct 2) |

YouTube has no sections inside a playlist, so the titles carry them:
- *Atomizer tutorial N: …*;
- *Atomizer, every recorded step (part N of 2): …*;
- *Atomizer ‹stage› (‹date›): …* for the recordings.

The recordings keep *training video N*, so the SOP's T1–T9 still match.

Every description has:
- a summary;
- YouTube chapters from the [timestamp log](../timestamps.md), or for the tutorials from their own auto-captions;
- when the video was recorded and who is in it;
- its original title and the SOP's code for it.

It ends with links to the SOP, the video's own section of the timestamp log, its notes and its transcript, all
pinned at the commit [`a0e4b5f`](https://github.com/vertical-cloud-lab/byu-vcl/tree/a0e4b5f/atomizer-training). Every
link and anchor was checked against GitHub's rendered pages before upload. Each tutorial also lists the training-video
moments its clips come from. [`descriptions.md`](descriptions.md) has every title and description exactly as written.

The repo follows the new titles. [`../videos.json`](../videos.json) keeps each video's original title as `uploaded_as`
(`description` there is still the uploader's original one). The headings of [`../timestamps.md`](../timestamps.md) and
the keyframe pages use the new titles too.

## What changed on YouTube, and what did not

- **Titles and descriptions of 43 videos.** That is the 34 in the playlist and 9 superseded uploads. The 34 also gained the
  same six tags, on top of any they had, and the June unboxing clip's category moved from Entertainment to Science & Technology.
- **The 9 superseded uploads** are tutorial drafts 1 and 2 and the first upload of the cups tutorial. They are now titled
  `[superseded] …`, their descriptions point to the replacement, and they are not in the playlist.
- **Nothing was deleted and no video's privacy changed.** The mix of public and unlisted videos is as it was.
- **To undo**, run `python sync.py restore backup-2026-10-03.json [id ...]`. It puts back the title, description, tags
  and category each video had before, all saved in [`backup-2026-10-03.json`](backup-2026-10-03.json).
  [`state.json`](state.json) records the playlist id and what was applied.

## Running it

```bash
pip install -r ../../youtube/requirements.txt
python sync.py plan --ref <sha>     # validate the catalog, rewrite descriptions.md; no YouTube calls
python sync.py backup               # before a big change: current titles, descriptions, tags of every video
python sync.py apply --ref <sha>    # update the videos, then create / fill / reorder the playlist
```

- **`apply` needs the full token**, so it only works in an `@claude-youtube` run or in a shell with
  `YOUTUBE_TOKEN_PICKLE_B64` (see [`../../youtube/README.md`](../../youtube/README.md)).
- **`plan` fails if a heading or notes section is missing**, so a link that would miss stops it before upload.
  `apply` also refuses a commit that is not on a remote.
- **It is idempotent.** Videos that already match are skipped, and the playlist is synced to the catalog's order.
  Interrupted runs (quota, network) resume.
- **After PR #255 merges**, run `apply --ref main` to point every link at the living docs instead of the pinned commit.
- **For a new tutorial draft**, put its id in `TUTORIALS` in place of the old one and move the old one to `SUPERSEDED`,
  then `apply`. That renames both, swaps the playlist entry and leaves the old upload labelled.
- **Renaming a recording** also means updating its `title` in `../videos.json` and re-running
  `../tools/make_timestamps.py`, so that its timestamp-log heading (the link's anchor) matches.

## Still open

- **Deleting the 9 superseded uploads** is the user's call: it cannot be undone. Their ids are in `SUPERSEDED` in
  `catalog.py`.
- **The playlist is unlisted.** Anyone who opens a public playlist can watch the unlisted videos in it, so making it
  public would expose the 21 unlisted videos here too (13 of the 34 are public). Check *dosing Al 4047 with Claude* (`dXRB7c6GeDw`) first: a
  personal email is on screen around 50:00.
- **Three descriptions rest on thinner evidence:**
  - The June unboxing clip is not in the indexed set (no transcript, notes or timestamp rows yet), so its summary and
    chapters come from YouTube's auto-captions.
  - The chapters of the silent videos (expert cleaning POV, the two powder-doser sessions) name what the keyframes
    show, so their boundaries can be 30–60 s off.
- **Two June clips are left out:** *Vacuum Multimeter readings* (`ZpVbJW9lBTc`, `0y26-tjXQ1s`) measure the
  resistance of a vacuum's wand and lid, and it is not clear that vacuum belongs to the atomizer.
