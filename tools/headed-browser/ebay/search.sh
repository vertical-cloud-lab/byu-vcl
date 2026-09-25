#!/usr/bin/env bash
# search.sh "QUERY" NAME -- search eBay through the page's own search box, then save
# the rendered results with Ctrl+S (HTML only, no extra request) and summarise them.
#
# Coordinates are for the 1440x900 layout start_browser.sh opens, with an eBay page
# already showing. The first Ctrl+S dialog needs "Webpage, HTML Only" picked by hand
# (hb.py click on the format drop-down); Chrome remembers it after that.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
HB="$HERE/../hb.py"
WORK=${HB_WORK:-/tmp/hb}
"$HB" click 600 157; "$HB" key ctrl+a; "$HB" type "$1"; "$HB" click 1258 157
"$HB" wait 9
"$HB" scroll 3 700 600; "$HB" wait 1.5; "$HB" scroll -3 700 600
"$HB" shot "search-$2" >/dev/null
"$HB" key ctrl+s; "$HB" wait 2
"$HB" click 740 72; "$HB" key ctrl+a; "$HB" type "$WORK/save-$2.html"; "$HB" click 1231 844
"$HB" wait 3
python3 "$HERE/parse_srp.py" "$WORK/save-$2.html" 80
