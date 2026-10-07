# Pi tooling notes

Changes made on the Raspberry Pis that are not captured anywhere else in this repo.
See the "Tailscale → Raspberry Pi connection" section of `CLAUDE.md` for how to reach them.

## Headless Chromium on the Pi 5 stream cam (`RPI_STREAM_CAM_HOSTNAME`)

Installed 2026-09-17 with `sudo apt-get install chromium` (Chromium 152, Debian 13 arm64,
`chromium-l10n` and the usual `upower`/`usbmuxd` deps came along). Nothing is enabled at
boot — it is only ever invoked by hand.

**Why it is there.** Supplier sites that have to be read from a residential IP are
JavaScript single-page apps, so `curl` alone is not enough:

- McMaster-Carr returns a ~30 kB shell to plain `curl`. A Googlebot user agent gets the
  server-rendered *filter* sidebar but never the product grid, and any URL path McMaster
  does not recognise (a guessed filter or family slug) answers **HTTP 200 with a zero-byte
  body** rather than a 404 — so an empty file means "wrong URL", not "blocked".
- Sigma-Aldrich blocks the Pi outright (Akamai "Access Denied"), user agent regardless.

**Recipe.** `~/mcm/dump.sh <url> <outfile>` on that Pi:

```bash
chromium --headless --disable-gpu --no-sandbox --disable-dev-shm-usage \
  --user-agent="Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36" \
  --window-size=1600,3000 --virtual-time-budget=30000 \
  --user-data-dir=/tmp/cprof --dump-dom "$1" > "$2"
```

`--virtual-time-budget` is what makes it work; without it the DOM is dumped before the
grid renders. `~/mcm/txt.py` and `~/mcm/pair.py` strip tags to readable text.

**Two site-specific tricks worth keeping.**

- McMaster part numbers resolve as `https://www.mcmaster.com/<PART>/` (e.g. `4634T42`),
  and the `<title>` of the rendered page confirms the size — a cheap way to verify a link
  before quoting it. Category paths look like
  `https://www.mcmaster.com/products/rods/system-of-measurement~metric/material~aluminum-2/multipurpose-6061-aluminum-rods~~/`.
- Goodfellow renders only ~22 of its variants as visible rows, but the **full** variant
  list (sku, price, purity, diameter, length, url) is embedded in the page as an
  HTML-escaped JSON blob. Unescape the DOM and pull
  `{"id":...,"sku":...,"price":...}` objects instead of scraping the grid; the visible
  rows are paginated and the facet URLs (`/l/diameter:20mm`) are applied client-side, so
  they do not change what `--dump-dom` returns.

## Headed Chromium on a virtual display (2026-10-07)

Added for issue #161 because Fisher Scientific now fronts `fishersci.com` with an Akamai
behavioural challenge that plain `curl` and `chromium --headless` (old and `new`) both hit:
HTTP 403 for curl, a 2.6 kB "Powered and protected by Akamai" page for headless Chromium.
`thermofisher.com` catalogue pages for the same SKUs still answer 200 to curl.

Installed with `sudo apt-get install xvfb xdotool scrot` (34 packages). Nothing runs at
boot. A user venv at `~/.venvs/cdp` holds `websocket-client` for DevTools calls, and
`~/linkcheck/cdp.py` is a 60-line helper (`title | dom | text | nav <url> | shot <png> |
click <x> <y> | eval <js>`) that talks to a Chromium started with
`--remote-debugging-port=9222`. `~/linkcheck/linkcheck.sh` is the rate-limited curl link
checker used for the 2026-10-07 supplier-link audit.

Recipe:

```bash
Xvfb :99 -screen 0 1600x1000x24 &
DISPLAY=:99 chromium --no-sandbox --disable-dev-shm-usage --remote-debugging-port=9222 \
  --user-data-dir=/tmp/cprof_headed --window-size=1600,1000 "$URL" &
sleep 30; ~/.venvs/cdp/bin/python ~/linkcheck/cdp.py title
DISPLAY=:99 scrot -o shot.png           # read the screenshot, then xdotool mousemove/click
```

Outcome on Fisher: the challenge container (`#sec-if-cpt-container`) is injected but stays
`display:none` with a zero-height press-and-hold button, even after xdotool mouse movement,
a click and a reload. So as of 2026-10-07 Fisher product pages are not readable from the Pi
by any automated route; quote Thermo catalogue URLs instead. Kill Chromium and Xvfb when
done (`pkill -f remote-debugging-port=9222; pkill -x Xvfb`).
