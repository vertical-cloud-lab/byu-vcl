# Twin round 6: the used-equipment market (work in progress)

Issue [#424](https://github.com/vertical-cloud-lab/byu-vcl/issues/424): replace round 5's used-equipment stand-ins
(`USED_OK`, `USED` in `vertical-lab/twin/round5.py` at `4bb91b1`) with what is actually on the market, for every
station and instrument either lab buys in the twin (`twin/econ.py`'s `_vertical()` and `_conventional()`).

This README is filled in as the survey runs. The finished files will be:

- `listings.csv`: one row per listing seen;
- `summary.csv`: one row per station key, in the twin's units (weeks, fractions of the new price, probabilities);
- `new.csv`: each item's new price and the vendor's stated lead time;
- `sources.csv`: every source tried, and whether it could be read;
- `shots/`: screenshots of representative listings;
- `tools/`: the scripts that read the pages.

## How the pages were read

A headed Google Chrome on a virtual display (Xvfb) on the CI runner, with all of its traffic sent out through the
CubXL Pi over an SSH SOCKS tunnel, so sites see the lab's network (AS6510, Brigham Young University) and not a
datacenter. Chrome was not run on the Pi itself: that Pi has 1 GB of RAM and a live camera service (`deckcam`). The
rig is the one CLAUDE.md describes for Onshape (`rig.sh` at byu-vcl `49677cf`).

Every page is preceded by a pause of 4-9 s, read with mouse moves along eased, slightly curved paths with jitter
and uneven wheel scrolls, and checked for a challenge or block page. Only public pages were read: no log-in, bid,
purchase or message. A site that challenged or blocked the browser was recorded and left alone, not retried around.
