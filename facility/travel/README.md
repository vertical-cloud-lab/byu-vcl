# How the travel times were read

These are the scripts behind [`../travel-times.md`](../travel-times.md). They use only `google-chrome`, `sed` and GNU
`awk`; the session that made them couldn't run Python or Node.

| File | What it is |
| --- | --- |
| `queries_origins.tsv`, `queries_destinations.tsv` | What was typed into Google Maps as each origin and destination. `S9x`, `S11x` and `S13x` are map pins from [`../out/sites/sites.tsv`](../out/sites/sites.tsv) |
| `sites.tsv`, `destinations.tsv` | Query ids against the map numbers and names used in the tables |
| `drive.awk`, `transit.awk` | Read the first route out of a page's text |
| `tomin.awk` | Turns "typically 35 min to 1 hr 15 min" into 35 and 75 |
| `long.awk`, `tlong.awk` | Join the readings with the site names into [`../out/travel/drive.tsv`](../out/travel/drive.tsv) and [`transit.tsv`](../out/travel/transit.tsv) |
| `md.awk`, `tmd.awk`, `svg.awk` | The tables and the chart |

**1. Fetch.** One page per query, six at a time. `ts` is the local wall-clock time written as if it were UTC
(`date -u -d 2026-11-17T07:30:00Z +%s`), `m` is `0` for driving and `3` for transit, and `id` is
`<origin>_<destination>_<am|mid|pm>_<out|in>`. "out" leaves the site; "in" arrives at it.

```bash
url="https://www.google.com/maps/dir/${from// /+}/${to// /+}/data=!4m6!4m5!2m3!6e0!7e2!8j${ts}!3e${m}?hl=en"
timeout 70 google-chrome --headless=new --no-sandbox --disable-gpu --user-data-dir="/tmp/prof/$id" \
  --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36" \
  --lang=en-US --window-size=1400,1000 --virtual-time-budget=20000 --dump-dom "$url" > "out/$id.html"
```

**2. Read.** Strip the tags, then take the first route after "Copy link". Transit pages also need Google's icon
glyphs and narrow no-break spaces removed:

```bash
sed -e 's/<[^>]*>/\n/g' "out/$id.html" | sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//' | grep -v '^$' | awk -f drive.awk
sed -e 's/<[^>]*>/\n/g' "out/X$id.html" | LC_ALL=C sed -e 's/\xe2\x80\xaf/ /g; s/\xc2\xa0/ /g; s/\xe2\x80\x8b//g; s/\xee[\x80-\xbf][\x80-\xbf]//g; s/&nbsp;/ /g; s/^[[:space:]]*//; s/[[:space:]]*$//' | grep -v '^$' | awk -f transit.awk
```

Google's resolved origin and destination are the page's `aria-label="Starting point …"` and
`aria-label="Destination …"`.

**3. Tables and chart**, from the committed data:

```bash
awk -v mode=summary -f md.awk ../out/travel/drive.tsv   # the at-a-glance table
awk -f md.awk ../out/travel/drive.tsv                   # one table per destination
awk -f svg.awk ../out/travel/drive.tsv > ../out/travel/drive_ranges.svg
awk -f tmd.awk ../out/travel/transit.tsv                # the transit table
google-chrome --headless=new --hide-scrollbars --window-size=1316,592 \
  --screenshot=../out/travel/drive_ranges.png "file://$PWD/../out/travel/drive_ranges.svg"
```
