# Building the vertical cloud lab, prompt by prompt

**[vertical-lab-prompts.pdf](vertical-lab-prompts.pdf)** holds every comment and prompt Sterling wrote while the
vertical-lab visualizations were built. They come from issue
[#303](https://github.com/vertical-cloud-lab/byu-vcl/issues/303), PR
[#318](https://github.com/vertical-cloud-lab/byu-vcl/pull/318) and the threads spun off from them, from 27 October to
24 November 2026. Each comment is given whole and linked to the original on GitHub. After each comes what it produced:

- the reply and how its run ended;
- the job run;
- the videos it put on the lab's YouTube channel;
- the PRs and issues it opened;
- the commit it pushed up to;
- a thumbnail of the reply's first figure.

The last part lists related prompts and comments in
[digital-alloy-lab](https://github.com/vertical-cloud-lab/digital-alloy-lab) (DAL), each with a 5–7 word label.

## What's in the PDF

1. **Cover:** the counts. That's 83 comments in 16 threads, 73 of them starting a run and one handing off ten more,
   plus the run time, the videos and the PRs opened.
2. **Contents:** one row per comment, with its opening words, linked to its entry. A second table lists the threads.
3. **The comments and prompts, in order,** grouped by day (Mountain time, with UTC in brackets). Each entry is the
   comment as GitHub renders it, then a box with what it produced. The `@claude-super` prompt of 20 Nov also lists
   the ten runs it handed off, with each one's reply.
4. **Related prompts and comments in DAL,** in six groups. Each line has its label, where the link goes, who wrote it
   and when.
5. **How this was made.**

The PDF has an outline (bookmarks) by day and by entry, and every link in it is live.

## Rebuilding it

```bash
pip install playwright pillow            # Playwright drives the installed Chrome; no browser download
python3 docs/vertical-lab-prompts/fetch.py   # gh api -> data/, images/, thumbs/
python3 docs/vertical-lab-prompts/build.py   # data/ -> vertical-lab-prompts.pdf
```

`fetch.py` needs `gh` signed in (any token that reads public repos), plus YouTube's oEmbed endpoint for the titles
and channels of the linked videos.

## Files

| File | What it is |
|---|---|
| `vertical-lab-prompts.pdf` | The log |
| `fetch.py` | Reads the threads, replies, job runs and DAL links with `gh api`, and writes `data/log.json` |
| `build.py` | Renders `data/log.json` to HTML and prints it to PDF with Chrome |
| `dal_links.json` | The DAL links and their labels, picked by hand |
| `data/log.json` | The snapshot the PDF was built from: each comment in markdown and as GitHub's HTML, plus each reply's links |
| `data/youtube.json` | Title and channel of every YouTube video the replies link (from oEmbed) |
| `images/` | The screenshots in Sterling's comments |
| `thumbs/` | The first figure of each reply, shrunk |

## How the pairing works, and its limits

- **The comments:** every issue body, comment, review and review comment by `sgbaird` in the threads listed in
  `fetch.py` (`THREADS`). `fetch.py` warns about any newer thread that names #303 or #318 in its title.
  - #318's PR body is left out. It was opened under Sterling's name from a run's link, and Claude wrote its text.
- **The replies:** a run posts its tracking comment within seconds of the prompt, so the reply is the next
  `claude[bot]` comment in the same thread within five minutes.
  - Two prompts written a second apart on 20 Nov got their replies in the other order, so those two are paired by
    hand (`REPLY_OVERRIDES`).
- **What it produced** is read from each reply:
  - **videos:** those on the lab's channel and titled as the vertical lab. Each is listed under the first reply that
    links it, since later replies only refer back.
  - **PRs and issues:** those the reply names that a bot opened during the run.
  - **commit:** the one it says it pushed up to.
- **Text and dates:** each comment shows its latest text, and an edited one says when. Issue bodies don't, because
  an issue's update time moves with any activity on it.
- **The last entry** is the request for this log. Its run was still going when the data was read.
